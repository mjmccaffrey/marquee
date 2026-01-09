"""Marquee Lighted Sign Project - custom_modes"""

from dataclasses import dataclass
from functools import partial
import random

from lightset_misc import (
    ALL_HIGH, ALL_LOW, ALL_ON, LIGHT_COUNT,
)
from music.music_notation import Bell
from .playmode import PlayMode
from sequences import lights_in_groups, opposite, rotate
from specialparams import ChannelParams


# @dataclass(kw_only=True)
# class BellTest(PlayMusicMode):
#     """Test all bells."""

#     def __post_init__(self) -> None:
#         """Initialize."""
#         self.preset_devices()

#     def execute(self) -> None:
#         """Perform bell test."""
#         for pitch in range(self.bells.pitch_levels):
#             due = 0.5 * pitch
#             self.schedule(
#                 action = partial(self.bells.play, {pitch}),
#                 due = due,
#                 name = f"BellTest play {pitch}",
#             )
#             self.schedule(
#                 action = partial(self.bells.release, {pitch}),
#                 due = due + self.bells.release_time,
#                 name = f"BellTest release {pitch}",
#             )
            

@dataclass(kw_only=True)
class RotateReversible(PlayMode):
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


@dataclass(kw_only=True)
class RandomFade(PlayMode):
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
                self.player.lights.trans_min, 
                5.0 * self.player.speed_factor
            )
        )

    def new_duration(self) -> float:
        """Return either specified or random duration."""
        return (
            self.duration 
                if self.duration is not None else
            random.uniform(0, 8.0 * self.player.speed_factor)
        )

    def new_brightness(self, current: int) -> int:
        """Return random brightness significantly
           different than current brightness."""
        new = current
        while abs(new - current) < 20:
            new = random.randrange(101)
        assert isinstance(new, int)
        return new

    def update_light(self, index: int):
        """Update light to random / specified values.
           Schedule next update of light."""
        brightness = self.new_brightness(
            current=self.brightnesses[index],
        )
        transition = self.new_transition()
        duration = self.new_duration()
        self.lights.set_channels(
            brightness=brightness,
            transition=transition,
            channel_indexes=(index,)
        )
        self.brightnesses[index] = brightness

        self.schedule(
            action=partial(self.update_light, index=index),
            due_rel=(transition + duration),
            name=f"RandomFade update_light {index}",
        )

    def execute(self) -> None:
        """Start each bulb off on its unique journey."""
        print("***** EXECUTE *****")
        for light in range(self.lights.count):
            self.update_light(light)


@dataclass(kw_only=True)
class EvenOddFade(PlayMode):
    """Fade every-other bulb."""
    delay: float

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()
        self.lights.set_relays(ALL_ON)

    def execute(self) -> None:
        """Schedule next 2 patterns. Schedule next execute."""
        self.lights.set_channels(brightness=0) 
        odd_on = ''.join('1' if i % 2 else '0' for i in range(LIGHT_COUNT))
        even_on = opposite(odd_on)
        for i, pattern in enumerate((even_on, odd_on)):
            self.schedule(
                action=partial(
                    self.lights.set_relays,
                    pattern, 
                    special=ChannelParams(
                        concurrent=True,
                        brightness_on = 90,
                        brightness_off = 10,
                        trans_on=self.delay,
                        trans_off=self.delay,
                    )
                ),
                due_rel=(self.delay * i)
            )
        self.schedule(
            action=self.execute,
            due_rel=(self.delay * (i + 1))
        )


@dataclass(kw_only=True)
class SilentFadeBuild(PlayMode):
    """Alternately build rows / columns from top / bottom / left / right."""

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()
        self.player.lights.set_channels(brightness=0)
 
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
                            self.player.lights.set_channels,
                            brightness=brightness,
                            transition=1.0,
                            color=self.lights.colors.random(),
                            channel_indexes=lights,
                        ),
                        due_rel=due,
                    )
                    due += 0.5
                due += 1.0
            due += 1.0
        self.schedule(action=self.execute, due_rel=due)

