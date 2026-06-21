"""Marquee Lighted Sign Project - colorsetchase"""

from dataclasses import InitVar, dataclass
import logging
from typing_extensions import override

from devices.devices_misc import ButtonName
from devices.specialparams import ChannelParams
from . import ColorSetMode
from .modes_misc import CycleSequence, ModeDefinition
from .sequences import rotate
from .sequencemode import LightSetBaseline, SequenceMode

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class ColorSetChase(ColorSetMode):
    """Play repeating sequence of color sets."""
    sequence: InitVar[CycleSequence]  # (color_set_name, seconds)
    brightness: int | None = None
    transition: float = 0.0

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
        self.create_mode_instance(
            mode_definition=ModeDefinition(
                name='cs_chase',
                cls=SequenceMode,
            ),
            kwargs=dict(
                baseline=LightSetBaseline(on=False),
                color_set_name=entry.name,
                delay=0.35, 
                sequence=rotate,
                sequence_kwargs=dict(
                    pattern="012---------", 
                    clockwise=False,
                ),
                special=ChannelParams(),
            ),
            parent=self,
        ).execute()

