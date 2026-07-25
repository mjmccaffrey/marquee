"""Marquee Lighted Sign Project - pause"""

from dataclasses import dataclass
from itertools import cycle, repeat
import logging

from devices.color import Color
from light_defs import EXTRA_CUPOLA
from . import PerformanceMode
            
log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class Pause(PerformanceMode):
    """Do nothing."""