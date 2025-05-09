"""Marquee Lighted Sign Project - modes"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
import time
from typing import Any

from buttons import Button
from definitions import (
    ALL_HIGH, ALL_OFF, ALL_ON,
    ActionParams, DimmerParams, SpecialParams,
)
from dimmers import TRANSITION_DEFAULT
from music import Environment, set_environment
from sequence_defs import rotate_build_flip

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

    @staticmethod
    def wrap_value[T: (float, int)](
        lower: T, upper: T, current: T, delta: T,
    ):
        """"""
        value = current + delta % (upper - lower + 1)
        if (dif := value - upper) > 0:
            value = lower + dif - 1
        elif (dif := value - lower) < 0:
            value = upper + dif + 1
        return value

    def mode_index(self, current: int, delta: int) -> int:
        """Return a new mode index, wrapping index in both directions."""
        return self.wrap_value(1, max(self.player.modes), current, delta)

    @abstractmethod
    def button_action(self, button: Button):
        """Respond to the button press."""

    @abstractmethod
    def execute(self):
        """Play the mode."""
 
class SelectMode[T: (float, int)](Mode):
    """Supports the selection modes."""

    def __init__(
        self,
        player: Any,  # Player
        name: str,
        lower: T,
        upper: T,
        step: T,
        scale: T,
        previous: T,
        special_mode: int,
    ):
        """"""
        super().__init__(player, name, preset_dimmers=True)
        self.lower = lower
        self.upper = upper
        self.step = step
        self.scale = scale
        self.desired: T = previous
        self.previous_desired = None
        self.special_mode = special_mode

    def update_desired(self, delta: T) -> T:
        return self.wrap_value(self.lower, self.upper, self.desired, delta)

    def button_action(self, button: Button):
        """Respond to the button press."""
        match button.name:
            case 'body_back' | 'remote_a' | 'remote_d':
                self.desired = self.update_desired(+self.step)
            case 'remote_b':
                self.desired = self.update_desired(-self.step)
            case 'remote_c':
                return self.special_mode
            case _:
                raise Exception
        return None

    def execute(self):
        """Indicate current selection, 
           give user chance to change it."""
        if self.desired == self.special_mode:
            return self.special_mode
        if self.desired != self.previous_desired:
            # Not last pass.
            # Show user what desired mode number is currently selected.
            self.player.sign.set_lights(ALL_OFF)
            time.sleep(0.5)
            self.player.play_sequence(
                rotate_build_flip(count = int(self.desired * self.scale)),
                pace=0.20, post_delay=4.0,
            )
            self.previous_desired = self.desired
            result = None
        else:
            # Last pass.
            # Time elapsed without a button being pressed.
            # Implement the selection.
            result = self.desired
        return result

class BrightnessSelectMode(SelectMode):
    """Allows user to select maximum brightness."""

    def __init__(
        self,
        player: Any,  # Player
        name: str,
        previous_mode: int,
    ):
        """"""
        super().__init__(
            player=player, 
            name=name, 
            lower=0, upper=1, 
            step=0.1, scale=10,
            previous=player.sign.brightness_factor,
            special_mode=222,
        )
        self.previous_mode = previous_mode

    def execute(self):
        """Indicate current brightness selection, 
           give user chance to change it."""
        self.player.sign.brightness_factor = self.desired
        result = super().execute()
        if result is not None and result != self.special_mode:
            result = self.previous_mode
        return result

class ModeSelectMode(SelectMode):
    """Allows user to select mode."""

    def __init__(
        self,
        player: Any,  # Player
        name: str,
        previous_mode: int,
    ):
        """"""
        super().__init__(
            player=player, name=name, 
            lower=1, upper=max(player.modes), 
            step=1, scale=1, 
            previous=previous_mode, 
            special_mode=-1,
        )

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
                raise ValueError("Unrecognized button name.")
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
        stop: int | None = None,
        special: SpecialParams | None = None,
        **kwargs,
    ):
        """"""
        self.sequence = sequence
        self.pace = pace
        self.stop = stop
        self.special = special
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
        super().__init__(
            player, 
            name, 
            preset_dimmers=(special is None),
            preset_relays=(special is not None),
        )

    def play_sequence_once(self):
        """Play established sequence once."""
        self.player.replace_kwarg_values(self.kwargs)
        self.player.play_sequence(
            sequence=self.sequence(**self.kwargs),
            pace=self.pace,
            stop=self.stop,
            special=self.special,
        )

    def execute(self):
        """Play the mode."""
        super().execute()
        while True:
            self.play_sequence_once()

class PlayMusicMode(PlayMode):
    """Mode for playing music."""
    def __init__(
        self,
        player: Any,  # Player
        name: str,
    ):
        super().__init__(player, name, preset_dimmers=True, preset_relays=True)
        set_environment(
            Environment(
                bell_set=self.player.sign.bell_set,
                drum_set=self.player.sign.drum_set,
                dimmer=self.dimmer,
                light=self.light,
                wait=self.player.wait,
            )
        )

    def dimmer_sequence(self, brightness: int, transition: float) -> Callable:
        """Return callable to effect state of specified dimmers."""
        def func(lights: list[int]):
            self.player.sign.execute_dimmer_commands([
                (   self.player.sign.dimmer_channels[l], 
                    brightness, 
                    transition,
                )
                for l in lights
            ])
        return func

    def dimmer(self, pattern: str) -> Callable:
        """Return callable to effect dimmer pattern."""
        return lambda: self.player.sign.set_dimmers(pattern)

    def light(
        self, 
        pattern: Any,
        special: SpecialParams | None = None,
    ) -> Callable:
        """Return callable to effect light pattern."""
        if isinstance(special, DimmerParams):
            if special.transition_off is None:
                special.transition_off = TRANSITION_DEFAULT
            if special.transition_on is None:
                special.transition_on = TRANSITION_DEFAULT
        if isinstance(special, ActionParams):
            result = lambda: special.action(pattern)
        else:
            result = lambda: self.player.sign.set_lights(
                light_pattern=pattern,
                special=special,
            )
        return result
