# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT


from examples.samek.events import EventG
from examples.samek.state import Context


def entry(context: Context) -> None:
	print("        s11 entry")


def run_g(event: EventG, context: Context) -> None:
	print("        s11 run g")


def exit(context: Context) -> None:
	if context.foo == 1:
		context.foo = 0
		print(f"        s11 exit {context.foo=}")
	else:
		print("        s11 exit")
