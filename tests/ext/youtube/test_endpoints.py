from __future__ import annotations

import typing
from unittest import mock

import pytest

from ongaku import errors
from ongaku.ext.youtube import endpoints


def test__deserialize_youtube():
    payload: typing.Final[dict[str, typing.Any]] = {
        "refreshToken": "refresh_token",
        "skipInitialization": False,
        "poToken": "po_token",
        "visitorData": "visitor_data",
    }

    youtube = endpoints._deserialize_youtube(payload)

    assert youtube.refresh_token == "refresh_token"
    assert youtube.skip_initialization is False
    assert youtube.po_token == "po_token"
    assert youtube.visitor_data == "visitor_data"


def test__deserialize_youtube_with_null():
    payload: typing.Final[dict[str, typing.Any]] = {
        "refreshToken": "refresh_token",
    }

    youtube = endpoints._deserialize_youtube(payload)

    assert youtube.refresh_token == "refresh_token"
    assert youtube.skip_initialization is None
    assert youtube.po_token is None
    assert youtube.visitor_data is None


def test_deserialize_refresh_token_information():
    payload: typing.Final[dict[str, typing.Any]] = {
        "access_token": "access_token",
        "expires_in": 5400,
        "scope": "scope",
        "token_type": "token_type",
    }

    refresh_token = endpoints._deserialize_refresh_token_information(payload)

    assert refresh_token.access_token == "access_token"
    assert refresh_token.expires_in == 5400
    assert refresh_token.scope == "scope"
    assert refresh_token.token_type == "token_type"


@pytest.mark.asyncio
async def test_fetch_youtube():
    session_request = mock.AsyncMock(return_value={})
    session = mock.Mock(request=session_request)

    with (
        mock.patch.object(
            endpoints,
            "_deserialize_youtube",
        ) as patched_deserialize_youtube,
    ):
        await endpoints.fetch_youtube(session)

    session.request.assert_awaited_once_with(
        endpoints.GET_YOUTUBE.build(),
        optional=True,
    )
    patched_deserialize_youtube.assert_called_once_with(session_request.return_value)


@pytest.mark.asyncio
async def test_fetch_youtube_with_null():
    session_request = mock.AsyncMock(return_value=None)
    session = mock.Mock(request=session_request)

    with (
        mock.patch.object(
            endpoints,
            "_deserialize_youtube",
        ) as patched_deserialize_youtube,
    ):
        await endpoints.fetch_youtube(session)

    session.request.assert_awaited_once_with(
        endpoints.GET_YOUTUBE.build(),
        optional=True,
    )
    patched_deserialize_youtube.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_youtube_with_invalid_response():
    session_request = mock.AsyncMock(return_value=[])
    session = mock.Mock(request=session_request)

    with (
        mock.patch.object(
            endpoints,
            "_deserialize_youtube",
        ) as patched_deserialize_youtube,
        pytest.raises(errors.BuildTypeError, match=rf"({typing.Mapping}, {list})"),
    ):
        await endpoints.fetch_youtube(session)

    session.request.assert_awaited_once_with(
        endpoints.GET_YOUTUBE.build(),
        optional=True,
    )
    patched_deserialize_youtube.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_youtube_oauth():
    session_request = mock.AsyncMock(return_value={})
    session = mock.Mock(request=session_request)

    with (
        mock.patch.object(
            endpoints,
            "_deserialize_refresh_token_information",
        ) as patched__deserialize_refresh_token_information,
    ):
        await endpoints.fetch_youtube_oauth(session, "refresh_token")

    session.request.assert_awaited_once_with(
        endpoints.GET_YOUTUBE_OAUTH.build(refresh_token="refresh_token"),
    )
    patched__deserialize_refresh_token_information.assert_called_once_with(
        session_request.return_value,
    )


@pytest.mark.asyncio
async def test_fetch_youtube_oauth_with_invalid_response():
    session_request = mock.AsyncMock(return_value=[])
    session = mock.Mock(request=session_request)

    with (
        mock.patch.object(
            endpoints,
            "_deserialize_refresh_token_information",
        ) as patched__deserialize_refresh_token_information,
        pytest.raises(errors.BuildTypeError, match=rf"({typing.Mapping}, {list})"),
    ):
        await endpoints.fetch_youtube_oauth(session, "refresh_token")

    session.request.assert_awaited_once_with(
        endpoints.GET_YOUTUBE_OAUTH.build(refresh_token="refresh_token"),
    )
    patched__deserialize_refresh_token_information.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("refresh_token", "skip_initialization", "po_token", "visitor_data"),
    [
        (
            "refresh_token",
            None,
            None,
            None,
        ),
        (
            None,
            True,
            None,
            None,
        ),
        (
            None,
            False,
            None,
            None,
        ),
        (
            None,
            None,
            "po_token",
            None,
        ),
        (
            None,
            None,
            None,
            "visitor_data",
        ),
        (
            "refresh_token",
            True,
            "po_token",
            "visitor_data",
        ),
    ],
)
async def test_update_youtube(
    refresh_token: str | None,
    skip_initialization: bool | None,
    po_token: str | None,
    visitor_data: str | None,
):
    session_request = mock.AsyncMock(return_value={})
    session = mock.Mock(request=session_request)

    await endpoints.update_youtube(
        session,
        refresh_token=refresh_token,
        skip_initialization=skip_initialization,
        po_token=po_token,
        visitor_data=visitor_data,
    )

    body: dict[str, typing.Any] = {}

    if refresh_token is not None:
        body["refreshToken"] = refresh_token

    if skip_initialization is not None:
        body["skipInitialization"] = skip_initialization

    if po_token is not None:
        body["poToken"] = po_token

    if visitor_data is not None:
        body["visitorData"] = visitor_data

    session.request.assert_awaited_once_with(
        endpoints.POST_YOUTUBE.build(),
        body=body,
    )


@pytest.mark.asyncio
async def test_update_youtube_with_null():
    session_request = mock.AsyncMock(return_value={})
    session = mock.Mock(request=session_request)

    with pytest.raises(
        ValueError,
        match=r"^$",
    ):
        await endpoints.update_youtube(session)

    session.request.assert_not_called()
