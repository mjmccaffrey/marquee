"""Marquee Lighted Sign Project - backgroundmode"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from .basemode import BaseMode
from .mode_misc import ModeConstructor


@dataclass
class BackgroundMode(BaseMode, ABC):
    """Base for all background modes.
       Background modes should not play anything directly."""
    modes: ClassVar[dict[int, ModeConstructor]]
    mode_ids: ClassVar[dict[str, int]]

