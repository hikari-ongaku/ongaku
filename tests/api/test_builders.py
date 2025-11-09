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
from __future__ import annotations

import datetime
import typing
from unittest import mock

import hikari
import pytest

from ongaku import errors
from ongaku import filters
from ongaku import player
from ongaku import routeplanner
from ongaku import track
from ongaku.api.builders import ChannelMixBuilder
from ongaku.api.builders import DistortionBuilder
from ongaku.api.builders import EntityBuilder
from ongaku.api.builders import EqualizerBuilder
from ongaku.api.builders import FiltersBuilder
from ongaku.api.builders import KaraokeBuilder
from ongaku.api.builders import LowPassBuilder
from ongaku.api.builders import RotationBuilder
from ongaku.api.builders import TimescaleBuilder
from ongaku.api.builders import TremoloBuilder
from ongaku.api.builders import VibratoBuilder


class TestEntityBuilder:
    @pytest.fixture
    def entity_builder(self) -> EntityBuilder:
        return EntityBuilder()

    @staticmethod
    def mock_dump(
        _object: typing.Mapping[str, typing.Any] | typing.Sequence[typing.Any],
    ) -> bytes:
        return b"hello world"

    @staticmethod
    def mock_load(_bytes: str | bytes) -> typing.Mapping[str, typing.Any]:
        return {}

    def test_properties(self):
        entity_builder = EntityBuilder(dumps=self.mock_dump, loads=self.mock_load)

        assert entity_builder._dumps == self.mock_dump

        assert entity_builder._loads == self.mock_load

    def test__ensure_mapping(self, entity_builder: EntityBuilder):
        with mock.patch.object(
            entity_builder,
            "_loads",
            side_effect=NotImplementedError,
        ) as patched__loads:
            assert entity_builder._ensure_mapping({"test": "test"}) == {"test": "test"}

        patched__loads.assert_not_called()

    def test__ensure_mapping_from_string(self, entity_builder: EntityBuilder):
        with mock.patch.object(
            entity_builder,
            "_loads",
            return_value={"test": "test"},
        ) as patched__loads:
            assert entity_builder._ensure_mapping('{"test":"test"}') == {"test": "test"}

        patched__loads.assert_called_once_with('{"test":"test"}')

    def test__ensure_sequence(self, entity_builder: EntityBuilder):
        with mock.patch.object(
            entity_builder,
            "_loads",
            side_effect=NotImplementedError,
        ) as patched__loads:
            assert entity_builder._ensure_sequence(["test_1", "test_2"]) == [
                "test_1",
                "test_2",
            ]

        patched__loads.assert_not_called()

    def test__ensure_sequence_from_string(self, entity_builder: EntityBuilder):
        with mock.patch.object(
            entity_builder,
            "_loads",
            return_value=["test_1", "test_2"],
        ) as patched__loads:
            assert entity_builder._ensure_sequence('["test_1", "test_2"]') == [
                "test_1",
                "test_2",
            ]

        patched__loads.assert_called_once_with('["test_1", "test_2"]')

    @pytest.fixture
    def rest_error_payload(self) -> dict[str, typing.Any]:
        return {
            "timestamp": 1000,
            "status": 400,
            "error": "error",
            "message": "message",
            "path": "path",
            "trace": "trace",
        }

    def test_deserialize_rest_error(
        self,
        entity_builder: EntityBuilder,
        rest_error_payload: dict[str, typing.Any],
    ):
        rest_error = entity_builder.deserialize_rest_error(rest_error_payload)

        assert rest_error.timestamp == datetime.datetime.fromtimestamp(
            1,
            datetime.timezone.utc,
        )
        assert rest_error.status == 400
        assert rest_error.error == "error"
        assert rest_error.message == "message"
        assert rest_error.path == "path"
        assert rest_error.trace == "trace"

    def test_deserialize_rest_error_with_nullable(
        self,
        entity_builder: EntityBuilder,
        rest_error_payload: dict[str, typing.Any],
    ):
        rest_error_payload["trace"] = None

        rest_error = entity_builder.deserialize_rest_error(rest_error_payload)

        assert rest_error.timestamp == datetime.datetime.fromtimestamp(
            1,
            datetime.timezone.utc,
        )
        assert rest_error.status == 400
        assert rest_error.error == "error"
        assert rest_error.message == "message"
        assert rest_error.path == "path"
        assert rest_error.trace is None

    @pytest.fixture
    def exception_error_payload(self) -> dict[str, typing.Any]:
        return {
            "message": "message",
            "severity": "common",
            "cause": "cause",
        }

    def test_deserialize_exception_error(
        self,
        entity_builder: EntityBuilder,
        exception_error_payload: dict[str, typing.Any],
    ):
        exception_error = entity_builder.deserialize_exception_error(
            exception_error_payload,
        )

        assert exception_error.message == "message"
        assert exception_error.severity is errors.SeverityType.COMMON
        assert exception_error.cause == "cause"

    def test_deserialize_exception_error_with_null(
        self,
        entity_builder: EntityBuilder,
        exception_error_payload: dict[str, typing.Any],
    ):
        exception_error_payload["message"] = None

        exception_error = entity_builder.deserialize_exception_error(
            exception_error_payload,
        )

        assert exception_error.message is None
        assert exception_error.severity is errors.SeverityType.COMMON
        assert exception_error.cause == "cause"

    @pytest.fixture
    def ready_event_payload(self) -> dict[str, typing.Any]:
        return {
            "op": "ready",
            "resumed": False,
            "sessionId": "session_id",
        }

    def test_deserialize_ready_event(
        self,
        entity_builder: EntityBuilder,
        ready_event_payload: dict[str, typing.Any],
    ):
        session = mock.Mock()

        ready_event = entity_builder.deserialize_ready_event(
            ready_event_payload,
            session=session,
        )

        assert ready_event.session == session
        assert ready_event.resumed is False
        assert ready_event.session_id == "session_id"

    @pytest.fixture
    def player_update_event_payload(
        self,
        player_state_payload: dict[str, typing.Any],
    ) -> dict[str, typing.Any]:
        return {
            "op": "playerUpdate",
            "guildId": 123,
            "state": player_state_payload,
        }

    def test_deserialize_player_update_event(
        self,
        entity_builder: EntityBuilder,
        player_update_event_payload: dict[str, typing.Any],
        player_state_payload: dict[str, typing.Any],
    ):
        session = mock.Mock()

        player_update_event = entity_builder.deserialize_player_update_event(
            player_update_event_payload,
            session=session,
        )

        assert player_update_event.session == session
        assert player_update_event.guild_id == 123
        assert player_update_event.state == entity_builder.deserialize_state(
            player_state_payload,
        )

    def test_deserialize_statistics_event(
        self,
        entity_builder: EntityBuilder,
        statistics_payload: dict[str, typing.Any],
        statistics_memory_payload: dict[str, typing.Any],
        statistics_cpu_payload: dict[str, typing.Any],
        statistics_frame_stats_payload: dict[str, typing.Any],
    ):
        session = mock.Mock()

        statistics_event = entity_builder.deserialize_statistics_event(
            statistics_payload,
            session=session,
        )

        assert statistics_event.session == session
        assert statistics_event.players == 1
        assert statistics_event.playing_players == 2
        assert statistics_event.uptime == 3
        assert statistics_event.memory == entity_builder._deserialize_memory(
            statistics_memory_payload,
        )
        assert statistics_event.cpu == entity_builder._deserialize_cpu(
            statistics_cpu_payload,
        )
        assert (
            statistics_event.frame_statistics
            == entity_builder._deserialize_frame_statistics(
                statistics_frame_stats_payload,
            )
        )

    @pytest.fixture
    def track_start_event_payload(
        self,
        track_payload: dict[str, typing.Any],
    ) -> dict[str, typing.Any]:
        return {
            "op": "event",
            "type": "TrackStartEvent",
            "guildId": 123,
            "track": track_payload,
        }

    def test_deserialize_track_start_event(
        self,
        entity_builder: EntityBuilder,
        track_start_event_payload: dict[str, typing.Any],
        track_payload: dict[str, typing.Any],
    ):
        session = mock.Mock()

        track_start_event = entity_builder.deserialize_track_start_event(
            track_start_event_payload,
            session=session,
        )

        assert track_start_event.session == session
        assert track_start_event.guild_id == hikari.Snowflake(123)
        assert track_start_event.track == entity_builder.deserialize_track(
            track_payload,
        )

    @pytest.fixture
    def track_end_event_payload(
        self,
        track_payload: dict[str, typing.Any],
    ) -> dict[str, typing.Any]:
        return {
            "op": "event",
            "type": "TrackEndEvent",
            "guildId": 123,
            "track": track_payload,
            "reason": "finished",
        }

    def test_deserialize_track_end_event(
        self,
        entity_builder: EntityBuilder,
        track_end_event_payload: dict[str, typing.Any],
        track_payload: dict[str, typing.Any],
    ):
        session = mock.Mock()

        track_end_event = entity_builder.deserialize_track_end_event(
            track_end_event_payload,
            session=session,
        )

        assert track_end_event.session == session
        assert track_end_event.guild_id == hikari.Snowflake(123)
        assert track_end_event.track == entity_builder.deserialize_track(track_payload)
        assert track_end_event.reason == track.TrackEndReasonType.FINISHED

    @pytest.fixture
    def track_exception_event_payload(
        self,
        track_payload: dict[str, typing.Any],
        exception_error_payload: dict[str, typing.Any],
    ) -> dict[str, typing.Any]:
        return {
            "op": "event",
            "type": "TrackExceptionEvent",
            "guildId": 123,
            "track": track_payload,
            "exception": exception_error_payload,
        }

    def test_deserialize_track_exception_event(
        self,
        entity_builder: EntityBuilder,
        track_exception_event_payload: dict[str, typing.Any],
        track_payload: dict[str, typing.Any],
        exception_error_payload: dict[str, typing.Any],
    ):
        session = mock.Mock()

        track_exception_event = entity_builder.deserialize_track_exception_event(
            track_exception_event_payload,
            session=session,
        )

        assert track_exception_event.session == session
        assert track_exception_event.guild_id == hikari.Snowflake(123)
        assert track_exception_event.track == entity_builder.deserialize_track(
            track_payload,
        )
        assert (
            track_exception_event.exception
            == entity_builder.deserialize_exception_error(exception_error_payload)
        )

    @pytest.fixture
    def track_stuck_event_payload(
        self,
        track_payload: dict[str, typing.Any],
    ) -> dict[str, typing.Any]:
        return {
            "op": "event",
            "type": "TrackStuckEvent",
            "guildId": 123,
            "track": track_payload,
            "thresholdMs": 1,
        }

    def test_deserialize_track_stuck_event(
        self,
        entity_builder: EntityBuilder,
        track_stuck_event_payload: dict[str, typing.Any],
        track_payload: dict[str, typing.Any],
    ):
        session = mock.Mock()

        track_stuck_event = entity_builder.deserialize_track_stuck_event(
            track_stuck_event_payload,
            session=session,
        )

        assert track_stuck_event.session == session
        assert track_stuck_event.guild_id == hikari.Snowflake(123)
        assert track_stuck_event.track == entity_builder.deserialize_track(
            track_payload,
        )
        assert track_stuck_event.threshold_ms == 1

    @pytest.fixture
    def websocket_closed_event_payload(self) -> dict[str, typing.Any]:
        return {
            "op": "event",
            "type": "WebSocketClosedEvent",
            "guildId": 123,
            "code": 1,
            "reason": "reason",
            "byRemote": False,
        }

    def test_deserialize_websocket_closed_event(
        self,
        entity_builder: EntityBuilder,
        websocket_closed_event_payload: dict[str, typing.Any],
    ):
        session = mock.Mock()

        websocket_closed_event = entity_builder.deserialize_websocket_closed_event(
            websocket_closed_event_payload,
            session=session,
        )

        assert websocket_closed_event.session == session
        assert websocket_closed_event.guild_id == 123
        assert websocket_closed_event.code == 1
        assert websocket_closed_event.reason == "reason"
        assert websocket_closed_event.by_remote is False

    @pytest.fixture
    def filters_payload(
        self,
        filters_equalizer_payload: dict[str, typing.Any],
        filters_karaoke_payload: dict[str, typing.Any],
        filters_timescale_payload: dict[str, typing.Any],
        filters_tremolo_payload: dict[str, typing.Any],
        filters_vibrato_payload: dict[str, typing.Any],
        filters_rotation_payload: dict[str, typing.Any],
        filters_distortion_payload: dict[str, typing.Any],
        filters_channel_mix_payload: dict[str, typing.Any],
        filters_low_pass_payload: dict[str, typing.Any],
    ) -> dict[str, typing.Any]:
        return {
            "volume": 1.2,
            "equalizer": [filters_equalizer_payload],
            "karaoke": filters_karaoke_payload,
            "timescale": filters_timescale_payload,
            "tremolo": filters_tremolo_payload,
            "vibrato": filters_vibrato_payload,
            "rotation": filters_rotation_payload,
            "distortion": filters_distortion_payload,
            "channelMix": filters_channel_mix_payload,
            "lowPass": filters_low_pass_payload,
        }

    @pytest.fixture
    def filters_equalizer_payload(self) -> dict[str, typing.Any]:
        return {"band": 3, "gain": 0.95}

    @pytest.fixture
    def filters_karaoke_payload(self) -> dict[str, typing.Any]:
        return {
            "level": 1,
            "monoLevel": 0.5,
            "filterBand": 4.5,
            "filterWidth": 6,
        }

    @pytest.fixture
    def filters_timescale_payload(self) -> dict[str, typing.Any]:
        return {"speed": 1.2, "pitch": 2.3, "rate": 4}

    @pytest.fixture
    def filters_tremolo_payload(self) -> dict[str, typing.Any]:
        return {"frequency": 1.2, "depth": 1}

    @pytest.fixture
    def filters_vibrato_payload(self) -> dict[str, typing.Any]:
        return {"frequency": 3, "depth": 0.5}

    @pytest.fixture
    def filters_rotation_payload(self) -> dict[str, typing.Any]:
        return {"rotationHz": 6}

    @pytest.fixture
    def filters_distortion_payload(self) -> dict[str, typing.Any]:
        return {
            "sinOffset": 2.1,
            "sinScale": 3,
            "cosOffset": 6.9,
            "cosScale": 7.2,
            "tanOffset": 9.4,
            "tanScale": 2,
            "offset": 4.1,
            "scale": 8,
        }

    @pytest.fixture
    def filters_channel_mix_payload(self) -> dict[str, typing.Any]:
        return {
            "leftToLeft": 0,
            "leftToRight": 1,
            "rightToLeft": 0.5,
            "rightToRight": 0.63,
        }

    @pytest.fixture
    def filters_low_pass_payload(self) -> dict[str, typing.Any]:
        return {"smoothing": 3.8}

    def test_deserialize_filters(
        self,
        entity_builder: EntityBuilder,
        filters_payload: dict[str, typing.Any],
        filters_equalizer_payload: dict[str, typing.Any],
        filters_karaoke_payload: dict[str, typing.Any],
        filters_timescale_payload: dict[str, typing.Any],
        filters_tremolo_payload: dict[str, typing.Any],
        filters_vibrato_payload: dict[str, typing.Any],
        filters_rotation_payload: dict[str, typing.Any],
        filters_distortion_payload: dict[str, typing.Any],
        filters_channel_mix_payload: dict[str, typing.Any],
        filters_low_pass_payload: dict[str, typing.Any],
    ):
        filters = entity_builder.deserialize_filters(filters_payload)

        assert filters.volume == 1.2
        assert filters.equalizer == [
            entity_builder._deserialize_equalizer(filters_equalizer_payload),
        ]
        assert filters.karaoke == entity_builder._deserialize_karaoke(
            filters_karaoke_payload,
        )
        assert filters.timescale == entity_builder._deserialize_timescale(
            filters_timescale_payload,
        )
        assert filters.tremolo == entity_builder._deserialize_tremolo(
            filters_tremolo_payload,
        )
        assert filters.vibrato == entity_builder._deserialize_vibrato(
            filters_vibrato_payload,
        )
        assert filters.rotation == entity_builder._deserialize_rotation(
            filters_rotation_payload,
        )
        assert filters.distortion == entity_builder._deserialize_distortion(
            filters_distortion_payload,
        )
        assert filters.channel_mix == entity_builder._deserialize_channel_mix(
            filters_channel_mix_payload,
        )
        assert filters.low_pass == entity_builder._deserialize_low_pass(
            filters_low_pass_payload,
        )

    def test_deserialize_filters_with_null(self, entity_builder: EntityBuilder):
        filters = entity_builder.deserialize_filters({})

        assert filters.volume is None
        assert filters.equalizer == []
        assert filters.karaoke is None
        assert filters.timescale is None
        assert filters.tremolo is None
        assert filters.vibrato is None
        assert filters.rotation is None
        assert filters.distortion is None
        assert filters.channel_mix is None
        assert filters.low_pass is None

    def test__deserialize_equalizer(
        self,
        entity_builder: EntityBuilder,
        filters_equalizer_payload: dict[str, typing.Any],
    ):
        equalizer = entity_builder._deserialize_equalizer(filters_equalizer_payload)

        assert equalizer.band == 3
        assert equalizer.gain == 0.95

    def test__deserialize_karaoke(
        self,
        entity_builder: EntityBuilder,
        filters_karaoke_payload: dict[str, typing.Any],
    ):
        karaoke = entity_builder._deserialize_karaoke(filters_karaoke_payload)

        assert karaoke.level == 1
        assert karaoke.mono_level == 0.5
        assert karaoke.filter_band == 4.5
        assert karaoke.filter_width == 6

    def test__deserialize_karaoke_with_null(self, entity_builder: EntityBuilder):
        karaoke = entity_builder._deserialize_karaoke({})

        assert karaoke.level is None
        assert karaoke.mono_level is None
        assert karaoke.filter_band is None
        assert karaoke.filter_width is None

    def test__deserialize_timescale(
        self,
        entity_builder: EntityBuilder,
        filters_timescale_payload: dict[str, typing.Any],
    ):
        timescale = entity_builder._deserialize_timescale(filters_timescale_payload)

        assert timescale.speed == 1.2
        assert timescale.pitch == 2.3
        assert timescale.rate == 4

    def test__deserialize_timescale_with_null(self, entity_builder: EntityBuilder):
        timescale = entity_builder._deserialize_timescale({})

        assert timescale.speed is None
        assert timescale.pitch is None
        assert timescale.rate is None

    def test__deserialize_tremolo(
        self,
        entity_builder: EntityBuilder,
        filters_tremolo_payload: dict[str, typing.Any],
    ):
        tremolo = entity_builder._deserialize_tremolo(filters_tremolo_payload)

        assert tremolo.frequency == 1.2
        assert tremolo.depth == 1

    def test__deserialize_tremolo_with_null(self, entity_builder: EntityBuilder):
        tremolo = entity_builder._deserialize_tremolo({})

        assert tremolo.frequency is None
        assert tremolo.depth is None

    def test__deserialize_vibrato(
        self,
        entity_builder: EntityBuilder,
        filters_vibrato_payload: dict[str, typing.Any],
    ):
        vibrato = entity_builder._deserialize_vibrato(filters_vibrato_payload)

        assert vibrato.frequency == 3
        assert vibrato.depth == 0.5

    def test__deserialize_vibrato_with_null(self, entity_builder: EntityBuilder):
        vibrato = entity_builder._deserialize_vibrato({})

        assert vibrato.frequency is None
        assert vibrato.depth is None

    def test__deserialize_rotation(
        self,
        entity_builder: EntityBuilder,
        filters_rotation_payload: dict[str, typing.Any],
    ):
        rotation = entity_builder._deserialize_rotation(filters_rotation_payload)

        assert rotation.rotation_hz == 6

    def test__deserialize_rotation_with_null(self, entity_builder: EntityBuilder):
        rotation = entity_builder._deserialize_rotation({})

        assert rotation.rotation_hz is None

    def test__deserialize_distortion(
        self,
        entity_builder: EntityBuilder,
        filters_distortion_payload: dict[str, typing.Any],
    ):
        distortion = entity_builder._deserialize_distortion(filters_distortion_payload)

        assert distortion.sin_offset == 2.1
        assert distortion.sin_scale == 3
        assert distortion.cos_offset == 6.9
        assert distortion.cos_scale == 7.2
        assert distortion.tan_offset == 9.4
        assert distortion.tan_scale == 2
        assert distortion.offset == 4.1
        assert distortion.scale == 8

    def test__deserialize_distortion_with_null(self, entity_builder: EntityBuilder):
        distortion = entity_builder._deserialize_distortion({})

        assert distortion.sin_offset is None
        assert distortion.sin_scale is None
        assert distortion.cos_offset is None
        assert distortion.cos_scale is None
        assert distortion.tan_offset is None
        assert distortion.tan_scale is None
        assert distortion.offset is None
        assert distortion.scale is None

    def test__deserialize_channel_mix(
        self,
        entity_builder: EntityBuilder,
        filters_channel_mix_payload: dict[str, typing.Any],
    ):
        channel_mix = entity_builder._deserialize_channel_mix(
            filters_channel_mix_payload,
        )

        assert channel_mix.left_to_left == 0
        assert channel_mix.left_to_right == 1
        assert channel_mix.right_to_left == 0.5
        assert channel_mix.right_to_right == 0.63

    def test__deserialize_channel_mix_with_null(self, entity_builder: EntityBuilder):
        channel_mix = entity_builder._deserialize_channel_mix({})

        assert channel_mix.left_to_left is None
        assert channel_mix.left_to_right is None
        assert channel_mix.right_to_left is None
        assert channel_mix.right_to_right is None

    def test__deserialize_low_pass(
        self,
        entity_builder: EntityBuilder,
        filters_low_pass_payload: dict[str, typing.Any],
    ):
        low_pass = entity_builder._deserialize_low_pass(filters_low_pass_payload)

        assert low_pass.smoothing == 3.8

    def test__deserialize_low_pass_with_null(self, entity_builder: EntityBuilder):
        low_pass = entity_builder._deserialize_low_pass({})

        assert low_pass.smoothing is None

    @pytest.fixture
    def information_payload(
        self,
        information_version_payload: dict[str, typing.Any],
        information_git_payload: dict[str, typing.Any],
        information_plugin_payload: dict[str, typing.Any],
    ) -> dict[str, typing.Any]:
        return {
            "version": information_version_payload,
            "buildTime": 1000,
            "git": information_git_payload,
            "jvm": "jvm",
            "lavaplayer": "lavaplayer",
            "sourceManagers": ["source_manager_1", "source_manager_2"],
            "filters": ["filter_1", "filter_2"],
            "plugins": [information_plugin_payload],
        }

    @pytest.fixture
    def information_version_payload(self) -> dict[str, typing.Any]:
        return {
            "semver": "semver",
            "major": 1,
            "minor": 2,
            "patch": 3,
            "preRelease": "pre_release",
            "build": "build",
        }

    @pytest.fixture
    def information_git_payload(self) -> dict[str, typing.Any]:
        return {"branch": "branch", "commit": "commit", "commitTime": 1000}

    @pytest.fixture
    def information_plugin_payload(self) -> dict[str, typing.Any]:
        return {"name": "name", "version": "version"}

    def test_deserialize_information(
        self,
        entity_builder: EntityBuilder,
        information_payload: dict[str, typing.Any],
        information_version_payload: dict[str, typing.Any],
        information_git_payload: dict[str, typing.Any],
        information_plugin_payload: dict[str, typing.Any],
    ):
        information = entity_builder.deserialize_information(information_payload)

        assert information.version == entity_builder._deserialize_version(
            information_version_payload,
        )
        assert information.build_time == datetime.datetime.fromtimestamp(
            1,
            datetime.timezone.utc,
        )
        assert information.git == entity_builder._deserialize_git(
            information_git_payload,
        )
        assert information.jvm == "jvm"
        assert information.lavaplayer == "lavaplayer"
        assert information.source_managers == ["source_manager_1", "source_manager_2"]
        assert information.filters == ["filter_1", "filter_2"]
        assert information.plugins == [
            entity_builder._deserialize_plugin(information_plugin_payload),
        ]

    def test__deserialize_version(
        self,
        entity_builder: EntityBuilder,
        information_version_payload: dict[str, typing.Any],
    ):
        version = entity_builder._deserialize_version(information_version_payload)

        assert version.semver == "semver"
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.pre_release == "pre_release"
        assert version.build == "build"

    def test__deserialize_version_with_null(
        self,
        entity_builder: EntityBuilder,
        information_version_payload: dict[str, typing.Any],
    ):
        del information_version_payload["build"]

        version = entity_builder._deserialize_version(information_version_payload)

        assert version.semver == "semver"
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.pre_release == "pre_release"
        assert version.build is None

    def test__deserialize_git(
        self,
        entity_builder: EntityBuilder,
        information_git_payload: dict[str, typing.Any],
    ):
        git = entity_builder._deserialize_git(information_git_payload)

        assert git.branch == "branch"
        assert git.commit == "commit"
        assert git.commit_time == datetime.datetime.fromtimestamp(
            1,
            datetime.timezone.utc,
        )

    def test__deserialize_plugin(
        self,
        entity_builder: EntityBuilder,
        information_plugin_payload: dict[str, typing.Any],
    ):
        plugin = entity_builder._deserialize_plugin(information_plugin_payload)

        assert plugin.name == "name"
        assert plugin.version == "version"

    @pytest.fixture
    def player_payload(
        self,
        track_payload: dict[str, typing.Any],
        player_state_payload: dict[str, typing.Any],
        player_voice_payload: dict[str, typing.Any],
        filters_payload: dict[str, typing.Any],
    ) -> dict[str, typing.Any]:
        return {
            "guildId": 123,
            "track": track_payload,
            "volume": 1,
            "paused": True,
            "state": player_state_payload,
            "voice": player_voice_payload,
            "filters": filters_payload,
        }

    @pytest.fixture
    def player_state_payload(self) -> dict[str, typing.Any]:
        return {
            "time": 1000,
            "position": 2,
            "connected": True,
            "ping": 3,
        }

    @pytest.fixture
    def player_voice_payload(self) -> dict[str, typing.Any]:
        return {
            "token": "token",
            "endpoint": "endpoint",
            "sessionId": "session_id",
        }

    def test_deserialize_player(
        self,
        entity_builder: EntityBuilder,
        player_payload: dict[str, typing.Any],
        player_state_payload: dict[str, typing.Any],
        player_voice_payload: dict[str, typing.Any],
        track_payload: dict[str, typing.Any],
        filters_payload: dict[str, typing.Any],
    ):
        player = entity_builder.deserialize_player(player_payload)

        assert player.guild_id == 123
        assert player.track == entity_builder.deserialize_track(track_payload)
        assert player.volume == 1
        assert player.is_paused is True
        assert player.state == entity_builder.deserialize_state(player_state_payload)
        assert player.voice == entity_builder._deserialize_voice(player_voice_payload)
        assert player.filters == entity_builder.deserialize_filters(filters_payload)

    def test_deserialize_player_with_null(
        self,
        entity_builder: EntityBuilder,
        player_payload: dict[str, typing.Any],
        player_state_payload: dict[str, typing.Any],
        player_voice_payload: dict[str, typing.Any],
    ):
        player_payload["track"] = None
        player_payload["filters"] = None

        player = entity_builder.deserialize_player(player_payload)

        assert player.guild_id == 123
        assert player.track is None
        assert player.volume == 1
        assert player.is_paused is True
        assert player.state == entity_builder.deserialize_state(player_state_payload)
        assert player.voice == entity_builder._deserialize_voice(player_voice_payload)
        assert player.filters is None

    def test_deserialize_state(
        self,
        entity_builder: EntityBuilder,
        player_state_payload: dict[str, typing.Any],
    ):
        state = entity_builder.deserialize_state(player_state_payload)

        assert state.time == datetime.datetime.fromtimestamp(1, datetime.timezone.utc)
        assert state.position == 2
        assert state.is_connected is True
        assert state.ping == 3

    def test__deserialize_voice(
        self,
        entity_builder: EntityBuilder,
        player_voice_payload: dict[str, typing.Any],
    ):
        voice = entity_builder._deserialize_voice(player_voice_payload)

        assert voice.token == "token"
        assert voice.endpoint == "endpoint"
        assert voice.session_id == "session_id"

    @pytest.fixture
    def playlist_payload(
        self,
        playlist_info_payload: dict[str, typing.Any],
        track_payload: dict[str, typing.Any],
    ) -> dict[str, typing.Any]:
        return {
            "info": playlist_info_payload,
            "pluginInfo": {},
            "tracks": [track_payload],
        }

    @pytest.fixture
    def playlist_info_payload(self) -> dict[str, typing.Any]:
        return {"name": "name", "selectedTrack": 1}

    def test_deserialize_playlist(
        self,
        entity_builder: EntityBuilder,
        playlist_payload: dict[str, typing.Any],
        playlist_info_payload: dict[str, typing.Any],
        track_payload: dict[str, typing.Any],
    ):
        playlist = entity_builder.deserialize_playlist(playlist_payload)

        assert playlist.info == entity_builder._deserialize_playlist_info(
            playlist_info_payload,
        )
        assert playlist.tracks == [entity_builder.deserialize_track(track_payload)]
        assert playlist.plugin_info == {}

    def test__deserialize_playlist_info(
        self,
        entity_builder: EntityBuilder,
        playlist_info_payload: dict[str, typing.Any],
    ):
        playlist_info = entity_builder._deserialize_playlist_info(playlist_info_payload)

        assert playlist_info.name == "name"
        assert playlist_info.selected_track == 1

    @pytest.fixture
    def routeplanner_status_payload(
        self,
        routeplanner_details_payload: dict[str, typing.Any],
    ) -> dict[str, typing.Any]:
        return {
            "class": "RotatingIpRoutePlanner",
            "details": routeplanner_details_payload,
        }

    @pytest.fixture
    def routeplanner_details_payload(
        self,
        routeplanner_ip_block_payload: dict[str, typing.Any],
        routeplanner_failing_address_payload: dict[str, typing.Any],
    ) -> dict[str, typing.Any]:
        return {
            "ipBlock": routeplanner_ip_block_payload,
            "failingAddresses": [routeplanner_failing_address_payload],
            "rotateIndex": "rotate_index",
            "ipIndex": "ip_index",
            "currentAddress": "current_address",
            "currentAddressIndex": "current_address_index",
            "blockIndex": "block_index",
        }

    @pytest.fixture
    def routeplanner_ip_block_payload(self) -> dict[str, typing.Any]:
        return {"type": "Inet4Address", "size": "size"}

    @pytest.fixture
    def routeplanner_failing_address_payload(self) -> dict[str, typing.Any]:
        return {
            "failingAddress": "failing_address",
            "failingTimestamp": 1000,
            "failingTime": "failing_time",
        }

    def test_deserialize_routeplanner_status(
        self,
        entity_builder: EntityBuilder,
        routeplanner_status_payload: dict[str, typing.Any],
        routeplanner_details_payload: dict[str, typing.Any],
    ):
        routeplanner_status = entity_builder.deserialize_routeplanner_status(
            routeplanner_status_payload,
        )

        assert (
            routeplanner_status.cls
            == routeplanner.RoutePlannerType.ROTATING_ROUTE_PLANNER
        )
        assert (
            routeplanner_status.details
            == entity_builder._deserialize_routeplanner_details(
                routeplanner_details_payload,
            )
        )

    def test__deserialize_routeplanner_details(
        self,
        entity_builder: EntityBuilder,
        routeplanner_details_payload: dict[str, typing.Any],
        routeplanner_ip_block_payload: dict[str, typing.Any],
        routeplanner_failing_address_payload: dict[str, typing.Any],
    ):
        routeplanner_details = entity_builder._deserialize_routeplanner_details(
            routeplanner_details_payload,
        )

        assert (
            routeplanner_details.ip_block
            == entity_builder._deserialize_routeplanner_ipblock(
                routeplanner_ip_block_payload,
            )
        )
        assert routeplanner_details.failing_addresses == [
            entity_builder._deserialize_routeplanner_failing_address(
                routeplanner_failing_address_payload,
            ),
        ]
        assert routeplanner_details.rotate_index == "rotate_index"
        assert routeplanner_details.ip_index == "ip_index"
        assert routeplanner_details.current_address == "current_address"
        assert routeplanner_details.current_address_index == "current_address_index"
        assert routeplanner_details.block_index == "block_index"

    def test__deserialize_routeplanner_details_with_null(
        self,
        entity_builder: EntityBuilder,
        routeplanner_details_payload: dict[str, typing.Any],
        routeplanner_ip_block_payload: dict[str, typing.Any],
    ):
        routeplanner_details_payload["failingAddresses"] = []
        routeplanner_details_payload["rotateIndex"] = None
        routeplanner_details_payload["ipIndex"] = None
        routeplanner_details_payload["currentAddress"] = None
        routeplanner_details_payload["currentAddressIndex"] = None
        routeplanner_details_payload["blockIndex"] = None

        routeplanner_details = entity_builder._deserialize_routeplanner_details(
            routeplanner_details_payload,
        )

        assert (
            routeplanner_details.ip_block
            == entity_builder._deserialize_routeplanner_ipblock(
                routeplanner_ip_block_payload,
            )
        )
        assert routeplanner_details.failing_addresses == []
        assert routeplanner_details.rotate_index is None
        assert routeplanner_details.ip_index is None
        assert routeplanner_details.current_address is None
        assert routeplanner_details.current_address_index is None
        assert routeplanner_details.block_index is None

    def test__deserialize_routeplanner_ipblock(
        self,
        entity_builder: EntityBuilder,
        routeplanner_ip_block_payload: dict[str, typing.Any],
    ):
        ip_block = entity_builder._deserialize_routeplanner_ipblock(
            routeplanner_ip_block_payload,
        )

        assert ip_block.type == routeplanner.IPBlockType.INET_4_ADDRESS
        assert ip_block.size == "size"

    def test__deserialize_routeplanner_failing_address(
        self,
        entity_builder: EntityBuilder,
        routeplanner_failing_address_payload: dict[str, typing.Any],
    ):
        failing_address = entity_builder._deserialize_routeplanner_failing_address(
            routeplanner_failing_address_payload,
        )

        assert failing_address.address == "failing_address"
        assert failing_address.timestamp == datetime.datetime.fromtimestamp(
            1,
            datetime.timezone.utc,
        )
        assert failing_address.time == "failing_time"

    @pytest.fixture
    def session_payload(self) -> dict[str, typing.Any]:
        return {"resuming": True, "timeout": 1}

    def test_deserialize_session(
        self,
        entity_builder: EntityBuilder,
        session_payload: dict[str, typing.Any],
    ):
        session = entity_builder.deserialize_session(session_payload)

        assert session.resuming is True
        assert session.timeout == 1

    @pytest.fixture
    def statistics_payload(
        self,
        statistics_memory_payload: dict[str, typing.Any],
        statistics_cpu_payload: dict[str, typing.Any],
        statistics_frame_stats_payload: dict[str, typing.Any],
    ) -> dict[str, typing.Any]:
        return {
            "players": 1,
            "playingPlayers": 2,
            "uptime": 3,
            "memory": statistics_memory_payload,
            "cpu": statistics_cpu_payload,
            "frameStats": statistics_frame_stats_payload,
        }

    @pytest.fixture
    def statistics_memory_payload(self) -> dict[str, typing.Any]:
        return {
            "free": 1,
            "used": 2,
            "allocated": 3,
            "reservable": 4,
        }

    @pytest.fixture
    def statistics_cpu_payload(self) -> dict[str, typing.Any]:
        return {"cores": 1, "systemLoad": 2.3, "lavalinkLoad": 4.5}

    @pytest.fixture
    def statistics_frame_stats_payload(self) -> dict[str, typing.Any]:
        return {"sent": 1, "nulled": 2, "deficit": 3}

    def test_deserialize_statistics(
        self,
        entity_builder: EntityBuilder,
        statistics_payload: dict[str, typing.Any],
        statistics_memory_payload: dict[str, typing.Any],
        statistics_cpu_payload: dict[str, typing.Any],
        statistics_frame_stats_payload: dict[str, typing.Any],
    ):
        statistics = entity_builder.deserialize_statistics(statistics_payload)

        assert statistics.players == 1
        assert statistics.playing_players == 2
        assert statistics.uptime == 3
        assert statistics.memory == entity_builder._deserialize_memory(
            statistics_memory_payload,
        )
        assert statistics.cpu == entity_builder._deserialize_cpu(statistics_cpu_payload)
        assert (
            statistics.frame_statistics
            == entity_builder._deserialize_frame_statistics(
                statistics_frame_stats_payload,
            )
        )

    def test_deserialize_statistics_with_null(
        self,
        entity_builder: EntityBuilder,
        statistics_payload: dict[str, typing.Any],
        statistics_memory_payload: dict[str, typing.Any],
        statistics_cpu_payload: dict[str, typing.Any],
    ):
        statistics_payload["frameStats"] = None

        statistics = entity_builder.deserialize_statistics(statistics_payload)

        assert statistics.players == 1
        assert statistics.playing_players == 2
        assert statistics.uptime == 3
        assert statistics.memory == entity_builder._deserialize_memory(
            statistics_memory_payload,
        )
        assert statistics.cpu == entity_builder._deserialize_cpu(statistics_cpu_payload)
        assert statistics.frame_statistics is None

    def test__deserialize_memory(
        self,
        entity_builder: EntityBuilder,
        statistics_memory_payload: dict[str, typing.Any],
    ):
        memory = entity_builder._deserialize_memory(statistics_memory_payload)

        assert memory.free == 1
        assert memory.used == 2
        assert memory.allocated == 3
        assert memory.reservable == 4

    def test__deserialize_cpu(
        self,
        entity_builder: EntityBuilder,
        statistics_cpu_payload: dict[str, typing.Any],
    ):
        cpu = entity_builder._deserialize_cpu(statistics_cpu_payload)

        assert cpu.cores == 1
        assert cpu.system_load == 2.3
        assert cpu.lavalink_load == 4.5

    def test__deserialize_frame_statistics(
        self,
        entity_builder: EntityBuilder,
        statistics_frame_stats_payload: dict[str, typing.Any],
    ):
        frame_statistics = entity_builder._deserialize_frame_statistics(
            statistics_frame_stats_payload,
        )

        assert frame_statistics.sent == 1
        assert frame_statistics.nulled == 2
        assert frame_statistics.deficit == 3

    @pytest.fixture
    def track_payload(
        self,
        track_info_payload: dict[str, typing.Any],
    ) -> dict[str, typing.Any]:
        return {
            "encoded": "encoded",
            "info": track_info_payload,
            "pluginInfo": {},
            "userData": {},
        }

    @pytest.fixture
    def track_info_payload(self) -> dict[str, typing.Any]:
        return {
            "identifier": "identifier",
            "isSeekable": False,
            "author": "author",
            "length": 1,
            "isStream": True,
            "position": 2,
            "title": "title",
            "sourceName": "source_name",
            "uri": "uri",
            "artworkUrl": "artwork_url",
            "isrc": "isrc",
        }

    def test_deserialize_track(
        self,
        entity_builder: EntityBuilder,
        track_payload: dict[str, typing.Any],
        track_info_payload: dict[str, typing.Any],
    ):
        track = entity_builder.deserialize_track(track_payload)

        assert track.encoded == "encoded"
        assert track.info == entity_builder._deserialize_track_info(track_info_payload)
        assert track.plugin_info == {}
        assert track.user_data == {}
        assert track.requestor is None

    def test_deserialize_track_with_requestor(
        self,
        entity_builder: EntityBuilder,
        track_payload: dict[str, typing.Any],
        track_info_payload: dict[str, typing.Any],
    ):
        track_payload["userData"] = {"ongaku_requestor": 123}

        track = entity_builder.deserialize_track(track_payload)

        assert track.encoded == "encoded"
        assert track.info == entity_builder._deserialize_track_info(track_info_payload)
        assert track.plugin_info == {}
        assert track.user_data == {}
        assert track.requestor == hikari.Snowflake(123)

    def test_deserialize_track_info(
        self,
        entity_builder: EntityBuilder,
        track_info_payload: dict[str, typing.Any],
    ):
        track_info = entity_builder._deserialize_track_info(track_info_payload)

        assert track_info.identifier == "identifier"
        assert track_info.is_seekable is False
        assert track_info.author == "author"
        assert track_info.length == 1
        assert track_info.is_stream is True
        assert track_info.position == 2
        assert track_info.title == "title"
        assert track_info.source_name == "source_name"
        assert track_info.uri == "uri"
        assert track_info.artwork_url == "artwork_url"
        assert track_info.isrc == "isrc"

    def test_deserialize_track_info_with_null(
        self,
        entity_builder: EntityBuilder,
        track_info_payload: dict[str, typing.Any],
    ):
        track_info_payload["uri"] = None
        track_info_payload["artworkUrl"] = None
        track_info_payload["isrc"] = None

        track_info = entity_builder._deserialize_track_info(track_info_payload)

        assert track_info.identifier == "identifier"
        assert track_info.is_seekable is False
        assert track_info.author == "author"
        assert track_info.length == 1
        assert track_info.is_stream is True
        assert track_info.position == 2
        assert track_info.title == "title"
        assert track_info.source_name == "source_name"
        assert track_info.uri is None
        assert track_info.artwork_url is None
        assert track_info.isrc is None

    def test_serialize_voice(
        self,
        entity_builder: EntityBuilder,
        player_voice_payload: dict[str, typing.Any],
    ):
        voice = player.Voice(
            token="token",
            endpoint="endpoint",
            session_id="session_id",
        )

        assert entity_builder.serialize_voice(voice) == player_voice_payload


class TestFiltersBuilder:
    def test_properties(self):
        mock_equalizer_1 = mock.Mock()
        mock_equalizer_2 = mock.Mock()
        mock_karaoke = mock.Mock()
        mock_timescale = mock.Mock()
        mock_tremolo = mock.Mock()
        mock_vibrato = mock.Mock()
        mock_rotation = mock.Mock()
        mock_distortion = mock.Mock()
        mock_channel_mix = mock.Mock()
        mock_low_pass = mock.Mock()

        filters_builder = FiltersBuilder(
            volume=1.5,
            equalizer=[mock_equalizer_1, mock_equalizer_2],
            karaoke=mock_karaoke,
            timescale=mock_timescale,
            tremolo=mock_tremolo,
            vibrato=mock_vibrato,
            rotation=mock_rotation,
            distortion=mock_distortion,
            channel_mix=mock_channel_mix,
            low_pass=mock_low_pass,
            plugin_filters={"plugin": "filters"},
        )

        assert filters_builder.volume == 1.5
        assert filters_builder.equalizer == {mock_equalizer_1, mock_equalizer_2}
        assert filters_builder.karaoke == mock_karaoke
        assert filters_builder.timescale == mock_timescale
        assert filters_builder.tremolo == mock_tremolo
        assert filters_builder.vibrato == mock_vibrato
        assert filters_builder.rotation == mock_rotation
        assert filters_builder.distortion == mock_distortion
        assert filters_builder.channel_mix == mock_channel_mix
        assert filters_builder.low_pass == mock_low_pass
        assert filters_builder.plugin_filters == {"plugin": "filters"}

    def test_from_filter(self):
        filters_builder = FiltersBuilder.from_filter(
            filters.Filters(
                volume=1.2,
                equalizer=[
                    filters.Equalizer(band=filters.BandType.HZ25, gain=3),
                    filters.Equalizer(band=filters.BandType.HZ40, gain=4.5),
                ],
                karaoke=filters.Karaoke(
                    level=6,
                    mono_level=7.8,
                    filter_band=9,
                    filter_width=10.11,
                ),
                timescale=filters.Timescale(
                    speed=12,
                    pitch=13.14,
                    rate=15,
                ),
                tremolo=filters.Tremolo(
                    frequency=16.17,
                    depth=18,
                ),
                vibrato=filters.Vibrato(
                    frequency=19.20,
                    depth=21,
                ),
                rotation=filters.Rotation(
                    rotation_hz=22.23,
                ),
                distortion=filters.Distortion(
                    sin_offset=24,
                    sin_scale=25.26,
                    cos_offset=27,
                    cos_scale=28.29,
                    tan_offset=30,
                    tan_scale=31.32,
                    offset=33,
                    scale=34.35,
                ),
                channel_mix=filters.ChannelMix(
                    left_to_left=36,
                    left_to_right=37.38,
                    right_to_left=39,
                    right_to_right=40.41,
                ),
                low_pass=filters.LowPass(smoothing=42),
                plugin_filters={"plugin": "filters"},
            ),
        )

        assert filters_builder.volume == 1.2
        assert filters_builder.equalizer == {
            EqualizerBuilder(band=filters.BandType.HZ25, gain=3),
            EqualizerBuilder(band=filters.BandType.HZ40, gain=4.5),
        }
        assert filters_builder.karaoke == KaraokeBuilder(
            level=6,
            mono_level=7.8,
            filter_band=9,
            filter_width=10.11,
        )
        assert filters_builder.timescale == TimescaleBuilder(
            speed=12,
            pitch=13.14,
            rate=15,
        )
        assert filters_builder.tremolo == TremoloBuilder(
            frequency=16.17,
            depth=18,
        )
        assert filters_builder.vibrato == VibratoBuilder(
            frequency=19.20,
            depth=21,
        )
        assert filters_builder.rotation == RotationBuilder(rotation_hz=22.23)
        assert filters_builder.distortion == DistortionBuilder(
            sin_offset=24,
            sin_scale=25.26,
            cos_offset=27,
            cos_scale=28.29,
            tan_offset=30,
            tan_scale=31.32,
            offset=33,
            scale=34.35,
        )
        assert filters_builder.channel_mix == ChannelMixBuilder(
            left_to_left=36,
            left_to_right=37.38,
            right_to_left=39,
            right_to_right=40.41,
        )
        assert filters_builder.low_pass == LowPassBuilder(smoothing=42)
        assert filters_builder.plugin_filters == {"plugin": "filters"}

    def test_set_volume(self):
        filters_builder = FiltersBuilder()

        assert filters_builder.volume is None

        filters_builder.set_volume(1)

        assert filters_builder.volume == 1

    def test_set_volume_with_invalid(self):
        filters_builder = FiltersBuilder()

        with pytest.raises(ValueError, match=r"^$"):
            filters_builder.set_volume(-1)

    def test_add_equalizer(self):
        filters_builder = FiltersBuilder()

        filters_builder.add_equalizer(filters.BandType.HZ100, 1)

        assert filters_builder.equalizer == {
            EqualizerBuilder(band=filters.BandType.HZ100, gain=1),
        }

    def test_remove_equalizer(self):
        filters_builder = FiltersBuilder(
            equalizer=[EqualizerBuilder(band=filters.BandType.HZ100, gain=1)],
        )

        filters_builder.remove_equalizer(filters.BandType.HZ100)

        assert filters_builder.equalizer == set()

    def test_remove_equalizer_with_invalid(self):
        filters_builder = FiltersBuilder()

        with pytest.raises(IndexError, match=r"^$"):
            filters_builder.remove_equalizer(filters.BandType.HZ100)

    def test_clear_equalizer(self):
        filters_builder = FiltersBuilder(
            equalizer=[
                EqualizerBuilder(band=filters.BandType.HZ100, gain=1),
                EqualizerBuilder(band=filters.BandType.HZ2500, gain=2.3),
            ],
        )

        filters_builder.clear_equalizer()

        assert filters_builder.equalizer == set()

    def test_set_karaoke(self):
        filters_builder = FiltersBuilder()

        assert filters_builder.karaoke is None

        filters_builder.set_karaoke(
            level=1,
            mono_level=2.3,
            filter_band=4,
            filter_width=5.6,
        )

        assert filters_builder.karaoke == KaraokeBuilder(
            level=1,
            mono_level=2.3,
            filter_band=4,
            filter_width=5.6,
        )

    def test_set_karaoke_with_existing(self):
        filters_builder = FiltersBuilder(
            karaoke=KaraokeBuilder(
                level=1,
                mono_level=2.3,
                filter_band=4,
                filter_width=5.6,
            ),
        )

        assert filters_builder.karaoke == KaraokeBuilder(
            level=1,
            mono_level=2.3,
            filter_band=4,
            filter_width=5.6,
        )

        filters_builder.set_karaoke(level=3845793)

        assert filters_builder.karaoke == KaraokeBuilder(
            level=3845793,
            mono_level=2.3,
            filter_band=4,
            filter_width=5.6,
        )

        filters_builder.set_karaoke(mono_level=4590)

        assert filters_builder.karaoke == KaraokeBuilder(
            level=3845793,
            mono_level=4590,
            filter_band=4,
            filter_width=5.6,
        )

        filters_builder.set_karaoke(filter_band=349058)

        assert filters_builder.karaoke == KaraokeBuilder(
            level=3845793,
            mono_level=4590,
            filter_band=349058,
            filter_width=5.6,
        )

        filters_builder.set_karaoke(filter_width=548)

        assert filters_builder.karaoke == KaraokeBuilder(
            level=3845793,
            mono_level=4590,
            filter_band=349058,
            filter_width=548,
        )

    def test_clear_karaoke(self):
        filters_builder = FiltersBuilder(
            karaoke=KaraokeBuilder(
                level=1,
                mono_level=2.3,
                filter_band=4,
                filter_width=5.6,
            ),
        )

        assert filters_builder.karaoke == KaraokeBuilder(
            level=1,
            mono_level=2.3,
            filter_band=4,
            filter_width=5.6,
        )

        filters_builder.clear_karaoke()

        assert filters_builder.karaoke is None

    def test_set_timescale(self):
        filters_builder = FiltersBuilder()

        assert filters_builder.timescale is None

        filters_builder.set_timescale(
            speed=1,
            pitch=2.3,
            rate=4,
        )

        assert filters_builder.timescale == TimescaleBuilder(
            speed=1,
            pitch=2.3,
            rate=4,
        )

    def test_set_timescale_with_existing(self):
        filters_builder = FiltersBuilder(
            timescale=TimescaleBuilder(speed=1, pitch=2.3, rate=4),
        )

        assert filters_builder.timescale == TimescaleBuilder(speed=1, pitch=2.3, rate=4)

        filters_builder.set_timescale(speed=345)

        assert filters_builder.timescale == TimescaleBuilder(
            speed=345,
            pitch=2.3,
            rate=4,
        )

        filters_builder.set_timescale(pitch=6598)

        assert filters_builder.timescale == TimescaleBuilder(
            speed=345,
            pitch=6598,
            rate=4,
        )

        filters_builder.set_timescale(rate=659848)

        assert filters_builder.timescale == TimescaleBuilder(
            speed=345,
            pitch=6598,
            rate=659848,
        )

    def test_clear_timescale(self):
        filters_builder = FiltersBuilder(
            timescale=TimescaleBuilder(speed=1, pitch=2.3, rate=4),
        )

        assert filters_builder.timescale == TimescaleBuilder(speed=1, pitch=2.3, rate=4)

        filters_builder.clear_timescale()

        assert filters_builder.timescale is None

    def test_set_tremolo(self):
        filters_builder = FiltersBuilder()

        assert filters_builder.tremolo is None

        filters_builder.set_tremolo(
            frequency=1,
            depth=2.3,
        )

        assert filters_builder.tremolo == TremoloBuilder(
            frequency=1,
            depth=2.3,
        )

    def test_set_tremolo_with_existing(self):
        filters_builder = FiltersBuilder(
            tremolo=TremoloBuilder(frequency=1, depth=2.3),
        )

        assert filters_builder.tremolo == TremoloBuilder(frequency=1, depth=2.3)

        filters_builder.set_tremolo(frequency=34958)

        assert filters_builder.tremolo == TremoloBuilder(frequency=34958, depth=2.3)

        filters_builder.set_tremolo(depth=34958)

        assert filters_builder.tremolo == TremoloBuilder(frequency=34958, depth=34958)

    def test_clear_tremolo(self):
        filters_builder = FiltersBuilder(
            tremolo=TremoloBuilder(frequency=1, depth=2.3),
        )

        assert filters_builder.tremolo == TremoloBuilder(frequency=1, depth=2.3)

        filters_builder.clear_tremolo()

        assert filters_builder.tremolo is None

    def test_set_vibrato(self):
        filters_builder = FiltersBuilder()

        assert filters_builder.vibrato is None

        filters_builder.set_vibrato(
            frequency=1,
            depth=2.3,
        )

        assert filters_builder.vibrato == VibratoBuilder(
            frequency=1,
            depth=2.3,
        )

    def test_set_vibrato_with_existing(self):
        filters_builder = FiltersBuilder(
            vibrato=VibratoBuilder(frequency=1, depth=2.3),
        )

        assert filters_builder.vibrato == VibratoBuilder(frequency=1, depth=2.3)

        filters_builder.set_vibrato(frequency=23423)

        assert filters_builder.vibrato == VibratoBuilder(frequency=23423, depth=2.3)

        filters_builder.set_vibrato(depth=656)

        assert filters_builder.vibrato == VibratoBuilder(frequency=23423, depth=656)

    def test_clear_vibrato(self):
        filters_builder = FiltersBuilder(
            vibrato=VibratoBuilder(frequency=1, depth=2.3),
        )

        assert filters_builder.vibrato == VibratoBuilder(frequency=1, depth=2.3)

        filters_builder.clear_vibrato()

        assert filters_builder.vibrato is None

    def test_set_rotation(self):
        filters_builder = FiltersBuilder()

        assert filters_builder.rotation is None

        filters_builder.set_rotation(
            rotation_hz=1,
        )

        assert filters_builder.rotation == RotationBuilder(
            rotation_hz=1,
        )

    def test_set_rotation_with_existing(self):
        filters_builder = FiltersBuilder(
            rotation=RotationBuilder(rotation_hz=1),
        )

        assert filters_builder.rotation == RotationBuilder(rotation_hz=1)

        filters_builder.set_rotation(
            rotation_hz=239478,
        )

        assert filters_builder.rotation == RotationBuilder(
            rotation_hz=239478,
        )

    def test_clear_rotation(self):
        filters_builder = FiltersBuilder(
            rotation=RotationBuilder(rotation_hz=1),
        )

        assert filters_builder.rotation == RotationBuilder(rotation_hz=1)

        filters_builder.clear_rotation()

        assert filters_builder.rotation is None

    def test_set_distortion(self):
        filters_builder = FiltersBuilder()

        assert filters_builder.distortion is None

        filters_builder.set_distortion(
            sin_offset=1,
            sin_scale=2.3,
            cos_offset=4,
            cos_scale=5.6,
            tan_offset=7,
            tan_scale=8.9,
            offset=10,
            scale=11.12,
        )

        assert filters_builder.distortion == DistortionBuilder(
            sin_offset=1,
            sin_scale=2.3,
            cos_offset=4,
            cos_scale=5.6,
            tan_offset=7,
            tan_scale=8.9,
            offset=10,
            scale=11.12,
        )

    def test_set_distortion_with_existing(self):
        filters_builder = FiltersBuilder(
            distortion=DistortionBuilder(
                sin_offset=1,
                sin_scale=2.3,
                cos_offset=4,
                cos_scale=5.6,
                tan_offset=7,
                tan_scale=8.9,
                offset=10,
                scale=11.12,
            ),
        )

        assert filters_builder.distortion == DistortionBuilder(
            sin_offset=1,
            sin_scale=2.3,
            cos_offset=4,
            cos_scale=5.6,
            tan_offset=7,
            tan_scale=8.9,
            offset=10,
            scale=11.12,
        )

        filters_builder.set_distortion(
            sin_offset=34598,
        )

        assert filters_builder.distortion == DistortionBuilder(
            sin_offset=34598,
            sin_scale=2.3,
            cos_offset=4,
            cos_scale=5.6,
            tan_offset=7,
            tan_scale=8.9,
            offset=10,
            scale=11.12,
        )

        filters_builder.set_distortion(
            sin_scale=876,
        )

        assert filters_builder.distortion == DistortionBuilder(
            sin_offset=34598,
            sin_scale=876,
            cos_offset=4,
            cos_scale=5.6,
            tan_offset=7,
            tan_scale=8.9,
            offset=10,
            scale=11.12,
        )

        filters_builder.set_distortion(
            cos_offset=4983,
        )

        assert filters_builder.distortion == DistortionBuilder(
            sin_offset=34598,
            sin_scale=876,
            cos_offset=4983,
            cos_scale=5.6,
            tan_offset=7,
            tan_scale=8.9,
            offset=10,
            scale=11.12,
        )

        filters_builder.set_distortion(
            cos_scale=345367,
        )

        assert filters_builder.distortion == DistortionBuilder(
            sin_offset=34598,
            sin_scale=876,
            cos_offset=4983,
            cos_scale=345367,
            tan_offset=7,
            tan_scale=8.9,
            offset=10,
            scale=11.12,
        )

        filters_builder.set_distortion(
            tan_offset=57543,
        )

        assert filters_builder.distortion == DistortionBuilder(
            sin_offset=34598,
            sin_scale=876,
            cos_offset=4983,
            cos_scale=345367,
            tan_offset=57543,
            tan_scale=8.9,
            offset=10,
            scale=11.12,
        )

        filters_builder.set_distortion(
            tan_scale=2347,
        )

        assert filters_builder.distortion == DistortionBuilder(
            sin_offset=34598,
            sin_scale=876,
            cos_offset=4983,
            cos_scale=345367,
            tan_offset=57543,
            tan_scale=2347,
            offset=10,
            scale=11.12,
        )

        filters_builder.set_distortion(
            offset=12982,
        )

        assert filters_builder.distortion == DistortionBuilder(
            sin_offset=34598,
            sin_scale=876,
            cos_offset=4983,
            cos_scale=345367,
            tan_offset=57543,
            tan_scale=2347,
            offset=12982,
            scale=11.12,
        )

        filters_builder.set_distortion(
            scale=698,
        )

        assert filters_builder.distortion == DistortionBuilder(
            sin_offset=34598,
            sin_scale=876,
            cos_offset=4983,
            cos_scale=345367,
            tan_offset=57543,
            tan_scale=2347,
            offset=12982,
            scale=698,
        )

    def test_clear_distortion(self):
        filters_builder = FiltersBuilder(
            distortion=DistortionBuilder(
                sin_offset=1,
                sin_scale=2.3,
                cos_offset=4,
                cos_scale=5.6,
                tan_offset=7,
                tan_scale=8.9,
                offset=10,
                scale=11.12,
            ),
        )

        assert filters_builder.distortion == DistortionBuilder(
            sin_offset=1,
            sin_scale=2.3,
            cos_offset=4,
            cos_scale=5.6,
            tan_offset=7,
            tan_scale=8.9,
            offset=10,
            scale=11.12,
        )

        filters_builder.clear_distortion()

        assert filters_builder.distortion is None

    def test_set_channel_mix(self):
        filters_builder = FiltersBuilder()

        assert filters_builder.channel_mix is None

        filters_builder.set_channel_mix(
            left_to_left=1,
            left_to_right=2.3,
            right_to_left=4,
            right_to_right=5.6,
        )

        assert filters_builder.channel_mix == ChannelMixBuilder(
            left_to_left=1,
            left_to_right=2.3,
            right_to_left=4,
            right_to_right=5.6,
        )

    def test_set_channel_mix_with_existing(self):
        filters_builder = FiltersBuilder(
            channel_mix=ChannelMixBuilder(
                left_to_left=1,
                left_to_right=2.3,
                right_to_left=4,
                right_to_right=5.6,
            ),
        )

        assert filters_builder.channel_mix == ChannelMixBuilder(
            left_to_left=1,
            left_to_right=2.3,
            right_to_left=4,
            right_to_right=5.6,
        )

        filters_builder.set_channel_mix(left_to_left=38745)

        assert filters_builder.channel_mix == ChannelMixBuilder(
            left_to_left=38745,
            left_to_right=2.3,
            right_to_left=4,
            right_to_right=5.6,
        )

        filters_builder.set_channel_mix(left_to_right=2938)

        assert filters_builder.channel_mix == ChannelMixBuilder(
            left_to_left=38745,
            left_to_right=2938,
            right_to_left=4,
            right_to_right=5.6,
        )

        filters_builder.set_channel_mix(right_to_left=495876)

        assert filters_builder.channel_mix == ChannelMixBuilder(
            left_to_left=38745,
            left_to_right=2938,
            right_to_left=495876,
            right_to_right=5.6,
        )

        filters_builder.set_channel_mix(right_to_right=6989)

        assert filters_builder.channel_mix == ChannelMixBuilder(
            left_to_left=38745,
            left_to_right=2938,
            right_to_left=495876,
            right_to_right=6989,
        )

    def test_clear_channel_mix(self):
        filters_builder = FiltersBuilder(
            channel_mix=ChannelMixBuilder(
                left_to_left=1,
                left_to_right=2.3,
                right_to_left=4,
                right_to_right=5.6,
            ),
        )

        assert filters_builder.channel_mix == ChannelMixBuilder(
            left_to_left=1,
            left_to_right=2.3,
            right_to_left=4,
            right_to_right=5.6,
        )

        filters_builder.clear_channel_mix()

        assert filters_builder.channel_mix is None

    def test_set_low_pass(self):
        filters_builder = FiltersBuilder()

        assert filters_builder.low_pass is None

        filters_builder.set_low_pass(smoothing=1)

        assert filters_builder.low_pass == LowPassBuilder(smoothing=1)

    def test_set_low_pass_with_existing(self):
        filters_builder = FiltersBuilder(
            low_pass=LowPassBuilder(smoothing=1),
        )

        assert filters_builder.low_pass == LowPassBuilder(smoothing=1)

        filters_builder.set_low_pass(smoothing=348758)

        assert filters_builder.low_pass == LowPassBuilder(smoothing=348758)

    def test_clear_low_pass(self):
        filters_builder = FiltersBuilder(
            low_pass=LowPassBuilder(smoothing=1),
        )

        assert filters_builder.low_pass == LowPassBuilder(smoothing=1)

        filters_builder.clear_low_pass()

        assert filters_builder.low_pass is None

    def test_set_plugin_filters(self):
        filters_builder = FiltersBuilder()

        assert filters_builder.plugin_filters == {}

        filters_builder.set_plugin_filters({"plugin": "filters"})

        assert filters_builder.plugin_filters == {"plugin": "filters"}

    def test_build(self):
        mock_equalizer_1 = mock.Mock()
        mock_karaoke = mock.Mock()
        mock_timescale = mock.Mock()
        mock_tremolo = mock.Mock()
        mock_vibrato = mock.Mock()
        mock_rotation = mock.Mock()
        mock_distortion = mock.Mock()
        mock_channel_mix = mock.Mock()
        mock_low_pass = mock.Mock()

        filters_builder = FiltersBuilder(
            volume=1.5,
            equalizer=[mock_equalizer_1],
            karaoke=mock_karaoke,
            timescale=mock_timescale,
            tremolo=mock_tremolo,
            vibrato=mock_vibrato,
            rotation=mock_rotation,
            distortion=mock_distortion,
            channel_mix=mock_channel_mix,
            low_pass=mock_low_pass,
            plugin_filters={"plugin": "filters"},
        )

        assert filters_builder.build() == {
            "volume": 1.5,
            "equalizer": [
                mock_equalizer_1.build.return_value,
            ],
            "karaoke": mock_karaoke.build.return_value,
            "timescale": mock_timescale.build.return_value,
            "tremolo": mock_tremolo.build.return_value,
            "vibrato": mock_vibrato.build.return_value,
            "rotation": mock_rotation.build.return_value,
            "distortion": mock_distortion.build.return_value,
            "channelMix": mock_channel_mix.build.return_value,
            "lowPass": mock_low_pass.build.return_value,
            "pluginFilters": {"plugin": "filters"},
        }


class TestEqualizerBuilder:
    def test_properties(self):
        equalizer = EqualizerBuilder(band=filters.BandType.HZ100, gain=1)

        assert equalizer.band == filters.BandType.HZ100
        assert equalizer.gain == 1

    def test_build(self):
        equalizer = EqualizerBuilder(band=filters.BandType.HZ100, gain=1)

        assert equalizer.build() == {
            "band": filters.BandType.HZ100,
            "gain": 1,
        }


class TestKaraokeBuilder:
    def test_properties(self):
        karaoke = KaraokeBuilder(
            level=1,
            mono_level=2.3,
            filter_band=4,
            filter_width=5.6,
        )

        assert karaoke.level == 1
        assert karaoke.mono_level == 2.3
        assert karaoke.filter_band == 4
        assert karaoke.filter_width == 5.6

    def test_build(self):
        karaoke = KaraokeBuilder(
            level=1,
            mono_level=2.3,
            filter_band=4,
            filter_width=5.6,
        )

        assert karaoke.build() == {
            "level": 1,
            "monoLevel": 2.3,
            "filterBand": 4,
            "filterWidth": 5.6,
        }


class TestTimescaleBuilder:
    def test_properties(self):
        timescale = TimescaleBuilder(
            speed=1,
            pitch=2.3,
            rate=4,
        )

        assert timescale.speed == 1
        assert timescale.pitch == 2.3
        assert timescale.rate == 4

    def test_build(self):
        timescale = TimescaleBuilder(
            speed=1,
            pitch=2.3,
            rate=4,
        )

        assert timescale.build() == {
            "speed": 1,
            "pitch": 2.3,
            "rate": 4,
        }


class TestTremoloBuilder:
    def test_properties(self):
        tremolo = TremoloBuilder(
            frequency=1,
            depth=2.3,
        )

        assert tremolo.frequency == 1
        assert tremolo.depth == 2.3

    def test_build(self):
        tremolo = TremoloBuilder(
            frequency=1,
            depth=2.3,
        )

        assert tremolo.build() == {
            "frequency": 1,
            "depth": 2.3,
        }


class TestVibratoBuilder:
    def test_properties(self):
        vibrato = VibratoBuilder(
            frequency=1,
            depth=2.3,
        )

        assert vibrato.frequency == 1
        assert vibrato.depth == 2.3

    def test_build(self):
        vibrato = VibratoBuilder(
            frequency=1,
            depth=2.3,
        )

        assert vibrato.build() == {
            "frequency": 1,
            "depth": 2.3,
        }


class TestRotationBuilder:
    def test_properties(self):
        rotation = RotationBuilder(
            rotation_hz=1,
        )

        assert rotation.rotation_hz == 1

    def test_build(self):
        rotation = RotationBuilder(
            rotation_hz=1,
        )

        assert rotation.build() == {
            "rotationHz": 1,
        }


class TestDistortionBuilder:
    def test_properties(self):
        distortion = DistortionBuilder(
            sin_offset=1,
            sin_scale=2.3,
            cos_offset=4,
            cos_scale=5.6,
            tan_offset=7,
            tan_scale=8.9,
            offset=10,
            scale=11.12,
        )

        assert distortion.sin_offset == 1
        assert distortion.sin_scale == 2.3
        assert distortion.cos_offset == 4
        assert distortion.cos_scale == 5.6
        assert distortion.tan_offset == 7
        assert distortion.tan_scale == 8.9
        assert distortion.offset == 10
        assert distortion.scale == 11.12

    def test_build(self):
        distortion = DistortionBuilder(
            sin_offset=1,
            sin_scale=2.3,
            cos_offset=4,
            cos_scale=5.6,
            tan_offset=7,
            tan_scale=8.9,
            offset=10,
            scale=11.12,
        )

        assert distortion.build() == {
            "sinOffset": 1,
            "sinScale": 2.3,
            "cosOffset": 4,
            "cosScale": 5.6,
            "tanOffset": 7,
            "tanScale": 8.9,
            "offset": 10,
            "scale": 11.12,
        }


class TestChannelMixBuilder:
    def test_properties(self):
        channel_mix = ChannelMixBuilder(
            left_to_left=1,
            left_to_right=2.3,
            right_to_left=4,
            right_to_right=5.6,
        )

        assert channel_mix.left_to_left == 1
        assert channel_mix.left_to_right == 2.3
        assert channel_mix.right_to_left == 4
        assert channel_mix.right_to_right == 5.6

    def test_build(self):
        channel_mix = ChannelMixBuilder(
            left_to_left=1,
            left_to_right=2.3,
            right_to_left=4,
            right_to_right=5.6,
        )

        assert channel_mix.build() == {
            "leftToLeft": 1,
            "leftToRight": 2.3,
            "rightToLeft": 4,
            "rightToRight": 5.6,
        }


class TestLowPassBuilder:
    def test_properties(self):
        low_pass = LowPassBuilder(smoothing=1)

        assert low_pass.smoothing == 1

    def test_build(self):
        low_pass = LowPassBuilder(smoothing=1)

        assert low_pass.build() == {
            "smoothing": 1,
        }
