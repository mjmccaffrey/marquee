"""Marquee Lighted Sign Project - setup_devices"""

import signal

from gpiozero import Button as _Button  # type: ignore

from button import Button
from button_misc import ButtonSet
from dimmers import ShellyProDimmer2PM
from instruments import BellSet, DrumSet
from lightset import LightSet
from lightset_misc import ALL_RELAYS
from relays import NumatoRL160001, NumatoSSR80001

DIMMER_ADDRESSES = [
    '192.168.64.112',
    '192.168.64.112',
    '192.168.64.113',
    '192.168.64.114',
    '192.168.64.115',
    '192.168.64.116',
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
    lights = LightSet(
        relays = NumatoRL160001("/dev/marquee_lights", ALL_RELAYS),  # /dev/ttyACM2
        dimmers = [
            ShellyProDimmer2PM(i, ip)
            for i, ip in enumerate(DIMMER_ADDRESSES)
        ],
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
