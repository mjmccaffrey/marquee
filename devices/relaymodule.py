"""Marquee Lighted Sign Project - relaymodule"""

from abc import ABC, abstractmethod
from typing import ClassVar, Protocol
from typing_extensions import override

from dataclasses import dataclass
import logging
from typing import NewType

log = logging.getLogger('marquee.' + __name__)


DevicePattern = NewType('DevicePattern', str)
"""str[n] represents the state of the nth device in RelayClient."""

RelayPattern = NewType('RelayPattern', str)
"""str[len(str) - n] represents state of nth relay in RelayModule."""

RelayHex = NewType('RelayHex', str)
"""Numato hex representation of relay pattern."""


@dataclass()
class RelayClient:
    module: 'RelayModuleInterface'
    count: int
    device_to_relay: dict
    relay_to_device: dict

    def __post_init__(self):
        """"""
        self.device_pattern = self.get_state_of_devices()

    def get_state_of_devices(self) -> str:
        """"""
        return self.module.get_state_of_devices(self)

    def set_state_of_devices(self, pattern: str):
        """!!!THIS SHOULD NORMALIZE pattern???"""
        self.module.set_state_of_devices(self, DevicePattern(pattern))
        self.device_pattern = pattern


class RelayModuleInterface(Protocol):
    relay_count: ClassVar[int]

    @abstractmethod
    def set_state_of_devices(
        self, 
        client: RelayClient,
        pattern: DevicePattern,
    ) -> None:
        """Set the physical relays per client device pattern.
           Do not change relays not assigned to client."""

    @abstractmethod
    def get_state_of_devices(
        self, 
        client: RelayClient,
    ) -> DevicePattern:
        """Get the state of all relays from the module.
           Update saved state.
           Return a client device pattern."""


class RelayModule(RelayModuleInterface, ABC):
    """Base for any relay module."""
    relay_pattern: RelayPattern

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


class MockRelayModule(RelayModule):
    """Mock relay module for testing."""
    relay_count: ClassVar[int]

    def __init_subclass__(cls, relay_count: int) -> None:
        """"""
        cls.relay_count = relay_count

    def __init__(self):
        """"""
        self.relay_pattern = RelayPattern('0' * self.relay_count)

    @override
    def set_state_of_devices(
        self, 
        client: RelayClient,
        pattern: DevicePattern,
    ) -> None:
        self.relay_pattern = self._devices_to_relays(client, pattern)

    @override
    def get_state_of_devices(
        self, 
        client: RelayClient,
    ) -> DevicePattern:
        return DevicePattern(self.relay_pattern)

class MockRelay16(MockRelayModule, relay_count=16):
    """"""

class MockRelay32(MockRelayModule, relay_count=16):
    """"""


class CombinedRelayModule:
    """Virtual relay module combining 2 concrete relay modules."""
    relay_count: ClassVar[int]
    
    def __init__(
        self,
        rm1: RelayModuleInterface,
        rm2: RelayModuleInterface,
    ) -> None:
        """"""
        CombinedRelayModule.relay_count = rm1.relay_count + rm2.relay_count
        self.rm1, self.rc1 = rm1, create_client(rm1)
        self.rm2, self.rc2 = rm2, create_client(rm2)

    def set_state_of_devices(
        self, 
        client: RelayClient,
        pattern: DevicePattern,
    ) -> None:
        self.rm1.set_state_of_devices(
            self.rc1, DevicePattern(pattern[:self.rm1.relay_count]),
        )
        self.rm2.set_state_of_devices(
            self.rc2, DevicePattern(pattern[self.rm1.relay_count:]),
        )

    def get_state_of_devices(
        self, 
        client: RelayClient,
    ) -> DevicePattern:
        return DevicePattern(
            self.rm1.get_state_of_devices(self.rc1) + 
            self.rm2.get_state_of_devices(self.rc2)
        )


def create_client(
    relay_module: RelayModuleInterface,
    device_to_relay: dict[int, int] | None = None,
) -> RelayClient:
    """Define a client, in which device_to_relay maps 
        device indices to relay indices."""
    if device_to_relay is None:
        device_to_relay = {i: i for i in range(relay_module.relay_count)}
    return RelayClient(
        module=relay_module,
        count=len(device_to_relay),
        device_to_relay=device_to_relay,
        relay_to_device={v: k for k, v in device_to_relay.items()},
    )

