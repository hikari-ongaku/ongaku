from __future__ import annotations

import typing

import pytest

from ongaku.impl.playlist import Playlist
from ongaku.impl.playlist import PlaylistInfo
from ongaku.impl.track import Track
from ongaku.impl.track import TrackInfo


@pytest.fixture
def track() -> Track:
    track_info = TrackInfo(
        "identifier",
        False,
        "author",
        1,
        True,
        2,
        "title",
        "source_name",
        "uri",
        "artwork_url",
        "isrc",
    )
    return Track("encoded", track_info, {}, {}, None)


def test_playlist_info():
    playlist_info = PlaylistInfo("name", 1)

    assert playlist_info.name == "name"
    assert playlist_info.selected_track == 1


def test_playlist(track: Track):
    info = PlaylistInfo("name", 1)
    playlist = Playlist(info, [track], {})

    assert playlist.info == info
    assert playlist.plugin_info == {}
    assert isinstance(playlist.tracks, typing.Sequence)
    assert len(playlist.tracks) == 1
    assert playlist.tracks[0] == track
