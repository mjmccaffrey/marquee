"""Marquee Lighted Sign Project - play_modes"""

from collections.abc import Callable

from .basemode import BaseMode
from button import Button
from dataclasses import dataclass
from dimmers import TRANSITION_DEFAULT
from music import set_player
from playerinterface import PlayerInterface
from specialparams import DimmerParams, SpecialParams

@dataclass
class PlayMode(BaseMode):
    """Base for custom modes."""

    def __post_init__(self):
        """Initialize."""
        self.preset_devices()
        self.direction = +1

    def button_action(self, button: Button):
        """Respond to the button press."""
        new_mode = None
        b = self.player.buttons
        match button:
            case b.remote_a | b.body_back:
                if self.player.auto_mode is not None:
                    self.player.auto_mode.exit()
                new_mode = self.player.mode_ids['select_mode']
            case b.remote_c:
                self.player.click()
                if self.player.auto_mode is not None:
                    self.player.auto_mode.exit()
                new_mode = self.player.mode_ids['section_1']
            case b.remote_b:
                self.player.click()
                if self.player.auto_mode is None:
                    new_mode = self.mode_index(self.player.current_mode, -1)
                else:
                    print("Back button ignored in auto mode.")
            case b.remote_d:
                self.player.click()
                if self.player.auto_mode is None:
                    new_mode = self.mode_index(self.player.current_mode, +1)
                else:
                    new_mode = self.player.auto_mode.next_mode()
            case _:
                raise ValueError("Unrecognized button.")
        return new_mode

class PlaySequenceMode(PlayMode):
    """Supports all sequence-based modes."""
    def __init__(
        self,
        player: PlayerInterface,
        name: str,
        sequence: Callable,
        pace: tuple[float, ...] | float | None = None,
        stop: int | None = None,
        post_delay: float | None = 0.0,
        special: SpecialParams | None = None,
        **kwargs,
    ):
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

    def play_sequence_once(self):
        """Play established sequence once."""
        self.player.replace_kwarg_values(self.kwargs)
        self.player.play_sequence(
            sequence=self.sequence(**self.kwargs),
            pace=self.pace,
            stop=self.stop,
            post_delay=self.post_delay,
            special=self.special,
        )

    def execute(self):
        """Play the mode."""
        while True:
            self.play_sequence_once()

@dataclass
class PlayMusicMode(PlayMode):
    """Base for playing music."""

    def __post_init__(self):
        """Initialize."""
        # self.preset_devices(
        #     dimmers = not isinstance(self.special, DimmerParams),
        #     relays = isinstance(self.special, DimmerParams),
        # )
        set_player(self.player)
