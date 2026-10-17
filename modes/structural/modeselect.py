"""Marquee Lighted Sign Project - modeselect"""

from dataclasses import dataclass
import logging
from typing_extensions import override

from ..abstract.selectmode import SelectMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class ModeSelect(SelectMode):
    """Allows user to select the active mode."""
    previous: int

    def __post_init__(self) -> None:
        """Initialize."""
        super().setup(
            lower=1, 
            upper=max(self.modes),
            previous=self.previous,
        )

    @override
    def execute(self) -> None:
        """Set current brightness_factor."""
        new = super().execute()
        if new is not None:  # Final selection made.
            self.change_mode(new)

