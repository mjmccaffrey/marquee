"""Marquee Lighted Sign Project - setup_devices_hue"""

import signal

from gpiozero import Button as _Button  # type: ignore

from bulb import Hue_BR30_Enhanced_Color, Sylvania_G40_Frosted_100
from button import Button
from devices_misc import ButtonSet
from hue import HueBridge
from shelly import ShellyConsolidatedController, ShellyProDimmer1PM
from instruments import BellSet, DrumSet
from lightset import ClickSet, LightSet
from lightset_misc import LIGHT_TO_RELAY, TOP_TO_RELAY, CLICK_TO_RELAY
from relays import NumatoRL160001, NumatoSSR80001

SHELLY_IP_ADDRESSES = [
    '192.168.64.111',
    '192.168.64.112',
    '192.168.64.113',
    '192.168.64.114',
    '192.168.64.115',
    '192.168.64.116',
]

HUE_APPLICATION_KEY = open('hue.key').read().strip()
HUE_IP_ADDRESS = '192.168.64.130'
HUE_BULB_IDS = [
    "be70ec73-1aca-41a8-afaa-3e9dab07c27a",
    "3d3132d3-528c-4e15-bba7-f587e1442ef2",
    "35c48818-a97b-4b67-bbc8-22a68e6be153",
    "79d6cc75-8eaa-450a-be32-6bc14695b11a",
    "1e5bbfc7-f3f1-47e1-bba9-18e70588f1e3",
    "b0338b37-5ed1-4ec2-b4be-5f9157ba62af",
    "5e78cc1c-023d-4e29-80b3-379740a17cfb",
    "8939cef6-ed91-45b3-b656-1d14de4af4dc",
    "707de5cb-f986-4e79-89f0-16086f1fe56e",
    "90a20fd0-3aef-4a57-b93d-393c0956baa1",
    "6e3c6e43-7e01-40d5-a650-acbc391b716d",
    "108dee49-9e5c-4879-83be-1c6f361a89aa",
]
HUE_ZONE_IDS = [
    # "services": [
    #     {
    #         "rid": "2339a4b8-5dd2-438e-9c91-ed0fdb59180e",
    #         "rtype": "grouped_light"    
    "2339a4b8-5dd2-438e-9c91-ed0fdb59180e",
    "afbce248-f994-4f71-833d-f7c20eb96814",
]

def setup_devices(
    brightness_factor: float,
    speed_factor: float,
) -> tuple[BellSet, ButtonSet, DrumSet, LightSet, LightSet, ClickSet]:
    """Create and return objects for all physical devices."""

    relays = NumatoSSR80001("/dev/marquee_bells")  # /dev/ttyACM1
    bells = BellSet(relays=relays.create_client(
        {i: i for i in range(relays.relay_count)})
    )
    relays = NumatoRL160001("/dev/marquee_drums")  # /dev/ttyACM0
    drums = DrumSet(relays=relays.create_client(
        {i: i for i in range(relays.relay_count)})
    )
    relays = NumatoRL160001("/dev/marquee_lights")  # /dev/ttyACM2
    primary = LightSet(
        relays=relays.create_client(LIGHT_TO_RELAY),
        controller_type=HueBridge,
        controller_kwargs=dict(
            application_key=HUE_APPLICATION_KEY,
            ip_address=HUE_IP_ADDRESS,
            bulb_model=Hue_BR30_Enhanced_Color,
            bulb_ids=HUE_BULB_IDS,
            zone_ids=HUE_ZONE_IDS,
        ),
        brightness_factor_init=brightness_factor,
        speed_factor=speed_factor,
    )
    secondary = LightSet(
        relays=relays.create_client(TOP_TO_RELAY),
        controller_type=ShellyConsolidatedController,
        controller_kwargs=dict(
            bulb_model=Sylvania_G40_Frosted_100,
            dimmers=[
                ShellyProDimmer1PM(
                    index=0,
                    ip_address='192.168.64.116',
                    bulb_model=Sylvania_G40_Frosted_100,
                    channel_first_index=0,
                ),
            ],
        ),
        brightness_factor_init=brightness_factor,
        speed_factor=speed_factor,
    )
    clicker = ClickSet(
        relays=relays.create_client(CLICK_TO_RELAY),
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
    return bells, buttons, drums, primary, secondary, clicker

