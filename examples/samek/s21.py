# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from typing import Literal as L

from examples.samek.events import EventB, EventH
from examples.samek.state import Context
from spirea.sync import HSMStatus


def entry(context: Context) -> None:
	print("        s21 entry")


def run_b(event: EventB, context: Context) -> None:
	print("        s21 run b")


def run_h(event: EventH, context: Context) -> L[HSMStatus.SELF_TRANSITION] | L[HSMStatus.NO_TRANSITION]:
	if context.foo == 0:
		context.foo = 1
		print(f"        s21 run h {context.foo=}")
		return HSMStatus.SELF_TRANSITION
	else:
		print("        s21 run h")
		return HSMStatus.NO_TRANSITION


def exit(context: Context) -> None:
	print("        s21 exit")
