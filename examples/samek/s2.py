from typing import Literal as L

from examples.samek.state import State
from examples.samek.events import Event


def entry(state: State | None = None) -> None:
    print("    s2 entry")


def run_c(event: L[Event.c], state: State | None) -> None:
    print("    s2 run c")


def run_f(event: L[Event.f], state: State | None) -> None:
    print("    s2 run f")


def exit(state: State | None) -> None:
    print("    s2 exit")
