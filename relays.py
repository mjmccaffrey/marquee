"""Marquee Lighted Sign Project - relayboards"""

from abc import ABC, abstractmethod
from typing import ClassVar

import serial  # type: ignore
import time

class RelayModuleInterface(ABC):
    """"""

    relay_count: ClassVar[int]

    @abstractmethod
    def set_state_of_devices(self, device_pattern):
        """Set the physical relays per device_pattern."""

    @abstractmethod
    def get_state_of_devices(self) -> str:
        """Get the state of all devices and output a device pattern."""

class NumatoUSBRelayModule(RelayModuleInterface):
    """Supports Numato USB Relay Modules."""

    def __init__(self, port_address, device_mapping):
        """Create the RelayBoard object, where device_mapping
           is a dict mapping device indices to relay indices.
           Establish connection to relay module via serial port."""
        self.port_address = port_address
        self._serial_port = serial.Serial(
            self.port_address, 
            timeout=0,
        )
        print(f"Initializing {self}")
        print(device_mapping)
        print(self.relay_count)
        assert len(device_mapping) == self.relay_count
        self.device_mapping = device_mapping
        self.device_count = max(device_mapping.keys()) + 1
        match self.device_count:
            case 8: self.relay_pattern_len = 2
            case 16: self.relay_pattern_len = 4
            case _: raise ValueError("Unrecognized device count")
        self._device_to_bit = {
            l: self.relay_count - 1 - r
            for l, r in self.device_mapping.items()
        }
        self._bit_to_device = {
            v: k for k, v in self._device_to_bit.items()
        }

    def __str__(self):
        """"""
        return f"{type(self).__name__} @ {self.port_address}"
    
    def close(self):
        """Clean up."""
        self._serial_port.close()

    def set_state_of_devices(self, device_pattern):
        """Set the physical relays per device_pattern."""
        assert len(device_pattern) == self.relay_count
        relay_pattern = self._devices_to_relays(device_pattern)
        self._set_relays(relay_pattern)

    def get_state_of_devices(self) -> str:
        """Get the state of all devices and output a device pattern."""
        relays = self._get_relays()
        return self._relays_to_devices(relays)

    def _set_relays(self, relay_pattern_hex):
        """Send command to relay board to set all relays."""
        command = f"relay writeall {relay_pattern_hex}\n\r"
        self._serial_port.write(bytes(command, 'utf-8'))

    def _get_relays(self) -> str:
        """Get the state of all relays and output a relay pattern."""
        self._serial_port.reset_input_buffer()
        print("WAITING:", self._serial_port.in_waiting)
        command = "relay readall\n\r"
        self._serial_port.write(bytes(command, 'utf-8'))
        # Response example: b'relay readall\n\n\r0000\n\r>'
        time.sleep(2)
        print("WAITING:", self._serial_port.in_waiting)
        response = self._serial_port.read(255)  # 19 + self.relay_pattern_len)
        val = response[16:-3].decode('utf-8')
        print(response)
        print(val)
        val = bin(int(val, base=16))[2:]
        return f"{val:>0{self.relay_pattern_len}}"

    def _devices_to_relays(self, device_pattern) -> str:
        """Convert desired device (light) pattern,
           in which the first light is the string's leftmost 0 or 1,
           to a relay pattern, in which the first relay is the
           rightmost bit of the binary / hex value."""
        relay_pattern = ''.join(
            str(device_pattern[self._bit_to_device[b]])
            if b in self._bit_to_device else '0'
            for b in range(self.relay_count)
        )
        val = hex(int(''.join(str(e) for e in relay_pattern), 2))[2:]
        return f"{val:>04}"

    def _relays_to_devices(self, relay_pattern) -> str:
        """Convert a relay pattern to a device pattern."""
        device_pattern = ''.join(
            relay_pattern[self._device_to_bit[d]]
            for d in range(self.device_count)
        )
        return device_pattern

class NumatoRL160001(NumatoUSBRelayModule):
    """Supports the Numato RL160001 16 Channel USB Relay Module."""

    relay_count = 16
