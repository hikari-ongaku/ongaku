---
title: Youtube
description: All functions and usage of the injection extension.
---

# Injection

Custom functions for injecting and ensuring certain values.

Using the injection system should have ongaku installed via the following:

```
pip install hikari-ongaku[injection]
```

## Arc Ensure Player

Ensures a player exists, and if it doesn't, raises an error.

This function is attached to a function within arc.


```py
from ongaku.ext import injection

@client.include
@arc.with_hook(injection.arc_ensure_player)
@arc.slash_command("example", "example commands.")
async def example_command(
    ctx: arc.GatewayContext,
    player: ongaku.Player = arc.inject(),
) -> None:
    pass
```

In this scenario, the player value is expected.
This will raise an `arc.GuildOnlyError` if the command is not ran within a guild,
Or an `ongaku.PlayerMissingError` if the guild does not have a player.
Arc will then propagate the value for error handling.

You can handle that through arc's [error handling system](https://arc.hypergonial.com/guides/error_handling/).

!!! warning
    This function is only supported when [`arc`](https://arc.hypergonial.com/) library is used.
