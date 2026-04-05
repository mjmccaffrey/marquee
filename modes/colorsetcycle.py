"""Marquee Lighted Sign Project - color_setcycle"""

from dataclasses import InitVar, dataclass
import logging

from devices.devices_misc import ButtonInterface
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
        self.entries = self.expand_sequence(sequence)
        self.wrap_index = lambda d: (
            self.wrap_value(
                lower=0, 
                upper=len(self.entries) - 1, 
                current=self.entry_index,
                delta=d,
            )
        )
        self.entry_index = 0
        super().__post_init__()

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
            elif name not in self.color_sets.by_set_name:
                raise ValueError(f"Color set {name} not defined.")
            else:
                cs_sequence.append(CycleEntry(name, seconds))
        return cs_sequence

    def button_action(self, button: ButtonInterface) -> int | None:
        """Respond to button being pressed.
           Return index of new mode, if any."""
        if button == self.buttons.corded_a:
            self.manual_change(+1)
        elif button == self.buttons.corded_b:
            self.manual_change(-1)
        else:
            return super().button_action(button)

    def manual_change(self, delta: int):
        """"""
        self.tasks.delete_owned_by(self)
        self.entry_index = self.wrap_index(delta)
        self.show_color_set()

    def execute(self):
        """Automatic change to next set."""
        print("EXECUTE")
        self.entry_index = self.wrap_index(self.direction)
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

