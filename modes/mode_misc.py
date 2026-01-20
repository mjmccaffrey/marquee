"""Marquee Lighted Sign Project - mode_misc"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Any


@dataclass
class BGModeEntry:
    name: str
    seconds: float
    index: int = -1

@dataclass
class ModeDefinition:
    index: int
    name: str
    cls: type
    kwargs: dict[str, Any]

class ModeIndex(IntEnum):
    SELECT_BRIGHTNESS = -1
    COUNTER = -2
    SELECT_MODE = 0
    DEFAULT = 1

