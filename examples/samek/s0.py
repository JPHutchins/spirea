# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT


from examples.samek.events import EventE
from examples.samek.state import State


def entry(state: State | None = None) -> None:
	print("s0 entry")


def run_e(event: EventE, state: State | None) -> None:
	print("s0 run e")


def exit(state: State | None) -> None:
	print("s0 exit")
