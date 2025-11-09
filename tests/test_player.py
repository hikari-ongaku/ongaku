from __future__ import annotations

import asyncio
import datetime
import typing
from unittest import mock

import hikari
import pytest

from ongaku import errors
from ongaku import events
from ongaku import playlist
from ongaku import track
from ongaku.player import PartialPlayer
from ongaku.player import Player
from ongaku.player import State
from ongaku.player import Voice

if typing.TYPE_CHECKING:
    from ongaku import session as session_


def test_partial_player():
    mock_track = mock.Mock()
    mock_state = mock.Mock()
    mock_voice = mock.Mock()
    mock_filters = mock.Mock()

    player = PartialPlayer(
        guild_id=hikari.Snowflake(123),
        track=mock_track,
        volume=1,
        is_paused=False,
        state=mock_state,
        voice=mock_voice,
        filters=mock_filters,
    )

    assert player.guild_id == hikari.Snowflake(123)
    assert player.track == mock_track
    assert player.volume == 1
    assert player.is_paused is False
    assert player.state == mock_state
    assert player.voice == mock_voice
    assert player.filters == mock_filters


class TestState:
    def test_properties(self):
        mock_time = mock.Mock()

        state = State(
            time=mock_time,
            position=1,
            is_connected=True,
            ping=2,
        )

        assert state.time == mock_time
        assert state.position == 1
        assert state.is_connected is True
        assert state.ping == 2

    def test_empty(self):
        state = State.empty()

        assert state.time == datetime.datetime.fromtimestamp(
            0,
            tz=datetime.timezone.utc,
        )
        assert state.position == 0
        assert state.is_connected is False
        assert state.ping == -1


class TestVoice:
    def test_properties(self):
        voice = Voice(
            token="token",
            endpoint="endpoint",
            session_id="session_id",
        )

        assert voice.token == "token"
        assert voice.endpoint == "endpoint"
        assert voice.session_id == "session_id"

    def test_empty(self):
        voice = Voice.empty()

        assert voice.token == ""
        assert voice.endpoint == ""
        assert voice.session_id == ""


class TestPlayer:
    def test_properties(self):
        session = mock.Mock()
        guild_id = hikari.Snowflake(123)

        with mock.patch.object(
            session.app.event_manager,
            "subscribe",
        ) as patched_subscribe:
            player = Player(session, guild_id)

        patched_subscribe.assert_has_calls(
            [
                mock.call(events.TrackEndEvent, player._track_end_event),
                mock.call(events.PlayerUpdateEvent, player._player_update_event),
            ],
        )

        assert player.session == session
        assert player.app == session.app
        assert player.channel_id is None
        assert player.is_alive is False
        assert player.position == 0
        assert player.autoplay is True
        assert player.loop is False
        assert player.is_connected is False
        assert player.is_connected is player.state.is_connected
        assert player.queue == []
        assert player.guild_id == hikari.Snowflake(123)
        assert player.track is None
        assert player.volume == -1
        assert player.is_paused is True
        assert player.state == State.empty()
        assert player.voice == Voice.empty()
        assert player.filters is None

    @staticmethod
    async def connect_events(
        event_type: type[hikari.Event],
        /,
        timeout: float | None,  # noqa: ARG004
    ) -> hikari.Event:
        if event_type == hikari.VoiceServerUpdateEvent:
            return hikari.VoiceServerUpdateEvent(
                app=mock.Mock(),
                shard=mock.Mock(),
                guild_id=hikari.Snowflake(1234567890),
                token="token",
                raw_endpoint="raw_endpoint",
            )

        if event_type == hikari.VoiceStateUpdateEvent:
            return hikari.VoiceStateUpdateEvent(
                shard=mock.Mock(),
                old_state=mock.Mock(),
                state=mock.Mock(
                    session_id="session_id",
                ),
            )

        raise Exception("Invalid event requested.")

    @pytest.mark.asyncio
    async def test_connect(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        voice = Voice(
            token="token",
            endpoint="raw_endpoint",
            session_id="session_id",
        )

        mock_player = mock.Mock(Player)

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(
                ongaku_session.client.app,
                "update_voice_state",
                new_callable=mock.AsyncMock,
            ) as patched_voice_state,
            mock.patch.object(
                player.app.event_manager,
                "wait_for",
                TestPlayer.connect_events,
            ),
            mock.patch(
                "ongaku.api.rest.RESTClient.update_player",
                new_callable=mock.AsyncMock,
                return_value=mock_player,
            ) as patched_update_player,
            mock.patch.object(
                player,
                "_update",
            ) as patched__update,
        ):
            await player.connect(987)

        patched_voice_state.assert_called_once_with(
            hikari.Snowflake(123),
            hikari.Snowflake(987),
            self_mute=False,
            self_deaf=True,
        )

        patched_update_player.assert_called_once_with(
            "session_id",
            hikari.Snowflake(123),
            voice=voice,
            no_replace=False,
            session=ongaku_session,
        )

        patched__update.assert_called_once_with(mock_player)

        assert player.voice is not None

        assert player.voice == voice

        assert player.is_alive is True

    @pytest.mark.asyncio
    async def test_connect_with_missing_session_id(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(ongaku_session, "_session_id", None),
            pytest.raises(errors.SessionStartError),
        ):
            await player.connect(123)

    @pytest.mark.asyncio
    async def test_connect_with_missing_events(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(
                ongaku_session.client.app,
                "update_voice_state",
                new_callable=mock.AsyncMock,
            ) as patched_voice_state,
            mock.patch.object(
                player.app.event_manager,
                "wait_for",
                new_callable=mock.AsyncMock,
                side_effect=asyncio.TimeoutError,
            ),
            pytest.raises(errors.PlayerConnectEventMissingError),
        ):
            await player.connect(987)

        patched_voice_state.assert_awaited_once_with(
            hikari.Snowflake(123),
            hikari.Snowflake(987),
            self_mute=False,
            self_deaf=True,
        )

    @pytest.mark.asyncio
    async def test_connect_with_missing_raw_endpoint(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(
                player.app.event_manager,
                "wait_for",
                new_callable=mock.AsyncMock,
                return_value=mock.Mock(raw_endpoint=None),
            ),
            pytest.raises(errors.PlayerConnectError),
        ):
            await player.connect(987654321)

    @pytest.mark.asyncio
    async def test_disconnect(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(
                ongaku_session.client.app,
                "update_voice_state",
                new_callable=mock.AsyncMock,
            ) as patched_voice_state,
            mock.patch.object(
                player.app.event_manager,
                "wait_for",
                TestPlayer.connect_events,
            ),
            mock.patch(
                "ongaku.api.rest.RESTClient.update_player",
                new_callable=mock.AsyncMock,
                return_value=mock.Mock(),
            ),
            mock.patch.object(
                player,
                "_update",
            ),
            mock.patch(
                "ongaku.api.rest.RESTClient.delete_player",
            ) as patched_delete,
            mock.patch("ongaku.player.Player.clear") as patched_clear,
        ):
            await player.connect(987)

            await player.disconnect()

            patched_clear.assert_called_once()

            patched_delete.assert_called_once_with(
                ongaku_session.session_id,
                hikari.Snowflake(123),
                session=ongaku_session,
            )

            assert player.is_alive is False

            patched_voice_state.assert_called_with(hikari.Snowflake(123), None)

    @pytest.mark.asyncio
    async def test_disconnect_with_missing_session_id(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(ongaku_session, "_session_id", None),
            pytest.raises(errors.SessionStartError),
        ):
            await player.disconnect()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "track",
        [
            None,
            mock.Mock(),
        ],
    )
    @pytest.mark.parametrize(
        "requestor",
        [mock.Mock(hikari.PartialUser, __int__=mock.Mock(return_value=123456)), None],
    )
    async def test_play(
        self,
        ongaku_session: session_.Session,
        track: track.Track | None,
        requestor: hikari.PartialUser | None,
    ):
        player = Player(ongaku_session, 123)

        track_1 = mock.Mock()
        track_2 = mock.Mock()

        player._queue = [
            track_1,
            track_2,
        ]

        with (
            mock.patch.object(player, "_update") as patched__update,
            mock.patch.object(player, "_channel_id"),
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(ongaku_session, "_client") as patched_client,
            mock.patch.object(patched_client, "rest") as patched_rest,
            mock.patch.object(
                patched_rest,
                "update_player",
                new_callable=mock.AsyncMock,
            ) as patched_update_player,
        ):
            await player.play(track, requestor=requestor)

        expected_track = track
        if expected_track is None:
            expected_track = track_1

        if track is not None and requestor:
            expected_track._requestor = hikari.Snowflake(requestor)

        if track:
            assert player._queue == [expected_track, track_1, track_2]
        else:
            assert player._queue == [track_1, track_2]
        patched_update_player.assert_awaited_once_with(
            "session_id",
            player.guild_id,
            track=expected_track,
            no_replace=False,
            session=ongaku_session,
        )
        patched__update.assert_called_once_with(patched_update_player.return_value)

    @pytest.mark.asyncio
    async def test_play_with_missing_session_id(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(ongaku_session, "_session_id", None),
            pytest.raises(errors.SessionStartError),
        ):
            await player.play()

    @pytest.mark.asyncio
    async def test_play_with_missing_channel_id(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            pytest.raises(errors.PlayerNotConnectedError, match=r"^$"),
        ):
            await player.play()

    @pytest.mark.asyncio
    async def test_play_with_missing_queue(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(player, "_channel_id"),
            pytest.raises(
                errors.PlayerQueueEmptyError,
                match=r"^$",
            ),
        ):
            await player.play()

    @pytest.mark.parametrize(
        "current",
        [
            [],
            [
                mock.Mock(track.Track, requestor=None),
                mock.Mock(track.Track, requestor=None),
            ],
        ],
    )
    @pytest.mark.parametrize(
        "add",
        [
            mock.Mock(track.Track, requestor=None),
            [
                mock.Mock(track.Track, requestor=None),
                mock.Mock(track.Track, requestor=None),
            ],
            mock.Mock(
                playlist.Playlist,
                tracks=[
                    mock.Mock(track.Track, requestor=None),
                    mock.Mock(track.Track, requestor=None),
                ],
            ),
        ],
    )
    @pytest.mark.parametrize(
        "requestor",
        [mock.Mock(hikari.PartialUser, __int__=mock.Mock(return_value=123456)), None],
    )
    def test_add(
        self,
        ongaku_session: session_.Session,
        current: list[track.Track],
        add: list[track.Track] | playlist.Playlist | track.Track,
        requestor: hikari.PartialUser | None,
    ):
        player = Player(ongaku_session, 123)

        player._queue = current

        player.add(add, requestor=requestor)

        added_tracks: list[track.Track] = []
        if isinstance(add, track.Track):
            add._requestor = hikari.Snowflake(requestor) if requestor else None
            added_tracks = [add]
        elif isinstance(add, playlist.Playlist):
            for t in add.tracks:
                t._requestor = hikari.Snowflake(requestor) if requestor else None
                added_tracks.append(t)
        else:
            for t in add:
                t._requestor = hikari.Snowflake(requestor) if requestor else None
                added_tracks.append(t)

        expected_queue = current
        expected_queue.extend(added_tracks)
        assert player._queue == expected_queue

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("current", "value", "expected"),
        [
            (True, True, True),
            (False, False, False),
            (True, False, False),
            (False, True, True),
            (True, None, False),
            (False, None, True),
        ],
    )
    async def test_pause(
        self,
        ongaku_session: session_.Session,
        current: bool,
        value: bool | None,
        expected: bool,
    ):
        player = Player(ongaku_session, 123)

        player._is_paused = current

        with (
            mock.patch.object(player, "_update") as patched__update,
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(ongaku_session, "_client") as patched_client,
            mock.patch.object(patched_client, "rest") as patched_rest,
            mock.patch.object(
                patched_rest,
                "update_player",
                new_callable=mock.AsyncMock,
            ) as patched_update_player,
        ):
            await player.pause(value)

        patched_update_player.assert_awaited_once_with(
            "session_id",
            player.guild_id,
            paused=expected,
            session=ongaku_session,
        )
        patched__update.assert_called_once_with(patched_update_player.return_value)

    @pytest.mark.asyncio
    async def test_pause_with_missing_session_id(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(ongaku_session, "_session_id", None),
            pytest.raises(errors.SessionStartError),
        ):
            await player.pause()

    @pytest.mark.asyncio
    async def test_stop(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(player, "_update") as patched__update,
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(ongaku_session, "_client") as patched_client,
            mock.patch.object(patched_client, "rest") as patched_rest,
            mock.patch.object(
                patched_rest,
                "update_player",
                new_callable=mock.AsyncMock,
            ) as patched_update_player,
        ):
            await player.stop()

        patched_update_player.assert_awaited_once_with(
            "session_id",
            player.guild_id,
            track=None,
            no_replace=False,
            session=ongaku_session,
        )
        patched__update.assert_called_once_with(patched_update_player.return_value)

    @pytest.mark.asyncio
    async def test_stop_with_missing_session_id(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(ongaku_session, "_session_id", None),
            pytest.raises(errors.SessionStartError),
        ):
            await player.stop()

    @pytest.mark.asyncio
    async def test_shuffle(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        track_1 = mock.Mock()
        track_2 = mock.Mock()
        track_3 = mock.Mock()
        track_4 = mock.Mock()
        track_5 = mock.Mock()

        queue_order: list[track.Track] = [
            track_1,
            track_2,
            track_3,
            track_4,
            track_5,
        ]

        player._queue = queue_order

        exact = 0
        for _ in range(10):
            player.shuffle()

            assert player.queue[0] == track_1

            if player.queue == queue_order:
                exact += 1

        if exact >= 5:
            raise Exception("Too many exact matches.")

    @pytest.mark.asyncio
    async def test_skip(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        track_1 = mock.Mock()
        track_2 = mock.Mock()
        track_3 = mock.Mock()

        player._queue = [
            track_1,
            track_2,
            track_3,
        ]

        with (
            mock.patch.object(player, "_update") as patched__update,
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(ongaku_session, "_client") as patched_client,
            mock.patch.object(patched_client, "rest") as patched_rest,
            mock.patch.object(
                patched_rest,
                "update_player",
                new_callable=mock.AsyncMock,
            ) as patched_update_player,
        ):
            await player.skip()

        assert player.queue == [track_2, track_3]
        patched_update_player.assert_awaited_once_with(
            "session_id",
            player.guild_id,
            track=track_2,
            no_replace=False,
            session=ongaku_session,
        )
        patched__update.assert_called_once_with(patched_update_player.return_value)

    @pytest.mark.asyncio
    async def test_skip_when_one(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        track_1 = mock.Mock()

        player._queue = [
            track_1,
        ]

        with (
            mock.patch.object(player, "_update") as patched__update,
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(ongaku_session, "_client") as patched_client,
            mock.patch.object(patched_client, "rest") as patched_rest,
            mock.patch.object(
                patched_rest,
                "update_player",
                new_callable=mock.AsyncMock,
            ) as patched_update_player,
        ):
            await player.skip()

        assert player.queue == []
        patched_update_player.assert_awaited_once_with(
            "session_id",
            player.guild_id,
            track=None,
            no_replace=False,
            session=ongaku_session,
        )
        patched__update.assert_called_once_with(patched_update_player.return_value)

    @pytest.mark.asyncio
    async def test_skip_with_multiple(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        track_1 = mock.Mock()
        track_2 = mock.Mock()
        track_3 = mock.Mock()

        player._queue = [
            track_1,
            track_2,
            track_3,
        ]

        with (
            mock.patch.object(player, "_update") as patched__update,
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(ongaku_session, "_client") as patched_client,
            mock.patch.object(patched_client, "rest") as patched_rest,
            mock.patch.object(
                patched_rest,
                "update_player",
                new_callable=mock.AsyncMock,
            ) as patched_update_player,
        ):
            await player.skip(2)

        assert player.queue == [track_3]
        patched_update_player.assert_awaited_once_with(
            "session_id",
            player.guild_id,
            track=track_3,
            no_replace=False,
            session=ongaku_session,
        )
        patched__update.assert_called_once_with(patched_update_player.return_value)

    @pytest.mark.asyncio
    async def test_skip_with_missing_session_id(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        player._queue = [mock.Mock(track.Track), mock.Mock(track.Track)]

        with (
            mock.patch.object(ongaku_session, "_session_id", None),
            pytest.raises(errors.SessionStartError),
        ):
            await player.skip()

    @pytest.mark.asyncio
    async def test_skip_with_invalid_amount(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        with pytest.raises(ValueError, match=r"^$"):
            await player.skip(-3)

    @pytest.mark.asyncio
    async def test_skip_with_empty_queue(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        assert player.queue == []

        with pytest.raises(errors.PlayerQueueEmptyError, match=r"^$"):
            await player.skip()

    @pytest.mark.asyncio
    async def test_remove(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        track_1 = mock.Mock()
        track_2 = mock.Mock()

        player._queue = [
            track_1,
            track_2,
        ]

        with mock.patch.object(ongaku_session, "_session_id", "session_id"):
            await player.remove(1)

        assert player._queue == [track_1]

    @pytest.mark.asyncio
    async def test_remove_with_track(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        track_1 = mock.Mock(track.Track)
        track_2 = mock.Mock(track.Track)

        player._queue = [
            track_1,
            track_2,
        ]

        with mock.patch.object(ongaku_session, "_session_id", "session_id"):
            await player.remove(track_2)

        assert player._queue == [track_1]

    @pytest.mark.asyncio
    async def test_remove_first_track(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        track_1 = mock.Mock()
        track_2 = mock.Mock()

        player._queue = [
            track_1,
            track_2,
        ]

        with (
            mock.patch.object(player, "_update") as patched__update,
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(ongaku_session, "_client") as patched_client,
            mock.patch.object(patched_client, "rest") as patched_rest,
            mock.patch.object(
                patched_rest,
                "update_player",
                new_callable=mock.AsyncMock,
            ) as patched_update_player,
        ):
            await player.remove(0)

        assert player._queue == [track_2]
        patched_update_player.assert_awaited_once_with(
            "session_id",
            player.guild_id,
            track=None,
            session=ongaku_session,
        )
        patched__update.assert_called_once_with(patched_update_player.return_value)

    @pytest.mark.asyncio
    async def test_remove_first_track_and_play_next(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        track_1 = mock.Mock()
        track_2 = mock.Mock()
        track_3 = mock.Mock()

        player._queue = [
            track_1,
            track_2,
            track_3,
        ]

        with (
            mock.patch.object(player, "_update") as patched__update,
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(ongaku_session, "_client") as patched_client,
            mock.patch.object(patched_client, "rest") as patched_rest,
            mock.patch.object(
                patched_rest,
                "update_player",
                new_callable=mock.AsyncMock,
            ) as patched_update_player,
        ):
            await player.remove(0, play_next=True)

        assert player._queue == [track_2, track_3]
        patched_update_player.assert_awaited_once_with(
            "session_id",
            player.guild_id,
            track=track_2,
            session=ongaku_session,
        )
        patched__update.assert_called_once_with(patched_update_player.return_value)

    @pytest.mark.asyncio
    async def test_remove_with_empty_queue(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        assert player._queue == []

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            pytest.raises(errors.PlayerQueueEmptyError, match=r"^$"),
        ):
            await player.remove(1)

    @pytest.mark.asyncio
    async def test_remove_with_invalid_index(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        track_1 = mock.Mock()
        track_2 = mock.Mock()

        player._queue = [
            track_1,
            track_2,
        ]

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            pytest.raises(
                errors.PlayerQueueError,
                match=r"^$",
            ),
        ):
            await player.remove(99)

    @pytest.mark.asyncio
    async def test_remove_with_track_with_invalid_index(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        track_1 = mock.Mock(track.Track)
        track_2 = mock.Mock(track.Track)

        player._queue = [
            track_1,
            track_2,
        ]

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            pytest.raises(
                errors.PlayerQueueError,
                match=r"^$",
            ),
        ):
            await player.remove(mock.Mock(track.Track))

    @pytest.mark.asyncio
    async def test_clear(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        player._queue = [
            mock.Mock(),
            mock.Mock(),
        ]

        with (
            mock.patch.object(player, "_update") as patched__update,
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(ongaku_session, "_client") as patched_client,
            mock.patch.object(patched_client, "rest") as patched_rest,
            mock.patch.object(
                patched_rest,
                "update_player",
                new_callable=mock.AsyncMock,
            ) as patched_update_player,
        ):
            await player.clear()

        assert player._queue == []
        patched_update_player.assert_awaited_once_with(
            "session_id",
            player.guild_id,
            track=None,
            session=ongaku_session,
        )
        patched__update.assert_called_once_with(patched_update_player.return_value)

    @pytest.mark.asyncio
    async def test_clear_with_missing_session_id(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(ongaku_session, "_session_id", None),
            pytest.raises(errors.SessionStartError),
        ):
            await player.clear()

    @pytest.mark.parametrize(
        ("current", "value", "expected"),
        [
            (True, True, True),
            (False, False, False),
            (True, False, False),
            (False, True, True),
            (True, None, False),
            (False, None, True),
        ],
    )
    def test_set_autoplay(
        self,
        ongaku_session: session_.Session,
        current: bool,
        value: bool | None,
        expected: bool,
    ):
        player = Player(ongaku_session, 123)

        player._autoplay = current

        assert player.set_autoplay(value) is expected

    @pytest.mark.asyncio
    async def test_set_volume(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(player, "_update") as patched__update,
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(ongaku_session, "_client") as patched_client,
            mock.patch.object(patched_client, "rest") as patched_rest,
            mock.patch.object(
                patched_rest,
                "update_player",
                new_callable=mock.AsyncMock,
            ) as patched_update_player,
        ):
            await player.set_volume(50)

        patched_update_player.assert_awaited_once_with(
            "session_id",
            player.guild_id,
            volume=50,
            no_replace=False,
            session=ongaku_session,
        )
        patched__update.assert_called_once_with(patched_update_player.return_value)

    @pytest.mark.asyncio
    async def test_set_volume_with_missing_session_id(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(ongaku_session, "_session_id", None),
            pytest.raises(errors.SessionStartError),
        ):
            await player.set_volume()

    @pytest.mark.asyncio
    async def test_set_volume_with_invalid_volume(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            pytest.raises(ValueError, match=r"^$"),
        ):
            await player.set_volume(-50)

    @pytest.mark.asyncio
    async def test_set_position(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        player._queue = [
            mock.Mock(info=mock.Mock(length=10000)),
        ]

        with (
            mock.patch.object(player, "_update") as patched__update,
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(ongaku_session, "_client") as patched_client,
            mock.patch.object(patched_client, "rest") as patched_rest,
            mock.patch.object(
                patched_rest,
                "update_player",
                new_callable=mock.AsyncMock,
            ) as patched_update_player,
        ):
            await player.set_position(5400)

        patched_update_player.assert_awaited_once_with(
            "session_id",
            player.guild_id,
            position=5400,
            no_replace=False,
            session=ongaku_session,
        )
        patched__update.assert_called_once_with(patched_update_player.return_value)

    @pytest.mark.asyncio
    async def test_set_invalid_position(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        player._queue = []

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            pytest.raises(
                ValueError,
                match=r"^$",
            ),
        ):
            await player.set_position(-5400)

    @pytest.mark.asyncio
    async def test_set_position_with_missing_session_id(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(ongaku_session, "_session_id", None),
            pytest.raises(errors.SessionStartError),
        ):
            await player.set_position(10)

    @pytest.mark.asyncio
    async def test_set_position_with_invalid_position(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        player._queue = [
            mock.Mock(info=mock.Mock(length=5000)),
        ]

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            pytest.raises(
                ValueError,
                match=r"^$",
            ),
        ):
            await player.set_position(5400)

    @pytest.mark.asyncio
    async def test_set_position_with_missing_queue(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        assert player._queue == []

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            pytest.raises(errors.PlayerQueueEmptyError, match=r"^$"),
        ):
            await player.set_position(5400)

    @pytest.mark.asyncio
    async def test_set_filters(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        filters_builder = mock.Mock()

        with (
            mock.patch.object(player, "_update") as patched__update,
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(ongaku_session, "_client") as patched_client,
            mock.patch.object(patched_client, "rest") as patched_rest,
            mock.patch.object(
                patched_rest,
                "update_player",
                new_callable=mock.AsyncMock,
            ) as patched_update_player,
        ):
            await player.set_filters(filters_builder)

        patched_update_player.assert_awaited_once_with(
            "session_id",
            player.guild_id,
            filters=filters_builder,
            session=ongaku_session,
        )
        patched__update.assert_called_once_with(patched_update_player.return_value)

    @pytest.mark.asyncio
    async def test_set_filters_with_missing_session_id(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        with (
            mock.patch.object(ongaku_session, "_session_id", None),
            pytest.raises(errors.SessionStartError),
        ):
            await player.stop()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("current", "value", "expected"),
        [
            (True, True, True),
            (False, False, False),
            (True, False, False),
            (False, True, True),
            (True, None, False),
            (False, None, True),
        ],
    )
    async def test_set_loop(
        self,
        ongaku_session: session_.Session,
        current: bool,
        value: bool | None,
        expected: bool,
    ):
        player = Player(ongaku_session, 123)

        player._loop = current

        assert player.set_loop(value) is expected

    @pytest.mark.asyncio
    async def test_transfer(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        player_queue: list[track.Track] = [
            mock.Mock(),
            mock.Mock(),
        ]

        player._queue = player_queue

        mock_session = mock.Mock()

        with (
            mock.patch("ongaku.player.Player.disconnect") as patched_disconnect,
            mock.patch("ongaku.player.Player.connect") as patched_connect,
            mock.patch("ongaku.player.Player.play") as patched_play,
            mock.patch("ongaku.player.Player.set_position") as patched_set_position,
        ):
            player = await player.transfer(session=mock_session)

        patched_disconnect.assert_not_called()
        patched_connect.assert_not_called()
        patched_play.assert_not_called()
        patched_set_position.assert_not_called()
        assert player._queue == player_queue

    @pytest.mark.asyncio
    async def test_transfer_with_connection(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        mock_session = mock.Mock()

        with (
            mock.patch.object(player, "_channel_id", 1234),
            mock.patch("ongaku.player.Player.is_connected", True),
            mock.patch("ongaku.player.Player.disconnect") as patched_disconnect,
            mock.patch("ongaku.player.Player.connect") as patched_connect,
            mock.patch("ongaku.player.Player.play") as patched_play,
            mock.patch("ongaku.player.Player.set_position") as patched_set_position,
        ):
            await player.transfer(session=mock_session)

        patched_disconnect.assert_awaited_once_with()
        patched_connect.assert_awaited_once_with(1234)
        patched_play.assert_not_called()
        patched_set_position.assert_not_called()

    @pytest.mark.asyncio
    async def test_transfer_with_connection_and_playing(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        player._is_paused = False
        player._track = mock.Mock(position=1000)
        player._queue = [player._track]
        player._position = 827

        mock_session = mock.Mock()

        with (
            mock.patch.object(player, "_channel_id", 1234),
            mock.patch("ongaku.player.Player.is_connected", True),
            mock.patch("ongaku.player.Player.disconnect") as patched_disconnect,
            mock.patch("ongaku.player.Player.connect") as patched_connect,
            mock.patch("ongaku.player.Player.play") as patched_play,
            mock.patch("ongaku.player.Player.set_position") as patched_set_position,
        ):
            await player.transfer(session=mock_session)

        patched_disconnect.assert_awaited_once_with()
        patched_connect.assert_awaited_once_with(1234)
        patched_play.assert_awaited_once_with()
        patched_set_position.assert_awaited_once_with(827)

    @pytest.mark.asyncio
    async def test__update(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        mock_player = mock.Mock()

        player._update(mock_player)

        assert player.volume == mock_player.volume
        assert player.is_paused == mock_player.is_paused
        assert player.state == mock_player.state
        assert player.voice == mock_player.voice
        assert player.filters == mock_player.filters
        assert player.is_connected == mock_player.state.is_connected
        assert player.track == mock_player.track

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "end_reason",
        [
            track.TrackEndReasonType.FINISHED,
            track.TrackEndReasonType.LOADFAILED,
            track.TrackEndReasonType.STOPPED,
            track.TrackEndReasonType.REPLACED,
            track.TrackEndReasonType.CLEANUP,
        ],
    )
    async def test__track_end_event(
        self,
        ongaku_session: session_.Session,
        end_reason: track.TrackEndReasonType,
    ):
        player = Player(ongaku_session, 123)

        track_1 = mock.Mock()

        player._queue = [
            track_1,
        ]

        assert player.loop is False

        end_event = mock.Mock(guild_id=123, reason=end_reason)

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(player, "remove") as patched_remove,
            mock.patch.object(player.app.event_manager, "dispatch") as patched_dispatch,
            mock.patch.object(player, "play") as patched_play,
            mock.patch(
                "ongaku.events.QueueEmptyEvent.from_session",
            ) as patched_queue_empty_event,
        ):
            await player._track_end_event(end_event)

        if end_reason in [
            track.TrackEndReasonType.FINISHED,
            track.TrackEndReasonType.LOADFAILED,
        ]:
            patched_remove.assert_called_once_with(0)
            patched_dispatch.assert_called_once_with(
                patched_queue_empty_event.return_value,
                return_tasks=False,
            )
            patched_play.assert_not_called()
            patched_queue_empty_event.assert_called_once_with(
                ongaku_session,
                guild_id=player.guild_id,
                old_track=player.queue[0],
            )
        else:
            patched_remove.assert_not_called()
            patched_dispatch.assert_not_called()
            patched_play.assert_not_called()
            patched_queue_empty_event.assert_not_called()

    @pytest.mark.asyncio
    async def test__track_end_event_with_loop(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        track_1 = mock.Mock()

        player._queue = [
            track_1,
        ]

        player._loop = True

        end_event = mock.Mock(guild_id=123, reason=track.TrackEndReasonType.FINISHED)

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(player, "remove") as patched_remove,
            mock.patch.object(player.app.event_manager, "dispatch") as patched_dispatch,
            mock.patch.object(player, "play") as patched_play,
            mock.patch(
                "ongaku.events.QueueNextEvent.from_session",
            ) as patched_queue_next_event,
        ):
            await player._track_end_event(end_event)

        patched_remove.assert_not_called()
        patched_dispatch.assert_called_once_with(
            patched_queue_next_event.return_value,
            return_tasks=False,
        )
        patched_play.assert_called_once_with()
        patched_queue_next_event.assert_called_once_with(
            ongaku_session,
            guild_id=player.guild_id,
            track=player.queue[0],
            old_track=end_event.track,
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "autoplay",
        [True, False],
    )
    async def test__track_end_event_with_autoplay(
        self,
        ongaku_session: session_.Session,
        autoplay: bool,
    ):
        player = Player(ongaku_session, 123)

        track_1 = mock.Mock()
        track_2 = mock.Mock()

        player._queue = [
            track_1,
            track_2,
        ]

        player._autoplay = autoplay

        end_event = mock.Mock(
            guild_id=123,
            reason=track.TrackEndReasonType.FINISHED,
            track=track_1,
        )

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(player, "remove") as patched_remove,
            mock.patch.object(player.app.event_manager, "dispatch") as patched_dispatch,
            mock.patch.object(player, "play") as patched_play,
            mock.patch(
                "ongaku.events.QueueNextEvent.from_session",
            ) as patched_queue_next_event,
        ):
            await player._track_end_event(end_event)

        if autoplay:
            patched_remove.assert_called_once_with(0)
            patched_dispatch.assert_called_once_with(
                patched_queue_next_event.return_value,
                return_tasks=False,
            )
            patched_play.assert_awaited_once_with()
            patched_queue_next_event.assert_called_once_with(
                ongaku_session,
                guild_id=player.guild_id,
                track=track_1,
                old_track=end_event.track,
            )
        else:
            patched_remove.assert_not_called()
            patched_dispatch.assert_not_called()
            patched_play.assert_not_called()
            patched_queue_next_event.assert_not_called()

    @pytest.mark.asyncio
    async def test__track_end_event_with_wrong_guild(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        end_event = mock.Mock(guild_id=456)

        with (
            mock.patch.object(ongaku_session, "_session_id", "session_id"),
            mock.patch.object(player, "remove") as patched_remove,
            mock.patch.object(player.app.event_manager, "dispatch") as patched_dispatch,
            mock.patch.object(player, "play") as patched_play,
        ):
            await player._track_end_event(end_event)

        patched_remove.assert_not_called()
        patched_dispatch.assert_not_called()
        patched_play.assert_not_called()

    @pytest.mark.asyncio
    async def test__track_end_event_with_missing_session_id(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        end_event = mock.Mock(guild_id=456)

        with pytest.raises(errors.SessionStartError):
            await player._track_end_event(end_event)

    @pytest.mark.asyncio
    async def test__player_update_event(self, ongaku_session: session_.Session):
        player = Player(ongaku_session, 123)

        update_event = mock.Mock(guild_id=123)

        await player._player_update_event(update_event)

        assert player.state == update_event.state

    @pytest.mark.asyncio
    async def test__player_update_event_with_wrong_guild(
        self,
        ongaku_session: session_.Session,
    ):
        player = Player(ongaku_session, 123)

        update_event = mock.Mock(guild_id=456)

        current_state = player.state

        await player._player_update_event(update_event)

        assert player.state == current_state
