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
        super().__post_init__()
        super().setup(
            lower=1, 
            upper=LIGHT_COUNT,
            previous=6,
        )

    def execute(self) -> int | None:
        """Set current brightness. Return select_mode if 
           final brightness selected, else None."""
        self.lights.brightness_factor = self.desired / LIGHT_COUNT
        self.lights.set_channels(brightness=[100] * LIGHT_COUNT)
        new = super().execute()
        if new is not None:  # Selection was made.
            new = ModeIndex.SELECT_MODE
        return new

    def c_button_pressed(self) -> None:
        """Respond to C button press."""
        print("C button ignored in brightness select mode.")

