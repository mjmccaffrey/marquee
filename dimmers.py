"""Marquee Lighted Sign Project - dimmers"""

import asyncio
from dataclasses import dataclass
import requests
import time
import types

import aiohttp

TRANSITION_MINIMUM = 0.5
TRANSITION_MAXIMUM = 10800.0

@dataclass
class DimmerParams:
    """"""
    override_relays: bool = False
    level_on: int = 100
    level_off: int = 0
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
            r = self.session.get(
                f'http://{self.ip_address}/rpc/Light.Set', 
                params=params,
                timeout=1.0,
            )
        except requests.exceptions.ConnectTimeout:
            print(time.time(), self.ip_address, self.id)
        if wait:
            print("WAIT")
            time.sleep(self.transition_default)

    def stage_set_command(
        self, 
        level=None, 
        offset=None,
        transition=None, 
        on=None,
    ):
        """ RETURNS COLLECTION THAT CALLER WILL ADD TO ITERABLE """
        if level:
            brightness = level 
        elif offset:
            brightness = self.brightness + offset
        else:
            brightness = None
        params = (
            ({'id': self.id}) |
            ({'brightness': brightness} if brightness else {})
            ({'transition_duration': transition or self.transition_default})
        )
        return types.SimpleNamespace(
            dimmer=self,
            url=f'http://{self.ip_address}/rpc/Light.Set',
            params=params,
        )

    @classmethod
    def execute_multiple_commands(cls, commands):
        """"""
        # async etc.
        # set each dimmer's brightness if needed'

