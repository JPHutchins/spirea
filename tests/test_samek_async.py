# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from dataclasses import dataclass  # noqa: I001
from enum import IntEnum
from typing import Awaitable as A
from typing import Callable
from typing import Literal as L
from typing import Type
from unittest.mock import Mock, call

import pytest

from spirea.asyncio import HSMStatus, Node, hsm_handle_entries, hsm_handle_event


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


async def s21_h(
	event: L[Event.h], state: State
) -> L[HSMStatus.SELF_TRANSITION] | L[HSMStatus.NO_TRANSITION]:
	mock.s21_run(event, state)
	if state.foo == 0:
		state.foo = 1
		return HSMStatus.SELF_TRANSITION
	else:
		return HSMStatus.NO_TRANSITION


async def s1_a(event: L[Event.a], state: State | None) -> L[HSMStatus.SELF_TRANSITION]:
	mock.s1_run(event, state)
	return HSMStatus.SELF_TRANSITION


async def s1_b(event: L[Event.b], state: State | None) -> Type["s0.s1.s11"]:
	mock.s1_run(event, state)
	return s0.s1.s11


async def s1_c(event: L[Event.c], state: State | None) -> Type["s0.s2"]:
	mock.s1_run(event, state)
	return s0.s2


async def s1_d(event: L[Event.d], state: State | None) -> Type["s0"]:
	mock.s1_run(event, state)
	return s0


async def s1_f(event: L[Event.f], state: State | None) -> Type["s0.s2.s21.s211"]:
	mock.s1_run(event, state)
	return s0.s2.s21.s211


async def s11_g(event: L[Event.g], state: State | None) -> Type["s0.s2.s21.s211"]:
	mock.s11_run(event, state)
	return s0.s2.s21.s211


async def s2_c(event: L[Event.c], state: State | None) -> Type["s0.s1"]:
	mock.s2_run(event, state)
	return s0.s1


async def s2_f(event: L[Event.f], state: State | None) -> Type["s0.s1.s11"]:
	mock.s2_run(event, state)
	return s0.s1.s11


async def s21_b(event: L[Event.b], state: State | None) -> Type["s0.s2.s21.s211"]:
	mock.s21_run(event, state)
	return s0.s2.s21.s211


async def s211_d(event: L[Event.d], state: State | None) -> Type["s0.s2.s21"]:
	mock.s211_run(event, state)
	return s0.s2.s21


async def s211_g(event: L[Event.g], state: State | None) -> Type["s0"]:
	mock.s211_run(event, state)
	return s0


class s0(Node[Event, State]):
	@staticmethod
	async def entry(state: State | None = None) -> Type[Node[Event, State]]:
		mock.s0_entry(state)
		return s0.s1

	class EventHandlers:
		@staticmethod
		async def _e(event: L[Event.e], state: State | None) -> Type["s0.s2.s21.s211"]:
			mock.s0_run(event, state)
			return s0.s2.s21.s211

		e: Callable[[L[Event.e], State | None], A[Type["s0.s2.s21.s211"]]] = _e

	@staticmethod
	async def exit(state: State | None = None) -> None:
		mock.s0_exit(state)

	class s1(Node[Event, State]):
		@staticmethod
		async def entry(state: State | None = None) -> Type[Node[Event, State]]:
			mock.s1_entry(state)
			return s0.s1.s11

		class EventHandlers:
			a: Callable[[L[Event.a], State | None], A[L[HSMStatus.SELF_TRANSITION]]] = s1_a
			b: Callable[[L[Event.b], State | None], A[Type["s0.s1.s11"]]] = s1_b
			c: Callable[[L[Event.c], State | None], A[Type["s0.s2"]]] = s1_c
			d: Callable[[L[Event.d], State | None], A[Type["s0"]]] = s1_d
			f: Callable[[L[Event.f], State | None], A[Type["s0.s2.s21.s211"]]] = s1_f

		@staticmethod
		async def exit(state: State | None = None) -> None:
			mock.s1_exit(state)

		class s11(Node[Event, State]):
			@staticmethod
			async def entry(state: State | None = None) -> Type[Node[Event, State]]:
				mock.s11_entry(state)
				return s0.s1.s11

			class EventHandlers:
				g: Callable[[L[Event.g], State | None], A[Type["s0.s2.s21.s211"]]] = s11_g

			@staticmethod
			async def exit(state: State) -> None:  # type: ignore[override]
				mock.s11_exit(state)
				if state.foo == 1:
					state.foo = 0

	class s2(Node[Event, State]):
		@staticmethod
		async def entry(state: State | None = None) -> Type[Node[Event, State]]:
			mock.s2_entry(state)
			return s0.s2.s21

		class EventHandlers:
			c: Callable[[L[Event.c], State | None], A[Type["s0.s1"]]] = s2_c
			f: Callable[[L[Event.f], State | None], A[Type["s0.s1.s11"]]] = s2_f

		@staticmethod
		async def exit(state: State | None = None) -> None:
			mock.s2_exit(state)

		class s21(Node[Event, State]):
			@staticmethod
			async def entry(state: State | None = None) -> Type[Node[Event, State]]:
				mock.s21_entry(state)
				return s0.s2.s21.s211

			class EventHandlers:
				b: Callable[[L[Event.b], State | None], A[Type["s0.s2.s21.s211"]]] = s21_b
				h: Callable[
					[L[Event.h], State],
					A[L[HSMStatus.SELF_TRANSITION] | L[HSMStatus.NO_TRANSITION]],
				] = s21_h

			@staticmethod
			async def exit(state: State | None = None) -> None:
				mock.s21_exit(state)

			class s211(Node[Event, State]):
				@staticmethod
				async def entry(state: State | None = None) -> Type[Node[Event, State]]:
					mock.s211_entry(state)
					return s0.s2.s21.s211

				class EventHandlers:
					d: Callable[[L[Event.d], State | None], A[Type["s0.s2.s21"]]] = s211_d
					g: Callable[[L[Event.g], State | None], A[Type["s0"]]] = s211_g

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
@pytest.mark.parametrize("event", set(Event) - {Event.b, Event.c, Event.e, Event.f, Event.h})
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
	assert state.foo == 1

	mock.assert_has_calls((call.s21_run(Event.h, state),))

	mock.assert_has_calls((call.s21_run(Event.h, state),))
	mock.assert_has_calls((call.s21_run(Event.h, state),))
	mock.assert_has_calls((call.s21_run(Event.h, state),))
	mock.assert_has_calls((call.s21_run(Event.h, state),))
	mock.assert_has_calls((call.s21_run(Event.h, state),))
	mock.assert_has_calls((call.s21_run(Event.h, state),))
	mock.assert_has_calls((call.s21_run(Event.h, state),))
	mock.assert_has_calls((call.s21_run(Event.h, state),))
	mock.assert_has_calls((call.s21_run(Event.h, state),))
	mock.assert_has_calls((call.s21_run(Event.h, state),))
	mock.assert_has_calls((call.s21_run(Event.h, state),))
