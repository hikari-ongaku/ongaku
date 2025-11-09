# ╔═══════════╗
# ║ Lightbulb ║
# ╚═══════════╝
from __future__ import annotations

import logging

import hikari
import lightbulb

import ongaku
from ongaku.ext import checker

bot = lightbulb.BotApp(token="...", banner=None)

ongaku_client = ongaku.Client(bot)

ongaku_client.create_session(
    "lightbulb-session",
    host="127.0.0.1",
    password="youshallnotpass",
)

# ╔════════╗
# ║ Events ║
# ╚════════╝


@bot.listen(ongaku.ReadyEvent)
async def ready_event(event: ongaku.ReadyEvent) -> None:
    logging.info(
        "Ready Event, Resumed: %s, session id: %s",
        event.resumed,
        event.session_id,
    )


@bot.listen(ongaku.TrackStartEvent)
async def track_start_event(event: ongaku.TrackStartEvent) -> None:
    logging.info(
        "Track Started Event, guild: %s, Track Title: %s",
        event.guild_id,
        event.track.info.title,
    )


@bot.listen(ongaku.TrackEndEvent)
async def track_end_event(event: ongaku.TrackEndEvent) -> None:
    logging.info(
        "Track Ended Event, guild: %s, Track Title: %s, Reason: %s",
        event.guild_id,
        event.track.info.title,
        event.reason.name,
    )


@bot.listen(ongaku.TrackExceptionEvent)
async def track_exception_event(event: ongaku.TrackExceptionEvent) -> None:
    logging.info(
        "Track Exception Event, guild: %s, Track Title: %s, Exception message: %s",
        event.guild_id,
        event.track.info.title,
        event.exception.message,
    )


@bot.listen(ongaku.TrackStuckEvent)
async def track_stuck_event(event: ongaku.TrackStuckEvent) -> None:
    logging.info(
        "Track Stuck Event, guild: %s, Track Title: %s, Threshold ms: %s",
        event.guild_id,
        event.track.info.title,
        event.threshold_ms,
    )


@bot.listen(ongaku.WebsocketClosedEvent)
async def websocket_close_event(event: ongaku.WebsocketClosedEvent) -> None:
    logging.info(
        "Websocket Close Event, guild: %s, Reason: %s, Code: %s, By Remote: %s",
        event.guild_id,
        event.reason,
        event.code,
        event.by_remote,
    )


@bot.listen(ongaku.QueueNextEvent)
async def queue_next_event(event: ongaku.QueueNextEvent) -> None:
    logging.info(
        "guild: %s's track: %s has finished! Now playing: %s",
        event.guild_id,
        event.old_track.info.title,
        event.track.info.title,
    )


@bot.listen(ongaku.QueueEmptyEvent)
async def queue_empty_event(event: ongaku.QueueEmptyEvent) -> None:
    logging.info("Queue is empty in guild: %s", event.guild_id)


@bot.listen(ongaku.SessionConnectedEvent)
async def session_connected_event(event: ongaku.SessionConnectedEvent) -> None:
    logging.info(
        "Session %s has successfully connected to the lavalink server.",
        event.session.name,
    )


@bot.listen(ongaku.SessionDisconnectedEvent)
async def session_disconnected_event(event: ongaku.SessionDisconnectedEvent) -> None:
    logging.info(
        "Session %s has disconnected, code: %s, reason: %s",
        event.session.name,
        event.code,
        event.reason,
    )


@bot.listen(ongaku.SessionErrorEvent)
async def session_error_event(event: ongaku.SessionErrorEvent) -> None:
    logging.info("Session %s has had an error occur.", event.session.name)


# ╔═══════════════╗
# ║ Error Handler ║
# ╚═══════════════╝


@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.OnlyInGuild):
        await event.context.respond(
            "You need to be in a guild to run this command.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )

    elif isinstance(exception, ongaku.PlayerMissingError):
        await event.context.respond(
            "No player was found for this guild.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )

    else:
        await event.context.respond(
            f"An uncaught error was received: {exception}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


# ╔══════════╗
# ║ Commands ║
# ╚══════════╝


@bot.command
@lightbulb.option("query", "The name, or link of the song to play.", str, required=True)
@lightbulb.command("play", "Play a song or playlist.")
@lightbulb.implements(lightbulb.SlashCommand)
async def play_command(
    ctx: lightbulb.Context,
) -> None:
    music: ongaku.Client = ctx.bot.d.ongaku_client

    if ctx.guild_id is None:
        raise lightbulb.OnlyInGuild

    voice_state = bot.cache.get_voice_state(ctx.guild_id, ctx.author.id)
    if not voice_state or not voice_state.channel_id:
        await ctx.respond(
            "you are not in a voice channel.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    query = ctx.options.query

    if not isinstance(query, str):
        await ctx.respond(
            "The query received was invalid.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    if checker.check(query):
        result = await music.rest.load_track(query)
    else:
        result = await music.rest.load_track(f"ytsearch:{query}")

    if result is None:
        await ctx.respond(
            "Sorry, no songs were found.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    if isinstance(result, ongaku.Playlist):
        track = result.tracks[0]

    elif isinstance(result, ongaku.Track):
        track = result

    else:
        track = result[0]

    embed = hikari.Embed(
        title=f"[{track.info.title}]({track.info.uri})",
        description=f"made by: {track.info.author}",
    )

    player = music.create_player(ctx.guild_id)

    if player.is_connected is False:
        await player.connect(voice_state.channel_id)

    await player.play(track)

    await ctx.respond(
        embed=embed,
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@bot.command
@lightbulb.option("query", "The name, or link of the song to add.", str, required=True)
@lightbulb.command("add", "Add more songs or a playlist.")
@lightbulb.implements(lightbulb.SlashCommand)
async def add_command(
    ctx: lightbulb.Context,
) -> None:
    music: ongaku.Client = ctx.bot.d.ongaku_client

    if ctx.guild_id is None:
        raise lightbulb.OnlyInGuild

    player = music.get_player(ctx.guild_id)

    query = ctx.options.query

    if not isinstance(query, str):
        await ctx.respond(
            "The query received was invalid.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    if checker.check(query):
        result = await music.rest.load_track(query)
    else:
        result = await music.rest.load_track(f"ytsearch:{query}")

    if result is None:
        await ctx.respond(
            "Sorry, no songs were found.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    if isinstance(result, ongaku.Playlist):
        tracks = result.tracks

    elif isinstance(result, ongaku.Track):
        tracks = [result]

    else:
        tracks = [result[0]]

    player.add(tracks)

    embed = hikari.Embed(
        title="Tracks added",
        description=f"All the tracks that have been added. (only shows top 25.)\nTotal tracks added: {len(tracks)}",
    )

    for track in tracks:
        if len(embed.fields) >= 25:
            break
        embed.add_field(track.info.title, track.info.author)

    await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)


@bot.command
@lightbulb.command("queue", "View the current queue.")
@lightbulb.implements(lightbulb.SlashCommand)
async def queue_command(ctx: lightbulb.Context) -> None:
    music: ongaku.Client = ctx.bot.d.ongaku_client

    if ctx.guild_id is None:
        raise lightbulb.OnlyInGuild

    player = music.get_player(ctx.guild_id)

    if len(player.queue) == 0:
        await ctx.respond(
            "There is no songs in the queue.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    embed = hikari.Embed(
        title="Queue",
        description=f"There is currently {len(player.queue)} song{'s' if len(player.queue) > 1 else ''} in the queue.",
    )

    embed.add_field(
        f"▶️ {player.queue[0].info.title}",
        f"Length: {player.queue[0].info.length / 1000}s\nArtist: {player.queue[0].info.author}",
    )

    if len(player.queue) > 1:
        for i in range(1, 24):
            if i > len(player.queue):
                break

            embed.add_field(
                player.queue[i].info.title,
                f"Length: {player.queue[i].info.length / 1000}s\nArtist: {player.queue[i].info.author}",
            )

    await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)


@bot.command
@lightbulb.command("pause", "Pause or play the current song.")
@lightbulb.implements(lightbulb.SlashCommand)
async def pause_command(
    ctx: lightbulb.Context,
) -> None:
    music: ongaku.Client = ctx.bot.d.ongaku_client

    if ctx.guild_id is None:
        raise lightbulb.OnlyInGuild

    player = music.get_player(ctx.guild_id)

    await player.pause()

    if player.is_paused:
        await ctx.respond(
            "The song has been paused.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
    else:
        await ctx.respond(
            "The song has been unpaused.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@bot.command
@lightbulb.command("skip", "Skip the currently playing song.")
@lightbulb.implements(lightbulb.SlashCommand)
async def skip_command(
    ctx: lightbulb.Context,
) -> None:
    music: ongaku.Client = ctx.bot.d.ongaku_client

    if ctx.guild_id is None:
        raise lightbulb.OnlyInGuild

    player = music.get_player(ctx.guild_id)

    await player.skip()

    if len(player.queue) > 0:
        embed = hikari.Embed(
            title=player.queue[0].info.title,
            description=f"Length: {player.queue[0].info.length / 1000}s\nArtist: {player.queue[0].info.author}",
        )

        artwork_url = player.queue[0].info.artwork_url

        if artwork_url:
            embed.set_thumbnail(hikari.files.URL(artwork_url, "artwork.png"))

        await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)

    await ctx.respond("The queue is now empty!", flags=hikari.MessageFlag.EPHEMERAL)


@bot.command
@lightbulb.option(
    "volume",
    "The volume to set.",
    int,
    required=True,
    min_value=0,
    max_value=200,
)
@lightbulb.command("volume", "Skip the currently playing song.")
@lightbulb.implements(lightbulb.SlashCommand)
async def volume_command(
    ctx: lightbulb.Context,
) -> None:
    music: ongaku.Client = ctx.bot.d.ongaku_client

    if ctx.guild_id is None:
        raise lightbulb.OnlyInGuild

    player = music.get_player(ctx.guild_id)

    volume = ctx.options.volume

    if not isinstance(volume, int):
        await ctx.respond(
            "The query received was invalid.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    await player.set_volume(volume)

    await ctx.respond(
        f"The volume is now set to {volume}%",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@bot.command
@lightbulb.command("loop", "Enable or disable the looping of the current track.")
@lightbulb.implements(lightbulb.SlashCommand)
async def loop_command(
    ctx: lightbulb.Context,
) -> None:
    music: ongaku.Client = ctx.bot.d.ongaku_client

    if ctx.guild_id is None:
        raise lightbulb.OnlyInGuild

    player = music.get_player(ctx.guild_id)

    player.set_loop()

    if player.loop:
        if player.track:
            await ctx.respond(
                f"The player is now looping.\nTrack: {player.track.info.title}",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        else:
            await ctx.respond(
                "The player is now looping.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
    else:
        await ctx.respond(
            "The player is no longer looping.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@bot.command
@lightbulb.command("shuffle", "Shuffle the current queue.")
@lightbulb.implements(lightbulb.SlashCommand)
async def shuffle_command(
    ctx: lightbulb.Context,
) -> None:
    music: ongaku.Client = ctx.bot.d.ongaku_client

    if ctx.guild_id is None:
        raise lightbulb.OnlyInGuild

    player = music.get_player(ctx.guild_id)

    player.shuffle()

    await ctx.respond(
        "The queue has been successfully shuffled.",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@bot.command
@lightbulb.option(
    "speed",
    "The speed to change the player to.",
    float,
    required=False,
    min_value=0,
    max_value=5,
    default=1,
)
@lightbulb.command("speed", "Increase the speed of the currently playing song.")
@lightbulb.implements(lightbulb.SlashCommand)
async def speed_command(
    ctx: lightbulb.Context,
) -> None:
    music: ongaku.Client = ctx.bot.d.ongaku_client

    if ctx.guild_id is None:
        raise lightbulb.OnlyInGuild

    player = music.get_player(ctx.guild_id)

    if player.filters:
        filters = ongaku.FiltersBuilder.from_filter(player.filters)
    else:
        filters = ongaku.FiltersBuilder()

    speed = ctx.options.speed

    if not isinstance(speed, float | int):
        await ctx.respond(
            "The query received was invalid.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    filters.set_timescale(speed=speed)

    await player.set_filters(filters)

    await ctx.respond(
        f"The speed has now been set to {speed}",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@bot.command
@lightbulb.command("stop", "Stop the currently playing song.")
@lightbulb.implements(lightbulb.SlashCommand)
async def stop_command(
    ctx: lightbulb.Context,
) -> None:
    music: ongaku.Client = ctx.bot.d.ongaku_client

    if ctx.guild_id is None:
        raise lightbulb.OnlyInGuild

    player = music.get_player(ctx.guild_id)

    await player.stop()

    await ctx.respond(
        "The player has been stopped.",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@bot.command
@lightbulb.command(
    "disconnect",
    "Stop the currently playing song and disconnect from the VC.",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def disconnect_command(
    ctx: lightbulb.Context,
) -> None:
    music: ongaku.Client = ctx.bot.d.ongaku_client

    if ctx.guild_id is None:
        raise lightbulb.OnlyInGuild

    player = music.get_player(ctx.guild_id)

    await player.disconnect()

    await ctx.respond(
        "The player has been disconnected.",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


if __name__ == "__main__":
    bot.run()
