"""Marquee Lighted Sign Project - color_setcycle"""

from dataclasses import InitVar, dataclass
from itertools import cycle

from .performancemode import PerformanceMode
from .mode_misc import CycleEntry, CycleSequence


@dataclass(kw_only=True)
class ColorSetCycle(PerformanceMode):
    """Play repeating sequence of color sets."""
    sequence: InitVar[CycleSequence]  # (color_set_name, seconds)
    transition: float | None = None

    def __post_init__(self, sequence: CycleSequence) -> None:
        """Initialize."""
        self.expanded = self.expand_sequence(sequence)
        self.cycle = enumerate(cycle(self.expanded))

    def expand_sequence(
        self, 
        sequence: CycleSequence,
    ) -> list[CycleEntry]:
        """Return cycle of color sets and durations.
           Any groups specified are expanded into the member color sets."""
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

    def execute(self):
        """Change to next set. Schedule next next set."""
        index, entry = next(self.cycle)
        cs = self.color_sets.by_set_name[entry.name]
        print(
            f"Displaying color set {cs.group}.{cs.name} "
            f"({index + 1} / {len(self.expanded)}) "
            f"for {entry.seconds} seconds."
        )
        self.lights.set_channels(transition=self.transition, **cs.set_channels_kwargs)
        self.schedule(due=entry.seconds)

