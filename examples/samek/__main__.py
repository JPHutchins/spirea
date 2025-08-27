# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from typing import Any, Final

import readchar

from examples.samek.events import (
	Event,
	EventA,
	EventB,
	EventC,
	EventD,
	EventE,
	EventF,
	EventG,
	EventH,
)
from examples.samek.hsm import s0
from examples.samek.state import Context
from spirea.sync import Node, hsm_handle_entries, hsm_handle_event


def init_context(context: Context) -> None:
	"""This would normally be done by entry functions, but we bypass for testing."""
	s0._context = context


MAP_CHAR_TO_EVENT: Final[dict[str, Event]] = {
	"a": EventA(),
	"b": EventB(),
	"c": EventC(),
	"d": EventD(),
	"e": EventE(),
	"f": EventF(),
	"g": EventG(),
	"h": EventH(),
}


def print_node_and_context(node: type[Node[Event, Context, Any]], context: Context) -> None:
	indent = ""
	if node is s0:
		indent = ""
	elif node is s0.s1 or node is s0.s2:
		indent = "----"
	elif node is s0.s1.s11 or node is s0.s2.s21:
		indent = "--------"
	elif node is s0.s2.s21.s211:
		indent = "------------"

	print(indent + node.__name__ + " " + str(context))


def app() -> None:
	context = Context(foo=0)
	init_context(context)
	node = hsm_handle_entries(s0)

	print_node_and_context(node, context)

	while True:
		try:
			event = MAP_CHAR_TO_EVENT[readchar.readkey()]
			print(f"{repr(event)}")
		except KeyError:
			continue

		node = hsm_handle_event(node, event)

		print_node_and_context(node, context)


if __name__ == "__main__":
	app()
