from typing import Any

from loguru import logger as log
from prisma import Prisma
from prisma.errors import PrismaError

prisma = Prisma(auto_register=True)


# ======================================
#              🔥Sexboard🔥
# ======================================


async def update_user_sex_count(user_id: int) -> None:
    """Update a users sex message counter.

    Arguments:
        user_id: The id of the user
    Returns:
        None
    """
    async with prisma as db:
        await db.user.upsert(
            where={"id": user_id}, data={"create": {"id": user_id}, "update": {"sex_count": {"increment": 1}}}
        )
        log.debug(f"⬆️ Successfully updated {user_id} sex_count")


async def get_sex_leaderboard() -> list[Any] | None:
    """Get the top 10 of the sex message leaderboard.

    Returns:
        List of Users
    """
    try:
        async with prisma as db:
            return await db.user.find_many(take=10, order={"sex_count": "desc"})
    except PrismaError:
        return None


async def set_user_sex_count(user_id: int, sex_count: int) -> None:
    """Set a users sex message counter.

    Args:
        user_id: The id of the user
        sex_count: The number to set for the counter
    Returns:
        None
    """
    async with prisma as db:
        await db.user.upsert(
            where={"id": user_id},
            data={"create": {"id": user_id, "sex_count": sex_count}, "update": {"sex_count": sex_count}},
        )
        log.debug(f"📝 Successfully updated {user_id} sex_count")


# ======================================
#           🤫Confessions🤫
# ======================================


async def set_confession_channel(guild_id: int, channel_id: int) -> None:
    """Function to set/update the confession channel for a given guild.

    Args:
        guild_id: ID of the guild
        channel_id: ID of the channel being set/updated
    Returns:
        None
    """
    async with prisma as db:
        await db.server.upsert(
            where={"id": guild_id},
            data={
                "create": {"id": guild_id, "confess_channel": channel_id},
                "update": {"confess_channel": channel_id},
            },
        )
        log.debug(f"Successfully set confession channel for {guild_id}")


async def get_confession_channel(guild_id: int) -> int | None:
    """Function to get the confession channel for a given guild.

    Args:
        guild_id: ID of the guild
    Returns:
        ID of the confession channel or None
    """
    async with prisma as db:
        guild = await db.server.find_unique(where={"id": guild_id})
        if not guild:
            await db.server.create({"id": guild_id})
            return None
        return guild.confess_channel


# ======================================
#             😭Cunny Share😭
# ======================================
async def get_cnuy_channel(guild_id: int) -> int | None:
    """Function to get the cunny channel for given guild."""
    async with prisma as db:
        guild = await db.server.find_unique(where={"id": guild_id})
        if not guild:
            await db.server.create({"id": guild_id})
            return None
        return guild.cnuy_channel


async def set_cnuy_channel(guild_id: int, channel_id: int) -> None:
    """Function to set/update the confession channel for a given guild.

    Args:
        guild_id: ID of the guild
        channel_id: ID of the channel being set/updated
    Returns:
        None
    """
    async with prisma as db:
        await db.server.upsert(
            where={"id": guild_id},
            data={
                "create": {"id": guild_id, "cnuy_channel": channel_id},
                "update": {"cnuy_channel": channel_id},
            },
        )
        log.debug(f"Successfully set cnuy channel for {guild_id}")


# # ======================================
# #             👁️The Logger👁️
# # ======================================
#
#
# async def get_log_channel(guild_id: int) -> int | None:
#     """Fetch the logger channel ID.
#
#     Args:
#         guild_id: ID of the guild
#
#     Returns:
#         ID of the logger channel or None
#     """
#     async with prisma as db:
#         guild = await db.server.find_unique(where={"id": guild_id})
#         if not guild:
#             await db.server.create({"id": guild_id})
#         return guild.logging_channel
