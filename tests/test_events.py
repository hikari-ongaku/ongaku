from __future__ import annotations

from unittest import mock

import aiohttp
import hikari

from ongaku import track as track_
from ongaku.events import PayloadEvent
from ongaku.events import PlayerUpdateEvent
from ongaku.events import QueueEmptyEvent
from ongaku.events import QueueNextEvent
from ongaku.events import ReadyEvent
from ongaku.events import SessionConnectedEvent
from ongaku.events import SessionDisconnectedEvent
from ongaku.events import SessionErrorEvent
from ongaku.events import StatisticsEvent
from ongaku.events import TrackEndEvent
from ongaku.events import TrackExceptionEvent
from ongaku.events import TrackStartEvent
from ongaku.events import TrackStuckEvent
from ongaku.events import WebsocketClosedEvent


class TestPayloadEvent:
    def test_properties(self):
        mock_app = mock.Mock()
        mock_client = mock.Mock()
        mock_session = mock.Mock()

        event = PayloadEvent(
            mock_app,
            mock_client,
            mock_session,
            payload="payload",
        )

        assert event.app == mock_app
        assert event.client == mock_client
        assert event.session == mock_session
        assert event.payload == "payload"

    def test_from_session(self):
        mock_session = mock.Mock()

        event = PayloadEvent.from_session(
            mock_session,
            payload="payload",
        )

        assert event.app == mock_session.app
        assert event.client == mock_session.client
        assert event.session == mock_session
        assert event.payload == "payload"


class TestReadyEvent:
    def test_properties(self):
        mock_app = mock.Mock()
        mock_client = mock.Mock()
        mock_session = mock.Mock()

        event = ReadyEvent(
            mock_app,
            mock_client,
            mock_session,
            resumed=False,
            session_id="session_id",
        )

        assert event.app == mock_app
        assert event.client == mock_client
        assert event.session == mock_session
        assert event.resumed is False
        assert event.session_id == "session_id"

    def test_from_session(self):
        mock_session = mock.Mock()

        event = ReadyEvent.from_session(
            mock_session,
            resumed=False,
            session_id="session_id",
        )

        assert event.app == mock_session.app
        assert event.client == mock_session.client
        assert event.session == mock_session
        assert event.resumed is False
        assert event.session_id == "session_id"


class TestPlayerUpdateEvent:
    def test_properties(self):
        mock_app = mock.Mock()
        mock_client = mock.Mock()
        mock_session = mock.Mock()
        mock_state = mock.Mock()

        event = PlayerUpdateEvent(
            mock_app,
            mock_client,
            mock_session,
            guild_id=hikari.Snowflake(123),
            state=mock_state,
        )

        assert event.app == mock_app
        assert event.client == mock_client
        assert event.session == mock_session
        assert event.guild_id == hikari.Snowflake(123)
        assert event.state == mock_state

    def test_from_session(self):
        mock_session = mock.Mock()
        mock_state = mock.Mock()

        event = PlayerUpdateEvent.from_session(
            mock_session,
            guild_id=hikari.Snowflake(123),
            state=mock_state,
        )

        assert event.app == mock_session.app
        assert event.client == mock_session.client
        assert event.session == mock_session
        assert event.guild_id == hikari.Snowflake(123)
        assert event.state == mock_state


class TestStatisticsEvent:
    def test_properties(self):
        mock_app = mock.Mock()
        mock_client = mock.Mock()
        mock_session = mock.Mock()
        mock_memory = mock.Mock()
        mock_cpu = mock.Mock()
        mock_frame_statistics = mock.Mock()

        event = StatisticsEvent(
            mock_app,
            mock_client,
            mock_session,
            players=1,
            playing_players=2,
            uptime=3,
            memory=mock_memory,
            cpu=mock_cpu,
            frame_statistics=mock_frame_statistics,
        )

        assert event.app == mock_app
        assert event.client == mock_client
        assert event.session == mock_session
        assert event.players == 1
        assert event.playing_players == 2
        assert event.uptime == 3
        assert event.memory == mock_memory
        assert event.cpu == mock_cpu
        assert event.frame_statistics == mock_frame_statistics

    def test_from_session(self):
        mock_session = mock.Mock()
        mock_memory = mock.Mock()
        mock_cpu = mock.Mock()
        mock_frame_statistics = mock.Mock()

        event = StatisticsEvent.from_session(
            mock_session,
            players=1,
            playing_players=2,
            uptime=3,
            memory=mock_memory,
            cpu=mock_cpu,
            frame_statistics=mock_frame_statistics,
        )

        assert event.app == mock_session.app
        assert event.client == mock_session.client
        assert event.session == mock_session
        assert event.players == 1
        assert event.playing_players == 2
        assert event.uptime == 3
        assert event.memory == mock_memory
        assert event.cpu == mock_cpu
        assert event.frame_statistics == mock_frame_statistics


class TestWebsocketClosedEvent:
    def test_properties(self):
        mock_app = mock.Mock()
        mock_client = mock.Mock()
        mock_session = mock.Mock()

        event = WebsocketClosedEvent(
            mock_app,
            mock_client,
            mock_session,
            guild_id=hikari.Snowflake(123),
            code=1,
            reason="reason",
            by_remote=True,
        )

        assert event.app == mock_app
        assert event.client == mock_client
        assert event.session == mock_session
        assert event.guild_id == hikari.Snowflake(123)
        assert event.code == 1
        assert event.reason == "reason"
        assert event.by_remote is True

    def test_from_session(self):
        mock_session = mock.Mock()

        event = WebsocketClosedEvent.from_session(
            mock_session,
            guild_id=hikari.Snowflake(123),
            code=1,
            reason="reason",
            by_remote=True,
        )

        assert event.app == mock_session.app
        assert event.client == mock_session.client
        assert event.session == mock_session
        assert event.guild_id == hikari.Snowflake(123)
        assert event.code == 1
        assert event.reason == "reason"
        assert event.by_remote is True


class TestSessionConnectedEvent:
    def test_properties(self):
        mock_app = mock.Mock()
        mock_client = mock.Mock()
        mock_session = mock.Mock()

        event = SessionConnectedEvent(
            mock_app,
            mock_client,
            mock_session,
        )

        assert event.app == mock_app
        assert event.client == mock_client
        assert event.session == mock_session

    def test_from_session(self):
        mock_session = mock.Mock()

        event = SessionConnectedEvent.from_session(mock_session)

        assert event.app == mock_session.app
        assert event.client == mock_session.client
        assert event.session == mock_session


class TestSessionDisconnectedEvent:
    def test_properties(self):
        mock_app = mock.Mock()
        mock_client = mock.Mock()
        mock_session = mock.Mock()

        event = SessionDisconnectedEvent(
            mock_app,
            mock_client,
            mock_session,
            code=aiohttp.WSCloseCode.GOING_AWAY,
            reason="reason",
        )

        assert event.app == mock_app
        assert event.client == mock_client
        assert event.session == mock_session
        assert event.code == aiohttp.WSCloseCode.GOING_AWAY
        assert event.reason == "reason"

    def test_from_session(self):
        mock_session = mock.Mock()

        event = SessionDisconnectedEvent.from_session(
            mock_session,
            code=aiohttp.WSCloseCode.GOING_AWAY,
            reason="reason",
        )

        assert event.app == mock_session.app
        assert event.client == mock_session.client
        assert event.session == mock_session
        assert event.code == aiohttp.WSCloseCode.GOING_AWAY
        assert event.reason == "reason"


class TestSessionErrorEvent:
    def test_properties(self):
        mock_app = mock.Mock()
        mock_client = mock.Mock()
        mock_session = mock.Mock()

        event = SessionErrorEvent(
            mock_app,
            mock_client,
            mock_session,
        )

        assert event.app == mock_app
        assert event.client == mock_client
        assert event.session == mock_session

    def test_from_session(self):
        mock_session = mock.Mock()

        event = SessionErrorEvent.from_session(mock_session)

        assert event.app == mock_session.app
        assert event.client == mock_session.client
        assert event.session == mock_session


class TestTrackStartEvent:
    def test_properties(self):
        mock_app = mock.Mock()
        mock_client = mock.Mock()
        mock_session = mock.Mock()
        mock_track = mock.Mock()

        event = TrackStartEvent(
            mock_app,
            mock_client,
            mock_session,
            guild_id=hikari.Snowflake(123),
            track=mock_track,
        )

        assert event.app == mock_app
        assert event.client == mock_client
        assert event.session == mock_session
        assert event.guild_id == hikari.Snowflake(123)
        assert event.track == mock_track

    def test_from_session(self):
        mock_session = mock.Mock()
        mock_track = mock.Mock()

        event = TrackStartEvent.from_session(
            mock_session,
            guild_id=hikari.Snowflake(123),
            track=mock_track,
        )

        assert event.app == mock_session.app
        assert event.client == mock_session.client
        assert event.session == mock_session
        assert event.guild_id == hikari.Snowflake(123)
        assert event.track == mock_track


class TestTrackEndEvent:
    def test_properties(self):
        mock_app = mock.Mock()
        mock_client = mock.Mock()
        mock_session = mock.Mock()
        mock_track = mock.Mock()

        event = TrackEndEvent(
            mock_app,
            mock_client,
            mock_session,
            guild_id=hikari.Snowflake(123),
            track=mock_track,
            reason=track_.TrackEndReasonType.FINISHED,
        )

        assert event.app == mock_app
        assert event.client == mock_client
        assert event.session == mock_session
        assert event.guild_id == hikari.Snowflake(123)
        assert event.track == mock_track
        assert event.reason == track_.TrackEndReasonType.FINISHED

    def test_from_session(self):
        mock_session = mock.Mock()
        mock_track = mock.Mock()

        event = TrackEndEvent.from_session(
            mock_session,
            guild_id=hikari.Snowflake(123),
            track=mock_track,
            reason=track_.TrackEndReasonType.FINISHED,
        )

        assert event.app == mock_session.app
        assert event.client == mock_session.client
        assert event.session == mock_session
        assert event.guild_id == hikari.Snowflake(123)
        assert event.track == mock_track
        assert event.reason == track_.TrackEndReasonType.FINISHED


class TestTrackExceptionEvent:
    def test_properties(self):
        mock_app = mock.Mock()
        mock_client = mock.Mock()
        mock_session = mock.Mock()
        mock_track = mock.Mock()
        mock_exception = mock.Mock()

        event = TrackExceptionEvent(
            mock_app,
            mock_client,
            mock_session,
            guild_id=hikari.Snowflake(123),
            track=mock_track,
            exception=mock_exception,
        )

        assert event.app == mock_app
        assert event.client == mock_client
        assert event.session == mock_session
        assert event.guild_id == hikari.Snowflake(123)
        assert event.track == mock_track
        assert event.exception == mock_exception

    def test_from_session(self):
        mock_session = mock.Mock()
        mock_track = mock.Mock()
        mock_exception = mock.Mock()

        event = TrackExceptionEvent.from_session(
            mock_session,
            guild_id=hikari.Snowflake(123),
            track=mock_track,
            exception=mock_exception,
        )

        assert event.app == mock_session.app
        assert event.client == mock_session.client
        assert event.session == mock_session
        assert event.guild_id == hikari.Snowflake(123)
        assert event.track == mock_track
        assert event.exception == mock_exception


class TestTrackStuckEvent:
    def test_properties(self):
        mock_app = mock.Mock()
        mock_client = mock.Mock()
        mock_session = mock.Mock()
        mock_track = mock.Mock()

        event = TrackStuckEvent(
            mock_app,
            mock_client,
            mock_session,
            guild_id=hikari.Snowflake(123),
            track=mock_track,
            threshold_ms=1,
        )

        assert event.app == mock_app
        assert event.client == mock_client
        assert event.session == mock_session
        assert event.guild_id == hikari.Snowflake(123)
        assert event.track == mock_track
        assert event.threshold_ms == 1

    def test_from_session(self):
        mock_session = mock.Mock()
        mock_track = mock.Mock()

        event = TrackStuckEvent.from_session(
            mock_session,
            guild_id=hikari.Snowflake(123),
            track=mock_track,
            threshold_ms=1,
        )

        assert event.app == mock_session.app
        assert event.client == mock_session.client
        assert event.session == mock_session
        assert event.guild_id == hikari.Snowflake(123)
        assert event.track == mock_track
        assert event.threshold_ms == 1


class TestQueueEmptyEvent:
    def test_properties(self):
        mock_app = mock.Mock()
        mock_client = mock.Mock()
        mock_session = mock.Mock()
        mock_old_track = mock.Mock()

        event = QueueEmptyEvent(
            mock_app,
            mock_client,
            mock_session,
            guild_id=hikari.Snowflake(123),
            old_track=mock_old_track,
        )

        assert event.app == mock_app
        assert event.client == mock_client
        assert event.session == mock_session
        assert event.guild_id == hikari.Snowflake(123)
        assert event.old_track == mock_old_track

    def test_from_session(self):
        mock_session = mock.Mock()
        mock_old_track = mock.Mock()

        event = QueueEmptyEvent.from_session(
            mock_session,
            guild_id=hikari.Snowflake(123),
            old_track=mock_old_track,
        )

        assert event.app == mock_session.app
        assert event.client == mock_session.client
        assert event.session == mock_session
        assert event.guild_id == hikari.Snowflake(123)
        assert event.old_track == mock_old_track


class TestQueueNextEvent:
    def test_properties(self):
        mock_app = mock.Mock()
        mock_client = mock.Mock()
        mock_session = mock.Mock()
        mock_track = mock.Mock()
        mock_old_track = mock.Mock()

        event = QueueNextEvent(
            mock_app,
            mock_client,
            mock_session,
            guild_id=hikari.Snowflake(123),
            track=mock_track,
            old_track=mock_old_track,
        )

        assert event.app == mock_app
        assert event.client == mock_client
        assert event.session == mock_session
        assert event.guild_id == hikari.Snowflake(123)
        assert event.track == mock_track
        assert event.old_track == mock_old_track

    def test_from_session(self):
        mock_session = mock.Mock()
        mock_track = mock.Mock()
        mock_old_track = mock.Mock()

        event = QueueNextEvent.from_session(
            mock_session,
            guild_id=hikari.Snowflake(123),
            track=mock_track,
            old_track=mock_old_track,
        )

        assert event.app == mock_session.app
        assert event.client == mock_session.client
        assert event.session == mock_session
        assert event.guild_id == hikari.Snowflake(123)
        assert event.track == mock_track
        assert event.old_track == mock_old_track
