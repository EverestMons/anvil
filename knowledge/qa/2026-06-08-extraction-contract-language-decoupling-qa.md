# QA Report — Extraction Contract + Language-Extractor Decoupling

**Date:** 2026-06-09
**Plan:** `executable-anvil-extraction-contract-language-decoupling-2026-06-08`
**Blueprint:** `knowledge/architecture/anvil-extraction-contract-archetype-design-2026-06-08.md` (sections A, B, B.4, B.5)
**Dev Log:** `knowledge/development/extraction-contract-language-decoupling-2026-06-08.md`
**Agent:** Anvil QA Analyst
**Step:** Step 2 (QA)

---

## Verification Table

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | Contract + registry exist and conform | ✅ | `contract_check.txt` — `registry.get_extractor('.py')` returns `PythonExtractor` instance; `src/contracts.py` defines `ChunkRecord`, `LanguageExtractor` (Protocol), `StructuralMetadata`, `SymbolData`; `src/parsers/registry.py` defines `register`/`get_extractor`; `PythonExtractor` implements the protocol and is auto-registered at import |
| 2 | Extraction byte-identical before/after | ✅ | `extract_diff.txt` — invoice-pulse: count=8206, hash=b33a444...; bellows: count=3695, hash=0e70adf...; both IDENTICAL between baseline and after |
| 3 | `chunk_type` constraint relaxed without data loss | ✅ | `chunk_type_constraint.txt` — `sqlite_master` schema shows `chunk_type TEXT NOT NULL` with no CHECK; chunk counts unchanged (invoice-pulse=8206, bellows=3695) |
| 4 | Extraction no longer hardcodes `.py` | ✅ | `py_hardcode_check.txt` — `grep` for `.endswith(".py")` and `.py")` in `src/extractor.py` returned zero matches; extension dispatch goes through `registry.get_extractor()` |
| 5 | Full test suite passes | ✅ | `pytest_full.txt` — 240 passed in 4.95s; matches baseline count of 240; one test updated (`test_chunk_type_check_constraint` → `test_chunk_type_accepts_arbitrary_strings`) with output assertions unchanged |
| 6 | Scope guard — classifier/SCAN_TARGETS untouched | ✅ | `changed_files.txt` — `src/classifier.py` and `src/config.py` are NOT in the changed files list |

---

## Observations

1. **Behavior preservation confirmed.** The core regression gate — byte-identical extraction output for both invoice-pulse and bellows — passes. The SHA-256 hash over `(name, file_path, chunk_type, content_hash, structural_metadata)` ordered by `(file_path, start_line)` is identical before and after the refactor.

2. **Contract design is clean.** `src/contracts.py` uses `TypedDict` for all data structures and `Protocol` for the extractor interface. `ChunkRecord` uses `total=False` to allow optional fields while keeping the required fields documented in comments. `UNIVERSAL_CHUNK_TYPES` provides a 11-type vocabulary that supersedes the old CHECK constraint enum.

3. **Registry is minimal and correct.** `src/parsers/registry.py` is 26 lines: a dict, a register function, and a get function. `PythonExtractor` self-registers at import time. The import is triggered in `extractor.py` via `from src.parsers import python_parser  # noqa: F401`.

4. **Extractor dispatch is language-agnostic.** `src/extractor.py` filters modules via `registry.get_extractor(os.path.splitext(file_path)[1])` instead of `.endswith(".py")`. All parsing, symbol extraction, structural metadata computation, and module-path resolution go through the extractor instance.

5. **SQLAlchemy detection correctly guarded.** The `hasattr(extractor, "detect_sqlalchemy_models")` check ensures language-specific hooks only fire when the extractor supports them.

6. **`import ast` remains in extractor.py** for the inheritance resolution section of `resolve_dependencies()`. The DEV flagged this as Python-specific AST usage that persists in the core — a legitimate future abstraction target but not in scope for this plan.

7. **Migration is idempotent.** The `_migrate_chunk_type_constraint()` function checks `sqlite_master` for CHECK presence before recreating the table, and `init_db()` creates the relaxed schema directly for fresh databases.

---

## Output Receipt
**Agent:** Anvil QA Analyst
**Step:** Step 2 (QA)
**Status:** Complete

### What Was Done
Executed all 6 verification checks for the extraction contract + language-extractor decoupling plan. All checks pass. Contract and registry conform to blueprint spec. Extraction output is byte-identical before and after. chunk_type constraint relaxed without data loss. No .py hardcoding remains. Full test suite passes (240/240). Classifier and SCAN_TARGETS are untouched.

### Files Deposited
- `knowledge/qa/2026-06-08-extraction-contract-language-decoupling-qa.md` — this QA report
- `knowledge/qa/evidence/executable-anvil-extraction-contract-language-decoupling-2026-06-08/contract_check.txt` — check 1 evidence
- `knowledge/qa/evidence/executable-anvil-extraction-contract-language-decoupling-2026-06-08/extract_diff.txt` — check 2 evidence
- `knowledge/qa/evidence/executable-anvil-extraction-contract-language-decoupling-2026-06-08/chunk_type_constraint.txt` — check 3 evidence
- `knowledge/qa/evidence/executable-anvil-extraction-contract-language-decoupling-2026-06-08/py_hardcode_check.txt` — check 4 evidence
- `knowledge/qa/evidence/executable-anvil-extraction-contract-language-decoupling-2026-06-08/pytest_full.txt` — check 5 evidence
- `knowledge/qa/evidence/executable-anvil-extraction-contract-language-decoupling-2026-06-08/changed_files.txt` — check 6 evidence

### Files Created or Modified (Code)
- None (QA step — verification only)

### Decisions Made
- Used `git diff HEAD~1 --name-only` instead of `git diff --cached --name-only` for scope guard check, because DEV already committed (no staged changes); the commit diff is the authoritative source

### Flags for CEO
- None

### Flags for Next Step
- None

---

## Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/anvil/.bellows-worktrees/anvil-extraction-contract-language-decoupling-2026-06-08/knowledge/qa/evidence/executable-anvil-extraction-contract-language-decoupling-2026-06-08/
Files verified: 5
```
