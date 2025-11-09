from __future__ import annotations

from unittest import mock

import arc as arc_lib
import hikari
import pytest

from ongaku import client
from ongaku import errors
from ongaku.ext.injection import arc


@pytest.mark.asyncio
async def test_arc_ensure_player():
    context = mock.Mock(guild_id=hikari.Snowflake(123))

    await arc.arc_ensure_player(context)

    context.get_type_dependency.assert_called_once_with(client.Client)


@pytest.mark.asyncio
async def test_arc_ensure_player_with_missing_guild_id():
    context = mock.Mock(guild_id=None)

    with pytest.raises(arc_lib.GuildOnlyError):
        await arc.arc_ensure_player(context)

    context.get_type_dependency.assert_not_called()


@pytest.mark.asyncio
async def test_arc_ensure_player_with_missing_player():
    context = mock.Mock(
        guild_id=hikari.Snowflake(123),
        get_type_dependency=mock.Mock(side_effect=KeyError),
    )

    with pytest.raises(errors.PlayerMissingError):
        await arc.arc_ensure_player(context)

    context.get_type_dependency.assert_called_once_with(client.Client)
