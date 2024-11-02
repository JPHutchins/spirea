from typing import Type, Literal, NamedTuple

from enum import IntEnum

from hsm import Node, hsm_get_lca, hsm_get_path_to_root, HSMStatus

print(Node)


class Event(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4


class State(NamedTuple):
    pass


class A(Node[State, Event]):
    __slots__ = ()

    @classmethod
    def run(
        cls, state: State, event: Literal[Event.ONE, Event.TWO] | Event
    ) -> Type["A.B"] | Type["A.C"] | HSMStatus:
        if event == Event.ONE:
            return A.B
        elif event == Event.TWO:
            return A.C
        return HSMStatus.EVENT_ERROR_UNKNOWN_EVENT

    class B(Node[State, Event]):
        __slots__ = ()

        @classmethod
        def run(cls, event: Literal[Event.THREE, Event.FOUR] | Event) -> Type["A.C"]:
            return A.C

    class C(Node[State, Event]):
        __slots__ = ()

        @classmethod
        def run(cls, event: IntEnum) -> Type["A.C.D"] | Type["A.B"]:
            if event == Event.THREE:
                return A.B
            return A.C.D

        class D(Node[State, Event]):
            @classmethod
            def run(cls, event: IntEnum) -> HSMStatus:
                return HSMStatus.NO_TRANSITION


def test_tests() -> None:
    assert True


def test_init() -> None:
    print(A.run.__annotations__["event"].__args__)

    assert {Event.ONE, Event.TWO} == set(
        A.run.__annotations__["event"].__args__[0].__args__
    )
    assert {Event.ONE, Event.TWO} == set(A.run_events())

    pathA = hsm_get_path_to_root(A)
    assert pathA == (A,)

    pathB = hsm_get_path_to_root(A.B)
    assert pathB == (A.B, A)

    pathC = hsm_get_path_to_root(A.C)
    assert pathC == (A.C, A)

    pathD = hsm_get_path_to_root(A.C.D)
    assert pathD == (A.C.D, A.C, A)

    lca = hsm_get_lca(pathB, pathC)
    assert lca == A

    lca = hsm_get_lca(pathB, pathD)
    assert lca == A

    lca = hsm_get_lca(pathC, pathD)
    assert lca == A.C

    lca = hsm_get_lca(pathA, pathD)
    assert lca == A

    lca = hsm_get_lca(pathA, pathB)
    assert lca == A

    lca = hsm_get_lca(pathA, pathC)
    assert lca == A

    lca = hsm_get_lca(pathA, pathA)
    assert lca == A

    lca = hsm_get_lca(pathB, pathB)
    assert lca == A.B

    lca = hsm_get_lca(pathC, pathC)
    assert lca == A.C

    lca = hsm_get_lca(pathD, pathD)
    assert lca == A.C.D
