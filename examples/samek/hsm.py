# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from typing import Callable, Type
from typing import Literal as L
from unittest.mock import Mock

import examples.samek.s0 as s0_
import examples.samek.s1 as s1_
import examples.samek.s2 as s2_
import examples.samek.s11 as s11_
import examples.samek.s21 as s21_
import examples.samek.s211 as s211_
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
from examples.samek.state import Context
from spirea.sync import HSMStatus, Node

mock = Mock()


class s0(Node[Event, Context, Context]):
	@staticmethod
	def entry(context: Context) -> tuple[type["s0.s1"], Context]:
		s0.set_context(context)
		mock.s0_entry(context)
		s0_.entry(context)
		return s0.s1, context

	class EventHandlers:
		e: Callable[[EventE, Context], Type["s0.s2.s21.s211"]] = (
			lambda e, s: (mock.s0_run(e, s) and s0_.run_e(e, s)) or s0.s2.s21.s211  # type: ignore[func-returns-value]
		)

	@staticmethod
	def exit(context: Context) -> None:
		mock.s0_exit(context)
		s0_.exit(context)

	class s1(Node[Event, Context, Context]):
		@staticmethod
		def entry(context: Context) -> tuple[Type["s0.s1.s11"], Context]:
			s0.s1.set_context(context)
			mock.s1_entry(context)
			s1_.entry(context)
			return s0.s1.s11, context

		class EventHandlers:
			a: Callable[[EventA, Context], L[HSMStatus.SELF_TRANSITION]] = (
				lambda e, s: (mock.s1_run(e, s) and s1_.run_a(e, s))  # type: ignore[func-returns-value]
				or HSMStatus.SELF_TRANSITION
			)
			b: Callable[[EventB, Context], Type["s0.s1.s11"]] = (
				lambda e, s: (mock.s1_run(e, s) and s1_.run_b(e, s)) or s0.s1.s11  # type: ignore[func-returns-value]
			)
			c: Callable[[EventC, Context], Type["s0.s2"]] = (
				lambda e, s: (mock.s1_run(e, s) and s1_.run_c(e, s)) or s0.s2  # type: ignore[func-returns-value]
			)
			d: Callable[[EventD, Context], Type["s0"]] = (
				lambda e, s: (mock.s1_run(e, s) and s1_.run_d(e, s)) or s0  # type: ignore[func-returns-value]
			)
			f: Callable[[EventF, Context], Type["s0.s2.s21.s211"]] = (
				lambda e, s: (mock.s1_run(e, s) and s1_.run_f(e, s)) or s0.s2.s21.s211  # type: ignore[func-returns-value]
			)

		@staticmethod
		def exit(context: Context) -> None:
			mock.s1_exit(context)
			s1_.exit(context)

		class s11(Node[Event, Context, Context]):
			@staticmethod
			def entry(context: Context) -> tuple[Type["s0.s1.s11"], Context]:
				s0.s1.s11.set_context(context)
				mock.s11_entry(context)
				s11_.entry(context)
				return s0.s1.s11, context

			class EventHandlers:
				g: Callable[[EventG, Context], Type["s0.s2.s21.s211"]] = (
					lambda e, s: (mock.s11_run(e, s) and s11_.run_g(e, s))  # type: ignore[func-returns-value]
					or s0.s2.s21.s211
				)

			@staticmethod
			def exit(context: Context) -> None:
				mock.s11_exit(context)
				s11_.exit(context)

	class s2(Node[Event, Context, Context]):
		@staticmethod
		def entry(context: Context) -> tuple[Type["s0.s2.s21"], Context]:
			s0.s2.set_context(context)
			mock.s2_entry(context)
			s2_.entry(context)
			return s0.s2.s21, context

		class EventHandlers:
			c: Callable[[EventC, Context], Type["s0.s1"]] = (
				lambda e, s: (mock.s2_run(e, s) and s2_.run_c(e, s)) or s0.s1  # type: ignore[func-returns-value]
			)
			f: Callable[[EventF, Context], Type["s0.s1.s11"]] = (
				lambda e, s: (mock.s2_run(e, s) and s2_.run_f(e, s)) or s0.s1.s11  # type: ignore[func-returns-value]
			)

		@staticmethod
		def exit(context: Context) -> None:
			mock.s2_exit(context)
			s2_.exit(context)

		class s21(Node[Event, Context, Context]):
			@staticmethod
			def entry(context: Context) -> tuple[Type["s0.s2.s21.s211"], Context]:
				s0.s2.s21.set_context(context)
				mock.s21_entry(context)
				s21_.entry(context)
				return s0.s2.s21.s211, context

			class EventHandlers:
				b: Callable[[EventB, Context], Type["s0.s2.s21.s211"]] = (
					lambda e, s: (mock.s21_run(e, s) and s21_.run_b(e, s))  # type: ignore[func-returns-value]
					or s0.s2.s21.s211
				)
				h: Callable[
					[EventH, Context],
					L[HSMStatus.SELF_TRANSITION] | L[HSMStatus.NO_TRANSITION],
				] = lambda e, s: (mock.s21_run(e, s) and None) or s21_.run_h(e, s)

			@staticmethod
			def exit(context: Context) -> None:
				mock.s21_exit(context)
				s21_.exit(context)

			class s211(Node[Event, Context, Context]):
				@staticmethod
				def entry(context: Context) -> tuple[Type["s0.s2.s21.s211"], Context]:
					s0.s2.s21.s211.set_context(context)
					mock.s211_entry(context)
					s211_.entry(context)
					return s0.s2.s21.s211, context

				class EventHandlers:
					d: Callable[[EventD, Context], Type["s0.s2.s21"]] = (
						lambda e, s: (mock.s211_run(e, s) and s211_.run_d(e, s))  # type: ignore[func-returns-value]
						or s0.s2.s21
					)
					g: Callable[[EventG, Context], Type["s0"]] = (
						lambda e, s: (mock.s211_run(e, s) and s211_.run_g(e, s)) or s0  # type: ignore[func-returns-value]
					)

				@staticmethod
				def exit(context: Context) -> None:
					mock.s211_exit(context)
					s211_.exit(context)
