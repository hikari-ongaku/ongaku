---
title: Changelog
description: Changelog for Ongaku
hide:
  - navigation
  - toc
---

# Changelogs

All the changelogs for `hikari-ongaku`.

## **v1.0.4**
* Add Lavalink v4.2.0 support (DAVE)

## **v1.0.3**
* Youtube extension: Youtube now has an extension, for setting and getting the access tokens.
* Fix logger: Logging now works properly.

## **v1.0.2**
* Setting session: All rest methods allow you to specify a session to use to call said method.
* `__slots__`: All Classes now use slots, which should improve performance.
* Filters: Proper filter support has now been added! check them out [here](https://ongaku.mplaty.com/gs/filters/).
* Loop: You can now loop a song via the `.set_loop()` method.
* Requestor: The requestor is now stored within the `user_data`, which means that if you set a requestor for a track, it should show up in the events.
* Build error gives a optional exception (if one was raised) and an optional reason.
* Tests have been added to extensions.

## **v1.0.1**

- Import issue: Moved back to `setup.py` as its much more stable, and does not have weird errors.
- Documentation: Cleaned up issue in 1.0.0 changelog.

## **v1.0.0**
- JSON -> ORJSON: switched libraries, due to performance increases. (only if you do `pip install ongaku[speedups]`, which also enables a few other performance improvers.)
- SearchResult -> typing.Sequence[Track]: This has been changed, so there is less boilerplate within ongaku. This may break your code, so please check it.
- channel_id and guild_id: channel and guild id related things, have been modified, so they now support either giving them a guild/channel object, or just a snowflake.
- abc/impl: Most items have been separated into two different places. ABC (abstract classes) and Impl (implementation) ABC's are for the classes, and what they hold, where as Impl, is the actual implementation of it (the ones you can actually call/build)
- Tests: The long awaited tests. All files, and anything called has tests, meaning that most bugs should not exist in the code anymore.
- `Exception` to `Error`: All exceptions, now end with `Error`, not `Exception` to match other python exceptions.
- integer timestamp to `datetime.datetime`: Some fields used to send a UNIX timestamp, and it was set to an integer. It is now set to `datetime.datetime`.
- Client:
    - session handling: All session handling has been completely redesigned. auto_sessions no longer exists, and has been replaced by a `SessionHandler`'s, so now anyone can easily build their own sessions within, and change to different session types.
    - create, fetch and deleting sessions can now be done within the client directly.
    - server connection: All server connections have been re-built, to support more than one server connection (it will not use multiple servers, but it does use the other servers as fallbacks).
    - all methods within ongaku have been re-written to be cleaner, and easier to understand.
    - Added arc and tanjun injection support ([more here](gs/injection.md))
    - async to sync: fetching a player no longer requires an async function. You can simply call `.fetch_player()` without `await` at the start.
    - Players and sessions must be unique: Adding a player with the same guild id as another player or creating a session with the same name as another session, will raise a `UniqueError`.
- Routeplanner:
    - Docs: added route planner docs.
    - ABC: added route planner abstract classes.
- Session:
    - Kill players: Sessions now kill, and delete all players when shutting down.
    - request: You can now make requests to a session! simply call `.request()` and add your arguments, and away you go!
- Player:
    - Add: Add now supports a singular track, a sequence of tracks or a playlist.
    - Fixed issue where the track would continue playing, if you disconnected the bot.
    - Shuffle: Shuffle the current queue!
    - Volume reset: Allow for you to reset the volume
    - async to sync: Made a few methods like `set_autoplay` and `shuffle` to become sync.
    - autoplay: Autoplay now starts a new track on `LOADFAILED` as well as `FINISHED`
- Rest:
    - ClientSession: Client session is now re-used instead of creating and deleting a session, every time a new rest action is done.
    - RoutePlanner: added route planner endpoints (`fetch_routeplanner_status`, `update_routeplanner_address` and `update_all_routeplanner_addresses`)
    - new handling: All rest methods are now handled in a new way, that both makes them safer, and the code is also shorter.
    - all events are no longer split apart. They are all within rest. e.g. from `rest.player.update()` to `rest.update_player()`
    - fixed update session method: Update session now includes two arguments (resuming, timeout) which were not included, and would result in an error if called.
- Events:
    - Session and client: All events now have the client, and session attached to them.
    - Payload event: Ever wanted just a plain payload event, maybe for debugging, or client side stuff? Here you go!
- Fixes:
    - Fixed rare disconnection issue where the endpoint would fail.
    - Errors now actually report their errors in the terminal, meaning that if your lavalink server is not online, and you try to connect, you will get warnings if it can't do it.
    - Other, unlisted errors should be fixed.
- Documentation:
    - All documentation has been re-written, to make it easier to understand parts of the code, and give more detailed explanations of what things do.

## **v0.5.1**

- Logging removed from imports.

## **v0.5.0**

- About: Added about, so a few terminal commands can be used, to check the version of ongaku your using, about ongaku, and where it is installed.
- Logging: Added logging, mainly warnings, and errors, but also, traces, for errors and debugging stuff.
- Examples: Cleaned up examples, and made them more accurate.
- ABC:
    - Complete reformatting: all abc files, have been reformatted, to use the new method of handling payloads, [pydantic](https://docs.pydantic.dev/)!
- Fixes:
    - Player skip: An error occurred, when trying to skip a song, the bot would attempt to also use `autoplay` to play the next song, and keep looping, causing it to spam lavalink with update requests.
    - Player play: There was an issue, where, if the queue had songs, but you didn't provide a track, it would raise an error. This is no longer an issue.
    - Player autoplay: Fixed an issue, where it would duplicate the next track, when auto-playing tracks.
    - Player/Session Shutdown: Fixed an issue, where sessions were not shut down at all, and hikari forcefully shuts them down. This is no longer an issue, and you will not see a warning like `W 0000-00-00 00:00:00,000 hikari.bot: terminating 1 remaining tasks forcefully`
    - Player disconnect: Fixed an issue, where if you used `player.disconnect()`, it would not remove it from the node.

## **v0.4.1**

- Extensions:
    - Added the ability to create extensions for ongaku.
    - Checker: Checks if a link, contains a video/playlist.
- Fixes:
    - player skip: Fixed an issue where the skip function would not work.
    - player stop: Added a new function, to stop the current track, via removing it from the guilds session.

## **v0.4.0**

- Ongaku -> Client: `ongaku.Ongaku()` has been replaced by `ongaku.Client()`.
- Client:
    - create, delete, and fetch player, has been renamed from `client.create_player()` -> `client.player.create()`, for all types.
- `nodes` -> `sessions`: Nodes has been replaced with sessions, to match lavalink.
- Sessions:
    - Websocket: It is now handled as a task, and no longer concurrently.
    - Manual: The ability to create your own sessions, by whatever methods you want.
    - Connection: The connection to the websocket lavalink provides, is now handled as a task, and not directly blocking your code. This also means it can be shutdown.
- Player:
    - Exceptions: More cleanly handled, plus, documentation on those exceptions as well.
    - Updates: Each time a function is called, the player is actually modified (via any function) the player will be modified to reflect that.
    - volume -> set_volume: The reason for this rename, is so that the `volume` is the current volume, and `set_volume` actually sets the volume.
    - auto-play: a new feature has been added, called autoplay. (technically, it already existed) but now you can disable (and re-enable) it, and check its status via `player.set_autoplay()` and `player.autoplay`
- Rest changes:
    - General Function: All rest actions are no longer scattered across with some containing some error exceptions, and others containing different exceptions, they all will except, in the exact same way.
    - Searching: Ongaku no longer handles your queries, with whether or not, they are a url, or a query for youtube, youtube music, or soundcloud.
    - RestApi -> RESTClient: `RestApi` has been replaced by `RESTClient` for more consistent naming. (This does not change anything outside of it.)
    - Added methods: added `decode_track`, and `decode_tracks` for more search functions.
- Documentation:
    - Type checking: There is now type checking for the doc strings, so, they should look similar, with a lot more information packed within them.
    - Extensions: New tab added, for extensions, where extensions can be added in the future.

## **v0.3.0**

- Filters: Added filters, for the lavalink players, so your able to change different sound effects for the players, like the EQ, Low Pass, Vibrato, and more.
- Requestors: Added the ability to set a requestor to a specific track. When a song is added to the player, you can set a requestor as an optional argument. You can then fetch it via the [track][ongaku.abc.track.Track].
- Auto Nodes: Automatically creates nodes, for each new shard within the hikari bot.
