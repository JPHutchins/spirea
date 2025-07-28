# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT


from examples.samek.events import EventG
from examples.samek.state import State


def entry(state: State | None = None) -> None:
	print("        s11 entry")


def run_g(event: EventG, state: State | None) -> None:
	print("        s11 run g")


def exit(state: State) -> None:
	if state.foo == 1:
		state.foo = 0
		print(f"        s11 exit {state.foo=}")
	else:
		print("        s11 exit")
