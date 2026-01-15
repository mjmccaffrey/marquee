"""Marquee Lighted Sign Project - dynamictest"""

from .dynamicmode import DynamicMode
from specialparams import ChannelParams


class RandomColors(DynamicMode):
    """"""

    def generate_special(self) -> ChannelParams:
        """Return new set of ChannelParams."""
        delay = self.mode.kwargs['delay']
        return ChannelParams(
            brightness_on=100,
            brightness_off=100,
            color_on=self.lights.colors.random(),
            color_off=self.lights.colors.random(),
            generate=self.generate_special,
            trans_on=delay,
            trans_off=delay,
        )

