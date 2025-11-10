from __future__ import annotations

from unittest import mock

from ongaku.track import Track
from ongaku.track import TrackInfo


def test_track():
    mock_track_info = mock.Mock()

    track = Track(
        encoded="encoded",
        info=mock_track_info,
        plugin_info={},
        user_data={},
        requestor=None,
    )

    assert track.encoded == "encoded"
    assert track.info == mock_track_info
    assert track.plugin_info == {}
    assert track.user_data == {}
    assert track.requestor is None


def test_set_user_data_track():
    mock_track_info = mock.Mock()

    track = Track(
        encoded="encoded",
        info=mock_track_info,
        plugin_info={},
        user_data={},
        requestor=None,
    )

    assert track.user_data == {}

    track.user_data = {"beanos": "beanos"}

    assert track.user_data == {"beanos": "beanos"}


def test_track_info():
    track_info = TrackInfo(
        identifier="identifier",
        is_seekable=False,
        author="author",
        length=100,
        is_stream=True,
        position=2,
        title="title",
        source_name="source_name",
        uri="uri",
        artwork_url="artwork_url",
        isrc="isrc",
    )

    assert track_info.identifier == "identifier"
    assert track_info.is_seekable is False
    assert track_info.author == "author"
    assert track_info.length == 100
    assert track_info.is_stream is True
    assert track_info.position == 2
    assert track_info.title == "title"
    assert track_info.source_name == "source_name"
    assert track_info.uri == "uri"
    assert track_info.artwork_url == "artwork_url"
    assert track_info.isrc == "isrc"
