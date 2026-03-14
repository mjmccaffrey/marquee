"""Marquee Lighted Sign Project - color_setcycle"""

from collections.abc import Iterator
from dataclasses import InitVar, dataclass
from itertools import cycle

from .performancemode import PerformanceMode
from .mode_misc import CycleEntry


@dataclass(kw_only=True)
class ColorSetCycle(PerformanceMode):
    """Play repeating sequence of color sets."""
    sequence: InitVar[list[tuple[str, int]]]  # (color_set_name, seconds)
    transition: float | None

    def __post_init__(self, sequence: list[tuple[str, int]]) -> None:
        """Initialize."""
        self.cycle = self.create_sequence_cycle(sequence)
        self.on_deck = next(self.cycle)

    def create_sequence_cycle(self, sequence: list[tuple[str, int]]) -> Iterator:
        """Return cycle of color sets and durations.
           Any groups specified are expanded into the member color sets."""
        cs_sequence = []
        for name, seconds in sequence:
            if name in self.color_set_groups:
                cs_in_group = (
                    cs for cs in self.color_sets.values() 
                    if cs.group == name
                )
                for cs in cs_in_group:
                    cs_sequence.append(CycleEntry(cs.name, seconds))
            elif name not in self.color_sets:
                raise ValueError(f"Color set {name} not defined.")
            else:
                cs_sequence.append(CycleEntry(name, seconds))
        return cycle(cs_sequence)

    def execute(self):
        """Change to next set. Schedule next next set."""
        cs = self.color_sets[self.on_deck.name]
        color, brightness = cs.convert_for_set_channels()
        self.lights.set_channels(brightness=brightness, color=color)
        print(
            f"Next color set in sequence is "
            f"{self.on_deck.name} for "
            f"{self.on_deck.seconds} seconds."
        )
        self.schedule(due=self.on_deck.seconds)
        self.on_deck = next(self.cycle)

