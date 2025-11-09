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
"""Checker.

The extension, that allows you to check if a link is a url, or a video/playlist!
"""

from __future__ import annotations

import enum
import typing

import regex

__all__ = (
    "Sites",
    "check",
)


class Sites(enum.IntEnum):
    """Sites.

    All the available sites for lavalink.

    all sites are checked for `http` and `https`,
    except for twitch and vimeo, which are only `https`.

    !!! warning
        Some sites are only useable with plugins.
    """

    YOUTUBE = 1
    """Youtube.

    ??? tip "Checked URL's"

        - `youtube.com/watch`
        - `youtube.com/playlist`
        - `www.youtube.com/watch`
        - `www.youtube.com/playlist`
        - `youtu.be/watch`
        - `youtu.be/playlist`
    """
    YOUTUBE_MUSIC = 2
    """Youtube Music.

    ??? tip "Checked URL's"

        - music.youtube.com/watch
        - music.youtube.com/playlist
    """
    BANDCAMP = 3
    """Bandcamp.

    ??? tip "Checked URL's"

        - `bandcamp.com/track/`
        - `bandcamp.com/album/`
        - `www.bandcamp.com/track/`
        - `www.bandcamp.com/album/`
        - `xxxx.bandcamp.com/track/`
        - `xxxx.bandcamp.com/album/`

        Please note that `xxxx` can be anything.
    """
    SOUNDCLOUD = 4
    """Soundcloud.

    ??? tip "Checked URL's"

        - `soundcloud.com/user/song`
        - `www.soundcloud.com/band/`
        - `m.soundcloud.com/dj/`
        - `on.soundcloud.com/`
        - `soundcloud.com/user/song/`
        - `www.soundcloud.com/band/album/`
        - `m.soundcloud.com/dj/super-mix/`
        - `soundcloud.com/user123/likes`
        - `soundcloud.com/artist/likes`
        - `www.soundcloud.com/band/likes`
        - `m.soundcloud.com/dj/likes`
    """
    TWITCH = 5
    """Twitch.

    ??? tip "Checked URL's"

        - `twitch.tv/`
        - `www.twitch.tv/`
        - `go.twitch.tv/`
        - `m.twitch.tv/`
    """
    VIMEO = 6
    """Vimeo.

    ??? tip "Checked URL's"

        - `vimeo.com/1234567890`
    """
    NICO = 7
    """Nico.

    ??? tip "Checked URL's"

        - `nicovideo.jp/watch/`
        - `www.nicovideo.jp/watch/`

    """
    SPOTIFY = 8
    """Spotify.

    ??? tip "Checked URL's"

        - `www.open.spotify.com/track/`
        - `www.open.spotify.com/playlist/`
        - `www.open.spotify.com/album/`
        - `www.open.spotify.com/user/spotify/playlist/`
        - `www.open.spotify.com/artist/`
        - `www.open.spotify.com/us/user/spotify/track/`
        - `open.spotify.com/track/`
        - `open.spotify.com/playlist/`
        - `open.spotify.com/album/`
        - `open.spotify.com/user/spotify/playlist/`
        - `open.spotify.com/artist/`
        - `open.spotify.com/us/user/spotify/track/`

    """
    APPLE = 9
    """Apple.

    ??? tip "Checked URL's"

        - `www.music.apple.com/song/`
        - `www.music.apple.com/playlist/`
        - `www.music.apple.com/artist/`
        - `www.music.apple.com/album/`
        - `www.music.apple.com/us/album/`
        - `music.apple.com/song/`
        - `music.apple.com/playlist/`
        - `music.apple.com/artist/`
        - `music.apple.com/album/`
        - `music.apple.com/us/album/`
    """
    DEEZER = 10
    """Deezer.

    ??? tip "Checked URL's"

        - `www.deezer.com/track/`
        - `www.deezer.com/album/`
        - `www.deezer.com/playlist/`
        - `www.deezer.com/artist/`
        - `www.deezer.com/us/track/`
        - `deezer.com/track/`
        - `deezer.com/album/`
        - `deezer.com/playlist/`
        - `deezer.com/artist/`
        - `deezer.com/us/track/`
    """
    YANDEX = 11
    """Yandex.

    ??? tip "Checked URL's"

        - `music.yandex.ru/artist/`
        - `music.yandex.ru/album/`
        - `music.yandex.ru/track/`
        - `music.yandex.com/artist/`
        - `music.yandex.com/album/`
        - `music.yandex.com/track/`
        - `music.yandex.kz/artist/`
        - `music.yandex.kz/album/`
        - `music.yandex.kz/track/`
        - `music.yandex.by/artist/`
        - `music.yandex.by/album/`
        - `music.yandex.by/track/`
    """

    @classmethod
    def all(cls) -> typing.Sequence[Sites]:
        """All possible sources."""
        return (
            Sites.YOUTUBE,
            Sites.YOUTUBE_MUSIC,
            Sites.BANDCAMP,
            Sites.SOUNDCLOUD,
            Sites.TWITCH,
            Sites.VIMEO,
            Sites.NICO,
            Sites.SPOTIFY,
            Sites.APPLE,
            Sites.DEEZER,
            Sites.YANDEX,
        )

    @classmethod
    def default(cls) -> typing.Sequence[Sites]:
        """All possible sources without plugins."""
        return (
            Sites.YOUTUBE,
            Sites.YOUTUBE_MUSIC,
            Sites.BANDCAMP,
            Sites.SOUNDCLOUD,
            Sites.TWITCH,
            Sites.VIMEO,
            Sites.NICO,
        )


def check(query: str) -> Sites | None:
    """Check.

    Allows for the user to check a current string, and see what type it is.

    !!! warning
        Just because a value got rejected, does not mean it is not a url.

        **only** Lavalink/LavaSrc url regex's are supported.

    Example
    -------
    ```py
    from ongaku.ext import checker

    if checker.check(query):
        print("This is a video/playlist/album!")
    else:
        print("This is a query.")
    ```

    Example
    -------
    ```py
    from ongaku.ext import checker

    if checker.check(query) == Sites.SPOTIFY:
        print("This is a spotify link!")
    else:
        print("This is not a spotify link.")
    ```

    Parameters
    ----------
    query
        The query you wish to check.

    Returns
    -------
    bool
        If True, then it is a video/playlist, otherwise its just a query.
    """
    site_patterns: typing.Mapping[Sites, str | typing.Sequence[str]] = {
        Sites.YOUTUBE: [
            r"^(?:http:\/\/|https:\/\/|)(?:www\.|m\.|)youtube\.com\/.*",
            r"^(?:http:\/\/|https:\/\/|)(?:www\.|)youtu\.be\/.*",
            r"^(?:http:\/\/|https:\/\/|)(?:www\.|m\.|)youtube\.com\/embed\/.*",
            r"^(?:http:\/\/|https:\/\/|)(?:www\.|m\.|)youtube\.com\/shorts\/.*",
            r"^(?:http:\/\/|https:\/\/|)(?:www\.|m\.|)youtube\.com\/live\/.*",
        ],
        Sites.YOUTUBE_MUSIC: r"^(?:http:\/\/|https:\/\/|)music\.youtube\.com\/.*",
        Sites.BANDCAMP: r"^(https?:\/\/(?:[^.]+\.|)bandcamp\.com)\/(track|album)\/([a-zA-Z0-9-_]+)\/?(?:\\?.*|)$",  # noqa: E501
        Sites.SOUNDCLOUD: [
            r"^https?:\/\/soundcloud\.app\.goo\.gl\/([a-zA-Z0-9-_]+)\/?(?:\?.*|)$",
            r"^https?:\/\/(?:www\.|)(?:m\.|)soundcloud\.com\/([a-zA-Z0-9-_]+)\/([a-zA-Z0-9-_]+)\/?(?:\?.*|)$",
            r"^https:\/\/on\.soundcloud\.com\/[a-zA-Z0-9-_]+\/?(?:\?.*|)$",
            r"^https?:\/\/(?:www\.|)(?:m\.|)soundcloud\.com\/([a-zA-Z0-9-_]+)\/([a-zA-Z0-9-_]+)\/s-([a-zA-Z0-9-_]+)(?:\?.*|)$",
            r"^https?:\/\/(?:www\.|)(?:m\.|)soundcloud\.com\/([a-zA-Z0-9-_]+)\/likes\/?(?:\?.*|)$",
        ],
        Sites.TWITCH: r"^https:\/\/(?:www\.|go\.|m\.)?twitch\.tv\/([^/]+)$",
        Sites.VIMEO: r"^https?:\/\/vimeo\.com\/([0-9]+)(?:\?.*|)$",
        Sites.NICO: r"^(https?:\/\/)?(?:www\.|)nicovideo\.jp\/watch\/(.{2}[0-9]+)(?:\?.*|)$",  # noqa: E501
        Sites.SPOTIFY: r"(https?:\/\/)(www\.)?open\.spotify\.com\/(([a-zA-Z-]+)\/)?(user\/([a-zA-Z0-9-_]+)\/)?(track|album|playlist|artist)\/([a-zA-Z0-9-_]+)",  # noqa: E501
        Sites.APPLE: r"(https?:\/\/)?(www\.)?music\.apple\.com\/(([a-zA-Z]{2})\/)?(album|playlist|artist|song)(\/[a-zA-Z\p{L}\d\-]+)?\/([a-zA-Z\d\-.]+)(\?i=(\d+))?",  # noqa: E501
        Sites.DEEZER: r"(https?:\/\/)?(www\.)?deezer\.com\/([a-zA-Z]{2}\/)?(track|album|playlist|artist)\/([0-9]+)",  # noqa: E501
        Sites.YANDEX: [
            r"(https?:\/\/)?music\.yandex\.(ru|com|kz|by)\/(artist|album|track)\/([0-9]+)(\/(track)\/([0-9]+))?\/?",
            r"(https?:\/\/)?music\.yandex\.(ru|com|kz|by)\/users\/([0-9A-Za-z@.-]+)\/playlists\/([0-9]+)\/?",
        ],
    }

    for site, pattern in site_patterns.items():
        regex_patterns: typing.MutableSequence[str] = []
        if isinstance(pattern, str):
            regex_patterns.append(pattern)
        else:
            regex_patterns.extend(pattern)

        if any(regex.compile(rx).match(query) is not None for rx in regex_patterns):
            return site

    return None
