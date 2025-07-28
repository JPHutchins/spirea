# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT


from examples.samek.events import EventC, EventF
from examples.samek.state import State


def entry(state: State | None = None) -> None:
	print("    s2 entry")


def run_c(event: EventC, state: State | None) -> None:
	print("    s2 run c")


def run_f(event: EventF, state: State | None) -> None:
	print("    s2 run f")


def exit(state: State | None) -> None:
	print("    s2 exit")
