# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT


from examples.samek.events import EventC, EventF
from examples.samek.state import Context


def entry(context: Context) -> None:
	print("    s2 entry")


def run_c(event: EventC, context: Context) -> None:
	print("    s2 run c")


def run_f(event: EventF, context: Context) -> None:
	print("    s2 run f")


def exit(context: Context) -> None:
	print("    s2 exit")
