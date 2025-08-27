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
from examples.samek.state import Context
from spirea.sync import hsm_handle_entries, hsm_handle_event


def init_context(context: Context) -> None:
	"""This would normally be done by entry functions, but we bypass for testing."""
	s0._context = context
	s0.s1._context = context
	s0.s1.s11._context = context
	s0.s2._context = context
	s0.s2.s21._context = context
	s0.s2.s21.s211._context = context


def test_transitions_run() -> None:
	# Initialize the state machine with initial state
	context = Context(foo=0)
	init_context(context)
	node = hsm_handle_entries(s0)
	assert node is s0.s1.s11

	node = hsm_handle_event(node, EventB())
	assert node is s0.s1.s11

	node = hsm_handle_event(node, EventG())
	assert node is s0.s2.s21.s211

	node = hsm_handle_event(node, EventH())
	assert node is s0.s2.s21.s211
	assert context.foo == 1

	node = hsm_handle_event(node, EventG())
	assert node is s0

	node = hsm_handle_event(node, EventG())
	assert node is s0
	assert context.foo == 1


@pytest.mark.parametrize(
	"event", (EventA(), EventB(), EventC(), EventD(), EventF(), EventG(), EventH())
)
def test_s0_unhandled(event: Event) -> None:
	"""All events but e are ignored in s0."""

	mock.reset_mock()

	context = Context(foo=0)
	init_context(context)

	node = hsm_handle_event(s0, event)
	assert node is s0
	assert context.foo == 0

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

	context = Context(foo=0)
	init_context(context)

	node = hsm_handle_event(s0, EventE())
	assert node is s0.s2.s21.s211
	assert context.foo == 0

	mock.assert_has_calls(
		(
			call.s0_run(EventE(), context),
			call.s2_entry(context),
			call.s21_entry(context),
			call.s211_entry(context),
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

	context = Context(foo=foo)
	init_context(context)

	node = hsm_handle_event(s0.s1.s11, EventA())
	assert node is s0.s1.s11
	assert context.foo == 0

	mock.assert_has_calls(
		(
			call.s1_run(EventA(), context),
			call.s11_exit(context),
			call.s1_exit(context),
			call.s1_entry(context),
			call.s11_entry(context),
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

	context = Context(foo=foo)
	init_context(context)

	node = hsm_handle_event(s0.s1.s11, EventB())
	assert node is s0.s1.s11
	assert context.foo == 0

	mock.assert_has_calls(
		(
			call.s1_run(EventB(), context),
			call.s11_exit(context),
			call.s11_entry(context),
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

	context = Context(foo=foo)
	init_context(context)

	node = hsm_handle_event(s0.s1.s11, EventC())
	assert node is s0.s2.s21.s211
	assert context.foo == 0

	mock.assert_has_calls(
		(
			call.s1_run(EventC(), context),
			call.s11_exit(context),
			call.s1_exit(context),
			call.s2_entry(context),
			call.s21_entry(context),
			call.s211_entry(context),
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

	context = Context(foo=foo)
	init_context(context)

	node = hsm_handle_event(s0.s1.s11, EventD())
	assert node is s0
	assert context.foo == 0

	mock.assert_has_calls(
		(
			call.s1_run(EventD(), context),
			call.s11_exit(context),
			call.s1_exit(context),
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

	context = Context(foo=foo)
	init_context(context)

	node = hsm_handle_event(s0.s1.s11, EventE())
	assert node is s0.s2.s21.s211
	assert context.foo == 0

	mock.assert_has_calls(
		(
			call.s0_run(EventE(), context),
			call.s11_exit(context),
			call.s1_exit(context),
			call.s2_entry(context),
			call.s21_entry(context),
			call.s211_entry(context),
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

	context = Context(foo=foo)
	init_context(context)

	node = hsm_handle_event(s0.s1.s11, EventF())
	assert node is s0.s2.s21.s211
	assert context.foo == 0

	mock.assert_has_calls(
		(
			call.s1_run(EventF(), context),
			call.s11_exit(context),
			call.s1_exit(context),
			call.s2_entry(context),
			call.s21_entry(context),
			call.s211_entry(context),
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

	context = Context(foo=foo)
	init_context(context)

	node = hsm_handle_event(s0.s1.s11, EventG())
	assert node is s0.s2.s21.s211
	assert context.foo == 0

	mock.assert_has_calls(
		(
			call.s11_run(EventG(), context),
			call.s11_exit(context),
			call.s1_exit(context),
			call.s2_entry(context),
			call.s21_entry(context),
			call.s211_entry(context),
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

	context = Context(foo=foo)
	init_context(context)

	node = hsm_handle_event(s0.s1.s11, EventH())
	assert node is s0.s1.s11
	assert context.foo == foo

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

	context = Context(foo=foo)
	init_context(context)

	node = hsm_handle_event(s0.s2.s21.s211, EventA())
	assert node is s0.s2.s21.s211
	assert context.foo == foo

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

	context = Context(foo=foo)
	init_context(context)

	node = hsm_handle_event(s0.s2.s21.s211, EventB())
	assert node is s0.s2.s21.s211
	assert context.foo == foo

	mock.assert_has_calls(
		(
			call.s21_run(EventB(), context),
			call.s211_exit(context),
			call.s211_entry(context),
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

	context = Context(foo=foo)
	init_context(context)

	node = hsm_handle_event(s0.s2.s21.s211, EventC())
	assert node is s0.s1.s11
	assert context.foo == foo

	mock.assert_has_calls(
		(
			call.s2_run(EventC(), context),
			call.s211_exit(context),
			call.s21_exit(context),
			call.s2_exit(context),
			call.s1_entry(context),
			call.s11_entry(context),
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

	context = Context(foo=foo)
	init_context(context)

	node = hsm_handle_event(s0.s2.s21.s211, EventD())
	assert node is s0.s2.s21
	assert context.foo == foo

	mock.assert_has_calls(
		(
			call.s211_run(EventD(), context),
			call.s211_exit(context),
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

	context = Context(foo=foo)
	init_context(context)

	node = hsm_handle_event(s0.s2.s21.s211, EventE())
	assert node is s0.s2.s21.s211
	assert context.foo == foo

	mock.assert_has_calls(
		(
			call.s0_run(EventE(), context),
			call.s211_exit(context),
			call.s21_exit(context),
			call.s2_exit(context),
			call.s2_entry(context),
			call.s21_entry(context),
			call.s211_entry(context),
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

	context = Context(foo=foo)
	init_context(context)

	node = hsm_handle_event(s0.s2.s21.s211, EventF())
	assert node is s0.s1.s11
	assert context.foo == foo

	mock.assert_has_calls(
		(
			call.s2_run(EventF(), context),
			call.s211_exit(context),
			call.s21_exit(context),
			call.s2_exit(context),
			call.s1_entry(context),
			call.s11_entry(context),
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

	context = Context(foo=foo)
	init_context(context)

	node = hsm_handle_event(s0.s2.s21.s211, EventG())
	assert node is s0
	assert context.foo == foo

	mock.assert_has_calls(
		(
			call.s211_run(EventG(), context),
			call.s211_exit(context),
			call.s21_exit(context),
			call.s2_exit(context),
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

	context = Context(foo=0)
	init_context(context)

	node = hsm_handle_event(s0.s2.s21.s211, EventH())
	assert node is s0.s2.s21.s211
	assert context.foo == 1

	mock.assert_has_calls(
		(
			call.s21_run(EventH(), context),
			call.s211_exit(context),
			call.s21_exit(context),
			call.s21_entry(context),
			call.s211_entry(context),
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

	context = Context(foo=1)
	init_context(context)

	node = hsm_handle_event(s0.s2.s21.s211, EventH())
	assert node is s0.s2.s21.s211
	assert context.foo == 1

	mock.assert_has_calls((call.s21_run(EventH(), context),))

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

	context = Context(foo=0)
	init_context(context)

	node = hsm_handle_event(s0, event)
	assert node is s0
	assert context.foo == 0

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

	context = Context(foo=0)
	init_context(context)

	node = hsm_handle_event(s0.s2.s21, EventB())
	assert node is s0.s2.s21.s211
	assert context.foo == 0

	mock.assert_has_calls(
		(
			call.s21_run(EventB(), context),
			call.s211_entry(context),
		)
	)


def test_s21_c() -> None:
	mock.reset_mock()

	context = Context(foo=0)
	init_context(context)

	node = hsm_handle_event(s0.s2.s21, EventC())
	assert node is s0.s1.s11
	assert context.foo == 0

	mock.assert_has_calls(
		(
			call.s2_run(EventC(), context),
			call.s21_exit(context),
			call.s2_exit(context),
			call.s1_entry(context),
			call.s11_entry(context),
		)
	)


def test_s21_e() -> None:
	mock.reset_mock()

	context = Context(foo=0)
	init_context(context)

	node = hsm_handle_event(s0.s2.s21, EventE())
	assert node is s0.s2.s21.s211
	assert context.foo == 0

	mock.assert_has_calls(
		(
			call.s0_run(EventE(), context),
			call.s21_exit(context),
			call.s2_exit(context),
			call.s2_entry(context),
			call.s21_entry(context),
			call.s211_entry(context),
		)
	)


def test_s21_f() -> None:
	mock.reset_mock()

	context = Context(foo=0)
	init_context(context)

	node = hsm_handle_event(s0.s2.s21, EventF())
	assert node is s0.s1.s11
	assert context.foo == 0

	mock.assert_has_calls(
		(
			call.s2_run(EventF(), context),
			call.s21_exit(context),
			call.s2_exit(context),
			call.s1_entry(context),
			call.s11_entry(context),
		)
	)


def test_s21_h_foo_0() -> None:
	mock.reset_mock()

	context = Context(foo=0)
	init_context(context)

	node = hsm_handle_event(s0.s2.s21, EventH())
	assert node is s0.s2.s21.s211
	assert context.foo == 1

	mock.assert_has_calls(
		(
			call.s21_run(EventH(), context),
			call.s21_exit(context),
			call.s21_entry(context),
			call.s211_entry(context),
		)
	)


def test_s21_h_foo_1() -> None:
	mock.reset_mock()

	context = Context(foo=1)
	init_context(context)

	node = hsm_handle_event(s0.s2.s21, EventH())
	assert node is s0.s2.s21
	assert context.foo == 1

	mock.assert_has_calls((call.s21_run(EventH(), context),))
