import random
from io import BytesIO

from naff import (
    Attachment,
    Extension,
    File,
    GuildChannel,
    InteractionContext,
    OptionTypes,
    Permissions,
    PrefixedContext,
    User,
    check,
    dm_only,
    guild_only,
    is_owner,
    prefixed_command,
    slash_command,
    slash_option,
)
from petpetgif import petpet

from core import (
    Megumin,
    confession_embed,
    embed_builder,
    get_confession_channel,
    get_sex_leaderboard,
    has_permission,
    set_confession_channel,
    set_user_sex_count,
)


class Memes(Extension):
    bot: Megumin

    @slash_command("pet_pet", description="Send a pet pet gif of a certain user")
    @slash_option("user", "User you want to pet", OptionTypes.USER, required=True)
    async def command_pet_pet(self, ctx: InteractionContext, user: User):
        source = BytesIO(await user.avatar.fetch())
        dest = BytesIO()
        petpet.make(source, dest)
        dest.seek(0)

        petpet_file = File(file=dest, file_name="petpet.gif")
        await ctx.send(file=petpet_file)

    @slash_command("rate_me", description="I will rate the person you give")
    @slash_option("ratee", "Thing you want to rate", OptionTypes.STRING, required=True)
    async def command_rate_me(self, ctx: InteractionContext, ratee: str):
        rating = (hash(ratee) % 10) + 1
        await ctx.send(f"I rate {ratee} a {rating}/10")

    @slash_command(name="8ball", description="It's an 8ball")
    @slash_option(
        "question",
        "Question you want to ask the eight ball",
        OptionTypes.STRING,
        required=True,
    )
    async def command_eight_ball(self, ctx: InteractionContext, question: str):

        responses = [
            "As I see it, yes.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Dont count on it.",
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
        ]

        await ctx.send(
            embeds=[
                await embed_builder(
                    title="Magic 8 Ball",
                    description=f"Question: {question}\n Answer: {random.choice(responses)}",
                )
            ]
        )

    @slash_command(
        "set_confession_channel",
        description="Set the confession channel for the server",
    )
    @slash_option(
        "channel",
        "The channel you want to set as the confession channel",
        OptionTypes.CHANNEL,
        required=True,
    )
    @check(has_permission(Permissions.MANAGE_CHANNELS))
    @check(guild_only())
    async def command_set_confession_channel(self, ctx: InteractionContext, channel: GuildChannel):
        """Command to set the confession channel for a guild"""
        await set_confession_channel(ctx.guild_id, channel.id)
        await ctx.send(
            f"Successfully set the confession channel to {channel.mention}",
            ephemeral=True,
        )

    @slash_command("confess", description="Anonymous confession of your sins")
    @slash_option("confession", "Your confession", OptionTypes.STRING, required=True)
    @slash_option("image", "Any image you want to add", OptionTypes.ATTACHMENT, required=False)
    @check(guild_only())
    async def command_confess(self, ctx: InteractionContext, confession: str, image: Attachment = None):
        """Anon confessions to a set channel configured by the admins"""
        emb = await confession_embed(confession, image)
        confess_channel = await get_confession_channel(ctx.guild_id)

        if confess_channel is None:
            return await ctx.send("Guild has not set up a confess channel.", ephemeral=True)

        await ctx.bot.get_channel(confess_channel).send(embeds=[emb])
        await ctx.send("Sucessfully sent confession", ephemeral=True)

    @prefixed_command("confess")
    @check(dm_only())
    async def prefixed_command_confess(self, ctx: PrefixedContext, guild_id: int, *, confession: str):
        """megu confess `guild_id` `confession` and 1 image attachment"""
        attachments = ctx.message.attachments
        emb = await confession_embed(confession, attachments[0] if attachments else None)
        await ctx.send("Sending confession", delete_after=5)

        confess_channel = await get_confession_channel(guild_id)

        if confess_channel is None:
            return await ctx.send("Guild has not set up a confess channel.", delete_after=5)

        await ctx.bot.get_channel(confess_channel).send(embeds=[emb])

    @slash_command("sex_leaderboard", description="Fetches the sex leaderboard")
    async def slash_sex_leaderboard(self, ctx: InteractionContext):
        leaderboard = [f"<@{user.id}> | {user.sex_count} Sex Messages" for user in await get_sex_leaderboard()]
        leaderboard = " \n".join(leaderboard)

        await ctx.send(embeds=[await embed_builder(leaderboard, "Sex Leaderboard Top 10", color="#f47fff")])

    @slash_command("set_sex_number", description="Sets a users sex count")
    @slash_option("user", "User to update", OptionTypes.USER, required=True)
    @slash_option("count", "Number to use", OptionTypes.INTEGER, required=True)
    @check(is_owner())
    async def slash_set_sex_number(self, ctx: InteractionContext, user: User, count: int):
        await set_user_sex_count(user.id, int(count))
        await ctx.send(f"Successfully set {user}'s sex count to: {int(count)}", ephemeral=True)


def setup(client):
    Memes(client)
