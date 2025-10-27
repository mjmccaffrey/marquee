"""Marquee Lighted Sign Project - mode_misc"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Type


class ChangeMode(Exception):
    """Change mode exception."""


@dataclass
class ModeConstructor:
    name: str
    mode_class: Type
    kwargs: dict[str, Any]


class ModeIndex(IntEnum):
    SELECT_BRIGHTNESS = -99
    SELECT_MODE = 0
    DEFAULT = 1

