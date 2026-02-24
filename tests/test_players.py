from __future__ import annotations

import datetime
import typing
from unittest import mock

import pytest
from hikari.events.voice_events import VoiceServerUpdateEvent
from hikari.events.voice_events import VoiceStateUpdateEvent
from hikari.snowflakes import Snowflake

from ongaku import errors
from ongaku import events
from ongaku.abc.events import TrackEndReasonType
from ongaku.impl import player as player_
from ongaku.impl import playlist
from ongaku.impl.player import Voice
from ongaku.impl.track import Track
from ongaku.impl.track import TrackInfo
from ongaku.player import Player
from ongaku.session import Session

if typing.TYPE_CHECKING:
    from hikari import Event
    from hikari.impl import gateway_bot as gateway_bot_

    from ongaku.abc.filters import Filters
    from ongaku.client import Client


async def connect_events(
    event_type: type[Event],
    /,
    timeout: float | None,
):
    if event_type == VoiceServerUpdateEvent:
        return VoiceServerUpdateEvent(
            app=mock.Mock(),
            shard=mock.Mock(),
            guild_id=Snowflake(1234567890),
            token="token",
            raw_endpoint="raw_endpoint",
        )

    if event_type == VoiceStateUpdateEvent:
        return VoiceStateUpdateEvent(
            shard=mock.Mock(),
            old_state=mock.Mock(),
            state=mock.Mock(
                session_id="session_id",
            ),
        )

    raise Exception("Invalid event requested.")


class TestPlayer:
    @pytest.mark.asyncio
    async def test_properties(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_session: Session,
    ):
        new_player = Player(ongaku_session, 1234567890)

        assert new_player.session == ongaku_session

        assert new_player.app == gateway_bot

        assert new_player.guild_id == Snowflake(1234567890)

        assert new_player.channel_id is None

        assert new_player.is_alive is False

        assert new_player.position == 0

        assert new_player.volume == -1

        assert new_player.is_paused is True

        assert new_player.autoplay is True

        assert new_player.connected is False

        assert isinstance(new_player.queue, typing.Sequence)
        assert new_player.queue == []

        assert new_player.voice is None

        assert new_player.state is None

        assert new_player.filters is None

    @pytest.mark.asyncio
    async def test_connect(self, ongaku_session: Session):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        # Test Working

        voice = Voice("token", "raw_endpoint", "session_id")

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                ongaku_session.client.app,
                "update_voice_state",
                new_callable=mock.AsyncMock,
            ) as patched_voice_state,
            mock.patch.object(new_player.app.event_manager, "wait_for", connect_events),
            mock.patch(
                "ongaku.rest.RESTClient.update_player",
                new_callable=mock.AsyncMock,
                return_value=player_.Player(
                    Snowflake(1234567890),
                    None,
                    1,
                    False,
                    mock.Mock(),
                    voice,
                    mock.Mock(),
                ),
            ) as patched_update,
        ):
            await new_player.connect(987654321)

            patched_voice_state.assert_called_once_with(
                Snowflake(1234567890),
                Snowflake(987654321),
                self_mute=False,
                self_deaf=True,
            )

            patched_update.assert_called_once_with(
                ongaku_session._get_session_id(),
                Snowflake(1234567890),
                voice=voice,
                no_replace=False,
                session=ongaku_session,
            )

            assert new_player.voice is not None

            assert new_player.voice.endpoint == voice.endpoint
            assert new_player.voice.token == voice.token
            assert new_player.voice.session_id == voice.session_id

            assert new_player.is_alive is True

        # Events were received, but raw endpoint was empty.

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                ongaku_session.client.app,
                "update_voice_state",
                new_callable=mock.AsyncMock,
            ) as patched_voice_state,
            mock.patch.object(
                new_player.app.event_manager,
                "wait_for",
                new_callable=mock.AsyncMock,
                return_value=mock.Mock(raw_endpoint=None),
            ),
            pytest.raises(errors.PlayerConnectError),
        ):
            await new_player.connect(987654321)

    @pytest.mark.asyncio
    async def test_disconnect(self, ongaku_session: Session):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                ongaku_session.client.app,
                "update_voice_state",
                new_callable=mock.AsyncMock,
            ) as patched_voice_state,
            mock.patch.object(new_player.app.event_manager, "wait_for", connect_events),
            mock.patch(
                "ongaku.rest.RESTClient.update_player",
            ) as patched_update,
            mock.patch(
                "ongaku.rest.RESTClient.delete_player",
            ) as patched_delete,
            mock.patch("ongaku.player.Player.clear") as patched_clear,
        ):
            await new_player.connect(987654321)

            patched_voice_state.assert_called_once_with(
                Snowflake(1234567890),
                Snowflake(987654321),
                self_mute=False,
                self_deaf=True,
            )

            patched_update.assert_called_once_with(
                ongaku_session._get_session_id(),
                Snowflake(1234567890),
                voice=Voice("token", "raw_endpoint", "session_id"),
                no_replace=False,
                session=ongaku_session,
            )

            await new_player.disconnect()

            patched_clear.assert_called_once()

            patched_delete.assert_called_once_with(
                ongaku_session._get_session_id(),
                Snowflake(1234567890),
                session=ongaku_session,
            )

            assert new_player.is_alive is False

            patched_voice_state.assert_called_with(Snowflake(1234567890), None)

    @pytest.mark.asyncio
    async def test_play(self, ongaku_session: Session, ongaku_track: Track):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        # Test working

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                new_player,
                "_channel_id",
                new_callable=mock.PropertyMock(return_value=Snowflake(987654321)),
            ),
            mock.patch(
                "ongaku.rest.RESTClient.update_player",
                return_value=player_.Player(
                    Snowflake(1234567890),
                    ongaku_track,
                    3,
                    False,
                    mock.Mock(),
                    mock.Mock(),
                    mock.Mock(),
                ),
            ) as patched_update,
        ):
            await new_player.play(ongaku_track, Snowflake(123454321))

            patched_update.assert_called_once_with(
                ongaku_session._get_session_id(),
                Snowflake(1234567890),
                track=ongaku_track,
                no_replace=False,
                session=ongaku_session,
            )

            assert new_player.is_paused is False

            assert len(new_player.queue) == 1

            assert new_player.queue[0].requestor == Snowflake(123454321)

        # No session_id

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                side_effect=errors.SessionStartError,
            ),
            pytest.raises(errors.SessionStartError),
        ):
            await new_player.play(ongaku_track, 123454321)

        # No channel.

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            pytest.raises(errors.PlayerConnectError),
        ):
            await new_player.play(ongaku_track, 123454321)

        # No track in queue.

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                new_player,
                "_channel_id",
                new_callable=mock.PropertyMock(return_value=Snowflake(987654321)),
            ),
            pytest.raises(errors.PlayerQueueError),
        ):
            new_player.remove(0)

            await new_player.play()

    @pytest.mark.asyncio
    async def test_add(
        self,
        ongaku_session: Session,
        ongaku_track: Track,
        ongaku_track_info: TrackInfo,
    ):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        # Add singular track

        assert len(new_player.queue) == 0

        new_player.add(
            Track("encoded_1", ongaku_track_info, {}, {}, None),
            Snowflake(1),
        )

        assert len(new_player.queue) == 1

        # Add two tracks.

        tracks: list[Track] = [
            Track("encoded_2", ongaku_track_info, {}, {}, None),
            Track("encoded_3", ongaku_track_info, {}, {}, None),
        ]

        new_player.add(tracks, Snowflake(22))

        assert len(new_player.queue) == 3

        # Add a playlist
        info = playlist.PlaylistInfo("beans", -1)
        playlist_tracks: list[Track] = [
            Track("encoded_4", ongaku_track_info, {}, {}, None),
            Track("encoded_5", ongaku_track_info, {}, {}, None),
        ]
        new_playlist = playlist.Playlist(info, playlist_tracks, {})

        new_player.add(new_playlist, Snowflake(333))

        assert len(new_player.queue) == 5

        # Check correct requestor got set, and make sure none is supported.

        new_player.add(ongaku_track)

        assert len(new_player.queue) == 6
        assert new_player.queue[0].requestor == Snowflake(1)
        assert new_player.queue[1].requestor == Snowflake(22)
        assert new_player.queue[2].requestor == Snowflake(22)
        assert new_player.queue[3].requestor == Snowflake(333)
        assert new_player.queue[4].requestor == Snowflake(333)
        assert new_player.queue[5].requestor is None

    @pytest.mark.asyncio
    async def test_pause(self, ongaku_session: Session, ongaku_track: Track):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                new_player,
                "_channel_id",
                return_value=Snowflake(987654321),
            ),
            mock.patch(
                "ongaku.rest.RESTClient.update_player",
                return_value=player_.Player(
                    Snowflake(1234567890),
                    ongaku_track,
                    3,
                    False,
                    mock.Mock(),
                    mock.Mock(),
                    mock.Mock(),
                ),
            ) as patched_update,
        ):
            await new_player.pause(True)

            patched_update.assert_called_once_with(
                ongaku_session._get_session_id(),
                Snowflake(1234567890),
                paused=True,
                session=ongaku_session,
            )

    @pytest.mark.asyncio
    async def test_stop(self, ongaku_session: Session):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                new_player,
                "_channel_id",
                return_value=Snowflake(987654321),
            ),
            mock.patch(
                "ongaku.rest.RESTClient.update_player",
                return_value=player_.Player(
                    Snowflake(1234567890),
                    None,
                    3,
                    False,
                    mock.Mock(),
                    mock.Mock(),
                    mock.Mock(),
                ),
            ) as patched_update,
        ):
            await new_player.stop()

            patched_update.assert_called_once_with(
                ongaku_session._get_session_id(),
                Snowflake(1234567890),
                track=None,
                no_replace=False,
                session=ongaku_session,
            )

    @pytest.mark.asyncio
    async def test_shuffle(self, ongaku_session: Session, ongaku_track: Track):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        tracks: list[Track] = [  # So many tracks are placed here, to ensure
            mock.Mock(encoded="test_track_1"),
            mock.Mock(encoded="test_track_2"),
            mock.Mock(encoded="test_track_3"),
            mock.Mock(encoded="test_track_4"),
            mock.Mock(encoded="test_track_5"),
            mock.Mock(encoded="test_track_6"),
            mock.Mock(encoded="test_track_7"),
            mock.Mock(encoded="test_track_8"),
            mock.Mock(encoded="test_track_9"),
        ]

        new_player.add(tracks)

        assert new_player.queue == tracks

        new_player.shuffle()

        assert new_player.queue[0].encoded == tracks[0].encoded
        assert new_player.queue != tracks

        # Queue has 1 track

        new_player._queue = []

        new_player.add(ongaku_track)

        with pytest.raises(errors.PlayerQueueError):
            new_player.shuffle()

        # Queue has 2 tracks

        new_player._queue = []

        new_player.add([mock.Mock(), mock.Mock()])

        with pytest.raises(errors.PlayerQueueError):
            new_player.shuffle()

    @pytest.mark.asyncio
    async def test_skip(self, ongaku_session: Session):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                new_player,
                "_channel_id",
                return_value=Snowflake(987654321),
            ),
            mock.patch(
                "ongaku.rest.RESTClient.update_player",
                return_value=player_.Player(
                    Snowflake(1234567890),
                    None,
                    3,
                    False,
                    mock.Mock(),
                    mock.Mock(),
                    mock.Mock(),
                ),
            ) as patched_update,
        ):
            tracks: list[Track] = [
                mock.Mock(encoded="test_track_1"),
                mock.Mock(encoded="test_track_2"),
            ]

            new_player.add(tracks)

            # Skip to new song.

            await new_player.skip()

            patched_update.assert_called_with(
                ongaku_session._get_session_id(),
                Snowflake(1234567890),
                track=tracks[1],
                no_replace=False,
                session=ongaku_session,
            )

            assert len(new_player.queue) == 1

            # Skip to no song.

            await new_player.skip()

            patched_update.assert_called_with(
                ongaku_session._get_session_id(),
                Snowflake(1234567890),
                track=None,
                no_replace=False,
                session=ongaku_session,
            )

            assert len(new_player.queue) == 0

    @pytest.mark.asyncio
    async def test_remove(self, ongaku_session: Session, ongaku_track: Track):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        tracks: list[Track] = [
            mock.Mock(encoded="test_encoded_1"),
            mock.Mock(encoded="test_encoded_2"),
            ongaku_track,
            mock.Mock(encoded="test_encoded_3"),
        ]

        new_player.add(tracks)

        assert len(new_player.queue) == 4

        # Remove particular track

        new_player.remove(ongaku_track)

        assert len(new_player.queue) == 3
        assert new_player.queue == [tracks[0], tracks[1], tracks[3]]

        # Remove track based on position

        new_player.remove(1)

        assert len(new_player.queue) == 2
        assert new_player.queue == [tracks[0], tracks[3]]

        # Test empty queue

        new_player._queue = []

        with pytest.raises(errors.PlayerQueueError):
            new_player.remove(0)

        tracks.pop(2)

        new_player.add(tracks)

        with pytest.raises(errors.PlayerQueueError):
            new_player.remove(300)

        with pytest.raises(errors.PlayerQueueError):
            new_player.remove(ongaku_track)

    @pytest.mark.asyncio
    async def test_clear(self, ongaku_session: Session, ongaku_track: Track):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                new_player,
                "_channel_id",
                return_value=Snowflake(987654321),
            ),
            mock.patch(
                "ongaku.rest.RESTClient.update_player",
                return_value=player_.Player(
                    Snowflake(1234567890),
                    None,
                    3,
                    False,
                    mock.Mock(),
                    mock.Mock(),
                    mock.Mock(),
                ),
            ) as patched_update,
        ):
            tracks: list[Track] = [ongaku_track, mock.Mock(encoded="test_track_2")]

            new_player.add(tracks)

            assert len(new_player.queue) == 2

            await new_player.clear()

            patched_update.assert_called_once_with(
                ongaku_session._get_session_id(),
                Snowflake(1234567890),
                track=None,
                no_replace=False,
                session=ongaku_session,
            )

            assert len(new_player.queue) == 0

    @pytest.mark.asyncio
    async def test_set_autoplay(self, ongaku_session: Session):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        assert new_player.autoplay is True

        new_player.set_autoplay()

        assert new_player.autoplay is False

        new_player.set_autoplay(True)

        assert new_player.autoplay is True

        new_player.set_autoplay(False)

        assert new_player.autoplay is False

    @pytest.mark.asyncio
    async def test_set_volume(self, ongaku_session: Session):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch(
                "ongaku.rest.RESTClient.update_player",
                return_value=player_.Player(
                    Snowflake(1234567890),
                    None,
                    3,
                    False,
                    mock.Mock(),
                    mock.Mock(),
                    mock.Mock(),
                ),
            ) as patched_update,
        ):
            # set volume to a value

            await new_player.set_volume(250)

            patched_update.assert_called_with(
                ongaku_session._get_session_id(),
                Snowflake(1234567890),
                volume=250,
                no_replace=False,
                session=ongaku_session,
            )

            # Reset volume

            await new_player.set_volume()

            patched_update.assert_called_with(
                ongaku_session._get_session_id(),
                Snowflake(1234567890),
                volume=100,
                no_replace=False,
                session=ongaku_session,
            )

        # Give negative number

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            pytest.raises(ValueError),
        ):
            await new_player.set_volume(-100)

        # Give a number greater than 1000

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            pytest.raises(ValueError),
        ):
            await new_player.set_volume(9001)

    @pytest.mark.asyncio
    async def test_set_position(self, ongaku_session: Session, ongaku_track: Track):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch(
                "ongaku.rest.RESTClient.update_player",
                return_value=player_.Player(
                    Snowflake(1234567890),
                    None,
                    3,
                    False,
                    mock.Mock(),
                    mock.Mock(),
                    mock.Mock(),
                ),
            ) as patched_update,
        ):
            new_player.add(ongaku_track)

            assert len(new_player.queue) == 1

            await new_player.set_position(10)

            patched_update.assert_called_once_with(
                ongaku_session._get_session_id(),
                Snowflake(1234567890),
                position=10,
                no_replace=False,
                session=ongaku_session,
            )

        # Negative number provided

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            pytest.raises(ValueError),
        ):
            await new_player.set_position(-10)

        # Queue is empty

        new_player._queue = []

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            pytest.raises(errors.PlayerQueueError),
        ):
            await new_player.set_position(10)

        # Queue is empty

        new_player.add(ongaku_track)

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            pytest.raises(ValueError),
        ):
            await new_player.set_position(1000000000000000000000000)

    @pytest.mark.asyncio
    async def test_set_loop(self, ongaku_session: Session):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        assert new_player.loop is False

        new_player.set_loop()

        assert new_player.loop is True

        new_player.set_loop(True)

        assert new_player.loop is True

        new_player.set_loop(False)

        assert new_player.loop is False

    @pytest.mark.asyncio
    async def test_transfer(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        new_session = Session(
            ongaku_client,
            "session",
            False,
            "127.0.0.1",
            2333,
            "youshallnotpass",
            3,
        )

        # Test not connected

        tracks: list[Track] = [
            ongaku_track,
            mock.Mock(encoded="encoded_1"),
            mock.Mock(encoded="encoded_2"),
            mock.Mock(encoded="encoded_3"),
        ]

        new_player.add(tracks)

        new_player = await new_player.transfer(new_session)

        assert new_player.queue == new_player.queue

        # Test connected.

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch(
                "ongaku.session.Session._get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                new_session.client.app,
                "update_voice_state",
                new_callable=mock.AsyncMock,
            ),
            mock.patch.object(
                new_session.app.event_manager,
                "wait_for",
                connect_events,
            ),
            mock.patch(
                "ongaku.rest.RESTClient.update_player",
            ) as patched_update,
            mock.patch.object(
                new_player,
                "_connected",
                new_callable=mock.PropertyMock(return_value=True),
            ),
            mock.patch.object(
                new_player,
                "_is_paused",
                new_callable=mock.PropertyMock(return_value=False),
            ),
            mock.patch.object(
                new_player,
                "_position",
                new_callable=mock.PropertyMock(return_value=30),
            ),
            mock.patch.object(
                new_player,
                "_channel_id",
                return_value=Snowflake(987654321),
            ),
            mock.patch("ongaku.player.Player.disconnect") as patch_disconnect,
        ):
            new_player = await new_player.transfer(new_session)

            patch_disconnect.assert_called_once()

            # Check .connect() method of the new player was called.
            patched_update.assert_any_call(
                ongaku_session._get_session_id(),
                Snowflake(1234567890),
                voice=Voice("token", "raw_endpoint", "session_id"),
                no_replace=False,
                session=new_session,
            )

            # Check .play() method of the new player was called.
            patched_update.assert_any_call(
                ongaku_session._get_session_id(),
                Snowflake(1234567890),
                track=tracks[0],
                no_replace=False,
                session=new_session,
            )

            # Check .set_position() method of the new player was called.
            patched_update.assert_any_call(
                ongaku_session._get_session_id(),
                Snowflake(1234567890),
                position=30,
                no_replace=False,
                session=new_session,
            )

    @pytest.mark.asyncio
    async def test_update(self, ongaku_session: Session, ongaku_filters: Filters):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        assert new_player.volume == -1
        assert new_player.is_paused is True
        assert new_player.state is None
        assert new_player.voice is None
        assert new_player.filters is None
        assert new_player.connected is False

        state = player_.State(datetime.datetime.now(), 1, True, 2)
        voice = player_.Voice("token", "endpoint", "session_id")
        replacement_player = player_.Player(
            Snowflake(1234567890),
            None,
            10,
            False,
            state,
            voice,
            ongaku_filters,
        )

        new_player._update(replacement_player)

        assert new_player.volume == 10
        assert new_player.is_paused is False
        assert new_player.state == state
        assert new_player.voice == voice
        assert new_player.filters == ongaku_filters
        assert new_player.connected is True

    @pytest.mark.asyncio
    async def test_player_update_event(self, ongaku_session: Session):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        assert new_player.state is None
        assert new_player.connected is False

        state = player_.State(datetime.datetime.now(), 1, True, 2)
        event = events.PlayerUpdateEvent.from_session(
            ongaku_session,
            Snowflake(1234567890),
            state,
        )

        await new_player._player_update_event(event)

        assert new_player.state == state
        assert new_player.connected is True


class TestPlayerTrackEndEvent:
    @pytest.mark.asyncio
    async def test_autoplay(self, ongaku_session: Session):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        event = events.TrackEndEvent.from_session(
            ongaku_session,
            Snowflake(1234567890),
            track=mock.Mock(encoded="encoded"),
            reason=TrackEndReasonType.FINISHED,
        )

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                ongaku_session.client.app.event_manager,
                "dispatch",
                new_callable=mock.AsyncMock,
            ) as patched_dispatch,
        ):
            new_player.set_autoplay(False)

            await new_player._track_end_event(event)

            patched_dispatch.assert_not_called()

    @pytest.mark.asyncio
    async def test_loop_with_multiple_tracks(
        self,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        new_player.set_loop(True)

        new_player.add([ongaku_track, mock.Mock(encoded="track")])

        event = events.TrackEndEvent.from_session(
            ongaku_session,
            Snowflake(1234567890),
            track=ongaku_track,
            reason=TrackEndReasonType.FINISHED,
        )

        assert len(new_player.queue) == 2

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch("ongaku.player.Player.play") as patched_play,
            mock.patch.object(
                ongaku_session.client.app.event_manager,
                "dispatch",
                new_callable=mock.AsyncMock,
            ) as patched_dispatch,
        ):
            await new_player._track_end_event(event)

            assert len(new_player.queue) == 2

            patched_dispatch.assert_called_once()

            patched_play.assert_called_once()

    @pytest.mark.asyncio
    async def test_loop_with_singular_track(
        self,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        new_player.set_loop(True)

        new_player.add(ongaku_track)

        event = events.TrackEndEvent.from_session(
            ongaku_session,
            Snowflake(1234567890),
            track=ongaku_track,
            reason=TrackEndReasonType.FINISHED,
        )

        assert len(new_player.queue) == 1

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch("ongaku.player.Player.play") as patched_play,
            mock.patch.object(
                ongaku_session.client.app.event_manager,
                "dispatch",
                new_callable=mock.AsyncMock,
            ) as patched_dispatch,
        ):
            await new_player._track_end_event(event)

            assert len(new_player.queue) == 1

            patched_dispatch.assert_called_once()

            patched_play.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_track_end_types(self, ongaku_session: Session):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        invalid_events = [
            events.TrackEndEvent.from_session(
                ongaku_session,
                Snowflake(1234567890),
                track=mock.Mock(encoded="encoded"),
                reason=TrackEndReasonType.STOPPED,
            ),
            events.TrackEndEvent.from_session(
                ongaku_session,
                Snowflake(1234567890),
                track=mock.Mock(encoded="encoded"),
                reason=TrackEndReasonType.CLEANUP,
            ),
            events.TrackEndEvent.from_session(
                ongaku_session,
                Snowflake(1234567890),
                track=mock.Mock(encoded="encoded"),
                reason=TrackEndReasonType.REPLACED,
            ),
        ]

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                ongaku_session.client.app.event_manager,
                "dispatch",
                new_callable=mock.AsyncMock,
            ) as patched_dispatch,
        ):
            for event in invalid_events:
                await new_player._track_end_event(event)

            patched_dispatch.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_guild_id(self, ongaku_session: Session):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        event = events.TrackEndEvent.from_session(
            ongaku_session,
            Snowflake(1),
            track=mock.Mock(encoded="encoded"),
            reason=TrackEndReasonType.FINISHED,
        )

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                ongaku_session.client.app.event_manager,
                "dispatch",
                new_callable=mock.AsyncMock,
            ) as patched_dispatch,
        ):
            await new_player._track_end_event(event)

            patched_dispatch.assert_not_called()

    @pytest.mark.asyncio
    async def test_empty_queue(self, ongaku_session: Session):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        event = events.TrackEndEvent.from_session(
            ongaku_session,
            Snowflake(1234567890),
            track=mock.Mock(encoded="encoded"),
            reason=TrackEndReasonType.FINISHED,
        )

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                ongaku_session.client.app.event_manager,
                "dispatch",
                new_callable=mock.AsyncMock,
            ) as patched_dispatch,
        ):
            await new_player._track_end_event(event)

            patched_dispatch.assert_not_called()

    @pytest.mark.asyncio
    async def test_finished_singular(
        self,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        event = events.TrackEndEvent.from_session(
            ongaku_session,
            Snowflake(1234567890),
            track=mock.Mock(encoded="encoded"),
            reason=TrackEndReasonType.FINISHED,
        )

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                ongaku_session.client.app.event_manager,
                "dispatch",
                new_callable=mock.AsyncMock,
            ) as patched_dispatch,
        ):
            assert len(new_player.queue) == 0

            new_player.add(ongaku_track)

            assert len(new_player.queue) == 1
            assert new_player.queue[0] == ongaku_track

            await new_player._track_end_event(event)

            patched_dispatch.assert_called_once()

            assert len(new_player.queue) == 0

    @pytest.mark.asyncio
    async def test_finished_multiple(self, ongaku_session: Session):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        event = events.TrackEndEvent.from_session(
            ongaku_session,
            Snowflake(1234567890),
            track=mock.Mock(encoded="encoded"),
            reason=TrackEndReasonType.FINISHED,
        )

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                ongaku_session.client.app.event_manager,
                "dispatch",
                new_callable=mock.AsyncMock,
            ) as patched_dispatch,
            mock.patch(
                "ongaku.player.Player.play",
                new_callable=mock.AsyncMock,
            ) as patched_play,
        ):
            assert len(new_player.queue) == 0

            tracks: list[Track] = [
                mock.Mock(encoded="encoded_1"),
                mock.Mock(encoded="encoded_2"),
            ]

            new_player.add(tracks)

            assert len(new_player.queue) == 2

            await new_player._track_end_event(event)

            patched_dispatch.assert_called_once()

            patched_play.assert_called_once()

            assert len(new_player.queue) == 1

            assert new_player.queue[0].encoded == "encoded_2"

    @pytest.mark.asyncio
    async def test_load_failed_singular(
        self,
        ongaku_session: Session,
        ongaku_track: Track,
    ):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        event = events.TrackEndEvent.from_session(
            ongaku_session,
            Snowflake(1234567890),
            track=mock.Mock(encoded="encoded"),
            reason=TrackEndReasonType.LOADFAILED,
        )

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                ongaku_session.client.app.event_manager,
                "dispatch",
                new_callable=mock.AsyncMock,
            ) as patched_dispatch,
        ):
            assert len(new_player.queue) == 0

            new_player.add(ongaku_track)

            assert len(new_player.queue) == 1
            assert new_player.queue[0] == ongaku_track

            await new_player._track_end_event(event)

            patched_dispatch.assert_called_once()

            assert len(new_player.queue) == 0

    @pytest.mark.asyncio
    async def test_load_failed_multiple(self, ongaku_session: Session):
        new_player = Player(ongaku_session, Snowflake(1234567890))

        event = events.TrackEndEvent.from_session(
            ongaku_session,
            Snowflake(1234567890),
            track=mock.Mock(encoded="encoded"),
            reason=TrackEndReasonType.LOADFAILED,
        )

        with (
            mock.patch.object(
                ongaku_session,
                "_get_session_id",
                return_value="session_id",
            ),
            mock.patch.object(
                ongaku_session.client.app.event_manager,
                "dispatch",
                new_callable=mock.AsyncMock,
            ) as patched_dispatch,
            mock.patch(
                "ongaku.player.Player.play",
                new_callable=mock.AsyncMock,
            ) as patched_play,
        ):
            assert len(new_player.queue) == 0

            tracks: list[Track] = [
                mock.Mock(encoded="encoded_1"),
                mock.Mock(encoded="encoded_2"),
            ]

            new_player.add(tracks)

            assert len(new_player.queue) == 2

            await new_player._track_end_event(event)

            patched_dispatch.assert_called_once()

            patched_play.assert_called_once()

            assert len(new_player.queue) == 1

            assert new_player.queue[0].encoded == "encoded_2"
