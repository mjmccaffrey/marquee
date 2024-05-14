# Marquee Lighted Sign Project
# Version 1.0 - Connor's graduation party

import functools
import serial
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

def seq_clockwise():
    for i in range(LIGHT_COUNT):
        yield [int(y == i) for y in range(LIGHT_COUNT)]
        
def seq_clockwise_multiple(pattern = [1] + [0] * (LIGHT_COUNT - 1)):
    for i in range(LIGHT_COUNT, 0, -1):
        rotated_pattern = pattern[i:] + pattern[:i]
        yield rotated_pattern
        
def seq_counterclockwise():
    for i in reversed(range(LIGHT_COUNT)):
        yield [int(y == i) for y in range(LIGHT_COUNT)]
        
def seq_blink_all():
    yield [1] * LIGHT_COUNT
    yield [0] * LIGHT_COUNT

def seq_blink_alternate():
    yield [y % 2 for y in range(LIGHT_COUNT)]
    yield [(y + 1) % 2 for y in range(LIGHT_COUNT)]

def seq_build_left():
    lights = [0] * LIGHT_COUNT
    yield lights
    for t, b in zip(TOP_LIGHTS_LEFT_TO_RIGHT, BOTTOM_LIGHTS_LEFT_TO_RIGHT):
        lights[t], lights[b] = 1, 1
        yield lights

def seq_build_right():
    lights = [0] * LIGHT_COUNT
    yield lights
    for t, b in zip(reversed(TOP_LIGHTS_LEFT_TO_RIGHT), reversed(BOTTOM_LIGHTS_LEFT_TO_RIGHT)):
        lights[t], lights[b] = 1, 1
        yield lights

def seq_move_left():
    for t, b in zip(TOP_LIGHTS_LEFT_TO_RIGHT, BOTTOM_LIGHTS_LEFT_TO_RIGHT):
        yield [int(y == t or y == b) for y in range(LIGHT_COUNT)]

def seq_move_right():
    for t, b in zip(reversed(TOP_LIGHTS_LEFT_TO_RIGHT), reversed(BOTTOM_LIGHTS_LEFT_TO_RIGHT)):
        yield [int(y == t or y == b) for y in range(LIGHT_COUNT)]

def seq_invert_all():
    yield [(y + 1) % 2 for y in range(LIGHT_COUNT)]

def set_lights(light_pattern):
    global current_light_pattern
    
    # print("light_pattern: " + str(light_pattern))
    relay_pattern = [0] * RELAY_COUNT
    for i, l in enumerate(light_pattern):
        relay_pattern[RELAY_COUNT - 1 - LIGHT_TO_RELAY[i]] = l
    # print("relay_pattern: " + str(relay_pattern))
    temp = hex(int(''.join(str(e) for e in relay_pattern), 2))[2:]
    # print(temp)
    relay_pattern_hex = f"{temp:>04}"
    # print("relay_pattern_hex: " + relay_pattern_hex)

    command = "relay writeall %s\n\r" % relay_pattern_hex
    # print(command)
    relay_board_usb.write(bytes(command, 'utf-8'))
    current_light_pattern = light_pattern
    
def do_sequence(sequence, count, delay):
        for c in range(count):
            for s in sequence():
                set_lights(s)
                time.sleep(delay)
        
def program():
    while True:
        do_sequence(seq_clockwise, 2, 0.4)
        do_sequence(seq_counterclockwise, 2, 0.4)
        do_sequence(seq_blink_all, 4, 0.4)
        do_sequence(seq_blink_alternate, 4, 0.4)
        do_sequence(functools.partial(seq_clockwise_multiple, '1100000000'), 4, 0.3)
        do_sequence(functools.partial(seq_clockwise_multiple, '1101000000'), 4, 0.3)
        do_sequence(functools.partial(seq_clockwise_multiple, '1111111110'), 4, 0.3)
        do_sequence(seq_move_left, 10, 0.2)
        do_sequence(seq_build_left, 10, 0.2)
        do_sequence(seq_clockwise, 8, 0.05)
        set_lights([1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
        time.sleep(900)

        
def setup():
    global relay_board_usb
    relay_board_usb = serial.Serial("/dev/ttyACM0")
    set_lights([0] * 10)

def main():
    setup()
    program()

if __name__ == "__main__":
    main()


