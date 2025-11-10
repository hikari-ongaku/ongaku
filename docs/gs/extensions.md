---
title: Extensions
description: Using and making an extension.
---

# Extensions

All of the information of how to use, and make a custom extension.

!!! tip
    Most examples will use a custom extension (which can be found below)

!!! note
    You can also see some examples [here](https://github.com/hikari-ongaku/ongaku/tree/main/examples) in the `extension.py` file.

## Adding Extensions

When using **most** extensions, you have to add your extension to the Ongaku client.

=== "Creating it yourself"
    This is how you can create your client yourself,
    in case you plan to add extra arguments, or for other reasons.
    
    ```py linenums="1"
    client = ... # Create your client here.

    extension = CustomExtension(client)

    extension.set_name("banana")

    client.create_extension(extension)
    ```

    The first line you need, is the creation of the extension.
    ```py linenums="3"
    extension = CustomExtension(client)
    ```

    The next line will of course be different for each extension, but can be used like the following:
    ```py linenums="5"
    extension.name = "banana"  # This sets a `name` value to `banana`
    ```

    And the final, important line that is needed, adds the extension to the client.
    ```py linenums="7"
    client.create_extension(extension)
    ```

=== "Passing the type"
    If you don't need to set any values or arguments,
    you can simply just pass the typ to the handler.

    ```py linenums="1"
    client = ... # Create your client here.

    client.create_extension(CustomExtension)
    ```

    This, simply just adds the extension, and starts it up all behind the scenes.
    ```py linenums="3"
    client.create_extension(CustomExtension)
    ```


## Using Extensions

Extensions are reasonably easy to use, however different clients handle this different ways.

The first, and foremost easiest method for all cases, is using the get functions within the client.

```py
client = ...

extension = client.get_extension(CustomExtension)
```

The extension variable returned, will be the instance used within the extension.

However, some command handlers support extra functionality, called Dependency Injection. You can find out more [here](./injection.md).

=== "Arc"
    ```py
    @arc.slash_command("name", "description")
    async def some_command(ctx: arc.GatewayContext, extension: CustomExtension = arc.inject()) -> None:
        pass
    ```

=== "Tanjun"
    ```py
    @tanjun.as_slash_command("name", "description")
    async def some_command(ctx: tanjun.abc.SlashContext, extension: CustomExtension = alluka.inject()) -> None:
        pass
    ```

## Removing Extensions

Extensions can also be removed if needed. 

```py
client = ...

client.delete_extension(CustomExtension)
```

## Creating Custom Extensions

Finally, extensions can be created, by simply sub-classing the `Extension` class.

```py
import typing

import hikari

import ongaku
from ongaku.abc.events import OngakuEvent
from ongaku.abc.extensions import Extension


class CustomExtension(Extension):
    def event_handler(self, payload: typing.Mapping[str, typing.Any], session: ongaku.Session) -> OngakuEvent | None:
        if payload.get("op") != "event" and payload.get("type") != "custom_event":  # Check that the OP and code is correct.
            return None

        # Return a custom event.
        return CustomEvent(self.client.app, self.client, session, name=payload["name"])

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
```

This simply creates a custom extension (called `CustomExtension`). This extension doesn't really do anything, as its simply just an example of how to create a custom extension.
