from __future__ import annotations

from unittest import mock

from ongaku.playlist import Playlist
from ongaku.playlist import PlaylistInfo


def test_playlist_info():
    playlist_info = PlaylistInfo(name="name", selected_track=1)

    assert playlist_info.name == "name"
    assert playlist_info.selected_track == 1


def test_playlist():
    mock_info = mock.Mock()
    mock_track_1 = mock.Mock()
    mock_track_2 = mock.Mock()

    playlist = Playlist(
        info=mock_info,
        tracks=[mock_track_1, mock_track_2],
        plugin_info={},
    )

    assert playlist.info == mock_info
    assert playlist.plugin_info == {}
    assert playlist.tracks == [mock_track_1, mock_track_2]
