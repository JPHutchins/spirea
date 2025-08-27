# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from typing import Any, Callable, ClassVar, NamedTuple, Type
from unittest.mock import Mock

from spirea.sync import Node, hsm_handle_entries, hsm_handle_event


class CardIn(NamedTuple):
	id: str
	timestamp: float


class Done(NamedTuple): ...


class Broke(NamedTuple): ...


class Fixed(NamedTuple): ...


type Event = CardIn | Done | Broke | Fixed




# Declare mocks at file scope
idle_entry_mock = Mock()
idle_run_mock = Mock()
idle_exit_mock = Mock()

working_entry_mock = Mock()
working_run_mock = Mock()
working_exit_mock = Mock()

broken_entry_mock = Mock()
broken_run_mock = Mock()
broken_exit_mock = Mock()


def card_in(event: CardIn, state: None) -> Type["Working"]:
	idle_run_mock(event, state)
	# type safe access to event attributes
	print(event.id, event.timestamp)
	return Working


class Idle(Node[Event, None, None]):
	_state: ClassVar[None] = None
	
	@staticmethod
	def entry(state: None) -> tuple[Type["Idle"], None]:
		idle_entry_mock(state)
		return Idle, None

	class EventHandlers:
		card_in: Callable[[CardIn, None], Type["Working"]] = card_in
		broken: Callable[[Broke, None], Type["Broken"]] = (
			lambda e, s: (idle_run_mock(e, s) and None) or Broken
		)

	@staticmethod
	def exit(state: None) -> None:
		idle_exit_mock(state)


class Working(Node[Event, None, None]):
	_state: ClassVar[None] = None
	
	@staticmethod
	def entry(state: None) -> tuple[Type["Working"], None]:
		working_entry_mock(state)
		return Working, None

	class EventHandlers:
		DONE: Callable[[Done, None], Type[Idle]] = (
			lambda e, s: (working_run_mock(e, s) and None) or Idle
		)

	@staticmethod
	def exit(state: None) -> None:
		working_exit_mock(state)


class Broken(Node[Event, None, None]):
	_state: ClassVar[None] = None
	
	@staticmethod
	def entry(state: None) -> tuple[Type["Broken"], None]:
		broken_entry_mock(state)
		return Broken, None

	class EventHandlers:
		FIXED: Callable[[Fixed, None], Type[Idle]] = (
			lambda e, s: (broken_run_mock(e, s) and None) or Idle
		)

	@staticmethod
	def exit(state: None) -> None:
		broken_exit_mock(state)


def test_transitions_run() -> None:
	node: Type[Node[Event, None, Any]] = Idle
	node = hsm_handle_entries(node)  # type: ignore[assignment]
	
	# Reset mocks after initialization
	idle_entry_mock.reset_mock()
	idle_exit_mock.reset_mock()
	working_entry_mock.reset_mock()
	working_exit_mock.reset_mock()
	broken_entry_mock.reset_mock()
	broken_exit_mock.reset_mock()

	# test the unhandled events
	node = hsm_handle_event(node, Done())
	assert node is Idle
	node = hsm_handle_event(node, Fixed())
	assert node is Idle
	assert idle_run_mock.call_count == 0

	node = hsm_handle_event(node, CardIn("user1", 1234567890.0))
	assert node is Working
	idle_run_mock.assert_called_once_with(CardIn("user1", 1234567890.0), None)
	idle_run_mock.reset_mock()
	idle_exit_mock.assert_called_once_with(None)
	idle_exit_mock.reset_mock()
	working_entry_mock.assert_called_once_with(None)
	working_entry_mock.reset_mock()

	# test the unhandled events
	node = hsm_handle_event(node, CardIn("user1", 1234567890.0))
	assert node is Working
	node = hsm_handle_event(node, Broke())
	assert node is Working
	node = hsm_handle_event(node, Fixed())
	assert node is Working
	assert working_run_mock.call_count == 0

	node = hsm_handle_event(node, Done())
	assert node is Idle
	working_run_mock.assert_called_once_with(Done(), None)
	working_run_mock.reset_mock()
	working_exit_mock.assert_called_once_with(None)
	working_exit_mock.reset_mock()
	idle_entry_mock.assert_called_once_with(None)
	idle_entry_mock.reset_mock()

	node = hsm_handle_event(node, Broke())
	assert node is Broken
	idle_run_mock.assert_called_once_with(Broke(), None)
	idle_run_mock.reset_mock()
	idle_exit_mock.assert_called_once_with(None)
	idle_exit_mock.reset_mock()
	broken_entry_mock.assert_called_once_with(None)
	broken_entry_mock.reset_mock()

	node = hsm_handle_event(node, Fixed())
	assert node is Idle
	broken_run_mock.assert_called_once_with(Fixed(), None)
	broken_run_mock.reset_mock()
	broken_exit_mock.assert_called_once_with(None)
	broken_exit_mock.reset_mock()
	idle_entry_mock.assert_called_once_with(None)
	idle_entry_mock.reset_mock()
