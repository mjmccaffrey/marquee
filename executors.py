"""Marquee Lighted Sign Project - executors"""

from collections.abc import Callable
from signal import SIGUSR1  # type: ignore

from buttons import Button
from buttonsets import ButtonSet
from configuration import (
    ALL_RELAYS, ALL_OFF, DIMMER_ADDRESSES, EXTRA_COUNT, LIGHT_COUNT,
)
from dimmers import ShellyDimmer, ShellyProDimmer2PM, TRANSITION_DEFAULT
from gpiozero import Button as _Button  # type: ignore
from instruments import BellSet, DrumSet
from lights import LightSet
from mode_interface import AutoModeChangeEntry, ModeConstructor
import modes
from mode_defs import (
    BuildBrightness,  EvenOddFade, RotateReversible, RandomFade, RapidFade
)
from relays import NumatoRL160001, NumatoSSR80001
from sequences import (
    all_on, 
    all_off,
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
from specialparams import DimmerParams, SpecialParams

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
        body_back = Button(_Button(pin=26, bounce_time=0.10), SIGUSR1),
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
            index: int, 
            name: str,
            mode_class: type[modes.Mode],
            hidden: bool = False,
            **kwargs,
    ):
        """Register the mode IDs and everything needed to create an instance."""
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
            index: int, 
            name: str, 
            sequence: Callable,
            pace: tuple[float, ...] | float | None = None,
            special: SpecialParams | None = None,
            **kwargs,
        ):
        """Create a Mode object from a sequence and parameters, and register it."""
        self.add_mode(
            index, 
            name, 
            modes.PlaySequenceMode,
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
        print(f"{mode_index=}, {command=}, {light_pattern=}, {brightness_pattern=}")
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
            speed_factor)
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
        self.add_mode(0, "selection", modes.SelectMode, hidden=True, previous_mode="PREVIOUS_MODE")
        self.add_sequence_mode(1, "all_on", all_on)
        self.add_sequence_mode(2, "all_off", all_off)
        self.add_sequence_mode(3, "even_on", even_on)
        self.add_sequence_mode(4, "even_off", even_off)
        self.add_sequence_mode(5, "blink_all", blink_all, 
            pace=1,
        )
        self.add_sequence_mode(6, "blink_alternate", blink_alternate, 
            pace=1, 
        )
        self.add_sequence_mode(7, "rotate", rotate, 
            pace=0.5, pattern="110000000000",
        )
        self.add_sequence_mode(8, "random_flip", random_flip, 
            pace=0.5, light_pattern='LIGHT_PATTERN',
        )
        self.add_mode(9, "rapid_fade", RapidFade)  # !!!!!!!!!
        self.add_sequence_mode(10, "blink_alternate_fade",
            blink_alternate, pace=4, 
            special=DimmerParams(
                transition_on=1.0,
                transition_off=3.0,
            )
        )
        self.add_sequence_mode(11, "random_flip_fade_medium", random_flip, pace=2.0,
            special=DimmerParams(),
            light_pattern='LIGHT_PATTERN',
        )
        self.add_sequence_mode(12, "blink_all_fade_sequen",
            blink_all, pace=1,
            special=DimmerParams(
                concurrent=False,
                transition_on=0.5,
                transition_off=0.5,
            )
        )
        self.add_sequence_mode(13, "blink_all_fade_consec", 
            blink_all, pace=1,
            special=DimmerParams(
                concurrent=True,
                transition_on=0.5,
                transition_off=0.5,
            )
        )
        self.add_sequence_mode(14, "blink_all_fade_fast", 
            blink_all, pace=0.5,
            special=DimmerParams()
        )
        self.add_sequence_mode(15, "blink_all_fade_slowwww", 
            blink_all, pace=10,
            special=DimmerParams(
                brightness_on=100,
                brightness_off=10,
            )
        )
        self.add_sequence_mode(16, "blink_all_fade_stealth", 
            blink_all, pace=(1, 60),
            special=DimmerParams(
                transition_on=2,
                transition_off=2,
            )
        )
        self.add_sequence_mode(17, "corner_rotate_fade", 
            opposite_corner_pairs, pace=5,
            special=DimmerParams(
                concurrent=True,
                brightness_on = 90,
                brightness_off = 10,
            )
        )
        self.add_sequence_mode(18, "rotate_slight_fade",
            rotate, pace=0.5,
            special=DimmerParams(
                concurrent=False,
                brightness_on = 100,
                brightness_off = 30,
            )
        )
        self.add_mode(19, "even_odd_fade", EvenOddFade, pace=0.5)
        self.add_mode(20, "random_fade", RandomFade)
        self.add_mode(21, "random_fade_steady", RandomFade, transition=2)
        self.add_mode(22, "build_brightness_equal", BuildBrightness, equal_trans=True)
        self.add_mode(23, "build_brightness_unequal", BuildBrightness, equal_trans=False)
        self.add_mode(24, "rotate_reversible_1", 
            RotateReversible, pace=0.35, 
            pattern = "1" + "0" * (LIGHT_COUNT - 1))
        self.add_mode(25, "rotate_reversible_2", 
            RotateReversible, pace=0.35, 
            pattern = "0" + "1" * (LIGHT_COUNT - 1))
        self.add_mode(26, "signs", SignsSong)
        self.add_sequence_mode(27, "rotate_sides", rotate_sides, pace=1.0, pattern='1', clockwise=True)
        self.add_sequence_mode(28, "rotate_sides_silent", rotate_sides, pace=2.0, pattern='0', clockwise=False,
            special=DimmerParams(
                brightness_on = 90,
                brightness_off = 10,
                transition_on=1.0,
                transition_off=1.0,
            )
        )
        self.add_sequence_mode(29, "random_flip_fade_fast", random_flip, pace=0.5,
            special=DimmerParams(),
            light_pattern='LIGHT_PATTERN',
        )
        self.add_mode(30, "silent_variety", modes.AutoMode,
            mode_sequence=[
                AutoModeChangeEntry(
                    duration_seconds=60,
                    mode_index=i
                )
                for i in [10, 11, 15, 18, 28, 29]
            ]
        )
