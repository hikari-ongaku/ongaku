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
"""Client for ongaku."""

from __future__ import annotations

import logging
import typing

import aiohttp
import alluka
import hikari

from ongaku import errors
from ongaku import player as player_
from ongaku import session as session_
from ongaku.api.builders import EntityBuilder
from ongaku.api.handlers import BasicHandler
from ongaku.api.rest import RESTClient
from ongaku.internal.logging import TRACE_LEVEL

if typing.TYPE_CHECKING:
    try:
        import arc
        import tanjun
    except ImportError:
        pass

    from ongaku.abc.extensions import Extension
    from ongaku.abc.handlers import Handler
    from ongaku.internal import types

_logger: typing.Final[logging.Logger] = logging.getLogger("ongaku.client")

__all__: typing.Sequence[str] = ("Client",)


class Client:
    """Client.

    The client for ongaku.

    !!! note
        The lowest log level for ongaku is `TRACE_ONGAKU`,
        which will result in all traces being printed to the terminal.

    Example
    -------
    ```py
    bot = hikari.GatewayBot("...")
    client = ongaku.Client(bot)
    ```

    Parameters
    ----------
    app
        The application that the client will attach too.
    handler
        The session handler to use for the current client.
    logs
        The log level for ongaku.
    injector
        The injector for the client and extensions
    """

    __slots__: typing.Sequence[str] = (
        "_app",
        "_builder",
        "_client_session",
        "_extensions",
        "_handler",
        "_injector",
        "_is_alive",
        "_rest_client",
    )

    def __init__(
        self,
        app: hikari.GatewayBotAware,
        *,
        handler: type[Handler] = BasicHandler,
        logs: str | int = "INFO",
        injector: alluka.abc.Client | None = None,
    ) -> None:
        _logger.setLevel(logs)

        self._app = app
        self._client_session: aiohttp.ClientSession | None = None

        self._rest_client = RESTClient(self)

        self._is_alive = False

        self._handler = handler(self)

        self._builder = EntityBuilder()

        self._injector: alluka.abc.Client = injector or alluka.Client()

        self._extensions: set[type[Extension]] = set()

        self.injector.set_type_dependency(Client, self)

        app.event_manager.subscribe(hikari.StartedEvent, self._start_event)
        app.event_manager.subscribe(hikari.StoppingEvent, self._stop_event)

    @classmethod
    def from_arc(
        cls,
        client: arc.GatewayClient,
        *,
        handler: type[Handler] = BasicHandler,
        logs: str | int = "INFO",
    ) -> Client:
        """From Arc.

        This supports `client` and `player` [injection](../gs/injection.md) for [Arc](https://github.com/hypergonial/hikari-arc)

        Example
        -------
        ```py
        bot = arc.GatewayBot(...)
        client = arc.GatewayClient(bot)
        ongaku_client = ongaku.Client.from_arc(client)
        ```

        Parameters
        ----------
        client
            Your Gateway client for arc.
        handler
            The session handler to use for the current client.
        logs
            The log level for ongaku.
        """
        c = cls(
            client.app,
            handler=handler,
            logs=logs,
            injector=client.injector,
        )

        client.add_injection_hook(c._arc_player_injector)

        return c

    @classmethod
    def from_tanjun(
        cls,
        client: tanjun.abc.Client,
        *,
        handler: type[Handler] = BasicHandler,
        logs: str | int = "INFO",
    ) -> Client:
        """From Tanjun.

        This supports `client` [injection](../gs/injection.md) for [Tanjun](https://github.com/FasterSpeeding/Tanjun)

        Example
        -------
        ```py
        bot = arc.GatewayBot(...)
        client = tanjun.Client.from_gateway_bot(bot)
        ongaku_client = ongaku.Client.from_tanjun(client)
        ```

        Parameters
        ----------
        client
            Your Gateway client from tanjun.
        handler
            The session handler to use for the current client.
        logs
            The log level for ongaku.
        """
        try:
            app = client.get_type_dependency(hikari.GatewayBotAware)
        except KeyError as err:
            raise ValueError("Missing gateway bot.") from err  # noqa: TRY003

        return cls(
            app,
            handler=handler,
            logs=logs,
            injector=client.injector,
        )

    @property
    def app(self) -> hikari.GatewayBotAware:
        """The application this client is included in."""
        return self._app

    @property
    def rest(self) -> RESTClient:
        """The rest client for calling rest actions."""
        return self._rest_client

    @property
    def is_alive(self) -> bool:
        """Whether the session handler is alive.

        !!! note
            If the `hikari.StartedEvent` has occurred, and this is False,
            ongaku is no longer running and has crashed. Check your logs.
        """
        return self._is_alive

    @property
    def builder(self) -> EntityBuilder:
        """Builder.

        The builder to make internal entities.
        """
        return self._builder

    @property
    def handler(self) -> Handler:
        """Handler.

        The session handler that is currently controlling the sessions.

        !!! warning
            This should not be touched, or used if you do not know what you are doing.
            Please use the other methods in client for anything session handler related.
        """
        return self._handler

    @property
    def injector(self) -> alluka.abc.Client:
        """The dependency injector."""
        return self._injector

    async def _start_event(self, _: hikari.StartedEvent) -> None:
        _logger.log(TRACE_LEVEL, "Creating client session.")
        self._client_session = aiohttp.ClientSession()
        _logger.log(TRACE_LEVEL, "Starting up session handler.")
        await self.handler.start(self._client_session)

        if self.handler.is_alive and not self._client_session.closed:
            self._is_alive = True
        _logger.log(TRACE_LEVEL, "Successfully started ongaku.")

    async def _stop_event(self, _: hikari.StoppingEvent) -> None:
        _logger.log(TRACE_LEVEL, "Shutting down session handler.")
        await self.handler.stop()

        if self._client_session:
            _logger.log(TRACE_LEVEL, "Shutting down client session.")
            await self._client_session.close()

        _logger.log(TRACE_LEVEL, "Successfully shut down ongaku.")

    async def _arc_player_injector(
        self,
        ctx: arc.GatewayContext,
        inj_ctx: arc.InjectorOverridingContext,
    ) -> None:
        _logger.log(TRACE_LEVEL, "Attempting to inject player.")

        if ctx.guild_id is None:
            _logger.log(TRACE_LEVEL, "Player ignored, not in guild.")
            return

        try:
            player = self.get_player(ctx.guild_id)
        except errors.PlayerMissingError:
            _logger.log(TRACE_LEVEL, "Player not found for context.")
            return

        _logger.log(TRACE_LEVEL, "Successfully injected player into context.")

        inj_ctx.set_type_dependency(player_.Player, player)

    def create_session(
        self,
        name: str,
        *,
        ssl: bool = False,
        host: str = "127.0.0.1",
        port: int = 2333,
        password: str = "youshallnotpass",  # noqa: S107
    ) -> session_.Session:
        """Create session.

        Create a new session for the session handler.

        Example
        -------
        ```py
        client = ongaku.Client(...)

        client.add_session(host="192.168.68.69")
        ```

        !!! warning
            The name set must be unique, otherwise an error will be raised.

        Parameters
        ----------
        name
            The name of the session
        ssl
            Whether the server uses `https` or just `http`.
        host
            The host of the lavalink server.
        port
            The port of the lavalink server.
        password
            The password of the lavalink server.

        Raises
        ------
        KeyError
            Raised when a session with the same name is created.

        Returns
        -------
        Session
            The session that was added to the handler.
        """
        new_session = session_.Session(
            self,
            name=name,
            ssl=ssl,
            host=host,
            port=port,
            password=password,
        )

        return self.handler.add_session(session=new_session)

    def get_session(self, name: str) -> session_.Session:
        """Get session.

        Get a session from the session handler.

        Parameters
        ----------
        name
            The name of the session

        Returns
        -------
        Session
            The session that was requested.

        Raises
        ------
        SessionMissingError
            Raised when the session does not exist.
        """
        return self.handler.get_session(name=name)

    async def delete_session(self, name: str) -> None:
        """Delete session.

        Delete a session from the session handler.

        Parameters
        ----------
        name
            The name of the session

        Raises
        ------
        SessionMissingError
            Raised when the session does not exist.
        """
        await self.handler.delete_session(name=name)

    def create_player(
        self,
        guild: hikari.SnowflakeishOr[hikari.Guild],
    ) -> player_.Player:
        """Create player.

        Create a new player to play songs on.

        Example
        -------
        ```py
        client = ongaku.Client(...)

        player = await client.create_player(guild_id)

        await player.connect(channel_id)

        await player.play(track)
        ```

        Parameters
        ----------
        guild
            The `guild`, or `guild id` you wish to create a player for.

        Returns
        -------
        Player
            The player that was created.

        Raises
        ------
        NoSessionsError
            When there is no available sessions.
        """
        try:
            return self.handler.get_player(guild=hikari.Snowflake(guild))
        except errors.PlayerMissingError:
            pass

        session = self.handler.get_session()

        new_player = player_.Player(session, hikari.Snowflake(guild))

        return self.handler.add_player(player=new_player)

    def get_player(
        self,
        guild: hikari.SnowflakeishOr[hikari.Guild],
    ) -> player_.Player:
        """Get player.

        Gets an existing player.

        Example
        -------
        ```py
        client = ongaku.Client(...)
        player = await client.fetch_player(guild_id)

        await player.pause()
        ```

        Parameters
        ----------
        guild
            The `guild`, or `guild id` you wish to fetch the player for.

        Raises
        ------
        PlayerMissingError
            Raised when the player for the specified guild does not exist.
        """
        return self.handler.get_player(guild=guild)

    async def delete_player(
        self,
        guild: hikari.SnowflakeishOr[hikari.Guild],
    ) -> None:
        """Delete player.

        Delete a pre-existing player.

        Example
        -------
        ```py
        client = ongaku.Client(...)
        await client.delete_player(...)
        ```

        Parameters
        ----------
        guild
            The `guild`, or `guild id` you wish to delete the player from.

        Raises
        ------
        PlayerMissingError
            Raised when the player for the specified guild does not exist.
        """
        await self.handler.delete_player(guild=guild)

    def create_extension(
        self,
        extension: Extension | type[Extension],
    ) -> None:
        """Create extension.

        Add a new extension to ongaku.

        Parameters
        ----------
        extension
            The extension to add.
        """
        if isinstance(extension, type):
            extension = extension(self)

        self.injector.set_type_dependency(type(extension), extension)

        self._extensions.add(type(extension))

    def get_extension(self, extension: type[types.ExtensionT]) -> types.ExtensionT:
        """Get extension.

        Get an extension from the client.

        Parameters
        ----------
        extension
            The extension type to receive.

        Raises
        ------
        KeyError
            Raised when the extension could not be found.

        Returns
        -------
        ExtensionT
            The extension.
        """
        return self.injector.get_type_dependency(extension)

    def delete_extension(self, extension: type[Extension]) -> None:
        """Delete extension.

        Deletes an extension previously added.

        Parameters
        ----------
        extension
            The extension to remove.

        Raises
        ------
        KeyError
            Raised when the extension was not found.
        """
        self.injector.remove_type_dependency(extension)

        self._extensions.discard(extension)
