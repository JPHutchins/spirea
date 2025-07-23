# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from typing import Literal as L

from examples.samek.events import Event
from examples.samek.state import State


def entry(state: State | None = None) -> None:
	print("s0 entry")


def run_e(event: L[Event.e], state: State | None) -> None:
	print("s0 run e")


def exit(state: State | None) -> None:
	print("s0 exit")
