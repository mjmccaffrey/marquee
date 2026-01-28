"""Marquee Lighted Sign Project - dynamictest"""

from collections.abc import Sequence
from dataclasses import dataclass, replace
from itertools import chain

from .dynamicmode import DynamicMode
from specialparams import ChannelParams

@dataclass(kw_only=True)
class RandomColors(DynamicMode):
    """"""

    def generate(self, special: ChannelParams) -> ChannelParams:
        """Return new set of ChannelParams."""
        return replace(special, color_on=self.lights.colors.random())

@dataclass(kw_only=True)
class SequentialBrightness(DynamicMode):
    """"""
    sequence: Sequence

    def __post_init__(self) -> None:
        """Initialize."""
        seq_iter = chain(self.sequence)
        super().__post_init__()

    def generate(self, special: ChannelParams) -> ChannelParams:
        """Return modified ChannelParams."""
        return special
    
