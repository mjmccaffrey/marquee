"""Marquee Lighted Sign Project - main"""

# Video of variety with steady cam 
# Rs232
# Modify back cover
# Picture with back cover
# Paint touch-up w/ brush?
# Video to kevin and paul
# Test cleanup

import functools as ft
import signal
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
    if clockwise:
        light_range = range(LIGHT_COUNT, 0, -1)
    else:  # counterclockwise
        light_range = range(0, LIGHT_COUNT, 1)
    for i in light_range:
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

def do_sequence(sequence, count, delay, stop=None):
    """Execute sequence count times, with delay seconds in between."""
    for _ in range(count):
        for i, s in enumerate(sequence()):
            if stop is not None and i == stop:
                break
            set_lights(s)
            mode.button.wait(delay)

def simple_mode(sequence, delay=None):
    """Execute sequence indefinitely, with delay seconds in between.
       Delay=None is an infinite delay, so the sequence should have
       only 1 step."""
    def template():
        while True:
            do_sequence(sequence, 1, delay)
    return template

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
        else:
            mode.desired += 1
            if mode.desired == MODE_COUNT:
                mode.desired = 1
        indicate_mode_desired()
        mode.button.reset()
        pressed_again = mode.button.wait(5)
        if not pressed_again:
            mode.current = mode.desired
            mode.desired = None
            mode.button.reset()
            break

def set_lights(lights):
    """Set all lights per the supplied pattern."""
    relays.set_relays_from_pattern(lights)

def virtual_button_pressed(_, __):
    """Respond to receiving signal SIGUSR1 as if the physical
       button was pushed. Would be better if this raised a 
       unique exception, allowing for cleaner handling."""
    raise button.ButtonPressed

def setup():
    """Prepare devices and initial state."""
    global relays
    global mode
    relays = relayboard.RelayBoard(LIGHT_TO_RELAY)
    mode = types.SimpleNamespace()
    mode.current = 1
    mode.desired = None
    mode.button = button.Button()
    signal.signal(signal.SIGUSR1, virtual_button_pressed)

def execute():
    """Outermost application loop."""
    while True:
        try:
            MODES[mode.current]()
        except button.ButtonPressed:
            if mode.current != 0:
                mode.previous = mode.current
                mode.current = 0

def cleanup():
    """Close devices."""
    mode.button.close()
    relays.close()

def main():
    """Execute Marquee application."""
    # HACK - give Pi Zero time for relay board to show up during boot
    time.sleep(1)
    #
    setup()
    execute()
    cleanup()

MODES = [
    mode_selection, # Must be first
    simple_mode(seq_all_on),
    simple_mode(seq_even_on),
    simple_mode(seq_even_off),
    simple_mode(seq_all_off),
    simple_mode(seq_blink_all, 1),
    simple_mode(seq_blink_alternate, 1),
    mode_variety_1,
]
MODE_COUNT = len(MODES)
relays = None
mode = None

if __name__ == "__main__":
    main()
