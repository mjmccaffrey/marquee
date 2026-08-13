"""Marquee Lighted Sign Project - colorsetmode"""

from abc import ABC, abstractmethod
from dataclasses import InitVar, dataclass
import logging
from typing_extensions import override

from devices.devices_misc import ControlName
from .performancemode import PerformanceMode
from ..structural.modes_misc import CycleEntry, CycleSequence

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class ColorSetMode(PerformanceMode, ABC):
    """Play repeating sequence of color sets."""
    sequence: InitVar[CycleSequence]  # (color_set_name, seconds)
    brightness: int | None = None
    transition: float = 0.0

    def __post_init__(self, sequence: CycleSequence) -> None:
        """Initialize."""
        super().__post_init__()
        self.entry_index: int
        self.entries = self.expand_sequence(sequence)

    @abstractmethod
    def show_color_set(self):
        """Show color set. Schedule next set."""

    @override
    def control_action(self, control: ControlName) -> int | None:
        """If direction button pushed, change displayed color set.
           Otherwise, call parent's button handler."""
        direction_buttons = {
            ControlName.CORDED_A: +1,
            ControlName.CORDED_B: -1,
        }
        if control in direction_buttons:
            self.clicker.click()
            self.tasks.delete_owned_by(self)
            self.entry_index = self.wrap_entry_index(direction_buttons[control])
            self.schedule(action=self.show_color_set)
        else:
            return super().control_action(control)

    def expand_sequence(
        self, 
        sequence: CycleSequence,
    ) -> list[CycleEntry]:
        """Return expanded sequence of color set names and durations.
           Any group names specified are expanded into the member color sets.
           An initial entry with the pseudo group name "ALL" is expanded into
           all the groups and hence all the color sets."""
        assert sequence
        name, seconds = sequence[0]
        if name == 'ALL':
            sequence = [
                (n, seconds)
                for n in self.color_sets.by_group_name
            ]
        cs_sequence = []
        for name, seconds in sequence:
            if name in self.color_sets.by_group_name:
                for cs in self.color_sets.by_group_name[name]:
                    cs_sequence.append(CycleEntry(cs.name, seconds))
            else:
                _ = self.color_sets.lookup(name)
                cs_sequence.append(CycleEntry(name, seconds))
        return cs_sequence

    def wrap_entry_index(self, delta: int):
        """Return current index + delta, wrapped around if needed."""
        return self.wrap_value(
            lower=0, 
            upper=len(self.entries) - 1, 
            current=self.entry_index,
            delta=delta,
        )

