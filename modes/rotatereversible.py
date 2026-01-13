"""Marquee Lighted Sign Project - rotatereversible"""

from dataclasses import dataclass

from .performancemode import PerformanceMode
            

@dataclass(kw_only=True)
class RotateReversible(PerformanceMode):
    """Rotate a pattern, reversing direction in response to a button press."""
    delay: float
    pattern: str

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()
        self.lights.set_channels(brightness=100, on=True, force=True)
        self.pattern = self.lights.relay_pattern

    def execute(self) -> None:
        """"""
        
        # !!!! Need button handler to swap directions.

        self.pattern = (
            self.pattern[self.direction:] + 
            self.pattern[:self.direction]
        )
        self.lights.set_relays(light_pattern=self.pattern)
        self.schedule(
            action=self.execute,
            due_rel=self.delay,
        )

