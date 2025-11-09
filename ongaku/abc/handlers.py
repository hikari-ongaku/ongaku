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
"""Abstract handler objects."""

from __future__ import annotations

import abc
import typing

if typing.TYPE_CHECKING:
    import aiohttp
    import hikari

    from ongaku import player
    from ongaku import session
    from ongaku.client import Client

__all__: typing.Sequence[str] = ("Handler",)


class Handler(abc.ABC):
    """Handler base.

    The base session handler object.

    !!! note
        All custom session handlers **must** subclass this.

    Parameters
    ----------
    client
        The base ongaku client.
    """

    __slots__: typing.Sequence[str] = (
        "_client",
        "_is_alive",
    )

    @abc.abstractmethod
    def __init__(self, client: Client) -> None: ...

    @property
    @abc.abstractmethod
    def sessions(self) -> typing.Sequence[session.Session]:
        """The sessions attached to this handler."""

    @property
    @abc.abstractmethod
    def players(self) -> typing.Sequence[player.Player]:
        """The players attached to this handler."""

    @property
    def is_alive(self) -> bool:
        """Whether the handler is alive."""
        return self._is_alive

    @abc.abstractmethod
    async def start(self, client_session: aiohttp.ClientSession) -> None:
        """Start the session handler.

        Starts up the session handler and attempts,
        to connect all sessions to their websocket.

        Parameters
        ----------
        client_session
            The client session to pass to sessions when starting.
        """

    @abc.abstractmethod
    async def stop(self) -> None:
        """Stop the session handler.

        Stops the session handler and kills all players and sessions.
        """

    @abc.abstractmethod
    def add_session(self, session: session.Session) -> session.Session:
        """Add a session.

        Add a new session to the session handler.

        Parameters
        ----------
        session
            The session to add to the session handler.

        Returns
        -------
        Session
            The session that was added to the handler.
        """

    @abc.abstractmethod
    def get_session(self, name: str | None = None) -> session.Session:
        """Fetch a session.

        Returns a valid session.

        !!! note
            If a name is provided, only that session will be attempted to be returned.

        Parameters
        ----------
        name
            The name of the session.

        Returns
        -------
        Session
            The session to use.

        Raises
        ------
        NoSessionError
            Raised when there is no available sessions for the handler to return.
        SessionMissingError
            Raised when a session is requested, but does not exist.
        """

    @abc.abstractmethod
    async def delete_session(self, name: str) -> None:
        """Delete a session.

        Delete a session from the session handler.

        Parameters
        ----------
        name
            The name of the session to delete.

        Returns
        -------
        Session
            The session that was added to the handler.

        Raises
        ------
        SessionMissingError
            Raised when the session does not exist.
        """

    @abc.abstractmethod
    def add_player(self, player: player.Player) -> player.Player:
        """Add a player.

        Add a new player to the session handler.

        Parameters
        ----------
        player
            The player to add to the session handler.

        Returns
        -------
        Player
            The player you added to the session handler.
        """

    @abc.abstractmethod
    def get_player(
        self,
        guild: hikari.SnowflakeishOr[hikari.Guild],
    ) -> player.Player:
        """Fetch a player.

        Fetches an existing player.

        Parameters
        ----------
        guild
            The `guild`, or `guild id` you wish to fetch the player for.

        Raises
        ------
        PlayerMissingError
            Raised when the player for the specified guild does not exist.
        """

    @abc.abstractmethod
    async def delete_player(
        self,
        guild: hikari.SnowflakeishOr[hikari.Guild],
    ) -> None:
        """Delete a player.

        Delete a pre-existing player.

        Parameters
        ----------
        guild
            The `guild`, or `guild id` you wish to delete the player from.

        Raises
        ------
        PlayerMissingError
            Raised when the player for the specified guild does not exist.
        """
