"""Marquee Lighted Sign Project - backgroundmode"""

from abc import ABC
from dataclasses import dataclass

from .basemode import BaseMode


@dataclass
class BackgroundMode(BaseMode, ABC):
    """Base for all background modes.
       Background modes should not play 
       any lights, instruments, etc. directly."""

