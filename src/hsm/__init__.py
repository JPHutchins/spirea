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
    Protocol as TypingProtocol,
    runtime_checkable,
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


class StateMeta(type):
    def __new__(cls, name, bases, dct):
        dct["substates"] = []
        dct["superstate"] = None
        dct["__hsm_node"] = True
        new_cls = super().__new__(cls, name, bases, dct)

        for base in bases:
            if isinstance(base, StateMeta):
                print(base, base.superstate, new_cls)
                new_cls.superstate = base

                # the impl can use this to update referencees to its base with
                # updates to itself.  Use the substates for this
                print(base.__subclasses__())

                for substate in base.substates:
                    print(substate, substate.superstate, new_cls)
                    base.superstate = new_cls.superstate
                    # new_cls.substates.append(substate)

        for _, attr_value in dct.items():
            if hasattr(attr_value, "__hsm_node") is True:
                new_cls.substates.append(attr_value)
                attr_value.superstate = new_cls

        return new_cls


class CombinedMeta(type(TypingProtocol), StateMeta):
    pass


class Node(Protocol[TEvent], metaclass=CombinedMeta):
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


def hsm_get_path_to_root(node: Type[Node]) -> tuple[Type[Node], ...]:
    path: Final[list[Type[Node]]] = [node]
    print(node)
    print(node.superstate)
    while node.superstate is not None:
        print(node)
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


# assert StateA.superstate is None
assert StateA.StateB.superstate is StateA
assert StateA.StateC.superstate is StateA
assert StateA.StateC.StateD.superstate is StateA.StateC

assert StateA.substates == [StateA.StateB, StateA.StateC]


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


# assert A.superstate is None
# assert A.substates == [A.StateB, A.StateC], A.substates


class B(StateA.StateB):
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


assert B.superstate is A


class C(StateA.StateC):
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


class D(StateA.StateC.StateD):
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
