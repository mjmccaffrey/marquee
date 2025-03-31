"""Marquee Lighted Sign Project - executors"""

from collections.abc import Callable
from signal import SIGUSR1  # type: ignore

from buttons import Button
from dimmers import ShellyDimmer, ShellyProDimmer2PM, RelayOverride, TRANSITION_DEFAULT
from finale import Finale
from gpiozero import Button as _Button  # type: ignore
import modes
from mode_defs import *
import players
from relays import NumatoUSBRelayModule, NumatoRL160001
from sequence_defs import *
from signs import ALL_RELAYS, ALL_OFF, EXTRA_COUNT, Sign

DIMMER_ADDRESSES = [
    '192.168.51.111',
    '192.168.51.112',
    '192.168.51.113',
    '192.168.51.114',
    '192.168.51.115',
]
#   '192.168.51.116',

def create_sign(brightness_factor: float) -> Sign:
    """Creates and returns a Sign object and all associated device objects."""
    dimmers: list[ShellyDimmer] = [
        ShellyProDimmer2PM(index, address)
        for index, address in enumerate(DIMMER_ADDRESSES)
    ]
    relaymodule: NumatoUSBRelayModule = NumatoRL160001("/dev/ttyACM0", ALL_RELAYS)
    buttons = [
        Button('sign_back', _Button(pin=17, bounce_time=0.10), SIGUSR1),
        Button('remote_a', _Button(pin=18, pull_up=False, bounce_time=0.10)),
        Button('remote_b', _Button(pin=23, pull_up=False, bounce_time=0.10)),
        Button('remote_c', _Button(pin=24, pull_up=False, bounce_time=0.10)),
        Button('remote_d', _Button(pin=25, pull_up=False, bounce_time=0.10)),
    ]
    return Sign(
        dimmers=dimmers,
        relaymodule=relaymodule,
        buttons=buttons,
        brightness_factor=brightness_factor,
    )

class Executor():
    """Executes patterns and commands specified on the command line.
       Registers all of the play modes, and if specified on the command line,
       creates and turns control over to a Player object."""

    def __init__(
            self, 
            create_sign: Callable[[float], Sign],
            create_player: Callable[[
                    dict[int, modes.ModeConstructor], 
                    Sign, 
                    float
                ], 
                players.Player
            ],
        ):
        """"""
        self.create_sign = create_sign
        self.create_player = create_player
        self.mode_ids: dict[str, int] = {}
        self.mode_menu: list[tuple[int, str]] = []
        self.modes: dict[int, modes.ModeConstructor] = {}
        self.register_modes()
        self.commands: dict[str, Callable] = {
            'calibrate_dimmers': self.command_calibrate_dimmers,
            'configure_dimmers': self.command_configure_dimmers,
            'off': self.command_off,
        }

    def close(self):
        """Close dependencies."""
        self.player.close()
        self.sign.close()

    def command_calibrate_dimmers(self):
        """Calibrate dimmers."""
        ShellyDimmer.calibrate_all()

    def command_configure_dimmers(self):
        """Configure dimmers."""
        ShellyDimmer.configure_all()

    def command_off(self):
        """Turn off all relays and potentially other devices."""
        self.sign.set_lights(ALL_OFF, '0' * EXTRA_COUNT)
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
        self.mode_menu.append((index, name))
        self.mode_ids[str(index)] = index
        self.mode_ids[name] = index
        assert hidden or ( # !!!!!!!!!!!!!!!!!!!!!!!!!!
                self.mode_ids.get(str(index)) == index
            and self.mode_ids.get(name) == index
        ), "Mode index and / or name do not match registered IDs"
        self.modes[index] = modes.ModeConstructor(name, mode_class, kwargs)

    def add_sequence_mode(
            self,
            index: int, 
            name: str, 
            sequence: Callable,
            pace: tuple[float, ...] | float | None = None,
            override: RelayOverride | None = None,
            **kwargs,
        ):
        """Create a Mode object from a sequence and parameters, and register it."""
        self.add_mode(
            index, 
            name, 
            modes.PlaySequenceMode,
            sequence=sequence,
            pace=pace,
            override=override,
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
        self.sign: Sign = self.create_sign(brightness_factor)
        if command is not None:
            self.execute_command(command)
        elif mode_index is not None:
            self.execute_mode(mode_index, brightness_factor, speed_factor)
        else:
            self.execute_pattern(light_pattern, brightness_pattern)

    def execute_command(self, command: str):
        """Effects the command-line specified command."""
        self.commands[command]()

    def execute_mode(self, mode_index: int, brightness_factor: float, speed_factor: float):
        """Effects the command-line specified mode."""
        self.player = self.create_player(self.modes, self.sign, speed_factor)
        self.player.execute(mode_index)

    def execute_pattern(self, light_pattern: str | None, brightness_pattern: str | None):
        """Effects the command-line specified pattern(s)."""
        if brightness_pattern is not None:
            print(f"Setting dimmers {brightness_pattern}")
            self.sign.set_dimmers(brightness_pattern)
            Button.wait(TRANSITION_DEFAULT)
        if light_pattern is not None:
            print(f"Setting lights {light_pattern}")
            self.sign.set_lights(light_pattern)

    def register_modes(self):
        """Register all operating modes."""
        self.add_mode(0, "selection", modes.SelectMode, hidden=True, previous_mode="PREVIOUS_MODE")
        self.add_sequence_mode(1, "all_on", seq_all_on)
        self.add_sequence_mode(2, "all_off", seq_all_off)
        self.add_sequence_mode(3, "even_on", seq_even_on)
        self.add_sequence_mode(4, "even_off", seq_even_off)
        self.add_sequence_mode(5, "blink_all", seq_blink_all, 
            pace=1,
        )
        self.add_sequence_mode(6, "blink_alternate", seq_blink_alternate, 
            pace=1, 
        )
        self.add_sequence_mode(7, "rotate", seq_rotate, 
            pace=0.5, pattern="1100000000",
        )
        self.add_sequence_mode(8, "random_flip", seq_random_flip, 
            pace=0.5, light_pattern='LIGHT_PATTERN',
        )
        self.add_mode(9, "rapid_fade", RapidFade)  # !!!!!!!!!
        self.add_sequence_mode(10, "blink_alternate_fade",
            seq_blink_alternate, pace=4, 
            override=RelayOverride(
                transition_on=1.0,
                transition_off=3.0,
            )
        )
        self.add_sequence_mode(11, "random_flip_fade", seq_random_flip, pace=2.0,
            override=RelayOverride(),
            light_pattern='LIGHT_PATTERN',
        )
        self.add_sequence_mode(12, "blink_all_fade_seq",
            seq_blink_all, pace=1,
            override=RelayOverride(
                concurrent=False,
                transition_on=0.5,
                transition_off=0.5,
            )
        )
        self.add_sequence_mode(13, "blink_all_fade_con", 
            seq_blink_all, pace=1,
            override=RelayOverride(
                concurrent=True,
                transition_on=0.5,
                transition_off=0.5,
            )
        )
        self.add_sequence_mode(14, "blink_all_fade_fast", 
            seq_blink_all, pace=0.5,
            override=RelayOverride()
        )
        self.add_sequence_mode(15, "blink_all_fade_slowwww", 
            seq_blink_all, pace=10,
            override=RelayOverride(
                brightness_on=100,
                brightness_off=10,
            )
        )
        self.add_sequence_mode(16, "blink_all_fade_stealth", 
            seq_blink_all, pace=(1, 60),
            override=RelayOverride(
                transition_on=2,
                transition_off=2,
            )
        )
        self.add_sequence_mode(17, "corner_rotate_fade", 
            seq_opposite_corner_pairs, pace=5,
            override=RelayOverride(
                concurrent=True,
                brightness_on = 90,
                brightness_off = 10,
            )
        )
        self.add_sequence_mode(18, "rotate_slight_fade",
            seq_rotate, pace=0.5,
            override=RelayOverride(
                concurrent=False,
                brightness_on = 100,
                brightness_off = 30,
            )
        )
        self.add_mode(19, "even_odd_fade", EvenOddFade, pace=2)
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
        self.add_mode(26, "finale", Finale, tempo=90)
