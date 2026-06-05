# Anvil Dev Log — Orphan-Chunk Reconciliation (Deleted-File Prune + Bypass-Surface Freshness Filters)

**Date:** 2026-06-05 | **Agent:** Anvil Developer | **Plan:** `executable-anvil-orphan-chunk-reconciliation-2026-06-05.md` | **Blueprint:** `knowledge/architecture/orphan-chunk-reconciliation-blueprint-2026-06-05.md`

## Implementation Summary

Implemented the SA blueprint exactly: (1) pre-prune timestamped backup, (2) deleted-file orphan prune during SCAN, and (3) freshness filters on the three bypass surfaces (`find_clone_candidates`, `find_best_practice_deviations`, `generate_specialist_update_data`). The filter was marked INCLUDED by the blueprint (confirmed by CEO).

## Changes Made

### 1. Pre-Prune Backup + Deleted-File Orphan Prune (`src/scanner.py`)

- Added `prune_deleted_file_orphans(conn, project_id, on_disk_paths)` function
- Hooked into `scan_project()` after `discover_files()`, before `detect_changes()` — earliest point with the on-disk file set
- Backup: creates `{ANVIL_ROOT}/backups/anvil-backup-{YYYYMMDD-HHMMSS}.db` via `shutil.copy2`, only when orphans exist
- Prune: `DELETE FROM code_chunks WHERE project_id = ? AND file_path IN (orphan_fps)` — catches both modules and children for deleted files
- Cascade handles all dependent rows (confirmed by blueprint §3 and new test)
- Idempotent: no orphans → early return, no backup, no-op
- Logging: INFO-level log of backup creation and prune counts (modules, children, sample IDs)
- New imports: `logging`, `shutil`, `ANVIL_DB_PATH`, `ANVIL_ROOT`

### 2. Freshness Filter — `find_clone_candidates` (`src/lab.py:189`)

- Added `AND a.last_seen_cycle = ? AND b.last_seen_cycle = ?` to the WHERE clause
- Parameters: `(cycle_id, project_id, cycle_id, cycle_id)` — both sides filtered
- No signature change (already receives `cycle_id`)

### 3. Freshness Filter — `find_best_practice_deviations` (`src/lab.py:316`)

- **Signature change:** `(conn, project_id)` → `(conn, project_id, cycle_id)`
- Added `AND last_seen_cycle = ?` to the query
- Updated call site in `run_lab()` (line 66)

### 4. Freshness Filter — `generate_specialist_update_data` (`src/lab.py:762`)

- **Signature change:** `(conn, project_id)` → `(conn, project_id, cycle_id)`
- Added `AND last_seen_cycle = ?` (or `AND cc.last_seen_cycle = ?` for JOINed queries) to all 7 queries:
  - Chunk type counts, dep count, sim count, avg composite, high risk count, top 10 complex, top 10 coupled
- Updated call site in `run_lab()` (line 90)

### 5. Test Updates

- **`tests/test_scanner.py`:** Added 4 new tests — `test_prune_removes_orphan_chunks`, `test_prune_creates_backup`, `test_prune_idempotent`, `test_prune_no_orphans_no_backup`
- **`tests/test_lab.py`:** Added 4 new tests — `test_clone_candidates_excludes_stale_chunks`, `test_clone_candidates_includes_fresh_pair`, `test_best_practice_deviations_excludes_stale`, `test_specialist_update_data_excludes_stale`. Updated `lab_project` fixture and `test_cycle_report_includes_untested_complexity` to set `last_seen_cycle=1` on all chunks. Updated `generate_specialist_update_data` call sites to pass `cycle_id`.
- **`tests/test_db.py`:** Added `test_cascade_delete_removes_all_dependent_rows` — verifies CASCADE on all 6 dependent tables and SET NULL on `target_chunk_id`/`parent_chunk_id`
- **`tests/test_detector.py`:** Updated 3 existing tests (`test_find_deviations`, `test_no_deviations_for_compliant_chunk`, `test_unclassified_chunks_skipped`) to pass `cycle_id` and set `last_seen_cycle` on chunks

## Test Results

```
238 passed in 2.36s
```

All tests green. No pre-existing failures.

---

## Output Receipt

**Agent:** Anvil Developer
**Step:** Step 2
**Status:** Complete

### What Was Done
Implemented the orphan-chunk reconciliation blueprint: deleted-file prune in scanner.py (with pre-prune backup and logging), freshness filters on all three bypass surfaces in lab.py, and comprehensive test coverage across 4 test files.

### Files Deposited
- `knowledge/development/orphan-chunk-reconciliation-2026-06-05.md` — this implementation log

### Files Created or Modified (Code)
- `src/scanner.py` — added `prune_deleted_file_orphans()` function and hook in `scan_project()`; added imports for logging, shutil, ANVIL_DB_PATH, ANVIL_ROOT
- `src/lab.py` — added `last_seen_cycle` freshness filter to `find_clone_candidates`, `find_best_practice_deviations` (+ signature change), `generate_specialist_update_data` (+ signature change); updated call sites in `run_lab()`
- `tests/test_scanner.py` — 4 new prune tests (orphan removal, backup, idempotency, no-op)
- `tests/test_lab.py` — 4 new freshness filter tests; updated lab_project fixture and existing calls for new signatures
- `tests/test_db.py` — 1 new cascade-on-delete test
- `tests/test_detector.py` — updated 3 existing tests for `find_best_practice_deviations` signature change

### Decisions Made
- Placed backup inside `prune_deleted_file_orphans()` conditional on orphans existing (per blueprint §4)
- Guarded `shutil.copy2` with `os.path.isfile(ANVIL_DB_PATH)` to handle in-memory test DBs gracefully
- Used `set` difference for O(1) orphan detection (per blueprint §2)

### Flags for CEO
- None

### Flags for Next Step
- QA should verify cascade on a DB copy, run full cycle pipeline, and confirm the prune + filter work end-to-end
- The `backups/` directory will be created automatically on first prune; it is gitignored implicitly (no .db files tracked)
- The `find_best_practice_deviations` and `generate_specialist_update_data` signature changes affect only `run_lab()` call sites — no external callers
