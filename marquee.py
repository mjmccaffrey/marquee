# Marquee Lighted Sign Project - main
# Version 2.0.0 - Mode Selection Button

# Test all modes / functionality
# Look at clearing all the lights before / after

import functools
import time
import types

import button
import relayboard

LIGHT_TO_RELAY = {
    0:  9,
    1: 13,
    2: 14,
    3: 15,
    4:  2,
    5:  1,
    6:  0,
    7:  6,
    8:  7,
    9:  8,
}
LIGHT_COUNT = len(LIGHT_TO_RELAY)
TOP_LIGHTS_LEFT_TO_RIGHT = [9, 0, 1, 2, 3]
BOTTOM_LIGHTS_LEFT_TO_RIGHT = [8, 7, 6, 5, 4]
LIGHTS_CLOCKWISE = [9, 0, 1, 2, 3, 4, 5, 6, 7, 8]

def seq_all_on():
    """All lights on."""
    yield [1] * LIGHT_COUNT

def seq_all_off():
    """All lights off."""
    yield [0] * LIGHT_COUNT

def seq_blink_all():
    """All lights on and then off."""
    yield next(seq_all_on())
    yield next(seq_all_off())

def seq_even_on():
    """Even-numbered lights on; others off."""
    yield [y % 2 for y in range(LIGHT_COUNT)]

def seq_even_off():
    """Even-numbered lights off; others on."""
    yield [(y + 1) % 2 for y in range(LIGHT_COUNT)]

def seq_blink_alternate():
    """Every other light on and then off."""
    yield next(seq_even_on())
    yield next(seq_even_off())

def seq_rotate(pattern=None, clockwise=True):
    """Rotate a pattern of lights counter/clockwise.
       Pattern is a string of length LIGHT_COUNT containing 0 and 1."""
    if pattern is None:
        pattern = [1] + [0] * (LIGHT_COUNT - 1)
    for i in range(LIGHT_COUNT, 0, -1 if clockwise else +1):
        rotated_pattern = pattern[i:] + pattern[:i]
        yield rotated_pattern

def seq_build(from_left=True):
    """Grow the upper and lower rows, 
       starting from the left or the right."""
    if from_left:
        top = TOP_LIGHTS_LEFT_TO_RIGHT
        bot = BOTTOM_LIGHTS_LEFT_TO_RIGHT
    else:  # from right
        top = reversed(TOP_LIGHTS_LEFT_TO_RIGHT)
        bot = reversed(BOTTOM_LIGHTS_LEFT_TO_RIGHT)
    lights = [0] * LIGHT_COUNT
    for t, b in zip(top, bot):
        lights[t], lights[b] = 1, 1
        yield lights

def seq_move(from_left=True):
    """Move lit lights in the upper and lower rows, 
       starting from the left or the right."""
    if from_left:
        top = TOP_LIGHTS_LEFT_TO_RIGHT
        bot = BOTTOM_LIGHTS_LEFT_TO_RIGHT
    else:  # from right
        top = reversed(TOP_LIGHTS_LEFT_TO_RIGHT)
        bot = reversed(BOTTOM_LIGHTS_LEFT_TO_RIGHT)
    for t, b in zip(top, bot):
        yield [int(y in {t, b}) for y in range(LIGHT_COUNT)]

def do_sequence(sequence, count, delay):
    """Execute sequence count times, with delay seconds in between."""
    for _ in range(count):
        simple_mode(sequence, delay)()

def simple_mode(sequence, delay=None):
    """Execute sequence indefinitely, with delay seconds in between.
       Delay=None is an infinite delay, so the sequence should have
       only 1 step."""
    def template():
        while True:
            for s in sequence():
                set_lights(s)
                mode.button.wait(delay)
    return template

def mode_variety_1():
    """Perform a variety of sequences."""
    while True:
        # !!! do_sequence(seq_clockwise, 2, 0.4)
        # !!! do_sequence(seq_counterclockwise, 2, 0.4)
        # !!! do_sequence(seq_blink_all, 44, 2)
        # ??? OR SHOULD THIS SEQUENCE THROUGH THE MODES ???
        # do_sequence(seq_blink_alternate, 4, 0.4)
        do_sequence(functools.partial(seq_rotate, '1000000000'), 4, 0.2)
        do_sequence(functools.partial(seq_rotate, '1100000000'), 4, 0.2)
        do_sequence(functools.partial(seq_rotate, '1101000000'), 4, 0.2)
        do_sequence(functools.partial(seq_rotate, '1101010000'), 4, 0.2)
        do_sequence(functools.partial(seq_rotate, '1101010100'), 4, 0.2)
        do_sequence(functools.partial(seq_rotate, '1111111110'), 4, 0.2)
        # do_sequence(seq_move_left, 10, 0.2)
        # do_sequence(seq_build_left, 10, 0.2)
        mode.button.wait(900)

def indicate_mode_desired():
    """Show user what desired mode number is currently selected."""
    assert MODE_COUNT <= LIGHT_COUNT, "Cannot indicate this many modes"
    lights = [0] * LIGHT_COUNT
    set_lights(lights)
    time.sleep(0.6)
    for t in range(mode.desired):
        time.sleep(0.2)
        lights[LIGHTS_CLOCKWISE[t]] = 1
        set_lights(lights)

def mode_selection():
    """User uses the physical button to select 
       the next mode to execute."""
    while True:
        # Button was pressed
        if mode.desired is None:  # Just now entering selection mode
            mode.desired = mode.previous
            print(f"Desired mode is now {mode.desired}")
        else:
            mode.desired += 1
            if mode.desired == MODE_COUNT:
                mode.desired = 1
            print(f"Desired mode is now {mode.desired}")
        indicate_mode_desired()
        mode.button.reset()
        pressed_again = mode.button.wait(5)
        if not pressed_again:
            mode.current = mode.desired
            print(f"Current mode is now {mode.current}")
            mode.desired = None
            mode.button.reset()
            break

def set_lights(lights):
    """Set all lights per the supplied pattern."""
    relays.set_relays_from_pattern(lights)

def main():
    """Execute Marquee application."""
    global mode
    global relays

    # HACK - give Pi Zero time for relay board to show up during boot
    time.sleep(1)

    relays = relayboard.RelayBoard(LIGHT_TO_RELAY)
    mode = types.SimpleNamespace()
    mode.current = 1
    mode.desired = None
    mode.button = button.Button()

    while True:
        try:
            print(f"Executing mode {mode.current}")
            MODES[mode.current]()
        except button.ButtonPressed:
            print("Button Press Exception Caught")
            if mode.current != 0:
                mode.previous = mode.current
                mode.current = 0

MODES = [
    mode_selection,  # Must be first
    simple_mode(seq_all_on),
    simple_mode(seq_even_on),
    simple_mode(seq_even_off),
    simple_mode(seq_all_off),
    simple_mode(seq_blink_all, 1),
    simple_mode(seq_blink_alternate, 1),
    mode_variety_1,
]
MODE_COUNT = len(MODES)
mode, relays = None, None

if __name__ == "__main__":
    main()
