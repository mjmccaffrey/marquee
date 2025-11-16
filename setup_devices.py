"""Marquee Lighted Sign Project - setup_devices"""

import signal

from gpiozero import Button as _Button  # type: ignore

from button import Button
from button_misc import ButtonSet
from hue import HueBridge
from shelly import ShellyProDimmer2PM
from instruments import BellSet, DrumSet
from lightset import LightSet
from lightset_misc import ALL_RELAYS
from relays import NumatoRL160001, NumatoSSR80001

SHELLY_IP_ADDRESSES = [
    '192.168.64.111',
    '192.168.64.112',
    '192.168.64.113',
    '192.168.64.114',
    '192.168.64.115',
    '192.168.64.116',
]

HUE_APPLICATION_KEY = 'bWM1gTUsjVOLVyxC7zqwVuymvsziOIIikKy7RKmC'
HUE_IP_ADDRESS = '192.168.51.168'
HUE_BULB_IDS = [
    'a6233fab-9dfb-494f-b802-2d05b24e79bf',
    'a64ae2fb-b60d-4e4a-9c72-391cf6824ce0',
    'a65c68e2-ea8c-4016-a21a-6b85a728f784',
    'b6a92e92-ed7f-4ea4-8942-2bb1388cb888',
    'f4d943f2-6f03-4485-9242-dde71b146840',
    'fda76dea-1fa0-45e5-9084-59bbf1546574',
]

SYLVANIA_40_INCANDESCENT_FROSTED_GLOBE = {
    '0': 0, '1': 15, '2': 20, '3': 30, '4': 40,
    '5': 50, '6': 60, '7': 70, '8':80, '9': 90,
    'A': 100, 'F': 23,
}

HALCO_11_INCANDESCENT_S14_TRANSPARENT_AMBER = {
    '0': 0, '1': 15, '2': 20, '3': 30, '4': 40,
    '5': 50, '6': 60, '7': 70, '8':80, '9': 90,
    'A': 100, 'F': 23,
}  # ??

def setup_devices(
    brightness_factor: float
) -> tuple[BellSet, ButtonSet, DrumSet, LightSet]:
    """Create and return objects for all physical devices."""
    bells = BellSet(
        relays = NumatoSSR80001("/dev/marquee_bells")  # /dev/ttyACM1
    )
    drums = DrumSet(
        relays = NumatoRL160001("/dev/marquee_drums")  # /dev/ttyACM0
    )
    relays = NumatoRL160001(
        "/dev/marquee_lights", ALL_RELAYS,
    )  # /dev/ttyACM2
    dimmers = [
        ShellyProDimmer2PM(i, ip)
        for i, ip in enumerate(SHELLY_IP_ADDRESSES)
    ]
    hue = HueBridge(
        index = 0,
        ip_address = HUE_IP_ADDRESS,
        channel_count= len(HUE_BULB_IDS),
        application_key = HUE_APPLICATION_KEY,
    )
    lights = LightSet(
        relays=relays,
        dimmers=dimmers,
        hue=hue,
        bulb_adjustments=SYLVANIA_40_INCANDESCENT_FROSTED_GLOBE,
        brightness_factor_init=brightness_factor,
    )
    buttons = ButtonSet(
        body_back = Button(
            "body_back",
            _Button(pin=26, bounce_time=0.10, hold_time=10), 
            support_hold=True,
            signal_number=signal.SIGUSR1,  # type: ignore
        ),
        remote_a = Button(
            "remote_a",
            _Button(pin=19, pull_up=False, bounce_time=0.10)
        ),
        remote_b = Button(
            "remote_b",
            _Button(pin=13, pull_up=False, bounce_time=0.10)
        ),
        remote_c = Button(
            "remote_c",
            _Button(pin=6, pull_up=False, bounce_time=0.10)
        ),
        remote_d = Button(
            "remote_d",
            _Button(pin=5, pull_up=False, bounce_time=0.10)
        ),
    )
    return bells, buttons, drums, lights
