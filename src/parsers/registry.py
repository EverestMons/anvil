"""
Anvil language-extractor registry.

Maps file extensions to LanguageExtractor instances. Extractors self-register
at import time via ``register(extractor)``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.contracts import LanguageExtractor

EXTRACTORS: dict[str, "LanguageExtractor"] = {}


def register(extractor: "LanguageExtractor") -> None:
    """Register an extractor for each of its declared file extensions."""
    for ext in extractor.file_extensions:
        EXTRACTORS[ext] = extractor


def get_extractor(file_extension: str) -> "LanguageExtractor | None":
    """Return the registered extractor for *file_extension*, or ``None``."""
    return EXTRACTORS.get(file_extension)
