# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT


from examples.samek.events import EventA, EventB, EventC, EventD, EventF
from examples.samek.state import Context


def entry(context: Context) -> None:
	print("    s1 entry")


def run_a(event: EventA, context: Context) -> None:
	print("    s1 run a")


def run_b(event: EventB, context: Context) -> None:
	print("    s1 run b")


def run_c(event: EventC, context: Context) -> None:
	print("    s1 run c")


def run_d(event: EventD, context: Context) -> None:
	print("    s1 run d")


def run_f(event: EventF, context: Context) -> None:
	print("    s1 run f")


def exit(context: Context) -> None:
	print("    s1 exit")
