# Anvil — SA Blueprint: Intent-Gap Phantom Fix (last_seen_cycle)

**Date:** 2026-06-03 | **Agent:** Anvil Systems Analyst | **Plan:** `executable-anvil-intent-gap-phantom-fix-2026-06-03.md`

**CEO-approval flag:** The `last_seen_cycle` column addition to `code_chunks` is a schema deviation from the original PROJECT_BRIEF data model. **Pre-approved by CEO (2026-06-03)** — no re-escalation required.

## Summary

The (a2) population is **1,599 orphan module chunks** (files that no longer exist on disk), of which **17 are Python files** producing **252 orphan function/class/test_case child chunks**. However, 16 of the 17 Python orphans are test files (filtered by `file_path NOT LIKE 'tests/%'` in `find_intent_gaps`), leaving only **1 production file** (`web/training.py`, 20 child chunks) as an active (a2) phantom producer. **Recommendation: defer SCAN file-set reconciliation.** The `last_seen_cycle` stamping naturally handles (a2) because the extractor skips missing files (`if not os.path.isfile: continue`) and therefore never stamps their chunks — they remain at `last_seen_cycle = NULL` and are excluded by the scorer and lab guards. A BACKLOG note should capture the full reconciliation (module-chunk cleanup for deleted files) as a future DB hygiene task, not a correctness fix.

---

## (0) (a2) Population Sizing

**Query:** All `code_chunks` module file_paths for project_id=1 MINUS files currently on disk (using Anvil's scanner exclusion rules).

| Category | Count |
|---|---|
| DB module chunks | 4,029 |
| On-disk files | 2,435 |
| **Orphan module chunks (file gone)** | **1,599** |
| — .py files | 17 |
| — .json files | 1,560 |
| — other (md, html) | 22 |

**Python orphan child chunks:** 252 total across 17 deleted .py files. Only `web/training.py` (20 child chunks) is a production file; the other 16 are test files excluded from `find_intent_gaps` by the `NOT LIKE 'tests/%'` filter.

**Recommendation:** Defer file-set reconciliation to a BACKLOG item. The `last_seen_cycle` approach handles (a2) at the filter level — orphan chunks from deleted files are never stamped by the extractor (it `continue`s on missing files), so they remain `last_seen_cycle = NULL` and are excluded from scoring and findings. The 1,560 JSON and 22 other non-Python module chunks have no function-level children and are already excluded from scoring (`chunk_type != 'module'`). The only cost of deferral is ~1,600 inert rows in `code_chunks` — negligible for SQLite.

---

## (1) Schema Migration

### DDL

```sql
ALTER TABLE code_chunks ADD COLUMN last_seen_cycle INTEGER;
```

- **Nullable, default NULL.** Rationale: existing rows have never been stamped. NULL clearly signals "never confirmed by the current pipeline version" and makes the transition explicit — `WHERE last_seen_cycle = X` naturally excludes all pre-migration rows until the first post-fix scan stamps them.
- **No index required at this time.** The column is used in WHERE clauses alongside `project_id` (already indexed) and `chunk_type`. If query plans degrade, add `CREATE INDEX idx_code_chunks_last_seen ON code_chunks(last_seen_cycle)` later.

### Migration placement

In `src/db.py`, inside `init_db()`, after the existing `ALTER TABLE code_chunks ADD COLUMN functional_role TEXT` migration block (line ~252-257). Follow the existing idempotent pattern:

```python
# Migration: add last_seen_cycle column if not present
try:
    conn.execute("ALTER TABLE code_chunks ADD COLUMN last_seen_cycle INTEGER")
    conn.commit()
except sqlite3.OperationalError:
    pass  # Column already exists
```

### CREATE TABLE update

Also update the `CREATE TABLE IF NOT EXISTS code_chunks` DDL block (line ~35-49) to include `last_seen_cycle INTEGER` so that fresh databases get the column from the start, without relying on the migration path.

---

## (2) Write-Path Stamping

**Stamp location: `src/extractor.py`, inside `extract_project()`.**

The extractor is the correct stamping point because:
- It receives `cycle_id` as a parameter (the scanner does not).
- It iterates ALL module chunks for the project, including unchanged files.
- It visits every function/class/method/test_case chunk within each file.

### Stamping rules (4 paths)

**Path A — Module chunk (file exists on disk):** After the `if not os.path.isfile(abs_path): continue` guard (line ~61), stamp the module chunk:
```python
conn.execute(
    "UPDATE code_chunks SET last_seen_cycle = ? WHERE id = ?",
    (cycle_id, module_chunk["id"]),
)
```

**Path B — New function/class chunk (insert):** Add `last_seen_cycle=cycle_id` to the `db.create_chunk()` kwargs (line ~99-111). Since `create_chunk` uses `**kwargs`, this requires no signature change.

**Path C — Changed function/class chunk (update):** Add `last_seen_cycle` to the `_update_chunk()` SQL (line ~212-219). The UPDATE statement becomes:
```python
conn.execute(
    "UPDATE code_chunks SET content = ?, content_hash = ?, "
    "start_line = ?, end_line = ?, parent_chunk_id = ?, updated_at = ?, "
    "last_seen_cycle = ? WHERE id = ?",
    (chunk_dict["content"], chunk_dict["content_hash"],
     chunk_dict["start_line"], chunk_dict["end_line"],
     parent_chunk_id, now, cycle_id, chunk_id),
)
```

Note: `_update_chunk()` currently does not receive `cycle_id`. The DEV must add it as a parameter.

**Path D — Unchanged function/class chunk (content_hash match, THE TRAP):** Currently this branch (line ~87-91) does no database write — it just captures `chunk_id`. The DEV must add an explicit UPDATE:
```python
if existing["content_hash"] == chunk_dict["content_hash"]:
    chunk_id = existing["id"]
    conn.execute(
        "UPDATE code_chunks SET last_seen_cycle = ? WHERE id = ?",
        (cycle_id, chunk_id),
    )
```

**Path E — Missing file (extractor skips with `continue`):** No stamp. This is the (a2) defense — chunks for deleted files never get stamped, so `last_seen_cycle` stays NULL (or whatever its last value was before the file was deleted), and they are excluded from scoring.

### What does NOT get stamped

- Module chunks for files that no longer exist on disk (skipped by extractor).
- Function/class chunks belonging to files that no longer exist (their module is skipped → their children are never visited).
- Function/class chunks that were deleted from a surviving file (the parser doesn't return them → they are never visited in the per-chunk loop).
- These are exactly the phantom population. Their `last_seen_cycle` remains NULL (or stale from a prior cycle), and the scorer/lab filters exclude them.

---

## (3) Backfill / Cold-Start

**Decision: NO explicit backfill. Rely on the first post-fix scan.**

### Rationale

1. A backfill would need to re-parse every file and match functions against chunk rows — essentially re-running the extractor. Simpler and more reliable to just run a cycle.
2. The migration runs inside `init_db()`, which is called at the start of every `run_cycle()`. So the temporal gap between "migration applied" and "first post-fix scan stamps live chunks" is zero in normal operation — they happen in the same cycle.
3. After migration, all chunks have `last_seen_cycle = NULL`. The first post-fix cycle (cycle 20) will:
   - EXTRACT stamps all live chunks with `last_seen_cycle = 20`
   - SCORE filters on `last_seen_cycle = 20` → only scores live chunks
   - LAB queries cycle-20 health_scores → only surfaces live chunks
4. Pre-fix cycles' health_scores (1-19) are preserved in full, including phantom scores — this is consistent with philosophy A (non-destructive).

### Interim window behavior

If `find_intent_gaps()` is called *between* migration and the first post-fix cycle (e.g., manually, not via `run_cycle`): the belt-and-suspenders guard (§5) would filter on `cc.last_seen_cycle = latest_cycle_id`. Since no chunks have `last_seen_cycle = 19` (the column didn't exist during cycle 19), all findings would be filtered out — returning an empty list. This is acceptable: the correct behavior is to run a cycle first. To avoid surprise, the DEV may add a log warning in `find_intent_gaps()` if the count of stamped chunks is zero.

---

## (4) Scorer Scoping

### Change location: `src/scorer.py:41-46`

**Current:**
```python
cur = conn.execute(
    "SELECT * FROM code_chunks WHERE project_id = ? AND chunk_type != 'module'",
    (project_id,),
)
```

**New:**
```python
cur = conn.execute(
    "SELECT * FROM code_chunks WHERE project_id = ? AND chunk_type != 'module' "
    "AND last_seen_cycle = ?",
    (project_id, cycle_id),
)
```

Where `cycle_id` is the parameter already passed to `score_project(conn, project_name, cycle_id)`.

### "Current cycle" definition

`cycle_id` is the integer assigned in `run_cycle()` at `cycle.py:38` as `(MAX(cycle_number) + 1)`. It is passed through `extract_project(conn, project_name, cycle_id)` → stamping, then `score_project(conn, project_name, cycle_id)` → filtering. The same value is used for both stamping and filtering within a single cycle run, guaranteeing consistency.

### Unchanged chunk safety

Unchanged chunks ARE stamped with `last_seen_cycle = cycle_id` per Path D in §2. They will pass the `last_seen_cycle = cycle_id` filter. No legitimate chunks are stranded.

---

## (5) find_intent_gaps Guard (Belt-and-Suspenders)

### Change location: `src/lab.py`, all three query buckets inside `find_intent_gaps()`

**Coverage-gap query (~line 468-479) — add `AND cc.last_seen_cycle = ?`:**

```sql
SELECT cc.id, cc.name, cc.file_path, cc.chunk_type, cc.functional_role,
       hs.composite_score, hs.volatility_score, hs.coverage_score
FROM health_scores hs
JOIN code_chunks cc ON hs.chunk_id = cc.id
WHERE hs.cycle_id = ? AND cc.project_id = ?
  AND cc.last_seen_cycle = ?                    -- NEW: freshness guard
  AND hs.coverage_score >= 0.8
  AND cc.chunk_type != 'test_case'
  AND cc.file_path NOT LIKE 'tests/%'
ORDER BY hs.volatility_score DESC, hs.composite_score DESC
LIMIT ?
```

Parameters become: `(latest_cycle_id, project_id, latest_cycle_id, n_coverage)`.

**Apply the same `AND cc.last_seen_cycle = ?` predicate** to the coupling-hotspot query (~line 523-533) and the complexity-hotspot query (~line 577-588). Same parameter binding: `latest_cycle_id`.

### Why `cc.last_seen_cycle = latest_cycle_id` (not `IS NOT NULL`)

Using `= latest_cycle_id` is stricter than `IS NOT NULL`. It ensures the chunk was confirmed present during the *same* cycle whose health_scores we're reading. If a chunk was stamped in cycle 19 but the scorer is running cycle 20, the chunk must have been re-stamped in cycle 20 to appear. This catches a hypothetical bug where stamping runs but the chunk was actually deleted between cycles.

---

## (6) Cascade / Blast-Radius Check

### Philosophy A is non-destructive: confirmed

No DELETEs of any kind. The fix only:
- Adds a column (`last_seen_cycle`)
- Writes to that column during extraction
- Adds WHERE filters to scorer and lab queries

All existing data is preserved:
- `chunk_dependencies` — untouched
- `chunk_similarities` — untouched
- `chunk_symbol_bindings` — untouched
- `chunk_provenance` — untouched
- `health_scores` history (cycles 1-19) — untouched; phantom scores remain for historical queries

### Consumers that read `code_chunks` and might surface phantoms (not in scope, noted for future)

| Consumer | Location | Goes through health_scores? | Phantom risk | Action |
|---|---|---|---|---|
| `score_project` | scorer.py:42 | No (source query) | **Fixed in this plan** | — |
| `find_intent_gaps` (3 buckets) | lab.py:452,472,527,581 | Yes (cycle-filtered) | **Fixed in this plan** (belt-and-suspenders) | — |
| `find_staleness_alerts` | lab.py:216 | Yes (cycle-filtered) | **Transitively fixed** — scorer won't produce health_scores for phantoms post-fix | — |
| `find_near_clones` | lab.py:119 | Yes (cycle-filtered) | Transitively fixed | — |
| `find_co_change` | lab.py:149 | Yes (cycle-filtered) | Transitively fixed | — |
| `find_complexity_hotspots` | lab.py:243 | Yes (cycle-filtered) | Transitively fixed | — |
| `find_clone_candidates` | lab.py:193-194 | **No** (chunk_similarities) | Minor — dead chunks could appear as clone candidates | Defer |
| Role/chunk stats | lab.py:322, 763 | No | Minor — counts include dead chunks | Defer |
| `compute_fingerprints` | extractor.py:545 | No | Minor — computes fingerprints for dead chunks | Defer |
| `resolve_dependencies` | extractor.py:392 | No | Minor — resolves deps for dead chunks | Defer |
| `classify_project` | classifier.py:142 | No | Minor — classifies dead chunks | Defer |
| `compare_cycles` | cycle.py:174 | Yes (cycle-filtered) | Post-fix cycles are clean; pre-fix comparisons reflect historical data | OK |
| `get_cycle_summary` | cycle.py:97 | Yes (cycle-filtered) | Same as above | OK |

**Key observation:** All Lab finding functions that produce user-facing audit results go through `health_scores`, which is cycle-filtered. Since the scorer will only produce health_scores for stamped chunks post-fix, all finding functions are transitively fixed. The belt-and-suspenders guard on `find_intent_gaps` provides an extra layer for the highest-impact finding type.

The "Defer" consumers produce internal pipeline data (fingerprints, deps, classifications) or low-traffic stats sections in the cycle report. None produce phantom *findings* that would mislead the audit. They represent a DB hygiene opportunity, not a correctness bug.

---

## (7) How to Verify This Was Implemented Correctly

### Pre-cycle checks (after code changes, before running a cycle)

1. **Migration column exists:**
   ```sql
   PRAGMA table_info(code_chunks);
   ```
   Verify `last_seen_cycle` appears as an INTEGER column, nullable.

2. **All existing chunks have `last_seen_cycle = NULL`:**
   ```sql
   SELECT COUNT(*) FROM code_chunks WHERE last_seen_cycle IS NOT NULL;
   ```
   Expected: 0 (before first post-fix cycle).

### Post-cycle checks (after running cycle 20)

3. **Live chunks are stamped:**
   ```sql
   SELECT COUNT(*) FROM code_chunks
   WHERE project_id = 1 AND chunk_type != 'module' AND last_seen_cycle = 20;
   ```
   Should be > 0 and close to the total live non-module chunk count.

4. **The five named phantom chunk_ids are NOT stamped with the current cycle:**
   ```sql
   SELECT id, name, file_path, last_seen_cycle FROM code_chunks
   WHERE id IN (4114, 4051, 3777, 3778, 3775);
   ```
   All five should have `last_seen_cycle` either NULL or < 20.

5. **Phantom chunk_ids have NO cycle-20 health_scores:**
   ```sql
   SELECT chunk_id FROM health_scores
   WHERE cycle_id = 20 AND chunk_id IN (4114, 4051, 3777, 3778, 3775);
   ```
   Expected: 0 rows.

6. **`find_intent_gaps()` does not return the five phantoms:**
   Run `find_intent_gaps()` for cycle 20. Verify none of `rates_grid`, `import_contract_setup`, `record_response`, `_auto_route_after_response`, `confirm_carrier` appear in the results.

7. **Legitimate findings are preserved:**
   Compare cycle-20 `find_intent_gaps()` results against cycle-19 results (from `knowledge/research/anvil-findings-report-cycle19-2026-06-03.md` or the DB). All findings that were NOT in the known-phantom set should still appear. Count should be approximately cycle-19 count minus 5 (the phantoms). Small differences in ordering or threshold-boundary findings are acceptable.

8. **Module chunks for existing files are stamped:**
   ```sql
   SELECT COUNT(*) FROM code_chunks
   WHERE project_id = 1 AND chunk_type = 'module' AND last_seen_cycle = 20;
   ```
   Should match the count of on-disk files that the scanner discovers (~2,435).

---

## (8) Test Surface

### Files to update

| Test file | What to test | Notes |
|---|---|---|
| `tests/test_db.py` | Migration idempotency: call `init_db()` twice, verify `last_seen_cycle` column exists and no error on second call. Verify `create_chunk()` with `last_seen_cycle` kwarg works. | Follow existing pattern for structural_metadata/functional_role migration tests if they exist; otherwise add. |
| `tests/test_extractor.py` | **Path B (new chunk):** after extraction, new chunks have `last_seen_cycle = cycle_id`. **Path C (changed chunk):** update a chunk's content, re-extract, verify `last_seen_cycle` updated. **Path D (unchanged chunk, THE TRAP):** extract twice with same content, verify `last_seen_cycle` is stamped on the second run (not NULL). **Path A (module chunk):** verify module chunks for existing files get stamped. **Path E (missing file):** create a module chunk, delete the file, re-extract — verify its children's `last_seen_cycle` is NOT updated. | Path D is the most critical test — it covers the bug that caused the phantom problem. |
| `tests/test_scorer.py` | Verify scorer only scores chunks with `last_seen_cycle = cycle_id`. Create two chunks: one with `last_seen_cycle = cycle_id`, one with `last_seen_cycle = NULL`. After scoring, only the first should have a health_score for this cycle. | Contract change: scorer now requires `last_seen_cycle` to be set. |
| `tests/test_lab.py` | Verify `find_intent_gaps()` excludes chunks with `last_seen_cycle != latest_cycle_id`. Set up a stale chunk with a health_score but `last_seen_cycle = NULL` — verify it does not appear in results. | Contract change: lab now filters on freshness. |

### Contract changes to communicate

- **Scorer:** `score_project()` now requires that live chunks have `last_seen_cycle = cycle_id` set by the extractor. If the extractor hasn't run (or ran with a different cycle_id), the scorer will score 0 chunks. This is by design — the pipeline must run in order.
- **Lab:** `find_intent_gaps()` now filters on `cc.last_seen_cycle = latest_cycle_id`. This is a belt-and-suspenders guard; the primary defense is the scorer scoping.
- **Full-suite QA required:** The scorer and lab contract changes affect all downstream finding types. All existing tests must pass.

---

## Output Receipt

**Agent:** Anvil Systems Analyst
**Step:** Step 1
**Status:** Complete

### What Was Done
Designed the `last_seen_cycle` schema migration, write-path stamping (4 paths in extractor, including the skip-unchanged trap), scorer scoping, and `find_intent_gaps` belt-and-suspenders guard. Sized the (a2) orphan population (1,599 module chunks, only 1 production Python file) and recommended deferring file-set reconciliation. Produced the full implementation blueprint with verification checks and test surface.

### Files Deposited
- `anvil/knowledge/architecture/intent-gap-phantom-fix-blueprint-2026-06-03.md` — SA blueprint for phantom-function elimination via `last_seen_cycle`

### Files Created or Modified (Code)
- None (design-only step)

### Decisions Made
- Defer SCAN file-set reconciliation to BACKLOG (last_seen_cycle handles (a2) at filter level; only 1 production Python orphan)
- No explicit backfill — first post-fix cycle stamps live chunks naturally
- Stamp in extractor only (not scanner) — extractor has cycle_id and iterates all modules
- Use `last_seen_cycle = cycle_id` (exact match) over `IS NOT NULL` for strictness
- No index on `last_seen_cycle` at this time (monitor query plans)

### Flags for CEO
- None — column addition was pre-approved; all other decisions within SA authority

### Flags for Next Step
- The DEV must add `cycle_id` as a parameter to `_update_chunk()` (it currently doesn't receive it)
- Path D (unchanged chunk stamping) is the highest-risk implementation path — the existing branch does no DB write, so the DEV must add one without disrupting the content_hash skip logic
- The `compute_fingerprints` call in extractor.py (line 545) still processes ALL non-module chunks — this is a minor inefficiency, not a correctness issue, and is out of scope
- BACKLOG note needed: "File-set reconciliation — prune module chunks for deleted files (1,599 orphans, DB hygiene)"
