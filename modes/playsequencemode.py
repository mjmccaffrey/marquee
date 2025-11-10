"""Marquee Lighted Sign Project - playsequencemode"""

from collections.abc import Callable
from functools import partial
import itertools
import time
from typing import Iterable

from .foregroundmode import ForegroundMode
from .playmode import PlayMode
from dimmers import TRANSITION_DEFAULT
from player import Player
from specialparams import ActionParams, DimmerParams, SpecialParams

class PlaySequenceMode(PlayMode):
    """Supports all sequence-based modes."""
    def __init__(
        self,
        player: Player,
        index: int,
        name: str,
        sequence: Callable[[], Iterable],
        delay: tuple[float, ...] | float | None = None,
        stop: int | None = None,
        repeat: bool = True,
        special: SpecialParams | None = None,
        **kwargs,
    ) -> None:
        """Initialize."""
        super().__init__(player, index, name, special)
        ForegroundMode.__post_init__(self) # !!!
        self.sequence = sequence
        self.delay = delay
        self.stop = stop
        self.repeat = repeat
        self.kwargs = kwargs
        if isinstance(special, DimmerParams):
            default_trans = (
                delay if isinstance(delay, float) else
                TRANSITION_DEFAULT
            )
            if special.transition_off is None:
                special.transition_off = default_trans
            if special.transition_on is None:
                special.transition_on = default_trans
        self.preset_devices(
            dimmers = not isinstance(special, DimmerParams),
            relays = isinstance(special, DimmerParams),
        )

    def execute(self) -> None:
        """Execute sequence with delay seconds between steps.
           If stop is specified, end the sequence 
           just before the nth pattern."""
        print("Enter playsequencemode.execute")
        self.player.replace_kwarg_values(self.kwargs)
        print(f"PLAYING {self.name}")
        delay_iter = (
            itertools.cycle(self.delay) 
                if isinstance(self.delay, Iterable) else
            itertools.repeat(self.delay)
        )
        start = time.time()
        for i, lights in enumerate(self.sequence(**self.kwargs)):
            if self.stop is not None and i == self.stop:
                break
            delay = next(delay_iter)

            # if pace is not None:
            if isinstance(self.special, DimmerParams):
                self.special.speed_factor = self.player.speed_factor

            if isinstance(self.special, ActionParams):
                action = partial(
                        self.special.action,
                        lights,
                )
            else:
                action = partial(
                    self.lights.set_relays,
                    lights, 
                    special=self.special,
                )
            self.schedule(
                action = action,
                due = start + (0 if delay is None else i * delay),
                name = f"PlaySequenceMode execute {i} {lights}",
            )
            if delay is None:
                print("Exiting playsequencemode.play, delay is None")
                return
        if self.repeat: 
            self.schedule(
            action = self.execute,
            due = start + (i + 1) * delay,
            name = "PlaySequenceMode continue",
        )
        print("Exiting playsequencemode.play at bottom")

