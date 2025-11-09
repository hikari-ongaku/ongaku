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
"""Session handler implementations."""

from __future__ import annotations

import asyncio
import typing

import hikari
import typing_extensions as te

from ongaku import errors
from ongaku.abc.handlers import Handler
from ongaku.session import SessionStatus

if typing.TYPE_CHECKING:
    import aiohttp

    from ongaku import player
    from ongaku import session
    from ongaku.client import Client

__all__: typing.Sequence[str] = ("BasicHandler",)


class BasicHandler(Handler):
    """Basic Handler.

    This handler simply fetches the first working session, and returns it.
    If it closes or fails, it switches to the next available one.
    """

    __slots__: typing.Sequence[str] = (
        "_client_session",
        "_current_session",
        "_players",
        "_sessions",
    )

    @te.override
    def __init__(self, client: Client) -> None:
        self._client = client
        self._is_alive = False
        self._current_session: session.Session | None = None
        self._sessions: typing.MutableMapping[str, session.Session] = {}
        self._players: typing.MutableMapping[hikari.Snowflake, player.Player] = {}
        self._client_session = None

    @property
    @te.override
    def sessions(self) -> typing.Sequence[session.Session]:
        return list(self._sessions.values())

    @property
    @te.override
    def players(self) -> typing.Sequence[player.Player]:
        return list(self._players.values())

    @property
    def is_alive(self) -> bool:
        """Whether the handler is alive."""
        return self._is_alive

    @te.override
    async def start(self, client_session: aiohttp.ClientSession) -> None:
        self._is_alive = True

        self._client_session = client_session

        await asyncio.gather(*[i.start(client_session) for i in self.sessions])

    @te.override
    async def stop(self) -> None:
        await asyncio.gather(*[i.stop() for i in self.sessions])

        self._players.clear()

        self._is_alive = False

    @te.override
    def add_session(self, session: session.Session) -> session.Session:
        if self.is_alive and self._client_session is None:
            raise errors.SessionClientSessionMissingError

        if self._is_alive and self._client_session is not None:
            asyncio.create_task(session.start(self._client_session))  # noqa: RUF006 This will not last long enough to matter.

        if self._sessions.get(session.name, None) is None:
            self._sessions.update({session.name: session})
            return session

        raise KeyError

    @te.override
    def get_session(self, name: str | None = None) -> session.Session:
        if len(self._sessions) == 0:
            raise errors.NoSessionsError

        if name is not None:
            return self._sessions[name]

        if self._current_session:
            return self._current_session

        for session in self.sessions:
            if session.status == SessionStatus.CONNECTED:
                self._current_session = session
                return session

        raise errors.NoSessionsError

    @te.override
    async def delete_session(self, name: str) -> None:
        try:
            session = self._sessions.pop(name)
        except KeyError as err:
            raise errors.SessionMissingError from err

        if self._current_session is session:
            self._current_session = None

        await session.stop()

    @te.override
    def add_player(self, player: player.Player) -> player.Player:
        if self._players.get(player.guild_id, None) is not None:
            raise KeyError

        self._players.update({player.guild_id: player})

        return player

    @te.override
    def get_player(
        self,
        guild: hikari.SnowflakeishOr[hikari.Guild],
    ) -> player.Player:
        player = self._players.get(hikari.Snowflake(guild))

        if not player:
            raise errors.PlayerMissingError

        return player

    @te.override
    async def delete_player(
        self,
        guild: hikari.SnowflakeishOr[hikari.Guild],
    ) -> None:
        try:
            player = self._players.pop(hikari.Snowflake(guild))
        except KeyError as err:
            raise errors.PlayerMissingError from err

        await player.disconnect()
