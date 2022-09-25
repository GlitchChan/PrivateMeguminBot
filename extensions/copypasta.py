import json
import re
from pathlib import Path

from loguru import logger as log
from naff import DMChannel, Extension, listen
from naff.api.events import MessageCreate

from core import Megumin, update_user_sex_count

with open(
    f"{Path(__file__).parent.parent.absolute()}/copypastas.json",
    encoding="utf8",
) as f:
    copypastas = json.load(f)


class Copypasta(Extension):
    bot: Megumin

    @listen()
    async def on_message_create(self, event: MessageCreate):
        message = event.message

        # Ingore self and bot message:
        if message.author.bot:
            return

        if re.search(r"se(x|gg?s)", message.content, re.IGNORECASE):
            if isinstance(message.channel, DMChannel):
                log.debug("Ignoring DM Sex Message")
                return
            log.debug("Detected Sex")
            await update_user_sex_count(message.author.id)

        # Copypasta
        for k, v in copypastas.items():
            if re.search(k, message.content, re.IGNORECASE):
                log.debug(f"Copypasta Detected: {k} | {v}")
                await message.reply(v)


def setup(client):
    Copypasta(client)
