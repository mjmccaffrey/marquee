"""Marquee Lighted Sign Project - modes"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass
import time
from typing import Any

from buttons import Button
from dimmers import RelayOverride, TRANSITION_DEFAULT
from sequence_defs import seq_rotate_build_flip
from signs import ALL_HIGH, ALL_OFF, ALL_ON

@dataclass
class ModeConstructor:
    name: str
    mode_class: type["Mode"]
    kwargs: dict[str, Any]

class Mode(ABC):
    """Base for all Playing modes and the Select mode."""

    def __init__(
        self,
        player: Any,  # Player
        name: str,
        preset_dimmers: bool = False,
        preset_relays: bool = False,
    ):
        """"""
        self.player = player
        self.name = name
        if preset_dimmers:
            print("presetting DIMMERS")
            self.player.sign.set_dimmers(ALL_HIGH, force_update=True)
        if preset_relays:
            print("presetting RELAYS")
            self.player.sign.set_lights(ALL_ON)

    def mode_index(self, current: int, delta: int) -> int:
        """Return a new mode index, wrapping in both directions."""
        lower, upper = 1, len(self.player.modes) - 1
        value = current + delta % (upper - lower + 1)
        if (dif := value - upper) > 0:
            value = lower + dif - 1
        elif (dif := value - lower) < 0:
            value = upper + dif + 1
        return value

    @abstractmethod
    def button_action(self, button: Button):
        """Respond to the button press."""

    @abstractmethod
    def execute(self):
        """Play the mode."""
 
class SelectMode(Mode):
    """Supports the select mode."""

    def __init__(
        self,
        player: Any,  # Player
        name: str,
        #
        previous_mode: int,
    ):
        """"""
        super().__init__(player, name, preset_dimmers=True)
        self.desired_mode = previous_mode
        self.previous_desired_mode = -1

    def button_action(self, button: Button):
        """Respond to the button press."""
        assert self.desired_mode is not None
        match button.name:
            case 'body_back' | 'remote_a' | 'remote_d':
                self.desired_mode = self.mode_index(self.desired_mode, +1)
            case 'remote_b':
                self.desired_mode = self.mode_index(self.desired_mode, -1)
            case 'remote_c':
                # self.desired_mode = 2  # ALL_OFF
                return 222  # Quick change to mode ALL_OFF
            case _:
                raise Exception
        return None

    def execute(self):
        """User presses the button to select 
           the next mode to execute."""
        super().execute()
        new_mode = None
        if self.desired_mode != self.previous_desired_mode:
            # Not last pass.
            # Show user what desired mode number is currently selected.
            self.player.sign.set_lights(ALL_OFF)
            time.sleep(0.5)
            self.player.play_sequence(
                seq_rotate_build_flip(count=self.desired_mode),
                pace=0.20, post_delay=4.0,
            )
            self.previous_desired_mode = self.desired_mode
        else:
            # Last pass.
            # Time elapsed without a button being pressed.
            # Play the selected mode.
            new_mode = self.desired_mode
        return new_mode

class PlayMode(Mode):
    """Base for custom modes."""

    def __init__(
        self,
        player: Any,  # Player
        name: str,
        preset_dimmers: bool = False,
        preset_relays: bool = False,
    ):
        """"""
        super().__init__(player, name, preset_dimmers, preset_relays)
        self.direction = +1

    def button_action(self, button: Button):
        """Respond to the button press."""
        new_mode = None
        match button.name:
            case 'remote_a' | 'body_back':
                new_mode = 0
            case 'remote_c':
                self.player.sign.click()
                self.direction *= -1
            case 'remote_b':
                self.player.sign.click()
                new_mode = self.mode_index(self.player.current_mode, -1)
            case 'remote_d':
                self.player.sign.click()
                new_mode = self.mode_index(self.player.current_mode, +1)
                print("Button Action: ", new_mode)
            case _:
                raise Exception
        return new_mode

class PlaySequenceMode(PlayMode):
    """Supports all sequence-based modes."""

    def __init__(
        self,
        player: Any,  # Player
        name: str,
        #
        sequence: Callable,
        pace: tuple[float, ...] | float | None = None,
        override: RelayOverride | None = None,
        **kwargs,
    ):
        """"""
        self.sequence = sequence
        self.pace = pace
        self.override = override
        self.kwargs = kwargs

        if override is not None:
            default_trans = (
                pace if isinstance(pace, float) else
                TRANSITION_DEFAULT
            )
            if override.transition_off is None:
                override.transition_off = default_trans
            if override.transition_on is None:
                override.transition_on = default_trans

        super().__init__(
            player, 
            name, 
            preset_dimmers=(override is None),
            preset_relays=(override is not None),
        )

    def play_sequence(self):
        self.player.replace_kwarg_values(self.kwargs)
        self.player.play_sequence(
            sequence=self.sequence(**self.kwargs),
            pace=self.pace,
            override=self.override,
        )

    def execute(self):
        """Play the mode."""
        super().execute()
        while True:
            self.play_sequence()
