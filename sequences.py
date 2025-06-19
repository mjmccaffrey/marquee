"""Marquee Lighted Sign Project - sequence definitions"""

from collections.abc import Iterator, Sequence
import random

from definitions import *

def opposite(pattern: Sequence) -> str:
    """Return pattern or element with the state(s) flipped."""
    return "".join("1" if str(p) == "0" else "0" for p in pattern)

def all_on() -> Iterator[str]:
    """All lights on."""
    yield ALL_ON

def all_off() -> Iterator[str]:
    """All lights off."""
    yield ALL_OFF

def blink_all(on_first=True) -> Iterator[str]:
    """All lights on and then off."""
    if on_first:
        yield next(all_on())
        yield next(all_off())
    else:
        yield next(all_off())
        yield next(all_on())

def even_on() -> Iterator[str]:
    """Even-numbered lights on; others off."""
    yield ''.join('1' if y % 2 else '0' for y in range(LIGHT_COUNT))

def even_off() -> Iterator[str]:
    """Even-numbered lights off; others on."""
    yield opposite(next(even_on()))

def blink_alternate() -> Iterator[str]:
    """Every other light on and then off."""
    yield next(even_on())
    yield next(even_off())

def each_row(pattern="1") -> Iterator[str]:
    """Each row, starting at the top."""
    for row in LIGHTS_BY_ROW:
        yield ''.join(
            pattern if i in row else opposite(pattern)
            for i in range(LIGHT_COUNT)
        )

def build_rows(pattern="1", from_top=True) -> Iterator[str]:
    """Successive rows on / off."""
    assert len(pattern) == 1
    if from_top:
        rows = LIGHTS_BY_ROW
    else:  # from_bottom
        rows = reversed(LIGHTS_BY_ROW)
    lights = [opposite(pattern)] * LIGHT_COUNT
    for row in rows:
        for light in row:
            lights[light] = pattern
        yield ''.join(l for l in lights)

def rotate(pattern="1"+"0"*(LIGHT_COUNT-1), clockwise=True) -> Iterator[str]:
    """Rotate a pattern of lights counter/clockwise.
       Pattern is a string of length LIGHT_COUNT containing 0 and 1."""
    if clockwise:
        light_range = range(LIGHT_COUNT, 0, -1)
    else:  # counterclockwise
        light_range = range(0, LIGHT_COUNT, 1)
    for i in light_range:
        rotated_pattern = pattern[i:] + pattern[:i]
        yield rotated_pattern

def rotate_sides(pattern="1", clockwise=True) -> Iterator[str]:
    """ """
    sequence = LIGHTS_SIDES if clockwise else reversed(LIGHTS_SIDES)
    opp = opposite(pattern)
    for lights in sequence:
        yield ''.join(
            pattern if i in lights else opp
            for i in range(LIGHT_COUNT)
        )

def opposite_corner_pairs() -> Iterator[str]:
    """Alternate the lights in 2 diagonally-opposite corners
       with the other 2 diagonally-opposite corners."""
    corners_clockwise = [
        (LIGHTS_TOP[0], LIGHTS_LEFT[0]),
        (LIGHTS_TOP[-1], LIGHTS_RIGHT[0]),
        (LIGHTS_BOTTOM[-1], LIGHTS_RIGHT[-1]),
        (LIGHTS_BOTTOM[0], LIGHTS_LEFT[-1]),
    ]
    opposite_corners = [
        corners_clockwise[0] + corners_clockwise[2],
        corners_clockwise[1] + corners_clockwise[3],
    ]
    for lights in opposite_corners:
        pattern = ''.join(
            "0" if i in lights else "1"
            for i in range(LIGHT_COUNT)
        )
        yield pattern
        yield ALL_ON

def rotate_build(clockwise=True) -> Iterator[str]:
    """Successive lights on, rotating around."""
    if clockwise:
        light_range = LIGHTS_CLOCKWISE
    else:  # counterclockwise
        light_range = reversed(LIGHTS_CLOCKWISE)
    lights = ['0'] * LIGHT_COUNT
    for l in light_range:
        lights[l] = '1'
        yield ''.join(e for e in lights)

def rotate_build_flip(*, count: int, clockwise=True) -> Iterator[str]:
    """Successive lights on / off, rotating around."""
    if clockwise:
        light_range = LIGHTS_CLOCKWISE
    else:  # counterclockwise
        light_range = reversed(LIGHTS_CLOCKWISE)
    lights = ['0'] * LIGHT_COUNT
    for c in range(count):
        i = c % LIGHT_COUNT
        lights[i] = '0' if lights[i] else '1'
        yield ''.join(e for e in lights)

def center_alternate() -> Iterator[str]:
    """Alternate the top and bottom center lights."""
    yield "010000000000"
    yield "000000010000"

@staticmethod
def _random_light_gen() -> Iterator[int]:
    """Generate random light indexes 
       that never immediately repeats."""
    new = -1
    while True:
        old = new
        while new == old:
            new = random.randrange(LIGHT_COUNT)
        yield new

def random_flip_start_blank(*, pattern: str = "1") -> Iterator[str]:
    """Random light on / off, never immediately repeating a light.
       Starts with setting all lights to the opposite of pattern.
       This sequence does not end on its own."""
    opp = opposite(pattern)
    random_gen = _random_light_gen()
    while True:
        index = next(random_gen)
        yield ''.join(
            opp * index +
            pattern +
            opp * (LIGHT_COUNT - index - 1)
        )

def random_flip(*, light_pattern) -> Iterator[str]:
    """Random light on / off, never immediately repeating a light.
       Pass in current / starting state of lights.
       This sequence does not end on its own."""
    lights = list(light_pattern)
    random_gen = _random_light_gen()
    while True:
        index = next(random_gen)
        lights[index] = opposite(lights[index])
        yield ''.join(e for e in lights)

def random_once_each() -> Iterator[list[int]]:
    """Return random light index until all light indexes 
       have been returned exactly once."""
    indices = [i for i in range(LIGHT_COUNT)]
    random.shuffle(indices)
    while indices:
        yield [indices.pop()]
