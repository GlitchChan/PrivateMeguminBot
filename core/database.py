from pathlib import Path

from loguru import logger as log
from sqlitedict import SqliteDict

db_file = f"{Path(__file__).parent.parent.absolute()}/cache.sqlite3"


@log.catch()
def set_confess_channel(guild_id: int, channel_id: int) -> None:
    """Function to set the confession channel for a given guild

    :param guild_id: The id of the guild
    :param channel_id: The id of the channel being set
    :return: None
    """
    with SqliteDict(db_file, outer_stack=False, autocommit=True) as db:
        db[guild_id] = {"confess channel": channel_id}
        log.success(f"Successfully set confession channel for {guild_id}")


@log.catch()
def get_confess_channel(guild_id: int) -> int:
    """Function to fetch the confession channel for a given guild

    :param guild_id: The id of the guild
    :return: The channels id
    """
    with SqliteDict(db_file, outer_stack=False) as db:
        confess_channel = db[guild_id]["confess channel"]
        return confess_channel
