# ╔══════════════════╗
# ║ Crescent example ║
# ╚══════════════════╝
from __future__ import annotations

import dataclasses
import logging

import crescent
import hikari

import ongaku
from ongaku.ext import checker


@dataclasses.dataclass
class OngakuModel:
    ongaku_client: ongaku.Client


bot = hikari.GatewayBot("...")

ongaku_client = ongaku.Client(bot)

ongaku_client.create_session(
    "crescent-session",
    host="127.0.0.1",
    password="youshallnotpass",
)

client = crescent.Client(bot, OngakuModel(ongaku_client))


# ╔════════╗
# ║ Events ║
# ╚════════╝


@client.include
@crescent.event
async def ready_event(event: ongaku.ReadyEvent) -> None:
    logging.info(
        "Ready Event, Resumed: %s, session id: %s",
        event.resumed,
        event.session_id,
    )


@client.include
@crescent.event
async def track_start_event(event: ongaku.TrackStartEvent) -> None:
    logging.info(
        "Track Started Event, guild: %s, Track Title: %s",
        event.guild_id,
        event.track.info.title,
    )


@client.include
@crescent.event
async def track_end_event(event: ongaku.TrackEndEvent) -> None:
    logging.info(
        "Track Ended Event, guild: %s, Track Title: %s, Reason: %s",
        event.guild_id,
        event.track.info.title,
        event.reason.name,
    )


@client.include
@crescent.event
async def track_exception_event(event: ongaku.TrackExceptionEvent) -> None:
    logging.info(
        "Track Exception Event, guild: %s, Track Title: %s, Exception message: %s",
        event.guild_id,
        event.track.info.title,
        event.exception.message,
    )


@client.include
@crescent.event
async def track_stuck_event(event: ongaku.TrackStuckEvent) -> None:
    logging.info(
        "Track Stuck Event, guild: %s, Track Title: %s, Threshold ms: %s",
        event.guild_id,
        event.track.info.title,
        event.threshold_ms,
    )


@client.include
@crescent.event
async def websocket_close_event(event: ongaku.WebsocketClosedEvent) -> None:
    logging.info(
        "Websocket Close Event, guild: %s, Reason: %s, Code: %s, By Remote: %s",
        event.guild_id,
        event.reason,
        event.code,
        event.by_remote,
    )


@client.include
@crescent.event
async def queue_next_event(event: ongaku.QueueNextEvent) -> None:
    logging.info(
        "guild: %s's track: %s has finished! Now playing: %s",
        event.guild_id,
        event.old_track.info.title,
        event.track.info.title,
    )


@client.include
@crescent.event
async def queue_empty_event(event: ongaku.QueueEmptyEvent) -> None:
    logging.info("Queue is empty in guild: %s", event.guild_id)


@client.include
@crescent.event
async def session_connected_event(event: ongaku.SessionConnectedEvent) -> None:
    logging.info(
        "Session %s has successfully connected to the lavalink server.",
        event.session.name,
    )


@client.include
@crescent.event
async def session_disconnected_event(event: ongaku.SessionDisconnectedEvent) -> None:
    logging.info(
        "Session %s has disconnected, code: %s, reason: %s",
        event.session.name,
        event.code,
        event.reason,
    )


@client.include
@crescent.event
async def session_error_event(event: ongaku.SessionErrorEvent) -> None:
    logging.info("Session %s has had an error occur.", event.session.name)


# ╔═══════════════╗
# ║ Error Handler ║
# ╚═══════════════╝


class GuildOnlyError(Exception): ...


@client.include
@crescent.catch_command(GuildOnlyError)
async def guild_only_error_handler(_exc: GuildOnlyError, ctx: crescent.Context) -> None:
    await ctx.respond(
        "This command must be ran in a guild.",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@client.include
@crescent.catch_command(ongaku.PlayerMissingError)
async def player_missing_error_handler(
    _exc: ongaku.PlayerMissingError,
    ctx: crescent.Context,
) -> None:
    await ctx.respond(
        "No player was found for this guild.",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


# ╔══════════╗
# ║ Commands ║
# ╚══════════╝


@client.include
@crescent.command(name="play", description="Play a song or playlist.")
class Play:
    query = crescent.option(str, "The name, or link of the song to play.")

    async def callback(self, ctx: crescent.Context) -> None:
        music: ongaku.Client = ctx.client.model.ongaku

        if ctx.guild_id is None:
            raise GuildOnlyError

        voice_state = bot.cache.get_voice_state(ctx.guild_id, ctx.user.id)
        if not voice_state or not voice_state.channel_id:
            await ctx.respond(
                "you are not in a voice channel.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        if checker.check(self.query):
            result = await music.rest.load_track(self.query)
        else:
            result = await music.rest.load_track(f"ytsearch:{self.query}")

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

        player = ongaku_client.create_player(ctx.guild_id)

        if player.is_connected is False:
            await player.connect(voice_state.channel_id)

        await player.play(track)

        await ctx.respond(
            embed=embed,
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@client.include
@crescent.command(name="add", description="Add more songs or a playlist.")
class Add:
    query = crescent.option(str, "The name, or link of the song to add.")

    async def callback(self, ctx: crescent.Context) -> None:
        music: ongaku.Client = ctx.client.model.ongaku

        if ctx.guild_id is None:
            raise GuildOnlyError

        player = music.get_player(ctx.guild_id)

        if checker.check(self.query):
            result = await ongaku_client.rest.load_track(self.query)
        else:
            result = await ongaku_client.rest.load_track(f"ytsearch:{self.query}")

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


@client.include
@crescent.command(name="queue", description="View the current queue.")
class Queue:
    async def callback(self, ctx: crescent.Context) -> None:
        music: ongaku.Client = ctx.client.model.ongaku

        if ctx.guild_id is None:
            raise GuildOnlyError

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


@client.include
@crescent.command(name="pause", description="Pause or play the current song.")
class Pause:
    async def callback(self, ctx: crescent.Context) -> None:
        music: ongaku.Client = ctx.client.model.ongaku

        if ctx.guild_id is None:
            raise GuildOnlyError

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


@client.include
@crescent.command(name="skip", description="Skip the currently playing song.")
class Skip:
    async def callback(self, ctx: crescent.Context) -> None:
        music: ongaku.Client = ctx.client.model.ongaku

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

            await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)

        await ctx.respond("The queue is now empty!", flags=hikari.MessageFlag.EPHEMERAL)


@client.include
@crescent.command(name="volume", description="Set the volume of the player.")
class Volume:
    volume = crescent.option(int, "The volume to set.", min_value=0, max_value=200)

    async def callback(self, ctx: crescent.Context) -> None:
        music: ongaku.Client = ctx.client.model.ongaku

        if ctx.guild_id is None:
            raise GuildOnlyError

        player = music.get_player(ctx.guild_id)

        await player.set_volume(self.volume)

        await ctx.respond(
            f"The volume is now set to {self.volume}%",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@client.include
@crescent.command(
    name="loop",
    description="Enable or disable the looping of the current track.",
)
class Loop:
    async def callback(self, ctx: crescent.Context) -> None:
        music: ongaku.Client = ctx.client.model.ongaku

        if ctx.guild_id is None:
            raise GuildOnlyError

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


@client.include
@crescent.command(name="shuffle", description="Shuffle the current queue.")
class Shuffle:
    async def callback(self, ctx: crescent.Context) -> None:
        music: ongaku.Client = ctx.client.model.ongaku

        if ctx.guild_id is None:
            raise GuildOnlyError

        player = music.get_player(ctx.guild_id)

        player.shuffle()

        await ctx.respond(
            "The queue has been successfully shuffled.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@client.include
@crescent.command(
    name="speed",
    description="Increase the speed of the currently playing song.",
)
class Speed:
    speed = crescent.option(
        float,
        "The speed to change the player to.",
        min_value=0,
        max_value=5,
    )

    async def callback(self, ctx: crescent.Context) -> None:
        music: ongaku.Client = ctx.client.model.ongaku

        if ctx.guild_id is None:
            raise GuildOnlyError

        player = music.get_player(ctx.guild_id)

        if player.filters:
            filters = ongaku.FiltersBuilder.from_filter(player.filters)
        else:
            filters = ongaku.FiltersBuilder()

        filters.set_timescale(speed=self.speed)

        await player.set_filters(filters)

        await ctx.respond(
            f"The speed has now been set to {self.speed}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@client.include
@crescent.command(name="stop", description="Stop the currently playing song.")
class Stop:
    async def callback(self, ctx: crescent.Context) -> None:
        music: ongaku.Client = ctx.client.model.ongaku

        if ctx.guild_id is None:
            raise GuildOnlyError

        player = music.get_player(ctx.guild_id)

        await player.stop()

        await ctx.respond(
            "The player has been stopped.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@client.include
@crescent.command(
    name="disconnect",
    description="Stop the currently playing song and disconnect from the VC.",
)
class Disconnect:
    async def callback(self, ctx: crescent.Context) -> None:
        music: ongaku.Client = ctx.client.model.ongaku

        if ctx.guild_id is None:
            raise GuildOnlyError

        player = music.get_player(ctx.guild_id)

        await player.disconnect()

        await ctx.respond(
            "The player has been disconnected.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


if __name__ == "__main__":
    bot.run()
