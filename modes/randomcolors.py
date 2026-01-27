"""Marquee Lighted Sign Project - dynamictest"""

from .dynamicmode import DynamicMode
from specialparams import ChannelParams


class RandomColors(DynamicMode):
    """"""

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()

    def generate_special(self) -> ChannelParams:
        """Return new set of ChannelParams."""
        return ChannelParams(
            brightness_on=100,
            color_on=self.lights.colors.random(),
            trans_on=0.0,
            trans_off=0.0,
            generate=self.generate_special,
        )

