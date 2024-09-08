"""Marquee Lighted Sign Project - relayboard"""

import serial

RELAY_COUNT = 16

class RelayBoard:
    """Supports the Numato 16 Channel USB Relay Module (RL160001)."""

    def __init__(self, device_mapping):
        """Create the RelayBoard object, where device_mapping
           is a dict mapping device indices to relay indices.
           Establish connection to relay board via serial port."""
        self._serial_port = serial.Serial("/dev/ttyACM0", timeout=1)
        self.device_mapping = device_mapping
        last_relay = RELAY_COUNT - 1
        self._device_to_bit = {
            l: last_relay - r
            for l, r in self.device_mapping.items()
        }
        self._bit_to_device = {
            v: k for k, v in self._device_to_bit.items()
        }
        self.device_count = max(device_mapping.keys()) + 1

    def close(self):
        """Clean up."""
        self._serial_port.close()

    def _set_relays(self, relay_pattern_hex):
        """Send command to relay board to set all relays."""
        command = f"relay writeall {relay_pattern_hex}\n\r"
        self._serial_port.write(bytes(command, 'utf-8'))

    def _devices_to_relays(self, device_pattern):
        """Convert desired device (light) pattern,
           in which the first light is the leftmost 0 or 1 of the string,
           to a relay pattern, in which the first relay is the
           rightmost bit of the binary / hex value."""
        print(device_pattern)
        relay_pattern = ''.join(
            device_pattern[self._bit_to_device[b]]
            if b in self._bit_to_device else ''
            for b in range(RELAY_COUNT)
        )
        print(relay_pattern)
        val = hex(int(''.join(str(e) for e in relay_pattern), 2))[2:]
        return f"{val:>0{RELAY_COUNT}}"

    def _relays_to_devices(self, relay_pattern):
        """ """
        print(relay_pattern)
        device_pattern = ''.join(
            relay_pattern[self._device_to_bit[d]]
            for d in range(self.device_count)
        )
        print(device_pattern)
        return device_pattern

    def set_relays_from_pattern(self, device_pattern):
        """Set the physical relays per the supplied pattern."""
        relay_pattern = self._devices_to_relays(device_pattern)
        self._set_relays(relay_pattern)

    def _get_relays(self):
        """ """
        command = "relay readall\n\r"
        self._serial_port.write(bytes(command, 'utf-8'))
        # b'relay readall\n\n\r0000\n\r>'
        response = self._serial_port.read(23)
        val = response[-7:-3].decode('utf-8')
        val = bin(int(val, base=16))[2:]
        return f"{val:>04}"

    def get_state_of_devices(self):
        """ """
        relays = self._get_relays()
        return self._relays_to_devices(relays)
