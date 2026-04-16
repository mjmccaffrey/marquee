"""Marquee Lighted Sign Project - lightedbutton"""

from dataclasses import dataclass
import logging

from devices.button import Button
from devices_misc import LightedButtonInterface
from devices.relays import RelayClient

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class LightedButton(Button, LightedButtonInterface):
    """Supports lighted physical buttons."""
    relay: RelayClient
    
    def __post_init__(self) -> None:
        """Initialize."""
        self.set_light(False)

    def set_light(self, on: bool) -> None:
        """"""
        self.relay.set_state_of_devices('1' if on else '0')

