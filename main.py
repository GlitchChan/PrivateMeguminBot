import os
import sys
from distutils.util import strtobool
from pathlib import Path

import interactions as ipy
from dotenv import load_dotenv

from core import init_logger

# Load enviroment
load_dotenv()
dev_mode = strtobool(os.getenv("NECOARC_DEV", "False"))
log = init_logger("necoarc", bool(dev_mode))
ext_path = Path(__file__).parent / "extensions"


# Startup logging
@ipy.listen(ipy.events.Startup)
async def _startup(event: ipy.events.Startup) -> None:
    invite_link = "https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot"

    event.bot.logger.info(f"🏰 Connected to {len(event.bot.guilds)} guilds!")
    event.bot.logger.info(f"🎁 Invite me: [link={invite_link}]Click me![/link]")


# Main function
def main() -> None:
    """The main function that loads extensions and runs the bot."""
    token = os.getenv("DISCORD_DEV_TOKEN", None) if dev_mode else os.getenv("DISCORD_TOKEN", None)

    if not token:
        log.critical("[bold red]🛑 Discord token not found!")
        sys.exit(1)

    bot = ipy.Client(
        token=token,
        debug_scope=os.getenv("DISCORD_DEV_GUILD") if dev_mode else ipy.MISSING,  # type: ignore[arg-type]
        logger=log,
        send_command_tracebacks=False,
        intents=ipy.Intents.ALL,
    )

    if dev_mode:
        bot.logger.debug("[bold yellow]🔁 Enabling Jurigged")
        bot.load_extension("interactions.ext.jurigged")

    for e in ext_path.glob("*"):
        if not e.name.startswith("__"):
            bot.logger.debug(f"📦 Attempting to load {e.name}...")
            try:
                bot.load_extension(f"extensions.{e.name}")
                bot.logger.info(f"[green]✅ Successfully loaded[/green] {e.name}!")
            except ipy.errors.ExtensionLoadException:
                bot.logger.warning(f"[yellow]⚠️ Failed to load[/yellow] {e.name}!!!")

    bot.logger.info(f"🚀 Loaded < {len(bot.ext)} > extensions!")
    bot.start()


if __name__ == "__main__":
    main()
