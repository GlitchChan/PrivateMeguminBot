from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import no_type_check

import tomlkit
from interactions import Permissions
from interactions.models.internal.context import BaseContext

TYPE_CHECK_FUNCTION = Callable[[BaseContext], Awaitable[bool]]


@no_type_check
def has_permission(*permissions: Permissions) -> TYPE_CHECK_FUNCTION:
    """Wrapper around the has_permissions method to work with checks."""

    async def _check(ctx: BaseContext) -> bool:
        return ctx.author.has_permission(*permissions)

    return _check


@no_type_check
def is_trusted() -> TYPE_CHECK_FUNCTION:
    """Check if a user is trusted."""

    async def _check(ctx: BaseContext) -> bool:
        _secrets = Path(__file__).parent.parent / ".secrets.toml"
        toml = tomlkit.parse(_secrets.read_text("utf-8"))
        trusted = toml["necoarc"]["trusted"]
        return ctx.author.id in trusted or ctx.author.id in ctx.bot.owner_ids

    return _check
