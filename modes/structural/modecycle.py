"""Marquee Lighted Sign Project - modecycle"""

from dataclasses import dataclass
from itertools import cycle
import logging
import pygame
from typing_extensions import override

from devices.devices_misc import ButtonName
from ..abstract.mode import Mode
from .modes_misc import CycleEntry, CycleSequence

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class ModeCycle(Mode):
    """Execute repeating sequence of modes."""
    background: bool = True
    sequence: CycleSequence  # (mode_name, seconds)

    def __post_init__(self) -> None:
        """Initialize."""
        self.create_mode_sequence()
        self.mode_cycle = cycle(self.mode_sequence)

    def create_mode_sequence(self) -> None:
        """Create mode sequence."""
        self.mode_sequence = [
            CycleEntry(
                name,
                seconds,
                self.lookup_mode_index(name),
            )
            for name, seconds in self.sequence
        ]

    @override
    def execute(self):
        """Change to next mode in sequence. Schedule next next mode."""
        pygame.mixer.music.stop()  # !!! Move this to player?
        new = next(self.mode_cycle)
        log.info(
            f"Next mode in sequence is {new.name} for {new.seconds} seconds."
        )
        self.schedule(due=new.seconds)
        self.change_mode(new.index)
    
    @override
    def button_action(self, button: ButtonName) -> None:
        """Switch to next mode.
           But first, delete the scheduled task 
           for the timed switch."""
        if button == ButtonName.CORDED_A:
            self.tasks.delete_owned_by(self)
            self.schedule()

