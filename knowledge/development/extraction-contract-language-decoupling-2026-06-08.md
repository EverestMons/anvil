# Extraction Contract + Language-Extractor Decoupling — Dev Log

**Date:** 2026-06-08
**Plan:** `executable-anvil-extraction-contract-language-decoupling-2026-06-08`
**Blueprint:** `knowledge/architecture/anvil-extraction-contract-archetype-design-2026-06-08.md` (sections A, B, B.4, B.5)

## Summary

Implemented the language-extraction axis of the extraction-contract blueprint. This formalises the `ChunkRecord` contract, introduces a language-extractor registry, wraps the existing Python parser behind the `LanguageExtractor` protocol, dispatches extraction by file extension instead of hardcoding `.py`, and relaxes the `chunk_type` CHECK constraint to allow arbitrary strings.

**Scope:** Language-extraction axis ONLY. Classifier, scorer weights, archetypes, and `SCAN_TARGETS` format are untouched (deferred to Build Plan 2).

## Changes

### New Files

1. **`src/contracts.py`** — Formalised extraction contract:
   - `ChunkRecord` TypedDict (required + optional fields)
   - `StructuralMetadata`, `SymbolData`, `ImportRecord`, `DefinitionRecord`, `CallRecord`, `TestMappingRecord` TypedDicts
   - `UNIVERSAL_CHUNK_TYPES` set constant (11 types)
   - `LanguageExtractor` Protocol with `parse_file`, `extract_symbols`, `compute_structural_metadata`, `resolve_module_path`

2. **`src/parsers/registry.py`** — Language extractor registry:
   - `EXTRACTORS` dict mapping file extensions to extractor instances
   - `register(extractor)` — registers for all declared extensions
   - `get_extractor(file_extension)` — returns extractor or None

### Modified Files

3. **`src/parsers/python_parser.py`** — Added `PythonExtractor` class:
   - Implements `LanguageExtractor` protocol (`language="python"`, `file_extensions={".py"}`)
   - All methods delegate to existing module functions — NO logic changes
   - `detect_sqlalchemy_models` exposed as class method (post-parse hook)
   - `resolve_module_path` converts `foo/bar.py` → `foo.bar`
   - Auto-registers via `registry.register(PythonExtractor())` at import

4. **`src/extractor.py`** — Refactored for registry dispatch:
   - Replaced `py_modules = [m for m in module_chunks if m["file_path"].endswith(".py")]` with extension-based filtering via `registry.get_extractor()`
   - Replaced `python_parser.parse_file(abs_path)` with `extractor.parse_file(abs_path)`
   - Replaced direct `ast.parse()` + `python_parser.extract_symbols()` with `extractor.extract_symbols()`
   - New `_store_file_metadata_via_extractor()` replaces old `_store_file_metadata()` — iterates parsed chunks and calls `extractor.compute_structural_metadata()` per chunk
   - SQLAlchemy detection called through `extractor.detect_sqlalchemy_models()` (guarded by `hasattr`)
   - Module-path resolution in `resolve_dependencies()` uses `extractor.resolve_module_path()` instead of hardcoded `.replace("/", ".").replace(".py", "")`

5. **`src/db.py`** — Relaxed `chunk_type` CHECK constraint:
   - `CREATE TABLE` now uses `chunk_type TEXT NOT NULL` (no CHECK)
   - Added `_migrate_chunk_type_constraint()` migration: detects existing CHECK via `sqlite_master`, recreates table without it, preserves all rows and indexes

6. **`tests/test_db.py`** — Updated one test:
   - `test_chunk_type_check_constraint` → `test_chunk_type_accepts_arbitrary_strings`: verifies that non-Python chunk types (e.g. `struct`) are now accepted

## Verification

### Behavior Preservation (Step C)

Extraction baseline captured BEFORE changes, re-run AFTER:

| Project | Baseline Count | After Count | Baseline Hash | After Hash | Match |
|---|---|---|---|---|---|
| invoice-pulse | 8206 | 8206 | b33a444... | b33a444... | IDENTICAL |
| bellows | 3695 | 3695 | 0e70adf... | 0e70adf... | IDENTICAL |

Hash method: SHA-256 over `(name, file_path, chunk_type, content_hash, structural_metadata)` ordered by `(file_path, start_line)`.

### Test Suite (Step D)

```
240 passed in 3.54s
```

Matches baseline count of 240. One test updated (`test_chunk_type_check_constraint` → `test_chunk_type_accepts_arbitrary_strings`); output assertions unchanged.

## Design Decisions

1. **PythonExtractor wraps, doesn't replace:** Module-level functions (`parse_file`, `extract_symbols`, etc.) remain intact. The class delegates to them. This preserves backward compatibility for existing test imports.

2. **`_store_file_metadata_via_extractor` iterates parsed chunks:** Instead of re-walking the AST to find chunks (which the old `_store_file_metadata` did), the new function iterates the already-parsed chunk list and calls `extractor.compute_structural_metadata(content, chunk_type)`. Simpler and language-agnostic.

3. **SQLAlchemy detection guarded by `hasattr`:** Only Python files have SQLAlchemy models. The extractor dispatches this as a language-specific post-parse hook rather than a universal step.

4. **`chunk_type` migration is idempotent:** Checks `sqlite_master` for CHECK presence before recreating the table. Fresh databases created with `init_db()` get the relaxed schema directly.

---

## Output Receipt
**Agent:** Anvil Developer
**Step:** Step 1 (DEV)
**Status:** Complete

### What Was Done
Implemented the language-extraction axis of the extraction-contract blueprint: formalised ChunkRecord contract and LanguageExtractor protocol, created extractor registry, wrapped Python parser in PythonExtractor class, refactored extractor.py for registry dispatch, relaxed chunk_type CHECK constraint with safe migration. Verified byte-identical extraction output for both invoice-pulse and bellows. Full test suite passes (240/240).

### Files Deposited
- `knowledge/development/extraction-contract-language-decoupling-2026-06-08.md` — this dev log
- `knowledge/qa/evidence/executable-anvil-extraction-contract-language-decoupling-2026-06-08/extract_baseline.txt` — pre-change baseline
- `knowledge/qa/evidence/executable-anvil-extraction-contract-language-decoupling-2026-06-08/extract_after.txt` — post-change comparison

### Files Created or Modified (Code)
- `src/contracts.py` — NEW: ChunkRecord contract, LanguageExtractor protocol, type definitions
- `src/parsers/registry.py` — NEW: extractor registry (register/get_extractor)
- `src/parsers/python_parser.py` — MODIFIED: added PythonExtractor class wrapping existing functions
- `src/extractor.py` — MODIFIED: registry dispatch, extractor-based symbol/metadata extraction
- `src/db.py` — MODIFIED: relaxed chunk_type CHECK, added migration function
- `tests/test_db.py` — MODIFIED: updated CHECK constraint test to verify relaxed behavior

### Decisions Made
- PythonExtractor delegates to existing functions (no logic duplication)
- _store_file_metadata_via_extractor iterates parsed chunks instead of re-walking AST
- SQLAlchemy hook guarded by hasattr for language-agnosticism
- chunk_type migration checks sqlite_master before acting (idempotent)

### Flags for CEO
- None

### Flags for Next Step
- The chunk_type migration has been run on the canonical DB (`anvil.db`). The CHECK constraint is gone and all 11,901 chunks survive intact.
- One test was updated: `test_chunk_type_check_constraint` → `test_chunk_type_accepts_arbitrary_strings`. The assertion changed from "rejects invalid" to "accepts struct". Same test count (240).
- `import ast` remains in `extractor.py` for the inheritance resolution section of `resolve_dependencies()`. This is Python-specific AST usage that persists in the core — a future plan could abstract it into the extractor protocol.
