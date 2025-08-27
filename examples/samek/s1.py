# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT


from examples.samek.events import EventA, EventB, EventC, EventD, EventF
from examples.samek.state import State


def entry(state: State) -> None:
	print("    s1 entry")


def run_a(event: EventA, state: State) -> None:
	print("    s1 run a")


def run_b(event: EventB, state: State) -> None:
	print("    s1 run b")


def run_c(event: EventC, state: State) -> None:
	print("    s1 run c")


def run_d(event: EventD, state: State) -> None:
	print("    s1 run d")


def run_f(event: EventF, state: State) -> None:
	print("    s1 run f")


def exit(state: State) -> None:
	print("    s1 exit")
