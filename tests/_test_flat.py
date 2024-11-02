from typing import Type, Literal, NamedTuple, assert_never, TypeVar, overload
from unittest.mock import Mock

from enum import IntEnum

from hsm import Node, hsm_handle_event


class Event(IntEnum):
    CARD_IN = 0
    DONE = 1
    BROKEN = 2
    FIXED = 3


class State(NamedTuple):
    pass


T = TypeVar("T")

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


class Idle(Node[Event, State]):
    @classmethod
    def entry(cls, state: State | None = None) -> Type["Node[Event, State]"]:
        idle_entry_mock(state)
        return cls

    @overload  # type: ignore
    @classmethod
    def run(cls, event: Literal[Event.CARD_IN], state: State | None = None) -> Type["Working"]: ...

    @overload
    @classmethod
    def run(cls, event: Literal[Event.BROKEN], state: State | None = None) -> Type["Broken"]: ...

    @classmethod
    def run(
        cls,
        event: Literal[Event.CARD_IN, Event.BROKEN],
        state: State | None = None,
    ) -> Type["Working"] | Type["Broken"] | Type["Idle"]:
        idle_run_mock(event, state)
        if event == Event.CARD_IN:
            return Working
        elif event == Event.BROKEN:
            return Broken
        assert_never(event)

    @classmethod
    def exit(cls, state: State | None = None) -> None:
        idle_exit_mock(state)


class Working(Node[Event, State]):
    @classmethod
    def entry(cls, state: State | None = None) -> Type["Node[Event, State]"]:
        working_entry_mock(state)
        return cls

    @overload  # type: ignore
    @classmethod
    def run(cls, event: Literal[Event.DONE], state: State | None = None) -> Type["Idle"]: ...

    @classmethod
    def run(
        cls, event: Literal[Event.DONE], state: State | None = None
    ) -> Type["Idle"] | Type["Broken"]:
        working_run_mock(event, state)
        if event == Event.DONE:
            return Idle
        assert_never(event)

    @classmethod
    def exit(cls, state: State | None = None) -> None:
        working_exit_mock(state)


class Broken(Node[Event, State]):
    @classmethod
    def entry(cls, state: State | None = None) -> Type["Node[Event, State]"]:
        broken_entry_mock(state)
        return cls

    @overload  # type: ignore
    @classmethod
    def run(cls, event: Literal[Event.FIXED], state: State | None = None) -> Type["Idle"]: ...

    @classmethod
    def run(cls, event: Literal[Event.FIXED], state: State | None = None) -> Type["Idle"]:
        broken_run_mock(event, state)
        if event == Event.FIXED:
            return Idle
        assert_never(event)

    @classmethod
    def exit(cls, state: State | None = None) -> None:
        broken_exit_mock(state)


def test_transitions_raw() -> None:
    idle = Idle

    working = idle.run(Event.CARD_IN)
    assert working is Working

    idle = working.run(Event.DONE)
    assert idle is Idle

    broken = idle.run(Event.BROKEN)
    assert broken is Broken

    idle = broken.run(Event.FIXED)
    assert idle is Idle

    # Reset mocks
    idle_entry_mock.reset_mock()
    idle_run_mock.reset_mock()
    idle_exit_mock.reset_mock()
    working_entry_mock.reset_mock()
    working_run_mock.reset_mock()
    working_exit_mock.reset_mock()
    broken_entry_mock.reset_mock()
    broken_run_mock.reset_mock()
    broken_exit_mock.reset_mock()


def test_transitions_run() -> None:
    node: Type[Node[Event, State]] = Idle  # type: ignore

    # test the unhandled events
    node = hsm_handle_event(node, Event.DONE)
    assert node is Idle
    node = hsm_handle_event(node, Event.FIXED)
    assert node is Idle
    assert idle_run_mock.call_count == 0

    node = hsm_handle_event(node, Event.CARD_IN)
    assert node is Working
    idle_run_mock.assert_called_once_with(Event.CARD_IN, None)
    idle_run_mock.reset_mock()
    idle_exit_mock.assert_called_once_with(None)
    idle_exit_mock.reset_mock()
    working_entry_mock.assert_called_once_with(None)
    working_entry_mock.reset_mock()

    # test the unhandled events
    node = hsm_handle_event(node, Event.CARD_IN)
    assert node is Working
    node = hsm_handle_event(node, Event.BROKEN)
    assert node is Working
    node = hsm_handle_event(node, Event.FIXED)
    assert node is Working
    assert working_run_mock.call_count == 0

    node = hsm_handle_event(node, Event.DONE)
    assert node is Idle
    working_run_mock.assert_called_once_with(Event.DONE, None)
    working_run_mock.reset_mock()
    working_exit_mock.assert_called_once_with(None)
    working_exit_mock.reset_mock()
    idle_entry_mock.assert_called_once_with(None)
    idle_entry_mock.reset_mock()

    node = hsm_handle_event(node, Event.BROKEN)
    assert node is Broken
    idle_run_mock.assert_called_once_with(Event.BROKEN, None)
    idle_run_mock.reset_mock()
    idle_exit_mock.assert_called_once_with(None)
    idle_exit_mock.reset_mock()
    broken_entry_mock.assert_called_once_with(None)
    broken_entry_mock.reset_mock()

    node = hsm_handle_event(node, Event.FIXED)
    assert node is Idle
    broken_run_mock.assert_called_once_with(Event.FIXED, None)
    broken_run_mock.reset_mock()
    broken_exit_mock.assert_called_once_with(None)
    broken_exit_mock.reset_mock()
    idle_entry_mock.assert_called_once_with(None)
    idle_entry_mock.reset_mock()
