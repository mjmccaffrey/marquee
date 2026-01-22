"""Marquee Lighted Sign Project - brightnessselect"""

from dataclasses import dataclass

from .mode_misc import ModeIndex
from .selectmode import SelectMode
from lightset_misc import LIGHT_COUNT


@dataclass(kw_only=True)
class BrightnessSelect(SelectMode):
    """Allows user to select maximum brightness."""

    def __post_init__(self) -> None:
        """Initialize."""
        super().setup(
            lower=1, 
            upper=LIGHT_COUNT,
            previous=6,
        )

    def execute(self) -> None:
        """Set current brightness_factor."""
        self.lights.brightness_factor = self.desired / LIGHT_COUNT
        self.lights.set_channels(brightness=[100] * LIGHT_COUNT)
        new = super().execute()
        if new is None:  # Final selection not made.
            self.schedule(self.execute, due_rel=10.0)
        else:  # Final selection made.
            self.change_mode(ModeIndex.DEFAULT)

    def c_button_pressed(self) -> None:
        """Respond to C button press."""
        print("C button ignored in brightness select mode.")

