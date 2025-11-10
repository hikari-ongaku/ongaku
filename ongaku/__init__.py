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
"""A voice handling library for hikari.

GitHub:
https://github.com/hikari-ongaku/hikari-ongaku
Docs:
https://ongaku.mplaty.com
"""

from __future__ import annotations

from ongaku.abc.events import OngakuEvent
from ongaku.abc.events import QueueEvent
from ongaku.abc.events import SessionEvent
from ongaku.abc.events import TrackEvent
from ongaku.api import BasicHandler
from ongaku.api import FiltersBuilder
from ongaku.client import Client
from ongaku.errors import BuildError
from ongaku.errors import BuildTypeError
from ongaku.errors import BuildUnknownVariantError
from ongaku.errors import ClientAliveError
from ongaku.errors import ClientError
from ongaku.errors import ExceptionError
from ongaku.errors import NoSessionsError
from ongaku.errors import OngakuError
from ongaku.errors import PlayerConnectError
from ongaku.errors import PlayerConnectEventMissingError
from ongaku.errors import PlayerError
from ongaku.errors import PlayerMissingError
from ongaku.errors import PlayerNotConnectedError
from ongaku.errors import PlayerQueueEmptyError
from ongaku.errors import PlayerQueueError
from ongaku.errors import PlayerQueueLengthError
from ongaku.errors import RestEmptyError
from ongaku.errors import RestError
from ongaku.errors import RestRequestError
from ongaku.errors import RestStatusError
from ongaku.errors import SessionClientSessionMissingError
from ongaku.errors import SessionError
from ongaku.errors import SessionHandlerError
from ongaku.errors import SessionMissingBotInformationError
from ongaku.errors import SessionMissingError
from ongaku.errors import SessionStartError
from ongaku.errors import SeverityType
from ongaku.events import PayloadEvent
from ongaku.events import PlayerUpdateEvent
from ongaku.events import QueueEmptyEvent
from ongaku.events import QueueNextEvent
from ongaku.events import ReadyEvent
from ongaku.events import SessionConnectedEvent
from ongaku.events import SessionDisconnectedEvent
from ongaku.events import SessionErrorEvent
from ongaku.events import StatisticsEvent
from ongaku.events import TrackEndEvent
from ongaku.events import TrackExceptionEvent
from ongaku.events import TrackStartEvent
from ongaku.events import TrackStuckEvent
from ongaku.events import WebsocketClosedEvent
from ongaku.filters import BandType
from ongaku.filters import Filters
from ongaku.information import Information
from ongaku.internal.about import __author__
from ongaku.internal.about import __author_email__
from ongaku.internal.about import __license__
from ongaku.internal.about import __maintainer__
from ongaku.internal.about import __url__
from ongaku.internal.about import __version__
from ongaku.player import PartialPlayer
from ongaku.player import Player
from ongaku.playlist import Playlist
from ongaku.routeplanner import IPBlockType
from ongaku.routeplanner import RoutePlannerStatus
from ongaku.session import PartialSession
from ongaku.session import Session
from ongaku.session import SessionStatus
from ongaku.statistics import Statistics
from ongaku.track import Track

__all__ = (
    "BandType",
    "BasicHandler",
    "BuildError",
    "BuildTypeError",
    "BuildUnknownVariantError",
    "Client",
    "ClientAliveError",
    "ClientError",
    "ExceptionError",
    "Filters",
    "FiltersBuilder",
    "IPBlockType",
    "Information",
    "NoSessionsError",
    "OngakuError",
    "OngakuEvent",
    "PartialPlayer",
    "PartialSession",
    "PayloadEvent",
    "Player",
    "PlayerConnectError",
    "PlayerConnectEventMissingError",
    "PlayerError",
    "PlayerMissingError",
    "PlayerNotConnectedError",
    "PlayerQueueEmptyError",
    "PlayerQueueError",
    "PlayerQueueLengthError",
    "PlayerUpdateEvent",
    "Playlist",
    "QueueEmptyEvent",
    "QueueEvent",
    "QueueNextEvent",
    "ReadyEvent",
    "RestEmptyError",
    "RestError",
    "RestRequestError",
    "RestStatusError",
    "RoutePlannerStatus",
    "Session",
    "SessionClientSessionMissingError",
    "SessionConnectedEvent",
    "SessionDisconnectedEvent",
    "SessionError",
    "SessionErrorEvent",
    "SessionEvent",
    "SessionHandlerError",
    "SessionMissingBotInformationError",
    "SessionMissingError",
    "SessionStartError",
    "SessionStatus",
    "SeverityType",
    "Statistics",
    "StatisticsEvent",
    "Track",
    "TrackEndEvent",
    "TrackEvent",
    "TrackExceptionEvent",
    "TrackStartEvent",
    "TrackStuckEvent",
    "WebsocketClosedEvent",
    "__author__",
    "__author_email__",
    "__license__",
    "__maintainer__",
    "__url__",
    "__version__",
)
