"""Marquee Lighted Sign Project - executors"""

from collections.abc import Callable
from itertools import chain
from signal import SIGUSR1  # type: ignore

from gpiozero import Button as _Button  # type: ignore

from basemode import AutoMode, BaseMode
from buttons import Button
from buttonsets import ButtonSet
from configuration import (
    ALL_RELAYS, ALL_OFF, DIMMER_ADDRESSES, EXTRA_COUNT, LIGHT_COUNT,
)
from definitions import (
    DimmerParams, MirrorParams, SpecialParams, 
    AutoModeEntry, ModeConstructor,
)
from dimmers import ShellyDimmer, ShellyProDimmer2PM, TRANSITION_DEFAULT
from instruments import BellSet, DrumSet
from lightsets import LightSet
from modes import PlaySequenceMode, SelectMode
from custom_modes import (
    BellTest, BuildBrightness,  EvenOddFade, RotateReversible, 
    RandomFade, RapidFade, RotateRewind, SilentFadeBuild,
)
from relays import NumatoRL160001, NumatoSSR80001
from sequences import (
    all_on, 
    all_off,
    build,
    even_on,
    even_off,
    blink_all,
    blink_alternate,
    rotate,
    random_flip,
    opposite_corner_pairs,
    rotate_sides,
)
from signs_song import SignsSong

def setup_devices(brightness_factor: float):
    """"""
    bells = BellSet(
        NumatoSSR80001("/dev/ttyACM1")
    )
    drums = DrumSet(
        NumatoRL160001("/dev/ttyACM0")
    )
    lights = LightSet(
        relays = NumatoRL160001(
            "/dev/ttyACM2",
            ALL_RELAYS,
        ),
        dimmers = [
            ShellyProDimmer2PM(i, ip)
            for i, ip in enumerate(DIMMER_ADDRESSES)
        ],
        brightness_factor=brightness_factor,
    )
    buttons = ButtonSet(
        body_back = Button(
            _Button(pin=26, bounce_time=0.10, hold_time=10), 
            support_hold=True,
            signal_number=SIGUSR1,
        ),
        remote_a = Button(_Button(pin=18, pull_up=False, bounce_time=0.10)),
        remote_b = Button(_Button(pin=23, pull_up=False, bounce_time=0.10)),
        remote_c = Button(_Button(pin=24, pull_up=False, bounce_time=0.10)),
        remote_d = Button(_Button(pin=25, pull_up=False, bounce_time=0.10)),
    )
    return bells, buttons, drums, lights

class Executor():
    """Executes patterns and commands specified on the command line.
       Registers all of the play modes, and if specified on the command line,
       creates and turns control over to a Player object."""

    def __init__(
            self,
            create_player: Callable,
            setup_devices: Callable,
        ):
        """"""
        self.create_player = create_player
        self.setup_devices = setup_devices
        self.mode_ids: dict[str, int] = {}
        self.mode_menu: list[tuple[int, str]] = []
        self.modes: dict[int, ModeConstructor] = {}
        self.register_modes()
        self.commands: dict[str, Callable] = {
            'calibrate_dimmers': self.command_calibrate_dimmers,
            'off': self.command_off,
        }

    def close(self):
        """Close dependencies."""
        self.player.close()
        # !!! close devices

    def command_calibrate_dimmers(self):
        """Calibrate dimmers."""
        ShellyDimmer.calibrate_all()

    def command_off(self):
        """Turn off all relays and potentially other devices."""
        self.lights.set_relays(ALL_OFF, '0' * EXTRA_COUNT)
        print("Marquee hardware is now partially shut down.")
        print()

    def add_mode(
            self, 
            name: str,
            mode_class: type[BaseMode],
            hidden: bool = False,
            **kwargs,
    ):
        """Register the mode IDs and everything needed to create an instance."""
        index = len(self.modes)
        assert (str(index) not in self.mode_ids
            and name not in self.mode_ids
        ), "Duplicate mode index or name"
        assert all(
            str(k) in self.mode_ids for k in range(1, index)
        ), "Non-sequential mode index"
        if not hidden:
            self.mode_menu.append((index, name))
            self.mode_ids[str(index)] = index
            self.mode_ids[name] = index
        self.modes[index] = ModeConstructor(name, mode_class, kwargs)

    def add_sequence_mode(
            self,
            name: str, 
            sequence: Callable,
            pace: tuple[float, ...] | float | None = None,
            special: SpecialParams | None = None,
            **kwargs,
        ):
        """Create a Mode object from a sequence and parameters, and register it."""
        self.add_mode(
            name, 
            PlaySequenceMode,
            sequence=sequence,
            pace=pace,
            special=special,
            **kwargs,
        )

    def execute(
            self, 
            command: str | None = None, 
            mode_index: int | None = None, 
            brightness_factor: float = 1.0,
            speed_factor: float = 1.0,
            light_pattern: str | None = None, 
            brightness_pattern: str | None = None,
        ):
        """Effects the command-line specified command, mode or pattern(s)."""
        self.bells, self.buttons, self.drums, self.lights = (
            setup_devices(brightness_factor)
        )
        if command is not None:
            self.execute_command(command)
        elif mode_index is not None:
            self.execute_mode(mode_index, speed_factor)
        else:
            self.execute_pattern(light_pattern, brightness_pattern)

    def execute_command(self, command: str):
        """Effects the command-line specified command."""
        self.commands[command]()

    def execute_mode(self, mode_index: int, speed_factor: float):
        """Effects the command-line specified mode."""
        self.player = self.create_player(
            self.modes, 
            self.bells,
            self.buttons,
            self.drums,
            self.lights,
            speed_factor,
        )
        self.player.execute(mode_index)

    def execute_pattern(self, light_pattern: str | None, brightness_pattern: str | None):
        """Effects the command-line specified pattern(s)."""
        if brightness_pattern is not None:
            self.lights.set_dimmers(brightness_pattern)
            Button.wait(TRANSITION_DEFAULT)
        if light_pattern is not None:
            self.lights.set_relays(light_pattern)

    def register_modes(self):
        """Register all operating modes."""
        self.add_mode("selection", SelectMode, 
            hidden=True, special=MirrorParams(),
            previous_mode="PREVIOUS_MODE",
        )
        self.add_sequence_mode("all_on", all_on)
        self.add_sequence_mode("all_off", all_off)
        self.add_sequence_mode("even_on", even_on)
        self.add_sequence_mode("even_off", even_off)
        self.add_sequence_mode("blink_all", blink_all, 
            pace=1,
            special=MirrorParams(),
        )
        self.add_sequence_mode("blink_alternate", blink_alternate, 
            pace=1, 
        )
        self.add_sequence_mode("rotate", rotate, 
            pace=0.5, pattern="110000000000",
        )
        self.add_sequence_mode("random_flip", random_flip, 
            pace=0.5, light_pattern='LIGHT_PATTERN',
        )
        self.add_mode("rapid_fade", RapidFade)  # !!!!!!!!!
        self.add_sequence_mode("blink_alternate_fade",
            blink_alternate, pace=4, 
            special=DimmerParams(
                transition_on=1.0,
                transition_off=3.0,
            )
        )
        self.add_sequence_mode("random_flip_fade_medium", random_flip, pace=2.0,
            special=DimmerParams(),
            light_pattern='LIGHT_PATTERN',
        )
        self.add_sequence_mode("blink_all_fade_sequen",
            blink_all, pace=1,
            special=DimmerParams(
                concurrent=False,
                transition_on=0.5,
                transition_off=0.5,
            )
        )
        self.add_sequence_mode("blink_all_fade_consec", 
            blink_all, pace=1,
            special=DimmerParams(
                concurrent=True,
                transition_on=0.5,
                transition_off=0.5,
            )
        )
        self.add_sequence_mode("blink_all_fade_fast", 
            blink_all, pace=0.5,
            special=DimmerParams()
        )
        self.add_sequence_mode("blink_all_fade_slowwww", 
            blink_all, pace=10,
            special=DimmerParams(
                brightness_on=100,
                brightness_off=10,
            )
        )
        self.add_sequence_mode("blink_all_fade_stealth", 
            blink_all, pace=(1, 60),
            special=DimmerParams(
                transition_on=2,
                transition_off=2,
            )
        )
        self.add_sequence_mode("corner_rotate_fade", 
            opposite_corner_pairs, pace=5,
            special=DimmerParams(
                concurrent=True,
                brightness_on = 90,
                brightness_off = 10,
            )
        )
        self.add_sequence_mode("rotate_slight_fade",
            rotate, pace=0.5,
            special=DimmerParams(
                concurrent=False,
                brightness_on = 100,
                brightness_off = 30,
            )
        )
        self.add_mode("even_odd_fade", EvenOddFade, pace=0.5)
        self.add_mode("random_fade", RandomFade)
        self.add_mode("random_fade_steady", RandomFade, transition=2)
        self.add_mode("build_brightness_equal", BuildBrightness, equal_trans=True)
        self.add_mode("build_brightness_unequal", BuildBrightness, equal_trans=False)
        self.add_mode("rotate_reversible_1", 
            RotateReversible, pace=0.35, 
            pattern = "1" + "0" * (LIGHT_COUNT - 1))
        self.add_mode("rotate_reversible_2", 
            RotateReversible, pace=0.35, 
            pattern = "0" + "1" * (LIGHT_COUNT - 1))
        self.add_mode("signs", SignsSong)
        self.add_sequence_mode("rotate_sides", rotate_sides, pace=1.0, pattern='1', clockwise=True)
        self.add_sequence_mode("rotate_sides_silent", rotate_sides, pace=2.0, pattern='0', clockwise=False,
            special=DimmerParams(
                brightness_on = 90,
                brightness_off = 10,
                transition_on=1.0,
                transition_off=1.0,
            )
        )
        self.add_sequence_mode("random_flip_fade_fast", random_flip, pace=0.5,
            special=DimmerParams(),
            light_pattern='LIGHT_PATTERN',
        )
        self.add_mode("silent_variety", AutoMode,
            mode_sequence=[
                AutoModeEntry(
                    duration_seconds=(d or 30),
                    mode_index=i,
                )
                for i, d in [
                    (37, None),
                    (38, None),
                    (39, None),
                    (31, 15),
                    (32, None),
                    (33, None),
                    (34, 15),
                    (35, None),
                    (36, None),
                ]
            ],
        )
        self.add_sequence_mode("silent_blink_alternate_slow",
            blink_alternate, pace=10, 
            special=DimmerParams(
                transition_on=2.0,
                transition_off=3.0,
            )
        )
        self.add_sequence_mode("silent_random_flip_medium", random_flip, pace=2.0,
            special=DimmerParams(
                transition_on=2.0,
                transition_off=2.0,
            ),
            light_pattern='LIGHT_PATTERN',
        )
        self.add_sequence_mode("silent_random_flip_fast", random_flip, pace=0.25,
            special=DimmerParams(),
            light_pattern='LIGHT_PATTERN',
        )
        self.add_sequence_mode("silent_blink_all_slowwww", 
            blink_all, pace=10,
            special=DimmerParams(
                transition_on=5.0,
                transition_off=5.0,
                brightness_on=100,
                brightness_off=10,
            )
        )
        self.add_mode("silent_fade_build", 
            SilentFadeBuild,
        )
        self.add_sequence_mode("silent_rotate_slight_fade",
            rotate, pace=0.5, 
            special=DimmerParams(
                concurrent=False,
                brightness_on = 100,
                brightness_off = 20,
            ),
            pattern='110000000000',
        )
        self.add_sequence_mode("silent_random_flip_fade_fast", 
            random_flip, pace=0.5,
            special=DimmerParams(),
            light_pattern='LIGHT_PATTERN',
        )
        self.add_mode("silent_random_steady_trans", RandomFade, transition=0.5)
        self.add_mode("silent_random_random_trans", RandomFade)
        self.add_mode("bell_test", BellTest)
        self.add_mode("rotate_rewind_1", RotateRewind, 
            pattern="100000100000", special=MirrorParams(),
        )
        self.add_sequence_mode("ten_on", lambda: (p for p in ["101111101111"]))
        self.add_sequence_mode("ten_rotate", rotate, 
            pattern="101111101111", pace=(1.0, 1.0, 1.0, 999), stop=3)
        self.add_sequence_mode("twelve_on", all_on)
        