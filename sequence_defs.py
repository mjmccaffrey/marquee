"""Marquee Lighted Sign Project - sequence definitions"""

from collections.abc import Iterator
import random

from definitions import *

def opposite_pattern(pattern) -> str:
    """Return pattern with the states flipped."""
    return "".join("1" if str(p) == "0" else "0" for p in pattern)

def all_on():
    """All lights on."""
    yield ALL_ON

def all_off():
    """All lights off."""
    yield ALL_OFF

def blink_all(on_first=True):
    """All lights on and then off."""
    if on_first:
        yield next(all_on())
        yield next(all_off())
    else:
        yield next(all_off())
        yield next(all_on())

def even_on():
    """Even-numbered lights on; others off."""
    yield [y % 2 for y in range(LIGHT_COUNT)]

def even_off():
    """Even-numbered lights off; others on."""
    yield [(y + 1) % 2 for y in range(LIGHT_COUNT)]

def blink_alternate():
    """Every other light on and then off."""
    yield next(even_on())
    yield next(even_off())

def each_row(pattern="1"):
    """Each row, starting at the top."""
    for row in LIGHTS_BY_ROW:
        yield ''.join(
            pattern if i in row else opposite_pattern(pattern)
            for i in range(LIGHT_COUNT)
        )

def build_rows(pattern="1", from_top=True):
    """Successive rows on / off."""
    assert len(pattern) == 1
    if from_top:
        rows = LIGHTS_BY_ROW
    else:  # from_bottom
        rows = reversed(LIGHTS_BY_ROW)
    lights = [opposite_pattern(pattern)] * LIGHT_COUNT
    for row in rows:
        for light in row:
            lights[light] = pattern
        yield [l for l in lights]

def build_rows_4(*, pattern, from_top):
    """Successive rows on / off, grouping the middle rows together, 
       and starting with no rows."""
    assert len(pattern) == 1
    yield [opposite_pattern(pattern)] * LIGHT_COUNT
    seq = build_rows(pattern, from_top)
    yield next(seq)  # Row 0
    _ = next(seq)    # Row 1
    yield next(seq)  # Row 2
    yield next(seq)  # Row 3

def build_halves(from_left=True):
    """Grow the upper and lower halves together, 
       starting from the left or the right."""
    if from_left:
        top = TOP_LIGHTS_LEFT_TO_RIGHT
        bot = BOTTOM_LIGHTS_LEFT_TO_RIGHT
    else:  # from right
        top = reversed(TOP_LIGHTS_LEFT_TO_RIGHT)
        bot = reversed(BOTTOM_LIGHTS_LEFT_TO_RIGHT)
    lights = [0] * LIGHT_COUNT # ???
    for t, b in zip(top, bot):
        lights[t], lights[b] = 1, 1
        yield lights

def move_halves(from_left=True):
    """Move lit lights in the upper and lower halves, 
       starting from the left or the right."""
    if from_left:
        top = TOP_LIGHTS_LEFT_TO_RIGHT
        bot = BOTTOM_LIGHTS_LEFT_TO_RIGHT
    else:  # from right
        top = reversed(TOP_LIGHTS_LEFT_TO_RIGHT)
        bot = reversed(BOTTOM_LIGHTS_LEFT_TO_RIGHT)
    for t, b in zip(top, bot):
        yield [int(y in {t, b}) for y in range(LIGHT_COUNT)]

def rotate(pattern="1"+"0"*(LIGHT_COUNT-1), clockwise=True):
    """Rotate a pattern of lights counter/clockwise.
       Pattern is a string of length LIGHT_COUNT containing 0 and 1."""
    if clockwise:
        light_range = range(LIGHT_COUNT, 0, -1)
    else:  # counterclockwise
        light_range = range(0, LIGHT_COUNT, 1)
    for i in light_range:
        rotated_pattern = pattern[i:] + pattern[:i]
        yield rotated_pattern

def opposite_corner_pairs():
    """Alternate the lights in 2 diagonally-opposite corners
       with the other 2 diagonally-opposite corners."""
    lights_in_opposite_corners = [
        {
            l
            for i, c in enumerate(CORNER_LIGHTS_CLOCKWISE)
            for l in c
            if (i % 2) == eo
        }
        for eo in range(2)
    ]
    for lights in lights_in_opposite_corners:
        pattern = [
            "0" if i in lights else "1"
            for i in range(LIGHT_COUNT)
        ]
        yield pattern
        yield ALL_ON

def rotate_build(clockwise=True):
    """Successive lights on, rotating around."""
    if clockwise:
        light_range = LIGHTS_CLOCKWISE
    else:  # counterclockwise
        light_range = reversed(LIGHTS_CLOCKWISE)
    lights = [0] * LIGHT_COUNT
    for l in light_range:
        lights[l] = 1
        yield lights

def rotate_build_flip(*, count: int, clockwise=True):
    """Successive lights on / off, rotating around."""
    if clockwise:
        light_range = LIGHTS_CLOCKWISE
    else:  # counterclockwise
        light_range = reversed(LIGHTS_CLOCKWISE)
    lights = [0] * LIGHT_COUNT
    for c in range(count):
        i = c % LIGHT_COUNT
        lights[i] = 0 if lights[i] else 1
        yield [l for l in lights]

def center_alternate():
    """Alternate the top and bottom center lights."""
    yield "0100000000"
    yield "0000001000"

@staticmethod
def _random_light_gen():
    """Generate random light indexes 
       that never immediately repeats."""
    new = -1
    while True:
        old = new
        while new == old:
            new = random.randrange(LIGHT_COUNT)
        yield new

def random_flip_start_blank(*, pattern="1"):
    """Random light on / off, never immediately repeating a light.
       Starts with setting all lights to the opposite of pattern.
       This sequence does not end on its own."""
    opposite = [opposite_pattern(pattern)]
    pattern = [pattern]
    random_gen = _random_light_gen()
    while True:
        index = next(random_gen)
        yield (
            opposite * index +
            pattern +
            opposite * (LIGHT_COUNT - index - 1)
        )

def random_flip(*, light_pattern):
    """Random light on / off, never immediately repeating a light.
       Pass in current / starting state of lights.
       This sequence does not end on its own."""
    lights = list(light_pattern)
    random_gen = _random_light_gen()
    while True:
        index = next(random_gen)
        lights[index] = opposite_pattern(lights[index])
        yield [l for l in lights]

def random_once_each() -> Iterator[list[int]]:
    """Return random light index until all light indexes 
       have been returned exactly one."""
    indices = [i for i in range(LIGHT_COUNT)]
    random.shuffle(indices)
    while indices:
        yield [indices.pop()]
