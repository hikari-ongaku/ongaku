"""
Player ABC's.

The player Abstract classes.
"""

from __future__ import annotations

import abc
import typing

if typing.TYPE_CHECKING:
    import datetime

    import hikari

    from ongaku.abc.filters import Filters
    from ongaku.abc.track import Track

__all__ = (
    "Player",
    "State",
    "Voice",
)


class Player(abc.ABC):
    """
    Player information.

    All of the information about the player, for the specified guild.

    ![Lavalink](../../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest.html#player)
    """

    __slots__: typing.Sequence[str] = (
        "_filters",
        "_guild_id",
        "_is_paused",
        "_state",
        "_track",
        "_voice",
        "_volume",
    )

    @property
    def guild_id(self) -> hikari.Snowflake:
        """The guild id this player is attached too."""
        return self._guild_id

    @property
    def track(self) -> Track | None:
        """The track the player is currently playing.

        !!! note
            If the track is `None` then there is no current track playing.
        """
        return self._track

    @property
    def volume(self) -> int:
        """The volume of the player."""
        return self._volume

    @property
    def is_paused(self) -> bool:
        """Whether the player is paused."""
        return self._is_paused

    @property
    def state(self) -> State:
        """The player's state."""
        return self._state

    @property
    def voice(self) -> Voice:
        """The player's voice state."""
        return self._voice

    @property
    def filters(self) -> Filters | None:
        """The filter object."""
        return self._filters

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return False

        if self.guild_id != other.guild_id:
            return False

        if self.track != other.track:
            return False

        if self.volume != other.volume:
            return False

        if self.is_paused != other.is_paused:
            return False

        if self.state != other.state:
            return False

        if self.voice != other.voice:
            return False

        return self.filters == other.filters


class State(abc.ABC):
    """
    Players State.

    All the information for the players current state.

    ![Lavalink](../../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/websocket.html#player-state)
    """

    __slots__: typing.Sequence[str] = (
        "_connected",
        "_ping",
        "_position",
        "_time",
    )

    @property
    def time(self) -> datetime.datetime:
        """The current datetime."""
        return self._time

    @property
    def position(self) -> int:
        """The position of the track in milliseconds."""
        return self._position

    @property
    def connected(self) -> bool:
        """Whether Lavalink is connected to the voice gateway."""
        return self._connected

    @property
    def ping(self) -> int:
        """The ping of the session to the Discord voice server in milliseconds (-1 if not connected)."""
        return self._ping

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, State):
            return False

        if self.time != other.time:
            return False

        if self.position != other.position:
            return False

        if self.connected != other.connected:
            return False

        return self.ping == other.ping


class Voice(abc.ABC):
    """
    Players Voice state.

    All of the Player Voice information.

    ![Lavalink](../../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest.html#voice-state)
    """

    __slots__: typing.Sequence[str] = (
        "_channel_id",
        "_endpoint",
        "_session_id",
        "_token",
    )

    @property
    def token(self) -> str:
        """The Discord voice token to authenticate with."""
        return self._token

    @property
    def endpoint(self) -> str:
        """The Discord voice endpoint to connect to."""
        return self._endpoint

    @property
    def session_id(self) -> str:
        """The Discord voice session id to authenticate with."""
        return self._session_id

    @property
    def channel_id(self) -> hikari.Snowflake | None:
        """The channel the bot is currently connected to."""
        return self._channel_id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Voice):
            return False

        if self.token != other.token:
            return False

        if self.endpoint != other.endpoint:
            return False

        if self.session_id != other.session_id:
            return False

        return self.channel_id == other.channel_id

    def __str__(self) -> str:
        return f"Voice(token={self.token}, endpoint={self.endpoint}, session_id={self.session_id}, channel_id={self.channel_id})"

    def __repr__(self) -> str:
        return f"Voice(token={self.token}, endpoint={self.endpoint}, session_id={self.session_id}, channel_id={self.channel_id})"


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
