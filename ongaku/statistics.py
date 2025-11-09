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
"""Statistics and entities related to Lavalink statistics objects."""

from __future__ import annotations

import typing

__all__: typing.Sequence[str] = (
    "Cpu",
    "FrameStatistics",
    "Memory",
    "Statistics",
)


class Statistics:
    """Statistics.

    All of the Statistics information.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/websocket.html#stats-object)
    """

    __slots__: typing.Sequence[str] = (
        "_cpu",
        "_frame_statistics",
        "_memory",
        "_players",
        "_playing_players",
        "_uptime",
    )

    def __init__(
        self,
        *,
        players: int,
        playing_players: int,
        uptime: int,
        memory: Memory,
        cpu: Cpu,
        frame_statistics: FrameStatistics | None,
    ) -> None:
        self._players = players
        self._playing_players = playing_players
        self._uptime = uptime
        self._memory = memory
        self._cpu = cpu
        self._frame_statistics = frame_statistics

    @property
    def players(self) -> int:
        """The amount of players connected to the session."""
        return self._players

    @property
    def playing_players(self) -> int:
        """The amount of players playing a track."""
        return self._playing_players

    @property
    def uptime(self) -> int:
        """The uptime of the session in milliseconds."""
        return self._uptime

    @property
    def memory(self) -> Memory:
        """The memory stats of the session."""
        return self._memory

    @property
    def cpu(self) -> Cpu:
        """The CPU stats of the session."""
        return self._cpu

    @property
    def frame_statistics(self) -> FrameStatistics | None:
        """The frame statistics of the session."""
        return self._frame_statistics

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Statistics):
            return False

        return (
            self.players == other.players
            and self.playing_players == other.playing_players
            and self.uptime == other.uptime
            and self.memory == other.memory
            and self.cpu == other.cpu
            and self.frame_statistics == other.frame_statistics
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.players,
                self.playing_players,
                self.uptime,
                self.memory,
                self.cpu,
                self.frame_statistics,
            ),
        )


class Memory:
    """Memory.

    All of the Statistics Memory information.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/websocket.html#memory)
    """

    __slots__: typing.Sequence[str] = ("_allocated", "_free", "_reservable", "_used")

    def __init__(
        self,
        *,
        free: int,
        used: int,
        allocated: int,
        reservable: int,
    ) -> None:
        self._free = free
        self._used = used
        self._allocated = allocated
        self._reservable = reservable

    @property
    def free(self) -> int:
        """The amount of free memory in bytes."""
        return self._free

    @property
    def used(self) -> int:
        """The amount of used memory in bytes."""
        return self._used

    @property
    def allocated(self) -> int:
        """The amount of allocated memory in bytes."""
        return self._allocated

    @property
    def reservable(self) -> int:
        """The amount of reservable memory in bytes."""
        return self._reservable

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Memory):
            return False

        return (
            self.free == other.free
            and self.used == other.used
            and self.allocated == other.allocated
            and self.reservable == other.reservable
        )

    def __hash__(self) -> int:
        return hash((self.free, self.used, self.allocated, self.reservable))


class Cpu:
    """CPU.

    All of the Statistics CPU information.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/websocket.html#cpu)
    """

    __slots__: typing.Sequence[str] = ("_cores", "_lavalink_load", "_system_load")

    def __init__(self, *, cores: int, system_load: float, lavalink_load: float) -> None:
        self._cores = cores
        self._system_load = system_load
        self._lavalink_load = lavalink_load

    @property
    def cores(self) -> int:
        """The amount of cores the server has."""
        return self._cores

    @property
    def system_load(self) -> float:
        """The system load of the server."""
        return self._system_load

    @property
    def lavalink_load(self) -> float:
        """The load of Lavalink on the server."""
        return self._lavalink_load

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cpu):
            return False

        return (
            self.cores == other.cores
            and self.system_load == other.system_load
            and self.lavalink_load == other.lavalink_load
        )

    def __hash__(self) -> int:
        return hash((self.cores, self.system_load, self.lavalink_load))


class FrameStatistics:
    """Frame Statistics.

    All of the Statistics frame statistics information.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/websocket.html#frame-stats)
    """

    __slots__: typing.Sequence[str] = ("_deficit", "_nulled", "_sent")

    def __init__(self, *, sent: int, nulled: int, deficit: int) -> None:
        self._sent = sent
        self._nulled = nulled
        self._deficit = deficit

    @property
    def sent(self) -> int:
        """The amount of frames sent to Discord."""
        return self._sent

    @property
    def nulled(self) -> int:
        """The amount of frames that were nulled."""
        return self._nulled

    @property
    def deficit(self) -> int:
        """The difference between sent frames and the expected amount of frames."""
        return self._deficit

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FrameStatistics):
            return False

        return (
            self.sent == other.sent
            and self.nulled == other.nulled
            and self.deficit == other.deficit
        )

    def __hash__(self) -> int:
        return hash((self.sent, self.nulled, self.deficit))
