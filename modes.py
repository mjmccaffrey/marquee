"""Marquee Lighted Sign Project - modes"""

from abc import ABC
from collections.abc import Callable
import time

from basemode import BaseMode
from buttons import Button
from configuration import ALL_HIGH, ALL_OFF, ALL_ON
from dataclasses import dataclass
from definitions import (
    DimmerParams, MirrorParams, SpecialParams,
)
from dimmers import TRANSITION_DEFAULT
from music import set_player
from player_interface import PlayerInterface
from sequences import rotate_build_flip

@dataclass
class Mode(BaseMode, ABC):
    """Base for all Playing modes and the Select mode."""
    player: PlayerInterface
    special: SpecialParams | None = None

    def preset_devices(self, dimmers: bool = False, relays: bool = False):
        """Preset the dimmers and relays as specified."""
        if isinstance(self.special, MirrorParams):
            self.special.func = self.player.drums.mirror
        if dimmers:
            print("Presetting DIMMERS")
            self.player.lights.set_dimmers(ALL_HIGH, force_update=True)
        if relays:
            print("Presetting RELAYS")
            self.player.lights.set_relays(ALL_ON)

    def mode_index(self, current: int, delta: int) -> int:
        """Return a new mode index, wrapping index in both directions."""
        lower, upper = 1, len(self.player.modes) - 1
        value = current + delta % (upper - lower + 1)
        if (dif := value - upper) > 0:
            value = lower + dif - 1
        elif (dif := value - lower) < 0:
            value = upper + dif + 1
        return value

@dataclass(kw_only=True)
class SelectMode(Mode):
    """Supports the select mode."""
    previous_mode: int

    def __post_init__(self):
        """Initialize."""
        self.preset_devices(dimmers=True)
        self.desired_mode = self.previous_mode
        self.previous_desired_mode = -1

    def button_action(self, button: Button):
        """Respond to the button press."""
        assert self.desired_mode is not None
        b = self.player.buttons
        match button:
            case b.body_back | b.remote_a | b.remote_d:
                self.desired_mode = self.mode_index(self.desired_mode, +1)
            case b.remote_b:
                self.desired_mode = self.mode_index(self.desired_mode, -1)
            case b.remote_c:
                return 222  # Quick change
            case _:
                raise ValueError("Unrecognized button.")
        return None

    def execute(self):
        """User presses the button to select 
           the next mode to execute."""
        new_mode = None
        if self.desired_mode != self.previous_desired_mode:
            # Not last pass.
            # Show user what desired mode number is currently selected.
            self.player.lights.set_relays(ALL_OFF, special=self.special)
            time.sleep(0.5)
            self.player.play_sequence(
                rotate_build_flip(count=self.desired_mode),
                pace=0.20, post_delay=4.0,
                special=self.special,
            )
            self.previous_desired_mode = self.desired_mode
        else:
            # Last pass.
            # Time elapsed without a button being pressed.
            # Play the selected mode.
            new_mode = self.desired_mode
        return new_mode

@dataclass
class PlayMode(Mode):
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
            case b.remote_a:  # | b.body_back:
                if self.player.auto_mode is not None:
                    print("Exiting auto mode.")
                    self.player.auto_mode = None
                new_mode = 0
            case b.remote_c:
                self.player.click()
                new_mode = self.player.mode_ids['section_1']
            case b.remote_b:
                self.player.click()
                if self.player.auto_mode is None:
                    new_mode = self.mode_index(self.player.current_mode, -1)
            case b.remote_d | b.body_back:
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
    """Mode for playing music."""

    def __post_init__(self):
        """Initialize."""
        # self.preset_devices(
        #     dimmers = not isinstance(self.special, DimmerParams),
        #     relays = isinstance(self.special, DimmerParams),
        # )
        set_player(self.player)
