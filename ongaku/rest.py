"""
Rest client.

All REST based actions, happen in here.
"""

from __future__ import annotations

import typing

import hikari

from ongaku import errors
from ongaku.internal import routes
from ongaku.internal.logger import TRACE_LEVEL
from ongaku.internal.logger import logger

if typing.TYPE_CHECKING:
    from ongaku.abc import session as session_
    from ongaku.abc.filters import Filters
    from ongaku.abc.info import Info
    from ongaku.abc.player import Player
    from ongaku.abc.player import Voice
    from ongaku.abc.playlist import Playlist
    from ongaku.abc.routeplanner import RoutePlannerStatus
    from ongaku.abc.statistics import Statistics
    from ongaku.abc.track import Track
    from ongaku.session import Session

_logger = logger.getChild("rest")

if typing.TYPE_CHECKING:
    from ongaku.client import Client


__all__ = ("RESTClient",)


class RESTClient:
    """
    Base REST Client.

    The base REST client, for all rest related actions.

    !!! warning
        Please do not create this on your own. Please use the rest attribute, in the base client object you created.
    """

    __slots__: typing.Sequence[str] = "_client"

    def __init__(self, client: Client) -> None:
        self._client = client

    async def load_track(  # noqa: C901
        self,
        query: str,
        *,
        session: Session | None = None,
    ) -> Playlist | typing.Sequence[Track] | Track | None:
        """
        Load tracks.

        Loads tracks from a site, a playlist or a track, to play on a player.

        ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#track-loading)

        Example
        -------
        ```py
        track = await client.rest.load_track("ytsearch:ajr")

        await player.play(track)
        ```

        Parameters
        ----------
        query
            The query for the search/link.
        session
            If provided, the session to use for this request.

        Raises
        ------
        NoSessionsError
            Raised when there is no available sessions for this request to take place.
        TimeoutError
            Raised when the request takes too long to respond.
        RestEmptyError
            Raised when the request required a return type, but received nothing, or a 204 response.
        RestStatusError
            Raised when a 4XX or a 5XX status is received.
        BuildError
            Raised when the track, playlist or search could not be built.
        RestRequestError
            Raised when a 4XX or a 5XX status is received, and lavalink gives more information.
        RestError
            Raised when an unknown error is caught.

        Returns
        -------
        typing.Sequence[Track]
            A sequence of tracks (a search result)
        Playlist
            A Playlist object.
        Track
            A Track object.
        None
            No result was returned.
        """
        route = routes.GET_LOAD_TRACKS

        _logger.log(TRACE_LEVEL, str(route))

        if not session:
            session = self._client.session_handler.fetch_session()

        response = await session.request(
            route.method,
            route.path,
            dict,
            params={"identifier": query},
        )

        if response is None:
            raise ValueError("Response is required for this request.")

        load_type: str = response["loadType"]

        if load_type == "empty":
            _logger.log(TRACE_LEVEL, "loadType is empty.")
            return None

        if load_type == "error":
            _logger.log(TRACE_LEVEL, "loadType caused an error.")

            raise errors.RestExceptionError.from_error(
                self._client.entity_builder.build_exception_error(response["data"]),
            )

        if load_type == "search":
            _logger.log(TRACE_LEVEL, "loadType was a search result.")
            tracks: typing.Sequence[Track] = []
            for track in response["data"]:
                try:
                    tracks.append(self._client.entity_builder.build_track(track))
                except Exception as e:
                    raise errors.BuildError(e)

            build = tracks

        elif load_type == "track":
            _logger.log(TRACE_LEVEL, "loadType was a track link.")
            try:
                build = self._client.entity_builder.build_track(response["data"])
            except Exception as e:
                raise errors.BuildError(e)

        elif load_type == "playlist":
            _logger.log(TRACE_LEVEL, "loadType was a playlist link.")
            try:
                build = self._client.entity_builder.build_playlist(response["data"])
            except Exception as e:
                raise errors.BuildError(e)

        else:
            raise errors.BuildError(
                None,
                f"An unknown loadType was received: {load_type}",
            )

        return build

    async def decode_track(
        self,
        track: str,
        *,
        session: Session | None = None,
    ) -> Track:
        """
        Decode a track.

        Decode a track from its encoded state.

        ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#track-decoding)

        Example
        -------
        ```py
        track = await client.rest.decode_track(BASE64)

        await player.play(track)
        ```

        Parameters
        ----------
        track
            The BASE64 code, from a previously encoded track.
        session
            If provided, the session to use for this request.

        Raises
        ------
        NoSessionsError
            Raised when there is no available sessions for this request to take place.
        TimeoutError
            Raised when the request takes too long to respond.
        RestEmptyError
            Raised when the request required a return type, but received nothing, or a 204 response.
        RestStatusError
            Raised when a 4XX or a 5XX status is received.
        BuildError
            Raised when the track could not be built
        RestRequestError
            Raised when a 4XX or a 5XX status is received, and lavalink gives more information.
        RestError
            Raised when an unknown error is caught.

        Returns
        -------
        Track
            The Track object.
        """
        route = routes.GET_DECODE_TRACK

        _logger.log(TRACE_LEVEL, str(route))

        if not session:
            session = self._client.session_handler.fetch_session()

        response = await session.request(
            route.method,
            route.path,
            dict,
            params={"encodedTrack": track},
        )

        if response is None:
            raise ValueError("Response is required for this request.")

        try:
            return self._client.entity_builder.build_track(response)
        except Exception as e:
            raise errors.BuildError(e)

    async def decode_tracks(
        self,
        tracks: typing.Sequence[str],
        *,
        session: Session | None = None,
    ) -> typing.Sequence[Track]:
        """
        Decode tracks.

        Decode multiple tracks from their encoded state.

        ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#track-decoding)

        Example
        -------
        ```py
        tracks = await client.rest.decode_tracks([BASE64_1, BASE64_2])

        await player.add(tracks)
        ```

        Parameters
        ----------
        tracks
            The BASE64 codes, from all the previously encoded tracks.
        session
            If provided, the session to use for this request.

        Raises
        ------
        NoSessionsError
            Raised when there is no available sessions for this request to take place.
        TimeoutError
            Raised when the request takes too long to respond.
        RestEmptyError
            Raised when the request required a return type, but received nothing, or a 204 response.
        RestStatusError
            Raised when a 4XX or a 5XX status is received.
        BuildError
            Raised when the tracks could not be built.
        RestRequestError
            Raised when a 4XX or a 5XX status is received, and lavalink gives more information.
        RestError
            Raised when an unknown error is caught.

        Returns
        -------
        typing.Sequence[Track]
            The Track object.
        """
        route = routes.POST_DECODE_TRACKS

        _logger.log(TRACE_LEVEL, str(route))

        if not session:
            session = self._client.session_handler.fetch_session()

        response = await session.request(
            route.method,
            route.path,
            list,
            headers={"Content-Type": "application/json"},
            json=tracks,
        )

        if response is None:
            raise ValueError("Response is required for this request.")

        new_tracks: list[Track] = []

        for track in response:
            try:
                new_tracks.append(self._client.entity_builder.build_track(track))
            except Exception as e:
                raise errors.BuildError(e)

        return new_tracks

    async def fetch_players(
        self,
        session_id: str,
        *,
        session: Session | None = None,
    ) -> typing.Sequence[Player]:
        """
        Fetch all players.

        Fetches all players on this session.

        ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#get-players)

        Example
        -------
        ```py
        players = await client.rest.fetch_players(session_id)

        for player in players:
            print(player.guild_id)
        ```

        Parameters
        ----------
        session_id
            The Session ID that the players are attached too.
        session
            If provided, the session to use for this request.

        Raises
        ------
        NoSessionsError
            Raised when there is no available sessions for this request to take place.
        TimeoutError
            Raised when the request takes too long to respond.
        RestEmptyError
            Raised when the request required a return type, but received nothing, or a 204 response.
        RestStatusError
            Raised when a 4XX or a 5XX status is received.
        BuildError
            Raised when the players could not be built.
        RestRequestError
            Raised when a 4XX or a 5XX status is received, and lavalink gives more information.
        RestError
            Raised when an unknown error is caught.

        Returns
        -------
        typing.Sequence[Player]
            The Sequence of player objects.
        """
        route = routes.GET_PLAYERS

        _logger.log(TRACE_LEVEL, str(route))

        if not session:
            session = self._client.session_handler.fetch_session()

        response = await session.request(
            route.method,
            route.path.format(session_id=session_id),
            list,
        )

        if response is None:
            raise ValueError("Response is required for this request.")

        players: list[Player] = []

        for player in response:
            players.append(self._client.entity_builder.build_player(player))

        return players

    async def fetch_player(
        self,
        session_id: str,
        guild: hikari.SnowflakeishOr[hikari.Guild],
        *,
        session: Session | None = None,
    ) -> Player:
        """
        Fetch a player.

        Fetches a specific player from this session.

        ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#get-player)

        Example
        -------
        ```py
        player = await client.rest.fetch_player(session_id, guild_id)

        print(player.volume)
        ```

        Parameters
        ----------
        session_id
            The Session ID that the players are attached too.
        guild
            The `guild` or `guild id` that the player is attached to.
        session
            If provided, the session to use for this request.

        Raises
        ------
        NoSessionsError
            Raised when there is no available sessions for this request to take place.
        TimeoutError
            Raised when the request takes too long to respond.
        RestEmptyError
            Raised when the request required a return type, but received nothing, or a 204 response.
        RestStatusError
            Raised when a 4XX or a 5XX status is received.
        BuildError
            Raised when the player could not be built.
        RestRequestError
            Raised when a 4XX or a 5XX status is received, and lavalink gives more information.
        RestError
            Raised when an unknown error is caught.

        Returns
        -------
        Player
            The player object.
        """
        route = routes.GET_PLAYER

        _logger.log(TRACE_LEVEL, str(route))

        if not session:
            session = self._client.session_handler.fetch_session()

        response = await session.request(
            route.method,
            route.path.format(session_id=session_id, guild_id=hikari.Snowflake(guild)),
            dict,
        )

        if response is None:
            raise ValueError("Response is required for this request.")

        return self._client.entity_builder.build_player(response)

    async def update_player(  # noqa: C901
        self,
        session_id: str,
        guild: hikari.SnowflakeishOr[hikari.Guild],
        *,
        track: hikari.UndefinedNoneOr[Track] = hikari.UNDEFINED,
        position: hikari.UndefinedOr[int] = hikari.UNDEFINED,
        end_time: hikari.UndefinedOr[int] = hikari.UNDEFINED,
        volume: hikari.UndefinedOr[int] = hikari.UNDEFINED,
        paused: hikari.UndefinedOr[bool] = hikari.UNDEFINED,
        filters: hikari.UndefinedNoneOr[Filters] = hikari.UNDEFINED,
        voice: hikari.UndefinedOr[Voice] = hikari.UNDEFINED,
        no_replace: bool = True,
        session: Session | None = None,
    ) -> Player:
        """
        Fetch a player.

        Fetches a specific player from this session.

        ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#update-player)

        !!! tip
            Setting any value (except for `session_id`, or `guild_id`) to None, will set their values to None.
            To not modify them, do not set them to anything.

        !!! warning
            If you do not set any value (not including `session_id` or `guild_id` as they are required) you will receive a `ValueError`

        Example
        -------
        ```py
        await client.rest.update_player(session_id, guild_id, paused=True)
        ```

        Parameters
        ----------
        session_id
            The Session ID that the players are attached too.
        guild
            The `guild` or `guild id` that the player is attached to.
        track
            The track you wish to set, or remove
        position
            The new position for the track.
        end_time
            The end time for the track.
        volume
            The volume of the player.
        paused
            Whether or not to pause the player.
        filters
            The filters to apply to the player.
        voice
            The player voice object you wish to set.
        no_replace
            Whether or not the track can be replaced.
        session
            If provided, the session to use for this request.

        Raises
        ------
        ValueError
            Raised when nothing new has been set.
        NoSessionsError
            Raised when there is no available sessions for this request to take place.
        TimeoutError
            Raised when the request takes too long to respond.
        RestEmptyError
            Raised when the request required a return type, but received nothing, or a 204 response.
        RestStatusError
            Raised when a 4XX or a 5XX status is received.
        BuildError
            Raised when the track, playlist or search could not be built.
        RestRequestError
            Raised when a 4XX or a 5XX status is received, and lavalink gives more information.
        RestError
            Raised when an unknown error is caught.

        Returns
        -------
        Player
            The player object.
        """
        if (
            track is hikari.UNDEFINED
            and position is hikari.UNDEFINED
            and end_time is hikari.UNDEFINED
            and volume is hikari.UNDEFINED
            and paused is hikari.UNDEFINED
            and filters is hikari.UNDEFINED
            and voice is hikari.UNDEFINED
        ):
            raise ValueError("Update requires at least one change.")

        patch_data: typing.MutableMapping[str, typing.Any] = {}

        if track != hikari.UNDEFINED:
            if track is None:
                patch_data.update(
                    {
                        "track": {
                            "encoded": None,
                        },
                    },
                )
            else:
                track_data: typing.MutableMapping[str, typing.Any] = {
                    "encoded": track.encoded,
                }

                user_data = dict(track.user_data)

                if track.requestor:
                    user_data.update({"ongaku_requestor": str(track.requestor)})

                track_data.update({"userData": user_data})

                patch_data.update({"track": track_data})

        if position != hikari.UNDEFINED:
            patch_data.update({"position": position})

        if end_time != hikari.UNDEFINED:
            patch_data.update({"endTime": end_time})

        if volume != hikari.UNDEFINED:
            patch_data.update({"volume": volume})

        if paused != hikari.UNDEFINED:
            patch_data.update({"paused": paused})

        if filters != hikari.UNDEFINED:
            if filters is None:
                patch_data.update({"filters": None})
            else:
                filters_payload: typing.MutableMapping[str, typing.Any] = {}

                print(filters.plugin_filters)
                if len(filters.plugin_filters.items()) > 0:
                    filters_payload.update({"pluginFilters": filters.plugin_filters})

                if filters.volume is not None:
                    filters_payload.update({"volume": filters.volume})

                if filters.equalizer and len(filters.equalizer) > 0:
                    equalizer_list: typing.MutableSequence[typing.Any] = []
                    for eq in filters.equalizer:
                        equalizer_list.append({"band": eq.band.value, "gain": eq.gain})

                    filters_payload.update({"equalizer": equalizer_list})

                if filters.karaoke:
                    karaoke_payload: typing.MutableMapping[str, typing.Any] = {}
                    if filters.karaoke.level:
                        karaoke_payload.update({"level": filters.karaoke.level})
                    if filters.karaoke.mono_level is not None:
                        karaoke_payload.update(
                            {"monoLevel": filters.karaoke.mono_level},
                        )
                    if filters.karaoke.filter_band is not None:
                        karaoke_payload.update(
                            {"filterBand": filters.karaoke.filter_band},
                        )
                    if filters.karaoke.filter_width is not None:
                        karaoke_payload.update(
                            {"filterWidth": filters.karaoke.filter_width},
                        )

                    if len(karaoke_payload.items()) > 0:
                        filters_payload.update({"karaoke": karaoke_payload})

                if filters.timescale:
                    timescale_payload: typing.MutableMapping[str, typing.Any] = {}
                    if filters.timescale.speed is not None:
                        timescale_payload.update({"speed": filters.timescale.speed})
                    if filters.timescale.pitch is not None:
                        timescale_payload.update({"pitch": filters.timescale.pitch})
                    if filters.timescale.rate is not None:
                        timescale_payload.update({"rate": filters.timescale.rate})

                    if len(timescale_payload.items()) > 0:
                        filters_payload.update({"timescale": timescale_payload})

                if filters.tremolo:
                    tremolo_payload: typing.MutableMapping[str, typing.Any] = {}
                    if filters.tremolo.frequency is not None:
                        tremolo_payload.update({"frequency": filters.tremolo.frequency})
                    if filters.tremolo.depth is not None:
                        tremolo_payload.update({"depth": filters.tremolo.depth})

                    if len(tremolo_payload.items()) > 0:
                        filters_payload.update({"tremolo": tremolo_payload})

                if filters.vibrato:
                    vibrato_payload: typing.MutableMapping[str, typing.Any] = {}
                    if filters.vibrato.frequency is not None:
                        vibrato_payload.update({"frequency": filters.vibrato.frequency})
                    if filters.vibrato.depth is not None:
                        vibrato_payload.update({"depth": filters.vibrato.depth})

                    if len(vibrato_payload.items()) > 0:
                        filters_payload.update({"vibrato": vibrato_payload})

                if filters.rotation:
                    rotation_payload: typing.MutableMapping[str, typing.Any] = {}
                    if filters.rotation.rotation_hz is not None:
                        rotation_payload.update(
                            {"rotationHz": filters.rotation.rotation_hz},
                        )

                    if len(rotation_payload.items()) > 0:
                        filters_payload.update({"rotation": rotation_payload})

                if filters.distortion:
                    distortion_payload: typing.MutableMapping[str, typing.Any] = {}
                    if filters.distortion.sin_offset is not None:
                        distortion_payload.update(
                            {"sinOffset": filters.distortion.sin_offset},
                        )
                    if filters.distortion.sin_scale is not None:
                        distortion_payload.update(
                            {"sinScale": filters.distortion.sin_scale},
                        )
                    if filters.distortion.cos_offset is not None:
                        distortion_payload.update(
                            {"cosOffset": filters.distortion.cos_offset},
                        )
                    if filters.distortion.cos_scale is not None:
                        distortion_payload.update(
                            {"cosScale": filters.distortion.cos_scale},
                        )
                    if filters.distortion.tan_offset is not None:
                        distortion_payload.update(
                            {"tanOffset": filters.distortion.tan_offset},
                        )
                    if filters.distortion.tan_scale is not None:
                        distortion_payload.update(
                            {"tanScale": filters.distortion.tan_scale},
                        )
                    if filters.distortion.offset is not None:
                        distortion_payload.update({"offset": filters.distortion.offset})
                    if filters.distortion.scale is not None:
                        distortion_payload.update({"scale": filters.distortion.scale})

                    if len(distortion_payload.items()) > 0:
                        filters_payload.update({"distortion": distortion_payload})

                if filters.channel_mix:
                    channel_mix_payload: typing.MutableMapping[str, typing.Any] = {}
                    if filters.channel_mix.left_to_left is not None:
                        channel_mix_payload.update(
                            {"leftToLeft": filters.channel_mix.left_to_left},
                        )
                    if filters.channel_mix.left_to_right is not None:
                        channel_mix_payload.update(
                            {"leftToRight": filters.channel_mix.left_to_right},
                        )
                    if filters.channel_mix.right_to_left is not None:
                        channel_mix_payload.update(
                            {"rightToLeft": filters.channel_mix.right_to_left},
                        )
                    if filters.channel_mix.right_to_right is not None:
                        channel_mix_payload.update(
                            {"rightToRight": filters.channel_mix.right_to_right},
                        )

                    if len(channel_mix_payload.items()) > 0:
                        filters_payload.update({"channelMix": channel_mix_payload})

                if filters.low_pass:
                    low_pass_payload: typing.MutableMapping[str, typing.Any] = {}
                    if filters.low_pass.smoothing is not None:
                        low_pass_payload.update(
                            {"smoothing": filters.low_pass.smoothing},
                        )

                    if len(low_pass_payload.items()) > 0:
                        filters_payload.update({"lowPass": low_pass_payload})

                patch_data.update({"filters": filters_payload})

        if voice != hikari.UNDEFINED:
            patch_data.update(
                {
                    "voice": {
                        "token": voice.token,
                        "endpoint": voice.endpoint,
                        "sessionId": voice.session_id,
                        "channelId": str(voice.channel_id)
                        if voice.channel_id is not None
                        else None,
                    },
                },
            )

        route = routes.PATCH_PLAYER_UPDATE

        _logger.log(
            TRACE_LEVEL,
            str(route),
        )

        if not session:
            session = self._client.session_handler.fetch_session()

        response = await session.request(
            route.method,
            route.path.format(session_id=session_id, guild_id=hikari.Snowflake(guild)),
            dict,
            headers={"Content-Type": "application/json"},
            json=patch_data,
            params={"noReplace": "true" if no_replace else "false"},
        )

        if response is None:
            raise ValueError("Response is required for this request.")

        return self._client.entity_builder.build_player(response)

    async def delete_player(
        self,
        session_id: str,
        guild: hikari.SnowflakeishOr[hikari.Guild],
        session: Session | None = None,
    ) -> None:
        """
        Delete a player.

        Deletes a specific player from this session.

        ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#destroy-player)

        Example
        -------
        ```py
        await client.rest.delete_player(session_id, guild_id)
        ```

        Parameters
        ----------
        session_id
            The Session ID that the players are attached too.
        guild
            The `guild` or `guild id` that the player is attached to.
        session
            If provided, the session to use for this request.

        Raises
        ------
        NoSessionsError
            Raised when there is no available sessions for this request to take place.
        TimeoutError
            Raised when the request takes too long to respond.
        RestEmptyError
            Raised when the request required a return type, but received nothing, or a 204 response.
        RestStatusError
            Raised when a 4XX or a 5XX status is received.
        RestRequestError
            Raised when a 4XX or a 5XX status is received, and lavalink gives more information.
        RestError
            Raised when an unknown error is caught.
        """
        route = routes.DELETE_PLAYER

        _logger.log(TRACE_LEVEL, str(route))

        if not session:
            session = self._client.session_handler.fetch_session()

        await session.request(
            route.method,
            route.path.format(session_id=session_id, guild_id=hikari.Snowflake(guild)),
            None,
        )

    async def update_session(
        self,
        session_id: str,
        *,
        resuming: bool | None = None,
        timeout: int | None = None,
        session: Session | None = None,
    ) -> session_.Session:
        """
        Update Lavalink session.

        Updates the lavalink session.

        ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#update-session)

        Example
        -------
        ```py
        await client.rest.update_session(session_id, False)
        ```

        Parameters
        ----------
        session_id
            The session you wish to update.
        resuming
            Whether resuming is enabled for this session or not.
        timeout
            The timeout in seconds (default is 60s)
        session
            If provided, the session to use for this request.

        Raises
        ------
        NoSessionsError
            Raised when there is no available sessions for this request to take place.
        TimeoutError
            Raised when the request takes too long to respond.
        RestEmptyError
            Raised when the request required a return type, but received nothing, or a 204 response.
        RestStatusError
            Raised when a 4XX or a 5XX status is received.
        BuildError
            Raised when the session could not be built.
        RestRequestError
            Raised when a 4XX or a 5XX status is received, and lavalink gives more information.
        RestError
            Raised when an unknown error is caught.

        Returns
        -------
        Session
            The Session object.
        """
        route = routes.PATCH_SESSION_UPDATE

        _logger.log(TRACE_LEVEL, str(route))

        if not session:
            session = self._client.session_handler.fetch_session()

        data: typing.MutableMapping[str, typing.Any] = {}

        if resuming is not None:
            data.update({"resuming": resuming})

        if timeout:
            data.update({"timeout": timeout})

        response = await session.request(
            route.method,
            route.path.format(session_id=session_id),
            dict,
            headers={"Content-Type": "application/json"},
            json=data,
        )

        if response is None:
            raise ValueError("Response is required for this request.")

        return self._client.entity_builder.build_session(response)

    async def fetch_info(self, *, session: Session | None = None) -> Info:
        """
        Get information.

        Gets the current sessions information.

        ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#get-lavalink-info)

        Example
        -------
        ```py
        info = await client.rest.fetch_info()

        print(info.version.semver)
        ```

        Parameters
        ----------
        session
            If provided, the session to use for this request.

        Raises
        ------
        NoSessionsError
            Raised when there is no available sessions for this request to take place.
        TimeoutError
            Raised when the request takes too long to respond.
        RestEmptyError
            Raised when the request required a return type, but received nothing, or a 204 response.
        RestStatusError
            Raised when a 4XX or a 5XX status is received.
        BuildError
            Raised when the information could not be built.
        RestRequestError
            Raised when a 4XX or a 5XX status is received, and lavalink gives more information.
        RestError
            Raised when an unknown error is caught.

        Returns
        -------
        Info
            The Info object.
        """
        route = routes.GET_INFO

        _logger.log(TRACE_LEVEL, str(route))

        if not session:
            session = self._client.session_handler.fetch_session()

        response = await session.request(
            route.method,
            route.path,
            dict,
        )

        if response is None:
            raise ValueError("Response is required for this request.")

        return self._client.entity_builder.build_info(response)

    async def fetch_version(self, *, session: Session | None = None) -> str:
        """
        Get version.

        Gets the current Lavalink version.

        ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#get-lavalink-version)

        Example
        -------
        ```py
        version = await client.rest.fetch_version()

        print(version)
        ```

        Parameters
        ----------
        session
            If provided, the session to use for this request.

        Raises
        ------
        NoSessionsError
            Raised when there is no available sessions for this request to take place.
        TimeoutError
            Raised when the request takes too long to respond.
        RestEmptyError
            Raised when the request required a return type, but received nothing, or a 204 response.
        RestStatusError
            Raised when a 4XX or a 5XX status is received.
        RestRequestError
            Raised when a 4XX or a 5XX status is received, and lavalink gives more information.
        RestError
            Raised when an unknown error is caught.

        Returns
        -------
        str
            The version, in string format.
        """
        route = routes.GET_VERSION

        _logger.log(TRACE_LEVEL, str(route))

        if not session:
            session = self._client.session_handler.fetch_session()

        response = await session.request(route.method, route.path, str, version=False)

        if response is None:
            raise ValueError("Response is required for this request.")

        return response

    async def fetch_stats(self, *, session: Session | None = None) -> Statistics:
        """
        Get statistics.

        Gets the current Lavalink statistics.

        ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#get-lavalink-stats)

        !!! note
            frame_statistics will always be `None`.

        Example
        -------
        ```py
        stats = await client.rest.fetch_stats()

        print(stats.players)
        ```

        Parameters
        ----------
        session
            If provided, the session to use for this request.

        Raises
        ------
        NoSessionsError
            Raised when there is no available sessions for this request to take place.
        TimeoutError
            Raised when the request takes too long to respond.
        RestEmptyError
            Raised when the request required a return type, but received nothing, or a 204 response.
        RestStatusError
            Raised when a 4XX or a 5XX status is received.
        BuildError
            Raised when the statistics could not be built.
        RestRequestError
            Raised when a 4XX or a 5XX status is received, and lavalink gives more information.
        RestError
            Raised when an unknown error is caught.

        Returns
        -------
        Statistics
            The Statistics object.
        """
        route = routes.GET_STATISTICS

        _logger.log(TRACE_LEVEL, str(route))

        if not session:
            session = self._client.session_handler.fetch_session()

        response = await session.request(
            route.method,
            route.path,
            dict,
        )

        if response is None:
            raise ValueError("Response is required for this request.")

        return self._client.entity_builder.build_statistics(response)

    async def fetch_routeplanner_status(
        self,
        *,
        session: Session | None = None,
    ) -> RoutePlannerStatus | None:
        """
        Fetch routeplanner status.

        Fetches the routeplanner status of the current session.

        ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#get-routeplanner-status)

        Example
        -------
        ```py
        routeplanner_status = await client.rest.fetch_routeplanner_status()

        if routeplanner_status:
            print(routeplanner_status.class_type.name)
        ```

        Parameters
        ----------
        session
            If provided, the session to use for this request.

        Raises
        ------
        NoSessionsError
            Raised when there is no available sessions for this request to take place.
        TimeoutError
            Raised when the request takes too long to respond.
        RestEmptyError
            Raised when the request required a return type, but received nothing, or a 204 response.
        RestStatusError
            Raised when a 4XX or a 5XX status is received.
        BuildError
            Raised when the routeplanner status could not be built.
        RestRequestError
            Raised when a 4XX or a 5XX status is received, and lavalink gives more information.
        RestError
            Raised when an unknown error is caught.

        Returns
        -------
        RoutePlannerStatus
            The RoutePlannerStatus object.
        None
            The Route Planner for this server is not active.
        """
        route = routes.GET_ROUTEPLANNER_STATUS

        _logger.log(TRACE_LEVEL, str(route))

        if not session:
            session = self._client.session_handler.fetch_session()

        try:
            response = await session.request(
                route.method,
                route.path,
                dict,
            )
        except errors.RestEmptyError:
            response = None

        if response is None:
            return None

        return self._client.entity_builder.build_routeplanner_status(response)

    async def update_routeplanner_address(
        self,
        address: str,
        *,
        session: Session | None = None,
    ) -> None:
        """
        Free routeplanner address.

        Free's the specified routeplanner address.

        ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#unmark-a-failed-address)

        Example
        -------
        ```py
        await client.rest.update_routeplanner_address(address)
        ```

        Parameters
        ----------
        address
            The address you wish to free.
        session
            If provided, the session to use for this request.

        Raises
        ------
        NoSessionsError
            Raised when there is no available sessions for this request to take place.
        TimeoutError
            Raised when the request takes too long to respond.
        RestEmptyError
            Raised when the request required a return type, but received nothing, or a 204 response.
        RestStatusError
            Raised when a 4XX or a 5XX status is received.
        RestRequestError
            Raised when a 4XX or a 5XX status is received, and lavalink gives more information.
        RestError
            Raised when an unknown error is caught.
        """
        route = routes.POST_ROUTEPLANNER_FREE_ADDRESS

        _logger.log(TRACE_LEVEL, str(route))

        if not session:
            session = self._client.session_handler.fetch_session()

        await session.request(route.method, route.path, None, json={"address": address})

    async def update_all_routeplanner_addresses(
        self,
        *,
        session: Session | None = None,
    ) -> None:
        """
        Free all routeplanner addresses.

        Frees every blocked routeplanner address.

        ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest#unmark-all-failed-address)

        Example
        -------
        ```py
        await client.rest.update_all_routeplanner_addresses()
        ```

        Parameters
        ----------
        session
            If provided, the session to use for this request.

        Raises
        ------
        NoSessionsError
            Raised when there is no available sessions for this request to take place.
        TimeoutError
            Raised when the request takes too long to respond.
        RestEmptyError
            Raised when the request required a return type, but received nothing, or a 204 response.
        RestStatusError
            Raised when a 4XX or a 5XX status is received.
        RestRequestError
            Raised when a 4XX or a 5XX status is received, and lavalink gives more information.
        RestError
            Raised when an unknown error is caught.
        """
        route = routes.POST_ROUTEPLANNER_FREE_ALL

        _logger.log(TRACE_LEVEL, str(route))

        if not session:
            session = self._client.session_handler.fetch_session()

        await session.request(
            route.method,
            route.path,
            None,
        )


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
