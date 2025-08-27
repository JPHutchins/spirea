# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from dataclasses import dataclass  # noqa: I001
from typing import Awaitable as A, ClassVar
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
class Context:
	foo: int


mock = Mock()


async def s21_h(
	event: EventH, context: Context
) -> L[HSMStatus.SELF_TRANSITION] | L[HSMStatus.NO_TRANSITION]:
	mock.s21_run(event, s0._context)
	if s0._context.foo == 0:
		s0._context.foo = 1
		return HSMStatus.SELF_TRANSITION
	else:
		return HSMStatus.NO_TRANSITION


async def s1_a(event: EventA, context: Context) -> L[HSMStatus.SELF_TRANSITION]:
	mock.s1_run(event, s0._context)
	return HSMStatus.SELF_TRANSITION


async def s1_b(event: EventB, context: Context) -> Type["s0.s1.s11"]:
	mock.s1_run(event, s0._context)
	return s0.s1.s11


async def s1_c(event: EventC, context: Context) -> Type["s0.s2"]:
	mock.s1_run(event, s0._context)
	return s0.s2


async def s1_d(event: EventD, context: Context) -> Type["s0"]:
	mock.s1_run(event, s0._context)
	return s0


async def s1_f(event: EventF, context: Context) -> Type["s0.s2.s21.s211"]:
	mock.s1_run(event, s0._context)
	return s0.s2.s21.s211


async def s11_g(event: EventG, context: Context) -> Type["s0.s2.s21.s211"]:
	mock.s11_run(event, s0._context)
	return s0.s2.s21.s211


async def s2_c(event: EventC, context: Context) -> Type["s0.s1"]:
	mock.s2_run(event, s0._context)
	return s0.s1


async def s2_f(event: EventF, context: Context) -> Type["s0.s1.s11"]:
	mock.s2_run(event, s0._context)
	return s0.s1.s11


async def s21_b(event: EventB, context: Context) -> Type["s0.s2.s21.s211"]:
	mock.s21_run(event, s0._context)
	return s0.s2.s21.s211


async def s211_d(event: EventD, context: Context) -> Type["s0.s2.s21"]:
	mock.s211_run(event, s0._context)
	return s0.s2.s21


async def s211_g(event: EventG, context: Context) -> Type["s0"]:
	mock.s211_run(event, s0._context)
	return s0


class s0(Node[Event, Context, Context]):
	_context: ClassVar[Context]

	@staticmethod
	async def entry(context: Context) -> tuple[Type["s0.s1"], Context]:
		mock.s0_entry(s0._context)
		return s0.s1, context

	class EventHandlers:
		@staticmethod
		async def _e(event: EventE, context: Context) -> Type["s0.s2.s21.s211"]:
			mock.s0_run(event, s0._context)
			return s0.s2.s21.s211

		e: Callable[[EventE, Context], A[Type["s0.s2.s21.s211"]]] = _e

	@staticmethod
	async def exit(context: Context) -> None:
		mock.s0_exit(s0._context)

	class s1(Node[Event, Context, Context]):
		@staticmethod
		async def entry(context: Context) -> tuple[Type["s0.s1.s11"], Context]:
			mock.s1_entry(s0._context)
			return s0.s1.s11, context

		class EventHandlers:
			a: Callable[[EventA, Context], A[L[HSMStatus.SELF_TRANSITION]]] = s1_a
			b: Callable[[EventB, Context], A[Type["s0.s1.s11"]]] = s1_b
			c: Callable[[EventC, Context], A[Type["s0.s2"]]] = s1_c
			d: Callable[[EventD, Context], A[Type["s0"]]] = s1_d
			f: Callable[[EventF, Context], A[Type["s0.s2.s21.s211"]]] = s1_f

		@staticmethod
		async def exit(context: Context) -> None:
			mock.s1_exit(s0._context)

		class s11(Node[Event, Context, Context]):
			@staticmethod
			async def entry(context: Context) -> tuple[Type["s0.s1.s11"], Context]:
				mock.s11_entry(s0._context)
				return s0.s1.s11, context

			class EventHandlers:
				g: Callable[[EventG, Context], A[Type["s0.s2.s21.s211"]]] = s11_g

			@staticmethod
			async def exit(context: Context) -> None:  # type: ignore[override]
				mock.s11_exit(s0._context)
				if s0._context.foo == 1:
					s0._context.foo = 0

	class s2(Node[Event, Context, Context]):
		@staticmethod
		async def entry(context: Context) -> tuple[Type["s0.s2.s21"], Context]:
			mock.s2_entry(s0._context)
			return s0.s2.s21, context

		class EventHandlers:
			c: Callable[[EventC, Context], A[Type["s0.s1"]]] = s2_c
			f: Callable[[EventF, Context], A[Type["s0.s1.s11"]]] = s2_f

		@staticmethod
		async def exit(context: Context) -> None:
			mock.s2_exit(s0._context)

		class s21(Node[Event, Context, Context]):
			@staticmethod
			async def entry(context: Context) -> tuple[Type["s0.s2.s21.s211"], Context]:
				mock.s21_entry(s0._context)
				return s0.s2.s21.s211, context

			class EventHandlers:
				b: Callable[[EventB, Context], A[Type["s0.s2.s21.s211"]]] = s21_b
				h: Callable[
					[EventH, Context],
					A[L[HSMStatus.SELF_TRANSITION] | L[HSMStatus.NO_TRANSITION]],
				] = s21_h

			@staticmethod
			async def exit(context: Context) -> None:
				mock.s21_exit(s0._context)

			class s211(Node[Event, Context, Context]):
				@staticmethod
				async def entry(context: Context) -> tuple[Type["s0.s2.s21.s211"], Context]:
					mock.s211_entry(s0._context)
					return s0.s2.s21.s211, context

				class EventHandlers:
					d: Callable[[EventD, Context], A[Type["s0.s2.s21"]]] = s211_d
					g: Callable[[EventG, Context], A[Type["s0"]]] = s211_g

				@staticmethod
				async def exit(context: Context) -> None:
					mock.s211_exit(s0._context)


@pytest.mark.asyncio
async def test_transitions_run() -> None:
	s0._context = Context(foo=0)

	node = await hsm_handle_entries(s0)
	assert node is s0.s1.s11

	node = await hsm_handle_event(node, EventB())
	assert node is s0.s1.s11

	node = await hsm_handle_event(node, EventG())
	assert node is s0.s2.s21.s211

	node = await hsm_handle_event(node, EventH())
	assert node is s0.s2.s21.s211
	assert s0._context.foo == 1

	node = await hsm_handle_event(node, EventG())
	assert node is s0

	node = await hsm_handle_event(node, EventG())
	assert node is s0
	assert s0._context.foo == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
	"event", (EventA(), EventB(), EventC(), EventD(), EventF(), EventG(), EventH())
)
async def test_s0_unhandled(event: Event) -> None:
	"""All events but e are ignored in s0."""

	mock.reset_mock()

	s0._context = Context(foo=0)

	node = await hsm_handle_event(s0, event)
	assert node is s0
	assert s0._context.foo == 0

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

	s0._context = Context(foo=0)

	node = await hsm_handle_event(s0, EventE())
	assert node is s0.s2.s21.s211
	assert s0._context.foo == 0

	mock.assert_has_calls(
		(
			call.s0_run(EventE(), s0._context),
			call.s2_entry(s0._context),
			call.s21_entry(s0._context),
			call.s211_entry(s0._context),
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

	s0._context = Context(foo=foo)

	node = await hsm_handle_event(s0.s1.s11, EventA())
	assert node is s0.s1.s11
	assert s0._context.foo == 0

	mock.assert_has_calls(
		(
			call.s1_run(EventA(), s0._context),
			call.s11_exit(s0._context),
			call.s1_exit(s0._context),
			call.s1_entry(s0._context),
			call.s11_entry(s0._context),
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

	s0._context = Context(foo=foo)

	node = await hsm_handle_event(s0.s1.s11, EventB())
	assert node is s0.s1.s11
	assert s0._context.foo == 0

	mock.assert_has_calls(
		(
			call.s1_run(EventB(), s0._context),
			call.s11_exit(s0._context),
			call.s11_entry(s0._context),
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

	s0._context = Context(foo=foo)

	node = await hsm_handle_event(s0.s1.s11, EventC())
	assert node is s0.s2.s21.s211
	assert s0._context.foo == 0

	mock.assert_has_calls(
		(
			call.s1_run(EventC(), s0._context),
			call.s11_exit(s0._context),
			call.s1_exit(s0._context),
			call.s2_entry(s0._context),
			call.s21_entry(s0._context),
			call.s211_entry(s0._context),
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

	s0._context = Context(foo=foo)

	node = await hsm_handle_event(s0.s1.s11, EventD())
	assert node is s0
	assert s0._context.foo == 0

	mock.assert_has_calls(
		(
			call.s1_run(EventD(), s0._context),
			call.s11_exit(s0._context),
			call.s1_exit(s0._context),
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

	s0._context = Context(foo=foo)

	node = await hsm_handle_event(s0.s1.s11, EventE())
	assert node is s0.s2.s21.s211
	assert s0._context.foo == 0

	mock.assert_has_calls(
		(
			call.s0_run(EventE(), s0._context),
			call.s11_exit(s0._context),
			call.s1_exit(s0._context),
			call.s2_entry(s0._context),
			call.s21_entry(s0._context),
			call.s211_entry(s0._context),
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

	s0._context = Context(foo=foo)

	node = await hsm_handle_event(s0.s1.s11, EventF())
	assert node is s0.s2.s21.s211
	assert s0._context.foo == 0

	mock.assert_has_calls(
		(
			call.s1_run(EventF(), s0._context),
			call.s11_exit(s0._context),
			call.s1_exit(s0._context),
			call.s2_entry(s0._context),
			call.s21_entry(s0._context),
			call.s211_entry(s0._context),
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

	s0._context = Context(foo=foo)

	node = await hsm_handle_event(s0.s1.s11, EventG())
	assert node is s0.s2.s21.s211
	assert s0._context.foo == 0

	mock.assert_has_calls(
		(
			call.s11_run(EventG(), s0._context),
			call.s11_exit(s0._context),
			call.s1_exit(s0._context),
			call.s2_entry(s0._context),
			call.s21_entry(s0._context),
			call.s211_entry(s0._context),
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

	s0._context = Context(foo=foo)

	node = await hsm_handle_event(s0.s1.s11, EventH())
	assert node is s0.s1.s11
	assert s0._context.foo == foo

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

	s0._context = Context(foo=foo)

	node = await hsm_handle_event(s0.s2.s21.s211, EventA())
	assert node is s0.s2.s21.s211
	assert s0._context.foo == foo

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

	s0._context = Context(foo=foo)

	node = await hsm_handle_event(s0.s2.s21.s211, EventB())
	assert node is s0.s2.s21.s211
	assert s0._context.foo == foo

	mock.assert_has_calls(
		(
			call.s21_run(EventB(), s0._context),
			call.s211_exit(s0._context),
			call.s211_entry(s0._context),
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

	s0._context = Context(foo=foo)

	node = await hsm_handle_event(s0.s2.s21.s211, EventC())
	assert node is s0.s1.s11
	assert s0._context.foo == foo

	mock.assert_has_calls(
		(
			call.s2_run(EventC(), s0._context),
			call.s211_exit(s0._context),
			call.s21_exit(s0._context),
			call.s2_exit(s0._context),
			call.s1_entry(s0._context),
			call.s11_entry(s0._context),
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

	s0._context = Context(foo=foo)

	node = await hsm_handle_event(s0.s2.s21.s211, EventD())
	assert node is s0.s2.s21
	assert s0._context.foo == foo

	mock.assert_has_calls(
		(
			call.s211_run(EventD(), s0._context),
			call.s211_exit(s0._context),
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

	s0._context = Context(foo=foo)

	node = await hsm_handle_event(s0.s2.s21.s211, EventE())
	assert node is s0.s2.s21.s211
	assert s0._context.foo == foo

	mock.assert_has_calls(
		(
			call.s0_run(EventE(), s0._context),
			call.s211_exit(s0._context),
			call.s21_exit(s0._context),
			call.s2_exit(s0._context),
			call.s2_entry(s0._context),
			call.s21_entry(s0._context),
			call.s211_entry(s0._context),
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

	s0._context = Context(foo=foo)

	node = await hsm_handle_event(s0.s2.s21.s211, EventF())
	assert node is s0.s1.s11
	assert s0._context.foo == foo

	mock.assert_has_calls(
		(
			call.s2_run(EventF(), s0._context),
			call.s211_exit(s0._context),
			call.s21_exit(s0._context),
			call.s2_exit(s0._context),
			call.s1_entry(s0._context),
			call.s11_entry(s0._context),
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

	s0._context = Context(foo=foo)

	node = await hsm_handle_event(s0.s2.s21.s211, EventG())
	assert node is s0
	assert s0._context.foo == foo

	mock.assert_has_calls(
		(
			call.s211_run(EventG(), s0._context),
			call.s211_exit(s0._context),
			call.s21_exit(s0._context),
			call.s2_exit(s0._context),
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

	s0._context = Context(foo=0)

	node = await hsm_handle_event(s0.s2.s21.s211, EventH())
	assert node is s0.s2.s21.s211
	assert s0._context.foo == 1

	mock.assert_has_calls(
		(
			call.s21_run(EventH(), s0._context),
			call.s211_exit(s0._context),
			call.s21_exit(s0._context),
			call.s21_entry(s0._context),
			call.s211_entry(s0._context),
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

	s0._context = Context(foo=1)

	node = await hsm_handle_event(s0.s2.s21.s211, EventH())
	assert node is s0.s2.s21.s211
	assert s0._context.foo == 1

	mock.assert_has_calls((call.s21_run(EventH(), s0._context),))

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

	s0._context = Context(foo=0)

	node = await hsm_handle_event(s0, event)
	assert node is s0
	assert s0._context.foo == 0

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

	s0._context = Context(foo=0)

	node = await hsm_handle_event(s0.s2.s21, EventB())
	assert node is s0.s2.s21.s211
	assert s0._context.foo == 0

	mock.assert_has_calls(
		(
			call.s21_run(EventB(), s0._context),
			call.s211_entry(s0._context),
		)
	)


@pytest.mark.asyncio
async def test_s21_c() -> None:
	mock.reset_mock()

	s0._context = Context(foo=0)

	node = await hsm_handle_event(s0.s2.s21, EventC())
	assert node is s0.s1.s11
	assert s0._context.foo == 0

	mock.assert_has_calls(
		(
			call.s2_run(EventC(), s0._context),
			call.s21_exit(s0._context),
			call.s2_exit(s0._context),
			call.s1_entry(s0._context),
			call.s11_entry(s0._context),
		)
	)


@pytest.mark.asyncio
async def test_s21_e() -> None:
	mock.reset_mock()

	s0._context = Context(foo=0)

	node = await hsm_handle_event(s0.s2.s21, EventE())
	assert node is s0.s2.s21.s211
	assert s0._context.foo == 0

	mock.assert_has_calls(
		(
			call.s0_run(EventE(), s0._context),
			call.s21_exit(s0._context),
			call.s2_exit(s0._context),
			call.s2_entry(s0._context),
			call.s21_entry(s0._context),
			call.s211_entry(s0._context),
		)
	)


@pytest.mark.asyncio
async def test_s21_f() -> None:
	mock.reset_mock()

	s0._context = Context(foo=0)

	node = await hsm_handle_event(s0.s2.s21, EventF())
	assert node is s0.s1.s11
	assert s0._context.foo == 0

	mock.assert_has_calls(
		(
			call.s2_run(EventF(), s0._context),
			call.s21_exit(s0._context),
			call.s2_exit(s0._context),
			call.s1_entry(s0._context),
			call.s11_entry(s0._context),
		)
	)


@pytest.mark.asyncio
async def test_s21_h_foo_0() -> None:
	mock.reset_mock()

	s0._context = Context(foo=0)

	node = await hsm_handle_event(s0.s2.s21, EventH())
	assert node is s0.s2.s21.s211
	assert s0._context.foo == 1

	mock.assert_has_calls(
		(
			call.s21_run(EventH(), s0._context),
			call.s21_exit(s0._context),
			call.s21_entry(s0._context),
			call.s211_entry(s0._context),
		)
	)


@pytest.mark.asyncio
async def test_s21_h_foo_1() -> None:
	mock.reset_mock()

	s0._context = Context(foo=1)

	node = await hsm_handle_event(s0.s2.s21, EventH())
	assert node is s0.s2.s21
	assert s0._context.foo == 1

	mock.assert_has_calls((call.s21_run(EventH(), s0._context),))
	assert s0._context.foo == 1

	mock.assert_has_calls((call.s21_run(EventH(), s0._context),))
	mock.assert_has_calls((call.s21_run(EventH(), s0._context),))
