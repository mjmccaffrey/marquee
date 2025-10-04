"""Marquee Lighted Sign Project - playmode"""

from dataclasses import dataclass

from .background_modes import SequenceBGMode
from .foregroundmode import ForegroundMode
from button import Button
from dimmers import TRANSITION_DEFAULT
from modes.mode_misc import ModeIndex
from player import Player


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

