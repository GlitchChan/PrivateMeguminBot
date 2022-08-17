import json
import os
from datetime import datetime
from pathlib import Path

from loguru import logger as log
from naff import Client, Member, listen
from naff.api.events import MessageCreate
from naff.client.errors import HTTPException


class Megumin(Client):
    """A custom NAFF client stuffed with listeners and custom errors"""

    def __init__(self, *args, **kwargs):
        super(Megumin, self).__init__(*args, **kwargs)
        self.default_prefix = "megu "

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
        log.info("Initializing Extensions...")

        # https://github.com/NAFTeam/Bot-Template/blob/main/%7B%7B%20cookiecutter.project_slug%20%7D%7D/core/extensions_loader.py#L13-L21
        for root, dirs, files in os.walk("extensions"):
            for file in files:
                if file.endswith(".py") and not file.startswith("__init__"):
                    file = file.removesuffix(".py")
                    path = os.path.join(root, file)
                    python_import_path = path.replace(
                        "/",
                        ".",
                    ).replace("\\", ".")

                    self.load_extension(python_import_path)

        log.success(
            f"< {len(self.interactions.get(0, []))} > Global Interactions Loaded"
        )
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
