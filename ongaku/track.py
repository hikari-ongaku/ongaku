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
"""Track and entities related to Lavalink track objects."""

from __future__ import annotations

import enum
import typing

if typing.TYPE_CHECKING:
    import hikari


__all__: typing.Sequence[str] = (
    "Track",
    "TrackEndReasonType",
    "TrackInfo",
)


class Track:
    """Track.

    The track object.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest.html#track)
    """

    __slots__: typing.Sequence[str] = (
        "_encoded",
        "_info",
        "_plugin_info",
        "_requestor",
        "_user_data",
    )

    def __init__(
        self,
        *,
        encoded: str,
        info: TrackInfo,
        plugin_info: typing.Mapping[str, typing.Any],
        user_data: typing.Mapping[str, typing.Any],
        requestor: hikari.Snowflake | None,
    ) -> None:
        self._encoded = encoded
        self._info = info
        self._plugin_info = plugin_info
        self._user_data = user_data
        self._requestor = requestor

    @property
    def encoded(self) -> str:
        """The BASE-64 encoded track data."""
        return self._encoded

    @property
    def info(self) -> TrackInfo:
        """Information about the track."""
        return self._info

    @property
    def plugin_info(self) -> typing.Mapping[str, typing.Any]:
        """Additional track info provided by plugins."""
        return self._plugin_info

    @property
    def user_data(self) -> typing.Mapping[str, typing.Any]:
        """Additional track data.

        !!! warning
            If you store a value of any type,
              under the name `ongaku_requestor` it **will** be overridden.
        """
        return self._user_data

    @user_data.setter
    def user_data(self, value: typing.Mapping[str, typing.Any]) -> None:
        """Set user data."""
        self._user_data = value

    @property
    def requestor(self) -> hikari.Snowflake | None:
        """The person who requested this track."""
        return self._requestor

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Track):
            return False

        return (
            self.encoded == other.encoded
            and self.info == other.info
            and self.plugin_info == other.plugin_info
            and self.user_data == other.user_data
            and self.requestor == other.requestor
        )

    def __hash__(self) -> int:
        return hash(
            (self.encoded, self.info, self.plugin_info, self.user_data, self.requestor),
        )


class TrackInfo:
    """Track Information.

    The track information object.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest.html#track-info)
    """

    __slots__: typing.Sequence[str] = (
        "_artwork_url",
        "_author",
        "_identifier",
        "_is_seekable",
        "_is_stream",
        "_isrc",
        "_length",
        "_position",
        "_source_name",
        "_title",
        "_uri",
    )

    def __init__(  # noqa: PLR0913
        self,
        *,
        identifier: str,
        is_seekable: bool,
        author: str,
        length: int,
        is_stream: bool,
        position: int,
        title: str,
        source_name: str,
        uri: str | None,
        artwork_url: str | None,
        isrc: str | None,
    ) -> None:
        self._identifier = identifier
        self._is_seekable = is_seekable
        self._author = author
        self._length = length
        self._is_stream = is_stream
        self._position = position
        self._title = title
        self._source_name = source_name
        self._uri = uri
        self._artwork_url = artwork_url
        self._isrc = isrc

    @property
    def identifier(self) -> str:
        """The track identifier."""
        return self._identifier

    @property
    def is_seekable(self) -> bool:
        """Whether the track is seekable."""
        return self._is_seekable

    @property
    def author(self) -> str:
        """The track author."""
        return self._author

    @property
    def length(self) -> int:
        """The track length in milliseconds."""
        return self._length

    @property
    def is_stream(self) -> bool:
        """Whether the track is a stream."""
        return self._is_stream

    @property
    def position(self) -> int:
        """The track position in milliseconds."""
        return self._position

    @property
    def title(self) -> str:
        """The track title."""
        return self._title

    @property
    def source_name(self) -> str:
        """The tracks source name."""
        return self._source_name

    @property
    def uri(self) -> str | None:
        """The track URI."""
        return self._uri

    @property
    def artwork_url(self) -> str | None:
        """The track artwork URL."""
        return self._artwork_url

    @property
    def isrc(self) -> str | None:
        """The track ISRC."""
        return self._isrc

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrackInfo):
            return False

        return (
            self.identifier == other.identifier
            and self.is_seekable == other.is_seekable
            and self.author == other.author
            and self.length == other.length
            and self.is_stream == other.is_stream
            and self.position == other.position
            and self.title == other.title
            and self.source_name == other.source_name
            and self.uri == other.uri
            and self.artwork_url == other.artwork_url
            and self.isrc == other.isrc
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.identifier,
                self.is_seekable,
                self.author,
                self.length,
                self.is_stream,
                self.position,
                self.title,
                self.source_name,
                self.uri,
                self.artwork_url,
                self.isrc,
            ),
        )


class TrackEndReasonType(str, enum.Enum):
    """Track end reason type.

    The track end reason type for the track that was just playing.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/websocket#track-end-reason)
    """

    FINISHED = "finished"
    """The track finished playing."""
    LOADFAILED = "loadFailed"
    """The track failed to load."""
    STOPPED = "stopped"
    """The track was stopped."""
    REPLACED = "replaced"
    """The track was replaced."""
    CLEANUP = "cleanup"
    """The track was cleaned up."""
