"""Marquee Lighted Sign Project - relayboard"""

import serial

class RelayBoard():
    """Support the Numato 16 Channel USB Relay Module (RL160001)."""

    RELAY_COUNT = 16

    def __init__(self, device_mapping):
        """Create the RelayBoard object, where device_mapping
           is a dict mapping device indices to relay indices."""
        self.device_mapping = device_mapping
        self._relay_board = serial.Serial("/dev/ttyACM0")

    def _set_relays(self, relay_pattern_hex):
        """ """
        command = f"relay writeall {relay_pattern_hex}\n\r"
        self._relay_board.write(bytes(command, 'utf-8'))

    def _devices_to_relays(self, device_pattern):
        """ """
        # !! This could probably use optimizing !!
        relay_pattern = [0] * self.RELAY_COUNT
        for i, l in enumerate(device_pattern):
            relay_pattern[self.RELAY_COUNT - 1 - self.device_mapping[i]] = l
        val = hex(int(''.join(str(e) for e in relay_pattern), 2))[2:]
        return f"{val:>04}"

    def set_relays_from_pattern(self, device_pattern):
        """ """
        relay_pattern = self._devices_to_relays(device_pattern)
        self._set_relays(relay_pattern)
