from __future__ import annotations

from unittest import mock

from ongaku.information import Git
from ongaku.information import Information
from ongaku.information import Plugin
from ongaku.information import Version


def test_information():
    mock_version = mock.Mock()
    mock_build_time = mock.Mock()
    mock_git = mock.Mock()
    mock_plugin_1 = mock.Mock()
    mock_plugin_2 = mock.Mock()

    info = Information(
        version=mock_version,
        build_time=mock_build_time,
        git=mock_git,
        jvm="jvm",
        lavaplayer="lavaplayer",
        source_managers=["source_manager_1", "source_manager_2"],
        filters=["filter_1", "filter_2"],
        plugins=[mock_plugin_1, mock_plugin_2],
    )

    assert info.version == mock_version
    assert info.build_time == mock_build_time
    assert info.git == mock_git
    assert info.jvm == "jvm"
    assert info.lavaplayer == "lavaplayer"
    assert info.source_managers == ["source_manager_1", "source_manager_2"]
    assert info.filters == ["filter_1", "filter_2"]
    assert info.plugins == [mock_plugin_1, mock_plugin_2]


def test_info_version():
    info_version = Version(
        semver="semver",
        major=1,
        minor=2,
        patch=3,
        pre_release="pre_release",
        build="build",
    )

    assert info_version.semver == "semver"
    assert info_version.major == 1
    assert info_version.minor == 2
    assert info_version.patch == 3
    assert info_version.pre_release == "pre_release"
    assert info_version.build == "build"


def test_info_git():
    mock_commit_time = mock.Mock()

    info_git = Git(
        branch="branch",
        commit="commit",
        commit_time=mock_commit_time,
    )

    assert info_git.branch == "branch"
    assert info_git.commit == "commit"
    assert info_git.commit_time == mock_commit_time


def test_info_plugin():
    info_plugin = Plugin(name="name", version="version")

    assert info_plugin.name == "name"
    assert info_plugin.version == "version"
