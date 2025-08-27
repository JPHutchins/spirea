# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from examples.samek.events import EventD, EventG
from examples.samek.state import Context


def entry(context: Context) -> None:
	print("            s211 entry")


def run_d(event: EventD, context: Context) -> None:
	print("            s211 run d")


def run_g(event: EventG, context: Context) -> None:
	print("            s211 run g")


def exit(context: Context) -> None:
	print("            s211 exit")
