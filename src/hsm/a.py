from typing import Type, Literal

from hsm import HSMStatus, Event, A


def run_A(
    event_id: Literal[Event.ONE, Event.TWO] | Event,
) -> Type[A.B | A.C] | HSMStatus:
    if event_id == Event.ONE:
        return A.B
    elif event_id == Event.TWO:
        return A.C
    return HSMStatus.EVENT_ERROR_UNKNOWN_EVENT
