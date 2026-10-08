"""Marquee Lighted Sign Project - modecycle"""

from dataclasses import dataclass
from itertools import cycle
import logging
import pygame
from typing_extensions import override

from ..abstract.mode import Mode
from schemas import ControlName, CycleEntry, CycleSequence


log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class ModeCycle(Mode):
    """Execute repeating sequence of modes."""
    background: bool = True
    pause_before_each: bool = False
    sequence: CycleSequence

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()
        self.paused = False
        self.create_mode_sequence()
        self.mode_cycle = cycle(self.mode_sequence)

    def create_mode_sequence(self) -> None:
        """Create mode sequence."""
        self.mode_sequence = [
            CycleEntry(
                name,
                seconds,
                None 
                    if name is None else
                self.lookup_mode_index(name),
            )
            for name, seconds in self.sequence
        ]

    @override
    def execute(self):
        """Pause or unpause and / or change to next mode in sequence."""
        if self.pause_before_each:
            if self.paused:
                print("Unpausing")
                self._execute_next_mode()
            else:
                print("Pausing")
                self._delete_foreground_mode()
            self.paused = not self.paused
        else:
            self._execute_next_mode()

    @override
    def control_action(self, control: ControlName) -> bool:
        """Respond to control action and return True."""
        if control == ControlName.BUTTON_CORDED_A:
            self.player.tasks.delete_owned_by(self)
            self.schedule()
            return True
        return False

    def _delete_foreground_mode(self):
        """Delete active foreground mode, if any."""
        modes = self.player.active_modes.values()
        fg_mode = [m for m in modes if not m.background]
        if fg_mode:
            self.player.delete_active_mode(fg_mode[0].index)

    def _execute_next_mode(self):
        """"""
        new = next(self.mode_cycle)
        log.info(
            f"Next mode in sequence is {new.name} for {new.seconds} seconds."
        )
        if new.seconds is not None:
            self.schedule(due=new.seconds)
        if new.index is not None:
            self.change_mode(new.index)

