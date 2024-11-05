from typing import Literal as L

from examples.samek.state import State
from examples.samek.events import Event


def entry(state: State | None = None) -> None:
    print("            s211 entry")


def run_d(event: L[Event.d], state: State | None) -> None:
    print("            s211 run d")


def run_g(event: L[Event.g], state: State | None) -> None:
    print("            s211 run g")


def exit(state: State | None) -> None:
    print("            s211 exit")
