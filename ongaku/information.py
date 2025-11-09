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
"""Information and entities related to Lavalink information objects."""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import datetime

__all__ = ("Git", "Information", "Plugin", "Version")


class Information:
    """Information.

    All of the Information about the lavalink session.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest.html#info-response)
    """

    __slots__: typing.Sequence[str] = (
        "_build_time",
        "_filters",
        "_git",
        "_jvm",
        "_lavaplayer",
        "_plugins",
        "_source_managers",
        "_version",
    )

    def __init__(
        self,
        *,
        version: Version,
        build_time: datetime.datetime,
        git: Git,
        jvm: str,
        lavaplayer: str,
        source_managers: typing.Sequence[str],
        filters: typing.Sequence[str],
        plugins: typing.Sequence[Plugin],
    ) -> None:
        self._version = version
        self._build_time = build_time
        self._git = git
        self._jvm = jvm
        self._lavaplayer = lavaplayer
        self._source_managers = source_managers
        self._filters = filters
        self._plugins = plugins

    @property
    def version(self) -> Version:
        """The version of this Lavalink server."""
        return self._version

    @property
    def build_time(self) -> datetime.datetime:
        """The datetime object of when this Lavalink jar was built."""
        return self._build_time

    @property
    def git(self) -> Git:
        """The git information of this Lavalink server."""
        return self._git

    @property
    def jvm(self) -> str:
        """The JVM version this Lavalink server runs on."""
        return self._jvm

    @property
    def lavaplayer(self) -> str:
        """The Lavaplayer version being used by this server."""
        return self._lavaplayer

    @property
    def source_managers(self) -> typing.Sequence[str]:
        """The enabled source managers for this server."""
        return self._source_managers

    @property
    def filters(self) -> typing.Sequence[str]:
        """The enabled filters for this server."""
        return self._filters

    @property
    def plugins(self) -> typing.Sequence[Plugin]:
        """The enabled plugins for this server."""
        return self._plugins

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Information):
            return False

        return (
            self.version == other.version
            and self.build_time == other.build_time
            and self.git == other.git
            and self.jvm == other.jvm
            and self.lavaplayer == other.lavaplayer
            and self.source_managers == other.source_managers
            and self.filters == other.filters
            and self.plugins == other.plugins
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.version,
                self.build_time,
                self.git,
                self.jvm,
                self.lavaplayer,
                self.source_managers,
                self.filters,
                self.plugins,
            ),
        )


class Version:
    """Version.

    All information, about the version of lavalink that is running.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest.html#version-object)
    """

    __slots__: typing.Sequence[str] = (
        "_build",
        "_major",
        "_minor",
        "_patch",
        "_pre_release",
        "_semver",
    )

    def __init__(
        self,
        *,
        semver: str,
        major: int,
        minor: int,
        patch: int,
        pre_release: str,
        build: str | None,
    ) -> None:
        self._semver = semver
        self._major = major
        self._minor = minor
        self._patch = patch
        self._pre_release = pre_release
        self._build = build

    @property
    def semver(self) -> str:
        """The full version string of this Lavalink server."""
        return self._semver

    @property
    def major(self) -> int:
        """The major version of this Lavalink server."""
        return self._major

    @property
    def minor(self) -> int:
        """The minor version of this Lavalink server."""
        return self._minor

    @property
    def patch(self) -> int:
        """The patch version of this Lavalink server."""
        return self._patch

    @property
    def pre_release(self) -> str:
        """Pre Release.

        The pre-release version according to semver,
        as a `.` separated list of identifiers.
        """
        return self._pre_release

    @property
    def build(self) -> str | None:
        """Build.

        The build metadata according to semver,
        as a `.` separated list of identifiers.
        """
        return self._build

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return False

        return (
            self.semver == other.semver
            and self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.pre_release == other.pre_release
            and self.build == other.build
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.semver,
                self.major,
                self.minor,
                self.patch,
                self.pre_release,
                self.build,
            ),
        )


class Git:
    """Git.

    All of the information about the lavalink git information.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest.html#git-object)
    """

    __slots__: typing.Sequence[str] = (
        "_branch",
        "_commit",
        "_commit_time",
    )

    def __init__(
        self,
        *,
        branch: str,
        commit: str,
        commit_time: datetime.datetime,
    ) -> None:
        self._branch = branch
        self._commit = commit
        self._commit_time = commit_time

    @property
    def branch(self) -> str:
        """The branch this Lavalink server was built on."""
        return self._branch

    @property
    def commit(self) -> str:
        """The commit this Lavalink server was built on."""
        return self._commit

    @property
    def commit_time(self) -> datetime.datetime:
        """The datetime object of when the commit was created."""
        return self._commit_time

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Git):
            return False

        return (
            self.branch == other.branch
            and self.commit == other.commit
            and self.commit_time == other.commit_time
        )

    def __hash__(self) -> int:
        return hash((self.branch, self.commit, self.commit_time))


class Plugin:
    """Plugin.

    All of the Information about the currently loaded plugins.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/rest.html#plugin-object)
    """

    __slots__: typing.Sequence[str] = ("_name", "_version")

    def __init__(self, *, name: str, version: str) -> None:
        self._name = name
        self._version = version

    @property
    def name(self) -> str:
        """The name of the plugin."""
        return self._name

    @property
    def version(self) -> str:
        """The version of the plugin."""
        return self._version

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Plugin):
            return False

        return self.name == other.name and self.version == other.version

    def __hash__(self) -> int:
        return hash((self.name, self.version))
