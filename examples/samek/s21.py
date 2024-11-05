from typing import Literal as L

from hsm.sync import HSMStatus
from examples.samek.state import State
from examples.samek.events import Event


def entry(state: State | None = None) -> None:
    print("        s21 entry")


def run_b(event: L[Event.b], state: State | None) -> None:
    print("        s21 run b")


def run_h(
    event: L[Event.h], state: State
) -> L[HSMStatus.SELF_TRANSITION] | L[HSMStatus.NO_TRANSITION]:

    if state.foo == 0:
        state.foo = 1
        print(f"        s21 run h {state.foo=}")
        return HSMStatus.SELF_TRANSITION
    else:
        print("        s21 run h")
        return HSMStatus.NO_TRANSITION


def exit(state: State | None) -> None:
    print("        s21 exit")
