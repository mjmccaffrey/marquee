"""Marquee Lighted Sign Project - repl_misc"""

from collections.abc import Sequence
import time

from lightset import LightSet
from setup_devices_shelly import setup_devices


def setup():
    global bells, buttons, drums, lights

    bells, buttons, drums, lights = setup_devices(1.0, 1.0)


def test():
    # Light relays turned on during LightSet init.
    time.sleep(5)
    start = time.time() 
    for _ in range(10):
        lights.set_channels(on=True, force=True)
        lights.set_channels(on=False, force=True)
    print(time.time() - start)


def ppp(p: Sequence) -> None:
    """Pretty print pattern p."""
    print(
        f"  {p[0]} {p[1]} {p[2]}\n"
        f"{p[11]}       {p[3]}\n"
        f"{p[10]}       {p[4]}\n"
        f"{p[9]}       {p[5]}\n"
        f"  {p[8]} {p[7]} {p[6]}\n"
    )

def light_states(lights: LightSet) -> None:
    """"""
    for i, c in enumerate(lights.channels):
        print(f"{i} {c.brightness} {c.color} {c.on}")
