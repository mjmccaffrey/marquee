"""Marquee Lighted Sign Project - modes_misc"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Any

@dataclass
class CycleEntry:
    name: str
    seconds: float
    index: int = -1

CycleSequence = list[tuple[str, int]]

class ChangeMode(Exception):
    """Change mode exception."""

class InterruptMode(Exception):
    """Event that mode handles itself."""

@dataclass
class ModeDefinition:
    index: int
    name: str
    cls: type  # !!!
    kwargs: dict[str, Any]

class ModeIndex(IntEnum):
    COUNTER = -2
    BRIGHTNESS_SELECT = -1
    MODE_SELECT = 0
    DEFAULT = 1

