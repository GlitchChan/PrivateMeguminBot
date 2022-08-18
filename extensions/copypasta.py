import json
from pathlib import Path

from loguru import logger as log
from naff import (
    AutocompleteContext,
    Buckets,
    Extension,
    InteractionContext,
    OptionTypes,
    cooldown,
    listen,
    slash_command,
    slash_option,
)
from naff.api.events import MessageCreate

from core import Megumin

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

        # Copypasta
        for k, v in copypastas.items():
            if k in message.content.lower():
                log.debug(f"Copypasta Detected!: {k}")
                await message.reply(v)

    @slash_command("send_copypasta", description="Send a copypasta")
    @slash_option(
        "copypasta",
        "Copypasta to send",
        OptionTypes.STRING,
        required=True,
        autocomplete=True,
    )
    @cooldown(Buckets.USER, 1, 60)
    async def copypasta_command(self, ctx: InteractionContext, copypasta: str):
        for k, v in copypastas.items():
            if k == copypasta:
                return ctx.send(v)

    @copypasta_command.autocomplete("copypasta")
    async def copypasta_command_autocomplete(self, ctx: AutocompleteContext, copypasta: str):
        choices = []
        for k, v in copypastas.items():
            if copypasta.lower() in k:
                choices.append({"name": k, "value": k})

        await ctx.send(choices=choices)


def setup(client):
    Copypasta(client)
