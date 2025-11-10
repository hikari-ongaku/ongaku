from __future__ import annotations

import typing

import pytest

from ongaku.ext import checker
from ongaku.ext.checker import Sites

ConstantParameterT: typing.TypeAlias = typing.Final[typing.Sequence[str]]

SCHEMES: typing.Final[typing.Sequence[str]] = ["http://", "https://"]


@pytest.mark.parametrize(
    "query",
    [
        "a query.",
        "http://yourmom.com?banana=vegetable",
    ],
)
def test_checker_query(query: str):
    assert checker.check(query) is None


class TestYoutube:
    @pytest.mark.parametrize(
        "path",
        [
            "/watch?v=abcd1234",
            "/watch?v=abcd1234&list=abcd1234",
            "/playlist?list=abcd1234",
        ],
    )
    @pytest.mark.parametrize("domain", ["youtube.com", "www.youtube.com", "youtu.be"])
    @pytest.mark.parametrize("scheme", SCHEMES)
    def test_working(self, scheme: str, domain: str, path: str):
        assert checker.check(scheme + domain + path) == Sites.YOUTUBE

    @pytest.mark.skip(reason="TODO")
    def test_invalid(self):
        pass


class TestYoutubeMusic:
    @pytest.mark.parametrize(
        "path",
        [
            "/watch?v=abcd1234",
            "/watch?v=abcd1234&list=abcd1234",
            "/playlist?list=abcd1234",
        ],
    )
    @pytest.mark.parametrize(
        "domain",
        [
            "music.youtube.com",
        ],
    )
    @pytest.mark.parametrize("scheme", SCHEMES)
    def test_working(self, scheme: str, domain: str, path: str):
        assert checker.check(scheme + domain + path) == Sites.YOUTUBE_MUSIC

    @pytest.mark.skip(reason="TODO")
    def test_invalid(self):
        pass


class TestBandcamp:
    @pytest.mark.parametrize(
        "path",
        [
            "/track/abcd1234",
            "/album/abcd1234",
            "/track/abcd1234?abcd=1234",
            "/album/abcd1234?abcd=1234",
        ],
    )
    @pytest.mark.parametrize(
        "domain",
        [
            "bandcamp.com",
            "www.bandcamp.com",
            "test.bandcamp.com",
        ],
    )
    @pytest.mark.parametrize("scheme", SCHEMES)
    def test_working(self, scheme: str, domain: str, path: str):
        assert checker.check(scheme + domain + path) == Sites.BANDCAMP

    @pytest.mark.skip(reason="TODO")
    def test_invalid(self):
        pass


class TestSoundcloud:
    @pytest.mark.parametrize(
        "url",
        [
            "soundcloud.com/user1234/song1234",
            "www.soundcloud.com/band/abcd1234",
            "m.soundcloud.com/dj/super-mix?abcd=1234",
            "soundcloud.com/user1234/song1234/s-abcd1234",
            "www.soundcloud.com/band/album1234/s-abcd1234",
            "m.soundcloud.com/dj/super-mix/s-abcd1234?abcd=1234",
            "soundcloud.com/user123/likes",
            "soundcloud.com/artist/likes",
            "www.soundcloud.com/band/likes",
            "m.soundcloud.com/dj/likes?abcd=1234",
        ],
    )
    @pytest.mark.parametrize("scheme", SCHEMES)
    def test_working(self, scheme: str, url: str):
        assert checker.check(scheme + url) == Sites.SOUNDCLOUD

    @pytest.mark.parametrize(
        "url",
        [
            "https://on.soundcloud.com/abcd1234",
            "https://on.soundcloud.com/abcd1234?abcd=1234",
        ],
    )
    def test_working_https_only(self, url: str):
        assert checker.check(url) == Sites.SOUNDCLOUD

    @pytest.mark.skip(reason="TODO")
    def test_invalid(self):
        pass


class TestTwitch:
    @pytest.mark.parametrize(
        "url",
        [
            "https://twitch.tv/user1234",
            "https://www.twitch.tv/user1234",
            "https://go.twitch.tv/user1234",
            "https://m.twitch.tv/user1234",
        ],
    )
    def test_working(self, url: str):
        assert checker.check(url) == Sites.TWITCH

    @pytest.mark.skip(reason="TODO")
    def test_invalid(self):
        pass


class TestVimeo:
    @pytest.mark.parametrize(
        "url",
        [
            "https://vimeo.com/1234567890",
            "https://vimeo.com/1234567890?abcd=1234",
        ],
    )
    def test_working(self, url: str):
        assert checker.check(url) == Sites.VIMEO

    @pytest.mark.skip(reason="TODO")
    def test_invalid(self):
        pass


class TestNico:
    @pytest.mark.parametrize(
        "path",
        [
            "/watch/sm1234",
            "/watch/sm1234?abcd=1234",
        ],
    )
    @pytest.mark.parametrize(
        "domain",
        [
            "nicovideo.jp",
            "www.nicovideo.jp",
        ],
    )
    @pytest.mark.parametrize("scheme", SCHEMES)
    def test_working(self, scheme: str, domain: str, path: str):
        assert checker.check(scheme + domain + path) == Sites.NICO

    @pytest.mark.skip(reason="TODO")
    def test_invalid(self):
        pass


class TestSpotify:
    @pytest.mark.parametrize(
        "path",
        [
            "/track/abcd1234",
            "/playlist/abcd1234",
            "/album/abcd1234",
            "/user/spotify/playlist/abcd1234",
            "/artist/abcd1234",
            "/us/user/spotify/track/abcd1234",
        ],
    )
    @pytest.mark.parametrize(
        "domain",
        [
            "www.open.spotify.com",
            "open.spotify.com",
        ],
    )
    @pytest.mark.parametrize("scheme", SCHEMES)
    def test_working(self, scheme: str, domain: str, path: str):
        assert checker.check(scheme + domain + path) == Sites.SPOTIFY

    @pytest.mark.skip(reason="TODO")
    def test_invalid(self):
        pass


class TestApple:
    @pytest.mark.parametrize(
        "path",
        [
            "/song/1234",
            "/playlist/1234",
            "/artist/1234",
            "/album/1234",
            "/us/album/1234",
            "/artist/1234?i=1234",
            "/song/1234?i=1234",
        ],
    )
    @pytest.mark.parametrize(
        "domain",
        [
            "www.music.apple.com",
            "music.apple.com",
        ],
    )
    @pytest.mark.parametrize("scheme", SCHEMES)
    def test_working(self, scheme: str, domain: str, path: str):
        assert checker.check(scheme + domain + path) == Sites.APPLE

    @pytest.mark.skip(reason="TODO")
    def test_invalid(self):
        pass


class TestDeezer:
    @pytest.mark.parametrize(
        "path",
        [
            "/track/1234",
            "/album/1234",
            "/playlist/1234",
            "/artist/1234",
            "/us/track/1234",
        ],
    )
    @pytest.mark.parametrize(
        "domain",
        [
            "www.deezer.com",
            "deezer.com",
        ],
    )
    @pytest.mark.parametrize("scheme", SCHEMES)
    def test_working(self, scheme: str, domain: str, path: str):
        assert checker.check(scheme + domain + path) == Sites.DEEZER

    @pytest.mark.skip(reason="TODO")
    def test_invalid(self):
        pass


class TestYandex:
    @pytest.mark.parametrize(
        "path",
        [
            "/artist/1234",
            "/album/1234",
            "/track/1234",
            "/track/1234/track/1234",
            "/artist/1234/track/1234",
        ],
    )
    @pytest.mark.parametrize(
        "domain",
        [
            "music.yandex.ru",
            "music.yandex.com",
            "music.yandex.kz",
            "music.yandex.by",
        ],
    )
    @pytest.mark.parametrize("scheme", SCHEMES)
    def test_working(self, scheme: str, domain: str, path: str):
        assert checker.check(scheme + domain + path) == Sites.YANDEX

    @pytest.mark.skip(reason="TODO")
    def test_invalid(self):
        pass
