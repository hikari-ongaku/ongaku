from __future__ import annotations

from unittest import mock

from ongaku.filters import BandType
from ongaku.filters import ChannelMix
from ongaku.filters import Distortion
from ongaku.filters import Equalizer
from ongaku.filters import Filters
from ongaku.filters import Karaoke
from ongaku.filters import LowPass
from ongaku.filters import Rotation
from ongaku.filters import Timescale
from ongaku.filters import Tremolo
from ongaku.filters import Vibrato


def test_filters():
    mock_equalizer_1 = mock.Mock()
    mock_equalizer_2 = mock.Mock()
    mock_karaoke = mock.Mock()
    mock_timescale = mock.Mock()
    mock_tremolo = mock.Mock()
    mock_vibrato = mock.Mock()
    mock_rotation = mock.Mock()
    mock_distortion = mock.Mock()
    mock_channel_mix = mock.Mock()
    mock_low_pass = mock.Mock()

    filters = Filters(
        volume=1.5,
        equalizer=[mock_equalizer_1, mock_equalizer_2],
        karaoke=mock_karaoke,
        timescale=mock_timescale,
        tremolo=mock_tremolo,
        vibrato=mock_vibrato,
        rotation=mock_rotation,
        distortion=mock_distortion,
        channel_mix=mock_channel_mix,
        low_pass=mock_low_pass,
        plugin_filters={"plugin": "filters"},
    )

    assert filters.volume == 1.5
    assert filters.equalizer == [mock_equalizer_1, mock_equalizer_2]
    assert filters.karaoke == mock_karaoke
    assert filters.timescale == mock_timescale
    assert filters.tremolo == mock_tremolo
    assert filters.vibrato == mock_vibrato
    assert filters.rotation == mock_rotation
    assert filters.distortion == mock_distortion
    assert filters.channel_mix == mock_channel_mix
    assert filters.low_pass == mock_low_pass
    assert filters.plugin_filters == {"plugin": "filters"}


def test_equalizer():
    equalizer = Equalizer(band=BandType.HZ100, gain=1.2)

    assert equalizer.band == BandType.HZ100
    assert equalizer.gain == 1.2


def test_karaoke():
    karaoke = Karaoke(level=1, mono_level=2.3, filter_band=4, filter_width=5.6)

    assert karaoke.level == 1
    assert karaoke.mono_level == 2.3
    assert karaoke.filter_band == 4
    assert karaoke.filter_width == 5.6


def test_timescale():
    timescale = Timescale(speed=1, pitch=2.3, rate=4)

    assert timescale.speed == 1
    assert timescale.pitch == 2.3
    assert timescale.rate == 4


def test_tremolo():
    tremolo = Tremolo(frequency=1, depth=2.3)

    assert tremolo.frequency == 1
    assert tremolo.depth == 2.3


def test_vibrato():
    vibrato = Vibrato(frequency=1, depth=2.3)

    assert vibrato.frequency == 1
    assert vibrato.depth == 2.3


def test_rotation():
    rotation = Rotation(rotation_hz=1)

    assert rotation.rotation_hz == 1


def test_distortion():
    distortion = Distortion(
        sin_offset=1,
        sin_scale=2.3,
        cos_offset=4,
        cos_scale=5.6,
        tan_offset=7,
        tan_scale=8.9,
        offset=10,
        scale=11.12,
    )

    assert distortion.sin_offset == 1
    assert distortion.sin_scale == 2.3
    assert distortion.cos_offset == 4
    assert distortion.cos_scale == 5.6
    assert distortion.tan_offset == 7
    assert distortion.tan_scale == 8.9
    assert distortion.offset == 10
    assert distortion.scale == 11.12


def test_channel_mix():
    channel_mix = ChannelMix(
        left_to_left=1,
        left_to_right=2.3,
        right_to_left=4,
        right_to_right=5.6,
    )

    assert channel_mix.left_to_left == 1
    assert channel_mix.left_to_right == 2.3
    assert channel_mix.right_to_left == 4
    assert channel_mix.right_to_right == 5.6


def test_low_pass():
    low_pass = LowPass(smoothing=1)

    assert low_pass.smoothing == 1
