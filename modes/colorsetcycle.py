"""Marquee Lighted Sign Project - color_setcycle"""

from dataclasses import InitVar, dataclass
import logging
from typing import override

from devices.devices_misc import ButtonName
from .performancemode import PerformanceMode
from .modes_misc import CycleEntry, CycleSequence

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class ColorSetCycle(PerformanceMode):
    """Play repeating sequence of color sets."""
    sequence: InitVar[CycleSequence]  # (color_set_name, seconds)
    transition: float | None = None

    def __post_init__(self, sequence: CycleSequence) -> None:
        """Initialize."""
        self.lights.set_channels(on=True)
        self.direction = +1
        self.entries = self.expand_sequence(sequence)
        self.entry_index = -self.direction

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

    @override
    def button_action(self, button: ButtonName) -> int | None:
        """If direction button pushed, change displayed color set.
           Otherwise, call parent's button handler."""
        direction_buttons = {
            ButtonName.CORDED_A: +1,
            ButtonName.CORDED_B: -1,
        }
        if button in direction_buttons:
            self.clicker.click()
            self.tasks.delete_owned_by(self)
            self.entry_index = self.wrap_entry_index(direction_buttons[button])
            self.show_color_set()
        else:
            return super().button_action(button)

    @override
    def execute(self):
        """Timer-invoked change to next color set."""
        self.entry_index = self.wrap_entry_index(self.direction)
        self.show_color_set()

    def show_color_set(self):
        """Show color set. Schedule next set."""
        entry = self.entries[self.entry_index]
        cs = self.color_sets.by_set_name[entry.name]
        log.info(
            f"Displaying color set {cs.group}.{cs.name} "
            f"for {entry.seconds} seconds "
            f"({self.entry_index + 1} / {len(self.entries)})."
        )
        self.lights.set_channels(transition=self.transition, **cs.set_channels_kwargs)
        self.schedule(due=entry.seconds)

    def wrap_entry_index(self, delta: int):
        """"""
        return self.wrap_value(
            lower=0, 
            upper=len(self.entries) - 1, 
            current=self.entry_index,
            delta=delta,
        )

