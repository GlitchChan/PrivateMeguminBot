import sys
from argparse import ArgumentParser
from pathlib import Path

import tomlkit
from interactions import Client, Intents, listen
from interactions.client.errors import ExtensionLoadException
from loguru import logger as log

# Setup Interactions bot
bot = Client(intents=Intents.ALL, auto_defer=True, send_command_tracebacks=False)

# Setup argparse
parser = ArgumentParser(prog="Neco Arc", description="Private Discord bot for friends.")
parser.add_argument("-d", "--dev", action="store_true")
parser.add_argument("-v", "--verbose", action="store_true")

secret_file = Path(__file__).parent / ".secrets.toml"
_secrets = tomlkit.parse(secret_file.read_text("utf-8"))
base_token = _secrets["discord"]["token"]  # type:ignore[index]
dev_token = _secrets["discord"]["dev_token"]  # type:ignore[index]


def init_loggers(verbose: bool | None = None) -> None:
    """Custom function to initialize loguru as the default logger.

    Args:
        verbose: More logs
    Returns:
        None
    """
    log.remove()
    log.add(
        Path(__file__).parent / "logs/necoarc.log",
        backtrace=True,
        enqueue=True,
        diagnose=True,
        rotation="12:00",
        retention="10 days",
    )
    log.add(sys.stdout, level="DEBUG" if verbose else "INFO", enqueue=True)


@listen()
async def on_startup() -> None:
    """Even triggered on startup."""
    guilds = len(bot.guilds)
    username = f"{bot.user.display_name}#{bot.user.discriminator}"
    bot.log.info(f"🌐 Logged into: {username}")
    bot.log.info(f"🔌 Connected to: {guilds} Guild{'s' if guilds > 1 else ''}")
    bot.log.info(
        f"🔗 Invite link: https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot"
    )
    bot.log.debug("⚙️ Developer mode is active, this is a reminder!")


@log.catch(message="🚨 An unexpected error occurred! 🚨")
def run() -> None:
    """Main function to start the bot."""
    args = parser.parse_args()
    token = base_token if not args.dev else dev_token  # Fetch discord token

    # Setup custom loggers
    init_loggers(args.verbose)
    bot.logger = bot.log = log  # type:ignore[assignment]  # Set custom logger into bot

    # Load jurigged if devmode
    if args.dev:
        from interactions.ext.jurigged import setup

        bot.log.debug("🔥 Enabled hot reload extension")
        setup(bot)

    # Load all bot extensions
    ext_path = Path(__file__).parent / "extensions"

    for d in ext_path.iterdir():
        if d.name.startswith("__"):
            continue

        import_path = d.relative_to(Path(__file__).parent).as_posix().replace(r"\\", ".").replace("/", ".")
        try:
            bot.load_extension(import_path)
            bot.log.debug(f"✅ Loaded Extension: {d.name}")
        except ExtensionLoadException:
            bot.log.warning(f"⚠️ Failed loading Extension: {d.name}")
            continue

    bot.log.success(f"📦 < {len(bot.ext)} > Extensions Loaded!")
    bot.start(token)  # type:ignore[arg-type]


if __name__ == "__main__":
    run()
