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
"""Events and entities related to Lavalink event objects."""

from __future__ import annotations

import typing

from ongaku.abc import events

if typing.TYPE_CHECKING:
    import aiohttp
    import hikari

    from ongaku import errors
    from ongaku import player
    from ongaku import session
    from ongaku import statistics
    from ongaku import track
    from ongaku.client import Client

__all__ = (
    "PayloadEvent",
    "PlayerUpdateEvent",
    "QueueEmptyEvent",
    "QueueNextEvent",
    "ReadyEvent",
    "SessionConnectedEvent",
    "SessionDisconnectedEvent",
    "StatisticsEvent",
    "TrackEndEvent",
    "TrackExceptionEvent",
    "TrackStartEvent",
    "TrackStuckEvent",
    "WebsocketClosedEvent",
)


class PayloadEvent(events.OngakuEvent):
    """Payload Event.

    The event that is dispatched each time a message is received from the websocket.
    """

    __slots__: typing.Sequence[str] = ("_app", "_client", "_payload", "_session")

    def __init__(
        self,
        app: hikari.RESTAware,
        client: Client,
        session: session.Session,
        *,
        payload: str,
    ) -> None:
        self._app = app
        self._client = client
        self._session = session
        self._payload = payload

    @classmethod
    def from_session(
        cls,
        session: session.Session,
        *,
        payload: str,
    ) -> PayloadEvent:
        """Build the [PayloadEvent][ongaku.events.PayloadEvent] with just a session."""
        return cls(session.app, session.client, session, payload=payload)

    @property
    def app(self) -> hikari.RESTAware:  # noqa: D102 This has an inherited documentation string.
        return self._app

    @property
    def client(self) -> Client:  # noqa: D102 This has an inherited documentation string.
        return self._client

    @property
    def session(self) -> session.Session:  # noqa: D102 This has an inherited documentation string.
        return self._session

    @property
    def payload(self) -> str:
        """The payload received."""
        return self._payload

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PayloadEvent):
            return False

        return self.payload == other.payload

    def __hash__(self) -> int:
        return hash(self.payload)


class ReadyEvent(events.OngakuEvent):
    """Ready Event.

    Dispatched by Lavalink upon successful connection and authorization.
    Contains fields determining if resuming was successful, as well as the session id.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/websocket.html#ready-op)
    """

    __slots__: typing.Sequence[str] = (
        "_app",
        "_client",
        "_resumed",
        "_session",
        "_session_id",
    )

    def __init__(
        self,
        app: hikari.RESTAware,
        client: Client,
        session: session.Session,
        *,
        resumed: bool,
        session_id: str,
    ) -> None:
        self._app = app
        self._client = client
        self._session = session
        self._resumed = resumed
        self._session_id = session_id

    @classmethod
    def from_session(
        cls,
        session: session.Session,
        *,
        resumed: bool,
        session_id: str,
    ) -> ReadyEvent:
        """Build the ready event with just a session."""
        return cls(
            session.app,
            session.client,
            session,
            resumed=resumed,
            session_id=session_id,
        )

    @property
    def app(self) -> hikari.RESTAware:  # noqa: D102 This has an inherited documentation string.
        return self._app

    @property
    def client(self) -> Client:  # noqa: D102 This has an inherited documentation string.
        return self._client

    @property
    def session(self) -> session.Session:  # noqa: D102 This has an inherited documentation string.
        return self._session

    @property
    def resumed(self) -> bool:
        """Whether the session has been resumed, or is a new session."""
        return self._resumed

    @property
    def session_id(self) -> str:
        """The lavalink session id, for the current session."""
        return self._session_id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ReadyEvent):
            return False

        return self.resumed == other.resumed and self.session_id == other.session_id

    def __hash__(self) -> int:
        return hash((self.resumed, self.session_id))


class PlayerUpdateEvent(events.OngakuEvent):
    """Player Update Event.

    Dispatched every x seconds with the current state of the player.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/websocket.html#player-update-op)
    """

    __slots__: typing.Sequence[str] = (
        "_app",
        "_client",
        "_guild_id",
        "_session",
        "_state",
    )

    def __init__(
        self,
        app: hikari.RESTAware,
        client: Client,
        session: session.Session,
        *,
        guild_id: hikari.Snowflake,
        state: player.State,
    ) -> None:
        self._app = app
        self._client = client
        self._session = session
        self._guild_id = guild_id
        self._state = state

    @classmethod
    def from_session(
        cls,
        session: session.Session,
        *,
        guild_id: hikari.Snowflake,
        state: player.State,
    ) -> PlayerUpdateEvent:
        """Build the player update event with just a session."""
        return cls(session.app, session.client, session, guild_id=guild_id, state=state)

    @property
    def app(self) -> hikari.RESTAware:  # noqa: D102 This has an inherited documentation string.
        return self._app

    @property
    def client(self) -> Client:  # noqa: D102 This has an inherited documentation string.
        return self._client

    @property
    def session(self) -> session.Session:  # noqa: D102 This has an inherited documentation string.
        return self._session

    @property
    def guild_id(self) -> hikari.Snowflake:
        """The guild related to this event."""
        return self._guild_id

    @property
    def state(self) -> player.State:
        """The player state."""
        return self._state

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlayerUpdateEvent):
            return False

        return self.guild_id == other.guild_id and self.state == other.state

    def __hash__(self) -> int:
        return hash((self.guild_id, self.state))


class StatisticsEvent(events.OngakuEvent):
    """Statistics Event.

    A collection of statistics sent every minute.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/websocket.html#stats-op)
    """

    __slots__: typing.Sequence[str] = (
        "_app",
        "_client",
        "_cpu",
        "_frame_statistics",
        "_memory",
        "_players",
        "_playing_players",
        "_session",
        "_uptime",
    )

    def __init__(
        self,
        app: hikari.RESTAware,
        client: Client,
        session: session.Session,
        *,
        players: int,
        playing_players: int,
        uptime: int,
        memory: statistics.Memory,
        cpu: statistics.Cpu,
        frame_statistics: statistics.FrameStatistics | None,
    ) -> None:
        self._app = app
        self._client = client
        self._session = session
        self._players = players
        self._playing_players = playing_players
        self._uptime = uptime
        self._memory = memory
        self._cpu = cpu
        self._frame_statistics = frame_statistics

    @classmethod
    def from_session(
        cls,
        session: session.Session,
        *,
        players: int,
        playing_players: int,
        uptime: int,
        memory: statistics.Memory,
        cpu: statistics.Cpu,
        frame_statistics: statistics.FrameStatistics | None,
    ) -> StatisticsEvent:
        """Build the statistics event with just a session."""
        return cls(
            session.app,
            session.client,
            session,
            players=players,
            playing_players=playing_players,
            uptime=uptime,
            memory=memory,
            cpu=cpu,
            frame_statistics=frame_statistics,
        )

    @property
    def app(self) -> hikari.RESTAware:  # noqa: D102 This has an inherited documentation string.
        return self._app

    @property
    def client(self) -> Client:  # noqa: D102 This has an inherited documentation string.
        return self._client

    @property
    def session(self) -> session.Session:  # noqa: D102 This has an inherited documentation string.
        return self._session

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
    def memory(self) -> statistics.Memory:
        """The memory stats of the session."""
        return self._memory

    @property
    def cpu(self) -> statistics.Cpu:
        """The CPU stats of the session."""
        return self._cpu

    @property
    def frame_statistics(self) -> statistics.FrameStatistics | None:
        """The frame statistics of the session."""
        return self._frame_statistics

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StatisticsEvent):
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


class WebsocketClosedEvent(events.OngakuEvent):
    """Websocket Closed Event.

    Dispatched when an audio WebSocket (to Discord) is closed.
    This can happen for various reasons (normal and abnormal),
    e.g. when using an expired voice server update.

    See the [Discord Docs](https://discord.com/developers/docs/topics/opcodes-and-status-codes#voice-voice-close-event-codes).

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/websocket.html#websocketclosedevent)
    """

    __slots__: typing.Sequence[str] = (
        "_app",
        "_by_remote",
        "_client",
        "_code",
        "_guild_id",
        "_reason",
        "_session",
    )

    def __init__(
        self,
        app: hikari.RESTAware,
        client: Client,
        session: session.Session,
        *,
        guild_id: hikari.Snowflake,
        code: int,
        reason: str,
        by_remote: bool,
    ) -> None:
        self._app = app
        self._client = client
        self._session = session
        self._guild_id = guild_id
        self._code = code
        self._reason = reason
        self._by_remote = by_remote

    @classmethod
    def from_session(
        cls,
        session: session.Session,
        *,
        guild_id: hikari.Snowflake,
        code: int,
        reason: str,
        by_remote: bool,
    ) -> WebsocketClosedEvent:
        """Build the websocket closed event with just a session."""
        return cls(
            session.app,
            session.client,
            session,
            guild_id=guild_id,
            code=code,
            reason=reason,
            by_remote=by_remote,
        )

    @property
    def app(self) -> hikari.RESTAware:  # noqa: D102 This has an inherited documentation string.
        return self._app

    @property
    def client(self) -> Client:  # noqa: D102 This has an inherited documentation string.
        return self._client

    @property
    def session(self) -> session.Session:  # noqa: D102 This has an inherited documentation string.
        return self._session

    @property
    def guild_id(self) -> hikari.Snowflake:
        """The guild related to this event."""
        return self._guild_id

    @property
    def code(self) -> int:
        """The error code that discord responds with."""
        return self._code

    @property
    def reason(self) -> str:
        """The close reason."""
        return self._reason

    @property
    def by_remote(self) -> bool:
        """Whether the connection was closed by Discord."""
        return self._by_remote

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WebsocketClosedEvent):
            return False

        return (
            self.guild_id == other.guild_id
            and self.code == other.code
            and self.reason == other.reason
            and self.by_remote == other.by_remote
        )

    def __hash__(self) -> int:
        return hash((self.guild_id, self.code, self.reason, self.by_remote))


class SessionConnectedEvent(events.SessionEvent):
    """Session Connected Event.

    Dispatched when a session successfully connects to a lavalink server.
    """

    __slots__: typing.Sequence[str] = ("_app", "_client", "_session")

    def __init__(
        self,
        app: hikari.RESTAware,
        client: Client,
        session: session.Session,
    ) -> None:
        self._app = app
        self._client = client
        self._session = session

    @classmethod
    def from_session(
        cls,
        session: session.Session,
    ) -> SessionConnectedEvent:
        """Build the session connected event with just a session."""
        return cls(session.app, session.client, session)

    @property
    def app(self) -> hikari.RESTAware:  # noqa: D102 This has an inherited documentation string.
        return self._app

    @property
    def client(self) -> Client:  # noqa: D102 This has an inherited documentation string.
        return self._client

    @property
    def session(self) -> session.Session:  # noqa: D102 This has an inherited documentation string.
        return self._session


class SessionDisconnectedEvent(events.SessionEvent):
    """Session Disconnected Event.

    Dispatched when a session disconnects from a lavalink server.
    """

    __slots__: typing.Sequence[str] = (
        "_app",
        "_client",
        "_code",
        "_reason",
        "_session",
    )

    def __init__(
        self,
        app: hikari.RESTAware,
        client: Client,
        session: session.Session,
        *,
        code: aiohttp.WSCloseCode,
        reason: str | None,
    ) -> None:
        self._app = app
        self._client = client
        self._session = session
        self._code = code
        self._reason = reason

    @classmethod
    def from_session(
        cls,
        session: session.Session,
        *,
        code: aiohttp.WSCloseCode,
        reason: str | None,
    ) -> SessionDisconnectedEvent:
        """Build the session disconnected event with just a session."""
        return cls(session.app, session.client, session, code=code, reason=reason)

    @property
    def app(self) -> hikari.RESTAware:  # noqa: D102 This has an inherited documentation string.
        return self._app

    @property
    def client(self) -> Client:  # noqa: D102 This has an inherited documentation string.
        return self._client

    @property
    def session(self) -> session.Session:  # noqa: D102 This has an inherited documentation string.
        return self._session

    @property
    def code(self) -> aiohttp.WSCloseCode:
        """The code received from the lavalink server."""
        return self._code

    @property
    def reason(self) -> str | None:
        """The reason for the disconnection."""
        return self._reason

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SessionDisconnectedEvent):
            return False

        return self.code == other.code and self.reason == other.reason

    def __hash__(self) -> int:
        return hash((self.code, self.reason))


class SessionErrorEvent(events.SessionEvent):
    """Session Error Event.

    Dispatched when a session receives an error from a lavalink server.
    """

    __slots__: typing.Sequence[str] = ("_app", "_client", "_session")

    def __init__(
        self,
        app: hikari.RESTAware,
        client: Client,
        session: session.Session,
    ) -> None:
        self._app = app
        self._client = client
        self._session = session

    @classmethod
    def from_session(
        cls,
        session: session.Session,
    ) -> SessionErrorEvent:
        """Build the session disconnected event with just a session."""
        return cls(session.app, session.client, session)

    @property
    def app(self) -> hikari.RESTAware:
        return self._app

    @property
    def client(self) -> Client:
        return self._client

    @property
    def session(self) -> session.Session:
        return self._session


class TrackStartEvent(events.TrackEvent):
    """Track start event.

    Dispatched when a track starts playing.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/websocket.html#trackstartevent)
    """

    __slots__: typing.Sequence[str] = (
        "_app",
        "_client",
        "_guild_id",
        "_session",
        "_track",
    )

    def __init__(
        self,
        app: hikari.RESTAware,
        client: Client,
        session: session.Session,
        *,
        guild_id: hikari.Snowflake,
        track: track.Track,
    ) -> None:
        self._app = app
        self._client = client
        self._session = session
        self._guild_id = guild_id
        self._track = track

    @classmethod
    def from_session(
        cls,
        session: session.Session,
        *,
        guild_id: hikari.Snowflake,
        track: track.Track,
    ) -> TrackStartEvent:
        """Build the track start event with just a session."""
        return cls(session.app, session.client, session, guild_id=guild_id, track=track)

    @property
    def app(self) -> hikari.RESTAware:  # noqa: D102 This has an inherited documentation string.
        return self._app

    @property
    def client(self) -> Client:  # noqa: D102 This has an inherited documentation string.
        return self._client

    @property
    def session(self) -> session.Session:  # noqa: D102 This has an inherited documentation string.
        return self._session

    @property
    def guild_id(self) -> hikari.Snowflake:  # noqa: D102 This has an inherited documentation string.
        return self._guild_id

    @property
    def track(self) -> track.Track:  # noqa: D102 This has an inherited documentation string.
        return self._track

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrackStartEvent):
            return False

        return self.guild_id == other.guild_id and self.track == other.track

    def __hash__(self) -> int:
        return hash((self.guild_id, self.track))


class TrackEndEvent(events.TrackEvent):
    """Track end event.

    Dispatched when a track ends.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/websocket.html#trackendevent)
    """

    __slots__: typing.Sequence[str] = (
        "_app",
        "_client",
        "_guild_id",
        "_reason",
        "_session",
        "_track",
    )

    def __init__(
        self,
        app: hikari.RESTAware,
        client: Client,
        session: session.Session,
        *,
        guild_id: hikari.Snowflake,
        track: track.Track,
        reason: track.TrackEndReasonType,
    ) -> None:
        self._app = app
        self._client = client
        self._session = session
        self._guild_id = guild_id
        self._track = track
        self._reason = reason

    @classmethod
    def from_session(
        cls,
        session: session.Session,
        *,
        guild_id: hikari.Snowflake,
        track: track.Track,
        reason: track.TrackEndReasonType,
    ) -> TrackEndEvent:
        """Build the track end event with just a session."""
        return cls(
            session.app,
            session.client,
            session,
            guild_id=guild_id,
            track=track,
            reason=reason,
        )

    @property
    def app(self) -> hikari.RESTAware:  # noqa: D102 This has an inherited documentation string.
        return self._app

    @property
    def client(self) -> Client:  # noqa: D102 This has an inherited documentation string.
        return self._client

    @property
    def session(self) -> session.Session:  # noqa: D102 This has an inherited documentation string.
        return self._session

    @property
    def guild_id(self) -> hikari.Snowflake:  # noqa: D102 This has an inherited documentation string.
        return self._guild_id

    @property
    def track(self) -> track.Track:  # noqa: D102 This has an inherited documentation string.
        return self._track

    @property
    def reason(self) -> track.TrackEndReasonType:
        """The reason for the track ending."""
        return self._reason

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrackEndEvent):
            return False

        return (
            self.guild_id == other.guild_id
            and self.track == other.track
            and self.reason == other.reason
        )

    def __hash__(self) -> int:
        return hash((self.guild_id, self.track, self.reason))


class TrackExceptionEvent(events.TrackEvent):
    """Track exception event.

    Dispatched when a track throws an exception.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/websocket.html#trackexceptionevent)
    """

    __slots__: typing.Sequence[str] = (
        "_app",
        "_client",
        "_exception",
        "_guild_id",
        "_session",
        "_track",
    )

    def __init__(
        self,
        app: hikari.RESTAware,
        client: Client,
        session: session.Session,
        *,
        guild_id: hikari.Snowflake,
        track: track.Track,
        exception: errors.ExceptionError,
    ) -> None:
        self._app = app
        self._client = client
        self._session = session
        self._guild_id = guild_id
        self._track = track
        self._exception = exception

    @classmethod
    def from_session(
        cls,
        session: session.Session,
        *,
        guild_id: hikari.Snowflake,
        track: track.Track,
        exception: errors.ExceptionError,
    ) -> TrackExceptionEvent:
        """Build the track exception event with just a session."""
        return cls(
            session.app,
            session.client,
            session,
            guild_id=guild_id,
            track=track,
            exception=exception,
        )

    @property
    def app(self) -> hikari.RESTAware:  # noqa: D102 This has an inherited documentation string.
        return self._app

    @property
    def client(self) -> Client:  # noqa: D102 This has an inherited documentation string.
        return self._client

    @property
    def session(self) -> session.Session:  # noqa: D102 This has an inherited documentation string.
        return self._session

    @property
    def guild_id(self) -> hikari.Snowflake:  # noqa: D102 This has an inherited documentation string.
        return self._guild_id

    @property
    def track(self) -> track.Track:  # noqa: D102 This has an inherited documentation string.
        return self._track

    @property
    def exception(self) -> errors.ExceptionError:
        """The occurred exception."""
        return self._exception

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrackExceptionEvent):
            return False

        return (
            self.guild_id == other.guild_id
            and self.track == other.track
            and self.exception == other.exception
        )

    def __hash__(self) -> int:
        return hash((self.guild_id, self.track, self.exception))


class TrackStuckEvent(events.TrackEvent):
    """Track stuck event.

    Dispatched when a track gets stuck while playing.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/websocket.html#trackstuckevent)
    """

    __slots__: typing.Sequence[str] = (
        "_app",
        "_client",
        "_guild_id",
        "_session",
        "_threshold_ms",
        "_track",
    )

    def __init__(
        self,
        app: hikari.RESTAware,
        client: Client,
        session: session.Session,
        *,
        guild_id: hikari.Snowflake,
        track: track.Track,
        threshold_ms: int,
    ) -> None:
        self._app = app
        self._client = client
        self._session = session
        self._guild_id = guild_id
        self._track = track
        self._threshold_ms = threshold_ms

    @classmethod
    def from_session(
        cls,
        session: session.Session,
        *,
        guild_id: hikari.Snowflake,
        track: track.Track,
        threshold_ms: int,
    ) -> TrackStuckEvent:
        """Build the track stuck event with just a session."""
        return cls(
            session.app,
            session.client,
            session,
            guild_id=guild_id,
            track=track,
            threshold_ms=threshold_ms,
        )

    @property
    def app(self) -> hikari.RESTAware:  # noqa: D102 This has an inherited documentation string.
        return self._app

    @property
    def client(self) -> Client:  # noqa: D102 This has an inherited documentation string.
        return self._client

    @property
    def session(self) -> session.Session:  # noqa: D102 This has an inherited documentation string.
        return self._session

    @property
    def guild_id(self) -> hikari.Snowflake:  # noqa: D102 This has an inherited documentation string.
        return self._guild_id

    @property
    def track(self) -> track.Track:  # noqa: D102 This has an inherited documentation string.
        return self._track

    @property
    def threshold_ms(self) -> int:
        """The threshold in milliseconds that was exceeded."""
        return self._threshold_ms

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrackStuckEvent):
            return False

        return (
            self.guild_id == other.guild_id
            and self.track == other.track
            and self.threshold_ms != other.threshold_ms
        )

    def __hash__(self) -> int:
        return hash((self.guild_id, self.track, self.threshold_ms))


class QueueEmptyEvent(events.QueueEvent):
    """Queue empty event.

    Dispatched when the player finishes all the tracks in the queue.
    """

    __slots__: typing.Sequence[str] = (
        "_app",
        "_client",
        "_guild_id",
        "_old_track",
        "_session",
    )

    def __init__(
        self,
        app: hikari.RESTAware,
        client: Client,
        session: session.Session,
        *,
        guild_id: hikari.Snowflake,
        old_track: track.Track,
    ) -> None:
        self._app = app
        self._client = client
        self._session = session
        self._guild_id = guild_id
        self._old_track = old_track

    @classmethod
    def from_session(
        cls,
        session: session.Session,
        *,
        guild_id: hikari.Snowflake,
        old_track: track.Track,
    ) -> QueueEmptyEvent:
        """Build the queue event with just a session."""
        return cls(
            session.app,
            session.client,
            session,
            guild_id=guild_id,
            old_track=old_track,
        )

    @property
    def app(self) -> hikari.RESTAware:  # noqa: D102 This has an inherited documentation string.
        return self._app

    @property
    def client(self) -> Client:  # noqa: D102 This has an inherited documentation string.
        return self._client

    @property
    def session(self) -> session.Session:  # noqa: D102 This has an inherited documentation string.
        return self._session

    @property
    def guild_id(self) -> hikari.Snowflake:  # noqa: D102 This has an inherited documentation string.
        return self._guild_id

    @property
    def old_track(self) -> track.Track:  # noqa: D102 This has an inherited documentation string.
        return self._old_track

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QueueEmptyEvent):
            return False

        return self.guild_id == other.guild_id and self.old_track == other.old_track

    def __hash__(self) -> int:
        return hash((self.guild_id, self.old_track))


class QueueNextEvent(events.QueueEvent):
    """Queue next event.

    Dispatched when the player starts playing a new track.
    """

    __slots__: typing.Sequence[str] = (
        "_app",
        "_client",
        "_guild_id",
        "_old_track",
        "_session",
        "_track",
    )

    def __init__(
        self,
        app: hikari.RESTAware,
        client: Client,
        session: session.Session,
        *,
        guild_id: hikari.Snowflake,
        track: track.Track,
        old_track: track.Track,
    ) -> None:
        self._app = app
        self._client = client
        self._session = session
        self._guild_id = guild_id
        self._track = track
        self._old_track = old_track

    @classmethod
    def from_session(
        cls,
        session: session.Session,
        *,
        guild_id: hikari.Snowflake,
        track: track.Track,
        old_track: track.Track,
    ) -> QueueNextEvent:
        """Build the queue next event with just a session."""
        return cls(
            session.app,
            session.client,
            session,
            guild_id=guild_id,
            track=track,
            old_track=old_track,
        )

    @property
    def app(self) -> hikari.RESTAware:  # noqa: D102 This has an inherited documentation string.
        return self._app

    @property
    def client(self) -> Client:  # noqa: D102 This has an inherited documentation string.
        return self._client

    @property
    def session(self) -> session.Session:  # noqa: D102 This has an inherited documentation string.
        return self._session

    @property
    def guild_id(self) -> hikari.Snowflake:  # noqa: D102 This has an inherited documentation string.
        return self._guild_id

    @property
    def old_track(self) -> track.Track:  # noqa: D102 This has an inherited documentation string.
        return self._old_track

    @property
    def track(self) -> track.Track:
        """The track related to this event."""
        return self._track

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QueueNextEvent):
            return False

        return (
            self.guild_id == other.guild_id
            and self.track == other.track
            and self.old_track == other.old_track
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.guild_id,
                self.track,
                self.old_track,
            ),
        )
