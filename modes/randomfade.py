"""Marquee Lighted Sign Project - randomfade"""

from dataclasses import dataclass
from functools import partial
import random
from typing_extensions import override

from device_defs import ALL_ON
from devices.color import XY
from . import PerformanceMode


@dataclass(kw_only=True)
class RandomFade(PerformanceMode):
    """Change brightness of random bulb to a random level,
       with either random or specified transition time.
       Remain at that brightness for either random or 
       specified duration."""
    transition: float | None = None
    duration: float | None = None
    color_set_name: str | None = None

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()
        self.lights.set_relays(ALL_ON)
        self.lights.set_channels(on=True)
        self.brightnesses = self.lights.brightnesses()

    def new_transition(self) -> float:
        """Return either specified or random transition."""
        if self.transition is not None:
            return self.transition 
        else:
            return random.uniform(
                self.lights.trans_min, 
                5.0 * self.speed_factor
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
        if self.color_set_name is None:
            new = self.lights.colors.random()
        else:
            color_set = self.color_sets.by_set_name[self.color_set_name]
            choice = random.choice(color_set.colors)
            new = XY(choice.x, choice.y)
        return new

    def update_light_schedule_next(self, index: int) -> None:
        """"""
        due = self.update_light(index)
        self.schedule(
            action=partial(self.update_light_schedule_next, index=index),
            due=due,
            name=f"RandomFade update light {index}",
        )

    def update_light(self, index: int) -> float:
        """Update light to random / specified values.
           Return relative time for next update."""
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
            index=index,
        )
        self.brightnesses[index] = brightness
        return transition + duration

    @override
    def execute(self) -> None:
        """Start each bulb off on its unique journey."""
        for light in range(self.lights.count):
            self.update_light_schedule_next(light)

