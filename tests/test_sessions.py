from __future__ import annotations

import asyncio
import datetime
import typing
from unittest import mock

import aiohttp
import orjson
import pytest
from aiohttp import web
from hikari.snowflakes import Snowflake

import ongaku
from ongaku import errors
from ongaku import events
from ongaku.abc.session import SessionStatus
from ongaku.client import Client
from ongaku.player import Player
from ongaku.session import Session
from tests import payloads

if typing.TYPE_CHECKING:
    from hikari import OwnUser
    from hikari.impl import gateway_bot as gateway_bot_


class TestSession:
    def test_properties(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_name",
            False,
            "127.0.0.1",
            2333,
            "youshallnotpass",
            3,
        )

        assert session.client == ongaku_client

        assert session.app == ongaku_client.app

        assert session.name == "test_name"

        assert session.ssl is False

        assert session.host == "127.0.0.1"

        assert session.port == 2333

        assert session.password == "youshallnotpass"

        if session.ssl:
            assert session.base_uri == f"https://{session.host}:{session.port}"
        else:
            assert session.base_uri == f"http://{session.host}:{session.port}"

        assert session.auth_headers == {"Authorization": session.password}

        assert session.status == SessionStatus.NOT_CONNECTED

    @pytest.mark.asyncio
    async def test_get_session_id(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        with mock.patch(
            "ongaku.session.Session._session_id",
            new_callable=mock.PropertyMock,
            return_value="session_id",
        ):
            session_id = session._get_session_id()

            assert session_id == "session_id"

        with pytest.raises(errors.SessionStartError):
            session_id = session._get_session_id()

    @pytest.mark.asyncio
    async def test_transfer(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        handler = mock.Mock()

        player_1 = Player(session, Snowflake(1234567891))
        player_2 = Player(session, Snowflake(1234567890))

        new_session = Session(
            ongaku_client,
            "test_session_1",
            False,
            "127.0.0.1",
            2333,
            "youshallnotpass",
            3,
        )

        session._players = {
            player_1.guild_id: player_1,
            player_2.guild_id: player_2,
        }

        handler.players = tuple(session._players.values())

        with (
            mock.patch.object(handler, "fetch_session", return_value=new_session),
            mock.patch(
                "ongaku.player.Player.transfer",
            ) as patched_player_transfer,
        ):
            await session.transfer(handler)

            patched_player_transfer.assert_called_with(handler.fetch_session())

            assert patched_player_transfer.call_count == 2

            assert len(handler.players) == 2

            assert handler.players[0].guild_id == player_1.guild_id
            assert handler.players[1].guild_id == player_2.guild_id

    @staticmethod
    async def handler(request: web.Request):
        assert request.url.path == "/v4/websocket"

        assert request.headers.get("User-Id", None) == "1234567890"
        assert (
            request.headers.get("Client-Name", None)
            == f"test_username/{ongaku.__version__}"
        )
        assert request.headers.get("Authorization", None) == "password"

        ws = web.WebSocketResponse()
        await ws.prepare(request)
        await ws.send_str(orjson.dumps(payloads.READY_PAYLOAD).decode())

        await asyncio.sleep(2)

        await ws.close()

        return ws

    @pytest.mark.asyncio
    async def test_websocket(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        bot_user: OwnUser,
        aiohttp_client: typing.Any,
    ):
        ongaku_client = Client(gateway_bot)

        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        app = web.Application()
        app.router.add_route("GET", "/v4/websocket", self.handler)

        client = await aiohttp_client(app)

        with (
            mock.patch.object(gateway_bot, "get_me", return_value=bot_user),
            mock.patch("ongaku.client.Client._get_client_session", return_value=client),
            mock.patch.object(
                session,
                "_base_uri",
                new_callable=mock.PropertyMock(return_value=""),
            ),
            mock.patch.object(
                gateway_bot.event_manager,
                "dispatch",
                new_callable=mock.AsyncMock,
                return_value=None,
            ) as patched_dispatch,
            mock.patch("ongaku.session.Session.transfer") as patched_transfer,
        ):
            await session._websocket()

            assert len(patched_dispatch.call_args_list) == 2

            first_event_args = patched_dispatch.call_args_list[0].args

            assert len(first_event_args) == 1

            assert isinstance(first_event_args[0], events.PayloadEvent)

            first_event_args = patched_dispatch.call_args_list[1].args

            assert len(first_event_args) == 1

            assert isinstance(first_event_args[0], events.ReadyEvent)

            patched_transfer.assert_called_once_with(ongaku_client.session_handler)

    @pytest.mark.asyncio
    async def test_start(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        with mock.patch(
            "ongaku.session.Session._websocket",
            new_callable=mock.AsyncMock,
        ) as patched_websocket:
            await session.start()

            patched_websocket.assert_called_once()

            assert session._session_task is not None

    @pytest.mark.asyncio
    async def test_stop(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        with mock.patch(
            "ongaku.session.Session._websocket",
            new_callable=mock.AsyncMock,
        ) as patched_websocket:
            await session.start()

            patched_websocket.assert_called_once()

            assert session._session_task is not None

            await session.stop()

            assert session._session_task is None


class TestRequest:
    @pytest.mark.asyncio
    async def test_string(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        cs = aiohttp.ClientSession()

        with (
            mock.patch.object(session.client, "_client_session", cs),
            mock.patch.object(
                cs,
                "request",
                new_callable=mock.AsyncMock,
                return_value=mock.AsyncMock(
                    status=200,
                    text=mock.AsyncMock(return_value="text"),
                ),
            ) as patched_request,
        ):
            response = await session.request("GET", "/string", str)

            patched_request.assert_called_once_with(
                "GET",
                session.base_uri + "/v4/string",
                headers=session.auth_headers,
                json={},
                params={},
            )

            assert response == "text"

        await cs.close()

    @pytest.mark.asyncio
    async def test_integer(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        cs = aiohttp.ClientSession()

        with (
            mock.patch.object(session.client, "_client_session", cs),
            mock.patch.object(
                cs,
                "request",
                new_callable=mock.AsyncMock,
                return_value=mock.AsyncMock(
                    status=200,
                    text=mock.AsyncMock(return_value=1234567890),
                ),
            ) as patched_request,
        ):
            response = await session.request("GET", "/integer", int)

            patched_request.assert_called_once_with(
                "GET",
                session.base_uri + "/v4/integer",
                headers=session.auth_headers,
                json={},
                params={},
            )

            assert isinstance(response, int)
            assert response == 1234567890

        await cs.close()

    @pytest.mark.asyncio
    async def test_float(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        cs = aiohttp.ClientSession()

        with (
            mock.patch.object(session.client, "_client_session", cs),
            mock.patch.object(
                cs,
                "request",
                new_callable=mock.AsyncMock,
                return_value=mock.AsyncMock(
                    status=200,
                    text=mock.AsyncMock(return_value=4.2),
                ),
            ) as patched_request,
        ):
            response = await session.request("GET", "/float", float)

            patched_request.assert_called_once_with(
                "GET",
                session.base_uri + "/v4/float",
                headers=session.auth_headers,
                json={},
                params={},
            )

            assert isinstance(response, float)
            assert response == 4.2

        await cs.close()

    @pytest.mark.asyncio
    async def test_boolean(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        cs = aiohttp.ClientSession()

        with (
            mock.patch.object(session.client, "_client_session", cs),
            mock.patch.object(
                cs,
                "request",
                new_callable=mock.AsyncMock,
                return_value=mock.AsyncMock(
                    status=200,
                    text=mock.AsyncMock(return_value=True),
                ),
            ) as patched_request,
        ):
            response = await session.request("GET", "/boolean", bool)

            patched_request.assert_called_once_with(
                "GET",
                session.base_uri + "/v4/boolean",
                headers=session.auth_headers,
                json={},
                params={},
            )

            assert isinstance(response, bool)
            assert response is True

        await cs.close()

    @pytest.mark.asyncio
    async def test_dict(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        cs = aiohttp.ClientSession()

        return_dict = {"beanos": "Very cool."}

        with (
            mock.patch.object(session.client, "_client_session", cs),
            mock.patch.object(
                cs,
                "request",
                new_callable=mock.AsyncMock,
                return_value=mock.AsyncMock(
                    status=200,
                    text=mock.AsyncMock(
                        return_value=orjson.dumps(return_dict).decode(),
                    ),
                ),
            ) as patched_request,
        ):
            response = await session.request("GET", "/dict", dict)

            patched_request.assert_called_once_with(
                "GET",
                session.base_uri + "/v4/dict",
                headers=session.auth_headers,
                json={},
                params={},
            )

            assert isinstance(response, dict)
            assert response == return_dict

        await cs.close()

    @pytest.mark.asyncio
    async def test_list(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        cs = aiohttp.ClientSession()

        return_list = ["beanos", "are", "very", "cool"]

        with (
            mock.patch.object(session.client, "_client_session", cs),
            mock.patch.object(
                cs,
                "request",
                new_callable=mock.AsyncMock,
                return_value=mock.AsyncMock(
                    status=200,
                    text=mock.AsyncMock(
                        return_value=orjson.dumps(return_list).decode(),
                    ),
                ),
            ) as patched_request,
        ):
            response = await session.request("GET", "/list", list)

            patched_request.assert_called_once_with(
                "GET",
                session.base_uri + "/v4/list",
                headers=session.auth_headers,
                json={},
                params={},
            )

            assert isinstance(response, list)
            assert response == return_list

        await cs.close()

    @pytest.mark.asyncio
    async def test_tuple(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        cs = aiohttp.ClientSession()

        return_tuple = ("beanos", "are", "very", "cool")

        with (
            mock.patch.object(session.client, "_client_session", cs),
            mock.patch.object(
                cs,
                "request",
                new_callable=mock.AsyncMock,
                return_value=mock.AsyncMock(
                    status=200,
                    text=mock.AsyncMock(
                        return_value=orjson.dumps(return_tuple).decode(),
                    ),
                ),
            ) as patched_request,
        ):
            response = await session.request("GET", "/tuple", tuple)

            patched_request.assert_called_once_with(
                "GET",
                session.base_uri + "/v4/tuple",
                headers=session.auth_headers,
                json={},
                params={},
            )

            assert isinstance(response, tuple)
            assert response == return_tuple

        await cs.close()

    @pytest.mark.asyncio
    async def test_none(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        cs = aiohttp.ClientSession()

        with (
            mock.patch.object(session.client, "_client_session", cs),
            mock.patch.object(
                cs,
                "request",
                new_callable=mock.AsyncMock,
                return_value=mock.AsyncMock(
                    status=204,
                    text=mock.AsyncMock(return_value=""),
                ),
            ) as patched_request,
        ):
            response = await session.request("GET", "/none", None)

            patched_request.assert_called_once_with(
                "GET",
                session.base_uri + "/v4/none",
                headers=session.auth_headers,
                json={},
                params={},
            )

            assert response is None

        await cs.close()

    @pytest.mark.asyncio
    async def test_extra_args(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        cs = aiohttp.ClientSession()

        test_dict = {"fruit": "banana"}

        with (
            mock.patch.object(session.client, "_client_session", cs),
            mock.patch.object(
                cs,
                "request",
                new_callable=mock.AsyncMock,
                return_value=mock.AsyncMock(
                    status=204,
                    text=mock.AsyncMock(return_value=""),
                ),
            ) as patched_request,
        ):
            # Test extra headers

            response = await session.request("GET", "/headers", None, headers=test_dict)

            headers = dict(test_dict)

            headers.update(session.auth_headers)

            patched_request.assert_called_with(
                "GET",
                session.base_uri + "/v4/headers",
                headers=headers,
                json={},
                params={},
            )

            assert response is None

            # Test json payload.

            response = await session.request("GET", "/json", None, json=test_dict)

            patched_request.assert_called_with(
                "GET",
                session.base_uri + "/v4/json",
                headers=session.auth_headers,
                json=test_dict,
                params={},
            )

            assert response is None

            # Test extra params

            response = await session.request("GET", "/params", None, params=test_dict)

            params = dict(test_dict)

            params.update({})

            patched_request.assert_called_with(
                "GET",
                session.base_uri + "/v4/params",
                headers=session.auth_headers,
                json={},
                params=params,
            )

            assert response is None

        await cs.close()

    @pytest.mark.asyncio
    async def test_errors(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        cs = aiohttp.ClientSession()

        # Return type is a value, but received 204.

        with (
            mock.patch.object(session.client, "_client_session", cs),
            mock.patch.object(
                cs,
                "request",
                new_callable=mock.AsyncMock,
                return_value=mock.AsyncMock(
                    status=204,
                    text=mock.AsyncMock(return_value=""),
                ),
            ),
            pytest.raises(errors.RestEmptyError),
        ):
            await session.request("GET", "/none", str)

        # Response status is 400, and no text.

        with (
            mock.patch.object(session.client, "_client_session", cs),
            mock.patch.object(
                cs,
                "request",
                new_callable=mock.AsyncMock,
                return_value=mock.AsyncMock(
                    status=400,
                    reason="reason",
                    text=mock.AsyncMock(return_value=""),
                ),
            ),
            pytest.raises(errors.RestStatusError) as rest_status_error_1,
        ):
            await session.request("GET", "/none", str)

        assert isinstance(rest_status_error_1.value, errors.RestStatusError)

        assert rest_status_error_1.value.status == 400
        assert rest_status_error_1.value.reason == "reason"

        # Response status is 400, body included, but not a rest error payload.

        with (
            mock.patch.object(session.client, "_client_session", cs),
            mock.patch.object(
                cs,
                "request",
                new_callable=mock.AsyncMock,
                return_value=mock.AsyncMock(
                    status=400,
                    reason="reason",
                    text=mock.AsyncMock(return_value="not a rest error payload"),
                ),
            ),
            pytest.raises(errors.RestStatusError) as rest_status_error_2,
        ):
            await session.request("GET", "/none", str)

        assert isinstance(rest_status_error_2.value, errors.RestStatusError)

        assert rest_status_error_2.value.status == 400
        assert rest_status_error_2.value.reason == "reason"

        # Response status is 400, body included, and is a rest error.

        with (
            mock.patch.object(session.client, "_client_session", cs),
            mock.patch.object(
                cs,
                "request",
                new_callable=mock.AsyncMock,
                return_value=mock.AsyncMock(
                    status=400,
                    reason="reason",
                    text=mock.AsyncMock(
                        return_value=orjson.dumps(payloads.REST_ERROR_PAYLOAD).decode(),
                    ),
                ),
            ),
            pytest.raises(errors.RestRequestError) as rest_error_error,
        ):
            await session.request("GET", "/none", str)

        assert isinstance(rest_error_error.value, errors.RestRequestError)

        assert rest_error_error.value.timestamp == datetime.datetime.fromtimestamp(
            1 / 1000,
            datetime.timezone.utc,
        )
        assert rest_error_error.value.status == 2
        assert rest_error_error.value.error == "error"
        assert rest_error_error.value.message == "message"
        assert rest_error_error.value.path == "path"
        assert rest_error_error.value.trace == "trace"

        # Response was ok, however a malformed json document was received.

        with (
            mock.patch.object(session.client, "_client_session", cs),
            mock.patch.object(
                cs,
                "request",
                new_callable=mock.AsyncMock,
                return_value=mock.AsyncMock(
                    status=200,
                    text=mock.AsyncMock("I am malformed."),
                ),
            ),
            pytest.raises(errors.BuildError) as build_error,
        ):
            await session.request("GET", "/none", dict)

        assert isinstance(build_error.value, errors.BuildError)

        await cs.close()


class TestHandleOPCode:
    @pytest.mark.asyncio
    async def test_ready_event(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        event = session._handle_op_code(orjson.dumps(payloads.READY_PAYLOAD).decode())

        assert isinstance(event, events.ReadyEvent)

    @pytest.mark.asyncio
    async def test_player_update_event(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        event = session._handle_op_code(
            orjson.dumps(payloads.PLAYER_UPDATE_PAYLOAD).decode(),
        )

        assert isinstance(event, events.PlayerUpdateEvent)

    @pytest.mark.asyncio
    async def test_statistics_event(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        payload = dict(payloads.STATISTICS_PAYLOAD)

        payload.update({"op": "stats"})

        event = session._handle_op_code(orjson.dumps(payload).decode())

        assert isinstance(event, events.StatisticsEvent)

    @pytest.mark.asyncio
    async def test_track_start_event(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        event = session._handle_op_code(
            orjson.dumps(payloads.TRACK_START_PAYLOAD).decode(),
        )

        assert isinstance(event, events.TrackStartEvent)

    @pytest.mark.asyncio
    async def test_track_end_event(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        event = session._handle_op_code(
            orjson.dumps(payloads.TRACK_END_PAYLOAD).decode(),
        )

        assert isinstance(event, events.TrackEndEvent)

    @pytest.mark.asyncio
    async def test_track_exception_event(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        event = session._handle_op_code(
            orjson.dumps(payloads.TRACK_EXCEPTION_PAYLOAD).decode(),
        )

        assert isinstance(event, events.TrackExceptionEvent)

    @pytest.mark.asyncio
    async def test_track_stuck_event(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        event = session._handle_op_code(
            orjson.dumps(payloads.TRACK_STUCK_PAYLOAD).decode(),
        )

        assert isinstance(event, events.TrackStuckEvent)

    @pytest.mark.asyncio
    async def test_websocket_closed_event(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        event = session._handle_op_code(
            orjson.dumps(payloads.WEBSOCKET_CLOSED_PAYLOAD).decode(),
        )

        assert isinstance(event, events.WebsocketClosedEvent)


class TestHandleWSMessage:
    def test_text(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        message = aiohttp.WSMessage(
            aiohttp.WSMsgType.TEXT,
            orjson.dumps(payloads.READY_PAYLOAD).decode(),
            None,
        )

        with (
            mock.patch.object(
                session.app,
                "event_manager",
                new_callable=mock.Mock,
                return_value=mock.Mock(),
            ),
            mock.patch.object(
                session.app.event_manager,
                "dispatch",
                new_callable=mock.AsyncMock,
                return_value=None,
            ) as event_dispatched,
        ):
            assert session._handle_ws_message(message) is True

            assert len(event_dispatched.call_args_list) == 2

            first_event_args = event_dispatched.call_args_list[0].args

            assert len(first_event_args) == 1

            assert isinstance(first_event_args[0], events.PayloadEvent)

            first_event_args = event_dispatched.call_args_list[1].args

            assert len(first_event_args) == 1

            assert isinstance(first_event_args[0], events.ReadyEvent)

    def test_error(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        message = aiohttp.WSMessage(aiohttp.WSMsgType.ERROR, "", None)

        assert session._handle_ws_message(message) is False

    def test_closed(self, ongaku_client: Client):
        session = Session(
            ongaku_client,
            "test_session",
            False,
            "host",
            2333,
            "password",
            3,
        )

        message = aiohttp.WSMessage(
            aiohttp.WSMsgType.CLOSED,
            aiohttp.WSCloseCode.GOING_AWAY,
            "extra",
        )

        assert session._handle_ws_message(message) is False
