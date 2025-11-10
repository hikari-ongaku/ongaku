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
"""YouTube endpoints."""

from __future__ import annotations

import typing

from ongaku.errors import BuildTypeError
from ongaku.ext.youtube.youtube import RefreshTokenInformation
from ongaku.ext.youtube.youtube import YouTube
from ongaku.internal.routes import Route

if typing.TYPE_CHECKING:
    from ongaku import session


__all__ = (
    "fetch_youtube",
    "fetch_youtube_oauth",
    "update_youtube",
)


GET_YOUTUBE: typing.Final[Route] = Route("GET", "/youtube")
GET_YOUTUBE_OAUTH: typing.Final[Route] = Route("GET", "/youtube/oauth/{refresh_token}")
POST_YOUTUBE: typing.Final[Route] = Route("POST", "/youtube")


def _deserialize_youtube(payload: typing.Mapping[str, typing.Any]) -> YouTube:
    return YouTube(
        refresh_token=payload.get("refreshToken"),
        skip_initialization=payload.get("skipInitialization"),
        po_token=payload.get("poToken"),
        visitor_data=payload.get("visitorData"),
    )


def _deserialize_refresh_token_information(
    payload: typing.Mapping[str, typing.Any],
) -> RefreshTokenInformation:
    return RefreshTokenInformation(
        access_token=payload["access_token"],
        expires_in=payload["expires_in"],
        scope=payload["scope"],
        token_type=payload["token_type"],
    )


async def fetch_youtube(session: session.Session) -> YouTube | None:
    """Fetch Youtube.

    fetches the current YouTube information.

    ![Lavalink](../../assets/lavalink_logo.png){ .twemoji } [Reference](https://github.com/lavalink-devs/youtube-source?tab=readme-ov-file#get-youtube)

    Example
    -------
    ```py
    token = await client.rest.fetch_youtube()

    print(token)
    ```

    Parameters
    ----------
    session
        If provided, the session to use for this request.

    Raises
    ------
    SessionClientSessionMissingError
        Raised when the client session has not been set.
    TimeoutError
        Raised when the request takes too long to respond.
    RestEmptyError
        Raised when the response is 204, or 404.
    RestStatusError
        Raised when a 4XX or a 5XX status is received.
    RestRequestError
        Raised when a request fails, but Lavalink has more information.
    RestError
        Raised when an unknown error is caught.

    Returns
    -------
    YouTube
        The youtube object with provided information.
    None
        Returned when youtube is disabled.
    """
    route = GET_YOUTUBE.build()

    response = await session.request(route, optional=True)

    if response is None:
        return None

    if not isinstance(response, typing.Mapping):
        raise BuildTypeError(typing.Mapping, type(response))

    return _deserialize_youtube(response)


async def fetch_youtube_oauth(
    session: session.Session,
    refresh_token: str,
) -> RefreshTokenInformation:
    """Fetch YouTube Stream.

    fetches the provided youtube stream.

    ![Lavalink](../../assets/lavalink_logo.png){ .twemoji } [Reference](https://github.com/lavalink-devs/youtube-source?tab=readme-ov-file#get-youtubeoauthrefreshtoken)

    Example
    -------
    ```py
    token = await client.rest.fetch_youtube_stream()

    print(token)
    ```

    Parameters
    ----------
    session
        If provided, the session to use for this request.
    refresh_token
        The refresh token to get information about.

    Raises
    ------
    SessionClientSessionMissingError
        Raised when the client session has not been set.
    TimeoutError
        Raised when the request takes too long to respond.
    RestEmptyError
        Raised when the response is 204, or 404.
    RestStatusError
        Raised when a 4XX or a 5XX status is received.
    RestRequestError
        Raised when a request fails, but Lavalink has more information.
    RestError
        Raised when an unknown error is caught.

    Returns
    -------
    RefreshTokenInformation
        The refresh token information.
    """
    route = GET_YOUTUBE_OAUTH.build(refresh_token=refresh_token)

    response = await session.request(route)

    if not isinstance(response, typing.Mapping):
        raise BuildTypeError(typing.Mapping, type(response))

    return _deserialize_refresh_token_information(response)


async def update_youtube(
    session: session.Session,
    *,
    refresh_token: str | None = None,
    skip_initialization: bool | None = None,
    po_token: str | None = None,
    visitor_data: str | None = None,
) -> None:
    """Update Youtube.

    Update youtube endpoints.

    ![Lavalink](../../assets/lavalink_logo.png){ .twemoji } [Reference](https://github.com/lavalink-devs/youtube-source?tab=readme-ov-file#post-youtube)

    Example
    -------
    ```py
    await client.rest.update_youtube(
        refresh_token="acooltoken",
        skip_initialization=True,
        po_token="anothercooltoken",
        visitor_data="visitordata",
    )
    ```

    Parameters
    ----------
    refresh_token
        The refresh token to use.
    skip_initialization
        Whether to skip initialization of OAuth.
    po_token
        The PO Token to use.
    visitor_data
        The visitor data to use.
    session
        If provided, the session to use for this request.

    Raises
    ------
    ValueError
        Raised when no values have been modified.
    SessionClientSessionMissingError
        Raised when the client session has not been set.
    TimeoutError
        Raised when the request takes too long to respond.
    RestStatusError
        Raised when a 4XX or a 5XX status is received.
    RestRequestError
        Raised when a request fails, but Lavalink has more information.
    RestError
        Raised when an unknown error is caught.
    """
    route = POST_YOUTUBE.build()

    if (
        refresh_token is None
        and skip_initialization is None
        and po_token is None
        and visitor_data is None
    ):
        raise ValueError

    body: typing.Mapping[str, typing.Any] = {}

    if refresh_token:
        body.update({"refreshToken": refresh_token})

    if skip_initialization is not None:
        body.update({"skipInitialization": skip_initialization})

    if po_token:
        body.update({"poToken": po_token})

    if visitor_data:
        body.update({"visitorData": visitor_data})

    await session.request(route, body=body)
