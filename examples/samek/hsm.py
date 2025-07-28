# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from typing import Callable  # noqa: I001
from typing import Literal as L
from typing import Type
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
from examples.samek.state import State
from spirea.sync import HSMStatus, Node

mock = Mock()


class s0(Node[Event, State]):
	@staticmethod
	def entry(state: State | None = None) -> type["s0.s1"]:
		mock.s0_entry(state)
		s0_.entry(state)
		return s0.s1

	class EventHandlers:
		e: Callable[[EventE, State | None], Type["s0.s2.s21.s211"]] = (
			lambda e, s: (mock.s0_run(e, s) and s0_.run_e(e, s)) or s0.s2.s21.s211  # type: ignore[func-returns-value]
		)

	@staticmethod
	def exit(state: State | None = None) -> None:
		mock.s0_exit(state)
		s0_.exit(state)

	class s1(Node[Event, State]):
		@staticmethod
		def entry(state: State | None = None) -> Type[Node[Event, State]]:
			mock.s1_entry(state)
			s1_.entry(state)
			return s0.s1.s11

		class EventHandlers:
			a: Callable[[EventA, State | None], L[HSMStatus.SELF_TRANSITION]] = (
				lambda e, s: (mock.s1_run(e, s) and s1_.run_a(e, s))  # type: ignore[func-returns-value]
				or HSMStatus.SELF_TRANSITION
			)
			b: Callable[[EventB, State | None], Type["s0.s1.s11"]] = (
				lambda e, s: (mock.s1_run(e, s) and s1_.run_b(e, s)) or s0.s1.s11  # type: ignore[func-returns-value]
			)
			c: Callable[[EventC, State | None], Type["s0.s2"]] = (
				lambda e, s: (mock.s1_run(e, s) and s1_.run_c(e, s)) or s0.s2  # type: ignore[func-returns-value]
			)
			d: Callable[[EventD, State | None], Type["s0"]] = (
				lambda e, s: (mock.s1_run(e, s) and s1_.run_d(e, s)) or s0  # type: ignore[func-returns-value]
			)
			f: Callable[[EventF, State | None], Type["s0.s2.s21.s211"]] = (
				lambda e, s: (mock.s1_run(e, s) and s1_.run_f(e, s)) or s0.s2.s21.s211  # type: ignore[func-returns-value]
			)

		@staticmethod
		def exit(state: State | None = None) -> None:
			mock.s1_exit(state)
			s1_.exit(state)

		class s11(Node[Event, State]):
			@staticmethod
			def entry(state: State | None = None) -> Type[Node[Event, State]]:
				mock.s11_entry(state)
				s11_.entry(state)
				return s0.s1.s11

			class EventHandlers:
				g: Callable[[EventG, State | None], Type["s0.s2.s21.s211"]] = (
					lambda e, s: (mock.s11_run(e, s) and s11_.run_g(e, s))  # type: ignore[func-returns-value]
					or s0.s2.s21.s211
				)

			@staticmethod
			def exit(state: State | None = None) -> None:
				mock.s11_exit(state)
				if state is None:
					raise ValueError
				s11_.exit(state)

	class s2(Node[Event, State]):
		@staticmethod
		def entry(state: State | None = None) -> Type[Node[Event, State]]:
			mock.s2_entry(state)
			s2_.entry(state)
			return s0.s2.s21

		class EventHandlers:
			c: Callable[[EventC, State | None], Type["s0.s1"]] = (
				lambda e, s: (mock.s2_run(e, s) and s2_.run_c(e, s)) or s0.s1  # type: ignore[func-returns-value]
			)
			f: Callable[[EventF, State | None], Type["s0.s1.s11"]] = (
				lambda e, s: (mock.s2_run(e, s) and s2_.run_f(e, s)) or s0.s1.s11  # type: ignore[func-returns-value]
			)

		@staticmethod
		def exit(state: State | None = None) -> None:
			mock.s2_exit(state)
			s2_.exit(state)

		class s21(Node[Event, State]):
			@staticmethod
			def entry(state: State | None = None) -> Type[Node[Event, State]]:
				mock.s21_entry(state)
				s21_.entry(state)
				return s0.s2.s21.s211

			class EventHandlers:
				b: Callable[[EventB, State | None], Type["s0.s2.s21.s211"]] = (
					lambda e, s: (mock.s21_run(e, s) and s21_.run_b(e, s))  # type: ignore[func-returns-value]
					or s0.s2.s21.s211
				)
				h: Callable[
					[EventH, State],
					L[HSMStatus.SELF_TRANSITION] | L[HSMStatus.NO_TRANSITION],
				] = lambda e, s: (mock.s21_run(e, s) and None) or s21_.run_h(e, s)

			@staticmethod
			def exit(state: State | None = None) -> None:
				mock.s21_exit(state)
				s21_.exit(state)

			class s211(Node[Event, State]):
				@staticmethod
				def entry(state: State | None = None) -> Type[Node[Event, State]]:
					mock.s211_entry(state)
					s211_.entry(state)
					return s0.s2.s21.s211

				class EventHandlers:
					d: Callable[[EventD, State | None], Type["s0.s2.s21"]] = (
						lambda e, s: (mock.s211_run(e, s) and s211_.run_d(e, s))  # type: ignore[func-returns-value]
						or s0.s2.s21
					)
					g: Callable[[EventG, State | None], Type["s0"]] = (
						lambda e, s: (mock.s211_run(e, s) and s211_.run_g(e, s)) or s0  # type: ignore[func-returns-value]
					)

				@staticmethod
				def exit(state: State | None = None) -> None:
					mock.s211_exit(state)
					s211_.exit(state)
