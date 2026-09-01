"""Marquee Lighted Sign Project - modecycle"""

from dataclasses import dataclass
from itertools import cycle
import logging
import pygame
from typing_extensions import override

from devices.device_schemas import ControlName
from ..abstract.mode import Mode
from .mode_schemas import CycleEntry, CycleSequence

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class ModeCycle(Mode):
    """Execute repeating sequence of modes."""
    background: bool = True
    sequence: CycleSequence

    def __post_init__(self) -> None:
        """Initialize."""
        super().__post_init__()
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
        new = next(self.mode_cycle)
        log.info(
            f"Next mode in sequence is {new.name} for {new.seconds} seconds."
        )
        if new.seconds is not None:
            self.schedule(due=new.seconds)
        self.change_mode(new.index)

    @override
    def control_action(self, control: ControlName) -> None:
        """Switch to next mode.
           But first, delete the scheduled task 
           for the timed switch."""
        if control == ControlName.CORDED_A:
            self.player.tasks.delete_owned_by(self)
            self.schedule()

