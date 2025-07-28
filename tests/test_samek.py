# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from unittest.mock import call

import pytest

from examples.samek.events import (
	Event,
	EventA,
	EventB,
	EventC,
	EventD,
	EventE,
	EventF,
	EventG,
	EventH,
)
from examples.samek.hsm import mock, s0
from examples.samek.state import State
from spirea.sync import hsm_handle_entries, hsm_handle_event


def test_transitions_run() -> None:
	state = State(foo=0)

	node = hsm_handle_entries(s0, state)
	assert node is s0.s1.s11

	node = hsm_handle_event(node, EventB(), state)
	assert node is s0.s1.s11

	node = hsm_handle_event(node, EventG(), state)
	assert node is s0.s2.s21.s211

	node = hsm_handle_event(node, EventH(), state)
	assert node is s0.s2.s21.s211
	assert state.foo == 1

	node = hsm_handle_event(node, EventG(), state)
	assert node is s0

	node = hsm_handle_event(node, EventG(), state)
	assert node is s0
	assert state.foo == 1


@pytest.mark.parametrize(
	"event", (EventA(), EventB(), EventC(), EventD(), EventF(), EventG(), EventH())
)
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

	node = hsm_handle_event(s0, EventE(), state)
	assert node is s0.s2.s21.s211
	assert state.foo == 0

	mock.assert_has_calls(
		(
			call.s0_run(EventE(), state),
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

	node = hsm_handle_event(s0.s1.s11, EventA(), state)
	assert node is s0.s1.s11
	assert state.foo == 0

	mock.assert_has_calls(
		(
			call.s1_run(EventA(), state),
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

	node = hsm_handle_event(s0.s1.s11, EventB(), state)
	assert node is s0.s1.s11
	assert state.foo == 0

	mock.assert_has_calls(
		(
			call.s1_run(EventB(), state),
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

	node = hsm_handle_event(s0.s1.s11, EventC(), state)
	assert node is s0.s2.s21.s211
	assert state.foo == 0

	mock.assert_has_calls(
		(
			call.s1_run(EventC(), state),
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

	node = hsm_handle_event(s0.s1.s11, EventD(), state)
	assert node is s0
	assert state.foo == 0

	mock.assert_has_calls(
		(
			call.s1_run(EventD(), state),
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

	node = hsm_handle_event(s0.s1.s11, EventE(), state)
	assert node is s0.s2.s21.s211
	assert state.foo == 0

	mock.assert_has_calls(
		(
			call.s0_run(EventE(), state),
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

	node = hsm_handle_event(s0.s1.s11, EventF(), state)
	assert node is s0.s2.s21.s211
	assert state.foo == 0

	mock.assert_has_calls(
		(
			call.s1_run(EventF(), state),
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

	node = hsm_handle_event(s0.s1.s11, EventG(), state)
	assert node is s0.s2.s21.s211
	assert state.foo == 0

	mock.assert_has_calls(
		(
			call.s11_run(EventG(), state),
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

	node = hsm_handle_event(s0.s1.s11, EventH(), state)
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

	node = hsm_handle_event(s0.s2.s21.s211, EventA(), state)
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

	node = hsm_handle_event(s0.s2.s21.s211, EventB(), state)
	assert node is s0.s2.s21.s211
	assert state.foo == foo

	mock.assert_has_calls(
		(
			call.s21_run(EventB(), state),
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

	node = hsm_handle_event(s0.s2.s21.s211, EventC(), state)
	assert node is s0.s1.s11
	assert state.foo == foo

	mock.assert_has_calls(
		(
			call.s2_run(EventC(), state),
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

	node = hsm_handle_event(s0.s2.s21.s211, EventD(), state)
	assert node is s0.s2.s21
	assert state.foo == foo

	mock.assert_has_calls(
		(
			call.s211_run(EventD(), state),
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

	node = hsm_handle_event(s0.s2.s21.s211, EventE(), state)
	assert node is s0.s2.s21.s211
	assert state.foo == foo

	mock.assert_has_calls(
		(
			call.s0_run(EventE(), state),
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

	node = hsm_handle_event(s0.s2.s21.s211, EventF(), state)
	assert node is s0.s1.s11
	assert state.foo == foo

	mock.assert_has_calls(
		(
			call.s2_run(EventF(), state),
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

	node = hsm_handle_event(s0.s2.s21.s211, EventG(), state)
	assert node is s0
	assert state.foo == foo

	mock.assert_has_calls(
		(
			call.s211_run(EventG(), state),
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

	node = hsm_handle_event(s0.s2.s21.s211, EventH(), state)
	assert node is s0.s2.s21.s211
	assert state.foo == 1

	mock.assert_has_calls(
		(
			call.s21_run(EventH(), state),
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

	node = hsm_handle_event(s0.s2.s21.s211, EventH(), state)
	assert node is s0.s2.s21.s211
	assert state.foo == 1

	mock.assert_has_calls((call.s21_run(EventH(), state),))

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


@pytest.mark.parametrize("event", (EventA(), EventD(), EventG()))
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

	node = hsm_handle_event(s0.s2.s21, EventB(), state)
	assert node is s0.s2.s21.s211
	assert state.foo == 0

	mock.assert_has_calls(
		(
			call.s21_run(EventB(), state),
			call.s211_entry(state),
		)
	)


def test_s21_c() -> None:
	mock.reset_mock()

	state = State(foo=0)

	node = hsm_handle_event(s0.s2.s21, EventC(), state)
	assert node is s0.s1.s11
	assert state.foo == 0

	mock.assert_has_calls(
		(
			call.s2_run(EventC(), state),
			call.s21_exit(state),
			call.s2_exit(state),
			call.s1_entry(state),
			call.s11_entry(state),
		)
	)


def test_s21_e() -> None:
	mock.reset_mock()

	state = State(foo=0)

	node = hsm_handle_event(s0.s2.s21, EventE(), state)
	assert node is s0.s2.s21.s211
	assert state.foo == 0

	mock.assert_has_calls(
		(
			call.s0_run(EventE(), state),
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

	node = hsm_handle_event(s0.s2.s21, EventF(), state)
	assert node is s0.s1.s11
	assert state.foo == 0

	mock.assert_has_calls(
		(
			call.s2_run(EventF(), state),
			call.s21_exit(state),
			call.s2_exit(state),
			call.s1_entry(state),
			call.s11_entry(state),
		)
	)


def test_s21_h_foo_0() -> None:
	mock.reset_mock()

	state = State(foo=0)

	node = hsm_handle_event(s0.s2.s21, EventH(), state)
	assert node is s0.s2.s21.s211
	assert state.foo == 1

	mock.assert_has_calls(
		(
			call.s21_run(EventH(), state),
			call.s21_exit(state),
			call.s21_entry(state),
			call.s211_entry(state),
		)
	)


def test_s21_h_foo_1() -> None:
	mock.reset_mock()

	state = State(foo=1)

	node = hsm_handle_event(s0.s2.s21, EventH(), state)
	assert node is s0.s2.s21
	assert state.foo == 1

	mock.assert_has_calls((call.s21_run(EventH(), state),))
