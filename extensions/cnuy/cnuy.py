from pathlib import Path
from typing import no_type_check
from xml.etree import ElementTree

import anyio
from httpx import AsyncClient
from interactions import (
    Buckets,
    Extension,
    GuildText,
    InteractionContext,
    IntervalTrigger,
    Message,
    OptionType,
    Permissions,
    Task,
    check,
    cooldown,
    guild_only,
    listen,
    slash_command,
    slash_option,
)

from necoarc import Necoarc, has_permission

id_file = Path(__file__).parent / "last_id"
url = "https://nitter.privacydev.net/glitchy_sus/rss"

if not id_file.exists():
    open(id_file, "w").close()  # noqa[SIM115]


class Cnuy(Extension):
    """Post cunny that @glitchy_sus rewteets."""

    bot: Necoarc

    async def get_cnuy_channel(self, guild_id: int) -> int | None:
        """Function to get the cunny channel for given guild."""
        async with self.bot.db as db:
            guild = await db.server.find_unique(where={"id": guild_id})
            if not guild:
                await db.server.create({"id": guild_id})
                return None
            return guild.cnuy_channel

    @Task.create(IntervalTrigger(minutes=30))
    async def check_twitter(self) -> None:
        """Task to check if @glitchy_sus retweeted."""
        async with await anyio.open_file(id_file, "r") as r, await anyio.open_file(
            id_file, "w"
        ) as w, AsyncClient() as c:
            self.bot.logger.debug("🐦 Checking Glitchy's twitter")
            last_id = await r.read()
            data = await c.get(url)
            xml = await anyio.to_thread.run_sync(ElementTree.fromstring, data.text)
            new_latest_id = xml.find("channel/item/link").text.split("/")[-1].strip("#m")  # type: ignore[union-attr]

            await w.write(new_latest_id)

            message = "😭 Glitchy just retweeted cunny! 😭\n"

            for i in await anyio.to_thread.run_sync(xml.findall, "channel/item"):
                if "RT by" in i.find("title").text:  # type: ignore[union-attr, operator]
                    link = await anyio.to_thread.run_sync(i.find, "link")
                    new_link = link.text.replace(  # type:ignore[union-attr]
                        "nitter.privacydev.net", "vxtwitter.com"
                    ).strip("#m")

                    if new_link.split("/")[-1] == last_id:
                        return

                    message += f"{new_link}\n"

            for g in self.bot.guilds:
                channel_id = await self.get_cnuy_channel(g.id)

                if channel_id:
                    self.bot.logger.debug("📩 Sending cunny to server")
                    await self.bot.get_channel(channel_id).send(message)  # type:ignore[union-attr]

    @listen()
    async def on_startup(self) -> None:
        """Even triggered on startup."""
        self.check_twitter.start()

    @slash_command("set_cnuy_channel", description="Set the cunny posting channel for the server")
    @slash_option("channel", description="Name of the channel to set", opt_type=OptionType.CHANNEL, required=True)
    @check(guild_only())
    @check(has_permission(Permissions.MANAGE_CHANNELS))
    @no_type_check
    async def command_set_cnuy_channel(self, ctx: InteractionContext, channel: GuildText) -> Message:
        """Set a cunny channel."""
        if not isinstance(channel, GuildText):
            return await ctx.send("💥 Error! Only guild text channels allowed.", ephemeral=True)

        async with self.bot.db as db:
            await db.server.upsert(
                where={"id": ctx.guild.id},
                data={
                    "create": {"id": ctx.guild.id, "confess_channel": channel.id},
                    "update": {"confess_channel": channel.id},
                },
            )
            self.bot.logger.debug(f"Successfully set confession channel for {ctx.guild.id}")

        return await ctx.send(f"😭 Successfully set {channel.name} as the cunny channel.", ephemeral=True)

    @slash_command("remove_cnuy_channel", description="Remove the cunny posting channel")
    @check(guild_only())
    @check(has_permission(Permissions.MANAGE_CHANNELS))
    @no_type_check
    async def command_remove_cnuy_channel(self, ctx: InteractionContext) -> Message:
        """Remove the cunny channel."""
        async with self.bot.db as db:
            guild = await db.server.find_unique(where={"id": ctx.guild.id})
            if not guild:
                return await ctx.send("💥 Theres no cnuy channel for this server.", ephemeral=True)
            await db.server.update(data={"cnuy_channel": 0}, where={"id": ctx.guild.id})
        return await ctx.send("✅ Successfully removed cnuy channel.", ephemeral=True)

    @slash_command("check_twitter", description="Manually check glitchy's twitter")
    @check(guild_only())
    @cooldown(Buckets.GUILD, 1, 3600)
    @no_type_check
    async def command_manual_twitter(self, ctx: InteractionContext) -> None:
        """Manually check glitchy's twitter."""
        await ctx.send("🐦 Checking twitter...", ephemeral=True)
        await self.check_twitter()
        self.check_twitter.restart()
        await ctx.send("✅ Done checking!", ephemeral=True)
