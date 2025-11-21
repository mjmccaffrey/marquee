"""Marquee Lighted Sign Project - playsequencemode"""

from collections.abc import Callable
from functools import partial
import itertools
from typing import Iterable

from .foregroundmode import ForegroundMode
from .playmode import PlayMode
from player import Player
from specialparams import ActionParams, ChannelParams, SpecialParams

class PlaySequenceMode(PlayMode):
    """Supports all sequence-based modes."""
    def __init__(
        self,
        player: Player,
        index: int,
        name: str,
        sequence: Callable[[], Iterable],
        pre_delay: float = 0.0,
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
        self.pre_delay = pre_delay
        self.delay = delay
        self.stop = stop
        self.repeat = repeat
        self.kwargs = kwargs
        if isinstance(special, ChannelParams):
            default_trans = (
                delay if isinstance(delay, float) else
                self.lights.trans_def
            )
            if special.trans_off is None:
                special.trans_off = default_trans
            if special.trans_on is None:
                special.trans_on = default_trans
        self.preset_devices(
            channels = not isinstance(special, ChannelParams),
            relays = isinstance(special, ChannelParams),
        )

    def execute(self, pre_delay_done=False) -> None:
        """Execute sequence with delay seconds between steps.
           If stop is specified, end the sequence 
           just before the nth pattern."""
        if self.pre_delay and not pre_delay_done:
            self.schedule(
                action = partial(self.execute, pre_delay_done=True),
                due = self.pre_delay,
                name = "PlaySequenceMode execute after pre_delay",
            )
            return
        self.player.replace_kwarg_values(self.kwargs)
        delay_iter = (
            itertools.cycle(self.delay) 
                if isinstance(self.delay, Iterable) else
            itertools.repeat(self.delay)
        )
        for i, lights in enumerate(self.sequence(**self.kwargs)):
            if self.stop is not None and i == self.stop:
                break
            delay = next(delay_iter)

            # if pace is not None: ????
            if isinstance(self.special, ChannelParams):
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
                due = 0 if delay is None else i * delay,
                name = f"PlaySequenceMode execute {i} {lights}",
            )
            if delay is None:
                print("Exiting playsequencemode.play, delay is None")
                return
        if self.repeat: 
            self.schedule(
            action = self.execute,
            due = (i + 1) * delay,
            name = "PlaySequenceMode continue",
        )
        print("Exiting playsequencemode.play at bottom")

