# ╔════════════════╗
# ║ Tanjun example ║
# ╚════════════════╝
from __future__ import annotations

import logging

import hikari
import tanjun

import ongaku
from ongaku.ext import checker

bot = hikari.GatewayBot("...")

client = tanjun.Client.from_gateway_bot(bot)

ongaku_client = ongaku.Client.from_tanjun(client)

ongaku_client.create_session(
    "tanjun-session",
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

hooks = tanjun.AnyHooks()


class GuildOnlyError(Exception): ...


@hooks.with_on_error
async def error_hook(ctx: tanjun.abc.Context, error: Exception) -> bool | None:
    if not isinstance(ctx, tanjun.abc.SlashContext):
        return False

    if isinstance(error, GuildOnlyError):
        await ctx.create_initial_response(
            "You need to be in a guild to run this command.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )

        return True

    if isinstance(error, ongaku.PlayerMissingError):
        await ctx.create_initial_response(
            "No player was found for this guild.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )

        return True
    return None


# ╔══════════╗
# ║ Commands ║
# ╚══════════╝


component = tanjun.Component()


@component.with_slash_command
@tanjun.with_str_slash_option("query", "The name, or link of the song to play.")
@tanjun.as_slash_command("play", "Play a song or playlist.")
async def play_command(
    ctx: tanjun.abc.SlashContext,
    query: str,
    music: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        raise GuildOnlyError

    voice_state = bot.cache.get_voice_state(ctx.guild_id, ctx.author.id)
    if not voice_state or not voice_state.channel_id:
        await ctx.create_initial_response(
            "you are not in a voice channel.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    if checker.check(query):
        result = await music.rest.load_track(query)
    else:
        result = await music.rest.load_track(f"ytsearch:{query}")

    if result is None:
        await ctx.create_initial_response(
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

    await ctx.create_initial_response(
        embed=embed,
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@component.with_slash_command
@tanjun.with_str_slash_option("query", "The name, or link of the song to add.")
@tanjun.as_slash_command("add", "Add more songs or a playlist.")
async def add_command(
    ctx: tanjun.abc.SlashContext,
    query: str,
    music: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        raise GuildOnlyError

    player = music.get_player(ctx.guild_id)

    if checker.check(query):
        result = await music.rest.load_track(query)
    else:
        result = await music.rest.load_track(f"ytsearch:{query}")

    if result is None:
        await ctx.create_initial_response(
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

    await ctx.create_initial_response(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)


@component.with_slash_command
@tanjun.as_slash_command("queue", "View the current queue.")
async def queue_command(
    ctx: tanjun.abc.SlashContext,
    music: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        raise GuildOnlyError

    player = music.get_player(ctx.guild_id)

    if len(player.queue) == 0:
        await ctx.create_initial_response(
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

    await ctx.create_initial_response(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)


@component.with_slash_command
@tanjun.as_slash_command("pause", "Pause or play the current song.")
async def pause_command(
    ctx: tanjun.abc.SlashContext,
    music: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        raise GuildOnlyError

    player = music.get_player(ctx.guild_id)

    await player.pause()

    if player.is_paused:
        await ctx.create_initial_response(
            "The song has been paused.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
    else:
        await ctx.create_initial_response(
            "The song has been unpaused.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@component.with_slash_command
@tanjun.as_slash_command("skip", "Skip the currently playing song.")
async def skip_command(
    ctx: tanjun.abc.SlashContext,
    music: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        raise GuildOnlyError

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

        await ctx.create_initial_response(
            embed=embed,
            flags=hikari.MessageFlag.EPHEMERAL,
        )

    await ctx.create_initial_response(
        "The queue is now empty!",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@component.with_slash_command
@tanjun.with_int_slash_option(
    "volume",
    "The volume to set.",
    min_value=0,
    max_value=200,
)
@tanjun.as_slash_command("volume", "Skip the currently playing song.")
async def volume_command(
    ctx: tanjun.abc.SlashContext,
    volume: int,
    music: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        raise GuildOnlyError

    player = music.get_player(ctx.guild_id)

    await player.set_volume(volume)

    await ctx.create_initial_response(
        f"The volume is now set to {volume}%",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@component.with_slash_command
@tanjun.as_slash_command("loop", "Enable or disable the looping of the current track.")
async def loop_command(
    ctx: tanjun.abc.SlashContext,
    music: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        raise GuildOnlyError

    player = music.get_player(ctx.guild_id)

    player.set_loop()

    if player.loop:
        if player.track:
            await ctx.create_initial_response(
                f"The player is now looping.\nTrack: {player.track.info.title}",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        else:
            await ctx.create_initial_response(
                "The player is now looping.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
    else:
        await ctx.create_initial_response(
            "The player is no longer looping.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@component.with_slash_command
@tanjun.as_slash_command("shuffle", "Shuffle the current queue.")
async def shuffle_command(
    ctx: tanjun.abc.SlashContext,
    music: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        raise GuildOnlyError

    player = music.get_player(ctx.guild_id)

    player.shuffle()

    await ctx.create_initial_response(
        "The queue has been successfully shuffled.",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@component.with_slash_command
@tanjun.with_float_slash_option(
    "speed",
    "The speed to change the player to.",
    min_value=0,
    max_value=5,
    default=1,
)
@tanjun.as_slash_command("speed", "Increase the speed of the currently playing song.")
async def speed_command(
    ctx: tanjun.abc.SlashContext,
    speed: int,
    music: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        raise GuildOnlyError

    player = music.get_player(ctx.guild_id)

    if player.filters:
        filters = ongaku.FiltersBuilder.from_filter(player.filters)
    else:
        filters = ongaku.FiltersBuilder()

    filters.set_timescale(speed=speed)

    await player.set_filters(filters)

    await ctx.create_initial_response(
        f"The speed has now been set to {speed}",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@component.with_slash_command
@tanjun.as_slash_command("stop", "Stop the currently playing song.")
async def stop_command(
    ctx: tanjun.abc.SlashContext,
    music: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        raise GuildOnlyError

    player = music.get_player(ctx.guild_id)

    await player.stop()

    await ctx.create_initial_response(
        "The player has been stopped.",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@component.with_slash_command
@tanjun.as_slash_command(
    "disconnect",
    "Stop the currently playing song and disconnect from the VC.",
)
async def disconnect_command(
    ctx: tanjun.abc.SlashContext,
    music: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        raise GuildOnlyError

    player = music.get_player(ctx.guild_id)

    await player.disconnect()

    await ctx.create_initial_response(
        "The player has been disconnected.",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


if __name__ == "__main__":
    client.add_component(component)
    component.set_hooks(hooks)
    bot.run()
