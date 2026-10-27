"""Marquee Lighted Sign Project - devices_edwards"""

from collections.abc import Sequence
from enum import IntEnum
from typing import Any

import requests
import urllib3

from devices.bulb import (
    Hue_BR30_Enhanced_Color, 
)
from devices.deviceset import DeviceSet
from devices.hue import HueBridge, http
from instruments import LightSet
from schemas import DeviceName, LightConfig


HUE_APPLICATION_KEY = open(r'systems/hue_edwards.key').read().strip()
HUE_IP_ADDRESS = '192.168.64.130'

HUE_BULB_IDS = [
    # "398bd880-e870-4d00-88ee-dce5aa83c17b",  # Donut
]
HUE_GROUPS: dict[str, Sequence[int]] = {
}
HUE_ZONE_IDS: dict[str, list[str]] = {
    # https://192.168.64.130/clip/v2/resource/zone
    # ↑ Lists zones, with names, and included bulbs
    # "services": [
    #     {
    #         "rid": "2339a4b8-5dd2-438e-9c91-ed0fdb59180e",
    #         "rtype": "grouped_light"
}


class Light(IntEnum):
    TL =  0  # Top
    TM =  1
    TR =  2
    RT =  3  # Right
    RM =  4
    RB =  5
    BR =  6  # Bottom
    BM =  7
    BL =  8
    LB =  9  # Left
    LM = 10
    LU = 11
    ML = 12  # Middle
    MM = 13
    MR = 14
    CP = 15  # Cupola


light_config = LightConfig()
c, l = light_config, Light
c.enum = l
c.count = len(l)


def setup_devices(
    brightness_factor: float,
    speed_factor: float,
    testing: bool,
) -> dict[DeviceName, Any]:  # DeviceSet:
    """Create and return objects for all physical devices."""
    session = requests.Session()
    session.headers = {'hue-application-key': HUE_APPLICATION_KEY}
    session.verify = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    lights = LightSet(
        count=light_config.count,
        relays=None,
        mirror=None,
        controller_type=HueBridge,
        controller_kwargs=dict(
            ip_address=HUE_IP_ADDRESS,
            bulb_model=Hue_BR30_Enhanced_Color,
            session=session,
            http=http,
            bulb_ids=HUE_BULB_IDS,
            zone_ids=HUE_ZONE_IDS,
            groups=HUE_GROUPS,
        ),
        brightness_factor_init=brightness_factor,
        channel_enum=Light,
        speed_factor=speed_factor,
        config=light_config,
    )
    return {
        DeviceName.LIGHTS: lights,
    }

