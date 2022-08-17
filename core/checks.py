from naff import Context
from naff import Permissions


def has_permission(*permissions: Permissions):
    """Wrapper around the has_permissions method to work with checks"""

    async def check(ctx: Context):
        return ctx.author.has_permission(*permissions)

    return check
