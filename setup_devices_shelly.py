"""Marquee Lighted Sign Project - setup_devices_shelly"""

import signal

from gpiozero import Button as _Button  # type: ignore

from devices.bulb import Sylvania_G25_Frosted_40
from devices.button import Button
from devices.devices_misc import ButtonSet
from devices.shelly import ShellyConsolidatedController, ShellyProDimmer2PM
from instruments import BellSet, DrumSet
from lightset import LightSet
from lightset_misc import ALL_RELAYS, TOP_TO_RELAY
from devices.relays import NumatoRL160001, NumatoSSR80001

SHELLY_IP_ADDRESSES = [
    '192.168.64.111',
    '192.168.64.112',
    '192.168.64.113',
    '192.168.64.114',
    '192.168.64.115',
    '192.168.64.116',
]

def setup_devices(
    brightness_factor: float,
    speed_factor: float,
) -> tuple[BellSet, ButtonSet, DrumSet, LightSet, LightSet]:
    """Create and return objects for all physical devices."""
    bells = BellSet(
        relays = NumatoSSR80001("/dev/marquee_bells")  # /dev/ttyACM1
    )
    drums = DrumSet(
        relays = NumatoRL160001("/dev/marquee_drums")  # /dev/ttyACM0
    )
    relays = NumatoRL160001(
        "/dev/marquee_lights", ALL_RELAYS,  THIS DOES NOT ALLOW DEVICE #s TO BE INDEPENDENT
    )  # /dev/ttyACM2
    lights = LightSet(
        relays=relays,
        relay_devices=list(TOP_TO_RELAY),
        controller_type=ShellyConsolidatedController,
        controller_kwargs=dict(
                bulb_model=Sylvania_G25_Frosted_40,
                dimmers=[
                    ShellyProDimmer2PM(
                        index=i,
                        ip_address=ip,
                        bulb_model=Sylvania_G25_Frosted_40,
                        channel_first_index=i * 2,
                    )
                    for i, ip in enumerate(SHELLY_IP_ADDRESSES)
                ],
        ),
        brightness_factor_init=brightness_factor,
        speed_factor=speed_factor,
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
