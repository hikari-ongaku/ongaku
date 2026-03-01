"""
Info Impl's.

The info implemented classes.
"""

from __future__ import annotations

import typing

from ongaku.abc import filters as filters_
from ongaku.abc import player as player_
from ongaku.abc import track as track_

if typing.TYPE_CHECKING:
    import datetime

    import hikari

__all__ = ("Player", "State", "Voice")


class Player(player_.Player):
    def __init__(
        self,
        guild_id: hikari.Snowflake,
        track: track_.Track | None,
        volume: int,
        is_paused: bool,
        state: player_.State,
        voice: player_.Voice,
        filters: filters_.Filters | None,
    ) -> None:
        self._guild_id = guild_id
        self._track = track
        self._volume = volume
        self._is_paused = is_paused
        self._state = state
        self._voice = voice
        self._filters = filters


class State(player_.State):
    def __init__(
        self,
        time: datetime.datetime,
        position: int,
        connected: bool,
        ping: int,
    ) -> None:
        self._time = time
        self._position = position
        self._connected = connected
        self._ping = ping


class Voice(player_.Voice):
    def __init__(
        self,
        token: str,
        endpoint: str,
        session_id: str,
        channel_id: hikari.Snowflake | None,
    ) -> None:
        self._token = token
        self._endpoint = endpoint
        self._session_id = session_id
        self._channel_id = channel_id


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
