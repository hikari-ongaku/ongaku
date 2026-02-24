from __future__ import annotations

from ongaku.impl.track import Track
from ongaku.impl.track import TrackInfo


def test_track():
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
    track = Track("encoded", track_info, {}, {}, None)

    assert track.encoded == "encoded"
    assert track.info == track_info
    assert track.plugin_info == {}
    assert track.user_data == {}
    assert track.requestor is None


def test_track_info():
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

    assert track_info.identifier == "identifier"
    assert track_info.is_seekable is False
    assert track_info.author == "author"
    assert track_info.length == 1
    assert track_info.is_stream is True
    assert track_info.position == 2
    assert track_info.title == "title"
    assert track_info.source_name == "source_name"
    assert track_info.uri == "uri"
    assert track_info.artwork_url == "artwork_url"
    assert track_info.isrc == "isrc"
