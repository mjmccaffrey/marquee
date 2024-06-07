# Marquee Lighted Sign Project - main
# Version 2.0.0 - Mode Selection Button
# ??? ADD A CHANGELOG?
# !!! remove debug stmts
# ---- Future: all sequences as modes?  all modes, including 0, to not exit prematurely, when mode selection initiated, start at current mode?
# !!! PEP8 !!!

import button
import relayboard

import functools
import threading
import time

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
current_mode = None
desired_mode = None
previous_mode = None
mode_button = None
relays = None
    
def seq_rotate(pattern = None, clockwise = True):
    if pattern is None:
        pattern = [1] + [0] * (LIGHT_COUNT - 1)
    for i in range(LIGHT_COUNT, 0, -1 if clockwise else +1):
        rotated_pattern = pattern[i:] + pattern[:i]
        yield rotated_pattern
                
def seq_blink_all():
    yield [1] * LIGHT_COUNT
    yield [0] * LIGHT_COUNT

def seq_blink_alternate():
    yield [y % 2 for y in range(LIGHT_COUNT)]
    yield [(y + 1) % 2 for y in range(LIGHT_COUNT)]

def seq_build(from_left = True):
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
    if from_left:
        top = TOP_LIGHTS_LEFT_TO_RIGHT
        bot = BOTTOM_LIGHTS_LEFT_TO_RIGHT
    else:  # from right
        top = reversed(TOP_LIGHTS_LEFT_TO_RIGHT)
        bot = reversed(BOTTOM_LIGHTS_LEFT_TO_RIGHT)
    for t, b in zip(top, bot):
        yield [int(y == t or y == b) for y in range(LIGHT_COUNT)]

def do_sequence(sequence, count, delay):
    for c in range(count):
        for s in sequence():
            set_lights(s)
            mode_button.wait(delay)
        
def mode_variety():
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
        mode_button.wait(900)


def mode_all_on():
    set_lights([1] * LIGHT_COUNT)
    mode_button.wait(60)

def mode_all_off():
    set_lights([0] * LIGHT_COUNT)
    mode_button.wait(60)

def mode_half_on():
    set_lights([(i + 1) % 2 for i in range(LIGHT_COUNT)])    
    mode_button.wait(60)

def mode_blink_alternate():
    do_sequence(seq_blink_alternate, 10, 0.4)
        
def mode_selection():
    global current_mode
    global desired_mode

    if mode_button.just_pressed():
        if desired_mode is None:
            desired_mode = previous_mode
            print(f"Desired mode is now {desired_mode} ({threading.get_ident()})")
        else:
            desired_mode += 1
            if desired_mode == MODE_COUNT:
                desired_mode = 1
            print(f"Desired mode is now {desired_mode} ({threading.get_ident()})")
        # Indicate desired mode
        lights = [0] * LIGHT_COUNT
        set_lights(lights)
        time.sleep(0.6)
        for t in range(desired_mode):
            time.sleep(0.2)
            lights[TOP_LIGHTS_LEFT_TO_RIGHT[t]] = 1
            set_lights(lights)
    else:
        now = time.time()
        if now - mode_button.last_pressed >= 5:
            current_mode = desired_mode
            print (f"Current mode is now {current_mode} ({threading.get_ident()})")
            desired_mode = None
            print(f"Desired mode is now {desired_mode} ({threading.get_ident()})")
    mode_button.reset()

def lights_to_relays(light_pattern):
    relay_pattern = [0] * RELAY_COUNT
    for i, l in enumerate(light_pattern):
        relay_pattern[RELAY_COUNT - 1 - LIGHT_TO_RELAY[i]] = l
    val = hex(int(''.join(str(e) for e in relay_pattern), 2))[2:]
    return f"{val:>04}"

def set_lights(light_pattern):
    relays.set_relays(lights_to_relays(light_pattern))

def setup():
    global current_mode
    global mode_button
    global relays 
    relays = relayboard.RelayBoard()
    set_lights([0] * 10)
    mode_button = button.Button()
    current_mode = 1  # Default mode
    print(f"Current mode is {current_mode} ({threading.get_ident()})")

def execute():
    global current_mode
    global previous_mode
    while True:
        try:
            print (f"Current mode is {current_mode} ({threading.get_ident()})")
            MODES[current_mode]()
            mode_button.wait(1)
        except button.ButtonPressed:
            print(f"Execute Caught Button Press ({threading.get_ident()})")
            previous_mode = current_mode
            current_mode = 0

def main():
    time.sleep(1)  # HACK - give Pi Zero time for relay board to show up during boot
    setup()
    execute()

MODES = [
    mode_selection,
    mode_all_on, 
    mode_half_on, 
    mode_all_off, 
    mode_blink_alternate,
    mode_variety,
]
MODE_COUNT = len(MODES)

if __name__ == "__main__":
    main()
