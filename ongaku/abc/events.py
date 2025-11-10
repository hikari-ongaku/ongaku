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
"""Abstract event objects."""

from __future__ import annotations

import abc
import typing

import hikari

if typing.TYPE_CHECKING:
    from ongaku import session
    from ongaku import track
    from ongaku.client import Client

__all__: typing.Sequence[str] = ("OngakuEvent", "QueueEvent", "TrackEvent")


class OngakuEvent(hikari.Event, abc.ABC):
    """Ongaku Event.

    The base ongaku event, that adds the client and session to all events.
    """

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def client(self) -> Client:
        """The ongaku client attached to the event."""

    @property
    @abc.abstractmethod
    def session(self) -> session.Session:
        """The session attached to the event."""


class SessionEvent(OngakuEvent, abc.ABC):
    """Session Event.

    Dispatched when a session event occurs.
    """


class TrackEvent(OngakuEvent, abc.ABC):
    """Track Event.

    Dispatched when a track event occurs.
    """

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def guild_id(self) -> hikari.Snowflake:
        """The guild ID related to this event."""

    @property
    @abc.abstractmethod
    def track(self) -> track.Track:
        """The track related to this event."""


class QueueEvent(OngakuEvent):
    """Queue event.

    Dispatched when the queue gets changed.
    """

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def guild_id(self) -> hikari.Snowflake:
        """The guild ID related to this event."""

    @property
    @abc.abstractmethod
    def old_track(self) -> track.Track:
        """The track that was previously playing."""
