"""Marquee Lighted Sign Project - playsequencemode"""

from collections.abc import Callable

from .playmode import PlayMode
from dimmers import TRANSITION_DEFAULT
from player import Player
from specialparams import DimmerParams, SpecialParams

class PlaySequenceMode(PlayMode):
    """Supports all sequence-based modes."""
    def __init__(
        self,
        player: Player,
        name: str,
        sequence: Callable,
        pace: tuple[float, ...] | float | None = None,
        stop: int | None = None,
        post_delay: float | None = 0.0,
        special: SpecialParams | None = None,
        **kwargs,
    ) -> None:
        """Initialize."""
        super().__init__(player, name, special)
        self.sequence = sequence
        self.pace = pace
        self.stop = stop
        self.post_delay = post_delay
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

    def play_sequence_once(self) -> None:
        """Play established sequence once."""
        self.player.replace_kwarg_values(self.kwargs)
        self.player.play_sequence(
            sequence=self.sequence(**self.kwargs),
            pace=self.pace,
            stop=self.stop,
            post_delay=self.post_delay,
            special=self.special,
        )

    def execute(self) -> None:
        """Play the mode."""
        while True:
            self.play_sequence_once()

