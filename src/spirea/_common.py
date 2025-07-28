# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from enum import Enum, unique
from typing import Any, Callable, Final, NamedTuple, Type, TypeVar, _ProtocolMeta, final

from typing_extensions import TypeIs

TEvent = TypeVar("TEvent")
TState = TypeVar("TState")
TNode = TypeVar("TNode")


class NoTransition(NamedTuple): ...


class SelfTransition(NamedTuple): ...


class EventUnhandled(NamedTuple): ...


@final
@unique
class HSMStatus(Enum):
	NO_TRANSITION = NoTransition
	SELF_TRANSITION = SelfTransition
	EVENT_UNHANDLED = EventUnhandled


def is_hsm_status(node: Type[TNode] | HSMStatus) -> TypeIs[HSMStatus]:
	return isinstance(node, HSMStatus)


def _is_hsm_node(cls: Any) -> TypeIs[Type["NodeMeta"]]:
	return hasattr(cls, "__hsm_node")


class _NodeMixin:
	_superstate: type | None
	_substates: tuple[type, ...]


class _NodeMeta(type, _NodeMixin):
	def __new__(
		cls: Type["_NodeMeta"],
		name: str,
		bases: tuple[type, ...],
		dct: dict[str, Any],
	) -> "_NodeMeta":
		dct["__hsm_node"] = True
		node_cls = super().__new__(cls, name, bases, dct)
		node_cls._superstate = None

		substates: Final[list[type]] = []
		for attr_value in dct.values():
			if _is_hsm_node(attr_value):
				substates.append(attr_value)
				attr_value._superstate = node_cls
		node_cls._substates = tuple(substates)
		del substates

		if not hasattr(node_cls, "EventHandlers"):
			return node_cls

		# Create a list of event handlers. Each handler is a tuple that pairs
		# the event, or event type, with the handler function.
		event_handlers: Final[  # type: ignore[valid-type]
			list[
				tuple[
					Type[TEvent],
					Callable[
						[TEvent, TState | None],
						type | HSMStatus,
					],
				]
			]
		] = []
		for name, value in node_cls.EventHandlers.__annotations__.items():
			event_handlers.append(
				(
					# Map type -> handler
					value.__args__[0],
					getattr(node_cls.EventHandlers, name),
				)
			)
		node_cls._event_handlers = tuple(event_handlers)  # type: ignore[attr-defined]
		del event_handlers

		return node_cls


@final
class NodeMeta(_NodeMeta, _ProtocolMeta): ...


def hsm_get_path_to_root(
	node: Type[TNode],
) -> tuple[Type[TNode] | None, ...]:
	path: Final[list[Type[TNode] | None]] = [node]
	while node is not None:
		node = node._superstate  # type: ignore[attr-defined]
		path.append(node)

	return tuple(path)


def hsm_get_lca(
	path1: tuple[Type[TNode] | None, ...],
	path2: tuple[Type[TNode] | None, ...],
) -> Type[TNode] | None:
	for node in path1:
		if node in path2:
			return node

	return None
