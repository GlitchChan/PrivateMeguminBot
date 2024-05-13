import typing

import interactions as ipy

from necoarc.config import CONFIG
from necoarc.const import ROOT
from necoarc.db import Server, User, pw_db, rd_db

__all__ = ("NecoArc",)

if typing.TYPE_CHECKING:
    from loguru import Logger


class NecoArc(ipy.Client):
    """Pre-configured interactions client."""
    logger: "Logger"  # type: ignore[assignment]

    def __init__(self) -> None:  # noqa: D107
        self.__custom_init__()
        super().__init__()

    def __custom_init__(self) -> None:
        """Custom __init__ method."""
        with pw_db:
            pw_db.create_tables({Server, User})

        self.logger = LOGGER
        self.send_command_tracebacks = False
        self.fetch_members = True
        self.debug_scope = CONFIG.dev_guild or ipy.MISSING
        self.intents = ipy.Intents.new(
            guilds=True,
            guild_messages=True,
            direct_messages=True,
            message_content=True,
        )

    def start(self, token: str | None = None) -> None:
        """Custom start method."""
        for ext in ROOT.joinpath("extensions").iterdir():
            _ext = ext.relative_to(ROOT.parent).as_posix().replace("/", ".").removesuffix(".py")
            self.load_extension(_ext)
        super().start(token)

    async def stop(self) -> None:
        """Custom stop method to close rocksdict."""
        rd_db.close()
        await super().stop()
