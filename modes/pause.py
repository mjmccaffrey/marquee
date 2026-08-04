"""Marquee Lighted Sign Project - pause"""

from dataclasses import dataclass
from itertools import cycle, repeat
import logging
from typing_extensions import override

from devices.color import Color
from light_defs import EXTRA_CUPOLA
from . import PerformanceMode
            
log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class Pause(PerformanceMode):
    """Do almost nothing."""

    @override
    def __post_init__(self):
        super().__post_init__()
        self.delete_mode_instance(17)
        self.delete_mode_instance(20)
        self.lights.set_channels(on=False, force=True)
        self.extra.set_channels(on=False, force=True)
