from pathlib import Path

from loguru import logger as log
from sqlitedict import SqliteDict

db_file = f"{Path(__file__).parent.parent.absolute()}/cache.sqlite3"

confession = SqliteDict(db_file, tablename="Confession", autocommit=True)
sex = SqliteDict(db_file, tablename="Sex", autocommit=True)


def set_confess_channel(guild_id: int, channel_id: int) -> None:
    """Function to set the confession channel for a given guild

    :param guild_id: The id of the guild
    :param channel_id: The id of the channel being set
    :return: None
    """
    with confession as db:
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
    with confession as db:
        try:
            confess_channel = db[guild_id]["confess channel"]
            return confess_channel
        except KeyError:
            KeyError("Guild has not set a confession channel")


def update_sex_leaderboard(author_id: int) -> None:
    """Function to update the sex leaderboard

    :param author_id: The id of the sex messanger
    :return: None
    """
    with sex as db:
        try:
            try:
                sex_count = db[author_id]["sex_count"]
            except KeyError:
                sex_count = 1
            log.debug(f"Sex count for {author_id} is {sex_count}")
            db[author_id] = {"sex_count": sex_count + 1}
        except KeyError:
            KeyError("Something happened")


def set_sex_number(author_id: int, sex_count: int) -> None:
    """Sets a users sex counter

    :param author_id: The id of the sex messanger
    :param sex_count: The amount of sex messages that will be set
    :return: None
    """
    with sex as db:
        try:
            db[author_id] = {"sex_count": int(sex_count)}
        except KeyError:
            KeyError("Something happened")


def get_sex_leaderboard() -> dict:
    """Gets the leaderboard for sex messages

    :return: Dict of leaderboard
    """

    leaderboard = {}

    with sex as db:
        try:
            for k, v in db.items():
                leaderboard[k] = v["sex_count"]
        except KeyError:
            KeyError("Something happened")

    log.debug(leaderboard)
    return leaderboard
