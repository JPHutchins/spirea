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
                        [TEvent, TState], Type["Node[TEvent, TState]"] | HSMStatus
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
            Callable[[TEvent, TState], Type["Node[TEvent, TState]"] | HSMStatus],
        ],
        ...,
    ]


def hsm_get_path_to_root(
    node: Type[Node[TEvent, TState]] | None,
) -> tuple[Type[Node[TEvent, TState]] | None, ...]:
    path: Final[list[Type[Node[TEvent, TState]] | None]] = [node]
    while node is not None:
        node = node._superstate
        path.append(node)

    return tuple(path)


def hsm_get_lca(
    path1: tuple[Type[Node[TEvent, TState]], ...],
    path2: tuple[Type[Node[TEvent, TState]], ...],
) -> Type[Node[TEvent, TState]] | None:
    print(f"Path1: {path1}")
    print(f"Path2: {path2}")
    for node in path1:
        if node in path2:
            return node

    return None


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


def hsm_handle_event(
    node_path: tuple[Type[Node[TEvent, TState]], ...],
    event: TEvent,
    state: TState | None = None,
) -> Type[Node[TEvent, TState]]:
    """
    Handle an event for the hierarchical state machine.

    Args:
        node (Type[Node]): The current state of the HSM.
        event (TEvent): The event to handle.

    Returns:
        Type[Node]: The new state after handling the event.

    Raises:
        ValueError: If an unknown event is encountered.
    """
    node, *_ = node_path

    # Log the current state and event
    logger.debug(f"Handling event {event} in state {node.__name__}")
    print(f"Handling event {event.name} in state {node.__name__}")

    for e, handler in node._event_handlers:
        if event == e:
            new_state_or_status = handler(event, state)
            break
    else:
        new_state_or_status = HSMStatus.EVENT_UNHANDLED

    print(new_state_or_status)

    # Check the returned value
    if isinstance(new_state_or_status, HSMStatus):
        if new_state_or_status == HSMStatus.NO_TRANSITION:
            logger.debug(f"No transition in state {node.__name__}")
            return node_path[-1]
        elif new_state_or_status == HSMStatus.SELF_TRANSITION:
            print(f"Doing self-transition for {node.__name__}")
            logger.debug(f"Self-transition in state {node.__name__}")
            for _node in reversed(node_path):
                _node.exit(state)
            return hsm_handle_entries(node, state)
        elif new_state_or_status == HSMStatus.EVENT_UNHANDLED:
            logger.debug(f"Unhandled event {event} in state {node.__name__}")
            if node._superstate is None:
                logger.debug(f"Reached root state {node.__name__}")
                return node_path[-1]
        else:
            assert_never(new_state_or_status)

    # if the new state is a node, then we can get the LCA
    if _is_hsm_node(new_state_or_status):
        path_to_root = hsm_get_path_to_root(node)
        next_node_path_to_root = hsm_get_path_to_root(new_state_or_status)
        lca = hsm_get_lca(next_node_path_to_root, path_to_root)

        print(f"LCA: {lca}")

        node = node_path[-1]
        while node != lca:
            print(f"doing exit for {node.__name__}")
            node.exit(state)
            node = node._superstate

        # do the entries from LCA to the new state
        entry_path = tuple(reversed(next_node_path_to_root))
        print(f"Entry path: {entry_path}")

        # start the entry path past the LCA
        entry_path = entry_path[entry_path.index(lca) + 1 :]

        print(f"Entry path: {entry_path}")

        if len(entry_path) == 0:
            # There are not entries to do, we exited to a super state
            return node

        next = entry_path[0] if entry_path else None
        for node in entry_path:
            if node != next:
                logger.warning(
                    "The entry return disagrees with the path -"
                    f"Entry of {node.__name__} returned {next.__name__} but expected {node.__name__}"
                    f"Path is {entry_path}"
                )
                # raise ValueError("The entry return disagrees with the path")
            next = node.entry(state)

        return hsm_handle_entries(next, state, entry_path[-1] if entry_path else None)

    else:  # see if we can handle the event in the superstate
        return hsm_handle_event((node._superstate,) + node_path, event, state)
