from __future__ import annotations

import typing
from unittest import mock

import hikari
import pytest

from ongaku import errors
from ongaku import session
from ongaku.api import handlers

if typing.TYPE_CHECKING:
    from ongaku.client import Client


class TestBasicHandler:
    def test_properties(self, ongaku_client: Client):
        handler = handlers.BasicHandler(ongaku_client)

        assert handler._client is ongaku_client
        assert handler._is_alive is False
        assert handler.sessions == []
        assert handler.players == []

    @pytest.mark.asyncio
    async def test_start(self, ongaku_client: Client):
        handler = handlers.BasicHandler(ongaku_client)

        session_1 = mock.Mock(start=mock.AsyncMock())
        session_2 = mock.Mock(start=mock.AsyncMock())

        client_session = mock.Mock()

        with mock.patch.object(
            handler,
            "_sessions",
            {hikari.Snowflake(123): session_1, hikari.Snowflake(456): session_2},
        ):
            await handler.start(client_session)

        assert handler.is_alive is True
        assert handler._client_session is client_session
        session_1.start.assert_awaited_once_with(client_session)
        session_2.start.assert_awaited_once_with(client_session)

    @pytest.mark.asyncio
    async def test_stop(self, ongaku_client: Client):
        handler = handlers.BasicHandler(ongaku_client)

        session_1 = mock.Mock(stop=mock.AsyncMock())
        session_2 = mock.Mock(stop=mock.AsyncMock())

        handler._is_alive = True

        with (
            mock.patch.object(
                handler,
                "_sessions",
                {"abc": session_1, "def": session_2},
            ),
            mock.patch.object(handler, "_players") as patched__players,
            mock.patch.object(patched__players, "clear") as patched_clear,
        ):
            await handler.stop()

        assert handler.is_alive is False
        patched_clear.assert_called_once_with()

        session_1.stop.assert_awaited_once_with()
        session_2.stop.assert_awaited_once_with()

    def test_add_session(self, ongaku_client: Client):
        handler = handlers.BasicHandler(ongaku_client)

        assert handler.sessions == []
        assert handler.is_alive is False

        mock_session = mock.Mock()

        handler.add_session(mock_session)

        assert handler.sessions == [mock_session]
        mock_session.start.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_session_with_started_client(self, ongaku_client: Client):
        handler = handlers.BasicHandler(ongaku_client)

        assert handler.sessions == []
        assert handler.is_alive is False

        mock_session = mock.Mock()

        with (
            mock.patch.object(handler, "_is_alive", True),
            mock.patch.object(handler, "_client_session") as patched__client_session,
            mock.patch("asyncio.create_task") as patched_create_task,
        ):
            handler.add_session(mock_session)

        assert handler.sessions == [mock_session]
        patched_create_task.assert_called_once_with(
            mock_session.start(patched__client_session),
        )

    def test_get_session(self, ongaku_client: Client):
        handler = handlers.BasicHandler(ongaku_client)

        mock_session = mock.Mock()

        handler._sessions = {
            "abc": mock_session,
        }
        handler._current_session = mock_session

        assert handler.get_session() is mock_session

    def test_get_session_with_name(self, ongaku_client: Client):
        handler = handlers.BasicHandler(ongaku_client)

        mock_session_1 = mock.Mock()
        mock_session_2 = mock.Mock()

        handler._sessions = {
            "abc": mock_session_1,
            "def": mock_session_2,
        }

        handler._current_session = mock_session_1

        assert handler.get_session("def") is mock_session_2

    def test_get_session_with_name_without_current_session(self, ongaku_client: Client):
        handler = handlers.BasicHandler(ongaku_client)

        mock_session_1 = mock.Mock()
        mock_session_2 = mock.Mock()

        handler._sessions = {
            "abc": mock_session_1,
            "def": mock_session_2,
        }

        assert handler.get_session("def") is mock_session_2

    def test_get_session_without_current_session(self, ongaku_client: Client):
        handler = handlers.BasicHandler(ongaku_client)

        mock_session_1 = mock.Mock(status=session.SessionStatus.FAILURE)
        mock_session_2 = mock.Mock(status=session.SessionStatus.CONNECTED)

        handler._sessions = {
            "abc": mock_session_1,
            "def": mock_session_2,
        }

        assert handler._current_session is None

        assert handler.get_session() is mock_session_2

        assert handler._current_session is mock_session_2

    def test_get_session_with_no_sessions(self, ongaku_client: Client):
        handler = handlers.BasicHandler(ongaku_client)

        assert handler.sessions == []

        with pytest.raises(errors.NoSessionsError):
            handler.get_session()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "set_current_session",
        [True, False],
    )
    async def test_delete_session(
        self,
        ongaku_client: Client,
        set_current_session: bool,
    ):
        handler = handlers.BasicHandler(ongaku_client)

        mock_session_1 = mock.Mock(stop=mock.AsyncMock())
        mock_session_2 = mock.Mock(stop=mock.AsyncMock())

        handler._sessions = {
            "abc": mock_session_1,
            "def": mock_session_2,
        }

        handler._current_session = mock_session_1 if set_current_session else None

        await handler.delete_session("def")

        if set_current_session:
            assert handler._current_session is mock_session_1
        else:
            assert handler._current_session is None
        assert handler._sessions == {
            "abc": mock_session_1,
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "set_current_session",
        [True, False],
    )
    async def test_delete_session_with_missing(
        self,
        ongaku_client: Client,
        set_current_session: bool,
    ):
        handler = handlers.BasicHandler(ongaku_client)

        mock_session_1 = mock.Mock(stop=mock.AsyncMock())

        handler._sessions = {
            "abc": mock_session_1,
        }

        handler._current_session = mock_session_1 if set_current_session else None

        with pytest.raises(errors.SessionMissingError):
            await handler.delete_session("def")

        if set_current_session:
            assert handler._current_session is mock_session_1
        else:
            assert handler._current_session is None
        assert handler._sessions == {
            "abc": mock_session_1,
        }

    def test_add_player(self, ongaku_client: Client):
        handler = handlers.BasicHandler(ongaku_client)

        assert handler._players == {}

        mock_player = mock.Mock(guild_id=hikari.Snowflake(123))

        assert handler.add_player(mock_player) is mock_player

        assert handler._players == {
            hikari.Snowflake(123): mock_player,
        }

    def test_add_player_with_existing(self, ongaku_client: Client):
        handler = handlers.BasicHandler(ongaku_client)

        mock_player = mock.Mock(guild_id=hikari.Snowflake(123))

        handler._players = {
            hikari.Snowflake(123): mock_player,
        }

        with pytest.raises(KeyError):
            handler.add_player(mock_player)

    def test_get_player(self, ongaku_client: Client):
        handler = handlers.BasicHandler(ongaku_client)

        mock_player = mock.Mock()

        handler._players = {
            hikari.Snowflake(123): mock_player,
        }

        assert handler.get_player(123) is mock_player

    def test_get_player_with_missing(self, ongaku_client: Client):
        handler = handlers.BasicHandler(ongaku_client)

        assert handler._players == {}

        with pytest.raises(errors.PlayerMissingError):
            handler.get_player(123)

    @pytest.mark.asyncio
    async def test_delete_player(self, ongaku_client: Client):
        handler = handlers.BasicHandler(ongaku_client)

        mock_player = mock.Mock(disconnect=mock.AsyncMock())

        handler._players = {
            hikari.Snowflake(123): mock_player,
        }

        await handler.delete_player(123)

        mock_player.disconnect.assert_awaited_once_with()

    @pytest.mark.asyncio
    async def test_delete_player_with_missing(self, ongaku_client: Client):
        handler = handlers.BasicHandler(ongaku_client)

        assert handler._players == {}

        with pytest.raises(errors.PlayerMissingError):
            await handler.delete_player(123)
