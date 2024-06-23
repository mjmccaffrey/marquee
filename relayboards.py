"""Marquee Lighted Sign Project - relayboard"""

import serial

RELAY_COUNT = 16

class RelayBoard:
    """Supports the Numato 16 Channel USB Relay Module (RL160001)."""

    def __init__(self, device_mapping):
        """Create the RelayBoard object, where device_mapping
           is a dict mapping device indices to relay indices.
           Establish connection to relay board via serial port."""
        self.device_mapping = device_mapping
        self._relay_board = serial.Serial("/dev/ttyACM0")

    def close(self):
        """Clean up."""
        self._relay_board.close()

    def _set_relays(self, relay_pattern_hex):
        """Send command to relay board to set all relays."""
        command = f"relay writeall {relay_pattern_hex}\n\r"
        self._relay_board.write(bytes(command, 'utf-8'))

    def _devices_to_relays(self, device_pattern):
        """Convert desired device (light) pattern,
           in which the first light is the leftmost 0 or 1 of the string,
           to a relay pattern, in which the first relay is the
           rightmost bit of the binary / hex value."""
        relay_pattern = [0] * RELAY_COUNT
        last_relay = RELAY_COUNT - 1
        for i, l in enumerate(device_pattern):
            relay_pattern[last_relay - self.device_mapping[i]] = l
        val = hex(int(''.join(str(e) for e in relay_pattern), 2))[2:]
        return f"{val:>04}"

    def set_relays_from_pattern(self, device_pattern):
        """Set the physical relays per the supplied pattern."""
        relay_pattern = self._devices_to_relays(device_pattern)
        self._set_relays(relay_pattern)
