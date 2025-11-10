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
"""Errors and exceptions."""

from __future__ import annotations

import enum
import typing

if typing.TYPE_CHECKING:
    import datetime


__all__: typing.Sequence[str] = (
    "BuildError",
    "BuildTypeError",
    "BuildUnknownVariantError",
    "ClientAliveError",
    "ClientError",
    "ExceptionError",
    "NoSessionsError",
    "OngakuError",
    "PlayerConnectError",
    "PlayerConnectEventMissingError",
    "PlayerError",
    "PlayerMissingError",
    "PlayerNotConnectedError",
    "PlayerQueueEmptyError",
    "PlayerQueueError",
    "PlayerQueueLengthError",
    "RestEmptyError",
    "RestError",
    "RestRequestError",
    "RestStatusError",
    "SessionClientSessionMissingError",
    "SessionError",
    "SessionHandlerError",
    "SessionMissingBotInformationError",
    "SessionMissingError",
    "SessionStartError",
    "SeverityType",
)


class OngakuError(Exception):
    """The base ongaku error."""


# Rest:


class RestError(OngakuError):
    """The base rest error for all rest action errors."""


class RestStatusError(RestError):
    """Raised when the status is 4XX or 5XX."""

    __slots__: typing.Sequence[str] = ("_reason", "_status")

    def __init__(self, status: int, reason: str | None) -> None:
        self._status = status
        self._reason = reason

    @property
    def status(self) -> int:
        """The status of the response."""
        return self._status

    @property
    def reason(self) -> str | None:
        """The response of the error."""
        return self._reason


class RestRequestError(RestError):
    """Raised when a rest error is received from the response."""

    __slots__: typing.Sequence[str] = (
        "_error",
        "_message",
        "_path",
        "_status",
        "_timestamp",
        "_trace",
    )

    def __init__(
        self,
        timestamp: datetime.datetime,
        status: int,
        error: str,
        message: str,
        path: str,
        trace: str | None,
    ) -> None:
        self._timestamp = timestamp
        self._status = status
        self._error = error
        self._message = message
        self._path = path
        self._trace = trace

    @property
    def timestamp(self) -> datetime.datetime:
        """The timestamp of the error in milliseconds since the Unix epoch."""
        return self._timestamp

    @property
    def status(self) -> int:
        """The HTTP status code."""
        return self._status

    @property
    def error(self) -> str:
        """The HTTP status code message."""
        return self._error

    @property
    def message(self) -> str:
        """The error message."""
        return self._message

    @property
    def path(self) -> str:
        """The request path."""
        return self._path

    @property
    def trace(self) -> str | None:
        """The stack trace of the error."""
        return self._trace


class RestEmptyError(RestError):
    """Raised when the request was 204, but data was requested."""


class ExceptionError(RestError):
    """Raised when a track search results in a error result."""

    __slots__: typing.Sequence[str] = ()

    def __init__(self, message: str | None, severity: SeverityType, cause: str) -> None:
        self._message = message
        self._severity = severity
        self._cause = cause

    @property
    def message(self) -> str | None:
        """The message of the exception."""
        return self._message

    @property
    def severity(self) -> SeverityType:
        """The severity of the exception."""
        return self._severity

    @property
    def cause(self) -> str:
        """The cause of the exception."""
        return self._cause

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExceptionError):
            return False

        return (
            self.message == other.message
            and self.severity == other.severity
            and self.cause == other.cause
        )

    def __hash__(self) -> int:
        return hash((self.message, self.severity, self.cause))


# Client


class ClientError(OngakuError):
    """The base for all client errors."""


class ClientAliveError(ClientError):
    """Raised when the client is not currently alive, or has crashed."""

    __slots__: typing.Sequence[str] = ("_reason",)

    def __init__(self, reason: str, /) -> None:
        self._reason = reason

    @property
    def reason(self) -> str:
        """The reason this error occurred."""
        return self._reason


# Sessions


class SessionError(OngakuError):
    """The base session error for all session related errors."""


class SessionClientSessionMissingError(SessionError):
    """Raised when the client session has not been set."""


class SessionStartError(SessionError):
    """Raised when the session has not successfully started."""


class SessionMissingBotInformationError(SessionStartError):
    """Raised when the bot information could not be successfully retrieved."""


class SessionMissingError(SessionError):
    """Raised when the session could not be found."""


# Session Handler


class SessionHandlerError(OngakuError):
    """The base for all session handler related errors."""


class NoSessionsError(SessionHandlerError):
    """Raised when there is no available sessions for the handler to return."""


# Player


class PlayerError(OngakuError):
    """The base for all player related errors."""


class PlayerConnectEventMissingError(PlayerError):
    """Raised when the event(s) requested are not received."""


class PlayerConnectError(PlayerError):
    """Raised when the player cannot connect to lavalink, or discord."""

    __slots__: typing.Sequence[str] = ("_reason",)

    def __init__(self, reason: str, /) -> None:
        self._reason = reason

    @property
    def reason(self) -> str:
        """The reason for failure of connection."""
        return self._reason


class PlayerNotConnectedError(PlayerError):
    """Raised when the player is not connected to a voice channel."""


class PlayerQueueError(PlayerError):
    """The base for all player queue related errors."""


class PlayerQueueLengthError(PlayerError):
    """Raised when the player queue is not of a certain length."""


class PlayerQueueEmptyError(PlayerQueueError):
    """Raised when the player queue is empty."""


class PlayerMissingError(PlayerError):
    """Raised when the player could not be found."""


# Others:


class BuildError(OngakuError):
    """Raised when a object fails to build."""

    __slots__: typing.Sequence[str] = ("_reason",)

    def __init__(
        self,
        reason: str | None = None,
        /,
    ) -> None:
        self._reason = reason

    @property
    def reason(self) -> str | None:
        """The reason this error occurred."""
        return self._reason


class BuildTypeError(BuildError, TypeError):
    """Raised when an expected type was not received."""

    __slots__: typing.Sequence[str] = (
        "_expected_type",
        "_received_type",
    )

    def __init__(
        self,
        expected_type: type,
        received_type: type,
    ) -> None:
        self._expected_type = expected_type
        self._received_type = received_type
        super().__init__(f"Expected `{expected_type}` received `{received_type}`")

    @property
    def expected_type(self) -> type:
        """The expected type."""
        return self._expected_type

    @property
    def received_type(self) -> type:
        """The received type."""
        return self._received_type


class BuildUnknownVariantError(OngakuError):
    """Raised when an unknown variant for a build type was received."""

    __slots__: typing.Sequence[str] = ("_unknown_value",)

    def __init__(
        self,
        unknown_value: str,
        /,
    ) -> None:
        self._unknown_value = unknown_value

    @property
    def unknown_value(self) -> str | None:
        """The unknown value."""
        return self._unknown_value


class SeverityType(str, enum.Enum):
    """
    Track error severity type.

    The severity type of the lavalink track error.

    ![Lavalink](../assets/lavalink_logo.png){ .twemoji } [Reference](https://lavalink.dev/api/websocket#severity)
    """

    COMMON = "common"
    """Common.

    The cause is known and expected,
    indicates that there is nothing wrong with the library itself.
    """
    SUSPICIOUS = "suspicious"
    """Suspicious.

    The cause might not be exactly known,
    but is possibly caused by outside factors.

    For example when an outside service responds in a format that we do not expect.
    """
    FAULT = "fault"
    """Fault.

    The probable cause is an issue with the library,
    or there is no way to tell what the cause might be.

    This is the default level and other levels are used,
    in cases where the thrower has more in-depth knowledge about the error.
    """
