"""Marquee Lighted Sign Project - play_modes"""

from collections.abc import Callable
from dataclasses import dataclass

from .background_modes import SequenceBGMode
from .foregroundmode import ForegroundMode
from button import Button
from configuration import ModeIndex
from dimmers import TRANSITION_DEFAULT
from music import set_player
from player import Player
from specialparams import DimmerParams, SpecialParams


@dataclass
class PlayMode(ForegroundMode):
    """Base for custom modes."""
    player: Player

    def __post_init__(self) -> None:
        """Initialize."""
        self.preset_devices()
        self.direction = +1

    def button_action(self, button: Button) -> int | None:
        """Respond to the button press."""

        # If in sequence mode, exit it.
        index = self.player.find_bg_mode(SequenceBGMode)
        if index is not None:
            self.player.terminate_bg_mode(index)
            return ModeIndex.DEFAULT

        assert self.player.current_mode is not None
        new_mode = None
        b = self.player.buttons
        match button:
            case b.remote_a | b.body_back:
                new_mode = ModeIndex.SELECT_MODE
            case b.remote_c:
                self.player.click()
                new_mode = self.player.mode_ids['section_1']
            case b.remote_b:
                self.player.click()
                new_mode = self.mode_index(self.player.current_mode, -1)
            case b.remote_d:
                self.player.click()
                new_mode = self.mode_index(self.player.current_mode, +1)
            case _:
                raise ValueError("Unrecognized button.")
        return new_mode


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


@dataclass
class PlayMusicMode(PlayMode):
    """Base for playing music."""

    def __post_init__(self) -> None:
        """Initialize."""
        # self.preset_devices(
        #     dimmers = not isinstance(self.special, DimmerParams),
        #     relays = isinstance(self.special, DimmerParams),
        # )
        set_player(self.player)

