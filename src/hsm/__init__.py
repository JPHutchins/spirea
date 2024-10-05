import logging
from typing import (
    Final,
    Protocol,
    Type,
    Union,
    Optional,
    TypeVar,
    NamedTuple,
    Literal,
    overload,
    override,
)
from enum import IntEnum


logger: Final = logging.getLogger(__name__)

TEvent = TypeVar("TEvent", bound=IntEnum, contravariant=True)


class HSMStatus(IntEnum):
    NO_TRANSITION = -2_147_483_648
    SELF_TRANSITION = -2_147_483_647
    EVENT_UNHANDLED = -2_147_483_646
    """No run actions were taken"""
    EVENT_ERROR_UNKNOWN_EVENT = -2_147_483_645
    """The event ID was not recognized"""
    ERROR_TRANSITION_NO_LCA = -2_147_483_644
    """No least common ancestor was found"""
    ERROR_TRANSITION_ENTRY_IS_NULL = -2_147_483_643
    """The entry action is NULL"""
    ERROR_TRANSITION_RUN_IS_NULL = -2_147_483_642
    """The run action is NULL"""
    ERROR_TRANSITION_EXIT_IS_NULL = -2_147_483_641
    """The exit action is NULL"""
    PARENT_OF_ROOT_NODE = -2_147_483_640
    """The root node of the state tree was reached"""


class Node(Protocol[TEvent]):
    __slots__ = ()

    @classmethod
    def entry(cls) -> Type["Node"]: ...

    @classmethod
    def run(cls, event_id: TEvent) -> Type["Node"] | HSMStatus: ...

    @classmethod
    def run_events(cls) -> tuple[IntEnum, ...]:
        return cls.run.__annotations__["event_id"].__args__

    @classmethod
    def exit(cls) -> None: ...

    superstate: Type["Node"]

    substates: tuple[Type["Node"], ...]


class Root(Node):
    __slots__ = ()

    @classmethod
    def entry(cls) -> Type[Node]:
        return Root

    @classmethod
    def run(cls, event_id: IntEnum) -> Type[Node] | HSMStatus:
        return Root

    @classmethod
    def exit(cls) -> None: ...

    superstate = Type["Root"]
    substates = ()

    class Event(IntEnum):
        pass


def _get_substates(
    node: Type[Node], state_impls: tuple[Type[Node], ...]
) -> tuple[Type[Node], ...]:
    state_names = tuple(
        name.replace("State", "") for name in dir(node) if name.startswith("State")
    )

    return tuple(impl for impl in state_impls if impl.__name__ in state_names)


def hsm_init(
    initial_state: Type[Node], state_impls: tuple[Type[Node], ...]
) -> Type[Node]:
    """Walk the state tree from the initial state to every leaf in order to
    initialize the superstate class variables."""

    if initial_state.superstate is not Root:
        raise ValueError("The initial state must have Root as superstate!")

    def walk_tree(node: Type[Node], superstate: Type[Node]) -> None:
        node.substates = _get_substates(node, state_impls)
        for substate in node.substates:
            walk_tree(substate, node)

        node.superstate = superstate

    walk_tree(initial_state, Root)

    return initial_state


def generate_mermaid(node: Type[Node]) -> str:
    """Generate a Mermaid diagram representation of the state hierarchy."""
    mermaid_lines = ["stateDiagram-v2"]

    # Dictionary to hold states and their substates for later reference
    state_definitions = {}

    def collect_states(node: Type[Node]):
        """Recursively collect state and substate names."""
        state_definitions[node.__name__] = []
        for substate in node.substates:
            state_definitions[node.__name__].append(substate)
            collect_states(substate)

    collect_states(node)  # Collect all states

    # Generate state definitions for Mermaid
    for state_name in state_definitions.keys():
        mermaid_lines.append(f"state {state_name} {{")
        mermaid_lines.append(f"    [*] --> [*]")  # Entry point for each state
        mermaid_lines.append(f"}}")  # Closing the state

    # Generate transitions
    mermaid_lines.append(f"[*] --> {node.__name__}")  # Starting point
    for state_name, substates in state_definitions.items():
        for substate in substates:
            mermaid_lines.append(f"{state_name} --> {substate.__name__}")

    # Ensure end transitions are correctly defined
    for state_name in state_definitions.keys():
        mermaid_lines.append(f"{state_name} --> [*]")  # End transition for each state

    return "\n".join(mermaid_lines)


def hsm_get_path_to_root(node: Type[Node]) -> tuple[Type[Node], ...]:
    path: Final[list[Type[Node]]] = [node]
    while node.superstate is not Root:
        node = node.superstate
        path.append(node)

    return tuple(path)


def hsm_get_lca(
    path1: tuple[Type[Node], ...], path2: tuple[Type[Node], ...]
) -> Type[Node]:
    for node in path1:
        if node in path2:
            return node

    return Root


def hsm_handle_event(current_state: Type[Node], event_id: TEvent) -> Type[Node]:
    """
    Handle an event for the hierarchical state machine.

    Args:
        current_state (Type[Node]): The current state of the HSM.
        event_id (TEvent): The event to handle.

    Returns:
        Type[Node]: The new state after handling the event.

    Raises:
        ValueError: If an unknown event is encountered.
    """
    # Log the current state and event
    logger.info(f"Handling event {event_id} in state {current_state.__name__}")

    # Call the entry action of the current state if it's the first event
    if current_state is not None:
        current_state.entry()

    # Handle the event in the current state
    new_state_or_status = current_state.run(event_id)

    # Check the returned value
    if isinstance(new_state_or_status, HSMStatus):
        if new_state_or_status == HSMStatus.EVENT_ERROR_UNKNOWN_EVENT:
            logger.error(f"Unknown event {event_id} in state {current_state.__name__}")
            raise ValueError(
                f"Unknown event {event_id} in state {current_state.__name__}"
            )

        # Handle other HSMStatus values as needed
        return current_state  # No state change, return current state

    # If the return type is a new state, exit the current state and enter the new state
    if new_state_or_status != current_state:
        current_state.exit()  # Exit the current state
        new_state_or_status.entry()  # Enter the new state

    return new_state_or_status


class Event(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4


class StateA(Node, Protocol):
    __slots__ = ()

    superstate: Type["Node"] = Root

    @overload
    @classmethod
    def run(cls, event_id: Literal[Event.ONE]) -> Type["StateA.StateB"]: ...

    @overload
    @classmethod
    def run(cls, event_id: Literal[Event.TWO]) -> Type["StateA.StateC"]: ...

    @overload
    @classmethod
    def run(
        cls, event_id: Literal[Event.ONE, Event.TWO]
    ) -> Union[Type["StateA.StateB"], Type["StateA.StateC"]]: ...

    class StateB(Node, Protocol):
        __slots__ = ()

        @classmethod
        def run(
            cls, event_id: Literal[Event.THREE, Event.FOUR]
        ) -> Type["StateA.StateC"]: ...

    class StateC(Node, Protocol):
        __slots__ = ()

        @classmethod
        def run(
            cls, event_id: IntEnum
        ) -> Type["StateA.StateC.StateD"] | Type["StateA.StateB"]: ...

        class StateD(Node, Protocol):
            @classmethod
            def run(cls, event_id: IntEnum) -> HSMStatus: ...


class A(StateA):
    __slots__ = ()

    @classmethod
    def entry(cls) -> Type["A"]:
        logger.info("A.entry")
        return A

    @overload
    @classmethod
    def run(cls, event_id: Literal[Event.ONE]) -> Type["B"]: ...

    @overload
    @classmethod
    def run(cls, event_id: Literal[Event.TWO]) -> Type["C"]: ...

    @classmethod
    def run(
        cls, event_id: Literal[Event.ONE, Event.TWO]
    ) -> Union[Type["StateA.StateB"], Type["StateA.StateC"]]:
        if event_id == Event.ONE:
            return A
        elif event_id == Event.TWO:
            return C
        raise ValueError(f"Invalid event_id: {event_id}")

    @classmethod
    def exit(cls) -> None:
        logger.info("A.exit")


class B(A.StateB):
    __slots__ = ()

    @classmethod
    def entry(cls) -> None:
        logger.info("B.entry")

    @classmethod
    def run(cls, event_id: IntEnum) -> Type["C"]:
        return C

    @classmethod
    def exit(cls) -> None:
        logger.info("B.exit")


class C(A.StateC):
    @classmethod
    def entry(cls) -> None:
        logger.info("C.entry")

    @classmethod
    def run(cls, event_id: IntEnum) -> Type[B] | Type["D"]:
        if event_id == 0:
            return B
        return D

    @classmethod
    def exit(cls) -> None:
        logger.info("C.exit")


class D(C.StateD):
    @classmethod
    def entry(cls) -> None:
        logger.info("D.entry")

    @classmethod
    def run(cls, event_id: IntEnum) -> None:
        logger.info("D.run")
        return None

    @classmethod
    def exit(cls) -> None:
        logger.info("D.exit")
