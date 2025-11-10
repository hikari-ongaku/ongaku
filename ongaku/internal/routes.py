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
"""Route and endpoint builders."""

from __future__ import annotations

import typing

__all__ = (
    "DELETE_PLAYER",
    "GET_DECODE_TRACK",
    "GET_INFO",
    "GET_LOAD_TRACKS",
    "GET_PLAYER",
    "GET_PLAYERS",
    "GET_ROUTEPLANNER_STATUS",
    "GET_STATISTICS",
    "GET_VERSION",
    "PATCH_PLAYER_UPDATE",
    "PATCH_SESSION_UPDATE",
    "POST_DECODE_TRACKS",
    "POST_ROUTEPLANNER_FREE_ADDRESS",
    "POST_ROUTEPLANNER_FREE_ALL",
    "BuiltRoute",
    "Route",
)

GET: typing.Final[str] = "GET"
POST: typing.Final[str] = "POST"
PATCH: typing.Final[str] = "PATCH"
DELETE: typing.Final[str] = "DELETE"


class Route:
    """Route.

    The route object that has mostly been built.
    """

    __slots__ = ("_include_version", "_method", "_path")

    def __init__(self, method: str, path: str, *, include_version: bool = True) -> None:
        self._method = method
        self._path = path
        self._include_version = include_version

    @property
    def method(self) -> str:
        """The route method."""
        return self._method

    @property
    def path(self) -> str:
        """The path."""
        return self._path

    @property
    def include_version(self) -> bool:
        """Whether to include the version."""
        return self._include_version

    def build(self, **kwargs: str | bool | float) -> BuiltRoute:
        """Build the route."""
        version = "/v4" if self.include_version else ""
        built_path = self.path.format_map(kwargs)

        return BuiltRoute(
            route=self,
            path=f"{version}{built_path}",
        )

    def __str__(self) -> str:
        return f"{self.method} {self.path}"

    def __repr__(self) -> str:
        return f"Route(method={self.method}, path={self.path}, include_version={self.include_version})"  # noqa: E501

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Route):
            return False

        return (
            self.method == other.method
            and self.path == other.path
            and self.include_version == other.include_version
        )

    def __hash__(self) -> int:
        return hash((self.method, self.path, self.include_version))


class BuiltRoute:
    """Built Route.

    The built route, with completed path.
    """

    __slots__ = ("_path", "_route")

    def __init__(self, *, route: Route, path: str) -> None:
        self._route = route
        self._path = path

    @property
    def route(self) -> Route:
        """The route that was compiled from."""
        return self._route

    @property
    def method(self) -> str:
        """The route method."""
        return self._route.method

    @property
    def path(self) -> str:
        """The built path, including the version."""
        return self._path

    def __str__(self) -> str:
        return f"{self.method} {self.path} ({self.route.path})"

    def __repr__(self) -> str:
        return f"BuiltRoute(method={self.method}, path={self.path}, raw_path={self.route.path}"  # noqa: E501

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BuiltRoute):
            return False

        return (
            self.route == other.route
            and self.method == other.method
            and self.path == other.path
        )

    def __hash__(self) -> int:
        return hash((self.route, self.method, self.path))


# Info

GET_INFO: typing.Final[Route] = Route(GET, "/info")

GET_VERSION: typing.Final[Route] = Route(GET, "/version", include_version=False)

GET_STATISTICS: typing.Final[Route] = Route(GET, "/stats")

# Session

PATCH_SESSION_UPDATE: typing.Final[Route] = Route(PATCH, "/sessions/{session_id}")

# Player

GET_PLAYERS: typing.Final[Route] = Route(GET, "/sessions/{session_id}/players")

GET_PLAYER: typing.Final[Route] = Route(
    GET,
    "/sessions/{session_id}/players/{guild_id}",
)

PATCH_PLAYER_UPDATE: typing.Final[Route] = Route(
    PATCH,
    "/sessions/{session_id}/players/{guild_id}",
)

DELETE_PLAYER: typing.Final[Route] = Route(
    DELETE,
    "/sessions/{session_id}/players/{guild_id}",
)

# Tracks

GET_LOAD_TRACKS: typing.Final[Route] = Route(GET, "/loadtracks")

GET_DECODE_TRACK: typing.Final[Route] = Route(GET, "/decodetrack")

POST_DECODE_TRACKS: typing.Final[Route] = Route(POST, "/decodetracks")

# Route Planner

GET_ROUTEPLANNER_STATUS: typing.Final[Route] = Route(GET, "/routeplanner/status")

POST_ROUTEPLANNER_FREE_ADDRESS: typing.Final[Route] = Route(
    POST,
    "/routeplanner/free/address",
)

POST_ROUTEPLANNER_FREE_ALL: typing.Final[Route] = Route(POST, "/routeplanner/free/all")
