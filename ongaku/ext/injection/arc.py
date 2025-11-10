# MIT License

# Copyright (c) 2023-present MPlatypus

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Arc Injection.

Adds arc's ensure player, so you don't have to make sure its a player.
"""

from __future__ import annotations

import arc

from ongaku import errors
from ongaku.client import Client

__all__ = ("arc_ensure_player",)


async def arc_ensure_player(ctx: arc.GatewayContext, /) -> None:
    """Arc ensure player.

    This is an arc hook, that ensures that the player you are injecting, exists.

    !!! warning
        You need to install the arc version of ongaku.
        ```
        pip install ongaku[arc]
        ```

    Example
    -------
    ```py
    from ongaku.ext import injection


    @arc.with_hook(injection.arc_ensure_player)
    @arc.slash_command("name", "description")
    async def example_command(ctx: arc.GatewayContext, player: ongaku.Player) -> None:
        await player.pause()
    ```

    Parameters
    ----------
    ctx
        The context for the hook.
    """
    if ctx.guild_id is None:
        raise arc.GuildOnlyError

    try:
        client = ctx.get_type_dependency(Client)
    except KeyError as err:
        raise errors.PlayerMissingError from err

    client.get_player(ctx.guild_id)
