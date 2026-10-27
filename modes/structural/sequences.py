"""Marquee Lighted Sign Project - sequences"""

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
import itertools
import random

from schemas import LightConfig


MAX_YIELDS = 50   # !!!


def opposite(pattern: Sequence) -> str:
    """Return pattern or element with the state(s) flipped."""
    return "".join("1" if str(p) == "0" else "0" for p in pattern)


@dataclass
class Sequences:
    """"""
    light_config: LightConfig

    def all_on(self) -> Iterator[str]:
        """All lights on."""
        yield '1' * self.light_config.count

    def all_off(self) -> Iterator[str]:
        """All lights off."""
        yield '0' * self.light_config.count

    def blink_all(self, on_first=True) -> Iterator[str]:
        """All lights on and then off."""
        if on_first:
            yield next(self.all_on())
            yield next(self.all_off())
        else:
            yield next(self.all_off())
            yield next(self.all_on())

    def even_on(self) -> Iterator[str]:
        """Even-numbered lights on; others off."""
        yield ''.join(
            '1' if y % 2 else '0'
            for y in range(self.light_config.count)
        )

    def even_off(self) -> Iterator[str]:
        """Even-numbered lights off; others on."""
        yield opposite(next(self.even_on()))

    def blink_alternate(self) -> Iterator[str]:
        """Every other light on and then off."""
        yield next(self.even_on())
        yield next(self.even_off())

    def each_row(self, pattern="1") -> Iterator[str]:
        """Each row, starting at the top."""
        opp = opposite(pattern)
        for row in self.light_config.lights_by_row:
            yield ''.join(
                pattern if i in row else opp
                for i in range(self.light_config.count)
            )

    def lights_in_groups(
        self, rows=True, from_top_left=True,
    ) -> Iterator[list[int]]:
        """Return lights in each group section."""
        if rows:
            groups = self.light_config.lights_by_row
        else:  # cols
            groups = self.light_config.lights_by_column
        if not from_top_left:
            groups = reversed(groups)
        for group in groups:
            yield group

    def build(
        self, pattern="1", rows=True, from_top_left=True,
    ) -> Iterator[str]:
        """Successive rows or cols on / off."""
        assert len(pattern) == 1
        lights = [opposite(pattern)] * self.light_config.count
        for group in self.lights_in_groups(rows, from_top_left):
            for light in group:
                lights[light] = pattern
            yield ''.join(l for l in lights)

    def rotate(self, pattern: str, clockwise=True) -> Iterator[str]:
        """Rotate a pattern of lights counter/clockwise.
        Pattern is a string of length LIGHT_COUNT containing 0 and 1."""
        if clockwise:
            light_range = range(self.light_config.count, 0, -1)
        else:  # counterclockwise
            light_range = range(0, self.light_config.count, 1)
        for i in light_range:
            rotated_pattern = pattern[i:] + pattern[:i]
            yield rotated_pattern

    def rotate_sides(self, pattern="1", clockwise=True) -> Iterator[str]:
        """Rotate lights 1 side at a time."""
        by_side = self.light_config.by_side
        sequence = by_side if clockwise else reversed(by_side)
        opp = opposite(pattern)
        for lights in sequence:
            yield ''.join(
                pattern if i in lights else opp
                for i in range(self.light_config.count)
            )

    def chase(self, pattern: str, mask: str, clockwise: bool) -> Iterator[str]:
        """Rotate mask around pattern."""
        for rotated_mask in self.rotate(mask, clockwise):
            result = ''.join(
                p if m == '*' else m
                for p, m in zip(pattern, rotated_mask)
            )
            yield result

    def rotate_build(self, clockwise=True) -> Iterator[str]:
        """Successive lights on, rotating around."""
        lights = self.light_config.lights_clockwise
        light_range = lights if clockwise else reversed(lights)
        lights = ['0'] * self.light_config.count
        for l in light_range:
            lights[l] = '1'
            yield ''.join(e for e in lights)

    def rotate_build_flip(self, *, count: int, clockwise=True) -> Iterator[str]:
        """Successive lights on / off, rotating around."""
        lights = self.light_config.clockwise
        light_range = lights if clockwise else reversed(lights)
        lights = ['0'] * self.light_config.count
        for c in range(count):
            i = c % self.light_config.count
            lights[i] = opposite(lights[i])
            yield ''.join(e for e in lights)

    def _random_light_gen(self) -> Iterator[int]:
        """Generate random light indexes 
        that never immediately repeat."""
        new = -1
        while True:
            old = new
            while new == old:
                new = random.randrange(self.light_config.count)
            yield new

    def random_flip_start_blank(self, *, pattern: str = "1") -> Iterator[str]:
        """Random light on / off, never immediately repeating a light.
        Starts with setting all lights to the opposite of pattern."""
        opp = opposite(pattern)
        random_gen = self._random_light_gen()
        for _ in range(MAX_YIELDS):
            index = next(random_gen)
            yield ''.join(
                opp * index +
                pattern +
                opp * (self.light_config.count - index - 1)
            )

    def random_flip(self, *, light_pattern) -> Iterator[str]:
        """Random light on / off, never immediately repeating a light.
        Pass in current / starting state of lights."""
        lights = list(light_pattern)
        random_gen = self._random_light_gen()
        for _ in range(MAX_YIELDS):
            index = next(random_gen)
            lights[index] = opposite(lights[index])
            yield ''.join(e for e in lights)

    def random_once_each(self) -> Iterator[list[int]]:
        """Yield random light index until all 
        have been yielded exactly once."""
        indices = [i for i in range(self.light_config.count)]
        random.shuffle(indices)
        while indices:
            yield [indices.pop()]

    def random_each(self) -> Iterator[list[int]]:
        """"Yield indefinitely a single random sequence of light indexes."""
        for index in itertools.cycle(self.random_once_each()):
            yield index

