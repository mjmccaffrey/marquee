"""Marquee Lighted Sign Project - device_defs"""

import signal

from gpiozero import Button as _Button

from devices.bulb import (
    Hue_BR30_Enhanced_Color, 
    Sylvania_G25_Frosted_40,
    Sylvania_G40_Frosted_100, 
)
from devices.button import Button, LightedButton
from devices.buttonset import ButtonSet 
from devices.devices_misc import ButtonName
from devices.deviceset import DeviceSet
from devices.hue import HueBridge
from devices.joystick import Joystick
from devices.numato import NumatoRL320001, NumatoRL160001, NumatoSSR80001
from devices.relaymodule import CombinedRelayModule, create_client
from devices.shelly import ShellyController, ShellyProDimmer1PM, ShellyProDimmer2PM
from devices.tiltset import TiltSet
from instruments import BellSet, ClickSet, DrumSet, LightSet, Ringer
from light_defs import *

HUE_APPLICATION_KEY = open('hue.key').read().strip()
HUE_IP_ADDRESS = '192.168.64.130'
HUE_BULB_IDS_0 = [
    "79d6cc75-8eaa-450a-be32-6bc14695b11a",  # Labeled 3 - top left
    "1e5bbfc7-f3f1-47e1-bba9-18e70588f1e3",
    "b0338b37-5ed1-4ec2-b4be-5f9157ba62af",
    "5e78cc1c-023d-4e29-80b3-379740a17cfb",
    "8939cef6-ed91-45b3-b656-1d14de4af4dc",
    "707de5cb-f986-4e79-89f0-16086f1fe56e",
    "90a20fd0-3aef-4a57-b93d-393c0956baa1",
    "6e3c6e43-7e01-40d5-a650-acbc391b716d",
    "108dee49-9e5c-4879-83be-1c6f361a89aa",
    "be70ec73-1aca-41a8-afaa-3e9dab07c27a",  # Labeled 0 - right bottom
    "3d3132d3-528c-4e15-bba7-f587e1442ef2",  # Labeled 1
    "35c48818-a97b-4b67-bbc8-22a68e6be153",  # Labeled 2
]
HUE_BULB_IDS_1 = [
    "04098e6c-f416-4ce5-b91c-06e6004b2a23",
    "a0906758-e0b5-45c3-8e19-85994f253bd7",
    "359de043-2614-443f-8e44-fad407fdc854",
    # "398bd880-e870-4d00-88ee-dce5aa83c17b",  # Donut
    "5bed6538-94b3-4fb9-8b14-c32c81ec80fa",  # Cupola
]
HUE_ZONE_IDS_0 = {
    # https://192.168.64.130/clip/v2/resource/zone
    # ↑ Lists zones, with names, and included bulbs
    # "services": [
    #     {
    #         "rid": "2339a4b8-5dd2-438e-9c91-ed0fdb59180e",
    #         "rtype": "grouped_light"
    '0.12': [
        "2339a4b8-5dd2-438e-9c91-ed0fdb59180e",
        "afbce248-f994-4f71-833d-f7c20eb96814",
    ],
    '0.15': [
        "2339a4b8-5dd2-438e-9c91-ed0fdb59180e",
        "afbce248-f994-4f71-833d-f7c20eb96814",
        "1afc2cc8-cbf8-484b-b2d6-46575b2cef97",
    ],
    '0.top': ['4cfe20b3-43ae-409e-8d21-ea84f96daef8'],
    '0.right': ['63818e6a-a041-472d-870d-20f5a5ddd9c3'],
    '0.bottom': ['94136ba4-d8dd-449e-a0ce-411ca6a9e9d7'],
    '0.left': ['f444479d-e7ee-4b76-bf7f-9cbf10ebfb68' ],
}
HUE_ZONE_IDS_1 = {
    '1.4': ['fca0fb37-bd2b-4f8a-b6b0-f58d7546f071'],
    '1.middle': ['1afc2cc8-cbf8-484b-b2d6-46575b2cef97'],
}
HUE_GROUPS_0 = {
    '0.12': LIGHTS_CLOCKWISE,
    '0.15': range(15),
    '0.top': LIGHTS_TOP,
    '0.right': LIGHTS_RIGHT,
    '0.bottom': LIGHTS_BOTTOM,
    '0.left': LIGHTS_LEFT,
}
HUE_GROUPS_1 = {
    '1.4': [0, 1, 2, 3],
    '1.middle': [0, 1, 2],
}

SHELLY_IP_ADDRESSES = [
    '192.168.64.111',
    '192.168.64.112',
    '192.168.64.113',
    '192.168.64.114',
    '192.168.64.115',
    '192.168.64.116',
]


def buttons(light_relays: NumatoRL160001) -> ButtonSet:
    """Define button set."""
    return ButtonSet(
        body_back = Button(
            ButtonName.BODY_BACK,
            _Button(pin=26, bounce_time=0.10, hold_time=10), 
            supports_hold=True,
        ),
        corded_a = Button(
            ButtonName.CORDED_A,
            _Button(pin=3, bounce_time=0.05),
            signal_number=signal.SIGUSR1,  # type: ignore
        ),
        corded_b = Button(
            ButtonName.CORDED_B,
            _Button(pin=2, bounce_time=0.05),
            signal_number=signal.SIGUSR2,  # type: ignore
        ),
        corded_c = Button(
            ButtonName.CORDED_C,
            _Button(pin=18, bounce_time=0.05),
            signal_number=signal.SIGFPE,  # type: ignore
        ),
        game_start = LightedButton(
            ButtonName.GAME_START,
            _Button(pin=16, bounce_time=0.05),
            relay=create_client(light_relays, BUTTON_TO_RELAY),
        ),
        remote_a = Button(
            ButtonName.REMOTE_A,
            _Button(pin=21, pull_up=False, bounce_time=0.10)  # 19

        ),
        remote_b = Button(
            ButtonName.REMOTE_B,
            _Button(pin=20, pull_up=False, bounce_time=0.10)  # 13
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
    """Define joystick."""
    return Joystick(
        up=_Button(pin=4, bounce_time=0.05),
        down=_Button(pin=17, bounce_time=0.05),
        left=_Button(pin=27, bounce_time=0.05),
        right=_Button(pin=22, bounce_time=0.05),
    )

def tilts() -> TiltSet:
    """"""
    return TiltSet(
        left=_Button(pin=13, pull_up=False, bounce_time=0.05),
        right=_Button(pin=19, pull_up=False, bounce_time=0.05),
    )

def define_devices(
    brightness_factor: float,
    speed_factor: float,
) -> DeviceSet:
    """Create and return objects for all physical devices."""
    drum_16_relays = NumatoRL160001("/dev/marquee_drums_16")
    drum_32_relays = NumatoRL320001("/dev/marquee_drums_32")
    drum_48_relays = CombinedRelayModule(drum_16_relays, drum_32_relays)
    drums = DrumSet(relays=create_client(drum_48_relays))
    light_relays = NumatoRL160001("/dev/marquee_lights")
    lights = LightSet(
        count=LIGHT_COUNT,
        relays=create_client(light_relays, LIGHT_TO_RELAY),
        mirror=create_client(drum_16_relays, LIGHT_TO_RELAY),
        controller_type=HueBridge,
        controller_kwargs=dict(
            application_key=HUE_APPLICATION_KEY,
            ip_address=HUE_IP_ADDRESS,
            bulb_model=Hue_BR30_Enhanced_Color,
            bulb_ids=HUE_BULB_IDS_0,
            zone_ids=HUE_ZONE_IDS_0,
            groups=HUE_GROUPS_0,
        ),
        brightness_factor_init=brightness_factor,
        speed_factor=speed_factor,
    )
    extra = LightSet(
        count=4,
        relays=create_client(light_relays, EXTRA_TO_RELAY),
        mirror=None,
        controller_type=HueBridge,
        controller_kwargs=dict(
            application_key=HUE_APPLICATION_KEY,
            ip_address=HUE_IP_ADDRESS,
            bulb_model=Hue_BR30_Enhanced_Color,
            bulb_ids=HUE_BULB_IDS_1,
            zone_ids=HUE_ZONE_IDS_1,
            groups=HUE_GROUPS_1,
        ),
        brightness_factor_init=brightness_factor,
        speed_factor=speed_factor,
    )
    clicker = ClickSet(create_client(drum_16_relays, CLICK_TO_RELAY))
    ringer = Ringer(create_client(light_relays, RINGER_TO_RELAY))
    return DeviceSet(
        buttons(light_relays), drums, lights, extra, 
        clicker, ringer, joystick(), tilts(),
    )


def define_devices_shelly(
    brightness_factor: float,
    i: int,
    speed_factor: float,
) -> DeviceSet:
    """Create and return objects for all physical devices."""
    # bell_relays = NumatoSSR80001("/dev/marquee_bells")  # /dev/ttyACM1
    # bells = BellSet(relays=bell_relays.create_client(
    #     {i: i for i in range(bell_relays.relay_count)})
    # )
    drum_relays = NumatoRL160001("/dev/marquee_drums")  # /dev/ttyACM0
    drums = DrumSet(relays=create_client(drum_relays))
    light_relays = NumatoRL160001("/dev/marquee_lights")  # /dev/ttyACM2
    lights = LightSet(
        count=len(LIGHT_TO_RELAY),
        relays=create_client(light_relays, LIGHT_TO_RELAY),
        mirror=create_client(drum_relays, LIGHT_TO_RELAY),
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
    extra = None
    clicker = ClickSet(create_client(light_relays, CLICK_TO_RELAY))
    ringer = Ringer(create_client(light_relays, RINGER_TO_RELAY))
    return DeviceSet(
        buttons(light_relays), drums, lights, extra, 
        clicker, ringer, joystick(), tilts(),
    )


BUTTON_TO_RELAY = {0: 11}
RINGER_TO_RELAY = {0: 3}
EXTRA_TO_RELAY = {0: 10, 1: 10, 2: 10, 3: 10}  # Kludge.

CLICK_TO_RELAY = {0: 0, 1: 1}

