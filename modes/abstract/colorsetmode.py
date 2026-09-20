"""Marquee Lighted Sign Project - colorsetmode"""

from abc import ABC, abstractmethod
from dataclasses import InitVar, dataclass
import logging
from typing_extensions import override

from schemas import CycleEntry, CycleSequence, DeviceName
from .performancemode import PerformanceMode


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
    def control_action(self, control: DeviceName) -> None:
        """If direction button pushed, change displayed color set.
           Otherwise, call parent's button handler."""
        match control:
            case DeviceName.BUTTON_CORDED_A, DeviceName.BUTTON_REAR:
                self.clicker.play()
                self.next_entry()
            case DeviceName.BUTTON_CORDED_B:
                self.clicker.play()
                self.previous_entry()
            case _:
                super().control_action(control)

    @override
    def next_entry(self) -> None:
        self._change_entry(+1)
        return super().next_entry()

    @override
    def previous_entry(self) -> None:
        self._change_entry(-1)
        return super().previous_entry()

    def _change_entry(self, delta: int) -> None:
        """"""
        self.player.tasks.delete_owned_by(self)
        self.entry_index = self.wrap_entry_index(delta)
        print(f"{self.entry_index=}")
        self.schedule()

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
                for n in self.lights.color_sets.by_group_name
            ]
        cs_sequence = []
        for name, seconds in sequence:
            if name in self.lights.color_sets.by_group_name:
                for cs in self.lights.color_sets.by_group_name[name]:
                    cs_sequence.append(CycleEntry(cs.name, seconds))
            else:
                _ = self.lights.color_sets.lookup(name)
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

