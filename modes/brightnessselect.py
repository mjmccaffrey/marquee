"""Marquee Lighted Sign Project - brightnessselect"""

from dataclasses import dataclass
import logging
from typing import override

from .modes_misc import ModeIndex
from .selectmode import SelectMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class BrightnessSelect(SelectMode):
    """Allows user to adjust overall brightness."""

    def __post_init__(self) -> None:
        """Initialize."""
        INITIAL_LEVEL = 6
        self.set_brightness_level(INITIAL_LEVEL)
        super().setup(
            lower=1, 
            upper=self.lights.count,
            previous=INITIAL_LEVEL,
        )

    def set_brightness_level(self, level: int) -> None:
        """"""
        self.lights.brightness_factor = level / self.lights.count

    @override
    def execute(self) -> None:
        """Set current brightness_factor."""
        self.set_brightness_level(self.desired)
        new = super().execute()
        if new is not None:  # Final selection made.
            self.change_mode(ModeIndex.DEFAULT)

