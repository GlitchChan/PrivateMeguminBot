import re
from typing import no_type_check

import anyio
from anyio import to_thread
from humanize import intcomma, metric
from interactions import (
    Buckets,
    ChannelType,
    Color,
    Embed,
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
from interactions.api.events.discord import MessageCreate
from prisma.errors import PrismaError
from prisma.types import UserCreateInput

from v1.core import DB

SEX_REGEX = re.compile(r"\s?(?:e?)+s+e+(?:g+|(?:x+|s+))\b", re.IGNORECASE)


class Sexboard(Extension):
    """Extension for sexboard leaderboard."""

    @listen()
    async def _message(self, event: MessageCreate) -> None:
        m = event.message

        # Ingore self and bot message:
        if m.author.bot or m.channel.type in (ChannelType.DM, ChannelType.GROUP_DM):
            return

        if re.search(SEX_REGEX, m.content):
            self.bot.debug("🔥 Detected sex!")

            async with DB as db:
                try:
                    await db.user.upsert(
                        where={"id": m.author.id},
                        data={"create": UserCreateInput(id=m.author.id), "update": {"sex_count": {"increment": 1}}},
                    )
                    self.bot.debug(f"⬆️ Successfully updated {m.author.username}'s sex_count")
                except PrismaError:
                    pass

    @slash_command("sexboard", description="Shows the top 10 sex havers")
    @slash_option("raw", description="Removes abbreviations of larger numbers", opt_type=OptionType.BOOLEAN)
    @cooldown(Buckets.GUILD, 1, 3)
    @no_type_check
    async def command_sexboard(self, ctx: InteractionContext, raw: bool | None = None) -> Message:
        """Command to get top 10 sex havers."""
        async with DB as db:
            try:
                users = await db.user.find_many(take=10, order={"sex_count": "desc"})
            except PrismaError:
                return await ctx.send("The leaderboard doesn't have any users!")

        if not users:
            return await ctx.send("The leaderboard doesn't have any users!")

        leaderboard = []
        for idx, u in enumerate(users):
            user = await self.bot.fetch_user(u.id, force=True)
            count = (
                await to_thread.run_sync(metric, u.sex_count)
                if not raw
                else await to_thread.run_sync(intcomma, u.sex_count)
            )

            match idx:
                case 0:
                    leaderboard.append(user.display_name)
                    leaderboard.append(f"👑 {user.display_name} - {count}\n")
                case 1:
                    leaderboard[1] += f"🥈 {user.display_name} - {count}\n"
                case 2:
                    leaderboard[1] += f"🥉 {user.display_name} - {count}\n"
                case _:
                    leaderboard[1] += f"{user.display_name} - {count}\n"

        banner_file = anyio.Path(__file__).parent / "banner.png"
        embed_file = File(banner_file, file_name="banner.png")
        leader = f"👑 {leaderboard[0]} is currently the best sexer"

        banner = Embed(color=Color.from_hex("#e9d0a4"))
        banner.set_image("attachment://banner.png")
        list_emb = Embed(title=leader, description=leaderboard[1], color=Color.from_hex("#e9d0a4"))
        list_emb.set_footer("Sexboard banner by: @tsunemiukiyo")
        return await ctx.send(embeds=[banner, list_emb], files=embed_file)

    @slash_command("set_sex_number", description="Sets a users sex count")
    @slash_option("user", "User to update", OptionType.USER, required=True)
    @slash_option("count", "Number to use", OptionType.INTEGER, required=True)
    @check(is_owner())
    async def dev_set_sexboard_count(self, ctx: InteractionContext, user: User, count: int) -> Message:
        """Command to manually set someone's sexboard count."""
        async with DB as db:
            await db.user.upsert(
                where={"id": user.id},
                data={"create": UserCreateInput(id=user.id, sex_count=count), "update": {"sex_count": count}},
            )
            self.bot.debug(f"📝 Successfully updated {user.id} sex_count")

        return await ctx.send(f"📝 Successfully set {user.username}'s sex count to: {count}", ephemeral=True)
