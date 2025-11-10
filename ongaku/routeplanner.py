# MIT License

# Copyright (c) 2023-present MPlatypus

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Route Planner and entities related to Lavalink route planner objects."""

from __future__ import annotations

__all__ = (
    "FailingAddress",
    "IPBlock",
    "IPBlockType",
    "RoutePlannerDetails",
    "RoutePlannerStatus",
    "RoutePlannerType",
)

import enum
import typing

if typing.TYPE_CHECKING:
    import datetime


class RoutePlannerStatus:
    """Routeplanner status.

    The status of the route-planner.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest.html#get-routeplanner-status)
    """

    __slots__: typing.Sequence[str] = ("_cls", "_details")

    def __init__(
        self,
        *,
        cls: RoutePlannerType,
        details: RoutePlannerDetails,
    ) -> None:
        self._cls = cls
        self._details = details

    @property
    def cls(self) -> RoutePlannerType:
        """The name of the RoutePlanner implementation being used by this server."""
        return self._cls

    @property
    def details(self) -> RoutePlannerDetails:
        """The status details of the RoutePlanner."""
        return self._details

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RoutePlannerStatus):
            return False

        return self.cls == other.cls and self.details == other.details

    def __hash__(self) -> int:
        return hash((self.cls, self.details))


class RoutePlannerDetails:
    """Routeplanner details.

    All of the information about the failing addresses.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#details-object)
    """

    __slots__: typing.Sequence[str] = (
        "_block_index",
        "_current_address",
        "_current_address_index",
        "_failing_addresses",
        "_ip_block",
        "_ip_index",
        "_rotate_index",
    )

    def __init__(
        self,
        *,
        ip_block: IPBlock,
        failing_addresses: typing.Sequence[FailingAddress],
        rotate_index: str | None,
        ip_index: str | None,
        current_address: str | None,
        current_address_index: str | None,
        block_index: str | None,
    ) -> None:
        self._ip_block = ip_block
        self._failing_addresses = failing_addresses
        self._rotate_index = rotate_index
        self._ip_index = ip_index
        self._current_address = current_address
        self._current_address_index = current_address_index
        self._block_index = block_index

    @property
    def ip_block(self) -> IPBlock:
        """The ip block being used."""
        return self._ip_block

    @property
    def failing_addresses(self) -> typing.Sequence[FailingAddress]:
        """The failing addresses."""
        return self._failing_addresses

    @property
    def rotate_index(self) -> str | None:
        """The number of rotations."""
        return self._rotate_index

    @property
    def ip_index(self) -> str | None:
        """The current offset in the block."""
        return self._ip_index

    @property
    def current_address(self) -> str | None:
        """The current address being used."""
        return self._current_address

    @property
    def current_address_index(self) -> str | None:
        """The current offset in the ip block."""
        return self._current_address_index

    @property
    def block_index(self) -> str | None:
        """The current offset in the ip block."""
        return self._block_index

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RoutePlannerDetails):
            return False

        return (
            self.ip_block == other.ip_block
            and self.failing_addresses == other.failing_addresses
            and self.rotate_index == other.rotate_index
            and self.ip_index == other.ip_index
            and self.current_address == other.current_address
            and self.current_address_index == other.current_address_index
            and self.block_index == other.block_index
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.ip_block,
                self.failing_addresses,
                self.rotate_index,
                self.ip_index,
                self.current_address,
                self.current_address_index,
                self.block_index,
            ),
        )


class IPBlock:
    """IP Block.

    All of the information about the IP Block.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest.html#ip-block-object)
    """

    __slots__: typing.Sequence[str] = ("_size", "_type")

    def __init__(self, *, type: IPBlockType, size: str) -> None:  # noqa: A002
        self._type = type
        self._size = size

    @property
    def type(self) -> IPBlockType:
        """The type of the ip block."""
        return self._type

    @property
    def size(self) -> str:
        """The size of the ip block."""
        return self._size

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IPBlock):
            return False

        return self.type == other.type and self.size == other.size

    def __hash__(self) -> int:
        return hash((self.type, self.size))


class FailingAddress:
    """Failing address.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#failing-address-object)
    """

    __slots__: typing.Sequence[str] = ("_address", "_time", "_timestamp")

    def __init__(
        self,
        *,
        address: str,
        timestamp: datetime.datetime,
        time: str,
    ) -> None:
        self._address = address
        self._timestamp = timestamp
        self._time = time

    @property
    def address(self) -> str:
        """The failing address."""
        return self._address

    @property
    def timestamp(self) -> datetime.datetime:
        """The datetime object of when the address failed."""
        return self._timestamp

    @property
    def time(self) -> str:
        """The timestamp when the address failed as a pretty string."""
        return self._time

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FailingAddress):
            return False

        return (
            self.address == other.address
            and self.timestamp == other.timestamp
            and self.time == other.time
        )

    def __hash__(self) -> int:
        return hash((self.address, self.timestamp, self.time))


class RoutePlannerType(str, enum.Enum):
    """Route Planner Type.

    The type of routeplanner that the server is currently using.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#route-planner-types)
    """

    ROTATING_ROUTE_PLANNER = "RotatingIpRoutePlanner"
    """Rotating Route Planner.

    IP address used is switched on ban.

    Recommended for IPv4 blocks or IPv6 blocks smaller than a /64.
    """
    NANO_IP_ROUTE_PLANNER = "NanoIpRoutePlanner"
    """Nano IP Route Planner.

    IP address used is switched on clock update.

    Use with at least 1 /64 IPv6 block.
    """
    ROTATING_NANO_IP_ROUTE_PLANNER = "RotatingNanoIpRoutePlanner"
    """Rotating Nano IP Route Planner.

    IP address used is switched on clock update,
    rotates to a different /64 block on ban.

    Use with at least 2x /64 IPv6 blocks.
    """
    BALANCING_IP_ROUTE_PLANNER = "BalancingIpRoutePlanner"
    """Balancing IP Route Planner.

    IP address used is selected at random per request.

    Recommended for larger IP blocks.
    """


class IPBlockType(str, enum.Enum):
    """IP Block Type.

    The IP Block type, IPV4, or IPV6.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#ip-block-type)
    """

    INET_4_ADDRESS = "Inet4Address"
    """The IPV4 block type."""
    INET_6_ADDRESS = "Inet6Address"
    """The IPV6 block type."""
