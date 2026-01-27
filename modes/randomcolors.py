"""Marquee Lighted Sign Project - dynamictest"""

from .dynamicmode import DynamicMode
from specialparams import ChannelParams


class RandomColors(DynamicMode):
    """!!! Currently sends color commands to each bulb,
           even the 11 that are OFF. !!!"""

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()

    def generate_special(self) -> ChannelParams:
        """Return new set of ChannelParams."""
        # delay = self.mode.kwargs['delay']
        return ChannelParams(
            brightness_on=100,
            brightness_off=100,
            color_on=self.lights.colors.random(),
            color_off=self.lights.colors.random(),
            generate=self.generate_special,
            trans_on=0.0,
            trans_off=0.0,
        )

