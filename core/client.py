import os

from loguru import logger as log
from naff import Client, listen
from naff.client.errors import HTTPException


class Megumin(Client):
    """A custom NAFF client stuffed with listeners and custom errors"""

    def __init__(self, *args, **kwargs):
        super(Megumin, self).__init__(*args, **kwargs)
        self.default_prefix = "megu "
        self.send_command_tracebacks = False

    async def on_error(self, source: str, error: Exception, *args, **kwargs) -> None:
        """NAFF on_error override"""
        if isinstance(error, HTTPException):
            errors = error.search_for_message(error.errors)
            out = f"HTTPException: {error.status}|{error.response.reason}: " + "\n".join(errors)
            log.error(out, exc_info=error)
        else:
            log.opt(exception=True).error(f"Ignoring exception in {source}")

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

        log.success(f"< {len(self.interactions.get(0, []))} > Global Interactions Loaded")
        super().start(token)

    @listen()
    async def on_startup(self) -> None:
        """NAFF on_startup override"""
        log.success(f"Logged in as {self.user}")
        log.success(f"Connected to {len(self.guilds)} guild(s)")
        log.info(
            f"Invite me: https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=8&scope=bot"
        )
