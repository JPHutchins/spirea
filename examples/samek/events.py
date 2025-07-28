# Copyright (c) 2025 JP Hutchins
# SPDX-License-Identifier: MIT

from typing import NamedTuple


class EventA(NamedTuple): ...


class EventB(NamedTuple): ...


class EventC(NamedTuple): ...


class EventD(NamedTuple): ...


class EventE(NamedTuple): ...


class EventF(NamedTuple): ...


class EventG(NamedTuple): ...


class EventH(NamedTuple): ...


type Event = EventA | EventB | EventC | EventD | EventE | EventF | EventG | EventH
