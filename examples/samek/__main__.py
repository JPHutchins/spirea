# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from typing import Final

import readchar

from examples.samek.events import Event
from examples.samek.hsm import s0
from examples.samek.state import State
from spirea.sync import Node, hsm_handle_entries, hsm_handle_event

MAP_CHAR_TO_EVENT: Final[dict[str, Event]] = {
	"a": Event.a,
	"b": Event.b,
	"c": Event.c,
	"d": Event.d,
	"e": Event.e,
	"f": Event.f,
	"g": Event.g,
	"h": Event.h,
}


def print_node_and_state(node: type[Node[Event, State]], state: State) -> None:
	if node is s0:
		indent = ""
	elif node is s0.s1 or node is s0.s2:
		indent = "----"
	elif node is s0.s1.s11 or node is s0.s2.s21:
		indent = "--------"
	elif node is s0.s2.s21.s211:
		indent = "------------"

	print(indent + node.__name__ + " " + str(state))


def app() -> None:
	state = State(foo=0)
	node = hsm_handle_entries(s0, state)

	print_node_and_state(node, state)

	while True:
		try:
			event = MAP_CHAR_TO_EVENT[readchar.readkey()]
			print(f"{repr(event)}")
		except KeyError:
			continue

		node = hsm_handle_event(node, event, state)

		print_node_and_state(node, state)


if __name__ == "__main__":
	app()
