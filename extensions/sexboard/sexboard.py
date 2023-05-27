import re

from humanize import intcomma, metric
from interactions import (
    Buckets,
    ChannelType,
    Embed,
    Extension,
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
from loguru import logger as log

from necoarc import get_sex_leaderboard, set_user_sex_count, update_user_sex_count

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
            log.debug("🔥 Detected sex!")
            await update_user_sex_count(m.author.id)

    @slash_command("sexboard", description="Shows the top 10 sex havers")
    @slash_option("raw", description="Removes abbreviations of larger numbers", opt_type=OptionType.BOOLEAN)
    @cooldown(Buckets.GUILD, 1, 3)
    async def command_sexboard(self, ctx: InteractionContext, raw: bool | None = None) -> Message:
        """Command to get top 10 sex havers."""
        users = await get_sex_leaderboard()

        if not users:
            return await ctx.send("The leaderboard doesn't have any users!")

        leaderboard = []
        for idx, u in enumerate(users):
            name = ctx.bot.get_user(u.id).username  # type:ignore[union-attr]
            count = metric(u.sex_count) if not raw else intcomma(u.sex_count)
            match idx:
                case 0:
                    leaderboard.append(f"👑 {name} - {count}")
                case 1:
                    leaderboard.append(f"🥈 {name} - {count}")
                case 2:
                    leaderboard.append(f"🥉 {name} - {count}")
                case _:
                    leaderboard.append(f"{name} - {count}")

        e = Embed("🔥Sexboard Leaderboard🔥", description=" \n".join(i for i in leaderboard))
        return await ctx.send(embeds=[e])

    @slash_command("set_sex_number", description="Sets a users sex count")
    @slash_option("user", "User to update", OptionType.USER, required=True)
    @slash_option("count", "Number to use", OptionType.INTEGER, required=True)
    @check(is_owner())
    async def dev_set_sexboard_count(self, ctx: InteractionContext, user: User, count: int) -> Message:
        """Command to manually set someone's sexboard count."""
        await set_user_sex_count(user.id, count)
        return await ctx.send(f"📝 Successfully set {user.username}'s sex count to: {count}", ephemeral=True)
