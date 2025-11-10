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
"""Builders for objects and entities."""

from __future__ import annotations

import datetime
import typing

import hikari

from ongaku import errors
from ongaku import events
from ongaku import filters
from ongaku import information
from ongaku import player
from ongaku import playlist
from ongaku import routeplanner
from ongaku import session
from ongaku import statistics
from ongaku import track
from ongaku.abc import builders
from ongaku.internal import types

__all__: typing.Sequence[str] = (
    "EntityBuilder",
    "FiltersBuilder",
)


class EntityBuilder:
    """Entity Builder.

    The class that allows for converting payloads (str, sequence, mapping, etc)
    into their respective classes and vise versa.

    Parameters
    ----------
    dumps
        The dumping method to use when dumping payloads.
    loads
        The loading method to use when loading payloads.
    """

    __slots__: typing.Sequence[str] = (
        "_dumps",
        "_loads",
    )

    def __init__(
        self,
        *,
        dumps: types.DumpType = types.json_dumps,
        loads: types.LoadType = types.json_loads,
    ) -> None:
        self._dumps = dumps
        self._loads = loads

    def _ensure_mapping(
        self,
        payload: types.PayloadMappingT,
        /,
    ) -> typing.Mapping[str, typing.Any]:
        data = self._loads(payload) if isinstance(payload, str | bytes) else payload

        if not isinstance(data, typing.Mapping):
            raise errors.BuildTypeError(typing.Mapping, type(data))

        return data

    def _ensure_sequence(
        self,
        payload: types.PayloadSequenceT,
        /,
    ) -> typing.Sequence[typing.Any]:
        data = self._loads(payload) if isinstance(payload, str | bytes) else payload

        if not isinstance(data, typing.Sequence):
            raise errors.BuildTypeError(typing.Sequence, type(data))

        return data

    #####################
    #                   #
    #     deserialize   #
    #                   #
    #####################

    # errors

    def deserialize_rest_error(
        self,
        payload: types.PayloadMappingT,
    ) -> errors.RestRequestError:
        """Deserialize Rest Request Error.

        Deserializes a rest request error object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.

        Returns
        -------
        RestRequestError
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return errors.RestRequestError(
            datetime.datetime.fromtimestamp(
                int(data["timestamp"]) / 1000,
                datetime.timezone.utc,
            ),
            data["status"],
            data["error"],
            data["message"],
            data["path"],
            data.get("trace", None),
        )

    def deserialize_exception_error(
        self,
        payload: types.PayloadMappingT,
    ) -> errors.ExceptionError:
        """Deserialize Exception Error.

        Deserializes a exception error object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.

        Returns
        -------
        RestExceptionError
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return errors.ExceptionError(
            data.get("message", None),
            errors.SeverityType(data["severity"]),
            data["cause"],
        )

    # Events

    def deserialize_ready_event(
        self,
        payload: types.PayloadMappingT,
        *,
        session: session.Session,
    ) -> events.ReadyEvent:
        """Deserialize Ready Event.

        Deserializes a ready event object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.
        session
            The session attached to this event.

        Returns
        -------
        events.ReadyEvent
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return events.ReadyEvent.from_session(
            session,
            resumed=data["resumed"],
            session_id=data["sessionId"],
        )

    def deserialize_player_update_event(
        self,
        payload: types.PayloadMappingT,
        *,
        session: session.Session,
    ) -> events.PlayerUpdateEvent:
        """Deserialize Player Update Event.

        Deserializes a player update event object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.
        session
            The session attached to this event.

        Returns
        -------
        events.PlayerUpdateEvent
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return events.PlayerUpdateEvent.from_session(
            session,
            guild_id=hikari.Snowflake(int(data["guildId"])),
            state=self.deserialize_state(data["state"]),
        )

    def deserialize_statistics_event(
        self,
        payload: types.PayloadMappingT,
        *,
        session: session.Session,
    ) -> events.StatisticsEvent:
        """Deserialize Statistics Event.

        Deserializes a statistics event object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.
        session
            The session attached to this event.

        Returns
        -------
        events.StatisticsEvent
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        statistics = self.deserialize_statistics(payload)

        return events.StatisticsEvent.from_session(
            session,
            players=statistics.players,
            playing_players=statistics.playing_players,
            uptime=statistics.uptime,
            memory=statistics.memory,
            cpu=statistics.cpu,
            frame_statistics=statistics.frame_statistics,
        )

    def deserialize_track_start_event(
        self,
        payload: types.PayloadMappingT,
        *,
        session: session.Session,
    ) -> events.TrackStartEvent:
        """Deserialize Track Start Event.

        Deserializes a track start event object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.
        session
            The session attached to this event.

        Returns
        -------
        events.TrackStartEvent
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return events.TrackStartEvent.from_session(
            session,
            guild_id=hikari.Snowflake(int(data["guildId"])),
            track=self.deserialize_track(data["track"]),
        )

    def deserialize_track_end_event(
        self,
        payload: types.PayloadMappingT,
        *,
        session: session.Session,
    ) -> events.TrackEndEvent:
        """Deserialize Track End Event.

        Deserializes a track end event object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.
        session
            The session attached to this event.

        Returns
        -------
        events.TrackEndEvent
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return events.TrackEndEvent.from_session(
            session,
            guild_id=hikari.Snowflake(int(data["guildId"])),
            track=self.deserialize_track(data["track"]),
            reason=track.TrackEndReasonType(data["reason"]),
        )

    def deserialize_track_exception_event(
        self,
        payload: types.PayloadMappingT,
        *,
        session: session.Session,
    ) -> events.TrackExceptionEvent:
        """Deserialize Track Exception Event.

        Deserializes a track exception event object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.
        session
            The session attached to this event.

        Returns
        -------
        events.TrackExceptionEvent
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return events.TrackExceptionEvent.from_session(
            session,
            guild_id=hikari.Snowflake(int(data["guildId"])),
            track=self.deserialize_track(data["track"]),
            exception=self.deserialize_exception_error(data["exception"]),
        )

    def deserialize_track_stuck_event(
        self,
        payload: types.PayloadMappingT,
        *,
        session: session.Session,
    ) -> events.TrackStuckEvent:
        """Deserialize Track Stuck Event.

        Deserializes a track stuck event object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.
        session
            The session attached to this event.

        Returns
        -------
        events.TrackStuckEvent
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return events.TrackStuckEvent.from_session(
            session,
            guild_id=hikari.Snowflake(int(data["guildId"])),
            track=self.deserialize_track(data["track"]),
            threshold_ms=data["thresholdMs"],
        )

    def deserialize_websocket_closed_event(
        self,
        payload: types.PayloadMappingT,
        *,
        session: session.Session,
    ) -> events.WebsocketClosedEvent:
        """Deserialize Websocket Closed Event.

        Deserializes a websocket closed event object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.
        session
            The session attached to this event.

        Returns
        -------
        events.WebsocketClosedEvent
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return events.WebsocketClosedEvent.from_session(
            session,
            guild_id=hikari.Snowflake(int(data["guildId"])),
            code=data["code"],
            reason=data["reason"],
            by_remote=data["byRemote"],
        )

    # filters

    def deserialize_filters(
        self,
        payload: types.PayloadMappingT,
    ) -> filters.Filters:
        """Deserialize Filters.

        Deserializes a filter object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.

        Returns
        -------
        filters_.Filters
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        equalizer = []

        if data.get("equalizer", None) is not None:
            equalizer = [
                self._deserialize_equalizer(equalizer)
                for equalizer in data["equalizer"]
            ]

        return filters.Filters(
            volume=data.get("volume", None),
            equalizer=equalizer,
            karaoke=self._deserialize_karaoke(data["karaoke"])
            if data.get("karaoke", None)
            else None,
            timescale=self._deserialize_timescale(data["timescale"])
            if data.get("timescale", None)
            else None,
            tremolo=self._deserialize_tremolo(data["tremolo"])
            if data.get("tremolo", None)
            else None,
            vibrato=self._deserialize_vibrato(data["vibrato"])
            if data.get("vibrato", None)
            else None,
            rotation=self._deserialize_rotation(data["rotation"])
            if data.get("rotation", None)
            else None,
            distortion=self._deserialize_distortion(data["distortion"])
            if data.get("distortion", None)
            else None,
            channel_mix=self._deserialize_channel_mix(data["channelMix"])
            if data.get("channelMix", None)
            else None,
            low_pass=self._deserialize_low_pass(data["lowPass"])
            if data.get("lowPass", None)
            else None,
            plugin_filters=data.get("pluginFilters", None),
        )

    def _deserialize_equalizer(
        self,
        payload: types.PayloadMappingT,
    ) -> filters.Equalizer:
        data = self._ensure_mapping(payload)

        return filters.Equalizer(
            band=filters.BandType(data["band"]),
            gain=data["gain"],
        )

    def _deserialize_karaoke(
        self,
        payload: types.PayloadMappingT,
    ) -> filters.Karaoke:
        data = self._ensure_mapping(payload)

        return filters.Karaoke(
            level=data.get("level", None),
            mono_level=data.get("monoLevel", None),
            filter_band=data.get("filterBand", None),
            filter_width=data.get("filterWidth", None),
        )

    def _deserialize_timescale(
        self,
        payload: types.PayloadMappingT,
    ) -> filters.Timescale:
        data = self._ensure_mapping(payload)

        return filters.Timescale(
            speed=data.get("speed", None),
            pitch=data.get("pitch", None),
            rate=data.get("rate", None),
        )

    def _deserialize_tremolo(
        self,
        payload: types.PayloadMappingT,
    ) -> filters.Tremolo:
        data = self._ensure_mapping(payload)

        return filters.Tremolo(
            frequency=data.get("frequency", None),
            depth=data.get("depth", None),
        )

    def _deserialize_vibrato(
        self,
        payload: types.PayloadMappingT,
    ) -> filters.Vibrato:
        data = self._ensure_mapping(payload)

        return filters.Vibrato(
            frequency=data.get("frequency", None),
            depth=data.get("depth", None),
        )

    def _deserialize_rotation(
        self,
        payload: types.PayloadMappingT,
    ) -> filters.Rotation:
        data = self._ensure_mapping(payload)

        return filters.Rotation(
            rotation_hz=data.get("rotationHz", None),
        )

    def _deserialize_distortion(
        self,
        payload: types.PayloadMappingT,
    ) -> filters.Distortion:
        data = self._ensure_mapping(payload)

        return filters.Distortion(
            sin_offset=data.get("sinOffset", None),
            sin_scale=data.get("sinScale", None),
            cos_offset=data.get("cosOffset", None),
            cos_scale=data.get("cosScale", None),
            tan_offset=data.get("tanOffset", None),
            tan_scale=data.get("tanScale", None),
            offset=data.get("offset", None),
            scale=data.get("scale", None),
        )

    def _deserialize_channel_mix(
        self,
        payload: types.PayloadMappingT,
    ) -> filters.ChannelMix:
        data = self._ensure_mapping(payload)

        return filters.ChannelMix(
            left_to_left=data.get("leftToLeft", None),
            left_to_right=data.get("leftToRight", None),
            right_to_left=data.get("rightToLeft", None),
            right_to_right=data.get("rightToRight", None),
        )

    def _deserialize_low_pass(
        self,
        payload: types.PayloadMappingT,
    ) -> filters.LowPass:
        data = self._ensure_mapping(payload)

        return filters.LowPass(
            smoothing=data.get("smoothing", None),
        )

    # info

    def deserialize_information(
        self,
        payload: types.PayloadMappingT,
    ) -> information.Information:
        """Deserialize Information.

        Deserializes a information object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.

        Returns
        -------
        info_.Info
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        source_managers: list[str] = data["sourceManagers"]

        filters: list[str] = data["filters"]

        plugins = [self._deserialize_plugin(plugin) for plugin in data["plugins"]]

        return information.Information(
            version=self._deserialize_version(data["version"]),
            build_time=datetime.datetime.fromtimestamp(
                int(data["buildTime"]) / 1000,
                datetime.timezone.utc,
            ),
            git=self._deserialize_git(data["git"]),
            jvm=data["jvm"],
            lavaplayer=data["lavaplayer"],
            source_managers=source_managers,
            filters=filters,
            plugins=plugins,
        )

    def _deserialize_version(
        self,
        payload: types.PayloadMappingT,
    ) -> information.Version:
        """Deserialize Version Information.

        Deserializes a information version object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.

        Returns
        -------
        info_.Version
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return information.Version(
            semver=data["semver"],
            major=data["major"],
            minor=data["minor"],
            patch=data["patch"],
            pre_release=data["preRelease"],
            build=data.get("build", None),
        )

    def _deserialize_git(self, payload: types.PayloadMappingT) -> information.Git:
        """Deserialize Git Information.

        Deserializes a information git object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.

        Returns
        -------
        info_.Info
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return information.Git(
            branch=data["branch"],
            commit=data["commit"],
            commit_time=datetime.datetime.fromtimestamp(
                int(data["commitTime"]) / 1000,
                datetime.timezone.utc,
            ),
        )

    def _deserialize_plugin(
        self,
        payload: types.PayloadMappingT,
    ) -> information.Plugin:
        """Deserialize Plugin Information.

        Deserializes a information plugin object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.

        Returns
        -------
        info_.Plugin
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return information.Plugin(name=data["name"], version=data["version"])

    # player

    def deserialize_player(
        self,
        payload: types.PayloadMappingT,
    ) -> player.PartialPlayer:
        """Deserialize Partial Player.

        Deserializes a partial player object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.

        Returns
        -------
        player_.PartialPlayer
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return player.PartialPlayer(
            guild_id=hikari.Snowflake(int(data["guildId"])),
            track=self.deserialize_track(data["track"])
            if data.get("track", None)
            else None,
            volume=data["volume"],
            is_paused=data["paused"],
            state=self.deserialize_state(data["state"]),
            voice=self._deserialize_voice(data["voice"]),
            filters=self.deserialize_filters(data["filters"])
            if data.get("filters", False)
            else None,
        )

    def deserialize_state(
        self,
        payload: types.PayloadMappingT,
    ) -> player.State:
        """Deserialize Player State.

        Deserializes a player state object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.

        Returns
        -------
        player_.State
            The [`State`][ongaku.player.State] object.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return player.State(
            time=datetime.datetime.fromtimestamp(
                int(data["time"]) / 1000,
                datetime.timezone.utc,
            ),
            position=data["position"],
            is_connected=data["connected"],
            ping=data["ping"],
        )

    def _deserialize_voice(
        self,
        payload: types.PayloadMappingT,
    ) -> player.Voice:
        data = self._ensure_mapping(payload)

        return player.Voice(
            token=data["token"],
            endpoint=data["endpoint"],
            session_id=data["sessionId"],
        )

    # playlist

    def deserialize_playlist(
        self,
        payload: types.PayloadMappingT,
    ) -> playlist.Playlist:
        """Deserialize Playlist.

        Deserializes a playlist object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.

        Returns
        -------
        playlist_.Playlist
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        tracks: list[track.Track] = [
            self.deserialize_track(track) for track in data["tracks"]
        ]

        return playlist.Playlist(
            info=self._deserialize_playlist_info(data["info"]),
            tracks=tracks,
            plugin_info=data["pluginInfo"],
        )

    def _deserialize_playlist_info(
        self,
        payload: types.PayloadMappingT,
    ) -> playlist.PlaylistInfo:
        data = self._ensure_mapping(payload)

        return playlist.PlaylistInfo(
            name=data["name"],
            selected_track=data["selectedTrack"],
        )

    # route planner

    def deserialize_routeplanner_status(
        self,
        payload: types.PayloadMappingT,
    ) -> routeplanner.RoutePlannerStatus:
        """Deserialize Route Planner Status.

        Deserializes a route planner status object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.

        Returns
        -------
        routeplanner_.RoutePlannerStatus
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return routeplanner.RoutePlannerStatus(
            cls=routeplanner.RoutePlannerType(data["class"]),
            details=self._deserialize_routeplanner_details(data["details"]),
        )

    def _deserialize_routeplanner_details(
        self,
        payload: types.PayloadMappingT,
    ) -> routeplanner.RoutePlannerDetails:
        data = self._ensure_mapping(payload)

        failing_addresses = [
            self._deserialize_routeplanner_failing_address(failing_address)
            for failing_address in data["failingAddresses"]
        ]

        return routeplanner.RoutePlannerDetails(
            ip_block=self._deserialize_routeplanner_ipblock(data["ipBlock"]),
            failing_addresses=failing_addresses,
            rotate_index=data.get("rotateIndex", None),
            ip_index=data.get("ipIndex", None),
            current_address=data.get("currentAddress", None),
            current_address_index=data.get("currentAddressIndex", None),
            block_index=data.get("blockIndex", None),
        )

    def _deserialize_routeplanner_ipblock(
        self,
        payload: types.PayloadMappingT,
    ) -> routeplanner.IPBlock:
        data = self._ensure_mapping(payload)

        return routeplanner.IPBlock(
            type=routeplanner.IPBlockType(data["type"]),
            size=data["size"],
        )

    def _deserialize_routeplanner_failing_address(
        self,
        payload: types.PayloadMappingT,
    ) -> routeplanner.FailingAddress:
        data = self._ensure_mapping(payload)

        return routeplanner.FailingAddress(
            address=data["failingAddress"],
            timestamp=datetime.datetime.fromtimestamp(
                int(data["failingTimestamp"]) / 1000,
                datetime.timezone.utc,
            ),
            time=data["failingTime"],
        )

    # session

    def deserialize_session(
        self,
        payload: types.PayloadMappingT,
    ) -> session.PartialSession:
        """Deserialize Partial Session.

        Deserializes a partial session object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.

        Returns
        -------
        session_.PartialSession
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return session.PartialSession(
            resuming=data["resuming"],
            timeout=data["timeout"],
        )

    # statistics

    def deserialize_statistics(
        self,
        payload: types.PayloadMappingT,
    ) -> statistics.Statistics:
        """Deserialize Statistics.

        Deserializes a statistics object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.

        Returns
        -------
        statistics_.Statistics
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        return statistics.Statistics(
            players=data["players"],
            playing_players=data["playingPlayers"],
            uptime=data["uptime"],
            memory=self._deserialize_memory(data["memory"]),
            cpu=self._deserialize_cpu(data["cpu"]),
            frame_statistics=self._deserialize_frame_statistics(
                data["frameStats"],
            )
            if data.get("frameStats", None) is not None
            else None,
        )

    def _deserialize_memory(
        self,
        payload: types.PayloadMappingT,
    ) -> statistics.Memory:
        data = self._ensure_mapping(payload)

        return statistics.Memory(
            free=data["free"],
            used=data["used"],
            allocated=data["allocated"],
            reservable=data["reservable"],
        )

    def _deserialize_cpu(
        self,
        payload: types.PayloadMappingT,
    ) -> statistics.Cpu:
        data = self._ensure_mapping(payload)

        return statistics.Cpu(
            cores=data["cores"],
            system_load=data["systemLoad"],
            lavalink_load=data["lavalinkLoad"],
        )

    def _deserialize_frame_statistics(
        self,
        payload: types.PayloadMappingT,
    ) -> statistics.FrameStatistics:
        data = self._ensure_mapping(payload)

        return statistics.FrameStatistics(
            sent=data["sent"],
            nulled=data["nulled"],
            deficit=data["deficit"],
        )

    # track

    def deserialize_track(self, payload: types.PayloadMappingT) -> track.Track:
        """Deserialize Track.

        Deserializes a track object from a payload.

        Parameters
        ----------
        payload
            The payload you provide.

        Returns
        -------
        track_.Track
            The object from the payload.

        Raises
        ------
        TypeError
            Raised when the payload could not be turned into a mapping.
        KeyError
            Raised when a value was not found in the payload.
        """
        data = self._ensure_mapping(payload)

        user_data: typing.MutableMapping[str, typing.Any] = (
            data["userData"] if data.get("userData", None) else {}
        )

        requestor = user_data.pop("ongaku_requestor", None)

        return track.Track(
            encoded=data["encoded"],
            info=self._deserialize_track_info(data["info"]),
            plugin_info=data["pluginInfo"],
            user_data=user_data,
            requestor=hikari.Snowflake(requestor) if requestor else None,
        )

    def _deserialize_track_info(
        self,
        payload: types.PayloadMappingT,
    ) -> track.TrackInfo:
        data = self._ensure_mapping(payload)

        return track.TrackInfo(
            identifier=data["identifier"],
            is_seekable=data["isSeekable"],
            author=data["author"],
            length=data["length"],
            is_stream=data["isStream"],
            position=data["position"],
            title=data["title"],
            source_name=data["sourceName"],
            uri=data.get("uri", None),
            artwork_url=data.get("artworkUrl", None),
            isrc=data.get("isrc", None),
        )

    #####################
    #                   #
    #     serialize     #
    #                   #
    #####################

    # player

    def serialize_voice(
        self,
        voice: player.Voice,
    ) -> typing.Mapping[str, typing.Any]:
        """Serialize Voice.

        Serializes a player voice object into a payload.

        Parameters
        ----------
        voice
            The [`Voice`][ongaku.player.Voice] object you provide.

        Returns
        -------
        typing.Mapping[str, typing.Any]
            The mapping built from the payload.
        """
        return {
            "token": voice.token,
            "endpoint": voice.endpoint,
            "sessionId": voice.session_id,
        }


class FiltersBuilder(builders.FilterBuilder):
    """Filters Builder.

    A builder for creating filters for ongaku.
    """

    __slots__: typing.Sequence[str] = (
        "_channel_mix",
        "_distortion",
        "_equalizer",
        "_karaoke",
        "_low_pass",
        "_plugin_filters",
        "_rotation",
        "_timescale",
        "_tremolo",
        "_vibrato",
        "_volume",
    )

    def __init__(  # noqa: PLR0913
        self,
        *,
        volume: float | None = None,
        equalizer: typing.Sequence[EqualizerBuilder] = [],
        karaoke: KaraokeBuilder | None = None,
        timescale: TimescaleBuilder | None = None,
        tremolo: TremoloBuilder | None = None,
        vibrato: VibratoBuilder | None = None,
        rotation: RotationBuilder | None = None,
        distortion: DistortionBuilder | None = None,
        channel_mix: ChannelMixBuilder | None = None,
        low_pass: LowPassBuilder | None = None,
        plugin_filters: typing.Mapping[str, typing.Any] = {},
    ) -> None:
        self._volume = volume
        self._equalizer: set[EqualizerBuilder] = set(equalizer)
        self._karaoke = karaoke
        self._timescale = timescale
        self._tremolo = tremolo
        self._vibrato = vibrato
        self._rotation = rotation
        self._distortion = distortion
        self._channel_mix = channel_mix
        self._low_pass = low_pass
        self._plugin_filters = plugin_filters

    @classmethod
    def from_filter(cls, filters: filters.Filters) -> FiltersBuilder:
        """From Filter.

        Generate a filter builder from a filter object on a player.

        Parameters
        ----------
        filters
            The filter to use.
        """
        return cls(
            volume=filters.volume,
            equalizer=[
                EqualizerBuilder(band=equalizer.band, gain=equalizer.gain)
                for equalizer in filters.equalizer
            ],
            karaoke=KaraokeBuilder(
                level=filters.karaoke.level,
                mono_level=filters.karaoke.mono_level,
                filter_band=filters.karaoke.filter_band,
                filter_width=filters.karaoke.filter_width,
            )
            if filters.karaoke
            else None,
            timescale=TimescaleBuilder(
                speed=filters.timescale.speed,
                pitch=filters.timescale.pitch,
                rate=filters.timescale.rate,
            )
            if filters.timescale
            else None,
            tremolo=TremoloBuilder(
                frequency=filters.tremolo.frequency,
                depth=filters.tremolo.depth,
            )
            if filters.tremolo
            else None,
            vibrato=VibratoBuilder(
                frequency=filters.vibrato.frequency,
                depth=filters.vibrato.depth,
            )
            if filters.vibrato
            else None,
            rotation=RotationBuilder(
                rotation_hz=filters.rotation.rotation_hz,
            )
            if filters.rotation
            else None,
            distortion=DistortionBuilder(
                sin_offset=filters.distortion.sin_offset,
                sin_scale=filters.distortion.sin_scale,
                cos_offset=filters.distortion.cos_offset,
                cos_scale=filters.distortion.cos_scale,
                tan_offset=filters.distortion.tan_offset,
                tan_scale=filters.distortion.tan_scale,
                offset=filters.distortion.offset,
                scale=filters.distortion.scale,
            )
            if filters.distortion
            else None,
            channel_mix=ChannelMixBuilder(
                left_to_left=filters.channel_mix.left_to_left,
                left_to_right=filters.channel_mix.left_to_right,
                right_to_left=filters.channel_mix.right_to_left,
                right_to_right=filters.channel_mix.right_to_right,
            )
            if filters.channel_mix
            else None,
            low_pass=LowPassBuilder(
                smoothing=filters.low_pass.smoothing,
            )
            if filters.low_pass
            else None,
            plugin_filters=filters.plugin_filters,
        )

    @property
    def volume(self) -> float | None:
        """Volume.

        The volume of the player.
        """
        return self._volume

    @property
    def equalizer(self) -> set[EqualizerBuilder]:
        """Equalizer.

        15 bands with different gains.
        """
        return self._equalizer

    @property
    def karaoke(self) -> KaraokeBuilder | None:
        """Karaoke.

        Eliminates part of a band, usually targeting vocals.
        """
        return self._karaoke

    @property
    def timescale(self) -> TimescaleBuilder | None:
        """Timescale.

        The speed, pitch, and rate.
        """
        return self._timescale

    @property
    def tremolo(self) -> TremoloBuilder | None:
        """Tremolo.

        Creates a shuddering effect, where the volume quickly oscillates.
        """
        return self._tremolo

    @property
    def vibrato(self) -> VibratoBuilder | None:
        """Vibrato.

        Creates a shuddering effect, where the pitch quickly oscillates.
        """
        return self._vibrato

    @property
    def rotation(self) -> RotationBuilder | None:
        """Rotation.

        Rotates the audio around the stereo channels/user headphones.
        """
        return self._rotation

    @property
    def distortion(self) -> DistortionBuilder | None:
        """Distortion.

        Distorts the audio.
        """
        return self._distortion

    @property
    def channel_mix(self) -> ChannelMixBuilder | None:
        """Channel Mix.

        Mixes both channels (left and right).
        """
        return self._channel_mix

    @property
    def low_pass(self) -> LowPassBuilder | None:
        """Low Pass.

        Filters higher frequencies.
        """
        return self._low_pass

    @property
    def plugin_filters(self) -> typing.Mapping[str, typing.Any]:
        """Plugin Filters.

        Filter plugin configurations.
        """
        return self._plugin_filters

    def set_volume(self, volume: float) -> FiltersBuilder:
        """Set Volume.

        Set the volume of the filter.

        Parameters
        ----------
        volume
            The volume of the player. (Must be greater than 0.)

        Raises
        ------
        ValueError
            Raised when the volume is set below 0.
        """
        if volume <= 0:
            raise ValueError

        self._volume = volume

        return self

    # Equalizer

    def add_equalizer(self, band: filters.BandType, gain: float) -> FiltersBuilder:
        """Add Equalizer.

        Add a new equalizer band, with appropriate gain.

        Parameters
        ----------
        band
            The [BandType][ongaku.filters.BandType].
        gain
            The gain of the band. (-0.25 to 1.0)
        """
        self._equalizer.add(EqualizerBuilder(band=band, gain=gain))

        return self

    def remove_equalizer(self, band: filters.BandType) -> FiltersBuilder:
        """Remove Equalizer.

        Remove a equalizer via its band.

        Parameters
        ----------
        band
            The band type to look for.

        Raises
        ------
        IndexError
            Raised when no values match the requested band.
        """
        for equalizer in self.equalizer:
            if equalizer.band == band:
                self._equalizer.discard(equalizer)
                return self

        raise IndexError

    def clear_equalizer(self) -> FiltersBuilder:
        """Clear Equalizer.

        Clear all equalizer bands from the filter.
        """
        self._equalizer.clear()

        return self

    # Karaoke

    def set_karaoke(
        self,
        *,
        level: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        mono_level: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        filter_band: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        filter_width: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
    ) -> FiltersBuilder:
        """Set Karaoke.

        Set karaoke values.

        Parameters
        ----------
        level
            The level (0 to 1.0 where 0.0 is no effect and 1.0 is full effect).
        mono_level
            The mono level (0 to 1.0 where 0.0 is no effect and 1.0 is full effect).
        filter_band
            The filter band (in Hz).
        filter_width
            The filter width.
        """
        if self._karaoke is None:
            self._karaoke = KaraokeBuilder(
                level=None,
                mono_level=None,
                filter_band=None,
                filter_width=None,
            )

        self._karaoke = KaraokeBuilder(
            level=self._karaoke.level if level == hikari.UNDEFINED else level,
            mono_level=self._karaoke.mono_level
            if mono_level == hikari.UNDEFINED
            else mono_level,
            filter_band=self._karaoke.filter_band
            if filter_band == hikari.UNDEFINED
            else filter_band,
            filter_width=self._karaoke.filter_width
            if filter_width == hikari.UNDEFINED
            else filter_width,
        )

        return self

    def clear_karaoke(self) -> FiltersBuilder:
        """Clear Karaoke.

        Clear all karaoke values from the filter.
        """
        self._karaoke = None
        return self

    # Timescale

    def set_timescale(
        self,
        *,
        speed: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        pitch: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        rate: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
    ) -> FiltersBuilder:
        """Set Timescale.

        Set timescale values.

        Parameters
        ----------
        speed
            The playback speed 0.0 ≤ x.
        pitch
            The pitch 0.0 ≤ x.
        rate
            The rate 0.0 ≤ x.
        """
        if self._timescale is None:
            self._timescale = TimescaleBuilder(speed=None, pitch=None, rate=None)

        self._timescale = TimescaleBuilder(
            speed=self._timescale.speed if speed == hikari.UNDEFINED else speed,
            pitch=self._timescale.pitch if pitch == hikari.UNDEFINED else pitch,
            rate=self._timescale.rate if rate == hikari.UNDEFINED else rate,
        )

        return self

    def clear_timescale(self) -> FiltersBuilder:
        """Clear Timescale.

        Clear all timescale values from the filter.
        """
        self._timescale = None
        return self

    # Tremolo

    def set_tremolo(
        self,
        *,
        frequency: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        depth: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
    ) -> FiltersBuilder:
        """Set Tremolo.

        Set tremolo values.

        Parameters
        ----------
        frequency
            The frequency 0.0 < x.
        depth
            The tremolo depth 0.0 < x ≤ 1.0.
        """
        if self._tremolo is None:
            self._tremolo = TremoloBuilder(frequency=None, depth=None)

        self._tremolo = TremoloBuilder(
            frequency=self._tremolo.frequency
            if frequency == hikari.UNDEFINED
            else frequency,
            depth=self._tremolo.depth if depth == hikari.UNDEFINED else depth,
        )

        return self

    def clear_tremolo(self) -> FiltersBuilder:
        """Clear Tremolo.

        Clear all tremolo values from the filter.
        """
        self._tremolo = None
        return self

    # Vibrato

    def set_vibrato(
        self,
        *,
        frequency: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        depth: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
    ) -> FiltersBuilder:
        """Set Vibrato.

        Set vibrato values.

        Parameters
        ----------
        frequency
            The frequency 0.0 < x ≤ 14.0.
        depth
            The vibrato depth 0.0 < x ≤ 1.0.

        """
        if self._vibrato is None:
            self._vibrato = VibratoBuilder(frequency=None, depth=None)

        self._vibrato = VibratoBuilder(
            frequency=self._vibrato.frequency
            if frequency == hikari.UNDEFINED
            else frequency,
            depth=self._vibrato.depth if depth == hikari.UNDEFINED else depth,
        )

        return self

    def clear_vibrato(self) -> FiltersBuilder:
        """Clear Vibrato.

        Clear all vibrato values from the filter.
        """
        self._vibrato = None
        return self

    # Rotation

    def set_rotation(
        self,
        *,
        rotation_hz: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
    ) -> FiltersBuilder:
        """Set Rotation.

        Set rotation values.

        Parameters
        ----------
        rotation_hz
            The frequency of the audio rotating around the listener in Hz.
        """
        if self._rotation is None:
            self._rotation = RotationBuilder(rotation_hz=None)

        self._rotation = RotationBuilder(
            rotation_hz=self._rotation.rotation_hz
            if rotation_hz == hikari.UNDEFINED
            else rotation_hz,
        )

        return self

    def clear_rotation(self) -> FiltersBuilder:
        """Clear Rotation.

        Clear all rotation values from the filter.
        """
        self._rotation = None
        return self

    # Distortion

    def set_distortion(
        self,
        *,
        sin_offset: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        sin_scale: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        cos_offset: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        cos_scale: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        tan_offset: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        tan_scale: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        offset: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        scale: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
    ) -> FiltersBuilder:
        """Set Distortion.

        Set distortion values.

        Parameters
        ----------
        sin_offset
            The sin offset.
        sin_scale
            The sin scale.
        cos_offset
            The cos offset.
        cos_scale
            The cos scale.
        tan_offset
            The tan offset.
        tan_scale
            The tan scale.
        offset
            The offset.
        scale
            The scale.
        """
        if self._distortion is None:
            self._distortion = DistortionBuilder(
                sin_offset=None,
                sin_scale=None,
                cos_offset=None,
                cos_scale=None,
                tan_offset=None,
                tan_scale=None,
                offset=None,
                scale=None,
            )

        self._distortion = DistortionBuilder(
            sin_offset=self._distortion.sin_offset
            if sin_offset == hikari.UNDEFINED
            else sin_offset,
            sin_scale=self._distortion.sin_scale
            if sin_scale == hikari.UNDEFINED
            else sin_scale,
            cos_offset=self._distortion.cos_offset
            if cos_offset == hikari.UNDEFINED
            else cos_offset,
            cos_scale=self._distortion.cos_scale
            if cos_scale == hikari.UNDEFINED
            else cos_scale,
            tan_offset=self._distortion.tan_offset
            if tan_offset == hikari.UNDEFINED
            else tan_offset,
            tan_scale=self._distortion.tan_scale
            if tan_scale == hikari.UNDEFINED
            else tan_scale,
            offset=self._distortion.offset if offset == hikari.UNDEFINED else offset,
            scale=self._distortion.scale if scale == hikari.UNDEFINED else scale,
        )

        return self

    def clear_distortion(self) -> FiltersBuilder:
        """Clear Distortion.

        Clear all distortion values from the filter.
        """
        self._distortion = None
        return self

    # Channel Mix

    def set_channel_mix(
        self,
        *,
        left_to_left: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        left_to_right: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        right_to_left: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
        right_to_right: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
    ) -> FiltersBuilder:
        """Set Channel Mix.

        Set tremolo values.

        Parameters
        ----------
        left_to_left
            The left to left channel mix factor (0.0 ≤ x ≤ 1.0).
        left_to_right
            The left to right channel mix factor (0.0 ≤ x ≤ 1.0).
        right_to_left
            The right to left channel mix factor (0.0 ≤ x ≤ 1.0).
        right_to_right
            The right to right channel mix factor (0.0 ≤ x ≤ 1.0).

        """
        if self._channel_mix is None:
            self._channel_mix = ChannelMixBuilder(
                left_to_left=None,
                left_to_right=None,
                right_to_left=None,
                right_to_right=None,
            )

        self._channel_mix = ChannelMixBuilder(
            left_to_left=self._channel_mix.left_to_left
            if left_to_left == hikari.UNDEFINED
            else left_to_left,
            left_to_right=self._channel_mix.left_to_right
            if left_to_right == hikari.UNDEFINED
            else left_to_right,
            right_to_left=self._channel_mix.right_to_left
            if right_to_left == hikari.UNDEFINED
            else right_to_left,
            right_to_right=self._channel_mix.right_to_right
            if right_to_right == hikari.UNDEFINED
            else right_to_right,
        )

        return self

    def clear_channel_mix(self) -> FiltersBuilder:
        """Clear Channel Mix.

        Clear all channel mix values from the filter.
        """
        self._channel_mix = None
        return self

    # Low Pass

    def set_low_pass(
        self,
        *,
        smoothing: hikari.UndefinedNoneOr[float] = hikari.UNDEFINED,
    ) -> FiltersBuilder:
        """Set Low Pass.

        Set low pass values.

        Parameters
        ----------
        smoothing
            The smoothing factor (1.0 < x).
        """
        if self._low_pass is None:
            self._low_pass = LowPassBuilder(smoothing=None)

        self._low_pass = LowPassBuilder(
            smoothing=self._low_pass.smoothing
            if smoothing == hikari.UNDEFINED
            else smoothing,
        )

        return self

    def clear_low_pass(self) -> FiltersBuilder:
        """Clear Low Pass.

        Clear all low pass values from the filter.
        """
        self._low_pass = None
        return self

    # Plugin filters

    def set_plugin_filters(
        self,
        plugin_filters: typing.Mapping[str, typing.Any] = {},
    ) -> FiltersBuilder:
        """Set Plugin Filters.

        Set the filters for plugins.

        Parameters
        ----------
        plugin_filters
            The plugin filters you wish to set.
        """
        self._plugin_filters = plugin_filters
        return self

    def build(self) -> types.PayloadMappingT:  # noqa: D102 This has an inherited documentation string.
        payload: dict[str, typing.Any] = {}

        if self.volume:
            payload["volume"] = self.volume

        if self.equalizer != set():
            payload["equalizer"] = [equalizer.build() for equalizer in self.equalizer]

        filters = {
            "karaoke": self.karaoke,
            "timescale": self.timescale,
            "tremolo": self.tremolo,
            "vibrato": self.vibrato,
            "rotation": self.rotation,
            "distortion": self.distortion,
            "channelMix": self.channel_mix,
            "lowPass": self.low_pass,
        }

        for name, item in filters.items():
            if item is not None:
                payload[name] = item.build()

        if self.plugin_filters != {}:
            payload["pluginFilters"] = self.plugin_filters

        return payload

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FiltersBuilder):
            return False

        return (
            self.volume == other.volume
            and self.equalizer == other.equalizer
            and self.karaoke == other.karaoke
            and self.timescale == other.timescale
            and self.tremolo == other.tremolo
            and self.vibrato == other.vibrato
            and self.rotation == other.rotation
            and self.distortion == other.distortion
            and self.channel_mix == other.channel_mix
            and self.low_pass == other.low_pass
            and self.plugin_filters == other.plugin_filters
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.volume,
                self.equalizer,
                self.karaoke,
                self.timescale,
                self.tremolo,
                self.vibrato,
                self.rotation,
                self.distortion,
                self.channel_mix,
                self.low_pass,
                self.plugin_filters,
            ),
        )


class EqualizerBuilder(builders.FilterBuilder):
    __slots__: typing.Sequence[str] = ("_band", "_gain")

    def __init__(self, *, band: filters.BandType, gain: float) -> None:
        self._band = band
        self._gain = gain

    @property
    def band(self) -> filters.BandType:
        """The band (0 to 14)."""
        return self._band

    @property
    def gain(self) -> float:
        """The gain (-0.25 to 1.0)."""
        return self._gain

    def build(self) -> types.PayloadMappingT:
        return {"band": self.band.value, "gain": self.gain}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EqualizerBuilder):
            return False

        return self.band == other.band and self.gain == other.gain

    def __hash__(self) -> int:
        return hash(self.band)


class KaraokeBuilder(builders.FilterBuilder):
    __slots__: typing.Sequence[str] = (
        "_filter_band",
        "_filter_width",
        "_level",
        "_mono_level",
    )

    def __init__(
        self,
        *,
        level: float | None,
        mono_level: float | None,
        filter_band: float | None,
        filter_width: float | None,
    ) -> None:
        self._level = level
        self._mono_level = mono_level
        self._filter_band = filter_band
        self._filter_width = filter_width

    @property
    def level(self) -> float | None:
        """The level (0 to 1.0 where 0.0 is no effect and 1.0 is full effect)."""
        return self._level

    @property
    def mono_level(self) -> float | None:
        """The mono level (0 to 1.0 where 0.0 is no effect and 1.0 is full effect)."""
        return self._mono_level

    @property
    def filter_band(self) -> float | None:
        """The filter band (in Hz)."""
        return self._filter_band

    @property
    def filter_width(self) -> float | None:
        """The filter width."""
        return self._filter_width

    def build(self) -> types.PayloadMappingT:
        return {
            "level": self.level,
            "monoLevel": self.mono_level,
            "filterBand": self.filter_band,
            "filterWidth": self.filter_width,
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, KaraokeBuilder):
            return False

        return (
            self.level == other.level
            and self.mono_level == other.mono_level
            and self.filter_band == other.filter_band
            and self.filter_width == other.filter_width
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.level,
                self.mono_level,
                self.filter_band,
                self.filter_width,
            ),
        )


class TimescaleBuilder(builders.FilterBuilder):
    __slots__: typing.Sequence[str] = ("_pitch", "_rate", "_speed")

    def __init__(
        self,
        *,
        speed: float | None,
        pitch: float | None,
        rate: float | None,
    ) -> None:
        self._speed = speed
        self._pitch = pitch
        self._rate = rate

    @property
    def speed(self) -> float | None:
        """The playback speed 0.0 ≤ x."""
        return self._speed

    @property
    def pitch(self) -> float | None:
        """The pitch 0.0 ≤ x."""
        return self._pitch

    @property
    def rate(self) -> float | None:
        """The rate 0.0 ≤ x."""
        return self._rate

    def build(self) -> types.PayloadMappingT:
        return {
            "speed": self.speed,
            "pitch": self.pitch,
            "rate": self.rate,
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TimescaleBuilder):
            return False

        return (
            self.speed == other.speed
            and self.pitch == other.pitch
            and self.rate == other.rate
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.speed,
                self.pitch,
                self.rate,
            ),
        )


class TremoloBuilder(builders.FilterBuilder):
    __slots__: typing.Sequence[str] = (
        "_depth",
        "_frequency",
    )

    def __init__(self, *, frequency: float | None, depth: float | None) -> None:
        self._frequency = frequency
        self._depth = depth

    @property
    def frequency(self) -> float | None:
        """The frequency 0.0 < x."""
        return self._frequency

    @property
    def depth(self) -> float | None:
        """The tremolo depth 0.0 < x ≤ 1.0."""
        return self._depth

    def build(self) -> types.PayloadMappingT:
        return {"frequency": self.frequency, "depth": self.depth}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TremoloBuilder):
            return False

        return self.frequency == other.frequency and self.depth == other.depth

    def __hash__(self) -> int:
        return hash((self.frequency, self.depth))


class VibratoBuilder(builders.FilterBuilder):
    __slots__: typing.Sequence[str] = (
        "_depth",
        "_frequency",
    )

    def __init__(self, *, frequency: float | None, depth: float | None) -> None:
        self._frequency = frequency
        self._depth = depth

    @property
    def frequency(self) -> float | None:
        """The frequency 0.0 < x ≤ 14.0."""
        return self._frequency

    @property
    def depth(self) -> float | None:
        """The vibrato depth 0.0 < x ≤ 1.0."""
        return self._depth

    def build(self) -> types.PayloadMappingT:
        return {"frequency": self.frequency, "depth": self.depth}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VibratoBuilder):
            return False

        return self.frequency == other.frequency and self.depth == other.depth

    def __hash__(self) -> int:
        return hash((self.frequency, self.depth))


class RotationBuilder(builders.FilterBuilder):
    __slots__: typing.Sequence[str] = ("_rotation_hz",)

    def __init__(self, *, rotation_hz: float | None) -> None:
        self._rotation_hz = rotation_hz

    @property
    def rotation_hz(self) -> float | None:
        """The frequency of the audio rotating around the listener in Hz."""
        return self._rotation_hz

    def build(self) -> types.PayloadMappingT:
        return {"rotationHz": self.rotation_hz}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RotationBuilder):
            return False

        return self.rotation_hz == other.rotation_hz

    def __hash__(self) -> int:
        return hash(self.rotation_hz)


class DistortionBuilder(builders.FilterBuilder):
    __slots__: typing.Sequence[str] = (
        "_cos_offset",
        "_cos_scale",
        "_offset",
        "_scale",
        "_sin_offset",
        "_sin_scale",
        "_tan_offset",
        "_tan_scale",
    )

    def __init__(
        self,
        *,
        sin_offset: float | None,
        sin_scale: float | None,
        cos_offset: float | None,
        cos_scale: float | None,
        tan_offset: float | None,
        tan_scale: float | None,
        offset: float | None,
        scale: float | None,
    ) -> None:
        self._sin_offset = sin_offset
        self._sin_scale = sin_scale
        self._cos_offset = cos_offset
        self._cos_scale = cos_scale
        self._tan_offset = tan_offset
        self._tan_scale = tan_scale
        self._offset = offset
        self._scale = scale

    @property
    def sin_offset(self) -> float | None:
        """The sin offset."""
        return self._sin_offset

    @property
    def sin_scale(self) -> float | None:
        """The sin scale."""
        return self._sin_scale

    @property
    def cos_offset(self) -> float | None:
        """The cos offset."""
        return self._cos_offset

    @property
    def cos_scale(self) -> float | None:
        """The cos scale."""
        return self._cos_scale

    @property
    def tan_offset(self) -> float | None:
        """The tan offset."""
        return self._tan_offset

    @property
    def tan_scale(self) -> float | None:
        """The tan scale."""
        return self._tan_scale

    @property
    def offset(self) -> float | None:
        """The offset."""
        return self._offset

    @property
    def scale(self) -> float | None:
        """The scale."""
        return self._scale

    def build(self) -> types.PayloadMappingT:
        return {
            "sinOffset": self.sin_offset,
            "sinScale": self.sin_scale,
            "cosOffset": self.cos_offset,
            "cosScale": self.cos_scale,
            "tanOffset": self.tan_offset,
            "tanScale": self.tan_scale,
            "offset": self.offset,
            "scale": self.scale,
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DistortionBuilder):
            return False

        return (
            self.sin_offset == other.sin_offset
            and self.sin_scale == other.sin_scale
            and self.cos_offset == other.cos_offset
            and self.cos_scale == other.cos_scale
            and self.tan_offset == other.tan_offset
            and self.tan_scale == other.tan_scale
            and self.offset == other.offset
            and self.scale == other.scale
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.sin_offset,
                self.sin_scale,
                self.cos_offset,
                self.cos_scale,
                self.tan_offset,
                self.tan_scale,
                self.offset,
                self.scale,
            ),
        )


class ChannelMixBuilder(builders.FilterBuilder):
    __slots__: typing.Sequence[str] = (
        "_left_to_left",
        "_left_to_right",
        "_right_to_left",
        "_right_to_right",
    )

    def __init__(
        self,
        *,
        left_to_left: float | None,
        left_to_right: float | None,
        right_to_left: float | None,
        right_to_right: float | None,
    ) -> None:
        self._left_to_left = left_to_left
        self._left_to_right = left_to_right
        self._right_to_left = right_to_left
        self._right_to_right = right_to_right

    @property
    def left_to_left(self) -> float | None:
        """The left to left channel mix factor (0.0 ≤ x ≤ 1.0)."""
        return self._left_to_left

    @property
    def left_to_right(self) -> float | None:
        """The left to right channel mix factor (0.0 ≤ x ≤ 1.0)."""
        return self._left_to_right

    @property
    def right_to_left(self) -> float | None:
        """The right to left channel mix factor (0.0 ≤ x ≤ 1.0)."""
        return self._right_to_left

    @property
    def right_to_right(self) -> float | None:
        """The right to right channel mix factor (0.0 ≤ x ≤ 1.0)."""
        return self._right_to_right

    def build(self) -> types.PayloadMappingT:
        return {
            "leftToLeft": self.left_to_left,
            "leftToRight": self.left_to_right,
            "rightToLeft": self.right_to_left,
            "rightToRight": self.right_to_right,
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ChannelMixBuilder):
            return False

        return (
            self.left_to_left == other.left_to_left
            and self.left_to_right == other.left_to_right
            and self.right_to_left == other.right_to_left
            and self.right_to_right == other.right_to_right
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.left_to_left,
                self.left_to_right,
                self.right_to_left,
                self.right_to_right,
            ),
        )


class LowPassBuilder(builders.FilterBuilder):
    """Low Pass Builder.

    An implementation of a low pass builder.

    Parameters
    ----------
    smoothing
        FIXME: Value

    Raises
    ------
    ValueError
        Raised when the smoothing value is set above 1.
    """

    __slots__: typing.Sequence[str] = ("_smoothing",)

    def __init__(self, *, smoothing: float | None) -> None:
        if smoothing is not None and smoothing < 1:
            raise ValueError

        self._smoothing = smoothing

    @property
    def smoothing(self) -> float | None:
        """The smoothing factor (1.0 < x)."""
        return self._smoothing

    def build(self) -> types.PayloadMappingT:
        return {
            "smoothing": self.smoothing,
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LowPassBuilder):
            return False

        return self.smoothing == other.smoothing

    def __hash__(self) -> int:
        return hash(self.smoothing)
