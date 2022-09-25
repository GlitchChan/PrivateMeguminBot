from typing import Union

from loguru import logger as log
from prisma import Prisma

prisma = Prisma(auto_register=True)


# Confession Channel Database Functions
async def set_confession_channel(guild_id: int, channel_id: int) -> None:
    """Function to set/update the confession channel for a given guild

    :param guild_id: The id of the guild
    :param channel_id: The id of the channel being set/updated
    :return: None
    """
    async with prisma as db:
        await db.server.upsert(
            where={"id": guild_id},
            data={"create": {"id": guild_id, "confess_channel": channel_id}, "update": {"confess_channel": channel_id}},
        )
        log.debug(f"Successfully set confession channel for {guild_id}")


async def get_confession_channel(guild_id: int) -> Union[int, None]:
    """Function to get the confession channel for a given guild

    :param guild_id: The id of the guild
    :return: Confession channel ID or None if not set
    """
    async with prisma as db:
        try:
            guild = await db.server.find_unique(where={"id": guild_id})

            return guild.confess_channel
        except AttributeError:
            log.warning(f"Guild {guild_id} has not set a confession channel")
            return None


# Sex Message Leaderboard Functions
async def update_user_sex_count(user_id: int) -> None:
    """Function to update a users sex message counter

    :param user_id: The id of the user
    :return: None
    """
    async with prisma as db:
        await db.user.upsert(
            where={"id": user_id}, data={"create": {"id": user_id}, "update": {"sex_count": {"increment": 1}}}
        )
        log.debug(f"Successfully updated {user_id} sex_count")


async def set_user_sex_count(user_id: int, sex_count: int) -> None:
    """Function to set a users sex message counter

    :param user_id: The id of the user
    :param sex_count: The number to set for the counter
    :return: None
    """
    async with prisma as db:
        await db.user.upsert(
            where={"id": user_id},
            data={"create": {"id": user_id, "sex_count": sex_count}, "update": {"sex_count": sex_count}},
        )
        log.debug(f"Successfully updated {user_id} sex_count")


async def get_sex_leaderboard() -> list:
    """Function to get the top 10 of the sex message leaderboard

    :return: List of Users
    """
    async with prisma as db:
        leaderboard = await db.user.find_many(take=10, order={"sex_count": "desc"})
        return leaderboard
