from __future__ import annotations

from unittest import mock

from ongaku.statistics import Cpu
from ongaku.statistics import FrameStatistics
from ongaku.statistics import Memory
from ongaku.statistics import Statistics


def test_statistics():
    mock_memory = mock.Mock()
    mock_cpu = mock.Mock()
    mock_frame_statistics = mock.Mock()

    statistics = Statistics(
        players=1,
        playing_players=2,
        uptime=3,
        memory=mock_memory,
        cpu=mock_cpu,
        frame_statistics=mock_frame_statistics,
    )

    assert statistics.players == 1
    assert statistics.playing_players == 2
    assert statistics.uptime == 3
    assert statistics.memory == mock_memory
    assert statistics.cpu == mock_cpu
    assert statistics.frame_statistics == mock_frame_statistics


def test_statistics_memory():
    stats_memory = Memory(free=1, used=2, allocated=3, reservable=4)

    assert stats_memory.free == 1
    assert stats_memory.used == 2
    assert stats_memory.allocated == 3
    assert stats_memory.reservable == 4


def test_statistics_cpu():
    stats_cpu = Cpu(cores=1, system_load=2.3, lavalink_load=4.5)

    assert stats_cpu.cores == 1
    assert stats_cpu.system_load == 2.3
    assert stats_cpu.lavalink_load == 4.5


def test_statistics_frame_stats():
    stats_frame_statistics = FrameStatistics(sent=1, nulled=2, deficit=3)

    assert stats_frame_statistics.sent == 1
    assert stats_frame_statistics.nulled == 2
    assert stats_frame_statistics.deficit == 3
