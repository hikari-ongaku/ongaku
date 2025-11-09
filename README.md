# Ongaku
A simple voice library for Hikari.

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/hikari-ongaku)](https://pypi.org/project/hikari-ongaku)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)
![Pyright](https://badgen.net/badge/Pyright/strict/2A6DB2)
[![Lavalink](https://badgen.net/badge/Lavalink/V4/ff624a)](https://lavalink.dev/)

</div>

Ongaku is a voice library that allows for playing tracks from a lavalink server, using the [Hikari discord API](https://hikari-py.dev/).

Ongaku tries to make everything as simple as possible for new users, but still having full access to add custom plugins and change (or create) session handlers.

## Current Features

- Player control
   - Playlists
   - Queuing
      - Adding songs.
      - Shuffling the queue.
      - Skipping a song or multiple.
      - Deleting via position, or a track object.
      - Clearing the queue.
   - Requestors
      - Setting the requestor of a track.
      - Viewing requestor in events.
   - Seeking/Reversing the tracks position.
   - Volume control
   - Looping (loops the same song over and over.)
   - Filters (allows for changing the way audio plays and sounds.)
- Events
   - Ready Event (when a session is online.)
   - Player Update Event (when a player gets updated.)
   - Statistics Event (about the server.)
   - Track Start Event
   - Track End Event
   - Track Exception Event
   - Track Stuck Event
   - Empty Queue Event
   - Next Queue Event
- Sessions
   - BasicSessionHandler (Gives next available session)
- Others
   - Traces (for debugging code.)
   - Tests (Full test coverage.)

## Future Features

- More session handlers: so there is more methods to use the sessions you have provided.
- Cache: a method to store information, and fetch it later, from events and rest actions.
- Changing channels: support for moving to different channels, without leaving and rejoining.
- Session failures: More control, like seeing why a session failed and allow for reconnecting, or resetting attempts.

## Installation

To install ongaku, run the following command:

```sh
pip install -U hikari-ongaku
```

To check if ongaku has successfully installed, run the following command:

```sh
python3 -m ongaku
# On Windows you may need to run:
py -m ongaku
```

## Getting Started

for more about how to get started see the [docs](https://ongaku.mplaty.com/gs/).

```py
import typing
import hikari
import ongaku

# Create a GatewayBot (RESTBot's are not supported.)
bot = hikari.GatewayBot(token="...")

# Give ongaku the bot.
client = ongaku.Client(bot)

@bot.listen()
async def message_event(
    event: hikari.GuildMessageCreateEvent
) -> None:
   # Ignore anything that has no content, is not a human, or is not in a guild.
   if not event.content or not event.is_human or not event.guild_id:
      return

   # Ignore anything that is not the play command.
   if not event.content.startswith("!play"):
      return

   # Get the query from play "command".
   query = event.content.strip("!play ")

   # Make sure the user is in a valid voice channel.
   voice_state = bot.cache.get_voice_state(event.guild_id, event.author.id)
   if not voice_state or not voice_state.channel_id:
      await bot.rest.create_message(event.channel_id, "you are not in a voice channel.", reply=event.message)
      return

   # Fetch the track from the query string. (This searches just Youtube.)
   result = await client.rest.load_track(f"ytsearch:{query}")

   # If the song is `None` let them know it failed.
   if result is None:
      await bot.rest.create_message(event.channel_id, "No songs were found.", reply=event.message)
      return

   # Create a player (or if it already exists, grab that one!)
   player = client.create_player(event.guild_id)

   # Add the playlist, track or search result to the player.
   if isinstance(result, typing.Sequence):
      player.add(result[0])
   else:
      player.add(result)

   # Tell the player to start playing the song!
   await player.play()

   await bot.rest.create_message(event.channel_id, f"Playing {player.queue[0].info.title}", reply=event.message)
```

### Extensions

Ongaku has a few built-in extensions:

- [`ext.checker`](https://ongaku.mplaty.com/ext/checker/) - For checking if a song is a URL, or just a query.
- [`ext.injection`](https://ongaku.mplaty.com/ext/injection/) - For injecting player instances into commands.
- [`ext.youtube`](https://ongaku.mplaty.com/ext/youtube/) - For setting or getting the token for your youtube config.

### Issues and support

For general usage help or questions, see the `#ongaku` channel in the [hikari discord](https://discord.gg/hikari), if you have found a bug or have a feature request, feel free to [open an issue](https://github.com/hikari-ongaku/hikari-ongaku/issues/new).

### Links

- [**Documentation**](https://ongaku.mplaty.com)
- [**Examples**](https://github.com/hikari-ongaku/hikari-ongaku/tree/main/examples)
- [**License**](https://github.com/hikari-ongaku/hikari-ongaku/blob/main/LICENSE)
