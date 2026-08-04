"""Marquee Lighted Sign Project - colorsetstatic"""

from dataclasses import InitVar, dataclass
import logging
from typing_extensions import override

from light_defs import EXTRA_CUPOLA
from . import ColorSetMode, CycleSequence

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class ColorSetStatic(ColorSetMode):
    """Play repeating sequence of color sets."""
    sequence: InitVar[CycleSequence]
    brightness: int | None = None
    transition: float = 0.0

    @override
    def __post_init__(self, sequence: CycleSequence) -> None:
        """Initialize."""
        super().__post_init__(sequence)
        self.lights = self.combined
        self.lights.set_channels(on=True, force=True)
        self.direction = +1
        self.entry_index = -self.direction

    @override
    def execute(self):
        """Timer-invoked change to next color set."""
        self.entry_index = self.wrap_entry_index(self.direction)
        self.show_color_set()

    @override
    def show_color_set(self):
        """Show color set. Schedule next set."""
        entry = self.entries[self.entry_index]
        cs = self.color_sets.by_set_name[entry.name]
        log.info(
            f"Displaying color set {cs.group}.{cs.name} "
            f"for {entry.seconds} seconds "
            f"({self.entry_index + 1} / {len(self.entries)})."
        )
        kwargs = cs.set_channels_kwargs(self.lights.count)
        if self.brightness is not None:
            kwargs |= dict(brightness=self.brightness)
        self.lights.set_channels(
            transition=self.transition, 
            **kwargs,  # type: ignore
        )
        if entry.seconds is not None:
            self.schedule(due=entry.seconds)

