"""Marquee Lighted Sign Project - device_defs"""

import signal

from gpiozero import Button as _Button  # type: ignore

from devices.bulb import (
    Hue_BR30_Enhanced_Color, Sylvania_G40_Frosted_100, 
    Sylvania_G25_Frosted_40,
)
from devices.button import Button, LightedButton
from devices.buttonset import ButtonSet 
from devices.devices_misc import ButtonName
from devices.hue import HueBridge
from devices.joystick import Joystick
from devices.relays import NumatoRL160001, NumatoSSR80001
from devices.shelly import ShellyController, ShellyProDimmer1PM, ShellyProDimmer2PM
from instruments import BellSet, ClickSet, DrumSet, LightSet
from light_defs import *

DeviceSet = tuple[
    BellSet, ButtonSet, DrumSet, LightSet, LightSet | None, ClickSet, Joystick,
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
SHELLY_IP_ADDRESSES = [
    '192.168.64.111',
    '192.168.64.112',
    '192.168.64.113',
    '192.168.64.114',
    '192.168.64.115',
    '192.168.64.116',
]


def buttons(light_relays: NumatoRL160001) -> ButtonSet:
    """"""
    return ButtonSet(
        body_back = Button(
            ButtonName.BODY_BACK,
            _Button(pin=26, bounce_time=0.10, hold_time=10), 
            supports_hold=True,
            signal_number=signal.SIGUSR1,  # type: ignore
        ),
        corded_a = Button(
            ButtonName.CORDED_A,
            _Button(pin=12, bounce_time=0.05),
        ),
        corded_b = Button(
            ButtonName.CORDED_B,
            _Button(pin=16, bounce_time=0.05),
        ),
        game_start = LightedButton(
            ButtonName.GAME_START,
            _Button(pin=21, bounce_time=0.05),
            relay=light_relays.create_client(BUTTON_TO_RELAY),
        ),
        remote_a = Button(
            ButtonName.REMOTE_A,
            _Button(pin=19, pull_up=False, bounce_time=0.10)

        ),
        remote_b = Button(
            ButtonName.REMOTE_B,
            _Button(pin=13, pull_up=False, bounce_time=0.10)
        ),
        remote_c = Button(
            ButtonName.REMOTE_C,
            _Button(pin=6, pull_up=False, bounce_time=0.10)
        ),
        remote_d = Button(
            ButtonName.REMOTE_D,
            _Button(pin=5, pull_up=False, bounce_time=0.10)
        ),
    )


def joystick() -> Joystick:
    """"""
    return Joystick(
        up=_Button(pin=4, bounce_time=0.05),
        down=_Button(pin=17, bounce_time=0.05),
        left=_Button(pin=27, bounce_time=0.05),
        right=_Button(pin=22, bounce_time=0.05),
    )

def define_devices_hue_shelly(
    brightness_factor: float,
    speed_factor: float,
) -> DeviceSet:
    """Create and return objects for all physical devices."""
    bell_relays = NumatoSSR80001("/dev/marquee_bells")  # /dev/ttyACM1
    bells = BellSet(relays=bell_relays.create_client(
        {i: i for i in range(bell_relays.relay_count)})
    )
    drum_relays = NumatoRL160001("/dev/marquee_drums")  # /dev/ttyACM0
    drums = DrumSet(relays=drum_relays.create_client(
        {i: i for i in range(drum_relays.relay_count)})
    )
    light_relays = NumatoRL160001("/dev/marquee_lights")  # /dev/ttyACM2
    lights = LightSet(
        count=LIGHT_COUNT,
        relays=light_relays.create_client(LIGHT_TO_RELAY),
        mirror=drum_relays.create_client(LIGHT_TO_RELAY),
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

    # zigbee:
    #     relay?
    #     donut
    #     3 pacman lights
    
    aux = LightSet(
        count=len(TOP_TO_RELAY),
        relays=light_relays.create_client(TOP_TO_RELAY),
        mirror=drum_relays.create_client(TOP_TO_RELAY),
        controller_type=ShellyController,
        controller_kwargs=dict(
            bulb_model=Sylvania_G40_Frosted_100,
            dimmers=[
                ShellyProDimmer1PM(
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
        relays=light_relays.create_client(CLICK_TO_RELAY),
    )
    return bells, buttons(light_relays), drums, lights, aux, clicker, joystick()


def define_devices_shelly(
    brightness_factor: float,
    i: int,
    speed_factor: float,
) -> DeviceSet:
    """Create and return objects for all physical devices."""
    bell_relays = NumatoSSR80001("/dev/marquee_bells")  # /dev/ttyACM1
    bells = BellSet(relays=bell_relays.create_client(
        {i: i for i in range(bell_relays.relay_count)})
    )
    drum_relays = NumatoRL160001("/dev/marquee_drums")  # /dev/ttyACM0
    drums = DrumSet(relays=drum_relays.create_client(
        {i: i for i in range(drum_relays.relay_count)})
    )
    light_relays = NumatoRL160001("/dev/marquee_lights")  # /dev/ttyACM2
    lights = LightSet(
        count=len(LIGHT_TO_RELAY),
        relays=light_relays.create_client(LIGHT_TO_RELAY),
        mirror=drum_relays.create_client(LIGHT_TO_RELAY),
        controller_type=ShellyController,
        controller_kwargs=dict(
                bulb_model=Sylvania_G25_Frosted_40,
                dimmers=[
                    ShellyProDimmer2PM(
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
    aux = None
    clicker = ClickSet(
        relays=light_relays.create_client(CLICK_TO_RELAY),
    )
    return bells, buttons(light_relays), drums, lights, aux, clicker, joystick()


define_devices = define_devices_hue_shelly
"""Create and return objects for all physical devices."""

BUTTON_TO_RELAY = {
    0: 11,    
}
CLICK_TO_RELAY = {
     0: 2,  1: 3, 
}
ALL_RELAYS = LIGHT_TO_RELAY | TOP_TO_RELAY | BUTTON_TO_RELAY | CLICK_TO_RELAY
