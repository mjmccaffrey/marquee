"""Marquee Lighted Sign Project - register_modes"""

from executor import Executor
from lightset_misc import LIGHT_COUNT
from modes.background_modes import SequenceBGMode, ModeEntry
from modes.custom_modes import (
    BellTest, EvenOddFade, FillBulbs, RotateReversible, 
    RandomFade, RapidFade, RotateRewind, SilentFadeBuild,
)
from modes.mode_misc import ModeIndex
from modes.select_modes import BrightnessSelectMode, ModeSelectMode
from sequences import (
    all_on, all_off, blink_all, blink_alternate, even_on, even_off,
    rotate, random_flip, rotate_sides,
)
from signs_song import SignsSong
from specialparams import DimmerParams, MirrorParams


def register_modes(exec: Executor) -> None:
    """Register all modes."""
    register_special_modes(exec)
    register_relay_modes(exec)
    # register_interactive_modes(exec)
    register_silent_modes(exec)
    register_test_modes(exec)
    # register_pyohio_2025_presentation_modes(exec)

def register_dimmer_modes(exec: Executor):
    """"""
    exec.add_mode("rapid_fade", RapidFade)
    exec.add_sequence_mode("blink_alternate_medium",
        blink_alternate, delay=4, 
        special=DimmerParams(
            transition_on=1.0,
            transition_off=3.0,
        )
    )
    exec.add_sequence_mode("random_flip_fade_medium", random_flip, delay=2.0,
        special=DimmerParams(),
        light_pattern='LIGHT_PATTERN',
    )
    exec.add_sequence_mode("blink_all_fade_fast", 
        blink_all, delay=0.5,
        special=DimmerParams()
    )
    exec.add_sequence_mode("blink_all_fade_slowwww", 
        blink_all, delay=10,
        special=DimmerParams(
            brightness_on=100,
            brightness_off=5,
            concurrent=False,
        )
    )
    exec.add_sequence_mode("blink_all_fade_stealth", 
        blink_all, delay=(1, 60),
        special=DimmerParams(
            transition_on=2,
            transition_off=2,
        )
    )


    exec.add_sequence_mode("center_rotate_fade", rotate, 
        delay=0.5, pattern = "010" * 4,
    )

    exec.add_mode("even_odd_fade", EvenOddFade, delay=0.5)
    # exec.add_mode("random_fade_steady", RandomFade, transition=2)

    exec.add_mode("rotate_reversible_1", 
        RotateReversible, delay=0.35, 
        pattern = "1" + "0" * (LIGHT_COUNT - 1))
    exec.add_mode("rotate_reversible_2", 
        RotateReversible, delay=0.35, 
        pattern = "0" + "1" * (LIGHT_COUNT - 1))

    exec.add_sequence_mode("rotate_sides", rotate_sides, delay=1.0, pattern='1', clockwise=True)
    exec.add_sequence_mode("rotate_sides_silent", rotate_sides, delay=2.0, pattern='0', clockwise=False,
        special=DimmerParams(
            brightness_on = 90,
            brightness_off = 10,
            transition_on=1.0,
            transition_off=1.0,
        )
    )
    exec.add_mode("rotate_rewind_1", RotateRewind, 
        pattern="100000100000", special=MirrorParams(),
    )


def register_special_modes(exec: Executor) -> None:
    """"""
    exec.add_mode("select_mode", ModeSelectMode, 
        index=ModeIndex.SELECT_MODE, hidden=True,
    )
    exec.add_mode("select_brightness", BrightnessSelectMode, 
        index=ModeIndex.SELECT_BRIGHTNESS, hidden=True,
    )
    exec.add_sequence_mode("all_off", all_off,
        index=ModeIndex.DEFAULT,
    )


def register_relay_modes(exec: Executor) -> None:
    """"""
    exec.add_sequence_mode("all_on", all_on)
    exec.add_sequence_mode("even_on", even_on)
    exec.add_sequence_mode("even_off", even_off)
    exec.add_sequence_mode("blink_all", blink_all, delay=1)
    exec.add_sequence_mode("blink_alternate", blink_alternate, delay=1)
    exec.add_sequence_mode("rotate", rotate, 
        delay=0.5, pattern="110000000000",
    )
    exec.add_sequence_mode("random_flip", random_flip, 
        delay=0.5, light_pattern='LIGHT_PATTERN',
    )


def register_silent_modes(exec: Executor) -> None:
    """"""
    exec.add_sequence_mode("silent_blink_alternate_slow",
        blink_alternate, delay=10, 
        special=DimmerParams(
            transition_on=2.0,
            transition_off=3.0,
        )
    )
    exec.add_sequence_mode("silent_random_flip_medium", random_flip, delay=2.0,
        special=DimmerParams(
            transition_on=2.0,
            transition_off=2.0,
            concurrent=False,
        ),
        light_pattern='LIGHT_PATTERN',
    )
    exec.add_sequence_mode("silent_random_flip_fast", random_flip, delay=0.25,
        special=DimmerParams(),
        light_pattern='LIGHT_PATTERN',
    )
    exec.add_sequence_mode("silent_blink_all_slowwww", 
        blink_all, delay=10,
        special=DimmerParams(
            transition_on=5.0,
            transition_off=5.0,
            brightness_on=100,
            brightness_off=10,
        )
    )
    exec.add_mode("silent_fade_build", 
        SilentFadeBuild,
    )
    exec.add_sequence_mode("silent_rotate_slight_fade",
        rotate, delay=0.5, 
        special=DimmerParams(
            concurrent=False,
            brightness_on = 100,
            brightness_off = 20,
        ),
        pattern='110000000000',
    )
    exec.add_mode("silent_random_steady_trans", RandomFade, transition=0.5)
    exec.add_mode("silent_random_random_trans", RandomFade)

    exec.add_mode("silent_variety_group", SequenceBGMode,
        sequence = [
            ModeEntry("silent_blink_alternate_slow", 60),
            ModeEntry("silent_random_flip_medium", 60),
            ModeEntry("silent_random_flip_fast", 15),
            ModeEntry("silent_blink_all_slowwww", 60),
            ModeEntry("silent_fade_build", 60),
            ModeEntry("silent_rotate_slight_fade", 60),
            ModeEntry("silent_random_steady_trans", 60),
            ModeEntry("silent_random_random_trans", 60),
        ],
    )


def register_test_modes(exec: Executor) -> None:
    """"""
    exec.add_mode("bell_test", BellTest)


def register_pyohio_2025_presentation_modes(exec: Executor) -> None:
    """PyOhio 2025 presentation."""
    exec.add_sequence_mode("section_1", all_off)
    exec.add_mode("fill_bulbs", FillBulbs)
    exec.add_sequence_mode("10_on", lambda: iter(["101111101111"]),
        special=MirrorParams(),
    )
    exec.add_sequence_mode("10_rotate", rotate, 
        pattern="110111110111", delay=1.0, stop=3,
        special=MirrorParams(),
    )
    exec.add_sequence_mode("12_on", all_on,
        special=MirrorParams(),
    )
    exec.add_sequence_mode("rotate_sides", rotate_sides, 
        delay=0.75, pattern='1', clockwise=False,
        special=MirrorParams(),
    )
    exec.add_sequence_mode("section_2", all_off)
    exec.add_mode("12_random_random_trans", RandomFade)
    exec.add_sequence_mode("blink_all_fade_sequential",
        blink_all, delay=1,
        special=DimmerParams(concurrent=False),
    )
    exec.add_sequence_mode("blink_all_fade_consecutive", 
        blink_all, delay=1,
        special=DimmerParams(concurrent=True),
    )
    exec.add_sequence_mode("section_3", all_off)
    exec.add_mode("signs", SignsSong, special=DimmerParams())
    exec.add_sequence_mode("section_4", all_off)

