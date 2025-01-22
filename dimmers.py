"""Marquee Lighted Sign Project - dimmers"""

import requests
import time

class Dimmer:
    """Supports the Shelly ... ."""

    all_dimmers = []
    transition_default = 0.5

    def __init__(self, ip_address, id):
        """Create the dimmer instance."""
        self.ip_address = ip_address
        self.id = id
        self.all_dimmers.append(self)
        # self._get_state()
        self.set_brightness(level=100, additional={'output': 'true'}) # !!!

    def close(self):
        """Clean up."""

    def set_brightness(
            self, 
            level=None, 
            offset=None,
            transition=None, 
            wait=False,
            additional=None,  # !!!
    ):
        """ """
        # !!!! Set and respond to timeout
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
        } | additional
        requests.get(f'http://{self.ip_address}/rpc/Light.Set', params=params)
        if wait:
            print("WAIT")
            time.sleep(transition_default)

    @classmethod
    def set_brightness_all(
            cls, 
            level=None, 
            offset=None, 
            transition=None, 
            wait=False,
    ):
        """ """
        return
        for dimmer in [all_dimmers[0]]:
            dimmer.set_brightness(level, offset, wait=False)
        if wait:
            time.sleep(transition_default)
