"""Marquee Lighted Sign Project - evenoddfade"""

from dataclasses import dataclass
from functools import partial
from typing_extensions import override

from . import PerformanceMode
from . import opposite
from devices.specialparams import ChannelParams
            

@dataclass(kw_only=True)
class EvenOddFade(PerformanceMode):
    """Fade every-other bulb."""
    delay: float

    @override
    def execute(self) -> None:
        """Schedule next 2 patterns. Schedule next execute."""
        self.lights.set_channels(brightness=0) 
        odd_on = ''.join(
            '1' if i % 2 else '0' for i in range(self.lights.count)
        )
        even_on = opposite(odd_on)
        for i, pattern in enumerate((even_on, odd_on)):
            self.schedule(
                action=partial(
                    self.lights.set_relays,
                    pattern, 
                    special=ChannelParams(
                        concurrent=True,
                        brightness_on = 100,
                        brightness_off = 0,
                        trans_on=self.delay,
                        trans_off=self.delay,
                    )
                ),
                due=(self.delay * i)
            )
        self.schedule(due=(self.delay * (i + 1)))

