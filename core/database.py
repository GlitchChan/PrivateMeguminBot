from pathlib import Path

from loguru import logger as log
from sqlitedict import SqliteDict

db_file = f"{Path(__file__).parent.parent.absolute()}/cache.sqlite3"


def set_confess_channel(guild_id: int, channel_id: int) -> None:
    """Function to set the confession channel for a given guild

    :param guild_id: The id of the guild
    :param channel_id: The id of the channel being set
    :return: None
    """
    with SqliteDict(db_file, outer_stack=False, autocommit=True) as db:
        try:
            db[guild_id] = {"confess channel": channel_id}
            log.debug(f"Successfully set confession channel for {guild_id}")
        except Exception:
            log.opt(exception=True).exception("An error occurred when trying to set guild confess channel")


def get_confess_channel(guild_id: int) -> int:
    """Function to fetch the confession channel for a given guild

    :param guild_id: The id of the guild
    :return: The channels id
    """
    with SqliteDict(db_file, outer_stack=False) as db:
        try:
            confess_channel = db[guild_id]["confess channel"]
            return confess_channel
        except KeyError:
            KeyError("Guild has not set a confession channel")
