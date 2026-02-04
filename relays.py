"""Marquee Lighted Sign Project - relays"""

from abc import ABC
from dataclasses import dataclass
from typing import ClassVar, NewType, Protocol

import serial  # type: ignore missing module

DevicePattern = NewType('DevicePattern', str)
"""str[n] represents the state of the nth client device."""

RelayPattern = NewType('RelayPattern', str)
"""str[len(str) - n] represents the state of the nth relay."""

RelayHex = NewType('RelayHex', str)
"""Hex representation of relay pattern."""


@dataclass()
class RelayClient:
    module: 'RelayModule'
    count: int
    device_to_relay: dict
    relay_to_device: dict

    def get_state_of_devices(self) -> str:
        return self.module.get_state_of_devices(self)

    def set_state_of_devices(self, pattern: str):
        return self.module.set_state_of_devices(
            self, DevicePattern(pattern)
        )


class RelayModule(Protocol):
    """Protocol for any relay module."""
    relay_count: ClassVar[int]

    def set_state_of_devices(
        self, 
        client: RelayClient,
        pattern: DevicePattern,
    ) -> None:
        """Set the physical relays per client device pattern.
           Do not change relays not assigned to client."""
        ...

    def get_state_of_devices(
        self, 
        client: RelayClient,
    ) -> DevicePattern:
        """Get the state of all relays from the module.
           Update saved state.
           Return a client device pattern."""
        ...


class NumatoUSBRelayModule(RelayModule, ABC):
    """Supports Numato USB Relay Modules."""

    def __init_subclass__(cls, relay_count: int) -> None:
        """"""
        cls.relay_count = relay_count

    def __init__(
        self, 
        port_address: str, 
    ) -> None:
        """Establish connection to relay module via serial port."""
        self.reserved = {r: False for r in range(self.relay_count)}
        try:
            hex_lengths = {8: 2, 16: 4}
            self.relay_pattern_hex_len = hex_lengths[self.relay_count]
        except LookupError:
            raise ValueError("Unrecognized device count")
        self.port_address = port_address
        print(f"Initializing {self}")
        try:
            self._serial_port = serial.Serial(self.port_address, timeout=2)
        except serial.serialutil.SerialException as e:  # type: ignore
            print()
            print(f"*** Failed to open '{self.port_address}' ***")
            print(f"*** Error: {e} ***")
            print()
            raise OSError from None
        self.relay_pattern = self._get_relays()

    def create_client(
        self,
        device_to_relay: dict[int, int],
    ) -> RelayClient:
        """Define a client, in which device_to_relay maps 
           device indices to relay indices."""
        for r in device_to_relay.values():
            assert not self.reserved[r]
            self.reserved[r] = True
        return RelayClient(
            module=self,
            count=len(device_to_relay),
            device_to_relay=device_to_relay,
            relay_to_device={v: k for k, v in device_to_relay.items()},
        )

    def __str__(self) -> str:
        return f"{type(self).__name__} @ {self.port_address}"
    
    def close(self) -> None:
        """Clean up."""
        self._serial_port.close()
        print(f"Relay module {self} closed.")

    def set_state_of_devices(
        self, 
        client: RelayClient,
        pattern: DevicePattern,
    ) -> None:
        """Set the physical relays per client device pattern.
           Do not change relays not assigned to client."""
        assert len(pattern) == client.count
        relay_pattern = self._devices_to_relays(client, pattern)
        relay_hex = self._relays_to_relay_hex(relay_pattern)
        self._set_relays(relay_hex)
        self.relay_pattern = relay_pattern

    def get_state_of_devices(
        self, 
        client: RelayClient,
    ) -> DevicePattern:
        """Get the state of all relays from the module.
           Update saved state.
           Return a client device pattern."""
        self.relay_pattern = self._get_relays()
        print(f"GSOD: {self._relays_to_devices(client, self.relay_pattern)}")
        return self._relays_to_devices(client, self.relay_pattern)

    def _devices_to_relays(
            self,
            client: RelayClient,
            pattern: DevicePattern,
        ) -> RelayPattern:
        """Build relay pattern using client device pattern and
           current state for relays not used by this client."""
        top = self.relay_count - 1
        return RelayPattern(
            ''.join(
                    pattern[client.relay_to_device[top - i]]
                        if top - i in client.relay_to_device else
                    relay
                for i, relay in enumerate(self.relay_pattern)
            )
        )

    def _relays_to_devices(
            self,
            client: RelayClient,
            pattern: RelayPattern,
        ) -> DevicePattern:
        """Convert a relay pattern to a device pattern."""
        top = self.relay_count - 1
        return DevicePattern(
            ''.join(
                pattern[top - client.device_to_relay[d]]
                for d in range(client.count)
            )
        )

    def _relays_to_relay_hex(self, pattern: RelayPattern) -> RelayHex:
        """Return relay hex pattern corresponding to relay pattern."""
        val = hex(int(''.join(str(e) for e in pattern), 2))[2:]
        return RelayHex(f"{val:>0{self.relay_pattern_hex_len}}")

    def _response_to_relays(self, response: bytes) -> RelayPattern:
        """Return relay pattern corresponding to relay module response."""
        # Response example: b'0000\n\r>'
        val = response[:self.relay_pattern_hex_len].decode('utf-8')
        val = bin(int(val, base=16))[2:]
        return RelayPattern(f"{val:>0{self.relay_count}}")
    
    def _get_relays(self) -> RelayPattern:
        """Get the state of relays and output a relay pattern."""
        self._serial_port.reset_input_buffer()
        self._send_command("relay readall")
        # Response example: b'0000\n\r>'
        response = self._serial_port.read(self.relay_pattern_hex_len + 3)
        return self._response_to_relays(response)

    def _set_relays(self, relay_hex: RelayHex) -> None:
        """Send command to relay board to set all relays."""
        self._send_command(f"relay writeall {relay_hex}")

    def _send_command(self, command: str) -> None:
        """Send command and read resulting echo."""
        self._serial_port.reset_input_buffer()
        command_b = bytes(command + '\r', 'utf-8')
        self._serial_port.write(command_b)
        self._serial_port.read(len(command_b) + 1)


class NumatoRL160001(NumatoUSBRelayModule, relay_count=16):
    """Supports the Numato RL160001 16 Channel USB 
       Mechanical Relay Module."""


class NumatoSSR80001(NumatoUSBRelayModule, relay_count=8):
    """Supports the Numato SSR80001 8 Channel USB 
       Solid State Relay Module."""

