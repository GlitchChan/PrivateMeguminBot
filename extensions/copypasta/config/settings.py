import os
import re
from pathlib import Path
from typing import no_type_check

import attr
import tomlkit
from interactions import PartialEmoji

__all__ = ("pastas", "add_custom_pasta", "remove_copypata", "update_custom_pasta")

pastas = []
base_pasta = Path(__file__).parent / "base.copypasta.toml"
custom_pasta = Path(__file__).parent / "custom.copypasta.toml"


@attr.frozen()
class Copyasta:  # type:ignore[no-untyped-def]
    """Class to represent a copypasta."""

    name: str = attr.ib()
    re: str = attr.ib(converter=lambda x: re.compile(x, re.IGNORECASE))  # type:ignore[var-annotated]
    text: str = attr.ib()
    emoji: str = attr.ib(converter=lambda x: PartialEmoji.from_str(x))  # type:ignore[var-annotated]
    file: str = attr.ib()


# Generate all the copypastas
with base_pasta.open(encoding="utf-8") as b, custom_pasta.open(encoding="utf-8") as c:
    base = tomlkit.parse(b.read())
    custom = tomlkit.parse(c.read())

    combined = {**base, **custom}
    for t, v in combined.items():
        pastas.append(Copyasta(t, v.get("re"), v.get("text"), v.get("emoji"), v.get("file")))


@no_type_check
async def update_custom_pasta(
    name: str,
    u_name: str | None = None,
    u_regex: str | None = None,
    u_text: str | None = None,
    u_emoji: str | None = None,
    u_file: str | None = None,
    r_file: bool | None = None,
) -> None:
    """Update a copyasta in the system.

    Args:
        name: Name of the copypasta
        u_name: Updated name
        u_regex: Updated regex
        u_text: Updated text
        u_emoji: Updated emoji
        u_file: Updated file
        r_file: Remove file
    """
    toml = tomlkit.parse(custom_pasta.read_text("utf-8"))

    old = toml[name]
    toml.pop(name)
    name = u_name if u_name else name
    edited = tomlkit.table(is_super_table=True)
    edited.update(old)

    if r_file and old["file"] or u_file and old["file"]:
        old_file = Path(__file__).parent.parent / f"assets/{old['file']}"
        os.remove(old_file)
        edited.update({"file": ""})
    if u_file:
        edited.update({"file": u_file})
    edited.update(
        {
            "re": u_regex or old["re"],
            "text": u_text or old["text"],
            "emoji": u_emoji or old["emoji"],
        }
    )
    toml.append(name, edited)
    with custom_pasta.open("w", encoding="utf-8") as t:
        tomlkit.dump(toml, t)
    pastas[:] = [c for c in pastas if c.name != name]
    pastas.append(Copyasta(name=u_name or name, **toml[u_name or name]))


async def add_custom_pasta(name: str, regex: str, text: str | None, emoji: str | None, file: str | None) -> None:
    """Add a custom copypasta to the system.

    Args:
        name: Name of the copypasta
        regex: Regex to match for the copypasta
        text: Any text to respond with
        emoji: An emoji to respond with
        file: Any file to respond with

    Returns:
        None
    """
    toml = tomlkit.parse(custom_pasta.read_text("utf-8"))
    pasta = tomlkit.table(is_super_table=True)
    pasta.update({"re": regex, "text": text or "", "emoji": emoji or "", "file": file or ""})
    toml.append(name, pasta)

    with custom_pasta.open("w", encoding="utf-8") as t:
        tomlkit.dump(toml, t)

    pastas.append(Copyasta(name=name, **toml[name]))  # type:ignore[arg-type]


async def remove_copypata(name: str) -> None:
    """Remove a custom copypasta.

    Args:
        name: Name of the copypasta

    Returns:
        None
    """
    toml = tomlkit.parse(custom_pasta.read_text("utf-8"))
    file = toml[name]["file"]  # type: ignore[index]

    if file:
        path = Path(__file__).parent.parent / f"assets/{file}"
        os.remove(path)

    toml.pop(name)
    with custom_pasta.open("w", encoding="utf-8") as t:
        tomlkit.dump(toml, t)
        pastas[:] = [c for c in pastas if c.name != name]
