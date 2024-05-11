from typing import no_type_check

import anyio
from httpx import AsyncClient, Headers
from interactions import (
    Buckets,
    ChannelType,
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
from parsel import Selector
from prisma.types import ServerCreateInput

from v1.core import DB, has_permission

ID_FILE = anyio.Path(__file__).parent / "last_id"
URL = "https://tweet.whateveritworks.org/glitchy_sus/rss"
HEADERS = Headers({"User-Agent": "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0"})
NITTER = "tweet.whateveritworks.org"
TWITFIX = "vxtwitter.com"


class Cnuy(Extension):
    """Post cunny that @glitchy_sus rewteets."""

    async def get_cnuy_channel(self, guild_id: int) -> int | None:
        """Function to get the cunny channel for given guild."""
        async with DB as db:
            guild = await db.server.find_unique(where={"id": guild_id})
            if not guild:
                await db.server.create(ServerCreateInput(id=guild_id))
                return None
            return guild.cnuy_channel

    @Task.create(IntervalTrigger(minutes=30))
    async def check_twitter(self) -> None:
        """Task to check if @glitchy_sus retweeted."""
        if not await ID_FILE.exists():
            self.bot.logger.debug(f"ID file doesn't exist at {ID_FILE}, creating.")
            await ID_FILE.write_text("")

        async with AsyncClient(headers=HEADERS) as c:
            self.bot.logger.debug("🐦 Checking Glitchy's twitter")
            data = await c.get(URL)
            xml = Selector(data.text, type="xml")

            last_id = await ID_FILE.read_text()
            new_last_id = await anyio.to_thread.run_sync(xml.xpath, "//item/link/text()")

            if last_id not in new_last_id.get():  # type: ignore[operator]
                self.bot.logger.debug("🐦 New tweets detected")

                def get_tweets(xml: Selector) -> str:
                    message = "😭 Glitchy Retweeted Cunny 😭\n"
                    for t in xml.xpath("//item"):
                        link = t.xpath(".//link/text()").get()
                        if last_id in link:  # type: ignore[operator]
                            break
                        if "RT by" in t.xpath(".//title/text()").get():  # type: ignore[operator]
                            link = t.xpath(".//link/text()").get()
                            message += f"{link.replace(NITTER, TWITFIX).strip('#m')}\n"  # type: ignore[union-attr]
                    return message

                message = await anyio.to_thread.run_sync(get_tweets, xml)
                await ID_FILE.write_text(new_last_id.get().split("/")[-1].strip("#m"))  # type: ignore[union-attr]

                if TWITFIX in message:
                    for g in self.bot.guilds:
                        channel_id = await self.get_cnuy_channel(g.id)

                        if channel_id:
                            channel = self.bot.get_channel(channel_id)
                            self.bot.logger.debug(f"📬 Sending cunny to {channel}")
                            await channel.send(message)  # type:ignore[union-attr]

    @listen()
    async def on_startup(self) -> None:
        """Even triggered on startup."""
        self.check_twitter.start()

    @slash_command("set_cnuy_channel", description="Set the cunny posting channel for the server")
    @slash_option(
        "channel",
        description="Name of the channel to set",
        opt_type=OptionType.CHANNEL,
        required=True,
        channel_types=[ChannelType.GUILD_TEXT],
    )
    @check(guild_only())
    @check(has_permission(Permissions.MANAGE_CHANNELS))
    @no_type_check
    async def command_set_cnuy_channel(self, ctx: InteractionContext, channel: GuildText) -> Message:
        """Set a cunny channel."""
        if not isinstance(channel, GuildText):
            return await ctx.send("💥 Error! Only guild text channels allowed.", ephemeral=True)

        async with DB as db:
            await db.server.upsert(
                where={"id": ctx.guild.id},
                data={
                    "create": ServerCreateInput(id=ctx.guild.id, cnuy_channel=channel.id),
                    "update": {"cnuy_channel": channel.id},
                },
            )
            self.bot.logger.debug(f"📬 Successfully set confession channel for {ctx.guild.id}")

        return await ctx.send(f"😭 Successfully set {channel.name} as the cunny channel.", ephemeral=True)

    @slash_command("remove_cnuy_channel", description="Remove the cunny posting channel")
    @check(guild_only())
    @check(has_permission(Permissions.MANAGE_CHANNELS))
    @no_type_check
    async def command_remove_cnuy_channel(self, ctx: InteractionContext) -> Message:
        """Remove the cunny channel."""
        async with DB as db:
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
        await anyio.to_thread.run_sync(self.check_twitter.restart)
        await ctx.send("✅ Done checking!", ephemeral=True)
