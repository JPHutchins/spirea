from typing import Type, Literal as L, NamedTuple, assert_never, TypeVar, overload
from unittest.mock import Mock, call
from dataclasses import dataclass
import pytest

from enum import IntEnum

from hsm import Node, hsm_handle_event, HSMStatus, hsm_handle_entries


class Event(IntEnum):
    a = 0
    b = 1
    c = 2
    d = 3
    e = 4
    f = 5
    g = 6
    h = 7


@dataclass
class State:
    foo: int


T = TypeVar("T")


mock = Mock()


class s0(Node[Event, State]):
    @classmethod
    def entry(cls, state: State | None = None) -> Type["Node[Event, State]"]:
        mock.s0_entry(state)
        return s0.s1

    @classmethod  # type: ignore[override]
    def run(
        cls, event: L[Event.e], state: State | None = None
    ) -> Type["s0.s2.s21.s211"]:
        mock.s0_run(event, state)
        if event == Event.e:
            return s0.s2.s21.s211
        assert_never(event)

    @classmethod
    def exit(cls, state: State | None = None) -> None:
        mock.s0_exit(state)

    class s1(Node[Event, State]):
        @classmethod
        def entry(cls, state: State | None = None) -> Type[Node[Event, State]]:
            mock.s1_entry(state)
            return s0.s1.s11

        @classmethod  # type: ignore[override]
        def run(
            cls,
            event: L[Event.a, Event.b, Event.c, Event.d, Event.f],
            state: State | None = None,
        ) -> (
            Type["s0.s1.s11"]
            | Type["s0"]
            | Type["s0.s2"]
            | Type["s0.s2.s21.s211"]
            | L[HSMStatus.SELF_TRANSITION]
        ):
            mock.s1_run(event, state)
            if event == Event.a:
                return HSMStatus.SELF_TRANSITION
            elif event == Event.b:
                return s0.s1.s11
            elif event == Event.c:
                return s0.s2
            elif event == Event.d:
                return s0
            elif event == Event.f:
                return s0.s2.s21.s211
            assert_never(event)

        @classmethod
        def exit(cls, state: State | None = None) -> None:
            mock.s1_exit(state)

        class s11(Node[Event, State]):
            @classmethod
            def entry(cls, state: State | None = None) -> Type[Node[Event, State]]:
                mock.s11_entry(state)
                return cls

            @classmethod  # type: ignore[override]
            def run(
                cls, event: L[Event.g], state: State | None = None
            ) -> Type["s0.s2.s21.s211"]:
                mock.s11_run(event, state)
                if event == Event.g:
                    return s0.s2.s21.s211
                assert_never(event)

            @classmethod  # type: ignore[override]
            def exit(cls, state: State) -> None:
                mock.s11_exit(state)
                if state.foo == 1:
                    state.foo = 0

    class s2(Node[Event, State]):
        @classmethod
        def entry(cls, state: State | None = None) -> Type[Node[Event, State]]:
            mock.s2_entry(state)
            return s0.s2.s21

        @classmethod  # type: ignore[override]
        def run(
            cls, event: L[Event.c, Event.f], state: State | None = None
        ) -> Type["s0.s1"] | Type["s0.s1.s11"]:
            mock.s2_run(event, state)
            if event == Event.c:
                return s0.s1
            elif event == Event.f:
                return s0.s1.s11
            assert_never(event)

        @classmethod
        def exit(cls, state: State | None = None) -> None:
            mock.s2_exit(state)

        class s21(Node[Event, State]):
            @classmethod
            def entry(cls, state: State | None = None) -> Type[Node[Event, State]]:
                mock.s21_entry(state)
                return s0.s2.s21.s211

            @classmethod  # type: ignore[override]
            def run(
                cls, event: L[Event.b, Event.h], state: State
            ) -> (
                Type["s0.s2.s21.s211"]
                | L[HSMStatus.SELF_TRANSITION, HSMStatus.NO_TRANSITION]
            ):
                mock.s21_run(event, state)
                if event == Event.b:
                    return s0.s2.s21.s211
                elif event == Event.h:
                    if state.foo == 0:
                        state.foo = 1
                        return HSMStatus.SELF_TRANSITION
                    else:
                        return HSMStatus.NO_TRANSITION
                assert_never(event)

            @classmethod
            def exit(cls, state: State | None = None) -> None:
                mock.s21_exit(state)

            class s211(Node[Event, State]):
                @classmethod
                def entry(cls, state: State | None = None) -> Type[Node[Event, State]]:
                    mock.s211_entry(state)
                    return cls

                @classmethod  # type: ignore[override]
                def run(
                    cls, event: L[Event.d, Event.g], state: State | None = None
                ) -> Type["s0.s2.s21"] | Type["s0"]:
                    mock.s211_run(event, state)
                    if event == Event.d:
                        return s0.s2.s21
                    elif event == Event.g:
                        return s0
                    assert_never(event)

                @classmethod
                def exit(cls, state: State | None = None) -> None:
                    mock.s211_exit(state)


def test_transitions_run() -> None:
    state = State(foo=0)

    node = hsm_handle_entries(s0, state)  # type: ignore[type-abstract]
    assert node is s0.s1.s11

    node = hsm_handle_event((node,), Event.b, state)
    assert node is s0.s1.s11

    node = hsm_handle_event((node,), Event.g, state)
    assert node is s0.s2.s21.s211

    node = hsm_handle_event((node,), Event.h, state)
    assert node is s0.s2.s21.s211
    assert state.foo == 1

    node = hsm_handle_event((node,), Event.g, state)
    assert node is s0

    node = hsm_handle_event((node,), Event.g, state)
    assert node is s0
    assert state.foo == 1


@pytest.mark.parametrize("event", set(Event) - {Event.e})
def test_s0_unhandled(event: Event) -> None:
    """All events but e are ignored in s0."""

    mock.reset_mock()

    state = State(foo=0)

    node = hsm_handle_event((s0,), event, state)
    assert node is s0
    assert state.foo == 0

    mock.s0_entry.assert_not_called()
    mock.s0_run.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s1_entry.assert_not_called()
    mock.s1_run.assert_not_called()
    mock.s1_exit.assert_not_called()

    mock.s11_entry.assert_not_called()
    mock.s11_run.assert_not_called()
    mock.s11_exit.assert_not_called()

    mock.s2_entry.assert_not_called()
    mock.s2_run.assert_not_called()
    mock.s2_exit.assert_not_called()

    mock.s21_entry.assert_not_called()
    mock.s21_run.assert_not_called()
    mock.s21_exit.assert_not_called()

    mock.s211_entry.assert_not_called()
    mock.s211_run.assert_not_called()
    mock.s211_exit.assert_not_called()


def test_s0_e() -> None:
    mock.reset_mock()

    state = State(foo=0)

    node = hsm_handle_event((s0,), Event.e, state)
    assert node is s0.s2.s21.s211
    assert state.foo == 0

    mock.assert_has_calls(
        (
            call.s0_run(Event.e, state),
            call.s2_entry(state),
            call.s21_entry(state),
            call.s211_entry(state),
        )
    )

    mock.s0_entry.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s1_entry.assert_not_called()
    mock.s1_run.assert_not_called()
    mock.s1_exit.assert_not_called()

    mock.s11_entry.assert_not_called()
    mock.s11_run.assert_not_called()
    mock.s11_exit.assert_not_called()

    mock.s2_run.assert_not_called()
    mock.s2_exit.assert_not_called()

    mock.s21_run.assert_not_called()
    mock.s21_exit.assert_not_called()

    mock.s211_run.assert_not_called()
    mock.s211_exit.assert_not_called()


@pytest.mark.parametrize("foo", (0, 1))
def test_s11_a(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = hsm_handle_event((s0.s1.s11,), Event.a, state)
    assert node is s0.s1.s11
    assert state.foo == 0

    mock.assert_has_calls(
        (
            call.s1_run(Event.a, state),
            call.s11_exit(state),
            call.s1_exit(state),
            call.s1_entry(state),
            call.s11_entry(state),
        )
    )

    mock.s11_run.assert_not_called()

    mock.s0_entry.assert_not_called()
    mock.s0_run.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s2_entry.assert_not_called()
    mock.s2_run.assert_not_called()
    mock.s2_exit.assert_not_called()

    mock.s21_entry.assert_not_called()
    mock.s21_run.assert_not_called()
    mock.s21_exit.assert_not_called()

    mock.s211_entry.assert_not_called()
    mock.s211_run.assert_not_called()
    mock.s211_exit.assert_not_called()


@pytest.mark.parametrize("foo", (0, 1))
def test_s11_b(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = hsm_handle_event((s0.s1.s11,), Event.b, state)
    assert node is s0.s1.s11
    assert state.foo == 0

    mock.assert_has_calls(
        (
            call.s1_run(Event.b, state),
            call.s11_exit(state),
            call.s11_entry(state),
        )
    )

    mock.s11_run.assert_not_called()

    mock.s1_entry.assert_not_called()
    mock.s1_exit.assert_not_called()

    mock.s0_entry.assert_not_called()
    mock.s0_run.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s2_entry.assert_not_called()
    mock.s2_run.assert_not_called()
    mock.s2_exit.assert_not_called()

    mock.s21_entry.assert_not_called()
    mock.s21_run.assert_not_called()
    mock.s21_exit.assert_not_called()

    mock.s211_entry.assert_not_called()
    mock.s211_run.assert_not_called()
    mock.s211_exit.assert_not_called()


@pytest.mark.parametrize("foo", (0, 1))
def test_s11_c(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = hsm_handle_event((s0.s1.s11,), Event.c, state)
    assert node is s0.s2.s21.s211
    assert state.foo == 0

    mock.assert_has_calls(
        (
            call.s1_run(Event.c, state),
            call.s11_exit(state),
            call.s1_exit(state),
            call.s2_entry(state),
            call.s21_entry(state),
            call.s211_entry(state),
        )
    )

    mock.s0_entry.assert_not_called()
    mock.s0_run.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s1_entry.assert_not_called()

    mock.s11_entry.assert_not_called()
    mock.s11_run.assert_not_called()

    mock.s2_run.assert_not_called()
    mock.s2_exit.assert_not_called()

    mock.s21_run.assert_not_called()
    mock.s21_exit.assert_not_called()

    mock.s211_run.assert_not_called()
    mock.s211_exit.assert_not_called()


@pytest.mark.parametrize("foo", (0, 1))
def test_s11_d(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = hsm_handle_event((s0.s1.s11,), Event.d, state)
    assert node is s0
    assert state.foo == 0

    mock.assert_has_calls(
        (
            call.s1_run(Event.d, state),
            call.s11_exit(state),
            call.s1_exit(state),
        )
    )

    mock.s0_run.assert_not_called()

    mock.s11_run.assert_not_called()

    mock.s2_entry.assert_not_called()
    mock.s2_run.assert_not_called()
    mock.s2_exit.assert_not_called()

    mock.s21_entry.assert_not_called()
    mock.s21_run.assert_not_called()
    mock.s21_exit.assert_not_called()

    mock.s211_entry.assert_not_called()
    mock.s211_run.assert_not_called()
    mock.s211_exit.assert_not_called()


@pytest.mark.parametrize("foo", (0, 1))
def test_s11_e(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = hsm_handle_event((s0.s1.s11,), Event.e, state)
    assert node is s0.s2.s21.s211
    assert state.foo == 0

    mock.assert_has_calls(
        (
            call.s0_run(Event.e, state),
            call.s11_exit(state),
            call.s1_exit(state),
            call.s2_entry(state),
            call.s21_entry(state),
            call.s211_entry(state),
        )
    )

    mock.s1_entry.assert_not_called()
    mock.s1_run.assert_not_called()

    mock.s11_entry.assert_not_called()
    mock.s11_run.assert_not_called()

    mock.s2_run.assert_not_called()
    mock.s2_exit.assert_not_called()

    mock.s21_run.assert_not_called()
    mock.s21_exit.assert_not_called()

    mock.s211_run.assert_not_called()
    mock.s211_exit.assert_not_called()


@pytest.mark.parametrize("foo", (0, 1))
def test_s11_f(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = hsm_handle_event((s0.s1.s11,), Event.f, state)
    assert node is s0.s2.s21.s211
    assert state.foo == 0

    mock.assert_has_calls(
        (
            call.s1_run(Event.f, state),
            call.s11_exit(state),
            call.s1_exit(state),
            call.s2_entry(state),
            call.s21_entry(state),
            call.s211_entry(state),
        )
    )

    mock.s0_entry.assert_not_called()
    mock.s0_run.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s1_entry.assert_not_called()

    mock.s11_entry.assert_not_called()
    mock.s11_run.assert_not_called()

    mock.s2_run.assert_not_called()
    mock.s2_exit.assert_not_called()

    mock.s21_run.assert_not_called()
    mock.s21_exit.assert_not_called()

    mock.s211_run.assert_not_called()
    mock.s211_exit.assert_not_called()


@pytest.mark.parametrize("foo", (0, 1))
def test_s11_g(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = hsm_handle_event((s0.s1.s11,), Event.g, state)
    assert node is s0.s2.s21.s211
    assert state.foo == 0

    mock.assert_has_calls(
        (
            call.s11_run(Event.g, state),
            call.s11_exit(state),
            call.s1_exit(state),
            call.s2_entry(state),
            call.s21_entry(state),
            call.s211_entry(state),
        )
    )

    mock.s0_entry.assert_not_called()
    mock.s0_run.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s1_entry.assert_not_called()
    mock.s1_run.assert_not_called()

    mock.s11_entry.assert_not_called()

    mock.s2_run.assert_not_called()
    mock.s2_exit.assert_not_called()

    mock.s21_run.assert_not_called()
    mock.s21_exit.assert_not_called()

    mock.s211_run.assert_not_called()
    mock.s211_exit.assert_not_called()


@pytest.mark.parametrize("foo", (0, 1))
def test_s11_h(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = hsm_handle_event((s0.s1.s11,), Event.h, state)
    assert node is s0.s1.s11
    assert state.foo == foo

    mock.s0_entry.assert_not_called()
    mock.s0_run.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s1_entry.assert_not_called()
    mock.s1_run.assert_not_called()
    mock.s1_exit.assert_not_called()

    mock.s11_entry.assert_not_called()
    mock.s11_run.assert_not_called()
    mock.s11_exit.assert_not_called()

    mock.s2_entry.assert_not_called()
    mock.s2_run.assert_not_called()
    mock.s2_exit.assert_not_called()

    mock.s21_entry.assert_not_called()
    mock.s21_run.assert_not_called()
    mock.s21_exit.assert_not_called()

    mock.s211_entry.assert_not_called()
    mock.s211_run.assert_not_called()
    mock.s211_exit.assert_not_called()


@pytest.mark.parametrize("foo", (0, 1))
def test_s211_a(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = hsm_handle_event((s0.s2.s21.s211,), Event.a, state)
    assert node is s0.s2.s21.s211
    assert state.foo == foo

    mock.s0_entry.assert_not_called()
    mock.s0_run.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s1_entry.assert_not_called()
    mock.s1_run.assert_not_called()
    mock.s1_exit.assert_not_called()

    mock.s11_entry.assert_not_called()
    mock.s11_run.assert_not_called()
    mock.s11_exit.assert_not_called()

    mock.s2_entry.assert_not_called()
    mock.s2_run.assert_not_called()
    mock.s2_exit.assert_not_called()

    mock.s21_entry.assert_not_called()
    mock.s21_run.assert_not_called()
    mock.s21_exit.assert_not_called()

    mock.s211_entry.assert_not_called()
    mock.s211_run.assert_not_called()
    mock.s211_exit.assert_not_called()


@pytest.mark.parametrize("foo", (0, 1))
def test_s211_b(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = hsm_handle_event((s0.s2.s21.s211,), Event.b, state)
    assert node is s0.s2.s21.s211
    assert state.foo == foo

    mock.assert_has_calls(
        (
            call.s21_run(Event.b, state),
            call.s211_exit(state),
            call.s211_entry(state),
        )
    )

    mock.s0_entry.assert_not_called()
    mock.s0_run.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s1_entry.assert_not_called()
    mock.s1_run.assert_not_called()
    mock.s1_exit.assert_not_called()

    mock.s11_entry.assert_not_called()
    mock.s11_run.assert_not_called()
    mock.s11_exit.assert_not_called()

    mock.s2_entry.assert_not_called()
    mock.s2_run.assert_not_called()
    mock.s2_exit.assert_not_called()

    mock.s21_entry.assert_not_called()
    mock.s21_exit.assert_not_called()

    mock.s211_run.assert_not_called()


@pytest.mark.parametrize("foo", (0, 1))
def test_s211_c(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = hsm_handle_event((s0.s2.s21.s211,), Event.c, state)
    assert node is s0.s1.s11
    assert state.foo == foo

    mock.assert_has_calls(
        (
            call.s2_run(Event.c, state),
            call.s211_exit(state),
            call.s21_exit(state),
            call.s2_exit(state),
            call.s1_entry(state),
            call.s11_entry(state),
        )
    )

    mock.s0_entry.assert_not_called()
    mock.s0_run.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s1_run.assert_not_called()
    mock.s1_exit.assert_not_called()

    mock.s11_run.assert_not_called()
    mock.s11_exit.assert_not_called()

    mock.s2_entry.assert_not_called()

    mock.s21_entry.assert_not_called()
    mock.s21_run.assert_not_called()

    mock.s211_entry.assert_not_called()
    mock.s211_run.assert_not_called()


@pytest.mark.parametrize("foo", (0, 1))
def test_s211_d(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = hsm_handle_event((s0.s2.s21.s211,), Event.d, state)
    assert node is s0.s2.s21
    assert state.foo == foo

    mock.assert_has_calls(
        (
            call.s211_run(Event.d, state),
            call.s211_exit(state),
        )
    )

    mock.s0_entry.assert_not_called()
    mock.s0_run.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s1_entry.assert_not_called()
    mock.s1_run.assert_not_called()
    mock.s1_exit.assert_not_called()

    mock.s11_entry.assert_not_called()
    mock.s11_run.assert_not_called()
    mock.s11_exit.assert_not_called()

    mock.s2_entry.assert_not_called()
    mock.s2_run.assert_not_called()
    mock.s2_exit.assert_not_called()

    mock.s21_entry.assert_not_called()
    mock.s21_run.assert_not_called()
    mock.s21_exit.assert_not_called()

    mock.s211_entry.assert_not_called()


@pytest.mark.parametrize("foo", (0, 1))
def test_s211_e(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = hsm_handle_event((s0.s2.s21.s211,), Event.e, state)
    assert node is s0.s2.s21.s211
    assert state.foo == foo

    mock.assert_has_calls(
        (
            call.s0_run(Event.e, state),
            call.s211_exit(state),
            call.s21_exit(state),
            call.s2_exit(state),
            call.s2_entry(state),
            call.s21_entry(state),
            call.s211_entry(state),
        )
    )

    mock.s0_entry.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s1_entry.assert_not_called()
    mock.s1_run.assert_not_called()
    mock.s1_exit.assert_not_called()

    mock.s11_entry.assert_not_called()
    mock.s11_run.assert_not_called()
    mock.s11_exit.assert_not_called()

    mock.s2_run.assert_not_called()

    mock.s21_run.assert_not_called()

    mock.s211_run.assert_not_called()


@pytest.mark.parametrize("foo", (0, 1))
def test_211_f(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = hsm_handle_event((s0.s2.s21.s211,), Event.f, state)
    assert node is s0.s1.s11
    assert state.foo == foo

    mock.assert_has_calls(
        (
            call.s2_run(Event.f, state),
            call.s211_exit(state),
            call.s21_exit(state),
            call.s2_exit(state),
            call.s1_entry(state),
            call.s11_entry(state),
        )
    )

    mock.s0_entry.assert_not_called()
    mock.s0_run.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s1_run.assert_not_called()
    mock.s1_exit.assert_not_called()

    mock.s11_run.assert_not_called()
    mock.s11_exit.assert_not_called()

    mock.s2_entry.assert_not_called()

    mock.s21_entry.assert_not_called()
    mock.s21_run.assert_not_called()

    mock.s211_entry.assert_not_called()
    mock.s211_run.assert_not_called()


@pytest.mark.parametrize("foo", (0, 1))
def test_211_g(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = hsm_handle_event((s0.s2.s21.s211,), Event.g, state)
    assert node is s0
    assert state.foo == foo

    mock.assert_has_calls(
        (
            call.s211_run(Event.g, state),
            call.s211_exit(state),
            call.s21_exit(state),
            call.s2_exit(state),
        )
    )

    mock.s0_entry.assert_not_called()
    mock.s0_run.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s1_entry.assert_not_called()
    mock.s1_run.assert_not_called()
    mock.s1_exit.assert_not_called()

    mock.s11_entry.assert_not_called()
    mock.s11_run.assert_not_called()
    mock.s11_exit.assert_not_called()

    mock.s2_entry.assert_not_called()
    mock.s2_run.assert_not_called()

    mock.s21_entry.assert_not_called()
    mock.s21_run.assert_not_called()

    mock.s211_entry.assert_not_called()


def test_211_h_foo_0() -> None:
    mock.reset_mock()

    state = State(foo=0)

    node = hsm_handle_event((s0.s2.s21.s211,), Event.h, state)
    assert node is s0.s2.s21.s211
    assert state.foo == 1

    mock.assert_has_calls(
        (
            call.s21_run(Event.h, state),
            call.s211_exit(state),
            call.s21_exit(state),
            call.s21_entry(state),
            call.s211_entry(state),
        )
    )

    mock.s0_entry.assert_not_called()
    mock.s0_run.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s1_entry.assert_not_called()
    mock.s1_run.assert_not_called()
    mock.s1_exit.assert_not_called()

    mock.s11_entry.assert_not_called()
    mock.s11_run.assert_not_called()
    mock.s11_exit.assert_not_called()

    mock.s2_entry.assert_not_called()
    mock.s2_run.assert_not_called()
    mock.s2_exit.assert_not_called()

    mock.s211_run.assert_not_called()


def test_211_h_foo_1() -> None:
    mock.reset_mock()

    state = State(foo=1)

    node = hsm_handle_event((s0.s2.s21.s211,), Event.h, state)
    assert node is s0.s2.s21.s211
    assert state.foo == 1

    mock.assert_has_calls((call.s21_run(Event.h, state),))

    mock.s0_entry.assert_not_called()
    mock.s0_run.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s1_entry.assert_not_called()
    mock.s1_run.assert_not_called()
    mock.s1_exit.assert_not_called()

    mock.s11_entry.assert_not_called()
    mock.s11_run.assert_not_called()
    mock.s11_exit.assert_not_called()

    mock.s2_entry.assert_not_called()
    mock.s2_run.assert_not_called()
    mock.s2_exit.assert_not_called()

    mock.s21_entry.assert_not_called()
    mock.s21_exit.assert_not_called()

    mock.s211_entry.assert_not_called()
    mock.s211_run.assert_not_called()
    mock.s211_exit.assert_not_called()


@pytest.mark.parametrize(
    "event", set(Event) - {Event.b, Event.c, Event.e, Event.f, Event.h}
)
def test_s21_unhandled(event: Event) -> None:
    """Some events are unhandled."""

    mock.reset_mock()

    state = State(foo=0)

    node = hsm_handle_event((s0,), event, state)
    assert node is s0
    assert state.foo == 0

    mock.s0_entry.assert_not_called()
    mock.s0_run.assert_not_called()
    mock.s0_exit.assert_not_called()

    mock.s1_entry.assert_not_called()
    mock.s1_run.assert_not_called()
    mock.s1_exit.assert_not_called()

    mock.s11_entry.assert_not_called()
    mock.s11_run.assert_not_called()
    mock.s11_exit.assert_not_called()

    mock.s2_entry.assert_not_called()
    mock.s2_run.assert_not_called()
    mock.s2_exit.assert_not_called()

    mock.s21_entry.assert_not_called()
    mock.s21_run.assert_not_called()
    mock.s21_exit.assert_not_called()

    mock.s211_entry.assert_not_called()
    mock.s211_run.assert_not_called()
    mock.s211_exit.assert_not_called()


def test_s21_b() -> None:
    mock.reset_mock()

    state = State(foo=0)

    node = hsm_handle_event((s0.s2.s21,), Event.b, state)
    assert node is s0.s2.s21.s211
    assert state.foo == 0

    mock.assert_has_calls(
        (
            call.s21_run(Event.b, state),
            call.s211_entry(state),
        )
    )


def test_s21_c() -> None:
    mock.reset_mock()

    state = State(foo=0)

    node = hsm_handle_event((s0.s2.s21,), Event.c, state)
    assert node is s0.s1.s11
    assert state.foo == 0

    mock.assert_has_calls(
        (
            call.s2_run(Event.c, state),
            call.s21_exit(state),
            call.s2_exit(state),
            call.s1_entry(state),
            call.s11_entry(state),
        )
    )


def test_s21_e() -> None:
    mock.reset_mock()

    state = State(foo=0)

    node = hsm_handle_event((s0.s2.s21,), Event.e, state)
    assert node is s0.s2.s21.s211
    assert state.foo == 0

    mock.assert_has_calls(
        (
            call.s0_run(Event.e, state),
            call.s21_exit(state),
            call.s2_exit(state),
            call.s2_entry(state),
            call.s21_entry(state),
            call.s211_entry(state),
        )
    )


def test_s21_f() -> None:
    mock.reset_mock()

    state = State(foo=0)

    node = hsm_handle_event((s0.s2.s21,), Event.f, state)
    assert node is s0.s1.s11
    assert state.foo == 0

    mock.assert_has_calls(
        (
            call.s2_run(Event.f, state),
            call.s21_exit(state),
            call.s2_exit(state),
            call.s1_entry(state),
            call.s11_entry(state),
        )
    )


def test_s21_h_foo_0() -> None:
    mock.reset_mock()

    state = State(foo=0)

    node = hsm_handle_event((s0.s2.s21,), Event.h, state)
    assert node is s0.s2.s21.s211
    assert state.foo == 1

    mock.assert_has_calls(
        (
            call.s21_run(Event.h, state),
            call.s21_exit(state),
            call.s21_entry(state),
            call.s211_entry(state),
        )
    )


def test_s21_h_foo_1() -> None:
    mock.reset_mock()

    state = State(foo=1)

    node = hsm_handle_event((s0.s2.s21,), Event.h, state)
    assert node is s0.s2.s21
    assert state.foo == 1

    mock.assert_has_calls((call.s21_run(Event.h, state),))
