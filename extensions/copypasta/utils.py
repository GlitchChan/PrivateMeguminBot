import re

from interactions import InteractionContext, PartialEmoji

from .config.settings import pastas


async def validate_copypasta(
    ctx: InteractionContext, name: str | None, regex: str | None, emoji: str | None, edited_name: str | None = None
) -> bool:
    """Function to validate a copypasta."""
    names = [c.name for c in pastas]

    if name in names or edited_name in names:
        await ctx.send("💥 Error! Invalid name, a copypasta already exists with this name!", ephemeral=True)
        return False

    if regex:
        try:
            re.compile(regex)
        except re.error:
            await ctx.send("💥 Error! Invalid regex, please try again.")
            return False
    if emoji:
        try:
            PartialEmoji.from_str(emoji)
        except ValueError:
            await ctx.send("💥 Error! Invalid emoji, please try again.")
            return False
    return True
