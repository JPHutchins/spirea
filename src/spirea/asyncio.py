# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

"""Hierarchical State Machine (HSM) API for asynchronous runtime."""

import logging
from typing import Any, Awaitable, Callable, ClassVar, Final, Protocol, Type, assert_never

from spirea._common import (
	HSMStatus,
	NodeMeta,
	TContext,
	TEntryContexts,
	TEvent,
	hsm_get_lca,
	hsm_get_path_to_root,
	is_hsm_status,
)

logger: Final = logging.getLogger(__name__)


__all__ = ("HSMStatus",)  # re-exported from _common


class Node(Protocol[TEvent, TContext, TEntryContexts], metaclass=NodeMeta):
	"""The asynchronous `Protocol` for a hierarchical state machine node."""

	@staticmethod
	async def entry(
		context: TEntryContexts,
	) -> tuple[type["Node[TEvent, TContext, Any]"], TContext]: ...

	@staticmethod
	async def exit(context: TContext) -> None: ...

	_event_handlers: tuple[
		tuple[
			Type[TEvent],
			Callable[
				[TEvent, TContext],
				Awaitable[Type["Node[TEvent, TContext, Any]"] | HSMStatus],
			],
		],
		...,
	] = ()
	"""This is provided by the metaclass, here for type hinting only."""

	_context: ClassVar[Any]


def _hsm_get_event_handler(
	node: Type[Node[TEvent, TContext, Any]],
	event: TEvent,
) -> Callable[[TEvent, TContext], Awaitable[Type[Node[TEvent, TContext, Any]] | HSMStatus]] | None:
	for eventT, handler in node._event_handlers:
		if isinstance(event, eventT):
			return handler

	return None


async def hsm_handle_entries(
	node: Type[Node[TEvent, TContext, Any]],
	prev: Type[Node[TEvent, TContext, Any]] | None = None,
) -> Type[Node[TEvent, TContext, Any]]:
	"""Do the entries for the given node and all transitions that its entry causes.

	Args:
		node (Type[Node]): The node to start the entries from.
		prev (Type[Node], optional): The previous node. Defaults to None.

	Returns:
		Type[Node]: The node after all entries have been done
	"""

	while node != prev:
		prev = node
		node, context = await node.entry(node._context)
		node._context = context
	return node


async def hsm_handle_event(
	node: Type[Node[TEvent, TContext, Any]],
	event: TEvent,
) -> Type[Node[TEvent, TContext, Any]]:
	"""
	Handle an event for the hierarchical state machine.

	Args:
		node (Type[Node[TEvent, TState, Any]]): The current node of the HSM.
		event (TEvent): The event to handle.

	Returns:
		node (Type[Node[TEvent, TState, Any]]): The new node after handling the event.
	"""

	# the node path from the starting node up to the handling node
	node_path: Final[list[Type[Node[TEvent, TContext, Any]]]] = [node]

	while True:
		current_node = node_path[-1]
		node_or_status: Final = (  # type: ignore[misc]
			await handler(event, current_node._context)
			if (handler := _hsm_get_event_handler(current_node, event))
			else HSMStatus.EVENT_UNHANDLED
		)

		if is_hsm_status(node_or_status):
			status: Final = node_or_status  # type: ignore[misc]

			if status == HSMStatus.NO_TRANSITION:
				logger.debug(f"No transition in state {current_node.__name__}")
				return node

			elif status == HSMStatus.SELF_TRANSITION:
				logger.debug(f"Self-transition in state {current_node.__name__}")
				for n in node_path:
					await n.exit(current_node._context)
				return await hsm_handle_entries(current_node)

			elif status == HSMStatus.EVENT_UNHANDLED:
				logger.debug(f"Unhandled event {event} in state {current_node.__name__}")
				if current_node._superstate is None:
					logger.debug(f"Reached root state {current_node.__name__}")
					return node
				else:
					node_path.append(current_node._superstate)
					continue

			else:
				assert_never(status)

		# else handle transitions to the new node
		target_node: Final = node_or_status  # type: ignore[misc]

		current_node_path_to_root: Final = hsm_get_path_to_root(current_node)  # type: ignore[misc]
		target_node_path_to_root: Final = hsm_get_path_to_root(target_node)  # type: ignore[misc]
		lca: Final = hsm_get_lca(target_node_path_to_root, current_node_path_to_root)  # type: ignore[misc]

		# do the exits from the original node to the LCA
		next_node = node
		while next_node != lca:
			await next_node.exit(next_node._context)
			if next_node._superstate is None:
				break
			next_node = next_node._superstate

		# start the entry path past the LCA
		entry_path = tuple(reversed(target_node_path_to_root))
		entry_path = tuple(entry_path[entry_path.index(lca) + 1 :])

		# check for an exit to a superstate in which no entries are called
		if len(entry_path) == 0:
			return next_node

		# do the entries from LCA to the new state
		if entry_path[0] is None:
			raise ValueError("The entry path is empty")
		next_node = entry_path[0]
		for entry_node in entry_path:
			if entry_node != next_node:
				logger.warning(f"The entry return disagrees with the path -> Path is {entry_path}")
				raise ValueError("The entry return disagrees with the entry path")
			next_node, next_context = await entry_node.entry(current_node._context)
			entry_node._context = next_context
			current_node = entry_node

		return await hsm_handle_entries(next_node, entry_path[-1] if entry_path else None)
