"""Marquee Lighted Sign Project - register_modes"""

from basemode import AutoMode
from configuration import LIGHT_COUNT
from definitions import DimmerParams, MirrorParams
from executors import Executor
from modes import SelectMode
from custom_modes import (
    BellTest, BuildBrightness, EvenOddFade, FillBulbs, RotateReversible, 
    RandomFade, RapidFade, RotateRewind, SilentFadeBuild,
)
from sequences import (
    all_on, 
    all_off,
    blink_all,
    blink_alternate,
    rotate,
    random_flip,
    rotate_sides,
)
from signs_song import SignsSong

def register_modes(exec: Executor):
    """Register all operating modes."""
    exec.add_mode("selection", SelectMode, 
        hidden=True, special=MirrorParams(),
        previous_mode="PREVIOUS_MODE",
    )
    # exec.add_sequence_mode("all_on", all_on)
    # exec.add_sequence_mode("all_off", all_off)
    # exec.add_sequence_mode("even_on", even_on)
    # exec.add_sequence_mode("even_off", even_off)
    # exec.add_sequence_mode("blink_all", blink_all, pace=1)
    # exec.add_sequence_mode("blink_alternate", blink_alternate, 
    #     pace=1, 
    # )
    # exec.add_sequence_mode("rotate", rotate, 
    #     pace=0.5, pattern="110000000000",
    # )
    # exec.add_sequence_mode("random_flip", random_flip, 
    #     pace=0.5, light_pattern='LIGHT_PATTERN',
    # )
    # exec.add_mode("rapid_fade", RapidFade)  # !!!!!!!!!
    # exec.add_sequence_mode("blink_alternate_fade",
    #     blink_alternate, pace=4, 
    #     special=DimmerParams(
    #         transition_on=1.0,
    #         transition_off=3.0,
    #     )
    # )
    # exec.add_sequence_mode("random_flip_fade_medium", random_flip, pace=2.0,
    #     special=DimmerParams(),
    #     light_pattern='LIGHT_PATTERN',
    # )
    # exec.add_sequence_mode("blink_all_fade_fast", 
    #     blink_all, pace=0.5,
    #     special=DimmerParams()
    # )
    # exec.add_sequence_mode("blink_all_fade_slowwww", 
    #     blink_all, pace=10,
    #     special=DimmerParams(
    #         brightness_on=100,
    #         brightness_off=10,
    #     )
    # )
    # exec.add_sequence_mode("blink_all_fade_stealth", 
    #     blink_all, pace=(1, 60),
    #     special=DimmerParams(
    #         transition_on=2,
    #         transition_off=2,
    #     )
    # )
    # exec.add_sequence_mode("corner_rotate_fade", 
    #     opposite_corner_pairs, pace=5,
    #     special=DimmerParams(
    #         concurrent=True,
    #         brightness_on = 90,
    #         brightness_off = 10,
    #     )
    # )
    # exec.add_sequence_mode("rotate_slight_fade",
    #     rotate, pace=0.5,
    #     special=DimmerParams(
    #         concurrent=False,
    #         brightness_on = 100,
    #         brightness_off = 30,
    #     )
    # )
    # exec.add_mode("even_odd_fade", EvenOddFade, pace=0.5)
    # exec.add_mode("random_fade_steady", RandomFade, transition=2)
    # exec.add_mode("build_brightness_equal", BuildBrightness, equal_trans=True)
    # exec.add_mode("build_brightness_unequal", BuildBrightness, equal_trans=False)
    # exec.add_mode("rotate_reversible_1", 
    #     RotateReversible, pace=0.35, 
    #     pattern = "1" + "0" * (LIGHT_COUNT - 1))
    # exec.add_mode("rotate_reversible_2", 
    #     RotateReversible, pace=0.35, 
    #     pattern = "0" + "1" * (LIGHT_COUNT - 1))
    # exec.add_sequence_mode("rotate_sides", rotate_sides, pace=1.0, pattern='1', clockwise=True)
    # exec.add_sequence_mode("rotate_sides_silent", rotate_sides, pace=2.0, pattern='0', clockwise=False,
    #     special=DimmerParams(
    #         brightness_on = 90,
    #         brightness_off = 10,
    #         transition_on=1.0,
    #         transition_off=1.0,
    #     )
    # )
    # exec.add_sequence_mode("random_flip_fade_fast", random_flip, pace=0.5,
    #     special=DimmerParams(),
    #     light_pattern='LIGHT_PATTERN',
    # )
    # exec.add_mode("rotate_rewind_1", RotateRewind, 
    #     pattern="100000100000", special=MirrorParams(),
    # )

    # ********** SILENT SIGN **********
    exec.add_sequence_mode("silent_blink_alternate_slow",
        blink_alternate, pace=10, 
        special=DimmerParams(
            transition_on=2.0,
            transition_off=3.0,
        )
    )
    exec.add_sequence_mode("silent_random_flip_medium", random_flip, pace=2.0,
        special=DimmerParams(
            transition_on=2.0,
            transition_off=2.0,
        ),
        light_pattern='LIGHT_PATTERN',
    )
    exec.add_sequence_mode("silent_random_flip_fast", random_flip, pace=0.25,
        special=DimmerParams(),
        light_pattern='LIGHT_PATTERN',
    )
    exec.add_sequence_mode("silent_blink_all_slowwww", 
        blink_all, pace=10,
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
        rotate, pace=0.5, 
        special=DimmerParams(
            concurrent=False,
            brightness_on = 100,
            brightness_off = 20,
        ),
        pattern='110000000000',
    )
    exec.add_mode("silent_random_steady_trans", RandomFade, transition=0.5)
    exec.add_mode("silent_random_random_trans", RandomFade)

    exec.add_mode("bell_test", BellTest)

    # ********** PRESENTATION **********
    exec.add_sequence_mode("section_1", all_off)
    exec.add_mode("fill_bulbs", FillBulbs)
    exec.add_sequence_mode("10_on", lambda: iter(["101111101111"]),
        special=MirrorParams(),
    )
    exec.add_sequence_mode("10_rotate", rotate, 
        pattern="110111110111", pace=1.0, stop=3, post_delay=None,
        special=MirrorParams(),
    )
    exec.add_sequence_mode("12_on", all_on,
        special=MirrorParams(),
    )
    exec.add_sequence_mode("rotate_sides", rotate_sides, 
        pace=0.75, pattern='1', clockwise=False,
        special=MirrorParams(),
    )
    exec.add_sequence_mode("section_2", all_off)
    exec.add_mode("12_random_random_trans", RandomFade)
    exec.add_sequence_mode("blink_all_fade_sequential",
        blink_all, pace=1,
        special=DimmerParams(concurrent=False),
    )
    exec.add_sequence_mode("blink_all_fade_consecutive", 
        blink_all, pace=1,
        special=DimmerParams(concurrent=True),
    )
    exec.add_sequence_mode("section_3", all_off)
    exec.add_mode("signs", SignsSong, special=DimmerParams())
    exec.add_sequence_mode("section_4", all_off)

    # ********** SILENT SIGN **********
    AutoMode.init(default_duration=60, mode_lookup=exec.mode_ids)
    exec.add_mode("silent_variety_group", AutoMode,
        modes=[
            AutoMode.add("silent_blink_alternate_slow"),
            AutoMode.add("silent_random_flip_medium"),
            AutoMode.add("silent_random_flip_fast", 15.0),
            AutoMode.add("silent_blink_all_slowwww"),
            AutoMode.add("silent_fade_build"),
            AutoMode.add("silent_rotate_slight_fade"),
            AutoMode.add("silent_random_steady_trans"),
            AutoMode.add("silent_random_random_trans"),
        ],
    )
