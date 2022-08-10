import json
import os

from datetime import datetime
from loguru import logger as log
from pathlib import Path
from naff import Client, listen, Member
from naff.api.events import MessageCreate
from naff.client.errors import HTTPException

log.add(
    "logs/megumin.log",
    backtrace=True,
    enqueue=True,
    diagnose=True,
    rotation="12:00",
    retention="10 days",
)
log.level("DEBUG")

with open(
    f"{Path(__file__).parent.parent.absolute()}/copypastas.json",
    encoding="utf8",
) as f:
    copypastas = json.load(f)


class Megumin(Client):
    """A custom NAFF client stuffed with listeners and custom errors"""

    def __init__(self, *args, **kwargs):
        self.default_prefix = "megu "
        super(Megumin, self).__init__(*args, **kwargs)

    async def on_error(self, source: str, error: Exception, *args, **kwargs) -> None:
        """NAFF on_error override"""
        if isinstance(error, HTTPException):
            errors = error.search_for_message(error.errors)
            out = (
                f"HTTPException: {error.status}|{error.response.reason}: "
                + "\n".join(errors)
            )
            log.error(out, exc_info=error)
        else:
            log.error(f"Ignoring exception in {source}", exc_info=error)

    def start(self, token) -> None:
        """
        Modified NAFF start method with cog detection and loading

        Args:
            token: Your bot's token

        """

        for cog in os.listdir(f"{Path(__file__).parent.parent}/cogs"):
            if cog not in ("__init__.py",) and cog[-3:] == ".py":
                try:
                    self.load_extension(f"cogs.{cog[:-3]}")
                except Exception as e:
                    log.exception(f"Failed to load cog {cog}", exc_info=e)

        super().start(token)

    @listen()
    async def on_ready(self):
        """NAFF on_ready override"""
        log.info(f"Logged in as {self.user}")
        log.info(f"Connected to {len(self.guilds)} guild(s)")
        log.info(
            f"Invite me: https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=8&scope=bot"
        )

    @listen()
    async def on_message_create(self, event: MessageCreate):
        """NAFF on_message_create override"""
        message = event.message

        # Ignore self-messages
        if message.author.id == self.user.id:
            return

        # Copypasta
        for k, v in copypastas.items():
            if k in message.content:
                log.debug(f"Copypasta Detected!: {k}")
                await message.reply(v)

    @listen()
    async def on_member_update(before: Member, after: Member):
        """League mock check"""

        # ignore bots
        if after.bot:
            return

        if after.activities:
            for a in after.activities:
                if a.name.lower() == "league of legends":
                    time_start = a.timestamps.start
                    time_now = datetime.utcnow()
                    duration = time_now - time_start

                    seconds = duration.total_seconds()
                    minutes = divmod(seconds, 60)[0]

                    if minutes == 30:
                        await after.send("Bro you really be playing league that long?")
