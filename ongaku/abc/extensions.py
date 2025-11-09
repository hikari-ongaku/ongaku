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
"""Abstract extension objects."""

from __future__ import annotations

import abc
import typing

if typing.TYPE_CHECKING:
    from ongaku import session
    from ongaku.abc import events
    from ongaku.client import Client

__all__: typing.Sequence[str] = ("Extension",)


class Extension(abc.ABC):
    """Extension.

    This is the base class an external plugin needs to send custom events,
    and use rest methods.

    Parameters
    ----------
    client
        The ongaku client attached to this extension.
    """

    __slots__: typing.Sequence[str] = ("_client",)

    def __init__(self, client: Client) -> None:
        self._client = client

    @property
    def client(self) -> Client:
        """The client this extension is included in."""
        return self._client

    @abc.abstractmethod
    def event_handler(
        self,
        payload: typing.Mapping[str, typing.Any],
        session: session.Session,
    ) -> events.OngakuEvent | None:
        """Event handler.

        This allows for you to hook into the event handler,
        and dispatch your own event(s) for extensions.

        !!! warning
            Do not dispatch your own events here. You will break how ongaku works.

        Parameters
        ----------
        payload
            The payload of the event.
        session
            The session connected to this payload.

        Returns
        -------
        events.OngakuEvent
            The ongaku event to be dispatched.
        None
            No event was found for dispatching.
        """
