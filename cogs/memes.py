import json

from io import BytesIO
from utils import (
    set_confess_channel,
    get_confess_channel,
    confession_embed,
    has_permission,
)
from petpetgif import petpet
from naff import (
    Extension,
    Client,
    slash_option,
    slash_command,
    OptionTypes,
    User,
    InteractionContext,
    Permissions,
    File,
    GuildChannel,
    Attachment,
    check,
    dm_only,
    prefixed_command,
    PrefixedContext,
    DMChannel,
)
from loguru import logger as log


class Memes(Extension):
    def __init__(self, client: Client):
        self.client = client
        log.success(f"Successfully loaded {__class__.__name__}")

    @slash_command("pet_pet", description="Send a pet pet gif of a certain user")
    @slash_option("user", "User you want to pet", OptionTypes.USER, required=False)
    async def command_pet_pet(self, ctx: InteractionContext, user: User):
        """Silly command to pet a user"""
        source = BytesIO(await user.avatar.fetch())
        dest = BytesIO()
        petpet.make(source, dest)
        dest.seek(0)

        petpet_file = File(file=dest, file_name="petpet.gif")
        await ctx.send(file=petpet_file)

    @slash_command("rate_me", description="I will rate the person you give")
    @slash_option("ratee", "Thing you want to rate", OptionTypes.STRING, required=False)
    async def rate_me(self, ctx: InteractionContext, ratee: str):
        rating = hash(ratee) % 10
        await ctx.send(f"I rate {ratee} a {rating}/10")



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
    async def command_set_confession_channel(
        self, ctx: InteractionContext, channel: GuildChannel
    ):
        """Command to set the confession channel for a guild"""
        try:
            set_confess_channel(ctx.guild_id, channel.id)
            await ctx.send(
                f"Successfully set the confession channel to {channel.mention}",
                ephemeral=True,
            )
        except:
            await ctx.send(
                "An unexpected error occurred when setting the confession channel"
            )

    @slash_command("confess", description="Anonymous confession of your sins")
    @slash_option("confession", "Your confession", OptionTypes.STRING, required=True)
    @slash_option(
        "image", "Any image you want to add", OptionTypes.ATTACHMENT, required=False
    )
    async def command_confess(
        self, ctx: InteractionContext, confession: str, image: Attachment = None
    ):
        """Anon confessions to a set channel configured by the admins"""

        if isinstance(ctx.channel, DMChannel):
            return await ctx.send(
                "This command only works in guilds try using: megu confess `guild_id` `confession` and an optional 1 image attachment"
            )

        emb = await confession_embed(confession, image)
        try:
            channel_id = get_confess_channel(ctx.guild_id)
        except KeyError:
            return await ctx.send(
                "Guild has not set up a confess channel.", ephemeral=True
            )

        await self.client.get_channel(channel_id).send(embeds=[emb])
        await ctx.send("Sucessfully sent confession", ephemeral=True)

    @prefixed_command("confess")
    @check(dm_only())
    async def prefixed_command_confess(
        self, ctx: PrefixedContext, guild_id: int, *confession: str
    ):
        """megu confess `guild_id` `confession` and 1 image attachment"""
        attachments = ctx.message.attachments
        emb = await confession_embed(
            " ".join(confession), attachments[0] if attachments else None
        )
        await ctx.send("Sending confession", delete_after=5)

        try:
            channel_id = get_confess_channel(guild_id)
        except KeyError:
            return await ctx.send(
                "Guild has not set up a confess channel.", delete_after=5
            )

        await self.client.get_channel(channel_id).send(embeds=[emb])


def setup(client):
    Memes(client)
