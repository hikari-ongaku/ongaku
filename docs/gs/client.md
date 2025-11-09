# Client as State

The ongaku Client is the main part of running the bot. It handles anything between rest actions, to updating players, and holding cache.

Below is some examples of how to use the client within a bot setup.

=== "Arc"
    Ongaku's client will automatically be set as a dependency when using `Client.from_arc()`

    ```py
    bot = hikari.GatewayBot(...)
    arc_client = arc.GatewayClient(bot)

    client = ongaku.Client.from_arc(arc_client)

    client.create_session(...)
    ```

    Example usage:

    ```py
    @arc.slash_command("name", "description")
    async def some_command(ctx: arc.GatewayContext, client: ongaku.Client = arc.inject()) -> None:
        player = client.get_player(...)

        await player.play(...)
    ```

=== "Crescent"

    The best method for adding ongaku to crescent, is by using crescents models.

    ```py
    @dataclasses.dataclass
    class MyModel:
        ongaku: ongaku.Client

    bot = hikari.GatewayBot(...)
    client = ongaku.Client(bot)

    crescent_client = crescent.Client(bot, MyModel(client))

    client.model.ongaku.create_session(...)
    ```

    Example usage:

    ```py
    @crescent.command("name", "description")
    class SomeCommand:
        async def callback(self, ctx: crescent.Context) -> None:
            player = ctx.client.model.ongaku.get_player(...)

            await player.play(...)
    ```

=== "Lightbulb"

    The best method for adding ongaku to lightbulb, is to use the datastore.

    ```py
    bot = lightbulb.BotApp(...)

    bot.d.ongaku = ongaku.Client(bot)

    bot.d.ongaku.create_session(...)
    ```

    Example usage:

    ```py
    @lightbulb.command("name", "description", auto_defer=False)
    @lightbulb.implements(lightbulb.SlashCommand)
    async def some_command(ctx: lightbulb.SlashContext) -> None:
        player = ctx.bot.d.ongaku.get_player(...)

        await player.play(...)
    ```

=== "Tanjun"

    Ongaku's client will automatically be set as a dependency when using `Client.from_tanjun()`

    ```py
    bot = hikari.GatewayBot(...)
    tanjun_client = tanjun.Client.from_gateway_bot(bot)

    client = ongaku.Client.from_tanjun(tanjun_client)

    client.create_session(...)
    ```

    Example usage:

    ```py
    @tanjun.as_slash_command("name", "description")
    async def some_command(ctx: tanjun.abc.SlashContext, client: ongaku.Client = alluka.inject()) -> None:
        player = client.get_player(...)

        await player.play(...)
    ```

!!! note
    To actually play any tracks, you will need to make sure you have [added a session](session.md#adding-a-session) and also need to [fetch a track](player.md#getting-tracks).