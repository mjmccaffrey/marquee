"""Marquee Lighted Sign Project - repl_misc"""

import time

from setup_devices import setup_devices


def setup():
    global bells, buttons, drums, lights

    bells, buttons, drums, lights = setup_devices(brightness_factor=1.0)

def test():
    # Light relays turned on during LightSet init.
    time.sleep(5)
    start = time.time() 
    for _ in range(10):
        lights.set_channels(on=True, force=True)
        lights.set_channels(on=False, force=True)
    print(time.time() - start)

