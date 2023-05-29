import random
from io import BytesIO
from typing import no_type_check

from interactions import (
    Attachment,
    Buckets,
    Color,
    Embed,
    Extension,
    File,
    GuildText,
    InteractionContext,
    Message,
    OptionType,
    Permissions,
    Timestamp,
    User,
    check,
    cooldown,
    guild_only,
    slash_command,
    slash_option,
)
from petpetgif import petpet  # type:ignore[import]

from necoarc import get_confession_channel, has_permission, set_confession_channel

# TODO: Add a random chance for an uwuified lolcat bible quote on message.


class Funny(Extension):
    """Extension all about fun!"""

    @slash_command("set_confess_channel", description="Set the confession channel for the server")
    @slash_option("channel", description="Name of the channel to set", opt_type=OptionType.CHANNEL, required=True)
    @check(guild_only())
    @check(has_permission(Permissions.MANAGE_CHANNELS))
    @no_type_check
    async def command_set_confess_channel(self, ctx: InteractionContext, channel: GuildText) -> Message:
        """Set a confession channel."""
        if not isinstance(channel, GuildText):
            return await ctx.send("💥 Error! Only guild text channels allowed.", ephemeral=True)

        await set_confession_channel(ctx.guild_id, channel.id)
        return await ctx.send(f"🤫 Successfully set {channel.name} as the confession channel.", ephemeral=True)

    @slash_command("confess", description="Confess your sins")
    @slash_option("text", description="Your confession", opt_type=OptionType.STRING, required=True)
    @slash_option("image", description="An added attachment", opt_type=OptionType.ATTACHMENT)
    @slash_option("guild_id", description="Manually specify a guild (DM only)", opt_type=OptionType.INTEGER)
    @cooldown(Buckets.USER, 3, 10)
    @no_type_check
    async def command_confess(
        self, ctx: InteractionContext, text: str, image: Attachment | None = None, guild_id: int | None = None
    ) -> Message:
        """Confess your sins."""
        if ctx.guild_id and guild_id or not ctx.guild_id and not guild_id:
            return await ctx.send(
                f"💥 Error! Please{' only' if ctx.guild_id else ''} provide `guild_id` when you are in dms.",
                ephemeral=True,
            )

        channel = await get_confession_channel(ctx.guild_id if isinstance(ctx.channel, GuildText) else guild_id)
        if not channel:
            return await ctx.send(f"💥 Error! Guild {ctx.guild.name} doesn't have confessions enabled.", ephemeral=True)

        e = Embed("🤫 Someone just confessed 🤫", description=text, color=Color.random(), timestamp=Timestamp.utcnow())
        if image:
            e.set_image(image.url)
        e.set_footer("🤔 Use /confess in DMs or a Guild to confess!")
        await ctx.bot.get_channel(channel).send(embeds=[e])
        guild = ctx.bot.get_guild(guild_id).name if guild_id else ctx.guild.name
        return await ctx.send(f"🤫 Successfully sent confession to {guild}", ephemeral=True)

    @slash_command("petpet", description="Pet a user")
    @slash_option("user", description="User to pet", opt_type=OptionType.USER, required=True)
    @no_type_check
    async def command_petpet(self, ctx: InteractionContext, user: User) -> Message:
        """Pet a user."""
        source = BytesIO(await user.avatar.fetch())
        dest = BytesIO()
        petpet.make(source, dest)
        dest.seek(0)

        petgif = File(file=dest, file_name="petpet.gif")
        return await ctx.send(f"🥺 {ctx.author.mention} just petted {user.mention} 💖", file=petgif)

    @slash_command("eightball", description="🎱 It's an eight ball")
    @slash_option("question", description="Ask the eight ball a question", opt_type=OptionType.STRING, required=True)
    @no_type_check
    async def command_eightball(self, ctx: InteractionContext, question: str) -> Message:
        """It's an eightball."""
        if len(question) < 5:  # noqa[PLR2004]
            return await ctx.send("🤔 Please ask something longer.")

        random.seed(hash(question))

        responses = [
            "As I see it, yes.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don`t count on it.",
            "It is certain.",
            "It is decidedly so.",
            "Most likely.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Outlook good.",
            "Reply hazy, try again.",
            "Signs point to yes.",
            "Very doubtful.",
            "Without a doubt.",
            "Yes.",
            "Yes - definitely.",
            "You may rely on it.",
            "What do you think?",
            "Maybe yes maybe not",
        ]
        return await ctx.send(f"🤔 {ctx.author.mention} asked: {question}\n\n🎱 Response: {random.choice(responses)}")
