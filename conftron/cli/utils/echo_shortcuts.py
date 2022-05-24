from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, Any

import typer
from art import text2art

from conftron import metadata

if TYPE_CHECKING:
    from conftron.sync.utils.metadata_manager import SyncMetadata

WORDS_DEFAULT = MappingProxyType({False: "UNAVAILABLE", True: "OK"})
WORDS_STYLES_DEFAULT = MappingProxyType(
    {True: {"fg": typer.colors.GREEN, "bold": True}, False: {"fg": typer.colors.YELLOW, "bold": True}}
)


def get_binary_styled_word(
    value: bool,
    words: dict[bool, str] | MappingProxyType[bool, str] = WORDS_DEFAULT,
    words_styles: dict[bool, dict[str, Any]] | MappingProxyType[bool, dict[str, Any]] = WORDS_STYLES_DEFAULT,
) -> str:
    return typer.style(words[value], **words_styles[value])


def get_metadata_message(metadata: SyncMetadata, line_before: str = ""):
    message: list[str] = []

    for key, value in metadata.to_dict().items():
        message.append(f"{line_before}{key}: {value}")

    return "\n".join(message)


def get_art_title():
    title = text2art(metadata.name, font="alligator2", chr_ignore=True)

    return f"{title}"
