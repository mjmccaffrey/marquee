# Marquee Lighted Sign Project - main
# Version 2.0.0 - Mode Selection Button

# ??? ADD A CHANGELOG?
# !!! remove debug stmts
# Future: 
# all sequences as modes?  all modes, including 0, to not exit prematurely, 
# when mode selection initiated, start at current mode?
# !!! PEP8 !!!

import functools
import time
import types

import button
import relayboard

LIGHT_COUNT = 10
RELAY_COUNT = 16
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
RELAY_TO_LIGHT = {v: k for k, v in LIGHT_TO_RELAY.items()}
TOP_LIGHTS_LEFT_TO_RIGHT = [9, 0, 1, 2, 3]
BOTTOM_LIGHTS_LEFT_TO_RIGHT = [8, 7, 6, 5, 4]

def seq_rotate(pattern = None, clockwise = True):
    if pattern is None:
        pattern = [1] + [0] * (LIGHT_COUNT - 1)
    for i in range(LIGHT_COUNT, 0, -1 if clockwise else +1):
        rotated_pattern = pattern[i:] + pattern[:i]
        yield rotated_pattern

def seq_blink_all():
    """All lights on and then off."""
    yield [1] * LIGHT_COUNT
    yield [0] * LIGHT_COUNT

def seq_blink_alternate():
    """Every other light on and then off."""
    yield [y % 2 for y in range(LIGHT_COUNT)]
    yield [(y + 1) % 2 for y in range(LIGHT_COUNT)]

def seq_build(from_left = True):
    """Grow the upper and lower rows, 
       starting from the left or the right."""
    lights = [0] * LIGHT_COUNT
    yield lights  # ???? SHOULD OTHERS DO THIS AS WELL ?????
    if from_left:
        top = TOP_LIGHTS_LEFT_TO_RIGHT
        bot = BOTTOM_LIGHTS_LEFT_TO_RIGHT
    else:  # from right
        top = reversed(TOP_LIGHTS_LEFT_TO_RIGHT)
        bot = reversed(BOTTOM_LIGHTS_LEFT_TO_RIGHT)
    for t, b in zip(top, bot):
        lights[t], lights[b] = 1, 1
        yield lights

def seq_move(from_left = True):
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
        for s in sequence():
            set_lights(s)
            mode.button.wait(delay)

def mode_variety():
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
        mode_half_on()
        mode.button.wait(900)

def mode_all_on():
    """All of the lights on, with no animation."""
    set_lights([1] * LIGHT_COUNT)
    mode.button.wait()

def mode_all_off():
    """All of the lights off, with no animation."""
    set_lights([0] * LIGHT_COUNT)
    mode.button.wait()

def mode_half_on():
    """Every other light on, with no animation."""
    set_lights([(i + 1) % 2 for i in range(LIGHT_COUNT)])
    mode.button.wait()

def mode_blink_alternate():
    """Wrapper around seq_blink_alternate."""
    # !!!!! Use this as factory for any mode from seq ???
    while True:
        do_sequence(seq_blink_alternate, 10, 0.4)

def indicate_mode_desired():
    """Show user what desired mode number is currently selected."""
    lights = [0] * LIGHT_COUNT
    set_lights(lights)
    time.sleep(0.6)
    for t in range(mode.desired):
        time.sleep(0.2)
        lights[TOP_LIGHTS_LEFT_TO_RIGHT[t]] = 1
        set_lights(lights)

def mode_selection():
    """User uses the physical button to select 
       the next mode to execute."""
    mode.button.wait(5)
    if mode.button.just_pressed():
        if mode.desired is None:
            mode.desired = mode.previous
            print(f"Desired mode is now {mode.desired}")
        else:
            mode.desired += 1
            if mode.desired == MODE_COUNT:
                mode.desired = 1
            print(f"Desired mode is now {mode.desired}")
        indicate_mode_desired()
    else:
        mode.current = mode.desired
        print (f"Current mode is now {mode.current}")
        mode.desired = None
        print(f"Desired mode is now {mode.desired}")
    mode.button.reset()

def lights_to_relays(light_pattern):
    # !! This could probably use optimizing !!
    relay_pattern = [0] * RELAY_COUNT
    for i, l in enumerate(light_pattern):
        relay_pattern[RELAY_COUNT - 1 - LIGHT_TO_RELAY[i]] = l
    val = hex(int(''.join(str(e) for e in relay_pattern), 2))[2:]
    return f"{val:>04}"

def set_lights(light_pattern):
    relays.set_relays(lights_to_relays(light_pattern))

def main():
    """Marquee application main."""
    global relays

    # HACK - give Pi Zero time for relay board to show up during boot
    time.sleep(1)

    mode.current = 1
    mode.button = button.Button()
    relays = relayboard.RelayBoard()
    set_lights([0] * 10)

    while True:
        try:
            print (f"Current mode is {mode.current}")
            MODES[mode.current]()
        except button.ButtonPressed:
            print("Execute Caught Button Press")
            mode.previous = mode.current
            mode.current = 0

MODES = [
    mode_selection,
    mode_all_on,
    mode_half_on,
    mode_all_off,
    mode_blink_alternate,
    mode_variety,
]
MODE_COUNT = len(MODES)

mode = types.SimpleNamespace()
relays = None

if __name__ == "__main__":
    main()
