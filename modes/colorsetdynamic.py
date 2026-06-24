"""Marquee Lighted Sign Project - colorsetdynamic"""

from dataclasses import InitVar, dataclass
import logging
from typing_extensions import override

from devices.specialparams import ChannelParams
from . import (
    ColorSetMode, CycleSequence, ModeDefinition,
    LightSetBaseline, SequenceMode, chase, rotate,
)

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class ColorSetDynamic(ColorSetMode):
    """Play repeating sequence of color sets.
       If mask is specified, it will rotate.
       Otherwise, pattern will rotate."""
    sequence: InitVar[CycleSequence]  # (color_set_name, seconds)
    brightness: int | None = None
    transition: float = 0.0
    pattern: str
    mask: str | None = None
    clockwise: bool

    @override
    def __post_init__(self, sequence: CycleSequence) -> None:
        """Initialize."""
        super().__post_init__(sequence)
        self.lights.set_channels(on=True)
        self.direction = +1
        self.entry_index = -self.direction

    @override
    def execute(self):
        """Timer-invoked change to next color set."""
        self.tasks.delete_owned_by(self)
        self.entry_index = self.wrap_entry_index(self.direction)
        self.show_color_set()

    @override
    def show_color_set(self):
        """Show color set."""
        entry = self.entries[self.entry_index]
        cs = self.color_sets.by_set_name[entry.name]
        log.info(
            f"Chasing color set {cs.group}.{cs.name} "
            f"for {entry.seconds} seconds "
            f"({self.entry_index + 1} / {len(self.entries)})."
        )
        self.schedule(due=entry.seconds)
        kwargs=dict(
            baseline=LightSetBaseline(on=False),
            color_set_name=entry.name,
            delay=0.35, 
            special=ChannelParams(),
        )
        sequence_kwargs=dict(
            clockwise=self.clockwise,
            pattern=self.pattern,
        )
        if self.mask is None:
            kwargs |= dict(sequence=rotate)
        else:
            kwargs |= dict(sequence=chase)
            sequence_kwargs |= dict(mask=self.mask)
        mode = self.create_mode_instance(
            mode_definition=ModeDefinition(
                name='cs_rotate',
                cls=SequenceMode,
            ),
            parent=self,
        )
        self.schedule(mode.execute)

