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
    name="tanjun-session",
    host="127.0.0.1",
    password="youshallnotpass",
)


# ╔════════╗
# ║ Events ║
# ╚════════╝


@bot.listen(ongaku.ReadyEvent)
async def ready_event(event: ongaku.ReadyEvent):
    logging.info(
        f"Ready Event, Resumed: {event.resumed}, session id: {event.session_id}",
    )


@bot.listen(ongaku.TrackStartEvent)
async def track_start_event(event: ongaku.TrackStartEvent):
    logging.info(
        f"Track Started Event, guild: {event.guild_id}, Track Title: {event.track.info.title}",
    )


@bot.listen(ongaku.TrackEndEvent)
async def track_end_event(event: ongaku.TrackEndEvent):
    logging.info(
        f"Track Ended Event, guild: {event.guild_id}, Track Title: {event.track.info.title}, Reason: {event.reason.name}",
    )


@bot.listen(ongaku.TrackExceptionEvent)
async def track_exception_event(event: ongaku.TrackExceptionEvent):
    logging.info(
        f"Track Exception Event, guild: {event.guild_id}, Track Title: {event.track.info.title}, Exception message: {event.exception.message}",
    )


@bot.listen(ongaku.TrackStuckEvent)
async def track_stuck_event(event: ongaku.TrackStuckEvent):
    logging.info(
        f"Track Stuck Event, guild: {event.guild_id}, Track Title: {event.track.info.title}, Threshold ms: {event.threshold_ms}",
    )


@bot.listen(ongaku.WebsocketClosedEvent)
async def websocket_close_event(event: ongaku.WebsocketClosedEvent):
    logging.info(
        f"Websocket Close Event, guild: {event.guild_id}, Reason: {event.reason}, Code: {event.code}, By Remote: {event.by_remote}",
    )


@bot.listen(ongaku.QueueNextEvent)
async def queue_next_event(event: ongaku.QueueNextEvent):
    logging.info(
        f"guild: {event.guild_id}'s track: {event.old_track.info.title} has finished! Now playing: {event.track.info.title}",
    )


@bot.listen(ongaku.QueueEmptyEvent)
async def queue_empty_event(event: ongaku.QueueEmptyEvent):
    logging.info(f"Queue is empty in guild: {event.guild_id}")


# ╔══════════╗
# ║ Commands ║
# ╚══════════╝


component = tanjun.Component()


@component.with_slash_command
@tanjun.with_str_slash_option("query", "The song you wish to play.")
@tanjun.as_slash_command("play", "Play a song.")
async def play_command(
    ctx: tanjun.abc.SlashContext,
    query: str,
    ongaku_client: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        await ctx.create_initial_response(
            "This command must be ran in a guild.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    voice_state = bot.cache.get_voice_state(ctx.guild_id, ctx.author.id)
    if not voice_state or not voice_state.channel_id:
        await ctx.create_initial_response(
            "you are not in a voice channel.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    checked_query = await checker.check(query)

    if checked_query.type == checker.CheckedType.QUERY:
        result = await ongaku_client.rest.load_track(f"ytsearch:{checked_query.value}")
    else:
        result = await ongaku_client.rest.load_track(checked_query.value)

    if result is None:
        await ctx.create_initial_response(
            "Sorry, no songs were found.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    track: ongaku.Track

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

    try:
        player = ongaku_client.fetch_player(ctx.guild_id)
    except ongaku.PlayerMissingError:
        player = ongaku_client.create_player(ctx.guild_id)

    if player.connected is False:
        await player.connect(voice_state.channel_id)

    try:
        await player.play(track)
    except Exception as e:
        raise e

    await ctx.create_initial_response(
        embed=embed,
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@component.with_slash_command
@tanjun.with_str_slash_option("query", "The song you wish to play.")
@tanjun.as_slash_command("add", "Add a song (or songs!)")
async def add_command(
    ctx: tanjun.abc.SlashContext,
    query: str,
    ongaku_client: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        await ctx.create_initial_response(
            "This command must be ran in a guild.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    try:
        current_player = ongaku_client.fetch_player(ctx.guild_id)
    except Exception:
        await ctx.create_initial_response(
            "You must have a player currently running!",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    checked_query = await checker.check(query)

    if checked_query.type == checker.CheckedType.QUERY:
        result = await ongaku_client.rest.load_track(f"ytsearch:{checked_query.value}")
    else:
        result = await ongaku_client.rest.load_track(checked_query.value)

    if result is None:
        await ctx.create_initial_response(
            "Sorry, no songs were found.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    tracks: list[ongaku.Track] = []

    if isinstance(result, ongaku.Playlist):
        tracks.extend(result.tracks)

    elif isinstance(result, ongaku.Track):
        tracks.append(result)

    else:
        tracks.extend(result)

    current_player.add(tracks)

    embed = hikari.Embed(
        title="Tracks added",
        description=f"All the tracks that have been added. (only shows top 25.)\nTotal tracks added: {len(tracks)}",
    )

    for track in tracks:
        if len(embed.fields) >= 25:
            break
        embed.add_field(track.info.title, track.info.author)

    await ctx.respond(embed=embed)


@component.with_slash_command
@tanjun.as_slash_command("pause", "pause or unpause the currently playing song.")
async def pause_command(
    ctx: tanjun.abc.SlashContext,
    ongaku_client: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        await ctx.create_initial_response(
            "This command must be ran in a guild.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    try:
        current_player = ongaku_client.fetch_player(ctx.guild_id)
    except Exception:
        await ctx.create_initial_response(
            "You must have a player currently running!",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    await current_player.pause()

    if current_player.is_paused:
        await ctx.create_initial_response(
            "Music has been paused.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
    else:
        await ctx.create_initial_response(
            "Music has been resumed.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@component.with_slash_command
@tanjun.as_slash_command("queue", "View the queue of the player.")
async def queue_command(
    ctx: tanjun.abc.SlashContext,
    ongaku_client: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        await ctx.create_initial_response(
            "Guild ID is none! You must be in a guild to run this command.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    try:
        player = ongaku_client.fetch_player(ctx.guild_id)
    except Exception:
        await ctx.create_initial_response(
            "There is no player currently playing in this server.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    if len(player.queue) == 0:
        await ctx.respond("There is not tracks in the queue currently.")
        return

    queue_embed = hikari.Embed(
        title="Queue",
        description=f"The queue for this server.\nCurrent song: {player.queue[0].info.title}",
    )

    for x in range(len(player.queue)):
        if x == 0:
            continue

        if x >= 25:
            break

        track = player.queue[x]

        queue_embed.add_field(track.info.title, track.info.author)

    await ctx.respond(embed=queue_embed)


@component.with_slash_command
@tanjun.with_int_slash_option(
    "volume",
    "The volume number you wish to set.",
    min_value=1,
    default=1,
)
@tanjun.as_slash_command("queue", "View the queue of the player.")
async def volume_command(
    ctx: tanjun.abc.SlashContext,
    volume: int,
    ongaku_client: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        await ctx.create_initial_response(
            "Guild ID is none! You must be in a guild to run this command.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    try:
        player = ongaku_client.fetch_player(ctx.guild_id)
    except Exception:
        await ctx.create_initial_response(
            "There is no player currently playing in this server.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    try:
        await player.set_volume(volume)
    except ValueError:
        await ctx.create_initial_response(
            "Sorry, but you have entered an invalid number.",
        )
        return

    await ctx.create_initial_response(
        f"the volume has successfully been set to {volume}/100",
    )


@component.with_slash_command
@tanjun.with_int_slash_option(
    "amount",
    "The amount of songs you wish to skip. default is 1.",
    min_value=1,
    default=1,
)
@tanjun.as_slash_command("queue", "View the queue of the player.")
async def skip_command(
    ctx: tanjun.abc.SlashContext,
    amount: int,
    ongaku_client: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        await ctx.create_initial_response(
            "Guild ID is none! You must be in a guild to run this command.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    try:
        player = ongaku_client.fetch_player(ctx.guild_id)
    except Exception:
        await ctx.create_initial_response(
            "There is no player currently playing in this server.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    try:
        await player.skip(amount)
    except ongaku.PlayerQueueError:
        await ctx.create_initial_response(
            "It looks like the queue is empty, so no new songs will be played.",
        )
        return

    await ctx.create_initial_response(f"{amount} song(s) were successfully skipped.")


@component.with_slash_command
@tanjun.as_slash_command(
    "stop",
    "Stops the player, and disconnects it from the server.",
)
async def stop_command(
    ctx: tanjun.abc.SlashContext,
    ongaku_client: ongaku.Client = tanjun.inject(),
) -> None:
    if ctx.guild_id is None:
        await ctx.create_initial_response(
            "Guild ID is none! You must be in a guild to run this command.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    try:
        player = ongaku_client.fetch_player(ctx.guild_id)
    except Exception:
        await ctx.create_initial_response(
            "There is no player currently playing in this server.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    await player.disconnect()

    await ctx.respond("Successfully stopped the player.")


if __name__ == "__main__":
    client.add_component(component)
    bot.run()
