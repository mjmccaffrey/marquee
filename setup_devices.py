"""Marquee Lighted Sign Project - setup_devices"""

import signal

from gpiozero import Button as _Button  # type: ignore

from bulb import Hue_BR30_Enhanced_Color
from button import Button
from button_misc import ButtonSet
from hue import HueBridge
# from shelly import ShellyConsolidatedController, ShellyProDimmer2PM
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

HUE_APPLICATION_KEY = open('hue.key').read()
HUE_IP_ADDRESS = '192.168.64.130'
HUE_BULB_IDS = [
    "ca051ade-5842-4c15-aacf-b1e795feb1ad",
    "7f053a5d-0283-4dd6-80b3-b4d8e83cf4f0",
    "afe4c0e3-ab80-40b2-966a-b0069ee50880",
    "3456c84d-9189-4369-b022-1eed24eedb58",
    "1367f291-d54c-41a5-90a5-6ec40616779c",
    "6da5e687-1eb4-404d-8f6e-7badc2c2b6d6",
    "7d42575e-f864-48e8-99f9-88905008ab07",
    "de84afc5-e39a-4b2e-aa15-b67a211ff4da",
    "6591a827-379b-417d-b165-a10cdadb81a1",
    "934abf75-d5f9-402d-a6cd-b1b82812ef2f",
    "8af80fb4-9daf-4762-bd54-bdc221690db0",
    "e2cfe6e2-845e-489a-8434-8d90ac74f74a",
]

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
    primary = LightSet(
        relays=relays,
        light_relays={1, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16,},
        click_relays={2, 3, 10},
        controller=HueBridge(
            application_key=HUE_APPLICATION_KEY,
            ip_address=HUE_IP_ADDRESS,
            bulb_model=Hue_BR30_Enhanced_Color,
            bulb_ids=HUE_BULB_IDS,
        ),
        brightness_factor_init=1.0,
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
    return bells, buttons, drums, primary
