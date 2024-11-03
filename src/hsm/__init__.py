import logging
from typing import (
    Final,
    Protocol,
    Type,
    TypeVar,
    Protocol,
    cast,
    Any,
    _ProtocolMeta,
    Callable,
    assert_never,
)
from typing_extensions import TypeIs
from enum import IntEnum


logger: Final = logging.getLogger(__name__)

TEvent = TypeVar("TEvent", bound=IntEnum)
TState = TypeVar("TState")


class HSMStatus(IntEnum):
    NO_TRANSITION = -2_147_483_648
    SELF_TRANSITION = -2_147_483_647
    EVENT_UNHANDLED = -2_147_483_646


def _is_hsm_node(cls: Any) -> TypeIs[Type["Node[TEvent, TState]"]]:
    return getattr(cls, "__hsm_node", False)


class StateMeta(type):
    def __new__(
        cls: Type["StateMeta"],
        name: str,
        bases: tuple[type, ...],
        dct: dict[str, Any],
    ) -> Type["Node[TEvent, TState]"]:
        dct["__hsm_node"] = True
        node_cls = cast(
            Type["Node[TEvent, TState]"], super().__new__(cls, name, bases, dct)
        )
        node_cls._superstate = None

        substates: Final[list[Type["Node[TEvent, TState]"]]] = []
        for attr_value in dct.values():
            if _is_hsm_node(attr_value):
                substates.append(attr_value)
                attr_value._superstate = node_cls  # type: ignore
        node_cls._substates = tuple(substates)
        del substates

        if not hasattr(node_cls, "EventHandlers"):
            return node_cls

        event_handlers: Final[
            list[
                tuple[
                    IntEnum,
                    Callable[
                        [TEvent, TState | None],
                        Type["Node[TEvent, TState]"] | HSMStatus,
                    ],
                ]
            ]
        ] = []
        for name, value in node_cls.EventHandlers.__annotations__.items():
            # Note: value.__args__ = (Literal[TEvent], TState, Return Type)
            event_handlers.append(
                (
                    value.__args__[0].__args__[0],
                    getattr(node_cls.EventHandlers, name),
                )
            )
        node_cls._event_handlers = tuple(event_handlers)
        del event_handlers

        return node_cls


class CombinedMeta(StateMeta, _ProtocolMeta):
    pass


class Node(Protocol[TEvent, TState], metaclass=CombinedMeta):
    @classmethod
    def entry(cls, state: TState | None = None) -> Type["Node[TEvent, TState]"]: ...

    @classmethod
    def exit(cls, state: TState | None = None) -> None: ...

    _superstate: Type["Node[TEvent, TState]"] | None
    _substates: tuple[Type["Node[TEvent, TState]"], ...]
    _event_handlers: tuple[
        tuple[
            IntEnum,
            Callable[[TEvent, TState | None], Type["Node[TEvent, TState]"] | HSMStatus],
        ],
        ...,
    ]


def hsm_get_path_to_root(
    node: Type[Node[TEvent, TState]],
) -> tuple[Type[Node[TEvent, TState]], ...]:
    path: Final[list[Type[Node[TEvent, TState]]]] = [node]
    while node is not None and node._superstate is not None:
        node = node._superstate
        path.append(node)

    return tuple(path)


def hsm_get_lca(
    path1: tuple[Type[Node[TEvent, TState]], ...],
    path2: tuple[Type[Node[TEvent, TState]], ...],
) -> Type[Node[TEvent, TState]]:
    for node in path1:
        if node in path2:
            return node

    raise ValueError("No common ancestor found")


def hsm_handle_entries(
    node: Type[Node[TEvent, TState]],
    state: TState | None = None,
    prev: Type[Node[TEvent, TState]] | None = None,
) -> Type[Node[TEvent, TState]]:
    """Do the entries for the given node and all transitions that its entry causes.

    Args:
        node (Type[Node]): The node to start the entries from.
        state (TState): The state to pass to the entry functions.
        prev (Type[Node], optional): The previous node. Defaults to None.

    Returns:
        Type[Node]: The node after all entries have been done
    """

    while node != prev:
        prev = node
        node = node.entry(state)
    return node


def _get_handler(
    node: Type[Node[TEvent, TState]],
    event: TEvent,
) -> Callable[[TEvent, TState | None], Type[Node[TEvent, TState]] | HSMStatus] | None:
    print(node)
    for e, handler in node._event_handlers:
        if event == e:
            return handler

    return None


def _is_hsm_status(node: Type[Node[TEvent, TState]] | HSMStatus) -> TypeIs[HSMStatus]:
    return isinstance(node, HSMStatus)


def hsm_handle_event(
    node: Type[Node[TEvent, TState]],
    event: TEvent,
    state: TState | None = None,
) -> Type[Node[TEvent, TState]]:
    """
    Handle an event for the hierarchical state machine.

    Args:
        node (Type[Node[TEvent, TState]]): The current node of the HSM.
        event (TEvent): The event to handle.
        state (TState, optional): The state to pass to the event handlers. Defaults to None.

    Returns:
        node (Type[Node[TEvent, TState]]): The new node after handling the event.
    """

    node: Final = node  # type: ignore[misc]
    event: Final = event  # type: ignore[misc]
    state: Final = state  # type: ignore[misc]

    # the node path from the starting node up to the handling node
    node_path: Final[list[Type[Node[TEvent, TState]]]] = [node]

    while True:
        current_node: Final = node_path[-1]  # type: ignore[misc]
        node_or_status: Final = (  # type: ignore[misc]
            handler(event, state)
            if (handler := _get_handler(current_node, event))
            else HSMStatus.EVENT_UNHANDLED
        )

        if _is_hsm_status(node_or_status):
            status: Final = node_or_status  # type: ignore[misc]

            if status == HSMStatus.NO_TRANSITION:
                logger.debug(f"No transition in state {current_node.__name__}")
                return node_path[0]

            elif status == HSMStatus.SELF_TRANSITION:
                print(f"Doing self-transition for {current_node.__name__}")
                logger.debug(f"Self-transition in state {current_node.__name__}")
                for n in node_path:
                    n.exit(state)
                return hsm_handle_entries(current_node, state)

            elif status == HSMStatus.EVENT_UNHANDLED:
                logger.debug(
                    f"Unhandled event {event} in state {current_node.__name__}"
                )
                if current_node._superstate is None:
                    logger.debug(f"Reached root state {current_node.__name__}")
                    return node_path[0]
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
        next_node = node_path[0]
        while next_node != lca and next_node._superstate is not None:
            next_node.exit(state)
            next_node = next_node._superstate

        # start the entry path past the LCA
        entry_path = tuple(reversed(target_node_path_to_root))
        entry_path = tuple(entry_path[entry_path.index(lca) + 1 :])

        # check for an exit to a superstate in which no entries are called
        if len(entry_path) == 0:
            return next_node

        # do the entries from LCA to the new state
        next_node = entry_path[0]
        for entry_node in entry_path:
            if entry_node != next_node:
                logger.warning(
                    f"The entry return disagrees with the path -> Path is {entry_path}"
                )
                raise ValueError("The entry return disagrees with the entry path")
            next_node = entry_node.entry(state)

        return hsm_handle_entries(
            next_node, state, entry_path[-1] if entry_path else None
        )
