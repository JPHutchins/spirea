# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from examples.samek.events import EventD, EventG
from examples.samek.state import State


def entry(state: State | None = None) -> None:
	print("            s211 entry")


def run_d(event: EventD, state: State | None) -> None:
	print("            s211 run d")


def run_g(event: EventG, state: State | None) -> None:
	print("            s211 run g")


def exit(state: State | None) -> None:
	print("            s211 exit")
