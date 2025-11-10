from __future__ import annotations

import re
import typing
from unittest import mock

import hikari
import pytest

from ongaku import errors as errors_
from ongaku import player as player_
from ongaku import session as session_
from ongaku import track as track_
from ongaku.api import builders as builders_
from ongaku.api.rest import RESTClient
from ongaku.client import Client
from ongaku.internal import routes


@pytest.fixture
def rest_client(ongaku_client: Client) -> RESTClient:
    return RESTClient(ongaku_client)


class TestRESTClient:
    def test_properties(self):
        client = mock.Mock()

        rest_client = RESTClient(client)

        assert rest_client._client == client

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("load_type", "expected_function"),
        [
            ("track", "deserialize_track"),
            ("playlist", "deserialize_playlist"),
        ],
    )
    async def test_load_track(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
        load_type: str,
        expected_function: str,
    ):
        route = routes.GET_LOAD_TRACKS.build()

        payload: dict[str, typing.Any] = {"loadType": load_type, "data": {}}

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payload,
            ) as patched_request,
            mock.patch(
                f"ongaku.api.builders.EntityBuilder.{expected_function}",
            ) as patched_expected_function,
        ):
            assert (
                await rest_client.load_track("yt:hilltop hoods")
                == patched_expected_function.return_value
            )

        patched_request.assert_awaited_once_with(
            route,
            params={"identifier": "yt:hilltop hoods"},
        )

        patched_get_session.assert_called_once_with()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("load_type", "expected_function"),
        [
            ("track", "deserialize_track"),
            ("playlist", "deserialize_playlist"),
        ],
    )
    async def test_load_track_with_session(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
        ongaku_session: session_.Session,
        load_type: str,
        expected_function: str,
    ):
        route = routes.GET_LOAD_TRACKS.build()

        payload: dict[str, typing.Any] = {"loadType": load_type, "data": {}}

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                session_.Session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payload,
            ) as patched_request,
            mock.patch(
                f"ongaku.api.builders.EntityBuilder.{expected_function}",
            ) as patched_expected_function,
        ):
            assert (
                await rest_client.load_track(
                    "yt:hilltop hoods",
                    session=ongaku_session,
                )
                == patched_expected_function.return_value
            )

        patched_request.assert_awaited_once_with(
            route,
            params={"identifier": "yt:hilltop hoods"},
        )

        patched_get_session.assert_not_called()

    @pytest.mark.asyncio
    async def test_load_track_with_invalid_response(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value=["bad", "data"],
            ),
            pytest.raises(
                errors_.BuildTypeError,
                match=rf"({typing.Mapping}, {list})",
            ),
        ):
            await rest_client.load_track("yt:hilltop hoods")

    @pytest.mark.asyncio
    async def test_load_track_with_empty(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        route = routes.GET_LOAD_TRACKS.build()

        payload: dict[str, typing.Any] = {
            "loadType": "empty",
            "data": {},
        }

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payload,
            ) as patched_request,
        ):
            assert await rest_client.load_track("yt:hilltop hoods") is None

        patched_request.assert_awaited_once_with(
            route,
            params={"identifier": "yt:hilltop hoods"},
        )

    @pytest.mark.asyncio
    async def test_load_track_with_error(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        route = routes.GET_LOAD_TRACKS.build()

        payload = {
            "loadType": "error",
            "data": {
                "message": "message",
                "severity": "common",
                "cause": "cause",
            },
        }

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payload,
            ) as patched_request,
            pytest.raises(errors_.ExceptionError),
        ):
            await rest_client.load_track("yt:hilltop hoods")

        patched_request.assert_awaited_once_with(
            route,
            params={"identifier": "yt:hilltop hoods"},
        )

    @pytest.mark.asyncio
    async def test_load_track_unknown_load_type(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        payload: dict[str, typing.Any] = {
            "loadType": "beans",
            "data": {},
        }

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value=payload,
            ),
            pytest.raises(errors_.BuildUnknownVariantError, match=re.escape("beans")),
        ):
            await rest_client.load_track("yt:hilltop hoods")

    @pytest.mark.asyncio
    async def test_decode_track(self, rest_client: RESTClient, ongaku_client: Client):
        route = routes.GET_DECODE_TRACK.build()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_track",
            ) as patched_deserialize_track,
        ):
            assert (
                await rest_client.decode_track("abc123")
                == patched_deserialize_track.return_value
            )

        patched_request.assert_awaited_once_with(
            route,
            params={"encodedTrack": "abc123"},
        )

        patched_get_session.assert_called_once_with()

        patched_deserialize_track.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_decode_track_with_session(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
        ongaku_session: session_.Session,
    ):
        route = routes.GET_DECODE_TRACK.build()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                session_.Session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_track",
            ) as patched_deserialize_track,
        ):
            assert (
                await rest_client.decode_track("abc123", session=ongaku_session)
                == patched_deserialize_track.return_value
            )

        patched_request.assert_awaited_once_with(
            route,
            params={"encodedTrack": "abc123"},
        )

        patched_get_session.assert_not_called()

        patched_deserialize_track.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_decode_track_with_invalid_response(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value=["bad", "data"],
            ),
            pytest.raises(
                errors_.BuildTypeError,
                match=rf"({typing.Mapping}, {list})",
            ),
        ):
            await rest_client.decode_track("abc123")

    @pytest.mark.asyncio
    async def test_decode_tracks(self, rest_client: RESTClient, ongaku_client: Client):
        route = routes.POST_DECODE_TRACKS.build()

        track_1 = mock.Mock()
        track_2 = mock.Mock()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value=[track_1, track_2],
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_track",
            ) as patched_deserialize_track,
        ):
            await rest_client.decode_tracks(["abc", "123"])

        patched_request.assert_awaited_once_with(
            route,
            headers={"Content-Type": "application/json"},
            body=["abc", "123"],
        )

        patched_get_session.assert_called_once_with()

        patched_deserialize_track.assert_has_calls(
            [
                mock.call(track_1),
                mock.call(track_2),
            ],
        )

    @pytest.mark.asyncio
    async def test_decode_tracks_with_session(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
        ongaku_session: session_.Session,
    ):
        route = routes.POST_DECODE_TRACKS.build()

        track_1 = mock.Mock()
        track_2 = mock.Mock()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                session_.Session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=[track_1, track_2],
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_track",
            ) as patched_deserialize_track,
        ):
            await rest_client.decode_tracks(["abc", "123"], session=ongaku_session)

        patched_request.assert_awaited_once_with(
            route,
            headers={"Content-Type": "application/json"},
            body=["abc", "123"],
        )

        patched_get_session.assert_not_called()

        patched_deserialize_track.assert_has_calls(
            [
                mock.call(track_1),
                mock.call(track_2),
            ],
        )

    @pytest.mark.asyncio
    async def test_decode_tracks_with_invalid_response(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value={"bad": "data"},
            ),
            pytest.raises(
                errors_.BuildTypeError,
                match=rf"({typing.Sequence}, {dict})",
            ),
        ):
            await rest_client.decode_tracks(["abc", "123"])

    @pytest.mark.asyncio
    async def test_fetch_player(self, rest_client: RESTClient, ongaku_client: Client):
        route = routes.GET_PLAYER.build(session_id="session_id", guild_id=123)

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_player",
            ) as patched_deserialize_player,
        ):
            assert (
                await rest_client.fetch_player("session_id", 123)
                == patched_deserialize_player.return_value
            )

        patched_request.assert_awaited_once_with(route)

        patched_get_session.assert_called_once_with()

        patched_deserialize_player.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_fetch_player_with_session(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
        ongaku_session: session_.Session,
    ):
        route = routes.GET_PLAYER.build(session_id="session_id", guild_id=123)

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                session_.Session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_player",
            ) as patched_deserialize_player,
        ):
            assert (
                await rest_client.fetch_player(
                    "session_id",
                    123,
                    session=ongaku_session,
                )
                == patched_deserialize_player.return_value
            )

        patched_request.assert_awaited_once_with(route)

        patched_get_session.assert_not_called()

        patched_deserialize_player.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_fetch_player_with_invalid_response(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value=["bad", "data"],
            ),
            pytest.raises(
                errors_.BuildTypeError,
                match=rf"({typing.Mapping}, {list})",
            ),
        ):
            await rest_client.fetch_player("session_id", 123)

    @pytest.mark.asyncio
    async def test_fetch_players(self, rest_client: RESTClient, ongaku_client: Client):
        route = routes.GET_PLAYERS.build(session_id="session_id")

        player_1 = mock.Mock()
        player_2 = mock.Mock()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value=[player_1, player_2],
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_player",
            ) as patched_deserialize_player,
        ):
            await rest_client.fetch_players("session_id")

        patched_request.assert_awaited_once_with(
            route,
        )

        patched_get_session.assert_called_once_with()

        patched_deserialize_player.assert_has_calls(
            [
                mock.call(player_1),
                mock.call(player_2),
            ],
        )

    @pytest.mark.asyncio
    async def test_fetch_players_with_session(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
        ongaku_session: session_.Session,
    ):
        route = routes.GET_PLAYERS.build(session_id="session_id")

        player_1 = mock.Mock()
        player_2 = mock.Mock()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                session_.Session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=[player_1, player_2],
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_player",
            ) as patched_deserialize_player,
        ):
            await rest_client.fetch_players("session_id", session=ongaku_session)

        patched_request.assert_awaited_once_with(route)

        patched_get_session.assert_not_called()

        patched_deserialize_player.assert_has_calls(
            [
                mock.call(player_1),
                mock.call(player_2),
            ],
        )

    @pytest.mark.asyncio
    async def test_fetch_players_with_invalid_response(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value={"bad": "data"},
            ),
            pytest.raises(
                errors_.BuildTypeError,
                match=rf"({typing.Mapping}, {dict})",
            ),
        ):
            await rest_client.fetch_players("session_id")

    @pytest.mark.asyncio
    async def test_update_player(self, rest_client: RESTClient, ongaku_client: Client):
        route = routes.PATCH_PLAYER_UPDATE.build(
            session_id="session_id",
            guild_id=123,
        )

        track = track_.Track(
            encoded="encoded",
            info=mock.Mock(),
            plugin_info={},
            user_data={},
            requestor=hikari.Snowflake(456),
        )

        filters = builders_.FiltersBuilder(
            volume=2.9,
            karaoke=builders_.KaraokeBuilder(
                level=1,
                mono_level=2.3,
                filter_band=4,
                filter_width=5.6,
            ),
        )

        voice = player_.Voice(
            token="token",
            endpoint="endpoint",
            session_id="session_id",
        )

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_player",
            ) as patched_deserialize_player,
        ):
            await rest_client.update_player(
                "session_id",
                123,
                track=track,
                position=1,
                end_time=2,
                volume=3,
                paused=False,
                filters=filters,
                voice=voice,
                no_replace=True,
            )

        patched__builder.serialize_voice.assert_called_once_with(voice)
        patched_request.assert_awaited_once_with(
            route,
            headers={"Content-Type": "application/json"},
            body={
                "track": {
                    "encoded": "encoded",
                    "userData": {"ongaku_requestor": "456"},
                },
                "position": 1,
                "endTime": 2,
                "volume": 3,
                "paused": False,
                "filters": filters.build(),
                "voice": patched__builder.serialize_voice.return_value,
            },
            params={"noReplace": "true"},
        )

        patched_deserialize_player.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_update_player_with_session(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
        ongaku_session: session_.Session,
    ):
        route = routes.PATCH_PLAYER_UPDATE.build(
            session_id="session_id",
            guild_id=123,
        )

        track = track_.Track(
            encoded="encoded",
            info=mock.Mock(),
            plugin_info={},
            user_data={},
            requestor=hikari.Snowflake(456),
        )

        filters = builders_.FiltersBuilder(
            volume=2.9,
            karaoke=builders_.KaraokeBuilder(
                level=1,
                mono_level=2.3,
                filter_band=4,
                filter_width=5.6,
            ),
        )

        voice = player_.Voice(
            token="token",
            endpoint="endpoint",
            session_id="session_id",
        )

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                session_.Session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_player",
            ) as patched_deserialize_player,
        ):
            await rest_client.update_player(
                "session_id",
                123,
                track=track,
                position=1,
                end_time=2,
                volume=3,
                paused=False,
                filters=filters,
                voice=voice,
                no_replace=True,
                session=ongaku_session,
            )

        patched__builder.serialize_voice.assert_called_once_with(voice)
        patched_request.assert_awaited_once_with(
            route,
            headers={"Content-Type": "application/json"},
            body={
                "track": {
                    "encoded": "encoded",
                    "userData": {"ongaku_requestor": "456"},
                },
                "position": 1,
                "endTime": 2,
                "volume": 3,
                "paused": False,
                "filters": filters.build(),
                "voice": patched__builder.serialize_voice.return_value,
            },
            params={"noReplace": "true"},
        )

        patched_get_session.assert_not_called()

        patched_deserialize_player.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_update_player_with_invalid_response(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value=["bad", "data"],
            ),
            pytest.raises(
                errors_.BuildTypeError,
                match=rf"({typing.Mapping}, {list})",
            ),
        ):
            await rest_client.update_player(
                "session_id",
                123,
                position=1,
            )

    @pytest.mark.asyncio
    async def test_update_player_with_all_undefined(
        self,
        rest_client: RESTClient,
    ):
        with pytest.raises(
            ValueError,
            match=r"^$",
        ):
            await rest_client.update_player("session_id", 123)

    @pytest.mark.asyncio
    async def test_delete_player(self, rest_client: RESTClient, ongaku_client: Client):
        route = routes.DELETE_PLAYER.build(session_id="session_id", guild_id=123)

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value=None,
            ) as patched_request,
        ):
            await rest_client.delete_player("session_id", 123)

        patched_request.assert_awaited_once_with(route)

        patched_get_session.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_delete_player_with_session(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
        ongaku_session: session_.Session,
    ):
        route = routes.DELETE_PLAYER.build(session_id="session_id", guild_id=123)

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                session_.Session,
                "request",
                new_callable=mock.AsyncMock,
                return_value=None,
            ) as patched_request,
        ):
            await rest_client.delete_player(
                "session_id",
                123,
                session=ongaku_session,
            )

        patched_request.assert_awaited_once_with(route)

        patched_get_session.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_session(self, rest_client: RESTClient, ongaku_client: Client):
        route = routes.PATCH_SESSION_UPDATE.build(session_id="session_id")

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_session",
            ) as patched_deserialize_session,
        ):
            await rest_client.update_session("session_id", resuming=False, timeout=1)

        patched_request.assert_awaited_once_with(
            route,
            headers={"Content-Type": "application/json"},
            body={
                "resuming": False,
                "timeout": 1,
            },
        )

        patched_deserialize_session.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_update_session_with_session(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        route = routes.PATCH_SESSION_UPDATE.build(session_id="session_id")

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_session",
            ) as patched_deserialize_session,
        ):
            await rest_client.update_session("session_id", resuming=False, timeout=1)

        patched_request.assert_awaited_once_with(
            route,
            headers={"Content-Type": "application/json"},
            body={
                "resuming": False,
                "timeout": 1,
            },
        )

        patched_deserialize_session.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_update_session_with_invalid_response(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value=[],
            ),
            pytest.raises(
                errors_.BuildTypeError,
                match=rf"({typing.Mapping}, {list})",
            ),
        ):
            await rest_client.update_session("session_id", resuming=False, timeout=1)

    @pytest.mark.asyncio
    async def test_fetch_info(self, rest_client: RESTClient, ongaku_client: Client):
        route = routes.GET_INFO.build()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_information",
            ) as patched_deserialize_information,
        ):
            assert (
                await rest_client.fetch_info()
                == patched_deserialize_information.return_value
            )

        patched_request.assert_awaited_once_with(route)

        patched_get_session.assert_called_once_with()

        patched_deserialize_information.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_fetch_info_with_session(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
        ongaku_session: session_.Session,
    ):
        route = routes.GET_INFO.build()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                session_.Session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_information",
            ) as patched_deserialize_information,
        ):
            assert (
                await rest_client.fetch_info(session=ongaku_session)
                == patched_deserialize_information.return_value
            )

        patched_request.assert_awaited_once_with(route)

        patched_get_session.assert_not_called()

        patched_deserialize_information.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_fetch_info_with_invalid_response(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        route = routes.GET_INFO.build()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value=[],
            ) as patched_request,
            pytest.raises(
                errors_.BuildTypeError,
                match=rf"({typing.Mapping}, {list})",
            ),
        ):
            await rest_client.fetch_info()

        patched_get_session.assert_called_once_with()

        patched_request.assert_awaited_once_with(route)

    @pytest.mark.asyncio
    async def test_fetch_version(self, rest_client: RESTClient, ongaku_client: Client):
        route = routes.GET_VERSION.build()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value="1.2.3",
            ) as patched_request,
        ):
            assert await rest_client.fetch_version() == "1.2.3"

        patched_get_session.assert_called_once_with()

        patched_request.assert_awaited_once_with(route)

    @pytest.mark.asyncio
    async def test_fetch_version_with_session(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
        ongaku_session: session_.Session,
    ):
        route = routes.GET_VERSION.build()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                session_.Session,
                "request",
                new_callable=mock.AsyncMock,
                return_value="1.2.3",
            ) as patched_request,
        ):
            assert await rest_client.fetch_version(session=ongaku_session) == "1.2.3"

        patched_get_session.assert_not_called()

        patched_request.assert_awaited_once_with(route)

    @pytest.mark.asyncio
    async def test_fetch_version_with_invalid_response(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ),
            pytest.raises(
                errors_.BuildTypeError,
                match=rf"({str}, {dict})",
            ),
        ):
            await rest_client.fetch_version()

    @pytest.mark.asyncio
    async def test_fetch_statistics(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        route = routes.GET_STATISTICS.build()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_statistics",
            ) as patched_deserialize_statistics,
        ):
            assert (
                await rest_client.fetch_statistics()
                == patched_deserialize_statistics.return_value
            )

        patched_request.assert_awaited_once_with(route)

        patched_get_session.assert_called_once_with()

        patched_deserialize_statistics.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_fetch_statistics_with_session(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
        ongaku_session: session_.Session,
    ):
        route = routes.GET_STATISTICS.build()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                session_.Session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_statistics",
            ) as patched_deserialize_statistics,
        ):
            assert (
                await rest_client.fetch_statistics(
                    session=ongaku_session,
                )
                == patched_deserialize_statistics.return_value
            )

        patched_request.assert_awaited_once_with(route)

        patched_get_session.assert_not_called()

        patched_deserialize_statistics.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_fetch_statistics_with_invalid_response(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value=["bad", "data"],
            ),
            pytest.raises(
                errors_.BuildTypeError,
                match=rf"({typing.Mapping}, {list})",
            ),
        ):
            await rest_client.fetch_statistics()

    @pytest.mark.asyncio
    async def test_fetch_routeplanner_status(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        route = routes.GET_ROUTEPLANNER_STATUS.build()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_routeplanner_status",
            ) as patched_deserialize_routeplanner_status,
        ):
            assert (
                await rest_client.fetch_routeplanner_status()
                == patched_deserialize_routeplanner_status.return_value
            )

        patched_request.assert_awaited_once_with(route)

        patched_get_session.assert_called_once_with()

        patched_deserialize_routeplanner_status.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_fetch_routeplanner_status_with_session(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
        ongaku_session: session_.Session,
    ):
        route = routes.GET_ROUTEPLANNER_STATUS.build()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                session_.Session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
            mock.patch.object(Client, "_builder") as patched__builder,
            mock.patch.object(
                patched__builder,
                "deserialize_routeplanner_status",
            ) as patched_deserialize_routeplanner_status,
        ):
            assert (
                await rest_client.fetch_routeplanner_status(
                    session=ongaku_session,
                )
                == patched_deserialize_routeplanner_status.return_value
            )

        patched_request.assert_awaited_once_with(route)

        patched_get_session.assert_not_called()

        patched_deserialize_routeplanner_status.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_fetch_routeplanner_status_with_invalid_response(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value=["bad", "data"],
            ),
            pytest.raises(
                errors_.BuildTypeError,
                match=rf"({typing.Mapping}, {list})",
            ),
        ):
            await rest_client.fetch_routeplanner_status()

    @pytest.mark.asyncio
    async def test_update_routeplanner_address(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        route = routes.POST_ROUTEPLANNER_FREE_ADDRESS.build()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
        ):
            await rest_client.update_routeplanner_address("1.2.3.4")

        patched_get_session.assert_called_once_with()

        patched_request.assert_awaited_once_with(
            route,
            body={"address": "1.2.3.4"},
        )

    @pytest.mark.asyncio
    async def test_update_routeplanner_address_with_session(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
        ongaku_session: session_.Session,
    ):
        route = routes.POST_ROUTEPLANNER_FREE_ADDRESS.build()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                session_.Session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
        ):
            await rest_client.update_routeplanner_address(
                "1.2.3.4",
                session=ongaku_session,
            )
        patched_get_session.assert_not_called()

        patched_request.assert_awaited_once_with(
            route,
            body={"address": "1.2.3.4"},
        )

    @pytest.mark.asyncio
    async def test_all_update_routeplanner_addresses(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
    ):
        route = routes.POST_ROUTEPLANNER_FREE_ALL.build()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                patched_get_session.return_value,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
        ):
            await rest_client.update_all_routeplanner_addresses()

        patched_get_session.assert_called_once_with()

        patched_request.assert_awaited_once_with(route)

    @pytest.mark.asyncio
    async def test_all_update_routeplanner_addresses_with_session(
        self,
        rest_client: RESTClient,
        ongaku_client: Client,
        ongaku_session: session_.Session,
    ):
        route = routes.POST_ROUTEPLANNER_FREE_ALL.build()

        with (
            mock.patch.object(ongaku_client, "_handler") as patched__handler,
            mock.patch.object(patched__handler, "get_session") as patched_get_session,
            mock.patch.object(
                session_.Session,
                "request",
                new_callable=mock.AsyncMock,
                return_value={},
            ) as patched_request,
        ):
            await rest_client.update_all_routeplanner_addresses(session=ongaku_session)
        patched_get_session.assert_not_called()

        patched_request.assert_awaited_once_with(
            route,
        )
