"""Marquee Lighted Sign Project - relaymodule"""

from typing import ClassVar, Protocol

from dataclasses import dataclass
import logging
from typing import NewType

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
        self.rm1, self.rm2 = rm1, rm2

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

    def get_state_of_devices(
        self, 
        client: RelayClient,
    ) -> DevicePattern:
        return DevicePattern(
            self.rm1.get_state_of_devices(client) + 
            self.rm2.get_state_of_devices(client)
        )

