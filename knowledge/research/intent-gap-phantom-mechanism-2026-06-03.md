# Anvil — Intent-Gap Phantom-Function Mechanism

**Date:** 2026-06-03 | **Diagnostic source:** `diagnostic-intent-gap-phantom-mechanism-2026-06-03.md`

## Executive Summary

The phantom-function mechanism is **uniformly (a1) — stale chunk rows in surviving files**. All five investigated phantoms have orphaned `code_chunks` rows that were never deleted when their functions were removed from the codebase. The extractor upserts present functions but never prunes removed ones. The scorer then indiscriminately scores ALL non-module chunks (no freshness filter), producing `health_scores` rows for the current cycle. `find_intent_gaps()` queries those current-cycle health_scores joined to code_chunks — surfacing phantoms. Mechanism **(b) (git-history-driven scoring independent of chunks)** is **not implicated**: the surfaced identity always comes from the `code_chunks` row, not from `git_changes`. Mechanism **(a2) (orphan from a deleted file)** could not be tested — the plan hypothesized `rates_grid`/`web/rates.py` as a deleted-file case, but the file still exists on disk (rebuilt in later commits); `rates_grid` was deleted from the surviving file, making it (a1). No (a2) specimen exists in this sample, though the codebase is structurally vulnerable to (a2) as well (no file-set reconciliation in SCAN).

---

## (1) Schema Binding

### Tables confirmed

```
projects, sqlite_sequence, code_chunks, chunk_fingerprints,
chunk_symbol_bindings, chunk_dependencies, chunk_similarities,
git_changes, test_results, health_scores, cycle_reports,
functional_roles, chunk_provenance, best_practices
```

### `code_chunks` columns (verbatim from PRAGMA)

| cid | name | type | notnull | dflt_value | pk |
|---|---|---|---|---|---|
| 0 | id | INTEGER | 0 | | 1 |
| 1 | project_id | INTEGER | 1 | | 0 |
| 2 | file_path | TEXT | 1 | | 0 |
| 3 | chunk_type | TEXT | 1 | | 0 |
| 4 | name | TEXT | 1 | | 0 |
| 5 | content | TEXT | 1 | | 0 |
| 6 | content_hash | TEXT | 1 | | 0 |
| 7 | start_line | INTEGER | 1 | | 0 |
| 8 | end_line | INTEGER | 1 | | 0 |
| 9 | parent_chunk_id | INTEGER | 0 | | 0 |
| 10 | created_at | TEXT | 1 | datetime('now') | 0 |
| 11 | updated_at | TEXT | 1 | datetime('now') | 0 |
| 12 | cycle_id | INTEGER | 0 | | 0 |
| 13 | structural_metadata | TEXT | 0 | | 0 |
| 14 | functional_role | TEXT | 0 | | 0 |

**Scan/cycle-stamp columns present:** `cycle_id`, `updated_at`
**Scan/cycle-stamp columns ABSENT:** `last_seen_cycle`, `deleted_at`, `scan_cycle`, `scan_id`, `cycle_number`, `is_current`, any active/alive flag. The `cycle_id` records which cycle *created* the row; it is never updated on re-scan. There is no mechanism to distinguish a live chunk from a dead one.

### `git_changes` columns

| cid | name | type |
|---|---|---|
| 0 | id | INTEGER |
| 1 | project_id | INTEGER |
| 2 | file_path | TEXT |
| 3 | commit_hash | TEXT |
| 4 | commit_date | TEXT |
| 5 | commit_message | TEXT |
| 6 | author | TEXT |
| 7 | created_at | TEXT |

### `health_scores` columns

| cid | name | type |
|---|---|---|
| 0 | id | INTEGER |
| 1 | chunk_id | INTEGER |
| 2 | volatility_score | REAL |
| 3 | coverage_score | REAL |
| 4 | complexity_score | REAL |
| 5 | coupling_score | REAL |
| 6 | staleness_score | REAL |
| 7 | composite_score | REAL |
| 8 | cycle_id | INTEGER |
| 9 | created_at | TEXT |

### `cycle_reports` columns

| cid | name | type |
|---|---|---|
| 0 | id | INTEGER |
| 1 | project_id | INTEGER |
| 2 | cycle_number | INTEGER |
| 3 | started_at | TEXT |
| 4 | completed_at | TEXT |
| 5 | files_scanned | INTEGER |
| 6 | chunks_extracted | INTEGER |
| 7 | chunks_scored | INTEGER |
| 8 | findings_count | INTEGER |
| 9 | report_path | TEXT |
| 10 | created_at | TEXT |

**Note:** `cycle_reports` has no `cycle_date` column. The BACKLOG's informal name is incorrect. The date is derivable from `started_at`.

**Most recent cycle:** id=19, cycle_number=19, started_at=2026-06-03T02:13:10 UTC. The `cycle_reports.id` and `cycle_number` are numerically identical (1:1 mapping confirmed for recent 5 cycles).

---

## (2) Per-Phantom Chunk Existence + Freshness

| Phantom | File | Plan class | Actual class | Row exists? | chunk_id | cycle_id (creation) | updated_at | Produced by cycle-19 SCAN? |
|---|---|---|---|---|---|---|---|---|
| `rates_grid` | web/rates.py | deleted-file | **deleted-func** (file rebuilt) | Yes | 4114 | 1 | 2026-04-04 | No |
| `import_contract_setup` | web/gap_dashboard.py | renamed | renamed | Yes | 4051 | 1 | 2026-04-01 | No |
| `_import_contract_setup_section` | web/gap_dashboard.py | (new name) | (new name) | Yes | 5384 | 6 | 2026-04-03 | No |
| `record_response` | web/action_queue.py | deleted-func | deleted-func | Yes | 3777 | 1 | 2026-03-30 | No |
| `_auto_route_after_response` | web/action_queue.py | deleted-func | deleted-func | Yes | 3778 | 1 | 2026-03-30 | No |
| `confirm_carrier` | web/action_queue.py | deleted-func | deleted-func | Yes | 3775 | 1 | 2026-03-30 | No |

**Key findings:**
- All 5 phantom chunk rows exist. None were created or updated by cycle 19 (all cycle_id ≤ 6, all updated_at ≤ 2026-04-04).
- The rename case shows **dual-chunk-id proof**: old `import_contract_setup` (id 4051, cycle 1) coexists with new `_import_contract_setup_section` (id 5384, cycle 6). The extractor created the new chunk but never deleted the old one.
- `rates_grid` was classified in the plan as a "deleted file (whole file removed in Phase 4 kill-dead-rate-routes)". **Correction:** `web/rates.py` still exists on disk (443 lines). It was rebuilt in commit `769e420` ("rebuild /rates as tariff document browser"). The function `rates_grid` was removed during rebuilding, but the file itself survives. This reclassifies `rates_grid` from (a2) to **(a1)**.

**Despite stale chunk rows, ALL 5 phantoms have `health_scores` for cycle 19:**

| Phantom | chunk_id | hs.cycle_id | volatility | coverage | composite |
|---|---|---|---|---|---|
| `rates_grid` | 4114 | 19 | 0.0 | 1.0 | 0.7751 |
| `import_contract_setup` | 4051 | 19 | 0.6667 | 1.0 | 0.604 |
| `record_response` | 3777 | 19 | 0.1667 | 1.0 | 0.7218 |
| `_auto_route_after_response` | 3778 | 19 | 0.1667 | 1.0 | 0.5621 |
| `confirm_carrier` | 3775 | 19 | 0.1667 | 1.0 | 0.5501 |

The scorer created fresh health_scores for these orphan chunks in cycle 19. This is *how* they enter `find_intent_gaps`.

**Codebase verification (read-only grep against invoice-pulse):**
- `def rates_grid` — not found in `web/rates.py` or anywhere in current source
- `def import_contract_setup` — not found (renamed to `_import_contract_setup_section`)
- `def _import_contract_setup_section` — found at `web/gap_dashboard.py:3203` (the live replacement)
- `def record_response`, `def _auto_route_after_response`, `def confirm_carrier` — none found in current source

---

## (3) `find_intent_gaps()` Trace

**Location:** `src/lab.py:416`

### Query structure (coverage-gap bucket, lines 468-479)

```sql
SELECT cc.id, cc.name, cc.file_path, cc.chunk_type, cc.functional_role,
       hs.composite_score, hs.volatility_score, hs.coverage_score
FROM health_scores hs
JOIN code_chunks cc ON hs.chunk_id = cc.id
WHERE hs.cycle_id = ?            -- latest_cycle_id (= 19)
  AND cc.project_id = ?
  AND hs.coverage_score >= 0.8   -- "zero coverage" threshold
  AND cc.chunk_type != 'test_case'
  AND cc.file_path NOT LIKE 'tests/%'
ORDER BY hs.volatility_score DESC, hs.composite_score DESC
LIMIT ?
```

Coupling-hotspot and complexity-hotspot buckets follow the same pattern: `health_scores JOIN code_chunks` filtered by `hs.cycle_id = latest_cycle_id`.

### Join graph

```
health_scores (hs)
    │
    ├── ON hs.chunk_id = cc.id ──► code_chunks (cc)
    │
    └── WHERE hs.cycle_id = MAX(hs.cycle_id)  [latest cycle]
```

### Answers

**(a) FROM table:** `health_scores`, joined to `code_chunks` on `hs.chunk_id = cc.id`.

**(b) Surfaced identity source:** The function name (`cc.name`) and file path (`cc.file_path`) come **FROM `code_chunks`**, not from `git_changes` or any history table. Mechanism (b) is not implicated.

**(c) Freshness predicate:** **NONE.** There is:
- No join to a scan-set or current-file list
- No `last_seen_cycle = current` filter
- No `os.path.isfile()` check
- No `chunk.updated_at >= cycle.started_at` check
- No `chunk.cycle_id = latest_cycle_id` check

The query trusts that every chunk with a current-cycle `health_scores` row is real. But the scorer creates health_scores for ALL chunks (see §4), so this trust is misplaced.

---

## (4) SCAN Orphan Handling

### (a1) Surviving file — function removed/renamed

**Extractor path** (`src/extractor.py:59-115`):
```python
for module_chunk in py_modules:
    abs_path = os.path.join(project_path, module_chunk["file_path"])
    if not os.path.isfile(abs_path):
        continue                       # skip missing files — but DON'T delete their chunks

    parsed_chunks = python_parser.parse_file(abs_path)
    for chunk_dict in parsed_chunks:
        existing = _find_existing_chunk(...)
        if existing:
            if existing["content_hash"] == chunk_dict["content_hash"]:
                pass                   # unchanged — skip
            else:
                _update_chunk(...)     # content changed — update in place
        else:
            db.create_chunk(...)       # new function — insert
```

**The extractor iterates ONLY over functions found by `python_parser.parse_file()`.** If a function was removed from the file, it simply does not appear in `parsed_chunks`. The old chunk row is never visited, never deleted, never flagged. It persists indefinitely.

The rename case is instructive: when `import_contract_setup` was renamed to `_import_contract_setup_section`, the parser returned the new name. The extractor couldn't find an existing chunk with the new name, so it created a new row (id 5384). The old row (id 4051, name `import_contract_setup`) was never touched — it's an orphan.

### (a2) Deleted file — no file-set reconciliation

**Scanner path** (`src/scanner.py:44-48`):
```python
discovered = discover_files(project_path, EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)
new_files, changed_files, unchanged_files = detect_changes(conn, project_id, discovered)
register_file_chunks(conn, project_id, new_files, changed_files, cycle_id=None)
```

`discover_files()` walks only current on-disk files. `detect_changes()` checks discovered files against existing module chunks, classifying them as new/changed/unchanged. **It never queries for module chunks whose files no longer exist on disk.** There is no set-difference operation, no reconciliation pass, no DELETE for files that disappeared.

In the extractor, `if not os.path.isfile(abs_path): continue` — missing files are skipped, not cleaned up. Their module chunks and all child function chunks persist.

**(For this diagnostic, the (a2) case was not testable — see §2 correction on `rates_grid`.)**

### Scorer amplification

**Scorer path** (`src/scorer.py:41-46`):
```python
cur = conn.execute(
    "SELECT * FROM code_chunks WHERE project_id = ? AND chunk_type != 'module'",
    (project_id,),
)
chunks = cur.fetchall()
```

The scorer loads ALL non-module chunks. No filter on `cycle_id`, no `os.path.isfile()` check. It scores every chunk and writes a `health_scores` row with the current `cycle_id`. This is the amplifier: stale chunks that would otherwise be invisible (because `find_intent_gaps` filters on `hs.cycle_id = latest`) are given fresh health_scores every cycle, keeping them permanently visible.

---

## (5) Verdict — Truth Table + Mechanism + Fix Surface

| Phantom | Actual class | Chunk exists & stale? | Surfaced via chunk or git-history? | Mechanism |
|---|---|---|---|---|
| `rates_grid` | deleted-func (file rebuilt) | Yes — cycle_id=1, updated 2026-04-04 | Chunk (code_chunks → health_scores) | **(a1)** |
| `import_contract_setup` | renamed | Yes — cycle_id=1, updated 2026-04-01 | Chunk | **(a1)** |
| `record_response` | deleted-func | Yes — cycle_id=1, updated 2026-03-30 | Chunk | **(a1)** |
| `_auto_route_after_response` | deleted-func | Yes — cycle_id=1, updated 2026-03-30 | Chunk | **(a1)** |
| `confirm_carrier` | deleted-func | Yes — cycle_id=1, updated 2026-03-30 | Chunk | **(a1)** |

### Aggregate verdict

**Across all five phantoms, mechanism (a1) is the sole confirmed cause.** The extractor upserts present functions but never prunes removed ones from surviving files. The scorer then scores all chunks indiscriminately, and `find_intent_gaps()` has no freshness gate. The mechanism is uniform across all phantom classes in this sample.

**Mechanism (b) is not implicated.** The surfaced identity always comes from `code_chunks`, not from `git_changes`. Git history feeds the volatility *score* but does not independently surface function names.

**Mechanism (a2) could not be tested** — the hypothesized deleted-file specimen (`rates_grid`/`rates.py`) turned out to be a surviving file. However, the code is structurally vulnerable to (a2): the scanner has no file-set reconciliation, and the extractor skips missing files without cleaning up their chunks.

### Fix surface mapping

| Mechanism | Fix surface | Notes |
|---|---|---|
| **(a1)** orphan in surviving file | **Option A:** Prune orphan chunks during EXTRACT — after parsing a file, DELETE chunk rows for that file whose names were not in the parsed set. **Option B:** Add a chunk-existence/freshness join in `find_intent_gaps()` (e.g., require `cc.updated_at >= cycle.started_at` or add a `last_seen_cycle` column and filter on it). | Option A fixes the root cause; Option B is a filter-level workaround. |
| **(a2)** orphan from deleted file | **File-set reconciliation during SCAN** — after `discover_files()`, compute the set of module chunks in DB minus the set of discovered files, and DELETE (or flag) the orphans and their children. | A prune-during-EXTRACT fix alone would **MISS** (a2) because deleted files are never re-parsed. The reconciliation must happen at the SCAN level, where the full file set is known. |
| **(b)** git-history surfacing | **Chunk-existence join** in `find_intent_gaps()` — the only fix that helps, since the identity wouldn't come from chunks at all. | Not confirmed in this diagnostic, but the query should have this guard regardless. |

**Recommended approach:** Fix (a1) at the EXTRACT level (prune orphans per-file after parsing) AND add file-set reconciliation at the SCAN level to cover (a2). Optionally add a defensive freshness join in `find_intent_gaps()` as belt-and-suspenders.

---

## (6) Methodology Notes

### Assumptions
- `cycle_reports.id` == `cycle_number` — confirmed for the 5 most recent cycles but not guaranteed by schema constraint.
- `code_chunks.cycle_id` records the cycle that *created* the row. It is not updated on re-scan or re-extraction. This was inferred from the data (all 5 phantoms have cycle_id=1 despite 19 cycles), not from an explicit code comment.
- Volatility scoring uses `git_changes` keyed by `file_path`, not by chunk-level identity. A file-level commit count is attributed equally to all chunks in that file. This means a phantom in a file that still gets commits will show non-zero volatility even though the phantom function no longer exists.

### Edge cases that could mislead
- **Function name reuse across files:** A function named `rates_grid` in a different file would be a separate chunk row. The query here filtered by `file_path` to avoid this.
- **Rename producing genuinely new row:** Confirmed — the rename case (`import_contract_setup` → `_import_contract_setup_section`) produced a new chunk_id (5384) while the old chunk_id (4051) persists. The extractor matches by `(project_id, file_path, name, chunk_type)`, so a rename always creates a new row and orphans the old one.
- **Content-hash collision:** Theoretically, if a renamed function had the same content_hash as the old name, the extractor would still create a new row because the name differs in the dedup lookup. The old row would still be orphaned.
- **`rates_grid` misclassification:** The plan hypothesized `rates_grid` as a deleted-file (a2) case. Investigation revealed `web/rates.py` was rebuilt (443 lines), not deleted. Commit `769e420` ("rebuild /rates as tariff document browser") recreated the file without `rates_grid`. This reclassified the phantom from (a2) to (a1) and left (a2) untested.

### What could not be determined from DB + source alone
- Whether any truly deleted files exist in the DB (would require comparing all module-chunk file_paths against the current file tree — a valid follow-up diagnostic).
- Whether the `cycle_id` column on `code_chunks` was intended as a `created_at_cycle` or a `last_seen_cycle` — the code never updates it after creation.
