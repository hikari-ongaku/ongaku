from __future__ import annotations

import typing

import arc
import hikari

import ongaku
from ongaku.abc.events import OngakuEvent
from ongaku.abc.extensions import Extension


class CustomExtension(Extension):
    def event_handler(
        self,
        payload: typing.Mapping[str, typing.Any],
        session: ongaku.Session,
    ) -> OngakuEvent | None:
        if payload.get("op") != "event" and payload.get("type") != "custom_event":
            return None

        return CustomEvent(self.client.app, self.client, session, payload["name"])

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value


class CustomEvent(OngakuEvent):
    def __init__(
        self,
        app: hikari.RESTAware,
        client: ongaku.Client,
        session: ongaku.Session,
        name: str,
    ) -> None:
        self._app = app
        self._client = client
        self._session = session
        self._name = name

    @property
    def app(self) -> hikari.RESTAware:
        return self._app

    @property
    def client(self) -> ongaku.Client:
        return self._client

    @property
    def session(self) -> ongaku.Session:
        return self._session

    @property
    def name(self) -> str:
        return self._name


bot = hikari.GatewayBot("...")

client = arc.GatewayClient(bot)

ongaku_client = ongaku.Client.from_arc(client)

ongaku_client.create_session(
    "arc-session",
    host="127.0.0.1",
    password="youshallnotpass",
)

ongaku_client.create_extension(CustomExtension)


@bot.listen()
@client.inject_dependencies
async def custom_event(
    event: CustomEvent,
    extension: CustomExtension = arc.inject(),
) -> None:
    extension.name = event.name
    print("Received our custom event!")


if __name__ == "__main__":
    bot.run()
