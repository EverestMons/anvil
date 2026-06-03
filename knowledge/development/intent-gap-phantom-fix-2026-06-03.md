# Anvil — DEV Log: Intent-Gap Phantom Fix (last_seen_cycle)

**Date:** 2026-06-03 | **Blueprint:** `knowledge/architecture/intent-gap-phantom-fix-blueprint-2026-06-03.md`

## Implementation Summary

Implemented philosophy A (soft-delete / freshness stamp) for phantom-function elimination. Added `last_seen_cycle INTEGER` column to `code_chunks`, stamped during extraction, and scoped the scorer and `find_intent_gaps()` to only process current-snapshot chunks.

## Changes

### 1. Schema Migration — `src/db.py`

- Added `last_seen_cycle INTEGER` to the `CREATE TABLE IF NOT EXISTS code_chunks` DDL (line ~49)
- Added idempotent `ALTER TABLE` migration after the existing `functional_role` migration (try/except for OperationalError)

### 2. Write-Path Stamping — `src/extractor.py`

Four stamping paths implemented in `extract_project()`:

- **Path A (module chunk):** After `os.path.isfile()` check, UPDATE module chunk's `last_seen_cycle = cycle_id`
- **Path B (new function chunk):** Added `last_seen_cycle=cycle_id` to `db.create_chunk()` kwargs
- **Path C (changed function chunk):** Added `cycle_id` parameter to `_update_chunk()`, included `last_seen_cycle` in UPDATE SQL
- **Path D (unchanged function chunk — the trap):** Added explicit `UPDATE code_chunks SET last_seen_cycle = ? WHERE id = ?` in the content_hash-match branch

### 3. Scorer Scoping — `src/scorer.py`

Changed the main chunk-loading query (line ~42) from:
```sql
SELECT * FROM code_chunks WHERE project_id = ? AND chunk_type != 'module'
```
to:
```sql
SELECT * FROM code_chunks WHERE project_id = ? AND chunk_type != 'module' AND last_seen_cycle = ?
```

### 4. find_intent_gaps Guard — `src/lab.py`

Added `AND cc.last_seen_cycle = ?` predicate to all three query buckets:
- Coverage gaps (line ~473)
- Coupling hotspots (line ~529)
- Complexity hotspots (line ~583)

## Tests

### Updated existing tests (2)
- `tests/test_lab.py::test_find_intent_gaps_returns_required_keys` — added `last_seen_cycle=1` to test chunk
- `tests/test_scorer.py::test_score_project_end_to_end` — added `last_seen_cycle=1` to all 3 non-module chunks in `scored_project` fixture

### New tests (10)
- `tests/test_db.py::test_last_seen_cycle_column_exists` — verifies PRAGMA shows the column
- `tests/test_db.py::test_last_seen_cycle_migration_idempotent` — double init_db doesn't error
- `tests/test_db.py::test_create_chunk_with_last_seen_cycle` — kwarg sets value
- `tests/test_db.py::test_create_chunk_without_last_seen_cycle_defaults_null` — default is NULL
- `tests/test_extractor.py::test_extract_stamps_last_seen_cycle_on_new_chunks` — Path B
- `tests/test_extractor.py::test_extract_stamps_last_seen_cycle_on_module_chunks` — Path A
- `tests/test_extractor.py::test_extract_stamps_unchanged_chunks` — Path D (the trap)
- `tests/test_extractor.py::test_extract_does_not_stamp_missing_file_chunks` — Path E
- `tests/test_scorer.py::test_scorer_excludes_unstamped_chunks` — scorer scoping
- `tests/test_lab.py::test_find_intent_gaps_excludes_stale_chunks` — lab guard

### Test results
**229 passed, 0 failed** (was 219 pre-change)

---

## Output Receipt

**Agent:** Anvil Developer
**Step:** Step 2
**Status:** Complete

### What Was Done
Implemented the `last_seen_cycle` phantom-function fix per the SA blueprint. Added the column, stamped it in the extractor across all 4 paths (including the unchanged-chunk trap), scoped the scorer, and added the belt-and-suspenders guard to `find_intent_gaps()`. All 229 tests pass.

### Files Deposited
- `anvil/knowledge/development/intent-gap-phantom-fix-2026-06-03.md` — this implementation log

### Files Created or Modified (Code)
- `src/db.py` — added `last_seen_cycle INTEGER` to CREATE TABLE and idempotent ALTER TABLE migration
- `src/extractor.py` — 4 stamping paths in `extract_project()` + `cycle_id` param in `_update_chunk()`
- `src/scorer.py` — `AND last_seen_cycle = ?` filter on main chunk query
- `src/lab.py` — `AND cc.last_seen_cycle = ?` guard on all 3 `find_intent_gaps` query buckets
- `tests/test_db.py` — 4 new tests for migration and column usage
- `tests/test_extractor.py` — 4 new tests for stamping paths
- `tests/test_scorer.py` — 1 new test for scorer scoping + fixture update
- `tests/test_lab.py` — 1 new test for lab guard + fixture update

### Decisions Made
- Used `conn.execute()` directly for Path D stamping (lightweight single-column UPDATE) rather than routing through a helper function

### Flags for CEO
- None

### Flags for Next Step
- QA should verify the five phantom chunk_ids (4114, 4051, 3777, 3778, 3775) are excluded post-fix per blueprint §7
- QA should run a full cycle to validate end-to-end phantom elimination
