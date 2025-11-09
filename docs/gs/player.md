---
title: Player
description: All player functions, and general information
---

# Player

Below, is an explanation of all the available functions for the player, and example usages.

## Creating and fetching a player

If you have followed the guide from [Client as State](./client.md) the following methods will work for fetching the player.

=== "Arc"

    ```py
    @arc.slash_command("name", "description")
    async def some_command(ctx: arc.GatewayContext, client: ongaku.Client = arc.inject()) -> None:
        try:
            player = client.create_player(...)
        except:
            await ctx.respond("The player could not be created.")
            return
            # Or possibly raise an error when it fails to fetch the player.

        # Do stuff with the player.
    ```

=== "Crescent"

    ```py
    @crescent.command("name", "description")
    class SomeCommand:
        async def callback(self, ctx: crescent.Context) -> None:
            try:
                player = client.create_player(...)
            except:
                await ctx.respond("The player could not be created.")
                return
                # Or possibly raise an error when it fails to fetch the player.

            # Do stuff with the player.
    ```

=== "Lightbulb"

    ```py
    @lightbulb.command("name", "description", auto_defer=False)
    @lightbulb.implements(lightbulb.SlashCommand)
    async def some_command(ctx: lightbulb.SlashContext) -> None:
        try:
            player = client.create_player(...)
        except:
            await ctx.respond("The player could not be created.")
            return
            # Or possibly raise an error when it fails to fetch the player.

        # Do stuff with the player.
    ```

=== "Tanjun"

    ```py
    @tanjun.as_slash_command("name", "description")
    async def some_command(ctx: tanjun.abc.SlashContext, client: ongaku.Client = alluka.inject()) -> None:
        @bot.command()
    @lightbulb.command("name", "description", auto_defer=False)
    @lightbulb.implements(lightbulb.SlashCommand)
    async def some_command(ctx: lightbulb.SlashContext) -> None:
        try:
            player = client.create_player(...)
        except:
            await ctx.create_initial_response("The player could not be created.")
            return
            # Or possibly raise an error when it fails to fetch the player.

        # Do stuff with the player.
    ```

!!! tip
    When using `client.fetch_player(...)` this only attempts to search for that current player. Using `client.create_player(...)` will search for an existing player (and return it if it exists), otherwise, will just create a new player.

## Getting tracks

Getting tracks, uses a rest method. There is a few methods of fetching a track (or tracks!)

=== "Searching"

    This method allows for the user to search on a platform for a track.

    ```py
    track = await client.rest.load_track(...)
    ```

    You need to replace the `...` with a link, or a track with a searching parameter, then followed by the query.

     - `ytsearch:` - Searches Youtube for the track.
     - `ytmsearch:` - Searches Youtube Music for the track.
     - `scsearch:` - Searches SoundCloud for the track.

    Examples:

     - `ytsearch:Imagine Dragons - Radioactive` (A Youtube search)
     - `ytmsearch:Imagine Dragons - Believer` (A Youtube music search)
     - `scsearch:Imagine Dragons - Eyes Closed` (A SoundCloud search)
     - `https://music.youtube.com/watch?v=y4FiCl-tUJc` (A link)

=== "Decoding a track"

    This method allows you to decode a track from its encoded state.

    !!! note
        The encoded state is attached to all [track][ongaku.track.Track] objects, and can be collected via `track.encoded`

    ```py

    track = await client.rest.decode_track(...)

    ```

## Player Functions

All of the functions you can do to a player.

### Connecting and disconnecting

#### Connecting

You can connect to a channel, via the following methods

```py
await player.connect(channel_id)
```

You can also mute and deafen the bot.

=== "Muting"

    This will mute the bot.

    ```py
    await player.connect(channel_id, mute=True)
    ```

    !!! tip
        By default, `mute` is set to `False`.

=== "Deafening"

    This will un-deafen the bot.

    ```py
    await player.connect(channel_id, deaf=False)
    ```

    !!! tip
        By default, `deaf` is set to `True`.

=== "Both"

    This will un-deafen and mute the bot.

    ```py
    await player.connect(channel_id, mute=True, deaf=False)
    ```

    !!! tip
        By default, `mute` is set to `False` and `deaf` is set to `True`.

!!! tip
    Replace `channel_id` with a [GuildVoiceChannel](https://docs.hikari-py.dev/en/latest/reference/hikari/channels/#hikari.channels.GuildVoiceChannel) or a integer of the channel id!

#### Disconnecting

You can disconnect and stop the player, via the following methods.

```py
await player.disconnect()
```

### Play

using the play method, has two different usages.

=== "With add"
    Using play with add, works like the following.

    ```py
    # Add track(s) to your player.
    await player.add(...)

    # Leave .play() empty, to play the current queue.
    await player.play()
    ```

=== "Without add"
    Using play without add, works like the following.

    ```py
    await player.play(...)
    ```

??? note "What is `...`"
    replace the `...` with a track. Need help getting a track? check [here](#getting-tracks)

!!! note
    `.play()` does not support multiple tracks. That is why the with .add() method exists.

!!! warning
    if you attempt to call `.play()` without any tracks, the player will error out.

### Add

Using add, allows for the user to add tracks to the queue, without playing/pausing.

Example usage of adding is the following:

```py
player.add(...)
```

??? note "What is `...`"
    replace the `...` with a track, multiple tracks or a playlist. Need help getting a track? check [here](#getting-tracks)

### Pause

Pausing, allows for you to play/pause the current track playing on the bot.
There is a few options for pausing the tracks.

=== "Force playing"

    The following method will force play the player, whether it is playing.

    ```py
    await player.pause(False)
    ```

=== "Force pausing"

    The following method will force pause the player, whether it is playing.

    ```py
    await player.pause(True)
    ```

=== "Toggling"

    The following method will change it from its current state, to the opposite state.

    ```py
    await player.pause()
    ```

### Stop

Stopping the track, tells the lavalink player to play no song.

```py
await player.stop()
```

!!! note
    This does not touch any of the tracks in the queue.

### Shuffle

Shuffle the current queue.

```py
player.shuffle()
```

!!! note
    This does not touch the track in the first position.

### Skip

Skipping songs allows for you to skip one, or multiple songs.

=== "One"

    The following code, simply skips a singular track.

    ```py

    await player.skip()

    ```

=== "Multiple"

    The following code allows for skipping one or more tracks.

    ```py
    # This will skip 3 songs in the queue, starting from the first, playing track.
    await player.skip(3)
    ```

### Remove

This allows for removing tracks. You can remove it via a track object, position or the tracks encoded value

=== "Track"

    This method allows for removing a track via its [track][ongaku.track.Track] object.

    ```py
    player.remove(track)
    ```

=== "Position"

    This method allows for removing a track via its position.

    ```py
    player.remove(3)
    ```

    !!! note
        Please remember, pythons lists start at 0. So this example will actually remove the track in the 4th position of the queue.

!!! warning
    If the track you remove is in the first position, it will **not** be stopped. It will continue playing.

### Clear

This is very similar to the [Remove](#remove).
It removes all tracks from the queue, and stops the player.

```py
await player.clear()
```

### Autoplay

This allows you to toggle autoplay on or off.

Autoplay allows for playing the next track in the queue when the previous one ends.

=== "Force enable"

    The following method will set autoplay to on.

    ```py
    player.set_autoplay(True)
    ```

=== "Force pausing"

    The following method will set autoplay to off.

    ```py
    player.set_autoplay(False)
    ```

=== "Toggling"

    The following method will set autoplay to its opposite value.

    ```py
    player.set_autoplay()
    ```

### Loop

Pausing, allows for you to play/pause the current track playing on the bot.
There is a few options for pausing the tracks.

=== "Force looping"

    The following method will force loop the player, whether it is looping.

    ```py
    player.set_loop(False)
    ```

=== "Force disable looping"

    The following method will force loop the player, whether it is looping.

    ```py
    player.set_loop(True)
    ```

=== "Toggling"

    The following method will change it from its current state, to the opposite state.

    ```py
    player.set_loop()
    ```

### Volume

This allows you to change the volume of the player.

=== "Change"

    This allows you to change the volume of the player.

    ```py
    # The following sets the volume to half of its original.
    await player.set_volume(50)
    ```

=== "Reset"

    This will simply reset the player to its default value.

    ```py
    await player.set_volume()
    ```

    ??? note "Default value"
        The default value is 100.

!!! note
    Any value above 100 will result in audio distortion, and artifacts.

### Position

This function allows for you to set the position of the track. This is in milliseconds.

```py
await player.set_position(40000)
```

### Filters

This allows you to set or clear the current filter.

=== "Change/Set"

    This allows you to change the current filter, or set a new one.

    ```py
    await player.set_filters(filters)
    ```

=== "Clear"

    This allows you to completely clear the current filter.

    ```py
    await player.set_filters()
    ```

    !!! tip
        Learn more about filters [here](./filters.md)

This function, will put the track at 40 seconds.

!!! warning
    If the position is outside of the track or there is no track playing, then it will result in an error.
