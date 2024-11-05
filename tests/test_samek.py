from unittest.mock import call
import pytest

from hsm.sync import hsm_handle_event, hsm_handle_entries

from examples.samek.events import Event
from examples.samek.state import State
from examples.samek.hsm import s0, mock


def test_transitions_run() -> None:
    state = State(foo=0)

    node = hsm_handle_entries(s0, state)
    assert node is s0.s1.s11

    node = hsm_handle_event(node, Event.b, state)
    assert node is s0.s1.s11

    node = hsm_handle_event(node, Event.g, state)
    assert node is s0.s2.s21.s211

    node = hsm_handle_event(node, Event.h, state)
    assert node is s0.s2.s21.s211
    assert state.foo == 1

    node = hsm_handle_event(node, Event.g, state)
    assert node is s0

    node = hsm_handle_event(node, Event.g, state)
    assert node is s0
    assert state.foo == 1


@pytest.mark.parametrize("event", set(Event) - {Event.e})
def test_s0_unhandled(event: Event) -> None:
    """All events but e are ignored in s0."""

    mock.reset_mock()

    state = State(foo=0)

    node = hsm_handle_event(s0, event, state)
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

    node = hsm_handle_event(s0, Event.e, state)
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

    node = hsm_handle_event(s0.s1.s11, Event.a, state)
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

    node = hsm_handle_event(s0.s1.s11, Event.b, state)
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

    node = hsm_handle_event(s0.s1.s11, Event.c, state)
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

    node = hsm_handle_event(s0.s1.s11, Event.d, state)
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

    node = hsm_handle_event(s0.s1.s11, Event.e, state)
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

    node = hsm_handle_event(s0.s1.s11, Event.f, state)
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

    node = hsm_handle_event(s0.s1.s11, Event.g, state)
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

    node = hsm_handle_event(s0.s1.s11, Event.h, state)
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

    node = hsm_handle_event(s0.s2.s21.s211, Event.a, state)
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

    node = hsm_handle_event(s0.s2.s21.s211, Event.b, state)
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

    node = hsm_handle_event(s0.s2.s21.s211, Event.c, state)
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

    node = hsm_handle_event(s0.s2.s21.s211, Event.d, state)
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

    node = hsm_handle_event(s0.s2.s21.s211, Event.e, state)
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

    node = hsm_handle_event(s0.s2.s21.s211, Event.f, state)
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

    node = hsm_handle_event(s0.s2.s21.s211, Event.g, state)
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

    node = hsm_handle_event(s0.s2.s21.s211, Event.h, state)
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

    node = hsm_handle_event(s0.s2.s21.s211, Event.h, state)
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

    node = hsm_handle_event(s0, event, state)
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

    node = hsm_handle_event(s0.s2.s21, Event.b, state)
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

    node = hsm_handle_event(s0.s2.s21, Event.c, state)
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

    node = hsm_handle_event(s0.s2.s21, Event.e, state)
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

    node = hsm_handle_event(s0.s2.s21, Event.f, state)
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

    node = hsm_handle_event(s0.s2.s21, Event.h, state)
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

    node = hsm_handle_event(s0.s2.s21, Event.h, state)
    assert node is s0.s2.s21
    assert state.foo == 1

    mock.assert_has_calls((call.s21_run(Event.h, state),))
