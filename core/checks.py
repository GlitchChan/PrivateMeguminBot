from collections.abc import Awaitable, Callable

import anyio
from interactions import Permissions
from interactions.models.internal.context import BaseContext

TYPE_CHECK_FUNCTION = Callable[[BaseContext], Awaitable[bool]]


def has_permission(*permissions: Permissions) -> TYPE_CHECK_FUNCTION:
    """Wrapper around the has_permissions method to work with checks."""

    async def _check(ctx: BaseContext) -> bool:
        return ctx.author.has_permission(*permissions)  # type: ignore[union-attr]

    return _check


def is_trusted() -> TYPE_CHECK_FUNCTION:
    """Check if a user is trusted."""

    async def _check(ctx: BaseContext) -> bool:
        file = anyio.Path(__file__).parent / "trusted_users"
        data = await file.read_text()

        users = await anyio.to_thread.run_sync(data.split, ",")
        return str(ctx.author.id) in users or ctx.author.id in ctx.bot.owner_ids

    return _check
