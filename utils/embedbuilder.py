from datetime import datetime
from naff import Embed, Color
from typing import Union, List, Optional, Tuple


async def embed_builder(
    description: Optional[str] = None,
    title: Optional[str] = None,
    color: Optional[Union[Color, dict, tuple, list, str, int]] = Color.random(),
    fields: Optional[List[Tuple[str, str, bool]]] = None,
    thumbnail: Optional[str] = None,
    author: Optional[Tuple[str, str]] = None,
    footer: Optional[Tuple[str, Optional[str]]] = None,
    url: Optional[str] = None,
    timestamp: Optional[datetime] = None,
    image: Optional[str] = None,
) -> Embed:
    """Quickly build embeds with one function call

    Args:
        description: The description of the embed. Defaults to None.
        title: The title of the embed. Defaults to None.
        color: The colour of the embed. Defaults to Color.random().
        fields: A list of fields to add to the embed. Defaults to None.
        thumbnail: The thumbnail of the embed. Defaults to None.
        author: The author of the embed. Defaults to None.
        footer: The footer of the embed. Defaults to None.
        url: The url the embed should direct to when clicked. Defaults to None.
        timestamp: Timestamp of embed content. Defaults to None.
        image: The image of the embed. Defaults to None.

    Returns:
        A NAFF embed object
    """

    embed = Embed(
        title=title, description=description, color=color, url=url, timestamp=timestamp
    )
    if fields:
        for field in fields:
            embed.add_field(field[0], field[1], bool(field[2]))
    if thumbnail:
        embed.set_thumbnail(thumbnail)
    if author:
        embed.set_author(author[0], author[1])
    if footer:
        embed.set_footer(footer[0], footer[1])
    if image:
        embed.set_image(image)

    return embed
