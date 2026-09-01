"""Marquee Lighted Sign Project - colorsetdynamic"""

from dataclasses import InitVar, dataclass
import logging
from typing import Any, cast
from typing_extensions import override

from devices.specialparams import ChannelParams
from . import (
    BaseMode, ColorSetMode, CycleSequence, ModeDefinition,
    LightSetBaseline, SequenceMode, chase, rotate,
)

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class ColorSetDynamic(ColorSetMode):
    """Play repeating sequence of color sets.
       If mask is specified, it will rotate.
       Otherwise, pattern will rotate."""
    sequence: InitVar[CycleSequence]
    brightness: int | None = None
    transition: float = 0.0
    pattern: str
    mask: str | None = None
    clockwise: bool
    delay: float

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
        self.player.tasks.delete_owned_by(self)
        self.entry_index = self.wrap_entry_index(self.direction)
        self.show_color_set()

    @override
    def show_color_set(self):
        """Show color set."""
        entry = self.entries[self.entry_index]
        cs = self.lights.color_sets.by_set_name[entry.name]
        log.info(
            f"Chasing color set {cs.group}.{cs.name} "
            f"for {entry.seconds} seconds "
            f"({self.entry_index + 1} / {len(self.entries)})."
        )
        if entry.seconds is not None:
            self.schedule(due=entry.seconds)
        kwargs: dict[str, Any] = dict(
            baseline=LightSetBaseline(on=False),
            color_set_name=entry.name,
            delay=self.delay, 
            special=ChannelParams(),
        )
        sequence_kwargs: dict[str, Any] = dict(
            clockwise=self.clockwise,
            pattern=self.pattern,
        )
        if self.mask is None:
            kwargs |= dict(sequence=rotate)
        else:
            kwargs |= dict(sequence=chase)
            sequence_kwargs |= dict(mask=self.mask)
        kwargs['sequence_kwargs'] = sequence_kwargs
        mode = cast(
            BaseMode,
            self.player.create_mode_instance(
                mode_definition=ModeDefinition(
                    name='cs_rotate',
                    cls=SequenceMode,
                ),
                kwargs=kwargs,
                parent=self,
            )
        )
        self.schedule(mode.execute)

