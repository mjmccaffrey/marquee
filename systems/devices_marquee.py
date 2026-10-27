"""Marquee Lighted Sign Project - devices_marquee"""

from collections.abc import Sequence
from enum import IntEnum
import signal
from typing import Any

import gpiozero
from gpiozero import Device
from gpiozero.pins.mock import MockFactory
import requests
import urllib3

from devices.bulb import (
    Hue_BR30_Enhanced_Color, 
)
from devices.button import Button, LightedButton
from devices.deviceset import DeviceSet
from devices.hue import HueBridge, http, http_mock
from devices.joystick import Joystick
from devices.numato import NumatoRL320001, NumatoRL160001
from devices.relaymodule import MockRelay16, MockRelay32
from devices.relaymodule import CombinedRelayModule, create_client
from devices.shelly import ShellyController, ShellyProDimmer2PM
from instruments import Buzzer, Clicker, DrumSet, LightSet, Ringer
from schemas import DeviceName, LightConfig


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
c.by_row = [
    [       l.TL, l.TM, l.TR,       ],
    [ l.LU,                   l.RT, ],
    [ l.LM,                   l.RM, ],
    [ l.LB,                   l.RB, ],
    [       l.BL, l.BM, l.BR,       ],
]
c.top = [l.TL, l.TM, l.TR]
c.right = [l.RT, l.RM, l.RB]
c.bottom = [l.BL, l.BM, l.BR]
c.left = [l.LU, l.LM, l.LB]
c.middle = [l.ML, l.MM, l.MR]
c.by_side = [c.top, c.right, c.bottom, c.left]
c.column_b = [l.TL, l.BL]
c.column_c = [l.TM, l.BM]
c.column_d = [l.TR, l.BR]
c.by_column = [c.left, c.column_b, c.column_c, c.column_d, c.right]
c.clockwise = [l for side in c.by_side for l in side]
c.count = len(l)


HUE_APPLICATION_KEY = open('systems/hue_marquee.key').read().strip()
HUE_IP_ADDRESS = '192.168.64.130'

HUE_BULB_IDS = [
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
    "04098e6c-f416-4ce5-b91c-06e6004b2a23",  # 13
    "a0906758-e0b5-45c3-8e19-85994f253bd7",  # 14
    "359de043-2614-443f-8e44-fad407fdc854",  # 15
    "5bed6538-94b3-4fb9-8b14-c32c81ec80fa",  # 16 Cupola
]
HUE_GROUPS: dict[str, Sequence[int]] = {
    'top': light_config.top,
    'right': light_config.right,
    'bottom': light_config.bottom,
    'left': light_config.left,
    'middle': light_config.middle,
    'even': [l.TL, l.TR, l.RM, l.BR, l.BL, l.LM],
    'odd': [l.TM, l.RT, l.RB, l.BM, l.LB, l.LU],
    '12': list(range(12)),
    '13': list(range(12)) + [l.CP],
    '15': list(range(15)),
    '16': list(range(16)),
}
HUE_ZONE_IDS: dict[str, list[str]] = {
    # https://192.168.64.130/clip/v2/resource/zone
    # ↑ Lists zones, with names, and included bulbs
    # "services": [
    #     {
    #         "rid": "2339a4b8-5dd2-438e-9c91-ed0fdb59180e",
    #         "rtype": "grouped_light"
    'top': ['4cfe20b3-43ae-409e-8d21-ea84f96daef8'],
    'right': ['63818e6a-a041-472d-870d-20f5a5ddd9c3'],
    'bottom': ['94136ba4-d8dd-449e-a0ce-411ca6a9e9d7'],
    'left': ['f444479d-e7ee-4b76-bf7f-9cbf10ebfb68'],
    'middle': ['1afc2cc8-cbf8-484b-b2d6-46575b2cef97'],
    'even': ['166bcc4f-9598-49e7-b853-a239be50b514'],
    'odd': ['587dddb8-bec3-4555-9f3b-b12b2fca918d'],
    '12': ['21c66184-6be0-4c79-832e-9308ee4501eb'],
    '13': ['af193689-f8a4-4ace-9cef-87264c9f5129'],
    '15': ['e896f871-f666-4d40-a61c-f0b789f48330'],
    '16': ['82204b9c-610c-4975-8e40-e6882ce39118'],
}
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
    testing: bool,
) -> dict[DeviceName, Any]:  # DeviceSet:
    """Create and return objects for all physical devices."""
    if testing:
        drum_16_relays = MockRelay16()
        drum_32_relays = MockRelay32()
        drum_48_relays = CombinedRelayModule(drum_16_relays, drum_32_relays)
        light_relays = MockRelay16()
    else:
        drum_16_relays = NumatoRL160001("/dev/marquee_drums_16")
        drum_32_relays = NumatoRL320001("/dev/marquee_drums_32")
        drum_48_relays = CombinedRelayModule(drum_16_relays, drum_32_relays)
        light_relays = NumatoRL160001("/dev/marquee_lights")
    drums = DrumSet(relays=create_client(drum_48_relays))
    #
    session = requests.Session()
    session.headers = {'hue-application-key': HUE_APPLICATION_KEY}
    session.verify = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    #
    if testing:
        Device.pin_factory = MockFactory()
    #
    LIGHT_TO_RELAY = {
                            l.CP: 10, 
                  l.TL:  6, l.TM:  7, l.TR:  8,
        l.LU:  5,                               l.RT:  9,
        l.LM:  4, l.ML: 10, l.MM: 10, l.MR: 10, l.RM: 12,
        l.LB:  1,                               l.RB: 13,
                  l.BL:  0, l.BM: 15, l.BR: 14,
    }
    INDEX_TO_RELAY = {k.value: v for k, v in LIGHT_TO_RELAY.items()}
    lights = LightSet(
        count=light_config.count,
        relays=create_client(light_relays, INDEX_TO_RELAY),
        mirror=create_client(drum_16_relays, INDEX_TO_RELAY),
        controller_type=HueBridge,
        controller_kwargs=dict(
            ip_address=HUE_IP_ADDRESS,
            bulb_model=Hue_BR30_Enhanced_Color,
            session=session,
            http=http_mock if testing else http,
            bulb_ids=HUE_BULB_IDS,
            zone_ids=HUE_ZONE_IDS,
            groups=HUE_GROUPS,
        ),
        brightness_factor_init=brightness_factor,
        channel_enum=Light,
        speed_factor=speed_factor,
        config=light_config,
    )
    clicker = Clicker(create_client(drum_16_relays, {0: 0, 1: 1}))
    ringer = Ringer(create_client(light_relays, {0: 3}))
    buzzer = Buzzer(create_client(light_relays, {0: 2}))
    return {
        DeviceName.DRUMS: drums, 
        DeviceName.LIGHTS: lights, 
        DeviceName.CLICKER: clicker, 
        DeviceName.RINGER: ringer, 
        DeviceName.BUZZER: buzzer, 
        DeviceName.BUTTON_REAR:
            Button(
                DeviceName.BUTTON_REAR,
                gpiozero.Button(pin=26, bounce_time=0.10, hold_time=10), 
                supports_hold=True,
            ),
        DeviceName.BUTTON_CORDED_A:
            Button(
                DeviceName.BUTTON_CORDED_A,
                gpiozero.Button(pin=3, bounce_time=0.05),
                # signal_number=signal.SIGUSR1,  # type: ignore
            ),
        DeviceName.BUTTON_CORDED_B:
            Button(
                DeviceName.BUTTON_CORDED_B,
                gpiozero.Button(pin=1, bounce_time=0.05),
                # signal_number=signal.SIGUSR2,  # type: ignore
            ),
        DeviceName.BUTTON_CORDED_C:
            Button(
                DeviceName.BUTTON_CORDED_C,
                gpiozero.Button(pin=2, bounce_time=0.05),
                # signal_number=signal.SIGUSR2,  # type: ignore
            ),
        DeviceName.BUTTON_GAME_START:
            LightedButton(
                DeviceName.BUTTON_GAME_START,
                gpiozero.Button(pin=16, bounce_time=0.05),
                relay=create_client(light_relays, {0: 11}),
            ),
        DeviceName.JOYSTICK:
            Joystick(
                name=DeviceName.JOYSTICK,
                up=gpiozero.Button(pin=4, bounce_time=0.05),
                down=gpiozero.Button(pin=17, bounce_time=0.05),
                left=gpiozero.Button(pin=27, bounce_time=0.05),
                right=gpiozero.Button(pin=22, bounce_time=0.05),
            ),
    }

