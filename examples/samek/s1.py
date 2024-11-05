from typing import Literal as L

from examples.samek.state import State
from examples.samek.events import Event


def entry(state: State | None = None) -> None:
    print("    s1 entry")


def run_a(event: L[Event.a], state: State | None) -> None:
    print("    s1 run a")


def run_b(event: L[Event.b], state: State | None) -> None:
    print("    s1 run b")


def run_c(event: L[Event.c], state: State | None) -> None:
    print("    s1 run c")


def run_d(event: L[Event.d], state: State | None) -> None:
    print("    s1 run d")


def run_f(event: L[Event.f], state: State | None) -> None:
    print("    s1 run f")


def exit(state: State | None) -> None:
    print("    s1 exit")
