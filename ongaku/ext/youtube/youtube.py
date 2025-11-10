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
"""Youtube and entities related to Lavalink YouTube objects."""

from __future__ import annotations

import typing

__all__: typing.Sequence[str] = (
    "RefreshTokenInformation",
    "YouTube",
)


class YouTube:
    """YouTube.

    The base youtube object.
    """

    __slots__: typing.Sequence[str] = (
        "_po_token",
        "_refresh_token",
        "_skip_initialization",
        "_visitor_data",
    )

    def __init__(
        self,
        *,
        refresh_token: str | None,
        skip_initialization: bool | None,
        po_token: str | None,
        visitor_data: str | None,
    ) -> None:
        self._refresh_token = refresh_token
        self._skip_initialization = skip_initialization
        self._po_token = po_token
        self._visitor_data = visitor_data

    @property
    def refresh_token(self) -> str | None:
        """The YouTube refresh token."""
        return self._refresh_token

    @property
    def skip_initialization(self) -> bool | None:
        """Whether to skip initializing the refresh token."""
        return self._skip_initialization

    @property
    def po_token(self) -> str | None:
        """The YouTube PO token."""
        return self._po_token

    @property
    def visitor_data(self) -> str | None:
        """The YouTube visitor data."""
        return self._visitor_data


class RefreshTokenInformation:
    """FIXME: Write documentation."""

    __slots__: typing.Sequence[str] = (
        "_access_token",
        "_expires_in",
        "_scope",
        "_token_type",
    )

    def __init__(
        self,
        *,
        access_token: str,
        expires_in: int,
        scope: str,
        token_type: str,
    ) -> None:
        self._access_token = access_token
        self._expires_in = expires_in
        self._scope = scope
        self._token_type = token_type

    @property
    def access_token(self) -> str:
        """FIXME: Write documentation."""
        return self._access_token

    @property
    def expires_in(self) -> int:
        """FIXME: Write documentation."""
        return self._expires_in

    @property
    def scope(self) -> str:
        """FIXME: Write documentation."""
        return self._scope

    @property
    def token_type(self) -> str:
        """FIXME: Write documentation."""
        return self._token_type
