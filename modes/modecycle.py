"""Marquee Lighted Sign Project - modecycle"""

from dataclasses import dataclass
from itertools import cycle
import logging

from devices.devices_misc import ButtonInterface
from .backgroundmode import BackgroundMode
from .mode_misc import CycleEntry, CycleSequence

log = logging.getLogger(__name__)


@dataclass(kw_only=True)
class ModeCycle(BackgroundMode):
    """Play repeating sequence of foreground modes."""
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

    def execute(self):
        """Change to next mode in sequence. Schedule next next mode."""
        new = next(self.mode_cycle)
        print(
            f"Next mode in sequence is {new.name} for {new.seconds} seconds."
        )
        self.schedule(due=new.seconds)
        self.change_mode(new.index)
    
    def button_action(self, button: ButtonInterface) -> None:
        """Close the instance in response to any button press."""
        # self.player.delete_mode_instance(bg_index=self.index)
        # !!!!!!!!!!!!!!1
