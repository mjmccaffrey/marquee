"""Marquee Lighted Sign Project - modeselect"""

from dataclasses import dataclass

from .mode_misc import ModeIndex
from .selectmode import SelectMode


@dataclass(kw_only=True)
class ModeSelect(SelectMode):
    """Allows user to select mode."""

    def __post_init__(self) -> None:
        """Initialize."""

        # Find most recent normal mode.
        previous = next(
            i for i in reversed(self.player.fg_mode_history) if i > 0
        )

        super().setup(
            lower=1, 
            upper=max(self.modes),
            previous=previous,
        )

    def c_button_pressed(self) -> None:
        """Respond to C button press."""
        self.desired = ModeIndex.SELECT_BRIGHTNESS

