import os
from distutils.util import strtobool

from dotenv import load_dotenv
from naff import Intents

from core import Megumin, jlogger, log

if __name__ == "__main__":

    # Load environment vars
    load_dotenv()
    log.level("DEBUG" if strtobool(os.getenv("DEBUG")) else "INFO")

    if strtobool(os.getenv("DEBUG")):
        import jurigged

        jurigged.watch(logger=jlogger)

    # Create bot instance
    bot = Megumin(intents=Intents.ALL, auto_defer=True)

    # Start the bot
    bot.start(os.getenv("DEV_DISCORD_TOKEN") if strtobool(os.getenv("DEBUG")) else os.getenv("DISCORD_TOKEN"))
