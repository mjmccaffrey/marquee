""""""

from collections.abc import Callable

from buttons import Button
from dimmers import Dimmer, RelayOverride, TRANSITION_DEFAULT
from modes import Mode, register_mode_ids, register_mode_functions
from players import Player
from relayboards import RelayBoard
from signs import (
    ALL_RELAYS,
    ALL_HIGH, ALL_OFF, ALL_ON, ButtonPressed, 
    EXTRA_COUNT, Sign,
)
DIMMER_ADDRESSES = [
    '192.168.51.111',
    '192.168.51.112',
    '192.168.51.113',
    '192.168.51.114',
    '192.168.51.115',
]
#   '192.168.51.116',

def create_sign() -> Sign:
    """"""
    dimmers: list[Dimmer] = [
        Dimmer(index, address)
        for index, address in enumerate(DIMMER_ADDRESSES)
    ]
    relayboard: RelayBoard = RelayBoard(ALL_RELAYS)
    button = Button('mode_select', 4)
    return Sign(
        dimmers=dimmers,
        relayboard=relayboard,
        button=button,
    )

class Executor():
    """"""

    def __init__(self):
        self.sign = create_sign()
        self.mode_id_to_index: dict[str, int] = {}
        self.modes: dict[int, Mode] = {}
        register_mode_ids(self)
        self.commands = {
            'calibrate_dimmers': self.command_calibrate_dimmers,
            'configure_dimmers': self.command_configure_dimmers,
            'off': self.command_off,
        }

    def close(self):
        """Close."""
        self.player.close()
        self.sign.close()

    def command_calibrate_dimmers(self):
        """Calibrate dimmers."""
        Dimmer.calibrate_all()

    def command_configure_dimmers(self):
        """Configure dimmers."""
        Dimmer.configure_all()

    def command_off(self):
        """Turn off all relays and potentially other devices."""
        self.sign.set_lights(ALL_OFF, '0' * EXTRA_COUNT)
        print("Marquee is now partially shut down.")
        print()

    def add_mode_ids(
            self, 
            index: int, 
            name: str, 
        ):
        """Register the mode, identified by index and name."""
        assert (
                index not in self.modes
            and str(index) not in self.mode_id_to_index 
            and name not in self.mode_id_to_index 
        ), "Duplicate mode index or name"
        assert all(
            k in self.modes for k in range(index)
        ), "Non-sequential mode index"
        self.mode_id_to_index[str(index)] = index
        self.mode_id_to_index[name] = index

    def add_mode_func(
            self, 
            index: int, 
            name: str, 
            function: Callable,
        ):
        self.modes[index] = Mode(
            name=name,
            function=function,
        )
            
    def add_sequence_mode_func(
            self,
            index: int, 
            name: str, 
            sequence: Callable,
            pace: tuple[float, ...] | float | None = None,
            override: RelayOverride | None = None,
        ):
        """"""

        def sequence_doer():
            # If using only dimmers, turn relays on, and vice versa
            if override is not None:
                self.sign.set_lights(ALL_ON)
            else:
                self.sign.set_dimmers(ALL_HIGH)
            while True:
                self.player.do_sequence(sequence,
                    pace=pace,
                    override=override,
                )

        if override is not None:
            default_trans = (
                pace if isinstance(pace, float) else
                TRANSITION_DEFAULT
            )
            if override.transition_off is None:
                override.transition_off = default_trans
            if override.transition_on is None:
                override.transition_on = default_trans
        self.add_mode_func(
            index=index,
            name=name,
            function=sequence_doer
        )

    def execute(
            self, 
            command: str | None = None, 
            mode_index: int | None = None, 
            speed_factor: float | None = None,
            light_pattern: str | None = None, 
            brightness_pattern: str | None = None,
        ):
        """Effects the specified command, mode or pattern(s)."""
        if command is not None:
            self.execute_command(command)
        elif mode_index is not None:
            assert speed_factor is not None
            self.execute_mode(mode_index, speed_factor)
        else:
            self.execute_pattern(light_pattern, brightness_pattern)

    def execute_command(self, command: str):
        """"""
        self.commands[command]()

    def execute_mode(self, mode_index: int, speed_factor: float):
        """"""
        self.player = Player(
            modes=self.modes,
            sign=self.sign, 
            speed_factor=speed_factor,
        )
        register_mode_functions(self)
        self.player.start(mode_index)

    def execute_pattern(self, light_pattern: str | None, brightness_pattern: str | None):
        """"""
        # ??? flip order and remove wait?
        if brightness_pattern is not None:
            print(f"Setting dimmers {brightness_pattern}")
            self.sign.set_dimmers(brightness_pattern)
            self.sign.button_interrupt_wait(TRANSITION_DEFAULT)
        if light_pattern is not None:
            print(f"Setting lights {light_pattern}")
            self.sign.set_lights(light_pattern)
