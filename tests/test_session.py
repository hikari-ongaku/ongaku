from __future__ import annotations

import asyncio
import http
import json
import re
import typing
from typing import TYPE_CHECKING
from unittest import mock

import aiohttp
import hikari
import pytest
from aiohttp import web

from ongaku import errors
from ongaku import events
from ongaku.abc import extensions
from ongaku.internal.about import __version__
from ongaku.session import PartialSession
from ongaku.session import Session
from ongaku.session import SessionStatus

if TYPE_CHECKING:
    from ongaku.client import Client


def test_partial_session():
    session = PartialSession(resuming=True, timeout=1)

    assert session.resuming is True
    assert session.timeout == 1


class TestSession:
    def test_properties(self, ongaku_client: Client):
        session = Session(
            client=ongaku_client,
            name="name",
            ssl=True,
            host="host",
            port=1234,
            password="password",
        )

        assert session.client == ongaku_client
        assert session.app == ongaku_client.app
        assert session.name == "name"
        assert session.ssl is True
        assert session.host == "host"
        assert session.port == 1234
        assert session.password == "password"
        assert session.base_uri == "https://host:1234"
        assert session.status == SessionStatus.NOT_CONNECTED
        assert session.session_id is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("global_name", "display_name", "expected_name"),
        [
            ("global_name", "display_name", "global_name"),
            ("global_name", None, "global_name"),
            ("global_name", hikari.UNDEFINED, "global_name"),
            (None, "display_name", "display_name"),
            (None, None, "unknown"),
            (None, hikari.UNDEFINED, "unknown"),
        ],
    )
    async def test_start(
        self,
        ongaku_client: Client,
        global_name: str | None,
        display_name: hikari.UndefinedNoneOr[str],
        expected_name: str,
    ):
        session = Session(
            client=ongaku_client,
            name="name",
            ssl=True,
            host="host",
            port=1234,
            password="password",
        )

        client_session = mock.Mock()

        with (
            mock.patch.object(
                ongaku_client.app,
                "get_me",
                return_value=mock.Mock(
                    id=123,
                    global_name=global_name,
                    display_name=display_name,
                ),
            ) as patched_get_me,
            mock.patch(
                "ongaku.session.Session._websocket",
                new_callable=mock.AsyncMock,
            ) as patched__websocket,
        ):
            await session.start(client_session)

        patched_get_me.assert_called_once()
        patched__websocket.assert_called_once_with(
            client_session,
            {
                "User-Id": "123",
                "Client-Name": f"{expected_name}/{__version__}",
                "Authorization": "password",
            },
        )

    @pytest.mark.asyncio
    async def test_start_with_missing_bot(self, ongaku_client: Client):
        session = Session(
            client=ongaku_client,
            name="name",
            ssl=True,
            host="host",
            port=1234,
            password="password",
        )

        client_session = mock.Mock()

        with (
            mock.patch.object(
                ongaku_client.app,
                "get_me",
                return_value=None,
            ) as patched_get_me,
            mock.patch(
                "ongaku.session.Session._websocket",
                new_callable=mock.AsyncMock,
            ) as patched__websocket,
            pytest.raises(
                errors.SessionMissingBotInformationError,
                match=r"^$",
            ),
        ):
            await session.start(client_session)

        patched_get_me.assert_called_once()
        patched__websocket.assert_not_called()

    @pytest.mark.asyncio
    async def test_stop(self, ongaku_client: Client):
        session = Session(
            client=ongaku_client,
            name="name",
            ssl=True,
            host="host",
            port=1234,
            password="password",
        )

        async def test_func() -> None:
            pass

        task: asyncio.Task[None] = asyncio.create_task(test_func())

        session._session_task = task

        await session.stop()

        assert task.cancelled() is True
        assert task.done() is True

    # To test:
    # - Attempts timeout.

    @staticmethod
    def ws_handler_setup(
        events: list[str],
    ) -> typing.Callable[[web.Request], typing.Awaitable[web.WebSocketResponse]]:
        async def ws_handler(request: web.Request) -> web.WebSocketResponse:
            assert request.url.path == "/v4/websocket"

            ws = web.WebSocketResponse()
            await ws.prepare(request)

            for event in events:
                await ws.send_str(event)
                await asyncio.sleep(1)

            return ws

        return ws_handler

    @pytest.mark.asyncio
    async def test_websocket(
        self,
        ongaku_client: Client,
        aiohttp_client: typing.Any,  # noqa: ANN401
    ):
        session = Session(
            client=ongaku_client,
            name="name",
            ssl=True,
            host="host",
            port=1234,
            password="password",
        )

        ws_events = [
            json.dumps(
                {
                    "op": "ready",
                    "sessionId": "session_id",
                },
            ),
        ]

        app = web.Application()
        app.router.add_route("GET", "/v4/websocket", self.ws_handler_setup(ws_events))

        client = await aiohttp_client(app)

        with (
            mock.patch.object(
                session,
                "_base_uri",
                new_callable=mock.PropertyMock(return_value=""),
            ),
            mock.patch.object(
                session.client._app.event_manager,
                "dispatch",
                new_callable=mock.Mock,
                return_value=None,
            ) as patched_dispatch,
            mock.patch(
                "ongaku.session.Session._handle_payload",
                side_effect=[mock.Mock(events.ReadyEvent)],
            ) as patched__handle_payload,
        ):
            task = asyncio.create_task(
                session._websocket(client, headers={"test": "headers"}),
            )
            await asyncio.sleep(2)
            task.cancel()

            assert len(patched_dispatch.call_args_list) == 3

            first_event_args = patched_dispatch.call_args_list[0].args
            assert len(first_event_args) == 1
            assert isinstance(first_event_args[0], events.SessionConnectedEvent)

            second_event_args = patched_dispatch.call_args_list[1].args
            assert len(second_event_args) == 1
            assert isinstance(second_event_args[0], events.PayloadEvent)

            third_event_args = patched_dispatch.call_args_list[2].args
            assert len(third_event_args) == 1
            assert isinstance(third_event_args[0], events.ReadyEvent)

            patched__handle_payload.assert_called_once()

    @pytest.mark.skip("TODO")
    @pytest.mark.asyncio
    async def test_websocket_error_event(
        self,
        ongaku_client: Client,
        aiohttp_client: typing.Any,  # noqa: ANN401
    ):
        pass

    @pytest.mark.skip("TODO")
    @pytest.mark.asyncio
    async def test_websocket_closed_event(
        self,
        ongaku_client: Client,
        aiohttp_client: typing.Any,  # noqa: ANN401
    ):
        pass

    @pytest.mark.asyncio
    async def test_websocket_timeout(
        self,
        ongaku_client: Client,
        aiohttp_client: typing.Any,  # noqa: ANN401
    ):
        session = Session(
            client=ongaku_client,
            name="name",
            ssl=True,
            host="host",
            port=1234,
            password="password",
        )

        app = web.Application()
        app.router.add_route("GET", "/v4/websocket", self.ws_handler_setup([]))

        client = await aiohttp_client(app)

        with (
            mock.patch.object(
                session,
                "_base_uri",
                new_callable=mock.PropertyMock(return_value=""),
            ),
            mock.patch.object(
                session.client._app.event_manager,
                "dispatch",
                new_callable=mock.Mock,
                return_value=None,
            ) as patched_dispatch,
            mock.patch(
                "ongaku.session.Session._handle_payload",
                side_effect=[],
            ) as patched__handle_payload,
            mock.patch(
                "ongaku.session.WEBSOCKET_TIMEOUT",
                2,
            ),
        ):
            task = asyncio.create_task(
                session._websocket(client, headers={"test": "headers"}),
            )
            await asyncio.sleep(4)
            task.cancel()

            assert len(patched_dispatch.call_args_list) == 2

            first_event_args = patched_dispatch.call_args_list[0].args
            assert len(first_event_args) == 1
            assert isinstance(first_event_args[0], events.SessionConnectedEvent)

            second_event_args = patched_dispatch.call_args_list[0].args
            assert len(second_event_args) == 1
            assert isinstance(second_event_args[0], events.SessionConnectedEvent)

            patched__handle_payload.assert_not_called()

    @pytest.mark.parametrize(
        ("op", "event", "deserialize_type"),
        [
            ("ready", None, "deserialize_ready_event"),
            ("playerUpdate", None, "deserialize_player_update_event"),
            ("stats", None, "deserialize_statistics_event"),
            ("event", "TrackStartEvent", "deserialize_track_start_event"),
            ("event", "TrackEndEvent", "deserialize_track_end_event"),
            ("event", "TrackExceptionEvent", "deserialize_track_exception_event"),
            ("event", "TrackStuckEvent", "deserialize_track_stuck_event"),
            ("event", "WebSocketClosedEvent", "deserialize_websocket_closed_event"),
        ],
    )
    def test__handle_payload(
        self,
        ongaku_client: Client,
        op: str,
        event: str | None,
        deserialize_type: str,
    ):
        with mock.patch(
            f"ongaku.api.builders.EntityBuilder.{deserialize_type}",
        ) as patched_deserialize_type:
            session = Session(
                client=ongaku_client,
                name="name",
                ssl=True,
                host="host",
                port=1234,
                password="password",
            )

            payload = {"op": op, "sessionId": "session_id"}

            if event:
                payload["type"] = event

            assert (
                session._handle_payload(json.dumps(payload))
                == patched_deserialize_type.return_value
            )

    def test__handle_payload_with_sequence(self, ongaku_client: Client):
        session = Session(
            client=ongaku_client,
            name="name",
            ssl=True,
            host="host",
            port=1234,
            password="password",
        )

        with pytest.raises(
            errors.BuildTypeError,
            match=rf"({typing.Mapping}, {typing.Sequence})",
        ):
            session._handle_payload("[{}, {}]")

    def test__handle_payload_with_extension(self, ongaku_client: Client):
        session = Session(
            client=ongaku_client,
            name="name",
            ssl=True,
            host="host",
            port=1234,
            password="password",
        )

        event_handler = mock.Mock()
        extension = mock.Mock(extensions.Extension, event_handler=event_handler)

        session._extensions = {extensions.Extension}

        payload = {
            "op": "event",
            "type": "CustomEvent",
        }

        with (
            mock.patch.object(session._client, "_injector") as patched__injector,
            mock.patch.object(
                patched__injector,
                "get_type_dependency",
                return_value=extension,
            ) as patched_get_type_dependency,
        ):
            session._handle_payload(json.dumps(payload))

        patched_get_type_dependency.assert_called_once_with(extensions.Extension)
        event_handler.assert_called_once_with(payload, session)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        (
            "headers",
            "body",
            "params",
            "ignore_default_headers",
            "optional",
            "cs_response",
            "return_value",
        ),
        [
            (
                None,
                None,
                None,
                False,
                False,
                mock.Mock(
                    aiohttp.ClientResponse,
                    status=http.HTTPStatus.OK,
                    content_type="text/plain",
                    text=mock.AsyncMock(return_value="test"),
                ),
                "test",
            ),
            (
                None,
                None,
                None,
                True,
                False,
                mock.Mock(
                    aiohttp.ClientResponse,
                    status=http.HTTPStatus.OK,
                    content_type="text/plain",
                    text=mock.AsyncMock(return_value="test"),
                ),
                "test",
            ),
            (
                None,
                None,
                None,
                False,
                True,
                mock.Mock(
                    aiohttp.ClientResponse,
                    status=http.HTTPStatus.OK,
                    content_type="application/json",
                    text=mock.AsyncMock(return_value="{}"),
                ),
                {},
            ),
            (
                None,
                None,
                None,
                False,
                True,
                mock.Mock(
                    aiohttp.ClientResponse,
                    status=http.HTTPStatus.NO_CONTENT,
                    content_type="text/plain",
                    text=mock.AsyncMock(return_value=""),
                ),
                None,
            ),
            (
                {"some": "headers"},
                {"a": "body"},
                {"more": "params"},
                False,
                True,
                mock.Mock(
                    aiohttp.ClientResponse,
                    status=http.HTTPStatus.NO_CONTENT,
                    content_type="text/plain",
                    text=mock.AsyncMock(return_value=""),
                ),
                None,
            ),
        ],
    )
    async def test_request(
        self,
        ongaku_client: Client,
        headers: dict[str, typing.Any] | None,
        body: str | None,
        params: dict[str, typing.Any] | None,
        ignore_default_headers: bool,
        optional: bool,
        cs_response: aiohttp.ClientResponse,
        return_value: dict[str, typing.Any] | list[typing.Any] | str | None,
    ):
        session = Session(
            client=ongaku_client,
            name="name",
            ssl=True,
            host="host",
            port=1234,
            password="password",
        )

        client_session = mock.AsyncMock(
            request=mock.AsyncMock(return_value=cs_response),
        )
        session._client_session = client_session

        route = mock.Mock(method="GET", path="/hello/world")
        assert (
            await session.request(
                route,
                headers=headers,
                body=body,
                params=params,
                ignore_default_headers=ignore_default_headers,
                optional=optional,
            )
            == return_value
        )

        if ignore_default_headers:
            client_session.request.assert_awaited_once_with(
                route.method,
                f"{session.base_uri}{route.path}",
                headers=headers or {},
                json=body,
                params=params,
            )
        else:
            final_headers = {"Authorization": session.password}
            if headers is not None:
                final_headers.update(headers)

            client_session.request.assert_awaited_once_with(
                route.method,
                f"{session.base_uri}{route.path}",
                headers=final_headers,
                json=body,
                params=params,
            )

    @pytest.mark.asyncio
    async def test_request_without_client_session(self, ongaku_client: Client):
        session = Session(
            client=ongaku_client,
            name="name",
            ssl=True,
            host="host",
            port=1234,
            password="password",
        )

        assert session._client_session is None

        with pytest.raises(
            errors.SessionClientSessionMissingError,
            match=r"^$",
        ):
            await session.request(mock.Mock())

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        (
            "optional",
            "cs_response",
            "exception",
            "match",
        ),
        [
            (
                False,
                mock.Mock(
                    aiohttp.ClientResponse,
                    status=http.HTTPStatus.NO_CONTENT,
                    content_type="text/plain",
                    text=mock.AsyncMock(return_value=""),
                ),
                errors.RestEmptyError,
                "^$",
            ),
            (
                False,
                mock.Mock(
                    aiohttp.ClientResponse,
                    status=http.HTTPStatus.NOT_FOUND,
                    content_type="text/plain",
                    text=mock.AsyncMock(return_value=""),
                ),
                errors.RestEmptyError,
                "^$",
            ),
            (
                True,
                mock.Mock(
                    aiohttp.ClientResponse,
                    status=http.HTTPStatus.BAD_REQUEST,
                    reason="A bad request was made.",
                    content_type="text/plain",
                    text=mock.AsyncMock(return_value=""),
                ),
                errors.RestStatusError,
                f"({http.HTTPStatus.BAD_REQUEST.real}, 'A bad request was made.')",
            ),
            (
                True,
                mock.Mock(
                    aiohttp.ClientResponse,
                    status=http.HTTPStatus.BAD_REQUEST,
                    reason="A bad request was made.",
                    content_type="application/json",
                    text=mock.AsyncMock(
                        return_value="""{
                        "timestamp": 1000,
                        "status": 400,
                        "error": "Bad Request",
                        "message": "A bad request was made.",
                        "path": "/hello/world",
                        "trace": null
                    }""",
                    ),
                ),
                errors.RestRequestError,
                re.escape(
                    "(datetime.datetime(1970, 1, 1, 0, 0, 1, tzinfo=datetime.timezone.utc), 400, 'Bad Request', 'A bad request was made.', '/hello/world', None)",
                ),
            ),
            (
                True,
                mock.Mock(
                    aiohttp.ClientResponse,
                    status=http.HTTPStatus.OK,
                    content_type="application/json",
                    text=mock.AsyncMock(return_value='{"test": invalid_data}'),
                ),
                errors.BuildError,
                re.escape("unexpected character: line 1 column 10 (char 9)"),
            ),
        ],
    )
    async def test_request_with_exceptions(
        self,
        ongaku_client: Client,
        optional: bool,
        cs_response: aiohttp.ClientResponse,
        exception: type[Exception],
        match: str | None,
    ):
        session = Session(
            client=ongaku_client,
            name="name",
            ssl=True,
            host="host",
            port=1234,
            password="password",
        )

        client_session = mock.AsyncMock(
            request=mock.AsyncMock(return_value=cs_response),
        )
        session._client_session = client_session

        route = mock.Mock(method="GET", path="/hello/world")

        with pytest.raises(exception, match=match):
            await session.request(
                route,
                optional=optional,
            )

        client_session.request.assert_awaited_once_with(
            route.method,
            f"{session.base_uri}{route.path}",
            headers={"Authorization": session.password},
            json=None,
            params=None,
        )

    @pytest.mark.asyncio
    async def test_transfer(self, ongaku_client: Client):
        session = Session(
            client=ongaku_client,
            name="name",
            ssl=True,
            host="host",
            port=1234,
            password="password",
        )

        player_1 = mock.AsyncMock()
        player_2 = mock.AsyncMock()
        player_3 = mock.AsyncMock()

        session._players = {
            hikari.Snowflake(123): player_1,
            hikari.Snowflake(456): player_2,
            hikari.Snowflake(789): player_3,
        }

        handler = mock.Mock()

        with mock.patch("ongaku.session.Session.stop") as patched_stop:
            await session.transfer(handler)

        handler.get_session.assert_called_once_with()
        add_player_calls: list[mock._Call] = handler.add_player.call_args_list
        assert len(add_player_calls) == 3
        assert add_player_calls[0].kwargs == {"player": player_1.transfer.return_value}
        assert add_player_calls[1].kwargs == {"player": player_2.transfer.return_value}
        assert add_player_calls[2].kwargs == {"player": player_3.transfer.return_value}
        player_1.transfer.assert_awaited_once_with(
            session=handler.get_session.return_value,
        )
        player_2.transfer.assert_awaited_once_with(
            session=handler.get_session.return_value,
        )
        player_3.transfer.assert_awaited_once_with(
            session=handler.get_session.return_value,
        )
        patched_stop.assert_awaited_once_with()
