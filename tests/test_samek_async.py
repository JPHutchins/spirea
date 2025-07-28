# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from dataclasses import dataclass  # noqa: I001
from typing import Awaitable as A
from typing import Callable
from typing import Literal as L
from typing import NamedTuple, Type
from unittest.mock import Mock, call

import pytest

from spirea.asyncio import HSMStatus, Node, hsm_handle_entries, hsm_handle_event


class EventA(NamedTuple): ...


class EventB(NamedTuple): ...


class EventC(NamedTuple): ...


class EventD(NamedTuple): ...


class EventE(NamedTuple): ...


class EventF(NamedTuple): ...


class EventG(NamedTuple): ...


class EventH(NamedTuple): ...


type Event = EventA | EventB | EventC | EventD | EventE | EventF | EventG | EventH


@dataclass
class State:
	foo: int


mock = Mock()


async def s21_h(
	event: EventH, state: State
) -> L[HSMStatus.SELF_TRANSITION] | L[HSMStatus.NO_TRANSITION]:
	mock.s21_run(event, state)
	if state.foo == 0:
		state.foo = 1
		return HSMStatus.SELF_TRANSITION
	else:
		return HSMStatus.NO_TRANSITION


async def s1_a(event: EventA, state: State | None) -> L[HSMStatus.SELF_TRANSITION]:
	mock.s1_run(event, state)
	return HSMStatus.SELF_TRANSITION


async def s1_b(event: EventB, state: State | None) -> Type["s0.s1.s11"]:
	mock.s1_run(event, state)
	return s0.s1.s11


async def s1_c(event: EventC, state: State | None) -> Type["s0.s2"]:
	mock.s1_run(event, state)
	return s0.s2


async def s1_d(event: EventD, state: State | None) -> Type["s0"]:
	mock.s1_run(event, state)
	return s0


async def s1_f(event: EventF, state: State | None) -> Type["s0.s2.s21.s211"]:
	mock.s1_run(event, state)
	return s0.s2.s21.s211


async def s11_g(event: EventG, state: State | None) -> Type["s0.s2.s21.s211"]:
	mock.s11_run(event, state)
	return s0.s2.s21.s211


async def s2_c(event: EventC, state: State | None) -> Type["s0.s1"]:
	mock.s2_run(event, state)
	return s0.s1


async def s2_f(event: EventF, state: State | None) -> Type["s0.s1.s11"]:
	mock.s2_run(event, state)
	return s0.s1.s11


async def s21_b(event: EventB, state: State | None) -> Type["s0.s2.s21.s211"]:
	mock.s21_run(event, state)
	return s0.s2.s21.s211


async def s211_d(event: EventD, state: State | None) -> Type["s0.s2.s21"]:
	mock.s211_run(event, state)
	return s0.s2.s21


async def s211_g(event: EventG, state: State | None) -> Type["s0"]:
	mock.s211_run(event, state)
	return s0


class s0(Node[Event, State]):
	@staticmethod
	async def entry(state: State | None = None) -> Type[Node[Event, State]]:
		mock.s0_entry(state)
		return s0.s1

	class EventHandlers:
		@staticmethod
		async def _e(event: EventE, state: State | None) -> Type["s0.s2.s21.s211"]:
			mock.s0_run(event, state)
			return s0.s2.s21.s211

		e: Callable[[EventE, State | None], A[Type["s0.s2.s21.s211"]]] = _e

	@staticmethod
	async def exit(state: State | None = None) -> None:
		mock.s0_exit(state)

	class s1(Node[Event, State]):
		@staticmethod
		async def entry(state: State | None = None) -> Type[Node[Event, State]]:
			mock.s1_entry(state)
			return s0.s1.s11

		class EventHandlers:
			a: Callable[[EventA, State | None], A[L[HSMStatus.SELF_TRANSITION]]] = s1_a
			b: Callable[[EventB, State | None], A[Type["s0.s1.s11"]]] = s1_b
			c: Callable[[EventC, State | None], A[Type["s0.s2"]]] = s1_c
			d: Callable[[EventD, State | None], A[Type["s0"]]] = s1_d
			f: Callable[[EventF, State | None], A[Type["s0.s2.s21.s211"]]] = s1_f

		@staticmethod
		async def exit(state: State | None = None) -> None:
			mock.s1_exit(state)

		class s11(Node[Event, State]):
			@staticmethod
			async def entry(state: State | None = None) -> Type[Node[Event, State]]:
				mock.s11_entry(state)
				return s0.s1.s11

			class EventHandlers:
				g: Callable[[EventG, State | None], A[Type["s0.s2.s21.s211"]]] = s11_g

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
			c: Callable[[EventC, State | None], A[Type["s0.s1"]]] = s2_c
			f: Callable[[EventF, State | None], A[Type["s0.s1.s11"]]] = s2_f

		@staticmethod
		async def exit(state: State | None = None) -> None:
			mock.s2_exit(state)

		class s21(Node[Event, State]):
			@staticmethod
			async def entry(state: State | None = None) -> Type[Node[Event, State]]:
				mock.s21_entry(state)
				return s0.s2.s21.s211

			class EventHandlers:
				b: Callable[[EventB, State | None], A[Type["s0.s2.s21.s211"]]] = s21_b
				h: Callable[
					[EventH, State],
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
					d: Callable[[EventD, State | None], A[Type["s0.s2.s21"]]] = s211_d
					g: Callable[[EventG, State | None], A[Type["s0"]]] = s211_g

				@staticmethod
				async def exit(state: State | None = None) -> None:
					mock.s211_exit(state)


@pytest.mark.asyncio
async def test_transitions_run() -> None:
	state = State(foo=0)

	node = await hsm_handle_entries(s0, state)
	assert node is s0.s1.s11

	node = await hsm_handle_event(node, EventB(), state)
	assert node is s0.s1.s11

	node = await hsm_handle_event(node, EventG(), state)
	assert node is s0.s2.s21.s211

	node = await hsm_handle_event(node, EventH(), state)
	assert node is s0.s2.s21.s211
	assert state.foo == 1

	node = await hsm_handle_event(node, EventG(), state)
	assert node is s0

	node = await hsm_handle_event(node, EventG(), state)
	assert node is s0
	assert state.foo == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
	"event", (EventA(), EventB(), EventC(), EventD(), EventF(), EventG(), EventH())
)
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

	node = await hsm_handle_event(s0, EventE(), state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s11_a(foo: int) -> None:
	mock.reset_mock()

	state = State(foo=foo)

	node = await hsm_handle_event(s0.s1.s11, EventA(), state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s11_b(foo: int) -> None:
	mock.reset_mock()

	state = State(foo=foo)

	node = await hsm_handle_event(s0.s1.s11, EventB(), state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s11_c(foo: int) -> None:
	mock.reset_mock()

	state = State(foo=foo)

	node = await hsm_handle_event(s0.s1.s11, EventC(), state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s11_d(foo: int) -> None:
	mock.reset_mock()

	state = State(foo=foo)

	node = await hsm_handle_event(s0.s1.s11, EventD(), state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s11_e(foo: int) -> None:
	mock.reset_mock()

	state = State(foo=foo)

	node = await hsm_handle_event(s0.s1.s11, EventE(), state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s11_f(foo: int) -> None:
	mock.reset_mock()

	state = State(foo=foo)

	node = await hsm_handle_event(s0.s1.s11, EventF(), state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s11_g(foo: int) -> None:
	mock.reset_mock()

	state = State(foo=foo)

	node = await hsm_handle_event(s0.s1.s11, EventG(), state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s11_h(foo: int) -> None:
	mock.reset_mock()

	state = State(foo=foo)

	node = await hsm_handle_event(s0.s1.s11, EventH(), state)
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

	node = await hsm_handle_event(s0.s2.s21.s211, EventA(), state)
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

	node = await hsm_handle_event(s0.s2.s21.s211, EventB(), state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s211_c(foo: int) -> None:
	mock.reset_mock()

	state = State(foo=foo)

	node = await hsm_handle_event(s0.s2.s21.s211, EventC(), state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s211_d(foo: int) -> None:
	mock.reset_mock()

	state = State(foo=foo)

	node = await hsm_handle_event(s0.s2.s21.s211, EventD(), state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_s211_e(foo: int) -> None:
	mock.reset_mock()

	state = State(foo=foo)

	node = await hsm_handle_event(s0.s2.s21.s211, EventE(), state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_211_f(foo: int) -> None:
	mock.reset_mock()

	state = State(foo=foo)

	node = await hsm_handle_event(s0.s2.s21.s211, EventF(), state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("foo", (0, 1))
async def test_211_g(foo: int) -> None:
	mock.reset_mock()

	state = State(foo=foo)

	node = await hsm_handle_event(s0.s2.s21.s211, EventG(), state)
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


@pytest.mark.asyncio
async def test_211_h_foo_0() -> None:
	mock.reset_mock()

	state = State(foo=0)

	node = await hsm_handle_event(s0.s2.s21.s211, EventH(), state)
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


@pytest.mark.asyncio
async def test_211_h_foo_1() -> None:
	mock.reset_mock()

	state = State(foo=1)

	node = await hsm_handle_event(s0.s2.s21.s211, EventH(), state)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("event", (EventA(), EventD(), EventG()))
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

	node = await hsm_handle_event(s0.s2.s21, EventB(), state)
	assert node is s0.s2.s21.s211
	assert state.foo == 0

	mock.assert_has_calls(
		(
			call.s21_run(EventB(), state),
			call.s211_entry(state),
		)
	)


@pytest.mark.asyncio
async def test_s21_c() -> None:
	mock.reset_mock()

	state = State(foo=0)

	node = await hsm_handle_event(s0.s2.s21, EventC(), state)
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


@pytest.mark.asyncio
async def test_s21_e() -> None:
	mock.reset_mock()

	state = State(foo=0)

	node = await hsm_handle_event(s0.s2.s21, EventE(), state)
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


@pytest.mark.asyncio
async def test_s21_f() -> None:
	mock.reset_mock()

	state = State(foo=0)

	node = await hsm_handle_event(s0.s2.s21, EventF(), state)
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


@pytest.mark.asyncio
async def test_s21_h_foo_0() -> None:
	mock.reset_mock()

	state = State(foo=0)

	node = await hsm_handle_event(s0.s2.s21, EventH(), state)
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


@pytest.mark.asyncio
async def test_s21_h_foo_1() -> None:
	mock.reset_mock()

	state = State(foo=1)

	node = await hsm_handle_event(s0.s2.s21, EventH(), state)
	assert node is s0.s2.s21
	assert state.foo == 1

	mock.assert_has_calls((call.s21_run(EventH(), state),))
	assert state.foo == 1

	mock.assert_has_calls((call.s21_run(EventH(), state),))
	mock.assert_has_calls((call.s21_run(EventH(), state),))
