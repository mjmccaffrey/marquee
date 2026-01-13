"""Marquee Lighted Sign Project - background_modes"""

from abc import ABC, abstractmethod
from calendar import timegm
from collections.abc import Iterator
from dataclasses import dataclass, field
from itertools import cycle
from time import gmtime, time
from typing import Callable, ClassVar, NoReturn

from button_misc import ButtonInterface
from .basemode import BaseMode
from .mode_misc import ModeConstructor, ModeIndex


@dataclass
class BackgroundMode(BaseMode, ABC):
    """Base for all background modes.
       Background modes should not play anything directly."""
    modes: ClassVar[dict[int, ModeConstructor]]
    mode_ids: ClassVar[dict[str, int]]

    @abstractmethod
    def execute(self) -> int:
        """Return index of next mode."""

