from typing import Literal as L

from examples.samek.state import State
from examples.samek.events import Event


def entry(state: State | None = None) -> None:
    print("s0 entry")


def run_e(event: L[Event.e], state: State | None) -> None:
    print("s0 run e")


def exit(state: State | None) -> None:
    print("s0 exit")
