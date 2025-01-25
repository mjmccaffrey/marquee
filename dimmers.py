"""Marquee Lighted Sign Project - dimmers"""

from dataclasses import dataclass
import requests
import time

TRANSITION_MINIMUM = 0.5

@dataclass
class DimmerParams:
    """"""
    override_relays: bool = False
    level_on: float = 100.0
    level_off: float = 0.0
    transition_on: float = TRANSITION_MINIMUM
    transition_off: float = TRANSITION_MINIMUM

class Dimmer:
    """Supports the Shelly Pro Dimmer 2PM."""

    transition_default = 0.5

    def __init__(self, ip_address, id):
        """Create the dimmer instance."""
        print(time.time())
        self.ip_address = ip_address
        self.id = id
        # self._get_state() !!!
        self.session = requests.Session()
        self.set_brightness(level=100, additional={'output': 'true'}) # !!!

    def close(self):
        """Clean up."""

    def set_brightness(
            self, 
            level=None, 
            offset=None,
            transition=None, 
            wait=False,
            additional=None,
    ):
        """ """
        assert level is not None or offset is not None
        self.brightness = (
            level 
                if level is not None else 
            self.brightness + offset
        )
        params = {
            'id': self.id, 
            'brightness': self.brightness, 
            'transition_duration': transition or self.transition_default,
        } | (additional or {})
        try:
            self.session.get(
                f'http://{self.ip_address}/rpc/Light.Set', 
                params=params,
                timeout=1.0,
            )
        except requests.exceptions.ConnectTimeout:
            print(time.time(), self.ip_address, self.id)
        if wait:
            print("WAIT")
            time.sleep(self.transition_default)
