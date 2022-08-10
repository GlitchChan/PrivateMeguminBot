from naff import Context, Permissions


def has_permission(*permissions: Permissions):
    """Wrapper around the has_permissions method to work with checks"""

    async def check(ctx: Context):
        result = ctx.author.has_permission(*permissions)
        return result

    return check
