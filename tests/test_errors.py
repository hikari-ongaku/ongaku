from __future__ import annotations

import datetime

from ongaku import errors


def test_rest_status_error():
    error = errors.RestStatusError(status=200, reason="reason")

    assert error.status == 200
    assert error.reason == "reason"


def test_rest_request_error():
    timestamp = datetime.datetime.now(datetime.timezone.utc)

    error = errors.RestRequestError(
        timestamp=timestamp,
        status=200,
        error="error",
        message="message",
        path="path",
        trace="trace",
    )

    assert error.timestamp == timestamp
    assert error.status == 200
    assert error.error == "error"
    assert error.message == "message"
    assert error.path == "path"
    assert error.trace == "trace"


def test_exception_error():
    error = errors.ExceptionError(
        "message",
        severity=errors.SeverityType.COMMON,
        cause="cause",
    )

    assert error.message == "message"
    assert error.severity is errors.SeverityType.COMMON
    assert error.cause == "cause"


def test_client_alive_error():
    error = errors.ClientAliveError("reason")

    assert error.reason == "reason"


def test_player_connect_error():
    error = errors.PlayerConnectError("reason")

    assert error.reason == "reason"


def test_build_error():
    error = errors.BuildError("reason")

    assert error.reason == "reason"
