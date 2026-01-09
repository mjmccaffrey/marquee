"""Marquee Lighted Sign Project - mode_misc"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Any

@dataclass
class ModeConstructor:
    index: int
    name: str
    cls: type
    kwargs: dict[str, Any]

@dataclass
class ModeEntry:
    name: str
    seconds: float
    index: int = -1

class ModeIndex(IntEnum):
    SELECT_BRIGHTNESS = -99
    SELECT_MODE = 0
    DEFAULT = 1
