from typing import Literal as L

from examples.samek.state import State
from examples.samek.events import Event


def entry(state: State | None = None) -> None:
    print("        s11 entry")


def run_e(event: L[Event.e], state: State | None) -> None:
    print("        s11 run e")


def exit(state: State) -> None:
    if state.foo == 1:
        state.foo = 0
        print(f"        s11 exit {state.foo=}")
    else:
        print("        s11 exit")
