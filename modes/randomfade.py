"""Marquee Lighted Sign Project - randomfade"""

from dataclasses import dataclass
from functools import partial
import random

from color import XY
from lightset_misc import ALL_ON
from .performancemode import PerformanceMode


@dataclass(kw_only=True)
class RandomFade(PerformanceMode):
    """Change brightness of random bulb to a random level,
       with either random or specified transition time.
       Remain at that brightness for either trandom or 
       specified duration."""
    transition: float | None = None
    duration: float | None = None

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()
        self.lights.set_relays(ALL_ON)
        self.brightnesses = self.lights.brightnesses()

    def new_transition(self) -> float:
        """Return either specified or random transition."""
        return (
            self.transition 
                if self.transition is not None else
            random.uniform(
                self.lights.trans_min, 
                5.0 * self.speed_factor
            )
        )

    def new_duration(self) -> float:
        """Return either specified or random duration."""
        return (
            self.duration 
                if self.duration is not None else
            random.uniform(0, 8.0 * self.speed_factor)
        )

    def new_brightness(self, current: int) -> int:
        """Return random brightness significantly
           different than current brightness."""
        new = current
        while abs(new - current) < 20:
            new = random.randrange(101)
        assert isinstance(new, int)
        return new

    def new_color(self) -> XY:
        """Return random color."""
        return self.lights.colors.random()

    def update_light(self, index: int):
        """Update light to random / specified values.
           Schedule next update of light."""
        brightness = self.new_brightness(
            current=self.brightnesses[index],
        )
        transition = self.new_transition()
        color = self.new_color()
        duration = self.new_duration()
        self.lights.set_channels(
            brightness=brightness,
            transition=transition,
            color=color,
            channel_indexes={index},
        )
        self.brightnesses[index] = brightness

        self.schedule(
            action=partial(self.update_light, index=index),
            due=(transition + duration),
            name=f"RandomFade update_light {index}",
        )

    def execute(self) -> None:
        """Start each bulb off on its unique journey."""
        for light in range(self.lights.count):
            self.update_light(light)

