from __future__ import annotations

import typing
from unittest import mock

import pytest
from hikari.snowflakes import Snowflake

from ongaku import Playlist
from ongaku import errors
from ongaku.abc.track import Track
from ongaku.impl import player as player
from ongaku.rest import RESTClient
from tests import payloads

if typing.TYPE_CHECKING:
    from ongaku.client import Client
    from ongaku.impl.filters import Filters
    from ongaku.session import Session


def test_properties(ongaku_client: Client):
    rest = RESTClient(ongaku_client)

    assert rest._client == ongaku_client


class TestRestTrack:
    @pytest.mark.asyncio
    async def test_load_track_with_custom_session(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={"loadType": "track", "data": payloads.TRACK_PAYLOAD},
            ) as patched_request,
        ):
            new_track = await rest.load_track(
                "https://youtube.com/watch?v=video",
                session=ongaku_session,
            )

            patched_fetch_session.assert_not_called()

            patched_request.assert_called_with(
                "GET",
                "/loadtracks",
                dict,
                params={"identifier": "https://youtube.com/watch?v=video"},
            )

            assert isinstance(new_track, Track)

            assert new_track.encoded == "encoded"

    @pytest.mark.asyncio
    async def test_load_track_as_track(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={"loadType": "track", "data": payloads.TRACK_PAYLOAD},
            ) as patched_request,
        ):
            new_track = await rest.load_track("https://youtube.com/watch?v=video")

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_once_with(
                "GET",
                "/loadtracks",
                dict,
                params={"identifier": "https://youtube.com/watch?v=video"},
            )

            assert isinstance(new_track, Track)

            assert new_track.encoded == "encoded"

    @pytest.mark.asyncio
    async def test_load_track_as_track_malformed(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={"loadType": "track", "data": {}},
            ) as patched_request,
            pytest.raises(errors.BuildError) as build_error,
        ):
            await rest.load_track("ytsearch:malformed-track")

        patched_fetch_session.assert_called_once()

        patched_request.assert_called_once_with(
            "GET",
            "/loadtracks",
            dict,
            params={"identifier": "ytsearch:malformed-track"},
        )

        assert isinstance(build_error.value, errors.BuildError)

    @pytest.mark.asyncio
    async def test_load_track_as_playlist(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={
                    "loadType": "playlist",
                    "data": payloads.PLAYLIST_PAYLOAD,
                },
            ) as patched_request,
        ):
            playlist = await rest.load_track(
                "https://www.youtube.com/watch?v=video&list=playlist",
            )

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_with(
                "GET",
                "/loadtracks",
                dict,
                params={
                    "identifier": "https://www.youtube.com/watch?v=video&list=playlist",
                },
            )

            assert isinstance(playlist, Playlist)

            assert playlist.info.name == "name"

    @pytest.mark.asyncio
    async def test_load_track_as_playlist_malformed(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={"loadType": "playlist", "data": {}},
            ) as patched_request,
            pytest.raises(errors.BuildError) as build_error,
        ):
            await rest.load_track("ytsearch:malformed-playlist")

        patched_fetch_session.assert_called_once()

        patched_request.assert_called_once_with(
            "GET",
            "/loadtracks",
            dict,
            params={"identifier": "ytsearch:malformed-playlist"},
        )

        assert isinstance(build_error.value, errors.BuildError)

    @pytest.mark.asyncio
    async def test_load_track_as_search(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={"loadType": "search", "data": [payloads.TRACK_PAYLOAD]},
            ) as patched_request,
        ):
            search = await rest.load_track("ytsearch:a-track")

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_with(
                "GET",
                "/loadtracks",
                dict,
                params={"identifier": "ytsearch:a-track"},
            )

            assert isinstance(search, typing.Sequence)

            assert len(search) == 1

    @pytest.mark.asyncio
    async def test_load_track_as_search_malformed(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={"loadType": "search", "data": [{}, {}, {}]},
            ) as patched_request,
            pytest.raises(errors.BuildError) as build_error,
        ):
            await rest.load_track("ytsearch:malformed-search")

        patched_fetch_session.assert_called_once()

        patched_request.assert_called_once_with(
            "GET",
            "/loadtracks",
            dict,
            params={"identifier": "ytsearch:malformed-search"},
        )

        assert isinstance(build_error.value, errors.BuildError)

    @pytest.mark.asyncio
    async def test_load_track_as_empty(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={"loadType": "empty", "data": {}},
            ) as patched_request,
        ):
            no_result = await rest.load_track("ytsearch:not-a-track")

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_with(
                "GET",
                "/loadtracks",
                dict,
                params={"identifier": "ytsearch:not-a-track"},
            )

            assert no_result is None

    @pytest.mark.asyncio
    async def test_load_track_as_exception(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={
                    "loadType": "error",
                    "data": payloads.EXCEPTION_ERROR_PAYLOAD,
                },
            ) as patched_request,
            pytest.raises(errors.RestExceptionError) as rest_exception_error,
        ):
            await rest.load_track("https://youtube.com/watch?v=a-broken-video")

        patched_fetch_session.assert_called_once()

        patched_request.assert_called_with(
            "GET",
            "/loadtracks",
            dict,
            params={"identifier": "https://youtube.com/watch?v=a-broken-video"},
        )

        assert isinstance(rest_exception_error.value, errors.RestExceptionError)

    @pytest.mark.asyncio
    async def test_decode_track_with_session(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.TRACK_PAYLOAD,
            ) as patched_request,
        ):
            new_track = await rest.decode_track("encoded", session=ongaku_session)

            patched_fetch_session.assert_not_called()

            patched_request.assert_called_once_with(
                "GET",
                "/decodetrack",
                dict,
                params={"encodedTrack": "encoded"},
            )

        assert isinstance(new_track, Track)

        assert new_track.encoded == "encoded"

    @pytest.mark.asyncio
    async def test_decode_track(self, ongaku_client: Client, ongaku_session: Session):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.TRACK_PAYLOAD,
            ) as patched_request,
        ):
            new_track = await rest.decode_track("encoded")

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_once_with(
                "GET",
                "/decodetrack",
                dict,
                params={"encodedTrack": "encoded"},
            )

        assert isinstance(new_track, Track)

        assert new_track.encoded == "encoded"

    @pytest.mark.asyncio
    async def test_decode_track_malformed(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
            pytest.raises(errors.BuildError),
        ):
            await rest.decode_track("encoded")

        patched_fetch_session.assert_called_once()

        patched_request.assert_called_once_with(
            "GET",
            "/decodetrack",
            dict,
            params={"encodedTrack": "encoded"},
        )

    @pytest.mark.asyncio
    async def test_decode_tracks_with_session(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=[payloads.TRACK_PAYLOAD],
            ) as patched_request,
        ):
            tracks = await rest.decode_tracks(["encoded"], session=ongaku_session)

            patched_fetch_session.assert_not_called()

            patched_request.assert_called_once_with(
                "POST",
                "/decodetracks",
                list,
                headers={"Content-Type": "application/json"},
                json=["encoded"],
            )

        assert isinstance(tracks, typing.Sequence)
        assert isinstance(tracks[0], Track)

        assert tracks[0].encoded == "encoded"

    @pytest.mark.asyncio
    async def test_decode_tracks(self, ongaku_client: Client, ongaku_session: Session):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=[payloads.TRACK_PAYLOAD],
            ) as patched_request,
        ):
            tracks = await rest.decode_tracks(["encoded"])

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_once_with(
                "POST",
                "/decodetracks",
                list,
                headers={"Content-Type": "application/json"},
                json=["encoded"],
            )

        assert isinstance(tracks, typing.Sequence)
        assert isinstance(tracks[0], Track)

        assert tracks[0].encoded == "encoded"

    @pytest.mark.asyncio
    async def test_decode_tracks_malformed(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=[{}],
            ) as patched_request,
            pytest.raises(errors.BuildError),
        ):
            await rest.decode_tracks(["encoded"])

        patched_fetch_session.assert_called_once()

        patched_request.assert_called_once_with(
            "POST",
            "/decodetracks",
            list,
            headers={"Content-Type": "application/json"},
            json=["encoded"],
        )


class TestRestPlayer:
    @pytest.mark.asyncio
    async def test_fetch_players_with_session(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=[payloads.PLAYER_PAYLOAD],
            ) as patched_request,
        ):
            await rest.fetch_players("session_id", session=ongaku_session)

            patched_fetch_session.assert_not_called()

            patched_request.assert_called_once_with(
                "GET",
                "/sessions/session_id/players",
                list,
            )

    @pytest.mark.asyncio
    async def test_fetch_players(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=[payloads.PLAYER_PAYLOAD],
            ) as patched_request,
        ):
            await rest.fetch_players("session_id")

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_once_with(
                "GET",
                "/sessions/session_id/players",
                list,
            )

    @pytest.mark.asyncio
    async def test_fetch_player_with_session(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.PLAYER_PAYLOAD,
            ) as patched_request,
        ):
            await rest.fetch_player(
                "session_id",
                Snowflake(1234567890),
                session=ongaku_session,
            )

            patched_fetch_session.assert_not_called()

            patched_request.assert_called_once_with(
                "GET",
                "/sessions/session_id/players/1234567890",
                dict,
            )

    @pytest.mark.asyncio
    async def test_fetch_player(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.PLAYER_PAYLOAD,
            ) as patched_request,
        ):
            await rest.fetch_player("session_id", Snowflake(1234567890))

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_once_with(
                "GET",
                "/sessions/session_id/players/1234567890",
                dict,
            )

    @pytest.mark.asyncio
    async def test_update_player_with_session(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.PLAYER_PAYLOAD,
            ) as patched_request,
        ):
            await rest.update_player(
                "session_id",
                Snowflake(1234567890),
                track=mock.Mock(
                    encoded="encoded",
                    user_data={},
                    requestor=Snowflake(1234),
                ),
                position=1,
                end_time=2,
                volume=3,
                paused=False,
                voice=player.Voice("token", "endpoint", "session_id"),
                no_replace=False,
                session=ongaku_session,
            )

            patched_fetch_session.assert_not_called()

            patched_request.assert_called_once_with(
                "PATCH",
                "/sessions/session_id/players/1234567890",
                dict,
                headers={"Content-Type": "application/json"},
                json={
                    "track": {
                        "encoded": "encoded",
                        "userData": {"ongaku_requestor": "1234"},
                    },
                    "position": 1,
                    "endTime": 2,
                    "volume": 3,
                    "paused": False,
                    "voice": {
                        "token": "token",
                        "endpoint": "endpoint",
                        "sessionId": "session_id",
                    },
                },
                params={"noReplace": "false"},
            )

    @pytest.mark.asyncio
    async def test_update_player(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
        ongaku_filters: Filters,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.PLAYER_PAYLOAD,
            ) as patched_request,
        ):
            await rest.update_player(
                "session_id",
                Snowflake(1234567890),
                track=mock.Mock(
                    encoded="encoded",
                    user_data={},
                    requestor=Snowflake(1234),
                ),
                position=1,
                end_time=2,
                volume=3,
                paused=False,
                filters=ongaku_filters,
                voice=player.Voice("token", "endpoint", "session_id"),
                no_replace=False,
            )

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_once_with(
                "PATCH",
                "/sessions/session_id/players/1234567890",
                dict,
                headers={"Content-Type": "application/json"},
                json={
                    "track": {
                        "encoded": "encoded",
                        "userData": {"ongaku_requestor": "1234"},
                    },
                    "position": 1,
                    "endTime": 2,
                    "volume": 3,
                    "paused": False,
                    "filters": payloads.FILTERS_PAYLOAD,
                    "voice": payloads.PLAYER_VOICE_PAYLOAD,
                },
                params={"noReplace": "false"},
            )

    @pytest.mark.asyncio
    async def test_delete_player_with_session(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=None,
            ) as patched_request,
        ):
            await rest.delete_player(
                "session_id",
                Snowflake(1234567890),
                session=ongaku_session,
            )

            patched_fetch_session.assert_not_called()

            patched_request.assert_called_once_with(
                "DELETE",
                "/sessions/session_id/players/1234567890",
                None,
            )

    @pytest.mark.asyncio
    async def test_delete_player(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=None,
            ) as patched_request,
        ):
            await rest.delete_player("session_id", Snowflake(1234567890))

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_once_with(
                "DELETE",
                "/sessions/session_id/players/1234567890",
                None,
            )


class TestRestSession:
    @pytest.mark.asyncio
    async def test_update_session_with_session(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.SESSION_PAYLOAD,
            ) as patched_request,
        ):
            await rest.update_session(
                "session_id",
                resuming=False,
                timeout=230,
                session=ongaku_session,
            )

            patched_fetch_session.assert_not_called()

            patched_request.assert_called_once_with(
                "PATCH",
                "/sessions/session_id",
                dict,
                headers={"Content-Type": "application/json"},
                json={"resuming": False, "timeout": 230},
            )

    @pytest.mark.asyncio
    async def test_update_session(self, ongaku_client: Client, ongaku_session: Session):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.SESSION_PAYLOAD,
            ) as patched_request,
        ):
            await rest.update_session("session_id", resuming=False, timeout=230)

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_once_with(
                "PATCH",
                "/sessions/session_id",
                dict,
                headers={"Content-Type": "application/json"},
                json={"resuming": False, "timeout": 230},
            )


class TestRestInformation:
    @pytest.mark.asyncio
    async def test_fetch_info_with_session(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.INFO_PAYLOAD,
            ) as patched_request,
        ):
            await rest.fetch_info(session=ongaku_session)

            patched_fetch_session.assert_not_called()

            patched_request.assert_called_once_with(
                "GET",
                "/info",
                dict,
            )

    @pytest.mark.asyncio
    async def test_fetch_info(self, ongaku_client: Client, ongaku_session: Session):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.INFO_PAYLOAD,
            ) as patched_request,
        ):
            await rest.fetch_info()

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_once_with(
                "GET",
                "/info",
                dict,
            )

    @pytest.mark.asyncio
    async def test_fetch_version_with_session(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.INFO_PAYLOAD,
            ) as patched_request,
        ):
            await rest.fetch_version(session=ongaku_session)

            patched_fetch_session.assert_not_called()

            patched_request.assert_called_once_with(
                "GET",
                "/version",
                str,
                version=False,
            )

    @pytest.mark.asyncio
    async def test_fetch_version(self, ongaku_client: Client, ongaku_session: Session):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.INFO_PAYLOAD,
            ) as patched_request,
        ):
            await rest.fetch_version()

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_once_with(
                "GET",
                "/version",
                str,
                version=False,
            )

    @pytest.mark.asyncio
    async def test_fetch_stats_with_session(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.STATISTICS_PAYLOAD,
            ) as patched_request,
        ):
            await rest.fetch_stats(session=ongaku_session)

            patched_fetch_session.assert_not_called()

            patched_request.assert_called_once_with(
                "GET",
                "/stats",
                dict,
            )

    @pytest.mark.asyncio
    async def test_fetch_stats(self, ongaku_client: Client, ongaku_session: Session):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.STATISTICS_PAYLOAD,
            ) as patched_request,
        ):
            await rest.fetch_stats()

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_once_with(
                "GET",
                "/stats",
                dict,
            )


class TestRestRoutePlanner:
    @pytest.mark.asyncio
    async def test_fetch_routeplanner_status_with_session(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.ROUTEPLANNER_STATUS_PAYLOAD,
            ) as patched_request,
        ):
            assert (
                await rest.fetch_routeplanner_status(session=ongaku_session) is not None
            )

            patched_fetch_session.assert_not_called()

            patched_request.assert_called_once_with(
                "GET",
                "/routeplanner/status",
                dict,
            )

    @pytest.mark.asyncio
    async def test_fetch_routeplanner_status(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.ROUTEPLANNER_STATUS_PAYLOAD,
            ) as patched_request,
        ):
            assert await rest.fetch_routeplanner_status() is not None

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_once_with(
                "GET",
                "/routeplanner/status",
                dict,
            )

    @pytest.mark.asyncio
    async def test_fetch_routeplanner_status_empty(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                side_effect=errors.RestEmptyError,
            ) as patched_request,
        ):
            assert await rest.fetch_routeplanner_status() is None

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_once_with(
                "GET",
                "/routeplanner/status",
                dict,
            )

    @pytest.mark.asyncio
    async def test_update_routeplanner_address_with_session(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        # Test with payload
        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.ROUTEPLANNER_STATUS_PAYLOAD,
            ) as patched_request,
        ):
            await rest.update_routeplanner_address("1.0.0.1", session=ongaku_session)

            patched_fetch_session.assert_not_called()

            patched_request.assert_called_once_with(
                "POST",
                "/routeplanner/free/address",
                None,
                json={"address": "1.0.0.1"},
            )

    @pytest.mark.asyncio
    async def test_update_routeplanner_address(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        # Test with payload
        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payloads.ROUTEPLANNER_STATUS_PAYLOAD,
            ) as patched_request,
        ):
            await rest.update_routeplanner_address("1.0.0.1")

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_once_with(
                "POST",
                "/routeplanner/free/address",
                None,
                json={"address": "1.0.0.1"},
            )

    @pytest.mark.asyncio
    async def test_update_all_routeplanner_address_with_session(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=None,
            ) as patched_request,
        ):
            await rest.update_all_routeplanner_addresses(session=ongaku_session)

            patched_fetch_session.assert_not_called()

            patched_request.assert_called_once_with(
                "POST",
                "/routeplanner/free/all",
                None,
            )

        await ongaku_client._stop_event(mock.Mock())

    @pytest.mark.asyncio
    async def test_update_all_routeplanner_address(
        self,
        ongaku_client: Client,
        ongaku_session: Session,
    ):
        rest = RESTClient(ongaku_client)

        with (
            mock.patch.object(rest._client, "_session_handler"),
            mock.patch.object(
                rest._client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ) as patched_fetch_session,
            mock.patch.object(
                ongaku_session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=None,
            ) as patched_request,
        ):
            await rest.update_all_routeplanner_addresses()

            patched_fetch_session.assert_called_once()

            patched_request.assert_called_once_with(
                "POST",
                "/routeplanner/free/all",
                None,
            )
