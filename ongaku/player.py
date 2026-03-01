"""
Player.

The player function, for all player related things.
"""

from __future__ import annotations

import random
import typing
import typing as t
from asyncio import TimeoutError
from asyncio import gather

import hikari

from ongaku import errors
from ongaku import events
from ongaku.abc import playlist as playlist_
from ongaku.abc import track as track_
from ongaku.abc.events import TrackEndReasonType
from ongaku.events import PlayerUpdateEvent
from ongaku.events import TrackEndEvent
from ongaku.impl.player import Voice
from ongaku.internal.logger import TRACE_LEVEL
from ongaku.internal.logger import logger

if t.TYPE_CHECKING:
    from ongaku.abc import player as player_
    from ongaku.abc.filters import Filters
    from ongaku.internal.types import RequestorT
    from ongaku.session import Session

_logger = logger.getChild("player")

__all__ = ("Player",)


class Player:
    """
    Base player.

    The class that allows the player, to play songs, and more.

    Parameters
    ----------
    session
        The session that the player is attached too.
    guild
        The Guild the bot is attached too.
    """

    __slots__: typing.Sequence[str] = (
        "_autoplay",
        "_channel_id",
        "_connected",
        "_filters",
        "_guild_id",
        "_is_alive",
        "_is_paused",
        "_loop",
        "_position",
        "_queue",
        "_session",
        "_session_id",
        "_state",
        "_voice",
        "_volume",
    )

    def __init__(
        self,
        session: Session,
        guild: hikari.SnowflakeishOr[hikari.Guild],
    ):
        self._session = session
        self._guild_id = hikari.Snowflake(guild)
        self._channel_id = None
        self._is_alive = False
        self._is_paused = True
        self._voice: player_.Voice | None = None
        self._state: player_.State | None = None
        self._queue: typing.MutableSequence[track_.Track] = []
        self._filters: Filters | None = None
        self._connected: bool = False
        self._session_id: str | None = None
        self._volume: int = -1
        self._autoplay: bool = True
        self._position: int = 0
        self._loop = False

        self.app.event_manager.subscribe(TrackEndEvent, self._track_end_event)
        self.app.event_manager.subscribe(PlayerUpdateEvent, self._player_update_event)

    @property
    def session(self) -> Session:
        """The session this player is included in."""
        return self._session

    @property
    def app(self) -> hikari.GatewayBotAware:
        """The session this player is included in."""
        return self.session.client.app

    @property
    def guild_id(self) -> hikari.Snowflake:
        """The `guild id` this player is attached too."""
        return self._guild_id

    @property
    def channel_id(self) -> hikari.Snowflake | None:
        """The `channel id` this player is attached too.

        `None` if not connected to a channel.
        """
        return self._channel_id

    @property
    def is_alive(self) -> bool:
        """Is alive.

        Whether the player is alive and attached to lavalink.
        """
        return self._is_alive

    @property
    def position(self) -> int:
        """Position.

        The position of the track in milliseconds.
        """
        return self._position

    @property
    def volume(self) -> int:
        """The volume of the player.

        If `-1` the player has not been connected to lavalink and updated.
        """
        return self._volume

    @property
    def is_paused(self) -> bool:
        """Whether the player is currently paused."""
        return self._is_paused

    @property
    def autoplay(self) -> bool:
        """Autoplay.

        Whether or not the next song will play, when this song ends.
        """
        return self._autoplay

    @property
    def loop(self) -> bool:
        """Whether the current track will play again."""
        return self._loop

    @property
    def connected(self) -> bool:
        """Connected.

        Whether or not the player is connected to discords gateway.
        """
        return self._connected

    @property
    def queue(self) -> t.Sequence[track_.Track]:
        """The current queue of tracks."""
        return self._queue

    @property
    def voice(self) -> player_.Voice | None:
        """The player's voice state."""
        return self._voice

    @property
    def state(self) -> player_.State | None:
        """The player's player state."""
        return self._state

    @property
    def filters(self) -> Filters | None:
        """Filters for the player."""
        return self._filters

    async def connect(
        self,
        channel: hikari.SnowflakeishOr[hikari.GuildVoiceChannel],
        *,
        mute: bool = False,
        deaf: bool = True,
    ) -> None:
        """Connect.

        Connect the current player to a voice channel.

        Example
        -------
        ```py
        await player.connect(channel_id)
        ```

        Parameters
        ----------
        channel
            The channel (or channel id) that you wish to connect the bot to.
        mute
            Whether or not to mute the player.
        deaf
            Whether or not to deafen the player.

        Raises
        ------
        SessionStartError
            Raised when the players session has not yet been started.
        PlayerConnectError
            Raised when the voice state of the bot cannot be updated, or the voice events required could not be received.
        RestEmptyError
            Raised when a return type was requested, yet nothing was received.
        RestStatusError
            Raised when nothing was received, but a 4XX/5XX error was reported.
        RestRequestError
            Raised when a rest error is returned with a 4XX/5XX error.
        BuildError
            Raised when a construction of a ABC class fails.
        """
        session = self.session._get_session_id()

        _logger.log(
            TRACE_LEVEL,
            f"Attempting connection to voice channel: {hikari.Snowflake(channel)} in guild: {self.guild_id}",
        )

        self._channel_id = hikari.Snowflake(channel)

        try:
            await self.app.update_voice_state(
                self.guild_id,
                self._channel_id,
                self_mute=mute,
                self_deaf=deaf,
            )
        except Exception as e:
            raise errors.PlayerConnectError(str(e))

        _logger.log(
            TRACE_LEVEL,
            f"waiting for voice events for channel: {self.channel_id} in guild: {self.guild_id}",
        )

        try:
            state_event, server_event = await gather(
                self.app.event_manager.wait_for(
                    hikari.VoiceStateUpdateEvent,
                    timeout=5,
                ),
                self.app.event_manager.wait_for(
                    hikari.VoiceServerUpdateEvent,
                    timeout=5,
                ),
            )
        except TimeoutError:
            raise errors.PlayerConnectError(
                f"Could not connect to voice channel {self.channel_id} in {self.guild_id} due to events not being received.",
            )

        if server_event.raw_endpoint is None:
            raise errors.PlayerConnectError(
                f"Endpoint missing for attempted server connection for voice channel {self.channel_id} in {self.guild_id}",
            )

        _logger.log(
            TRACE_LEVEL,
            f"Successfully received events for channel: {self.channel_id} in guild: {self.guild_id}",
        )

        new_voice = Voice(
            token=server_event.token,
            endpoint=server_event.raw_endpoint,
            session_id=state_event.state.session_id,
            channel_id=self.channel_id,
        )

        self._voice = new_voice

        player = await self.session.client.rest.update_player(
            session,
            self.guild_id,
            voice=new_voice,
            no_replace=False,
            session=self.session,
        )

        self._is_alive = True

        _logger.log(
            TRACE_LEVEL,
            f"Successfully connected, and sent data to lavalink for channel: {self.channel_id} in guild: {self.guild_id}",
        )

        self._update(player)

    async def disconnect(self) -> None:
        """
        Disconnect.

        Disconnect the player from the discord channel, and stop the currently playing track.

        Example
        -------
        ```py
        await player.disconnect()
        ```

        Raises
        ------
        SessionStartError
            Raised when the players session has not yet been started.
        RestEmptyError
            Raised when a return type was requested, yet nothing was received.
        RestStatusError
            Raised when nothing was received, but a 4XX/5XX error was reported.
        RestRequestError
            Raised when a rest error is returned with a 4XX/5XX error.
        BuildError
            Raised when a construction of a ABC class fails.
        """
        session = self.session._get_session_id()

        await self.clear()

        _logger.log(
            TRACE_LEVEL,
            f"Attempting to delete player for channel: {self.channel_id} in guild: {self.guild_id}",
        )

        await self.session.client.rest.delete_player(
            session,
            self._guild_id,
            session=self.session,
        )

        _logger.log(
            TRACE_LEVEL,
            f"Successfully deleted player for channel: {self.channel_id} in guild: {self.guild_id}",
        )

        self._is_alive = False

        _logger.log(
            TRACE_LEVEL,
            f"Updating voice state for channel: {self.channel_id} in guild: {self.guild_id}",
        )

        await self.app.update_voice_state(self.guild_id, None)

        _logger.log(
            TRACE_LEVEL,
            f"Successfully updated voice state for channel: {self.channel_id} in guild: {self.guild_id}",
        )

    async def play(
        self,
        track: track_.Track | None = None,
        requestor: RequestorT | None = None,
    ) -> None:
        """Play.

        Play a new track, or start the playing of the queue.

        Example
        -------
        ```py
        await player.play(track)
        ```

        Parameters
        ----------
        track
            The track you wish to play. If none, pulls from the queue.
        requestor
            The member who requested the track.

        Raises
        ------
        SessionStartError
            Raised when the players session has not yet been started.
        PlayerConnectError
            Raised when the player is not connected to a channel.
        RestEmptyError
            Raised when a return type was requested, yet nothing was received.
        RestStatusError
            Raised when nothing was received, but a 4XX/5XX error was reported.
        RestRequestError
            Raised when a rest error is returned with a 4XX/5XX error.
        BuildError
            Raised when a construction of a ABC class fails.
        """
        session = self.session._get_session_id()

        if self.channel_id is None:
            raise errors.PlayerConnectError("Not connected to a channel.")

        if len(self.queue) == 0 and track is None:
            raise errors.PlayerQueueError("Queue is empty.")

        if track:
            if requestor:
                track._requestor = hikari.Snowflake(requestor)

            self._queue.insert(0, track)

        player = await self.session.client.rest.update_player(
            session,
            self.guild_id,
            track=self.queue[0],
            no_replace=False,
            session=self.session,
        )

        self._is_paused = False

        self._update(player)

    def add(
        self,
        tracks: t.Sequence[track_.Track] | playlist_.Playlist | track_.Track,
        requestor: RequestorT | None = None,
    ) -> None:
        """
        Add tracks.

        Add tracks to the queue.

        !!! note
            This will not automatically start playing the songs.
            please call `.play()` after, with no track, if the player is not already playing.

        Example
        -------
        ```py
        await player.add(tracks)
        ```

        Parameters
        ----------
        tracks
            The list of tracks or a singular track you wish to add to the queue.
        requestor
            The user/member who requested the song.
        """
        new_requestor = None

        if requestor:
            new_requestor = hikari.Snowflake(requestor)

        track_count = 0

        if isinstance(tracks, track_.Track):
            if new_requestor:
                tracks._requestor = new_requestor
            self._queue.append(tracks)
            track_count = 1
            return

        if isinstance(tracks, playlist_.Playlist):
            tracks = tracks.tracks

        for track in tracks:
            if new_requestor:
                track._requestor = new_requestor
            self._queue.append(track)
            track_count += 1

        _logger.log(
            TRACE_LEVEL,
            f"Successfully added {track_count} track(s) to {self.guild_id}",
        )

    async def pause(self, value: bool | None = None) -> None:
        """
        Pause the player.

        Allows for the user to pause the currently playing track on this player.

        !!! info
            `True` will force pause the player, `False` will force unpause the player. Leaving it empty, will toggle it from its current state.

        Example
        -------
        ```py
        await player.pause()
        ```

        Parameters
        ----------
        value
            How you wish to pause the bot.

        Raises
        ------
        SessionStartError
            Raised when the players session has not yet been started.
        RestEmptyError
            Raised when a return type was requested, yet nothing was received.
        RestStatusError
            Raised when nothing was received, but a 4XX/5XX error was reported.
        RestRequestError
            Raised when a rest error is returned with a 4XX/5XX error.
        BuildError
            Raised when a construction of a ABC class fails.
        """
        session = self.session._get_session_id()

        if value:
            self._is_paused = value
        else:
            self._is_paused = not self.is_paused

        player = await self.session.client.rest.update_player(
            session,
            self.guild_id,
            paused=self.is_paused,
            session=self.session,
        )

        _logger.log(
            TRACE_LEVEL,
            f"Successfully set paused state to {self.is_paused} in guild {self.guild_id}",
        )

        self._update(player)

    async def stop(self) -> None:
        """
        Stop current track.

        Stops the audio, by setting the song to none.

        !!! note
            This does not touch the current queue, just clears the player of its track.

        Example
        -------
        ```py
        await player.stop()
        ```

        Raises
        ------
        SessionStartError
            Raised when the players session has not yet been started.
        RestEmptyError
            Raised when a return type was requested, yet nothing was received.
        RestStatusError
            Raised when nothing was received, but a 4XX/5XX error was reported.
        RestRequestError
            Raised when a rest error is returned with a 4XX/5XX error.
        BuildError
            Raised when a construction of a ABC class fails.
        """
        session = self.session._get_session_id()

        player = await self.session.client.rest.update_player(
            session,
            self.guild_id,
            track=None,
            no_replace=False,
            session=self.session,
        )

        self._is_paused = True

        _logger.log(TRACE_LEVEL, f"Successfully stopped track in guild {self.guild_id}")

        self._update(player)

    def shuffle(self) -> None:
        """Shuffle.

        Shuffle the current queue.

        !!! note
            This will not touch the first track.

        Raises
        ------
        PlayerQueueError
            Raised when the queue has 2 or less tracks in it.
        """
        if len(self.queue) <= 2:
            raise errors.PlayerQueueError(
                "Queue must have more than 2 tracks to shuffle.",
            )

        new_queue = list(self.queue)

        first_track = new_queue.pop(0)

        random.shuffle(new_queue)

        new_queue.insert(0, first_track)

        self._queue = new_queue

        _logger.log(
            TRACE_LEVEL,
            f"Successfully shuffled queue in guild {self.guild_id}",
        )

    async def skip(self, amount: int = 1) -> None:
        """
        Skip songs.

        skip a selected amount of songs in the queue.

        Example
        -------
        ```py
        await player.skip()
        ```

        Parameters
        ----------
        amount
            The amount of songs you wish to skip.

        Raises
        ------
        SessionStartError
            Raised when the players session has not yet been started.
        ValueError
            Raised when the amount set is 0 or negative.
        PlayerQueueError
            Raised when the queue is empty.
        RestEmptyError
            Raised when a return type was requested, yet nothing was received.
        RestStatusError
            Raised when nothing was received, but a 4XX/5XX error was reported.
        RestRequestError
            Raised when a rest error is returned with a 4XX/5XX error.
        BuildError
            Raised when a construction of a ABC class fails.
        """
        if amount <= 0:
            raise ValueError(f"Skip amount cannot be 0 or negative. Value: {amount}")
        if len(self.queue) == 0:
            raise errors.PlayerQueueError("Queue is empty.")

        removed_tracks = 0
        for _ in range(amount):
            if len(self._queue) == 0:
                break
            self._queue.pop(0)
            removed_tracks += 1

        _logger.log(
            TRACE_LEVEL,
            f"Successfully removed {removed_tracks} track(s) out of {amount} in guild {self.guild_id}",
        )

        session = self.session._get_session_id()

        if len(self.queue) <= 0:
            player = await self.session.client.rest.update_player(
                session,
                self.guild_id,
                track=None,
                no_replace=False,
                session=self.session,
            )

            self._update(player)
        else:
            player = await self.session.client.rest.update_player(
                session,
                self.guild_id,
                track=self.queue[0],
                no_replace=False,
                session=self.session,
            )

            self._update(player)

        _logger.log(TRACE_LEVEL, f"Successfully skipped track in {self.guild_id}")

    def remove(self, value: track_.Track | int) -> None:
        """
        Remove track.

        Removes the track, or the track in that position.

        !!! warning
            This does not stop the track if its in the first position.

        Example
        -------
        ```py
        await player.remove()
        ```

        Parameters
        ----------
        value
            Remove a selected track. If [Track][ongaku.abc.track.Track], then it will remove the first occurrence of that track. If an integer, it will remove the track at that position.

        Raises
        ------
        PlayerQueueError
            Raised when the removal of a track fails.
        """
        if len(self.queue) == 0:
            raise errors.PlayerQueueError("Queue is empty.")

        try:
            index = (
                self._queue.index(value) if isinstance(value, track_.Track) else value
            )
        except ValueError:
            if isinstance(value, track_.Track):
                raise errors.PlayerQueueError(
                    f"Failed to remove song: {value.info.title}",
                )
            raise errors.PlayerQueueError(
                f"Failed to remove song in position {value}",
            )

        try:
            self._queue.pop(index)
        except IndexError:
            if isinstance(value, track_.Track):
                raise errors.PlayerQueueError(
                    f"Failed to remove song: {value.info.title}",
                )
            raise errors.PlayerQueueError(
                f"Failed to remove song in position {value}",
            )

        _logger.log(TRACE_LEVEL, f"Successfully removed track in {self.guild_id}")

    async def clear(self) -> None:
        """
        Clear the queue.

        Clear the current queue, and also stop the audio from the player.

        Example
        -------
        ```py
        player.clear()
        ```

        Raises
        ------
        SessionStartError
            Raised when the players session has not yet been started.
        RestEmptyError
            Raised when a return type was requested, yet nothing was received.
        RestStatusError
            Raised when nothing was received, but a 4XX/5XX error was reported.
        RestRequestError
            Raised when a rest error is returned with a 4XX/5XX error.
        BuildError
            Raised when a construction of a ABC class fails.
        """
        self._queue.clear()

        session = self.session._get_session_id()

        player = await self.session.client.rest.update_player(
            session,
            self.guild_id,
            track=None,
            no_replace=False,
            session=self.session,
        )

        self._update(player)

        _logger.log(TRACE_LEVEL, f"Successfully cleared queue in {self.guild_id}")

    def set_autoplay(self, enable: bool | None = None) -> bool:
        """
        Set autoplay.

        whether to enable or disable autoplay.

        Example
        -------
        ```py
        await player.set_autoplay()
        ```

        Parameters
        ----------
        enable
            Whether or not to enable autoplay. If left empty, it will toggle the current status.
        """
        if enable:
            self._autoplay = enable
            return self._autoplay

        self._autoplay = not self._autoplay

        return self._autoplay

    async def set_volume(self, volume: int = 100) -> None:
        """
        Set the volume.

        The volume you wish to set for the player.

        Example
        -------
        ```py
        await player.set_volume(10)
        ```

        !!! note
            If you don't set a value to volume, it will simply become 100 (The default.)

        Parameters
        ----------
        volume
            The volume you wish to set, from 0 to 1000.

        Raises
        ------
        SessionStartError
            Raised when the players session has not yet been started.
        ValueError
            Raised when the value is below 0, or above 1000.
        RestEmptyError
            Raised when a return type was requested, yet nothing was received.
        RestStatusError
            Raised when nothing was received, but a 4XX/5XX error was reported.
        RestRequestError
            Raised when a rest error is returned with a 4XX/5XX error.
        BuildError
            Raised when a construction of a ABC class fails.
        """
        session = self.session._get_session_id()

        if volume:
            if volume < 0:
                raise ValueError(f"Volume cannot be below zero. Volume: {volume}")
            if volume > 1000:
                raise ValueError(f"Volume cannot be above 1000. Volume: {volume}")

        player = await self.session.client.rest.update_player(
            session,
            self.guild_id,
            volume=volume,
            no_replace=False,
            session=self.session,
        )

        self._update(player)

        _logger.log(
            TRACE_LEVEL,
            f"Successfully set volume to {volume} in {self.guild_id}",
        )

    async def set_position(self, value: int) -> None:
        """
        Set the position.

        Change the currently playing track's position.

        Example
        -------
        ```py
        await player.set_position(10000)
        ```

        Parameters
        ----------
        value
            The value, of the position, in milliseconds.

        Raises
        ------
        SessionStartError
            Raised when the players session has not yet been started.
        ValueError
            Raised when the position given is negative, or the current tracks length is greater than the length given.
        PlayerQueueError
            Raised when the queue is empty.
        RestEmptyError
            Raised when a return type was requested, yet nothing was received.
        RestStatusError
            Raised when nothing was received, but a 4XX/5XX error was reported.
        RestRequestError
            Raised when a rest error is returned with a 4XX/5XX error.
        BuildError
            Raised when a construction of a ABC class fails.
        """
        session = self.session._get_session_id()

        if value <= 0:
            raise ValueError("Negative value is not allowed.")

        if len(self.queue) <= 0:
            raise errors.PlayerQueueError("Queue is empty.")

        if self.queue[0].info.length < value:
            raise ValueError(
                "A value greater than the current tracks length is not allowed.",
            )

        player = await self.session.client.rest.update_player(
            session,
            self.guild_id,
            position=value,
            no_replace=False,
            session=self.session,
        )

        self._update(player)

        _logger.log(
            TRACE_LEVEL,
            f"Successfully set position ({value}) to track in {self.guild_id}",
        )

    async def set_filters(self, filters: Filters | None = None) -> None:
        """Set Filters.

        Set a new filter for the player.

        Parameters
        ----------
        filters
            The filter to set the player with.
        """
        session = self.session._get_session_id()

        player = await self.session.client.rest.update_player(
            session,
            self.guild_id,
            filters=filters,
            session=self.session,
        )

        _logger.log(
            TRACE_LEVEL,
            f"Successfully updated filters in guild {self.guild_id}",
        )

        self._update(player)

    def set_loop(self, enable: bool | None = None) -> bool:
        """
        Set loop.

        whether to enable or disable looping of the current track.

        Example
        -------
        ```py
        await player.set_loop()
        ```

        Parameters
        ----------
        enable
            Whether or not to enable looping. If left empty, it will toggle the current status.
        """
        if enable:
            self._loop = enable
            return self._loop

        self._loop = not self._loop

        return self._loop

    async def transfer(self, session: Session) -> Player:
        """Transfer.

        Transfer this player to another session.

        !!! warning
            This will kill the current player, and return a new player.

        Parameters
        ----------
        session
            The session you wish to add the new player to.

        Returns
        -------
        Player
            The new player.
        """
        _logger.log(
            TRACE_LEVEL,
            f"Attempting to transfer player in {self.guild_id} from session ({self.session.name}) to session ({session.name})",
        )

        new_player = Player(session, self.guild_id)

        new_player.add(self.queue)

        if self.connected and self.channel_id:
            await self.disconnect()

            await new_player.connect(self.channel_id)
            if self.is_paused is False:
                await new_player.play()
                await new_player.set_position(self.position)

        _logger.log(
            TRACE_LEVEL,
            f"Successfully transferred player in {self.guild_id} from session ({self.session.name}) to session ({session.name})",
        )

        return new_player

    def _update(self, player: player_.Player) -> None:
        _logger.log(
            TRACE_LEVEL,
            f"Updating player for channel: {self.channel_id} in guild: {self.guild_id}",
        )

        self._volume = player.volume
        self._is_paused = player.is_paused
        self._state = player.state
        self._voice = player.voice
        self._filters = player.filters
        self._connected = player.state.connected

    async def _track_end_event(self, event: TrackEndEvent) -> None:
        self.session._get_session_id()

        if event.guild_id != self.guild_id:
            return

        if not self.autoplay:
            return

        if (
            event.reason != TrackEndReasonType.FINISHED
            and event.reason != TrackEndReasonType.LOADFAILED
        ):
            return

        _logger.log(
            TRACE_LEVEL,
            f"Auto-playing track for channel: {self.channel_id} in guild: {self.guild_id}",
        )

        if len(self.queue) == 0:
            _logger.log(
                TRACE_LEVEL,
                f"queue is empty for channel: {self.channel_id} in guild: {self.guild_id}. Skipping.",
            )
            return

        if len(self.queue) == 1 and not self.loop:
            _logger.log(
                TRACE_LEVEL,
                f"queue is empty for channel: {self.channel_id} in guild: {self.guild_id}. Dispatching last known track.",
            )
            new_event = events.QueueEmptyEvent.from_session(
                self.session,
                guild_id=self.guild_id,
                old_track=self.queue[0],
            )

            self.remove(0)

            self.app.event_manager.dispatch(new_event, return_tasks=False)

            return

        if not self.loop:
            _logger.log(
                TRACE_LEVEL,
                f"Autoplay for channel: {self.channel_id} in guild: {self.guild_id}. Removing old song.",
            )
            self.remove(0)

        _logger.log(
            TRACE_LEVEL,
            f"Auto-playing next track for channel: {self.channel_id} in guild: {self.guild_id}. Track title: {self.queue[0].info.title}",
        )

        await self.play()

        self.app.event_manager.dispatch(
            events.QueueNextEvent.from_session(
                self.session,
                self.guild_id,
                self._queue[0],
                event.track,
            ),
            return_tasks=False,
        )

        _logger.log(
            TRACE_LEVEL,
            f"Auto-playing successfully completed for channel: {self.channel_id} in guild: {self.guild_id}",
        )

    async def _player_update_event(self, event: PlayerUpdateEvent) -> None:
        if event.guild_id != self.guild_id:
            return

        _logger.log(
            TRACE_LEVEL,
            f"Updating player state in {self.guild_id}",
        )

        if not event.state.connected and self.connected:
            await self.stop()

        _logger.log(
            TRACE_LEVEL,
            f"Successfully updated player state in {self.guild_id}",
        )

        self._state = event.state
        self._connected = event.state.connected


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
