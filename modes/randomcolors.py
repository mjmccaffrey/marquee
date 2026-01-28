"""Marquee Lighted Sign Project - dynamictest"""

from dataclasses import dataclass, replace

from .dynamicmode import DynamicMode
from specialparams import ChannelParams

@dataclass(kw_only=True)
class RandomColors(DynamicMode):
    """"""

    def generate(self, special: ChannelParams) -> ChannelParams:
        """Return new set of ChannelParams."""
        return replace(special, color_on=self.lights.colors.random())
    
