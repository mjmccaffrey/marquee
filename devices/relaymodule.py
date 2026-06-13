"""Marquee Lighted Sign Project - relaymodule"""

from typing import ClassVar, Protocol

from dataclasses import dataclass, field
import logging
from typing import NewType
from typing_extensions import override

log = logging.getLogger('marquee.' + __name__)


DevicePattern = NewType('DevicePattern', str)
"""str[n] represents the state of the nth device in RelayClient."""

RelayPattern = NewType('RelayPattern', str)
"""str[len(str) - n] represents state of nth relay in RelayModuleInterface."""

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
    """Protocol for any relay module."""
    relay_count: ClassVar[int]

    def set_state_of_devices(
        self, 
        client: RelayClient,
        pattern: DevicePattern,
    ) -> None: ...

    def get_state_of_devices(
        self, 
        client: RelayClient,
    ) -> DevicePattern: ...

    def create_client(
        self,
        device_to_relay: dict[int, int],
    ) -> RelayClient:
        """Define a client, in which device_to_relay maps 
           device indices to relay indices."""
        return RelayClient(
            module=self,
            count=len(device_to_relay),
            device_to_relay=device_to_relay,
            relay_to_device={v: k for k, v in device_to_relay.items()},
        )


@dataclass
class CombinedRelayModule(RelayModuleInterface):
    """Virtual relay module combining 2 concrete relay modules."""
    rm1: RelayModuleInterface
    rm2: RelayModuleInterface
    relay_count: int = field(init=False)

    def __post_init__(self):
        """"""
        self.relay_count = self.rm1.relay_count + self.rm2.relay_count

    @override
    def set_state_of_devices(
        self, 
        client: RelayClient,
        pattern: DevicePattern,
    ) -> None:
        self.rm1.set_state_of_devices(
            client, DevicePattern(pattern[:self.rm1.relay_count]),
        )
        self.rm2.set_state_of_devices(
            client, DevicePattern(pattern[self.rm1.relay_count:]),
        )

    @override
    def get_state_of_devices(
        self, 
        client: RelayClient,
    ) -> DevicePattern:
        return DevicePattern(
            self.rm1.get_state_of_devices(client) + 
            self.rm2.get_state_of_devices(client)
        )

