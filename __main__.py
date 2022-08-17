import os

from dotenv import load_dotenv
from loguru import logger as log
from naff import Intents

from core import Megumin

if __name__ == "__main__":

    # Load environment vars
    load_dotenv()

    # Init Logging
    log.add(
        "logs/megumin.log",
        backtrace=True,
        enqueue=True,
        diagnose=True,
        rotation="12:00",
        retention="10 days",
    )
    if os.getenv("DEBUG"):
        log.level("DEBUG")

    # Create bot instance
    bot = Megumin(intents=Intents.ALL, auto_defer=True)

    bot.start(os.getenv("DISCORD_TOKEN"))
