from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest
from aiohttp import ClientSession
from arc.client import GatewayClient as ArcGatewayClient
from hikari.snowflakes import Snowflake
from tanjun.clients import Client as TanjunClient

from ongaku import Player
from ongaku import errors
from ongaku.abc.handler import SessionHandler
from ongaku.builders import EntityBuilder
from ongaku.client import Client
from ongaku.rest import RESTClient

if TYPE_CHECKING:
    from hikari.impl import gateway_bot as gateway_bot_

    from ongaku.session import Session


class TestClient:
    def test_from_arc(self, gateway_bot: gateway_bot_.GatewayBot):
        command_client = ArcGatewayClient(gateway_bot)

        client = Client.from_arc(command_client)

        assert client.app == gateway_bot

        assert client.is_alive is False

        assert isinstance(client.rest, RESTClient)

        assert command_client.get_type_dependency(Client) == client

        # check that from_arc method, adds the player hook.

        command_client = ArcGatewayClient(gateway_bot)

        with mock.patch(
            "arc.client.Client.add_injection_hook",
        ) as patched_injection_hook:
            client = Client.from_arc(command_client)

            patched_injection_hook.assert_called_once_with(client._arc_player_injector)

    def test_from_tanjun(self, gateway_bot: gateway_bot_.GatewayBot):
        command_client = TanjunClient.from_gateway_bot(gateway_bot)

        client = Client.from_tanjun(command_client)

        assert client.app == gateway_bot

        assert client.is_alive is False

        assert isinstance(client.rest, RESTClient)

    def test_properties(self, gateway_bot: gateway_bot_.GatewayBot):
        client = Client(gateway_bot)

        assert client.app == gateway_bot

        assert isinstance(client.rest, RESTClient)

        assert client.is_alive is False

        assert isinstance(client.entity_builder, EntityBuilder)

        assert isinstance(client.session_handler, SessionHandler)

    @pytest.mark.asyncio
    async def test_get_client_session(self, gateway_bot: gateway_bot_.GatewayBot):
        client = Client(gateway_bot)

        assert isinstance(client._get_client_session(), ClientSession)

    @pytest.mark.asyncio
    async def test_create_session(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_session: Session,
    ):
        client = Client(gateway_bot)

        with (
            mock.patch.object(client, "_session_handler"),
            mock.patch.object(
                client.session_handler,
                "add_session",
                return_value=ongaku_session,
            ) as patched_add_session,
        ):
            client.create_session("test_session", False, host="127.0.0.1")

            patched_add_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_player_create(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_session: Session,
        ongaku_player: Player,
    ):
        client = Client(gateway_bot)

        # Create a new player.

        with (
            mock.patch.object(client, "_session_handler"),
            mock.patch.object(
                client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ),
            mock.patch.object(
                client.session_handler,
                "fetch_player",
                side_effect=errors.PlayerMissingError,
            ),
            mock.patch.object(
                client.session_handler,
                "add_player",
                return_value=mock.Mock(guild_id=Snowflake(1234567890)),
            ) as patched_add_player,
        ):
            player = client.create_player(1234567890)

            patched_add_player.assert_called_once()

            assert player.guild_id == Snowflake(1234567890)

        # Create an existing player.

        with (
            mock.patch.object(client, "_session_handler"),
            mock.patch.object(
                client.session_handler,
                "fetch_session",
                return_value=ongaku_session,
            ),
            mock.patch.object(
                client.session_handler,
                "fetch_player",
                return_value=ongaku_player,
            ),
            mock.patch.object(
                client.session_handler,
                "add_player",
                return_value=mock.Mock(guild_id=Snowflake(1234567890)),
            ) as patched_add_player,
        ):
            player = client.create_player(1234567890)

            assert player == ongaku_player

            patched_add_player.assert_not_called()

    @pytest.mark.asyncio
    async def test_player_fetch(
        self,
        gateway_bot: gateway_bot_.GatewayBot,
        ongaku_player: Player,
    ):
        client = Client(gateway_bot)

        client.session_handler.add_player(ongaku_player)

        player = client.fetch_player(1234567890)

        assert player.guild_id == Snowflake(1234567890)

        with mock.patch.object(
            ongaku_player,
            "disconnect",
            new_callable=mock.AsyncMock,
            return_value=None,
        ):
            await client.session_handler.delete_player(Snowflake(1234567890))

        with pytest.raises(errors.PlayerMissingError):
            client.fetch_player(1234567890)

    @pytest.mark.asyncio
    async def test_player_delete(self, gateway_bot: gateway_bot_.GatewayBot):
        client = Client(gateway_bot)

        with (
            mock.patch.object(client, "_session_handler"),
            mock.patch.object(
                client.session_handler,
                "delete_player",
                new_callable=mock.AsyncMock,
                return_value=None,
            ) as patched_delete_player,
        ):
            await client.session_handler.delete_player(Snowflake(1234567890))

            patched_delete_player.assert_called_once_with(Snowflake(1234567890))
