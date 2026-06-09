"""
Anvil extraction contract — formalised data structures and protocol.

Defines the ChunkRecord contract, structural metadata, symbol data types,
the LanguageExtractor protocol, and the universal chunk type vocabulary.
"""
from __future__ import annotations

from typing import Protocol, TypedDict


# --- Symbol sub-records ---

class ImportRecord(TypedDict):
    module: str
    names: list[str]
    is_from: bool
    line: int


class DefinitionRecord(TypedDict):
    name: str
    type: str
    line: int
    bases: list[str]


class CallRecord(TypedDict):
    caller: str
    callee: str
    line: int


class TestMappingRecord(TypedDict):
    test_name: str
    tested_module: str


# --- Structural metadata ---

class StructuralMetadata(TypedDict):
    cyclomatic_complexity: int
    nesting_depth: int
    parameter_count: int
    import_count: int
    has_docstring: bool
    line_count: int


# --- Symbol data ---

class SymbolData(TypedDict):
    imports: list[ImportRecord]
    definitions: list[DefinitionRecord]
    calls: list[CallRecord]
    test_mappings: list[TestMappingRecord]


# --- Chunk record ---

class ChunkRecord(TypedDict, total=False):
    # Required fields (every extractor MUST emit)
    name: str
    file_path: str
    chunk_type: str
    content: str
    content_hash: str
    start_line: int
    end_line: int
    parent_name: str | None

    # Optional fields
    structural_metadata: StructuralMetadata | None
    symbols: SymbolData | None


# --- Universal chunk types ---

UNIVERSAL_CHUNK_TYPES: set[str] = {
    "function",
    "class",
    "method",
    "module",
    "test_case",
    "config",
    "struct",
    "enum",
    "protocol",
    "component",
    "type_alias",
}


# --- Language extractor protocol ---

class LanguageExtractor(Protocol):
    """Interface that every language extractor must implement."""

    language: str
    file_extensions: set[str]

    def parse_file(self, file_path: str) -> list[dict]:
        """Parse a source file and return chunk records."""
        ...

    def extract_symbols(self, file_path: str, source: str) -> dict:
        """Extract symbol data from a source file."""
        ...

    def compute_structural_metadata(self, chunk_content: str,
                                     chunk_type: str) -> dict:
        """Compute structural metrics for a single chunk."""
        ...

    def resolve_module_path(self, file_path: str) -> str:
        """Convert a file path to a language-specific module identifier."""
        ...
