"""Marquee Lighted Sign Project - device_defs"""

import signal

import gpiozero

from devices.bulb import (
    Hue_BR30_Enhanced_Color, 
    Sylvania_G25_Frosted_40,
)
from devices.button import Button, LightedButton
from devices.controlset import ControlSet
from devices.devices_misc import Control, Device, DeviceSet
from devices.hue import HueBridge
from devices.joystick import Joystick
from devices.numato import NumatoRL320001, NumatoRL160001
from devices.relaymodule import CombinedRelayModule, create_client
from devices.shelly import ShellyController, ShellyProDimmer2PM
from instruments import Buzzer, ClickSet, DrumSet, LightSet, Ringer
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
HUE_BULB_IDS_2 = HUE_BULB_IDS_0 + HUE_BULB_IDS_1

HUE_GROUPS_0: dict[str, list[int]] = {
    'top': LIGHTS_TOP,
    'right': LIGHTS_RIGHT,
    'bottom': LIGHTS_BOTTOM,
    'left': LIGHTS_LEFT,
    'even': [0, 2, 4, 6, 8, 10],
    'odd': [1, 3, 5, 7, 9, 11],
    '12': LIGHTS_CLOCKWISE,
    '13': LIGHTS_CLOCKWISE + [Light.CP]
}
HUE_ZONE_IDS_0: dict[str, list[str]] = {
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
    'even': ['166bcc4f-9598-49e7-b853-a239be50b514'],
    'odd': ['587dddb8-bec3-4555-9f3b-b12b2fca918d'],
    '12': ['21c66184-6be0-4c79-832e-9308ee4501eb'],
    '13': ['af193689-f8a4-4ace-9cef-87264c9f5129'],
}
HUE_GROUPS_1 = {
    'middle': [0, 1, 2],
}
HUE_ZONE_IDS_1 = {
    'middle': ['1afc2cc8-cbf8-484b-b2d6-46575b2cef97'],
}
HUE_GROUPS_2 = HUE_GROUPS_0 | {
    'middle': [12, 13, 14],
    '15': range(15),
    '16': range(16),
}
HUE_ZONE_IDS_2 = HUE_ZONE_IDS_0 | {
    'middle': ['1afc2cc8-cbf8-484b-b2d6-46575b2cef97'],
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


def controls(light_relays: NumatoRL160001) -> ControlSet:
    """Define control set."""
    return ControlSet(
        body_back = Button(
            Control.BODY_BACK,
            gpiozero.Button(pin=26, bounce_time=0.10, hold_time=10), 
            supports_hold=True,
        ),
        corded_a = Button(
            Control.CORDED_A,
            gpiozero.Button(pin=2, bounce_time=0.05),
            signal_number=signal.SIGUSR1,  # type: ignore
        ),
        corded_b = Button(
            Control.CORDED_B,
            gpiozero.Button(pin=3, bounce_time=0.05),
            signal_number=signal.SIGUSR2,  # type: ignore
        ),
        corded_c = Button(
            Control.CORDED_C,
            gpiozero.Button(pin=18, bounce_time=0.05),
            signal_number=signal.SIGFPE,  # type: ignore
        ),
        game_start = LightedButton(
            Control.GAME_START,
            gpiozero.Button(pin=16, bounce_time=0.05),
            relay=create_client(light_relays, BUTTON_TO_RELAY),
        ),
    )


def joystick() -> Joystick:
    """Define joystick."""
    return Joystick(
        up=gpiozero.Button(pin=4, bounce_time=0.05),
        down=gpiozero.Button(pin=17, bounce_time=0.05),
        left=gpiozero.Button(pin=27, bounce_time=0.05),
        right=gpiozero.Button(pin=22, bounce_time=0.05),
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
        channel_enum=Light,
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
        channel_enum=Extra,
        speed_factor=speed_factor,
    )
    combined = LightSet(
        count=16,
        relays=create_client(light_relays, COMBINED_TO_RELAY),
        mirror=create_client(drum_16_relays, COMBINED_TO_RELAY),
        controller_type=HueBridge,
        controller_kwargs=dict(
            application_key=HUE_APPLICATION_KEY,
            ip_address=HUE_IP_ADDRESS,
            bulb_model=Hue_BR30_Enhanced_Color,
            bulb_ids=HUE_BULB_IDS_2,
            zone_ids=HUE_ZONE_IDS_2,
            groups=HUE_GROUPS_2,
            channel_sources=(lights, extra),
        ),
        brightness_factor_init=brightness_factor,
        channel_enum=Combined,
        speed_factor=speed_factor,
    )
    clicker = ClickSet(create_client(drum_16_relays, CLICK_TO_RELAY))
    ringer = Ringer(create_client(light_relays, RINGER_TO_RELAY))
    buzzer = Buzzer(create_client(light_relays, BUZZER_TO_RELAY))
    return {
        Device.CONTROLS: controls(light_relays),
        Device.DRUMS: drums, 
        Device.LIGHTS: lights, 
        Device.EXTRA: extra, 
        Device.COMBINED: combined, 
        Device.CLICKER: clicker, 
        Device.RINGER: ringer, 
        Device.BUZZER: buzzer, 
        Device.JOYSTICK: joystick(), 
    }


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
        channel_enum=Light,
        speed_factor=speed_factor,
    )
    extra = None
    clicker = ClickSet(create_client(light_relays, CLICK_TO_RELAY))
    ringer = Ringer(create_client(light_relays, RINGER_TO_RELAY))
    buzzer = Buzzer(create_client(light_relays, BUZZER_TO_RELAY))
    return {
        Device.CONTROLS: controls(light_relays),
        Device.DRUMS: drums, 
        Device.LIGHTS: lights, 
        Device.CLICKER: clicker, 
        Device.RINGER: ringer, 
        Device.BUZZER: buzzer, 
        Device.JOYSTICK: joystick(), 
    }

BUTTON_TO_RELAY = {0: 11}
RINGER_TO_RELAY = {0: 3}
BUZZER_TO_RELAY = {0: 2}
EXTRA_TO_RELAY = {0: 10, 1: 10, 2: 10, 3: 10}  # Kludge.

COMBINED_TO_RELAY = (
    LIGHT_TO_RELAY | {12: 10, 13: 10, 14: 10, 15: 10}  # Kludge.
)
CLICK_TO_RELAY = {0: 0, 1: 1}

