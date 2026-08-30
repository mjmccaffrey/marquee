"""Marquee Lighted Sign Project - mode_schemas"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class ChangeMode(Exception):
    """Change mode exception."""

@dataclass
class CycleEntry:
    name: str
    seconds: float | None
    index: int = -1

CycleSequence = list[tuple[str, int | None]]

@dataclass(kw_only=True)
class ModeDefinition:
    index: int | None = None
    name: str
    cls: type  # !!!
    kwargs: dict[str, Any] = field(default_factory=dict)

class ModeIndex(IntEnum):
    BRIGHTNESS_SELECT = -1
    MODE_SELECT = 0
    DEFAULT = 1

