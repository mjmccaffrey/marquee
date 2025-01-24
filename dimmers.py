"""Marquee Lighted Sign Project - dimmers"""

import requests
import time

class Dimmer:
    """Supports the Shelly Pro Dimmer 2PM."""

    transition_default = 0.5

    def __init__(self, ip_address, id):
        """Create the dimmer instance."""
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
        }
        self.session.get(
            f'http://{self.ip_address}/rpc/Light.Set', 
            params=params,
            timeout=1.0,
        )
        if wait:
            print("WAIT")
            time.sleep(self.transition_default)
