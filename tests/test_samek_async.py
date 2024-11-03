from typing import Type, Literal as L, Callable
from unittest.mock import Mock, call
from dataclasses import dataclass
import pytest

from enum import IntEnum, Enum

from hsm.asyncio import Node, hsm_handle_event, HSMStatus, hsm_handle_entries


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


mock = Mock()


def s21_handle_h(
    event: L[Event.h], state: State
) -> L[HSMStatus.SELF_TRANSITION] | L[HSMStatus.NO_TRANSITION]:
    mock.s21_run(event, state)
    if state.foo == 0:
        state.foo = 1
        return HSMStatus.SELF_TRANSITION
    else:
        return HSMStatus.NO_TRANSITION


class s0(Node[Event, State]):
    @staticmethod
    async def entry(state: State | None = None) -> Type[Node[Event, State]]:
        mock.s0_entry(state)
        return s0.s1

    class EventHandlers(Enum):
        e: Callable[[L[Event.e], State | None], Type["s0.s2.s21.s211"]] = (
            lambda e, s: (mock.s0_run(e, s) and None) or s0.s2.s21.s211
        )

    @staticmethod
    async def exit(state: State | None = None) -> None:
        mock.s0_exit(state)

    class s1(Node[Event, State]):
        @staticmethod
        async def entry(state: State | None = None) -> Type[Node[Event, State]]:
            mock.s1_entry(state)
            return s0.s1.s11

        class EventHandlers(Enum):
            a: Callable[[L[Event.a], State | None], L[HSMStatus.SELF_TRANSITION]] = (
                lambda e, s: (mock.s1_run(e, s) and None) or HSMStatus.SELF_TRANSITION
            )
            b: Callable[[L[Event.b], State | None], Type["s0.s1.s11"]] = (
                lambda e, s: (mock.s1_run(e, s) and None) or s0.s1.s11
            )
            c: Callable[[L[Event.c], State | None], Type["s0.s2"]] = (
                lambda e, s: (mock.s1_run(e, s) and None) or s0.s2
            )
            d: Callable[[L[Event.d], State | None], Type["s0"]] = (
                lambda e, s: (mock.s1_run(e, s) and None) or s0
            )
            f: Callable[[L[Event.f], State | None], Type["s0.s2.s21.s211"]] = (
                lambda e, s: (mock.s1_run(e, s) and None) or s0.s2.s21.s211
            )

        @staticmethod
        async def exit(state: State | None = None) -> None:
            mock.s1_exit(state)

        class s11(Node[Event, State]):
            @staticmethod
            async def entry(state: State | None = None) -> Type[Node[Event, State]]:
                mock.s11_entry(state)
                return s0.s1.s11

            class EventHandlers(Enum):
                g: Callable[[L[Event.g], State | None], Type["s0.s2.s21.s211"]] = (
                    lambda e, s: (mock.s11_run(e, s) and None) or s0.s2.s21.s211
                )

            @staticmethod  # type: ignore[override]
            async def exit(state: State) -> None:
                mock.s11_exit(state)
                if state.foo == 1:
                    state.foo = 0

    class s2(Node[Event, State]):
        @staticmethod
        async def entry(state: State | None = None) -> Type[Node[Event, State]]:
            mock.s2_entry(state)
            return s0.s2.s21

        class EventHandlers(Enum):
            c: Callable[[L[Event.c], State | None], Type["s0.s1"]] = (
                lambda e, s: (mock.s2_run(e, s) and None) or s0.s1
            )
            f: Callable[[L[Event.f], State | None], Type["s0.s1.s11"]] = (
                lambda e, s: (mock.s2_run(e, s) and None) or s0.s1.s11
            )

        @staticmethod
        async def exit(state: State | None = None) -> None:
            mock.s2_exit(state)

        class s21(Node[Event, State]):
            @staticmethod
            async def entry(state: State | None = None) -> Type[Node[Event, State]]:
                mock.s21_entry(state)
                return s0.s2.s21.s211

            class EventHandlers(Enum):
                b: Callable[[L[Event.b], State | None], Type["s0.s2.s21.s211"]] = (
                    lambda e, s: (mock.s21_run(e, s) and None) or s0.s2.s21.s211
                )
                h: Callable[
                    [L[Event.h], State],
                    L[HSMStatus.SELF_TRANSITION] | L[HSMStatus.NO_TRANSITION],
                ] = s21_handle_h

            @staticmethod
            async def exit(state: State | None = None) -> None:
                mock.s21_exit(state)

            class s211(Node[Event, State]):
                @staticmethod
                async def entry(state: State | None = None) -> Type[Node[Event, State]]:
                    mock.s211_entry(state)
                    return s0.s2.s21.s211

                class EventHandlers(Enum):
                    d: Callable[[L[Event.d], State | None], Type["s0.s2.s21"]] = (
                        lambda e, s: (mock.s211_run(e, s) and None) or s0.s2.s21
                    )
                    g: Callable[[L[Event.g], State | None], Type["s0"]] = (
                        lambda e, s: (mock.s211_run(e, s) and None) or s0
                    )

                @staticmethod
                async def exit(state: State | None = None) -> None:
                    mock.s211_exit(state)


@pytest.mark.asyncio
async def test_transitions_run() -> None:
    state = State(foo=0)

    node = await hsm_handle_entries(s0, state)
    assert node is s0.s1.s11

    node = await hsm_handle_event(node, Event.b, state)
    assert node is s0.s1.s11

    node = await hsm_handle_event(node, Event.g, state)
    assert node is s0.s2.s21.s211

    node = await hsm_handle_event(node, Event.h, state)
    assert node is s0.s2.s21.s211
    assert state.foo == 1

    node = await hsm_handle_event(node, Event.g, state)
    assert node is s0

    node = await hsm_handle_event(node, Event.g, state)
    assert node is s0
    assert state.foo == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("event", set(Event) - {Event.e})
async def test_s0_unhandled(event: Event) -> None:
    """All events but e are ignored in s0."""

    mock.reset_mock()

    state = State(foo=0)

    node = await hsm_handle_event(s0, event, state)
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


@pytest.mark.asyncio
async def test_s0_e() -> None:
    mock.reset_mock()

    state = State(foo=0)

    node = await hsm_handle_event(s0, Event.e, state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s11_a(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = await hsm_handle_event(s0.s1.s11, Event.a, state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s11_b(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = await hsm_handle_event(s0.s1.s11, Event.b, state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s11_c(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = await hsm_handle_event(s0.s1.s11, Event.c, state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s11_d(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = await hsm_handle_event(s0.s1.s11, Event.d, state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s11_e(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = await hsm_handle_event(s0.s1.s11, Event.e, state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s11_f(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = await hsm_handle_event(s0.s1.s11, Event.f, state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s11_g(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = await hsm_handle_event(s0.s1.s11, Event.g, state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s11_h(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = await hsm_handle_event(s0.s1.s11, Event.h, state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s211_a(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = await hsm_handle_event(s0.s2.s21.s211, Event.a, state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s211_b(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = await hsm_handle_event(s0.s2.s21.s211, Event.b, state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s211_c(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = await hsm_handle_event(s0.s2.s21.s211, Event.c, state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s211_d(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = await hsm_handle_event(s0.s2.s21.s211, Event.d, state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s211_e(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = await hsm_handle_event(s0.s2.s21.s211, Event.e, state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_211_f(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = await hsm_handle_event(s0.s2.s21.s211, Event.f, state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_211_g(foo: int) -> None:
    mock.reset_mock()

    state = State(foo=foo)

    node = await hsm_handle_event(s0.s2.s21.s211, Event.g, state)
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


@pytest.mark.asyncio
async def test_211_h_foo_0() -> None:
    mock.reset_mock()

    state = State(foo=0)

    node = await hsm_handle_event(s0.s2.s21.s211, Event.h, state)
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


@pytest.mark.asyncio
async def test_211_h_foo_1() -> None:
    mock.reset_mock()

    state = State(foo=1)

    node = await hsm_handle_event(s0.s2.s21.s211, Event.h, state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event", set(Event) - {Event.b, Event.c, Event.e, Event.f, Event.h}
)
async def test_s21_unhandled(event: Event) -> None:
    """Some events are unhandled."""

    mock.reset_mock()

    state = State(foo=0)

    node = await hsm_handle_event(s0, event, state)
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


@pytest.mark.asyncio
async def test_s21_b() -> None:
    mock.reset_mock()

    state = State(foo=0)

    node = await hsm_handle_event(s0.s2.s21, Event.b, state)
    assert node is s0.s2.s21.s211
    assert state.foo == 0

    mock.assert_has_calls(
        (
            call.s21_run(Event.b, state),
            call.s211_entry(state),
        )
    )


@pytest.mark.asyncio
async def test_s21_c() -> None:
    mock.reset_mock()

    state = State(foo=0)

    node = await hsm_handle_event(s0.s2.s21, Event.c, state)
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


@pytest.mark.asyncio
async def test_s21_e() -> None:
    mock.reset_mock()

    state = State(foo=0)

    node = await hsm_handle_event(s0.s2.s21, Event.e, state)
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


@pytest.mark.asyncio
async def test_s21_f() -> None:
    mock.reset_mock()

    state = State(foo=0)

    node = await hsm_handle_event(s0.s2.s21, Event.f, state)
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


@pytest.mark.asyncio
async def test_s21_h_foo_0() -> None:
    mock.reset_mock()

    state = State(foo=0)

    node = await hsm_handle_event(s0.s2.s21, Event.h, state)
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


@pytest.mark.asyncio
async def test_s21_h_foo_1() -> None:
    mock.reset_mock()

    state = State(foo=1)

    node = await hsm_handle_event(s0.s2.s21, Event.h, state)
    assert node is s0.s2.s21
    assert state.foo == 1

    mock.assert_has_calls((call.s21_run(Event.h, state),))
