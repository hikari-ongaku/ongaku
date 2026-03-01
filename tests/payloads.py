from __future__ import annotations

import typing

PayloadT: typing.TypeAlias = typing.Final[typing.Mapping[str, typing.Any]]

__all__ = (  # noqa: RUF022
    # guild id
    "GUILD_ID",
    # filter payloads
    "FILTERS_PAYLOAD",
    "FILTERS_EQUALIZER_PAYLOAD",
    "FILTERS_KARAOKE_PAYLOAD",
    "FILTERS_TIMESCALE_PAYLOAD",
    "FILTERS_TREMOLO_PAYLOAD",
    "FILTERS_VIBRATO_PAYLOAD",
    "FILTERS_ROTATION_PAYLOAD",
    "FILTERS_DISTORTION_PAYLOAD",
    "FILTERS_CHANNEL_MIX_PAYLOAD",
    "FILTERS_LOW_PASS_PAYLOAD",
    "TRACK_INFO_PAYLOAD",
    "TRACK_PAYLOAD",
    # player payloads
    "PLAYER_STATE_PAYLOAD",
    "PLAYER_VOICE_PAYLOAD",
    "PLAYER_PAYLOAD",
    # error payloads
    "REST_ERROR_PAYLOAD",
    "EXCEPTION_ERROR_PAYLOAD",
    # event payloads
    "READY_PAYLOAD",
    "PLAYER_UPDATE_PAYLOAD",
    "WEBSOCKET_CLOSED_PAYLOAD",
    "TRACK_START_PAYLOAD",
    "TRACK_END_PAYLOAD",
    "TRACK_EXCEPTION_PAYLOAD",
    "TRACK_STUCK_PAYLOAD",
    # info payloads
    "INFO_VERSION_PAYLOAD",
    "INFO_GIT_PAYLOAD",
    "INFO_PLUGIN_PAYLOAD",
    "INFO_PAYLOAD",
    # playlist payloads
    "PLAYLIST_INFO_PAYLOAD",
    "PLAYLIST_PAYLOAD",
    # routeplanner payloads
    "ROUTEPLANNER_FAILING_ADDRESS_PAYLOAD",
    "ROUTEPLANNER_IP_BLOCK_PAYLOAD",
    "ROUTEPLANNER_DETAILS_PAYLOAD",
    "ROUTEPLANNER_STATUS_PAYLOAD",
    # session payloads
    "SESSION_PAYLOAD",
    # statistics payloads
    "STATISTICS_MEMORY_PAYLOAD",
    "STATISTICS_CPU_PAYLOAD",
    "STATISTICS_FRAME_STATS_PAYLOAD",
    "STATISTICS_PAYLOAD",
)

GUILD_ID: typing.Final[str] = "1234567890"

FILTERS_EQUALIZER_PAYLOAD: PayloadT = {"band": 3, "gain": 0.95}

FILTERS_KARAOKE_PAYLOAD: PayloadT = {
    "level": 1,
    "monoLevel": 0.5,
    "filterBand": 4.5,
    "filterWidth": 6,
}

FILTERS_TIMESCALE_PAYLOAD: PayloadT = {"speed": 1.2, "pitch": 2.3, "rate": 4}

FILTERS_TREMOLO_PAYLOAD: PayloadT = {"frequency": 1.2, "depth": 1}

FILTERS_VIBRATO_PAYLOAD: PayloadT = {"frequency": 3, "depth": 0.5}

FILTERS_ROTATION_PAYLOAD: PayloadT = {"rotationHz": 6}

FILTERS_DISTORTION_PAYLOAD: PayloadT = {
    "sinOffset": 2.1,
    "sinScale": 3,
    "cosOffset": 6.9,
    "cosScale": 7.2,
    "tanOffset": 9.4,
    "tanScale": 2,
    "offset": 4.1,
    "scale": 8,
}

FILTERS_CHANNEL_MIX_PAYLOAD: PayloadT = {
    "leftToLeft": 0,
    "leftToRight": 1,
    "rightToLeft": 0.5,
    "rightToRight": 0.63,
}

FILTERS_LOW_PASS_PAYLOAD: PayloadT = {"smoothing": 3.8}

FILTERS_PAYLOAD: PayloadT = {
    "volume": 1.2,
    "equalizer": [FILTERS_EQUALIZER_PAYLOAD],
    "karaoke": FILTERS_KARAOKE_PAYLOAD,
    "timescale": FILTERS_TIMESCALE_PAYLOAD,
    "tremolo": FILTERS_TREMOLO_PAYLOAD,
    "vibrato": FILTERS_VIBRATO_PAYLOAD,
    "rotation": FILTERS_ROTATION_PAYLOAD,
    "distortion": FILTERS_DISTORTION_PAYLOAD,
    "channelMix": FILTERS_CHANNEL_MIX_PAYLOAD,
    "lowPass": FILTERS_LOW_PASS_PAYLOAD,
}

TRACK_INFO_PAYLOAD: PayloadT = {
    "identifier": "identifier",
    "isSeekable": False,
    "author": "author",
    "length": 1,
    "isStream": True,
    "position": 2,
    "title": "title",
    "sourceName": "source_name",
    "uri": "uri",
    "artworkUrl": "artwork_url",
    "isrc": "isrc",
}

TRACK_PAYLOAD: PayloadT = {
    "encoded": "encoded",
    "info": TRACK_INFO_PAYLOAD,
    "pluginInfo": {},
    "userData": {},
}

PLAYER_STATE_PAYLOAD: PayloadT = {
    "time": 1,
    "position": 2,
    "connected": True,
    "ping": 3,
}

PLAYER_VOICE_PAYLOAD: PayloadT = {
    "token": "token",
    "endpoint": "endpoint",
    "sessionId": "session_id",
    "channelId": "123",
}

PLAYER_PAYLOAD: PayloadT = {
    "guildId": GUILD_ID,
    "track": TRACK_PAYLOAD,
    "volume": 1,
    "paused": True,
    "state": PLAYER_STATE_PAYLOAD,
    "voice": PLAYER_VOICE_PAYLOAD,
    "filters": {},
}

REST_ERROR_PAYLOAD: PayloadT = {
    "timestamp": 1,
    "status": 2,
    "error": "error",
    "message": "message",
    "path": "path",
    "trace": "trace",
}

EXCEPTION_ERROR_PAYLOAD: PayloadT = {
    "message": "message",
    "severity": "common",
    "cause": "cause",
}

READY_PAYLOAD: PayloadT = {"op": "ready", "resumed": False, "sessionId": "session_id"}

PLAYER_UPDATE_PAYLOAD: PayloadT = {
    "op": "playerUpdate",
    "guildId": GUILD_ID,
    "state": PLAYER_STATE_PAYLOAD,
}

WEBSOCKET_CLOSED_PAYLOAD: PayloadT = {
    "op": "event",
    "type": "WebSocketClosedEvent",
    "guildId": GUILD_ID,
    "code": 1,
    "reason": "reason",
    "byRemote": False,
}

TRACK_START_PAYLOAD: PayloadT = {
    "op": "event",
    "type": "TrackStartEvent",
    "guildId": GUILD_ID,
    "track": TRACK_PAYLOAD,
}

TRACK_END_PAYLOAD: PayloadT = {
    "op": "event",
    "type": "TrackEndEvent",
    "guildId": GUILD_ID,
    "track": TRACK_PAYLOAD,
    "reason": "finished",
}

TRACK_EXCEPTION_PAYLOAD: PayloadT = {
    "op": "event",
    "type": "TrackExceptionEvent",
    "guildId": GUILD_ID,
    "track": TRACK_PAYLOAD,
    "exception": EXCEPTION_ERROR_PAYLOAD,
}

TRACK_STUCK_PAYLOAD: PayloadT = {
    "op": "event",
    "type": "TrackStuckEvent",
    "guildId": GUILD_ID,
    "track": TRACK_PAYLOAD,
    "thresholdMs": 1,
}

INFO_VERSION_PAYLOAD: PayloadT = {
    "semver": "semver",
    "major": 1,
    "minor": 2,
    "patch": 3,
    "preRelease": "pre_release",
    "build": "build",
}

INFO_GIT_PAYLOAD: PayloadT = {"branch": "branch", "commit": "commit", "commitTime": 1}

INFO_PLUGIN_PAYLOAD: PayloadT = {"name": "name", "version": "version"}

INFO_PAYLOAD: PayloadT = {
    "version": INFO_VERSION_PAYLOAD,
    "buildTime": 1,
    "git": INFO_GIT_PAYLOAD,
    "jvm": "jvm",
    "lavaplayer": "lavaplayer",
    "sourceManagers": ["source_manager_1", "source_manager_2"],
    "filters": ["filter_1", "filter_2"],
    "plugins": [INFO_PLUGIN_PAYLOAD],
}

PLAYLIST_INFO_PAYLOAD: PayloadT = {"name": "name", "selectedTrack": 1}

PLAYLIST_PAYLOAD: PayloadT = {
    "info": PLAYLIST_INFO_PAYLOAD,
    "pluginInfo": {},
    "tracks": [TRACK_PAYLOAD],
}

ROUTEPLANNER_FAILING_ADDRESS_PAYLOAD: PayloadT = {
    "failingAddress": "failing_address",
    "failingTimestamp": 1,
    "failingTime": "failing_time",
}

ROUTEPLANNER_IP_BLOCK_PAYLOAD: PayloadT = {"type": "Inet4Address", "size": "size"}

ROUTEPLANNER_DETAILS_PAYLOAD: PayloadT = {
    "ipBlock": ROUTEPLANNER_IP_BLOCK_PAYLOAD,
    "failingAddresses": [ROUTEPLANNER_FAILING_ADDRESS_PAYLOAD],
    "rotateIndex": "rotate_index",
    "ipIndex": "ip_index",
    "currentAddress": "current_address",
    "currentAddressIndex": "current_address_index",
    "blockIndex": "block_index",
}

ROUTEPLANNER_STATUS_PAYLOAD: PayloadT = {
    "class": "RotatingIpRoutePlanner",
    "details": ROUTEPLANNER_DETAILS_PAYLOAD,
}

SESSION_PAYLOAD: PayloadT = {"resuming": True, "timeout": 1}

STATISTICS_MEMORY_PAYLOAD: PayloadT = {
    "free": 1,
    "used": 2,
    "allocated": 3,
    "reservable": 4,
}

STATISTICS_CPU_PAYLOAD: PayloadT = {"cores": 1, "systemLoad": 2.3, "lavalinkLoad": 4.5}

STATISTICS_FRAME_STATS_PAYLOAD: PayloadT = {"sent": 1, "nulled": 2, "deficit": 3}

STATISTICS_PAYLOAD: PayloadT = {
    "players": 1,
    "playingPlayers": 2,
    "uptime": 3,
    "memory": STATISTICS_MEMORY_PAYLOAD,
    "cpu": STATISTICS_CPU_PAYLOAD,
    "frameStats": STATISTICS_FRAME_STATS_PAYLOAD,
}
