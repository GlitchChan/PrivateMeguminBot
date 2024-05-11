import os
import re
from pathlib import Path
from typing import no_type_check

import attr
import tomlkit as tk
from interactions import PartialEmoji
from tomlkit.toml_file import TOMLFile

base_pasta = TOMLFile(Path(__file__).parent / "base.copypasta.toml")
custom_pasta = TOMLFile(Path(__file__).parent / "custom.copypasta.toml")


@attr.frozen(eq=False, order=False, hash=False, kw_only=False)
class Copyasta:  # type:ignore[no-untyped-def]
    """Class to represent a copypasta."""

    name: str = attr.ib()
    re: str = attr.ib(converter=lambda x: re.compile(x, re.IGNORECASE))  # type:ignore[var-annotated]
    text: str = attr.ib()
    emoji: str = attr.ib(converter=lambda x: PartialEmoji.from_str(x))  # type:ignore[var-annotated]
    file: str = attr.ib()


# Generate all the copypastas
pastas: list[Copyasta] = []
combined = base_pasta.read()
combined.update(custom_pasta.read())
for t, v in combined.items():
    pastas.append(Copyasta(t, v["re"], v["text"], v["emoji"], v["file"]))


@no_type_check
def update_custom_pasta(
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
    custom = custom_pasta.read()
    old_pasta = custom[name]
    custom.pop(name)

    edited_pasta = tk.table(is_super_table=True)
    edited_pasta.update(old_pasta)

    if r_file or u_file:
        try:
            old_file = Path(__file__).parent.parent / f"assets/{old_pasta['file']}"
            os.remove(old_file)
            edited_pasta.update({"file": ""})
        except os.error:
            pass

    if u_file:
        edited_pasta.update({"file": u_file})

    edited_pasta.update(
        {
            "re": u_regex or old_pasta["re"],
            "text": u_text or old_pasta["text"],
            "emoji": u_emoji or old_pasta["emoji"],
        }
    )
    custom.add(u_name or name, edited_pasta)
    custom_pasta.write(custom)

    pastas[:] = [c for c in pastas if c.name != name]
    pastas.append(Copyasta(name=u_name or name, **custom[u_name or name]))


def add_custom_pasta(name: str, regex: str, text: str | None, emoji: str | None, file: str | None) -> None:
    """Add a custom copypasta to the system.

    Args:
        name: Name of the copypasta
        regex: Regex to match for the copypasta
        text: Any text to respond with
        emoji: An emoji to respond with
        file: Any file to respond with
    """
    custom = custom_pasta.read()

    new_pasta = tk.table(is_super_table=True)
    new_pasta.update({"re": regex, "text": text or "", "emoji": emoji or "", "file": file or ""})
    custom.append(name, new_pasta)

    custom_pasta.write(custom)
    pastas.append(Copyasta(name=name, **custom[name]))  # type:ignore[arg-type]


def remove_copypata(name: str) -> None:
    """Remove a custom copypasta.

    Args:
        name: Name of the copypasta
    """
    custom = custom_pasta.read()

    if custom[name]["file"]:  # type:ignore[index]
        path = Path(__file__).parent.parent / f"assets/{custom[name]['file']}"  # type:ignore[index]
        os.remove(path)

    custom.pop(name)
    custom_pasta.write(custom)
    pastas[:] = [c for c in pastas if c.name != name]
