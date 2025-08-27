# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT


from examples.samek.events import EventE
from examples.samek.state import Context


def entry(context: Context) -> None:
	print("s0 entry")


def run_e(event: EventE, context: Context) -> None:
	print("s0 run e")


def exit(context: Context) -> None:
	print("s0 exit")
