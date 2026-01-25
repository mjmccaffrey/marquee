"""Marquee Lighted Sign Project - silentfadebuild"""

from dataclasses import dataclass
from functools import partial
import random

from .performancemode import PerformanceMode
from sequences import lights_in_groups


@dataclass(kw_only=True)
class SilentFadeBuild(PerformanceMode):
    """Alternately build rows / columns from top / bottom / left / right."""

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()
        self.lights.set_channels(brightness=0)
 
    def execute(self) -> None:
        """Perform SilentFadeBuild indefinitely."""
        due = 0.0
        for rows in (False, True):
            for from_top_left, brightness in (
                (True, random.randrange(70, 101)), (False, random.randrange(0, 40)),
                (False, random.randrange(70, 101)), (True, random.randrange(0, 40)),
            ):
                for lights in lights_in_groups(rows, from_top_left):
                    self.schedule(
                        partial(
                            self.lights.set_channels,
                            brightness=brightness,
                            transition=1.0,
                            color=self.lights.colors.random(),
                            channel_indexes=set(lights),
                        ),
                        due=due,
                    )
                    due += 0.5
                due += 1.0
            due += 1.0
        self.schedule(action=self.execute, due=due)

