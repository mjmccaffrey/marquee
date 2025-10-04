"""Marquee Lighted Sign Project - playsequencemode"""

from collections.abc import Callable
from itertools import cycle, repeat
import time
from typing import Iterable

from .playmode import PlayMode
from dimmers import TRANSITION_DEFAULT
from player import Player
from specialparams import ActionParams, DimmerParams, SpecialParams

class PlaySequenceMode(PlayMode):
    """Supports all sequence-based modes."""
    def __init__(
        self,
        player: Player,
        name: str,
        sequence: Callable[[], Iterable],
        pace: tuple[float, ...] | float | None = None,
        stop: int | None = None,
        special: SpecialParams | None = None,
        **kwargs,
    ) -> None:
        """Initialize."""
        super().__init__(player, name, special)
        self.sequence = sequence
        self.pace = pace
        self.stop = stop
        self.kwargs = kwargs
        if isinstance(special, DimmerParams):
            default_trans = (
                pace if isinstance(pace, float) else
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

    def play(self) -> None:
        """Execute sequence with pace seconds between steps.
           If stop is specified, end the sequence 
           just before the nth pattern."""
        pace_iter = (
            cycle(self.pace) 
                if isinstance(self.pace, Iterable) else
            repeat(self.pace)
        )
        for i, lights in enumerate(self.sequence(**self.kwargs)):
            if self.stop is not None and i == self.stop:
                break
            p = next(pace_iter)
            before = time.time()
            if p is not None:
                if isinstance(self.special, DimmerParams):
                    self.special.speed_factor = self.player.speed_factor
            if isinstance(self.special, ActionParams):
                self.special.action(lights)
            else:
                self.player.lights.set_relays(lights, special=self.special)
            after = time.time()
            self.player.wait(p, after - before)

    def execute(self) -> None:
        """Update any kwarg special parameters. Play sequence. Repeat."""
        while True:
            self.player.replace_kwarg_values(self.kwargs)
            self.play()

