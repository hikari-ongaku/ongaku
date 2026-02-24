from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import hikari

from ongaku import events
from ongaku.abc.errors import SeverityType
from ongaku.abc.events import TrackEndReasonType
from ongaku.impl import player

if TYPE_CHECKING:
    from hikari.impl import gateway_bot as gateway_bot_

    from ongaku.client import Client
    from ongaku.impl.track import Track
    from ongaku.session import Session


class TestPayloadEvent:
    def test_event(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        event = events.PayloadEvent(
            gateway_bot,
            ongaku_client,
            ongaku_session,
            "payload",
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.payload == "payload"

    def test_from_session(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        event = events.PayloadEvent.from_session(ongaku_session, "payload")

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.payload == "payload"


class TestReadyEvent:
    def test_event(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        event = events.ReadyEvent(
            gateway_bot,
            ongaku_client,
            ongaku_session,
            False,
            "session_id",
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.resumed is False
        assert event.session_id == "session_id"

    def test_from_session(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        event = events.ReadyEvent.from_session(ongaku_session, False, "session_id")

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.resumed is False
        assert event.session_id == "session_id"


class TestPlayerUpdateEvent:
    def test_event(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        state = player.State(datetime.datetime.now(), 2, False, 3)
        event = events.PlayerUpdateEvent(
            gateway_bot,
            ongaku_client,
            ongaku_session,
            hikari.Snowflake(1234567890),
            state,
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.guild_id == hikari.Snowflake(1234567890)
        assert event.state == state

    def test_from_session(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        state = player.State(datetime.datetime.now(), 2, False, 3)
        event = events.PlayerUpdateEvent.from_session(
            ongaku_session,
            hikari.Snowflake(1234567890),
            state,
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.guild_id == hikari.Snowflake(1234567890)
        assert event.state == state


class TestWebsocketClosedEvent:
    def test_event(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        event = events.WebsocketClosedEvent(
            gateway_bot,
            ongaku_client,
            ongaku_session,
            hikari.Snowflake(1234567890),
            1,
            "reason",
            False,
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.guild_id == hikari.Snowflake(1234567890)
        assert event.code == 1
        assert event.reason == "reason"
        assert event.by_remote is False

    def test_from_session(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        event = events.WebsocketClosedEvent.from_session(
            ongaku_session,
            hikari.Snowflake(1234567890),
            1,
            "reason",
            False,
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.guild_id == hikari.Snowflake(1234567890)
        assert event.code == 1
        assert event.reason == "reason"
        assert event.by_remote is False


class TestTrackStartEvent:
    def test_event(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        event = events.TrackStartEvent(
            gateway_bot,
            ongaku_client,
            ongaku_session,
            hikari.Snowflake(1234567890),
            ongaku_track,
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.guild_id == hikari.Snowflake(1234567890)
        assert event.track == ongaku_track

    def test_from_session(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        event = events.TrackStartEvent.from_session(
            ongaku_session,
            hikari.Snowflake(1234567890),
            ongaku_track,
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.guild_id == hikari.Snowflake(1234567890)
        assert event.track == ongaku_track


class TestTrackEndEvent:
    def test_event(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        event = events.TrackEndEvent(
            gateway_bot,
            ongaku_client,
            ongaku_session,
            hikari.Snowflake(1234567890),
            ongaku_track,
            TrackEndReasonType.FINISHED,
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.guild_id == hikari.Snowflake(1234567890)
        assert event.track == ongaku_track
        assert event.reason == TrackEndReasonType.FINISHED

    def test_from_session(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        event = events.TrackEndEvent.from_session(
            ongaku_session,
            hikari.Snowflake(1234567890),
            ongaku_track,
            TrackEndReasonType.FINISHED,
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.guild_id == hikari.Snowflake(1234567890)
        assert event.track == ongaku_track
        assert event.reason == TrackEndReasonType.FINISHED


class TestTrackException:
    def test_event(self):
        exception = events.TrackException("message", SeverityType.COMMON, "cause")

        assert exception.message == "message"
        assert exception.severity == SeverityType.COMMON
        assert exception.cause == "cause"


class TestTrackExceptionEvent:
    def test_event(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        exception = events.TrackException("message", SeverityType.COMMON, "cause")
        event = events.TrackExceptionEvent(
            gateway_bot,
            ongaku_client,
            ongaku_session,
            hikari.Snowflake(1234567890),
            ongaku_track,
            exception,
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.guild_id == hikari.Snowflake(1234567890)
        assert event.track == ongaku_track
        assert event.exception == exception

    def test_from_session(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        exception = events.TrackException("message", SeverityType.COMMON, "cause")
        event = events.TrackExceptionEvent.from_session(
            ongaku_session,
            hikari.Snowflake(1234567890),
            ongaku_track,
            exception,
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.guild_id == hikari.Snowflake(1234567890)
        assert event.track == ongaku_track
        assert event.exception == exception


class TestTrackStuckEvent:
    def test_event(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        event = events.TrackStuckEvent(
            gateway_bot,
            ongaku_client,
            ongaku_session,
            hikari.Snowflake(1234567890),
            ongaku_track,
            1,
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.guild_id == hikari.Snowflake(1234567890)
        assert event.track == ongaku_track
        assert event.threshold_ms == 1

    def test_from_session(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        event = events.TrackStuckEvent.from_session(
            ongaku_session,
            hikari.Snowflake(1234567890),
            ongaku_track,
            1,
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.guild_id == hikari.Snowflake(1234567890)
        assert event.track == ongaku_track
        assert event.threshold_ms == 1


class TestQueueEmptyEvent:
    def test_event(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        event = events.QueueEmptyEvent(
            gateway_bot,
            ongaku_client,
            ongaku_session,
            hikari.Snowflake(1234567890),
            ongaku_track,
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.guild_id == hikari.Snowflake(1234567890)
        assert event.old_track == ongaku_track

    def test_from_session(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        event = events.QueueEmptyEvent.from_session(
            ongaku_session,
            hikari.Snowflake(1234567890),
            ongaku_track,
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.guild_id == hikari.Snowflake(1234567890)
        assert event.old_track == ongaku_track


class TestQueueNextEvent:
    def test_event(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        event = events.QueueNextEvent(
            gateway_bot,
            ongaku_client,
            ongaku_session,
            hikari.Snowflake(1234567890),
            ongaku_track,
            ongaku_track,
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.guild_id == hikari.Snowflake(1234567890)
        assert event.old_track == ongaku_track
        assert event.track == ongaku_track

    def test_from_session(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_client: Client,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        event = events.QueueNextEvent.from_session(
            ongaku_session,
            hikari.Snowflake(1234567890),
            ongaku_track,
            ongaku_track,
        )

        assert event.app == gateway_bot
        assert event.client == ongaku_client
        assert event.session == ongaku_session
        assert event.guild_id == hikari.Snowflake(1234567890)
        assert event.old_track == ongaku_track
        assert event.track == ongaku_track
