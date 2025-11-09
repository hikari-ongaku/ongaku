from __future__ import annotations

import typing
from unittest import mock

import pytest

from ongaku.client import Client
from ongaku.player import Player
from ongaku.session import Session

if typing.TYPE_CHECKING:
    import hikari


@pytest.fixture
def hikari_app() -> hikari.GatewayBotAware:
    return mock.Mock()


@pytest.fixture
def ongaku_client(hikari_app: hikari.GatewayBotAware) -> Client:
    return Client(hikari_app)


@pytest.fixture
def ongaku_session(ongaku_client: Client) -> Session:
    return Session(
        ongaku_client,
        name="name",
        ssl=False,
        host="host",
        port=1,
        password="password",
    )


@pytest.fixture
def ongaku_player(ongaku_session: Session) -> Player:
    return Player(
        ongaku_session,
        123,
    )
