from typing import (
    Type,
    Literal as L,
    NamedTuple,
    TypeVar,
    Callable,
)
from unittest.mock import Mock

from enum import IntEnum

from hsm.sync import Node, hsm_handle_event


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
    @staticmethod
    def entry(state: State | None = None) -> Type[Node[Event, State]]:
        idle_entry_mock(state)
        return Idle

    class EventHandlers:
        CARD_IN: Callable[[L[Event.CARD_IN], State | None], Type["Working"]] = (
            lambda e, s: (idle_run_mock(e, s) and None) or Working
        )
        BROKEN: Callable[[L[Event.BROKEN], State | None], Type["Broken"]] = (
            lambda e, s: (idle_run_mock(e, s) and None) or Broken
        )

    @staticmethod
    def exit(state: State | None = None) -> None:
        idle_exit_mock(state)


class Working(Node[Event, State]):
    @staticmethod
    def entry(state: State | None = None) -> Type[Node[Event, State]]:
        working_entry_mock(state)
        return Working

    class EventHandlers:
        DONE: Callable[[L[Event.DONE], State | None], Type[Idle]] = (
            lambda e, s: (working_run_mock(e, s) and None) or Idle
        )

    @staticmethod
    def exit(state: State | None = None) -> None:
        working_exit_mock(state)


class Broken(Node[Event, State]):
    @staticmethod
    def entry(state: State | None = None) -> Type[Node[Event, State]]:
        broken_entry_mock(state)
        return Broken

    class EventHandlers:
        FIXED: Callable[[L[Event.FIXED], State | None], Type[Idle]] = (
            lambda e, s: (broken_run_mock(e, s) and None) or Idle
        )

    @staticmethod
    def exit(state: State | None = None) -> None:
        broken_exit_mock(state)


def test_transitions_run() -> None:
    node: Type[Node[Event, State]] = Idle

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
