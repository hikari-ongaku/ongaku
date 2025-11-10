# ╔════════════════╗
# ║ Hikari example ║
# ╚════════════════╝
from __future__ import annotations

import logging

import hikari

import ongaku
from ongaku.ext import checker

bot = hikari.GatewayBot(
    "...",
    suppress_optimization_warning=True,
    intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT,
)
bot = hikari.GatewayBot(
    "...",
    suppress_optimization_warning=True,
    intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT,
)

ongaku_client = ongaku.Client(bot)

ongaku_client.create_session(
    "hikari-session",
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


@bot.listen()
async def error_handler(
    event: hikari.ExceptionEvent[hikari.GuildMessageCreateEvent],
) -> None:
    if isinstance(event.exception, ongaku.PlayerMissingError):
        await event.app.rest.create_message(
            event.failed_event.channel_id,
            "No player was found for this guild.",
            reply=event.failed_event.message,
        )


# ╔══════════╗
# ║ Commands ║
# ╚══════════╝


prefix = "!"


def handle_command(content: str, name: str) -> list[str]:
    if content.startswith(prefix + name):
        content = content.strip(prefix + name + " ")
        return content.split(" ")

    return []


@bot.listen()
async def play_command(event: hikari.GuildMessageCreateEvent) -> None:
    if event.content is None:
        return

    if event.is_bot:
        return

    args = handle_command(event.content, "play")

    if len(args) < 1:
        await event.app.rest.create_message(
            event.channel_id,
            "You need to provide a track to play.",
            reply=event.message,
        )
        return

    voice_state = bot.cache.get_voice_state(event.guild_id, event.author.id)
    if not voice_state or not voice_state.channel_id:
        await event.app.rest.create_message(
            event.channel_id,
            "you are not in a voice channel.",
            reply=event.message,
        )
        return

    query = args[0]

    if checker.check(query):
        result = await ongaku_client.rest.load_track(query)
    else:
        result = await ongaku_client.rest.load_track(f"ytsearch:{query}")

    if result is None:
        await event.app.rest.create_message(
            event.channel_id,
            "Sorry, no songs were found.",
            reply=event.message,
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

    player = ongaku_client.create_player(event.guild_id)

    if player.is_connected is False:
        await player.connect(voice_state.channel_id)

    await player.play(track)

    await event.app.rest.create_message(
        event.channel_id,
        embed=embed,
        reply=event.message,
    )


@bot.listen()
async def add_command(event: hikari.GuildMessageCreateEvent) -> None:
    if event.content is None:
        return

    if event.is_bot:
        return

    args = handle_command(event.content, "add")

    if len(args) < 1:
        await event.app.rest.create_message(
            event.channel_id,
            "You need to provide a track to add.",
            reply=event.message,
        )
        return

    player = ongaku_client.get_player(event.guild_id)

    query = args[0]

    if checker.check(query):
        result = await ongaku_client.rest.load_track(query)
    else:
        result = await ongaku_client.rest.load_track(f"ytsearch:{query}")

    if result is None:
        await event.app.rest.create_message(
            event.channel_id,
            "Sorry, no songs were found.",
            reply=event.message,
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

    await event.app.rest.create_message(
        event.channel_id,
        embed=embed,
        reply=event.message,
    )


@bot.listen()
async def queue_command(event: hikari.GuildMessageCreateEvent) -> None:
    if event.content is None:
        return

    if event.is_bot:
        return

    if len(handle_command(event.content, "queue")) > 0:
        await event.app.rest.create_message(
            event.channel_id,
            "Paused does not take any arguments.",
            reply=event.message,
        )
        return

    player = ongaku_client.get_player(event.guild_id)

    if len(player.queue) == 0:
        await event.app.rest.create_message(
            event.channel_id,
            "There is no songs in the queue.",
            reply=event.message,
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

    await event.app.rest.create_message(
        event.channel_id,
        embed=embed,
        reply=event.message,
    )


@bot.listen()
async def pause_command(event: hikari.GuildMessageCreateEvent) -> None:
    if event.content is None:
        return

    if event.is_bot:
        return

    if len(handle_command(event.content, "pause")) > 0:
        await event.app.rest.create_message(
            event.channel_id,
            "Paused does not take any arguments.",
            reply=event.message,
        )
        return

    player = ongaku_client.get_player(event.guild_id)

    await player.pause()

    if player.is_paused:
        await event.app.rest.create_message(
            event.channel_id,
            "The song has been paused.",
            reply=event.message,
        )
    else:
        await event.app.rest.create_message(
            event.channel_id,
            "The song has been unpaused.",
            reply=event.message,
        )


@bot.listen()
async def skip_command(event: hikari.GuildMessageCreateEvent) -> None:
    if event.content is None:
        return

    if event.is_bot:
        return

    if len(handle_command(event.content, "skip")) > 0:
        await event.app.rest.create_message(
            event.channel_id,
            "Skip does not take any arguments.",
            reply=event.message,
        )
        return

    player = ongaku_client.get_player(event.guild_id)

    await player.skip()

    if len(player.queue) > 0:
        embed = hikari.Embed(
            title=player.queue[0].info.title,
            description=f"Length: {player.queue[0].info.length / 1000}s\nArtist: {player.queue[0].info.author}",
        )

        artwork_url = player.queue[0].info.artwork_url

        if artwork_url:
            embed.set_thumbnail(hikari.files.URL(artwork_url, "artwork.png"))

        await event.app.rest.create_message(
            event.channel_id,
            embed=embed,
            reply=event.message,
        )

    await event.app.rest.create_message(
        event.channel_id,
        "The queue is now empty!",
        reply=event.message,
    )


@bot.listen()
async def volume_command(event: hikari.GuildMessageCreateEvent) -> None:
    if event.content is None:
        return

    if event.is_bot:
        return

    args = handle_command(event.content, "volume")

    if len(args) < 1:
        await event.app.rest.create_message(
            event.channel_id,
            "You need to provide a volume to set.",
            reply=event.message,
        )
        return

    player = ongaku_client.get_player(event.guild_id)

    volume = args[0]

    try:
        volume = int(volume)
    except Exception:
        await event.app.rest.create_message(
            event.channel_id,
            "The value provided was not an integer.",
            reply=event.message,
        )
        return

    await player.set_volume(volume)

    await event.app.rest.create_message(
        event.channel_id,
        f"The volume is now set to {volume}%",
        reply=event.message,
    )


@bot.listen()
async def loop_command(event: hikari.GuildMessageCreateEvent) -> None:
    if event.content is None:
        return

    if event.is_bot:
        return

    if len(handle_command(event.content, "loop")) > 0:
        await event.app.rest.create_message(
            event.channel_id,
            "Loop does not take any arguments.",
            reply=event.message,
        )
        return

    player = ongaku_client.get_player(event.guild_id)

    player.set_loop()

    if player.loop:
        if player.track:
            await event.app.rest.create_message(
                event.channel_id,
                f"The player is now looping.\nTrack: {player.track.info.title}",
                reply=event.message,
            )
        else:
            await event.app.rest.create_message(
                event.channel_id,
                "The player is now looping.",
                reply=event.message,
            )
    else:
        await event.app.rest.create_message(
            event.channel_id,
            "The player is no longer looping.",
            reply=event.message,
        )


@bot.listen()
async def shuffle_command(event: hikari.GuildMessageCreateEvent) -> None:
    if event.content is None:
        return

    if event.is_bot:
        return

    if len(handle_command(event.content, "shuffle")) > 0:
        await event.app.rest.create_message(
            event.channel_id,
            "Shuffle does not take any arguments.",
            reply=event.message,
        )
        return

    player = ongaku_client.get_player(event.guild_id)

    player.shuffle()

    await event.app.rest.create_message(
        event.channel_id,
        "The queue has been successfully shuffled.",
        reply=event.message,
    )


@bot.listen()
async def speed_command(event: hikari.GuildMessageCreateEvent) -> None:
    if event.content is None:
        return

    if event.is_bot:
        return

    args = handle_command(event.content, "speed")

    player = ongaku_client.get_player(event.guild_id)

    speed = 0 if len(args) < 1 else args[0]

    try:
        speed = float(speed)
    except Exception:
        await event.app.rest.create_message(
            event.channel_id,
            "The value provided was not a float.",
            reply=event.message,
        )
        return

    if player.filters:
        filters = ongaku.FiltersBuilder.from_filter(player.filters)
    else:
        filters = ongaku.FiltersBuilder()

    await player.set_filters(filters)

    await event.app.rest.create_message(
        event.channel_id,
        f"The speed has now been set to {speed}",
        reply=event.message,
    )


@bot.listen()
async def stop_command(event: hikari.GuildMessageCreateEvent) -> None:
    if event.content is None:
        return

    if event.is_bot:
        return

    if len(handle_command(event.content, "stop")) > 0:
        await event.app.rest.create_message(
            event.channel_id,
            "Stop does not take any arguments.",
            reply=event.message,
        )
        return

    player = ongaku_client.get_player(event.guild_id)

    await player.stop()

    await event.app.rest.create_message(
        event.channel_id,
        "The player has been stopped.",
        reply=event.message,
    )


@bot.listen()
async def disconnect_command(event: hikari.GuildMessageCreateEvent) -> None:
    if event.content is None:
        return

    if event.is_bot:
        return

    if len(handle_command(event.content, "disconnect")) > 0:
        await event.app.rest.create_message(
            event.channel_id,
            "Disconnect does not take any arguments.",
            reply=event.message,
        )
        return

    player = ongaku_client.get_player(event.guild_id)

    await player.disconnect()

    await event.app.rest.create_message(
        event.channel_id,
        "The player has been disconnected.",
        reply=event.message,
    )


if __name__ == "__main__":
    bot.run()
