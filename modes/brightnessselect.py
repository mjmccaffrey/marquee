"""Marquee Lighted Sign Project - brightnessselect"""

from dataclasses import dataclass

from .mode_misc import ModeIndex
from .selectmode import SelectMode
from lightset_misc import LIGHT_COUNT


@dataclass(kw_only=True)
class BrightnessSelect(SelectMode):
    """Allows user to adjust overall brightness."""

    def __post_init__(self) -> None:
        """Initialize."""
        INITIAL_LEVEL = 6
        self.set_brightness_level(INITIAL_LEVEL)
        self.lights.set_channels(
            brightness=100,
            color=self.lights.colors.ORANGE,
            on=True,
        )
        super().setup(
            lower=1, 
            upper=LIGHT_COUNT,
            previous=INITIAL_LEVEL,
        )

    def set_brightness_level(self, level: int) -> None:
        """"""
        self.lights.brightness_factor = level / LIGHT_COUNT

    def execute(self) -> None:
        """Set current brightness_factor."""
        self.set_brightness_level(self.desired)
        new = super().execute()
        if new is not None:  # Final selection made.
            self.change_mode(ModeIndex.DEFAULT)

    def c_button_pressed(self) -> None:
        """Respond to C button press."""
        print("C button ignored in brightness select mode.")

