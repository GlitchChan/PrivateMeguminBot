import re
from typing import no_type_check

import anyio
import httpx
import tomlkit
from interactions import (
    Attachment,
    Buckets,
    Extension,
    File,
    InteractionContext,
    Message,
    OptionType,
    User,
    check,
    cooldown,
    is_owner,
    listen,
    slash_command,
    slash_option,
)
from interactions.api.events import MessageCreate
from loguru import logger as log

from necoarc import is_trusted

from .config.settings import add_custom_pasta, pastas, remove_copypata, update_custom_pasta
from .utils import validate_copypasta


class Copypasta(Extension):
    """Extension for copypasta related things."""

    @listen()
    async def _message(self, event: MessageCreate) -> None:
        m = event.message

        # Ingore self and bot message:
        if m.author.bot:
            return

        # Copypasta
        for pasta in pastas:
            if await anyio.to_thread.run_sync(re.search, pasta.re, m.content):
                log.debug(f"🍝 Detected pasta: {pasta.name}")
                file = (
                    File(anyio.Path(__file__).parent / f"assets/{pasta.file}")  # type: ignore[arg-type]
                    if pasta.file
                    else None
                )
                if pasta.text or pasta.file:
                    await m.reply(pasta.text if pasta.text else None, file=file)  # type:ignore[arg-type]
                if pasta.emoji:
                    await m.add_reaction(pasta.emoji)

    @slash_command("add_copypasta", description="Used to add custom copypastas")
    @slash_option("name", description="Name of the copypasta", opt_type=OptionType.STRING, required=True)
    @slash_option("regex", description="The regex to detect the copypasta", opt_type=OptionType.STRING, required=True)
    @slash_option("text", description="Text reaction to copypasta", opt_type=OptionType.STRING)
    @slash_option("emoji", description="Emoji reaction to copypasta", opt_type=OptionType.STRING)
    @slash_option("file", description="Attachment reaction to copypasta", opt_type=OptionType.ATTACHMENT)
    @cooldown(Buckets.GUILD, 1, 3)
    @check(is_trusted())
    async def command_add_copypasta(
        self,
        ctx: InteractionContext,
        name: str,
        regex: str,
        text: str | None = None,
        emoji: str | None = None,
        file: Attachment | None = None,
    ) -> Message | None:
        """Command to add copypastas."""
        # Check if at least one optional argument was past
        if text and emoji and file is None:
            return await ctx.send("⚠️ At least one optional argument must be past!", ephemeral=True)

        # Validate copypasta
        if not await validate_copypasta(ctx, name, regex, emoji):
            return None

        # Download the file if one was given
        if file:
            try:
                async with httpx.AsyncClient() as c:
                    res = await c.get(file.url)
                    res.raise_for_status()

                    file_ext = res.headers["content-type"].split("/")[-1]
                    asset_dir = anyio.Path(__file__).parent / "assets"

                    async with await anyio.open_file(f"{asset_dir}/{name}.{file_ext}", "wb") as f:
                        await f.write(res.content)

                        file = f"{name}.{file_ext}"  # type: ignore[assignment]
            except (OSError, httpx.HTTPError) as e:
                return await ctx.send(f"💥 Error! Failed to get attachemnt with error: {e}", ephemeral=True)

        await add_custom_pasta(name, regex, text, emoji, file)  # type: ignore[arg-type]
        return await ctx.send(f"🍝 Successfully created {name} copypasta!", ephemeral=True)

    @slash_command("remove_copypasta", description="Used to add custom copypastas")
    @slash_option("name", description="Name of the copypasta", opt_type=OptionType.STRING, required=True)
    @cooldown(Buckets.GUILD, 1, 3)
    @check(is_trusted())
    async def command_remove_copypasta(self, ctx: InteractionContext, name: str) -> Message:
        """Command to remove a copypasta."""
        names = [c.name for c in pastas]

        if name not in names:
            return await ctx.send("💥 Error! Invalid name, no copypasta exists with this name!", ephemeral=True)

        await remove_copypata(name)
        return await ctx.send(f"🗑️ Successfully removed {name}", ephemeral=True)

    @slash_command("edit_copypasta", description="Used to edit custom copypastas")
    @slash_option("name", description="Name of the copypasta", opt_type=OptionType.STRING, required=True)
    @slash_option("edited_name", description="Edited name of the copypasta", opt_type=OptionType.STRING)
    @slash_option("edited_regex", description="Edited regex to detect the copypasta", opt_type=OptionType.STRING)
    @slash_option("edited_text", description="Edited text reaction to copypasta", opt_type=OptionType.STRING)
    @slash_option("edited_emoji", description="Edited emoji reaction to copypasta", opt_type=OptionType.STRING)
    @slash_option("edited_file", description="Edited attachment reaction to copypasta", opt_type=OptionType.ATTACHMENT)
    @slash_option("remove_file", description="Remove the attachment reaction to copypasta", opt_type=OptionType.BOOLEAN)
    @check(is_trusted())
    async def command_edit_copypasta(
        self,
        ctx: InteractionContext,
        name: str,
        edited_name: str | None = None,
        edited_regex: str | None = None,
        edited_text: str | None = None,
        edited_emoji: str | None = None,
        edited_file: Attachment | None = None,
        remove_file: bool | None = None,
    ) -> Message | None:
        """Command to edit a copypasta."""
        # Check if at least one optional argument was past
        if edited_name and edited_regex and edited_text and edited_emoji and edited_file and remove_file is None:
            return await ctx.send("⚠️ At least one optional argument must be past!", ephemeral=True)

        # Validate copypasta
        if not await validate_copypasta(ctx, edited_name, edited_regex, edited_emoji, edited_name):
            return None

        # Download the file if one was given
        if edited_file:
            try:
                async with httpx.AsyncClient() as c:
                    res = await c.get(edited_file.proxy_url)
                    log.debug(f"📩 Downloading: {edited_file.filename}")
                    res.raise_for_status()

                    file_ext = res.headers["content-type"].split("/")[-1]
                    asset_dir = anyio.Path(__file__).parent / "assets"
                    file_name = edited_name if edited_name else name

                    async with await anyio.open_file(f"{asset_dir}/{file_name}.{file_ext}", "wb") as f:
                        await f.write(res.content)

                    await update_custom_pasta(
                        name, edited_name, edited_regex, edited_text, edited_emoji, f"{file_name}.{file_ext}"
                    )
                    return await ctx.send(f"🍝 Successfully edited copyasta {name}", ephemeral=True)

            except (OSError, httpx.HTTPError) as e:
                return await ctx.send(f"💥 Error! Failed to get attachemnt with error: {e}", ephemeral=True)

        await update_custom_pasta(
            name,
            edited_name,
            edited_regex,
            edited_text,
            edited_emoji,
            r_file=remove_file,
        )
        return await ctx.send(f"🍝 Successfully edited copyasta {name}", ephemeral=True)

    @slash_command("add_trusted_user", description="Adds a trusted user")
    @slash_option("user", description="User to trust", opt_type=OptionType.USER)
    @check(is_owner())
    @no_type_check
    async def command_add_trusted_user(self, ctx: InteractionContext, user: User) -> Message:
        """Adds a trusted user."""
        if user.id in ctx.bot.owner_ids:
            return await ctx.send("💥Error! You're already trusted dummy!")

        _secrets = anyio.Path(__file__).parent.parent.parent / ".secrets.toml"
        toml = await anyio.to_thread.run_sync(tomlkit.parse, await _secrets.read_text("utf-8"))
        await anyio.to_thread.run_sync(toml["necoarc"]["trusted"].append, user.id)

        async with _secrets.open("w", encoding="utf-8") as t:
            await anyio.to_thread.run_sync(tomlkit.dump, toml, t)
            return await ctx.send(f"📝 Successfully added {user.username} to trusted users", ephemeral=True)
