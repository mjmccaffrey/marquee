"""Marquee Lighted Sign Project - modeselect"""

from dataclasses import dataclass

from .mode_misc import ModeIndex
from .selectmode import SelectMode


@dataclass(kw_only=True)
class ModeSelect(SelectMode):
    """Allows user to select mode."""
    previous: int

    def __post_init__(self) -> None:
        """Initialize."""
        self.lights.set_channels(
            brightness=100,
            color=self.lights.colors.ORANGE,
            on=True,
        )
        super().setup(
            lower=1, 
            upper=max(self.modes),
            previous=self.previous,
        )

    def execute(self) -> None:
        """Set current brightness_factor."""
        new = super().execute()
        if new is not None:  # Final selection made.
            self.change_mode(new)

    def c_button_pressed(self) -> None:
        """Respond to C button press."""
        self.desired = ModeIndex.SELECT_BRIGHTNESS

