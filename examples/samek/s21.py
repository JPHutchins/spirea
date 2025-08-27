# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from typing import Literal as L

from examples.samek.events import EventB, EventH
from examples.samek.state import State
from spirea.sync import HSMStatus


def entry(state: State) -> None:
	print("        s21 entry")


def run_b(event: EventB, state: State) -> None:
	print("        s21 run b")


def run_h(event: EventH, state: State) -> L[HSMStatus.SELF_TRANSITION] | L[HSMStatus.NO_TRANSITION]:
	if state.foo == 0:
		state.foo = 1
		print(f"        s21 run h {state.foo=}")
		return HSMStatus.SELF_TRANSITION
	else:
		print("        s21 run h")
		return HSMStatus.NO_TRANSITION


def exit(state: State) -> None:
	print("        s21 exit")
