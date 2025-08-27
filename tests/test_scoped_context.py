# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from typing import Callable, NamedTuple, Type
from unittest.mock import Mock

from spirea.sync import Node, hsm_handle_entries, hsm_handle_event


class Initialize(NamedTuple):
	session_id: str


class Connect(NamedTuple):
	host: str
	port: int


class Disconnect(NamedTuple): ...


class LoginUser(NamedTuple):
	username: str
	password: str


class LoginAdmin(NamedTuple):
	username: str
	password: str


class Logout(NamedTuple): ...


class AccessResource(NamedTuple):
	resource_id: str


type Event = Initialize | Connect | Disconnect | LoginUser | LoginAdmin | Logout | AccessResource


class InitialState(NamedTuple): ...


class BaseState(NamedTuple):
	"""Base state available to all states"""

	session_id: str


class ConnectedState(NamedTuple):
	"""State available when connected - inherits base state via composition"""

	base: BaseState
	transport: object
	connection_time: float


class UserState(NamedTuple):
	"""State available to authenticated user - inherits connected state"""

	connected: ConnectedState
	user_key: str
	permissions: list[str]


class AdminState(NamedTuple):
	"""State available to authenticated admin - inherits connected state"""

	connected: ConnectedState
	admin_key: str
	permissions: list[str]


# Mock instances
transport_mock = Mock()
auth_service_mock = Mock()
user_resource_mock = Mock()
admin_resource_mock = Mock()

# Entry/exit mocks
disconnected_entry_mock = Mock()
disconnected_exit_mock = Mock()
connected_entry_mock = Mock()
connected_exit_mock = Mock()
user_entry_mock = Mock()
user_exit_mock = Mock()
admin_entry_mock = Mock()
admin_exit_mock = Mock()

get_session_id_mock = Mock()


def connect_handler(event: Connect, state: BaseState) -> Type["Connected"]:
	"""Handle connection - creates transport and connected state"""
	transport_mock.connect(event.host, event.port)
	return Connected


class Disconnected(Node[Event, BaseState, ConnectedState | None]):
	@staticmethod
	def entry(state: None | ConnectedState) -> tuple[type["Disconnected"], BaseState]:
		new_state = BaseState(get_session_id_mock())
		disconnected_entry_mock(new_state)
		return Disconnected, new_state

	class EventHandlers:
		connect: Callable[[Connect, BaseState], Type["Connected"]] = connect_handler

	@staticmethod
	def exit(state: BaseState) -> None:
		disconnected_exit_mock(state)


class Connected(Node[Event, ConnectedState, BaseState]):
	@staticmethod
	def entry(state: BaseState) -> tuple[Type["Connected"], ConnectedState]:
		new_state = ConnectedState(
			base=state,
			transport=transport_mock,
			connection_time=123.456,
		)
		connected_entry_mock(new_state)
		return Connected, new_state

	class EventHandlers:
		disconnect: Callable[[Disconnect, ConnectedState], Type[Disconnected]] = (
			lambda e, s: (transport_mock.disconnect() and None) or Disconnected
		)
		login_user: Callable[[LoginUser, ConnectedState], Type["Connected.User"]] = (
			lambda e, s: (auth_service_mock.authenticate_user(e.username, e.password) and None)
			or Connected.User
		)
		login_admin: Callable[[LoginAdmin, ConnectedState], Type["Connected.Admin"]] = (
			lambda e, s: (auth_service_mock.authenticate_admin(e.username, e.password) and None)
			or Connected.Admin
		)

	@staticmethod
	def exit(state: ConnectedState) -> None:
		connected_exit_mock(state)

	class User(Node[Event, UserState, ConnectedState]):
		@staticmethod
		def entry(state: ConnectedState) -> tuple[Type["Connected.User"], UserState]:
			new_state = UserState(
				connected=state,
				user_key="user_key_abc123",
				permissions=["read", "write"],
			)
			user_entry_mock(new_state)
			return Connected.User, new_state

		class EventHandlers:
			logout: Callable[[Logout, UserState], Type["Connected"]] = (
				lambda e, s: (auth_service_mock.logout() and None) or Connected
			)
			access_resource: Callable[[AccessResource, UserState], Type["Connected.User"]] = (
				lambda e, s: (
					user_resource_mock.access(
						e.resource_id,
						s.user_key,
						s.connected.transport,
					)
					and None
				)
				or Connected.User
			)

		@staticmethod
		def exit(state: UserState) -> None:
			user_exit_mock(state)

	class Admin(Node[Event, AdminState, ConnectedState]):
		@staticmethod
		def entry(state: ConnectedState) -> tuple[Type["Connected.Admin"], AdminState]:
			new_state = AdminState(
				connected=state,
				admin_key="admin_key_xyz789",
				permissions=["read", "write", "admin", "delete"],
			)
			admin_entry_mock(new_state)
			return Connected.Admin, new_state

		class EventHandlers:
			logout: Callable[[Logout, AdminState], Type["Connected"]] = (
				lambda e, s: (auth_service_mock.logout() and None) or Connected
			)
			access_resource: Callable[[AccessResource, AdminState], Type["Connected.Admin"]] = (
				lambda e, s: (
					admin_resource_mock.access(
						e.resource_id,
						s.admin_key,
						s.connected.transport,
					)
					and None
				)
				or Connected.Admin
			)

		@staticmethod
		def exit(state: AdminState) -> None:
			admin_exit_mock(state)


def test_hierarchical_scoped_state() -> None:
	"""Test that nested states inherit state from parent states"""
	from typing import assert_type

	# Initial state
	disconnected = Disconnected
	get_session_id_mock.return_value = "session_123"
	disconnected = hsm_handle_entries(disconnected)  # type: ignore[assignment]
	assert disconnected is Disconnected
	assert disconnected._state.session_id == "session_123"

	# Start disconnected
	connected = hsm_handle_event(disconnected, Connect("localhost", 8080))
	assert connected is Connected
	assert connected._state.base.session_id == "session_123"
	assert connected._state.transport is transport_mock
	assert connected._state.connection_time == 123.456
	assert not hasattr(connected._state, "user_key")

	transport_mock.connect.assert_called_once_with("localhost", 8080)
	disconnected_exit_mock.assert_called_once()
	connected_entry_mock.assert_called_once()

	# Reset mocks
	transport_mock.reset_mock()
	disconnected_exit_mock.reset_mock()
	connected_entry_mock.reset_mock()

	# Login as user - transitions to nested User state
	user = hsm_handle_event(connected, LoginUser("alice", "password123"))  # type: ignore[assignment]
	assert user is Connected.User
	assert user._state.connected.base.session_id == "session_123"
	assert user._state.connected.transport is transport_mock
	assert user._state.user_key == "user_key_abc123"
	assert user._state.permissions == ["read", "write"]

	auth_service_mock.authenticate_user.assert_called_once_with("alice", "password123")
	user_entry_mock.assert_called_once()

	# Reset mocks
	auth_service_mock.reset_mock()
	connected_exit_mock.reset_mock()
	user_entry_mock.reset_mock()

	# User accesses resource - should have access to transport via inherited state
	user = hsm_handle_event(user, AccessResource("user_document"))  # type: ignore[assignment]
	assert user is Connected.User
	user_resource_mock.access.assert_called_once_with(
		"user_document", "user_key_abc123", transport_mock
	)

	# Reset mocks
	user_resource_mock.reset_mock()

	# Logout back to parent Connected state
	connected = hsm_handle_event(user, Logout())
	assert connected is Connected
	assert connected._state.base.session_id == "session_123"
	assert connected._state.transport is transport_mock

	auth_service_mock.logout.assert_called_once()
	user_exit_mock.assert_called_once()

	# Reset mocks
	auth_service_mock.reset_mock()
	user_exit_mock.reset_mock()

	# Login as admin - transitions to nested Admin state
	admin = hsm_handle_event(connected, LoginAdmin("admin", "admin_pass"))  # type: ignore[assignment]
	assert admin is Connected.Admin
	assert_type(admin._state.connected.base.session_id, str)
	assert admin._state.connected.base.session_id == "session_123"
	assert admin._state.connected.transport is transport_mock
	assert admin._state.admin_key == "admin_key_xyz789"
	assert admin._state.permissions == ["read", "write", "admin", "delete"]

	auth_service_mock.authenticate_admin.assert_called_once_with("admin", "admin_pass")
	admin_entry_mock.assert_called_once()

	# Reset mocks
	auth_service_mock.reset_mock()
	admin_entry_mock.reset_mock()

	# Admin accesses resource - should have access to transport via inherited state
	admin = hsm_handle_event(admin, AccessResource("system_config"))  # type: ignore[assignment]
	assert admin is Connected.Admin
	admin_resource_mock.access.assert_called_once_with(
		"system_config", "admin_key_xyz789", transport_mock
	)

	# Reset mocks
	admin_resource_mock.reset_mock()
	disconnected_entry_mock.reset_mock()

	# Test that disconnect from nested state works - should bubble up to parent
	get_session_id_mock.return_value = "session_456"
	disconnected = hsm_handle_event(admin, Disconnect())
	assert disconnected._state.session_id == "session_456"

	transport_mock.disconnect.assert_called_once()
	admin_exit_mock.assert_called_once()
	disconnected_entry_mock.assert_called_once()


def test_state_inheritance() -> None:
	"""Test that nested state data properly inherits from parent states"""
	# Create states showing the inheritance chain
	base_state = BaseState(session_id="test_session")
	connected_state = ConnectedState(
		base=base_state, transport=transport_mock, connection_time=1000.0
	)
	user_state = UserState(
		connected=connected_state, user_key="test_user_key", permissions=["read"]
	)

	# Verify access through the state hierarchy
	assert user_state.user_key == "test_user_key"  # User-specific
	assert user_state.connected.transport is transport_mock  # Connected-specific
	assert user_state.connected.base.session_id == "test_session"  # Base state

	# Similar for admin
	admin_state = AdminState(
		connected=connected_state,
		admin_key="test_admin_key",
		permissions=["read", "write", "admin"],
	)

	assert admin_state.admin_key == "test_admin_key"  # Admin-specific
	assert admin_state.connected.transport is transport_mock  # Connected-specific
	assert admin_state.connected.base.session_id == "test_session"  # Base state


def test_object_identity_preservation() -> None:
	"""Test that state objects maintain identity through hierarchical composition"""
	# Reset all mocks to prevent state pollution from other tests
	transport_mock.reset_mock()
	auth_service_mock.reset_mock()
	user_resource_mock.reset_mock()
	admin_resource_mock.reset_mock()
	disconnected_entry_mock.reset_mock()
	disconnected_exit_mock.reset_mock()
	connected_entry_mock.reset_mock()
	connected_exit_mock.reset_mock()
	user_entry_mock.reset_mock()
	user_exit_mock.reset_mock()
	admin_entry_mock.reset_mock()
	admin_exit_mock.reset_mock()

	# Reset node states to prevent pollution from previous tests
	Disconnected._state = None
	Connected._state = None
	Connected.User._state = None
	Connected.Admin._state = None

	# Initialize the HSM with a base state
	base_state = BaseState(session_id="identity_test_123")
	Disconnected._state = base_state
	disconnected = Disconnected

	# Verify the disconnected node has the base state
	assert disconnected._state is base_state

	# Transition to connected state
	connected = hsm_handle_event(disconnected, Connect("localhost", 8080))

	# Verify that the base state is preserved by object identity in the connected state
	assert connected._state.base is base_state
	assert connected._state.base is disconnected._state  # Same object!

	# Transition to user state
	user = hsm_handle_event(connected, LoginUser("test_user", "password"))

	# Verify object identity is preserved through the entire hierarchy
	assert user._state.connected.base is base_state
	assert user._state.connected.base is disconnected._state  # Same object!
	assert user._state.connected.base is connected._state.base  # Same object!

	# Transition to admin state from connected
	admin = hsm_handle_event(connected, LoginAdmin("admin", "admin_pass"))

	# Verify object identity is preserved in admin hierarchy too
	assert admin._state.connected.base is base_state
	assert admin._state.connected.base is disconnected._state  # Same object!
	assert admin._state.connected.base is connected._state.base  # Same object!
	assert admin._state.connected.base is user._state.connected.base  # Same object!

	# and of course that means that the value is preserved
	assert admin._state.connected.base.session_id == "identity_test_123"

	# Transition back to disconnected from admin
	disconnected_again = hsm_handle_event(admin, Disconnect())

	# Verify that a new state instance is created
	assert disconnected_again._state is not base_state
	assert disconnected_again._state == disconnected._state

	# The key insight: throughout the entire HSM lifecycle, the same BaseState object
	# is preserved by reference in all composed state structures that belong to
	# its children


def test_state_machine_cycles() -> None:
	"""Test that the state machine can handle multiple transition cycles correctly"""
	# Reset all mocks and node states
	transport_mock.reset_mock()
	auth_service_mock.reset_mock()
	user_resource_mock.reset_mock()
	admin_resource_mock.reset_mock()
	disconnected_entry_mock.reset_mock()
	disconnected_exit_mock.reset_mock()
	connected_entry_mock.reset_mock()
	connected_exit_mock.reset_mock()
	user_entry_mock.reset_mock()
	user_exit_mock.reset_mock()
	admin_entry_mock.reset_mock()
	admin_exit_mock.reset_mock()

	# Reset node states
	Disconnected._state = None
	Connected._state = None
	Connected.User._state = None
	Connected.Admin._state = None

	get_session_id_mock.return_value = "cycle_test_456"
	current = Disconnected
	current = hsm_handle_entries(current)
	assert current is Disconnected
	assert current._state.session_id == "cycle_test_456"

	# Perform multiple connect/disconnect cycles
	for _ in range(3):
		original_base = current._state

		# Connect
		current = hsm_handle_event(current, Connect("localhost", 8080))
		assert current is Connected
		assert current._state.base is original_base

		# Login as user
		current = hsm_handle_event(current, LoginUser("user", "pass"))
		assert current is Connected.User
		assert current._state.connected.base is original_base

		# Access resource
		current = hsm_handle_event(current, AccessResource("doc"))
		assert current is Connected.User
		assert current._state.connected.base is original_base

		# Logout to connected
		current = hsm_handle_event(current, Logout())
		assert current is Connected
		assert current._state.base is original_base

		# Login as admin
		current = hsm_handle_event(current, LoginAdmin("admin", "adminpass"))
		assert current is Connected.Admin
		assert current._state.connected.base is original_base

		# Access admin resource
		current = hsm_handle_event(current, AccessResource("sysconfig"))
		assert current is Connected.Admin
		assert current._state.connected.base is original_base

		# Disconnect from admin (should go back to disconnected)
		current = hsm_handle_event(current, Disconnect())
		assert current is Disconnected
		assert current._state is not original_base

		# Verify we're back where we started and can cycle again
		assert current._state.session_id == "cycle_test_456"
