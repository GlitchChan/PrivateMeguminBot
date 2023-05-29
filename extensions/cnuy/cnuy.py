from pathlib import Path
from typing import no_type_check
from xml.etree import ElementTree

import aiofiles as aio
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

from necoarc import get_cnuy_channel, has_permission, set_cnuy_channel

id_file = Path(__file__).parent / "last_id"
url = "https://nitter.privacydev.net/glitchy_sus/rss"


class Cnuy(Extension):
    """Post cunny that @glitchy_sus rewteets."""

    @Task.create(IntervalTrigger(minutes=5))
    async def check_twitter(self) -> None:
        """Task to check if @glitchy_sus retweeted."""
        async with aio.open(id_file, "r+") as r, aio.open(id_file, "r+") as w, AsyncClient() as c:
            self.bot.logger.debug("🐦 Checking Glitchy's twitter")
            last_id = await r.read()
            data = await c.get(url)
            xml = ElementTree.fromstring(data.text)  # noqa[S314]
            new_latest_id = xml.find("channel/item/link").text.split("/")[-1].strip("#m")  # type: ignore[union-attr]

            await w.write(new_latest_id)

            for g in self.bot.guilds:
                channel_id = await get_cnuy_channel(g.id)
                if channel_id:
                    self.bot.logger.debug("✅ Found cunny channel")
                    for i in xml.findall("channel/item"):
                        if "RT by" in i.find("title").text:  # type: ignore[union-attr, operator]
                            link = (
                                i.find("link")
                                .text.strip("#m")  # type: ignore[union-attr]
                                .replace("nitter.privacydev.net", "fxtwitter.com")
                            )

                            if link.split("/")[-1] == last_id:
                                return

                            self.bot.logger.debug("📩 Sending cunny to server")
                            await self.bot.get_channel(channel_id).send(f"😭 Glitchy just retweeted cunny! 😭\n {link}")

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

        await set_cnuy_channel(ctx.guild_id, channel.id)
        return await ctx.send(f"😭 Successfully set {channel.name} as the cunny channel.", ephemeral=True)

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
