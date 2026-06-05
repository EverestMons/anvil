# Anvil — SA Blueprint: Orphan-Chunk Reconciliation (Deleted-File Prune + Bypass-Surface Freshness Filters)

**Date:** 2026-06-05 | **Agent:** Anvil Systems Analyst | **Plan:** `executable-anvil-orphan-chunk-reconciliation-2026-06-05.md`

**CEO-approval flag:** The destructive DELETE of deleted-file orphan chunks deviates from Anvil's non-destructive default. **Pre-approved by CEO (2026-06-05, path (a) decision)** — no re-escalation required. Scope: module-chunk orphans of deleted files and their child chunks only.

## Summary

The **(a2) deleted-file orphan** population is **2,400 orphan module chunks** across **1,601 unique file_paths** (files no longer on disk), with **252 child chunks** from the 17 deleted Python files — **2,652 total chunks** to prune. Of the 17 deleted .py files, only **1 is production** (`web/training.py`, 20 children); the other 16 are test files. The **(a1) surviving-file orphan** population (chunks whose file exists but which were not stamped at cycle 20) is **235 non-module chunks**. Of these, **154 clone candidate rows** (56 distinct chunk IDs) and **154 chunks matching the best_practice_deviations predicate** currently leak through the two bypass surfaces. **The two-surface freshness filter IS load-bearing and should be included** — the (a1) leak is substantial, not zero.

---

## (0) Population Sizing (cycle 20)

### (a2) Deleted-File Orphans

| Category | Count |
|---|---|
| DB module chunks (project_id=1) | 5,213 |
| On-disk files (scanner exclusion rules) | 2,433 |
| **Orphan module chunks (file gone)** | **2,400** |
| Unique orphan file_paths | 1,601 |
| Child chunks of orphan .py files | 252 |
| **Total chunks to prune** | **2,652** |

Orphan breakdown by extension:

| Extension | Module Count |
|---|---|
| .json | 2,359 |
| .py | 17 |
| .html | 17 |
| .md | 7 |

**Python orphan modules (17):**

| ID | File | Children | Production? |
|---|---|---|---|
| 938 | web/training.py | 20 | **Yes — only production orphan** |
| 725 | tests/test_auto_contract_phase2 2.py | 17 | No (test) |
| 727 | tests/test_auto_contract_phase3 2.py | 17 | No (test) |
| 782 | tests/test_mode_navigation.py | 14 | No (test) |
| 783 | tests/test_nav_consolidation_qa.py | 19 | No (test) |
| ... | (12 more test files) | ... | No |

**Note on module duplication:** 2,400 module chunks across 1,601 unique file_paths implies ~799 duplicate module rows (scanner creating duplicate entries across cycles). The prune DELETE targets file_path, so duplicates are naturally cleaned up. This is a pre-existing scanner hygiene issue, not introduced by this fix.

### (a1) Surviving-File Orphans on Bypass Surfaces

| Category | Count |
|---|---|
| Non-module chunks with last_seen_cycle != 20 | 487 |
| Of those, file still exists on disk **(a1)** | **235** |
| (a1) in chunk_similarities at cycle 20 | 154 similarity rows (56 distinct IDs) |
| (a1) matching best_practice_deviations predicate | 154 chunks |

**Sample (a1) in clone candidates:**

| Chunk A | Chunk B | Similarity | (a1)? |
|---|---|---|---|
| sandbox (app.py) | _sandbox_removed (app.py) | 0.969 | Both |
| _dashboard_workload_card (app.py) | _dashboard_workload_card (app.py) | 1.000 | B side |
| dashboard_yesterday_api (app.py) | dashboard_yesterday_api (app.py) | 1.000 | B side |

**Sample (a1) in best_practice_deviations:**
- id=953 `_table_exists` (app.py, utility)
- id=962 `_determine_acc_alignment` (app.py, utility)
- id=976 `patterns_page` (app.py, utility)

**Conclusion:** The (a1) leak is non-zero and substantial. **Recommend INCLUDE the two-surface filter.** Flag for CEO at the pause.

---

## (1) Bypass-Surface Enumeration

Every reader of `code_chunks` across `anvil/src/` was audited. The table below classifies each by orphan exposure:

| Reader | Location | Through health_scores? | Orphan exposure | Fix |
|---|---|---|---|---|
| `find_clone_candidates` | lab.py:187 | No (chunk_similarities -> code_chunks) | Both (a1+a2) | **Prune resolves a2; filter resolves a1** |
| `find_best_practice_deviations` | lab.py:316 | No (direct code_chunks query) | Both (a1+a2) | **Prune resolves a2; filter resolves a1** |
| `generate_specialist_update_data` | lab.py:762 | No (aggregate code_chunks counts) | Both (a1+a2) | **Prune resolves a2; filter resolves a1** |
| `classify_project` | classifier.py:142 | No (direct code_chunks) | Both | Minor — classifies dead chunks, no findings produced. Defer. |
| `resolve_dependencies` | extractor.py:395 | No (direct code_chunks) | Both | Minor — resolves deps for dead chunks, no findings. Defer. |
| `compute_fingerprints` | extractor.py:559 | No (direct code_chunks) | Both | Minor — creates fingerprints/sims for dead chunks. Defer. |
| `find_coverage_gaps` | lab.py:113 | Yes (health_scores JOIN) | None post-fix | Transitively fixed via scorer scoping |
| `find_coupling_hotspots` | lab.py:138 | Yes (health_scores JOIN) | None post-fix | Transitively fixed via scorer scoping |
| `find_staleness_alerts` | lab.py:210 | Yes (health_scores JOIN) | None post-fix | Transitively fixed via scorer scoping |
| `find_complexity_hotspots` | lab.py:231 | Yes (health_scores JOIN) | None post-fix | Transitively fixed via scorer scoping |
| `find_intent_gaps` | lab.py:416 | Yes + last_seen_cycle guard | None | Fixed in phantom-fix plan (2026-06-03) |
| `find_cochange_patterns` | lab.py:276 | No (git_changes) | None | Not a code_chunks reader |

**No new bypass surfaces discovered beyond the three known.**

---

## (2) Prune Design

### Hook Location

**File:** `src/scanner.py`, function `scan_project()`

**Insertion point:** After `discover_files()` returns (line 44), before `detect_changes()` (line 45). This is the earliest point where the on-disk file set is available.

```python
# scan_project(), after line 44:
discovered = discover_files(project_path, EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)

# --- NEW: prune deleted-file orphan chunks ---
on_disk_paths = {f["relative_path"] for f in discovered}
prune_deleted_file_orphans(conn, project_id, on_disk_paths)

# existing code continues:
new_files, changed_files, unchanged_files = detect_changes(...)
```

### On-Disk File Set Computation

Uses the same `discover_files()` output that SCAN already produces — same `EXCLUDED_DIRS` and `EXCLUDED_EXTENSIONS`, same `os.walk()` logic, same `.startswith(".")` exclusion. No separate walk needed. The relative paths are extracted into a set for O(1) lookup.

### Prune Function

```python
def prune_deleted_file_orphans(conn, project_id: int,
                                on_disk_paths: set[str]) -> dict:
    """
    Remove all code_chunks for files no longer on disk.

    Scoped to the given project_id. Cascade handles dependent rows
    in chunk_symbol_bindings, chunk_dependencies, chunk_similarities,
    chunk_provenance, chunk_fingerprints, and health_scores.
    """
    cur = conn.execute(
        "SELECT DISTINCT file_path FROM code_chunks WHERE project_id = ?",
        (project_id,),
    )
    db_file_paths = {r[0] for r in cur.fetchall()}

    orphan_fps = db_file_paths - on_disk_paths
    if not orphan_fps:
        return {"pruned_files": 0, "pruned_chunks": 0}

    # Pre-prune backup
    backup_dir = os.path.join(ANVIL_ROOT, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    backup_path = os.path.join(backup_dir, f"anvil-backup-{timestamp}.db")
    shutil.copy2(ANVIL_DB_PATH, backup_path)
    logging.info("Pre-prune backup created: %s", backup_path)

    # Count before delete for logging
    placeholders = ",".join(["?"] * len(orphan_fps))
    cur = conn.execute(
        f"SELECT COUNT(*) FROM code_chunks "
        f"WHERE project_id = ? AND file_path IN ({placeholders})",
        (project_id, *orphan_fps),
    )
    total_chunks = cur.fetchone()[0]

    cur = conn.execute(
        f"SELECT COUNT(*) FROM code_chunks "
        f"WHERE project_id = ? AND chunk_type = 'module' "
        f"AND file_path IN ({placeholders})",
        (project_id, *orphan_fps),
    )
    module_count = cur.fetchone()[0]
    child_count = total_chunks - module_count

    # Sample IDs for the log
    cur = conn.execute(
        f"SELECT id FROM code_chunks "
        f"WHERE project_id = ? AND file_path IN ({placeholders}) LIMIT 5",
        (project_id, *orphan_fps),
    )
    sample_ids = [r[0] for r in cur.fetchall()]

    # DELETE — cascade handles all dependent tables
    conn.execute(
        f"DELETE FROM code_chunks "
        f"WHERE project_id = ? AND file_path IN ({placeholders})",
        (project_id, *orphan_fps),
    )
    conn.commit()

    logging.info(
        "Pruned %d orphan chunks (%d modules, %d children) "
        "for %d deleted files. Sample chunk IDs: %s",
        total_chunks, module_count, child_count,
        len(orphan_fps), sample_ids,
    )

    return {
        "pruned_files": len(orphan_fps),
        "pruned_chunks": total_chunks,
        "pruned_modules": module_count,
        "pruned_children": child_count,
    }
```

### DELETE Scope

```sql
DELETE FROM code_chunks
WHERE project_id = ? AND file_path IN (orphan_file_paths)
```

This catches **both module chunks AND their children** (all chunk_types for the same file_path). No separate child-deletion step is needed.

### Cascade Behavior (Schema-Confirmed)

| Table | Column | FK Policy | Effect |
|---|---|---|---|
| chunk_symbol_bindings | chunk_id | ON DELETE CASCADE | Rows deleted |
| chunk_symbol_bindings | target_chunk_id | ON DELETE SET NULL | Set to NULL |
| chunk_dependencies | source_chunk_id | ON DELETE CASCADE | Rows deleted |
| chunk_dependencies | target_chunk_id | ON DELETE CASCADE | Rows deleted |
| chunk_similarities | chunk_a_id | ON DELETE CASCADE | Rows deleted |
| chunk_similarities | chunk_b_id | ON DELETE CASCADE | Rows deleted |
| chunk_provenance | chunk_id | ON DELETE CASCADE | Rows deleted |
| chunk_fingerprints | chunk_id | ON DELETE CASCADE | Rows deleted |
| health_scores | chunk_id | ON DELETE CASCADE | Rows deleted |
| code_chunks | parent_chunk_id | ON DELETE SET NULL | Set to NULL |

**Schema correction vs plan context:** The plan context stated `chunk_dependencies.target_chunk_id` is `ON DELETE SET NULL`. The actual schema (db.py:103) specifies `ON DELETE CASCADE`. Both sides of chunk_dependencies cascade. This was confirmed empirically in (3).

---

## (3) Cascade Verification (on DB copy)

Tested against `/tmp/anvil-cascade-test.db` (copy of `anvil.db`). `PRAGMA foreign_keys=ON` confirmed before prune.

### Before/After Row Counts

| Table | Before | After | Delta |
|---|---|---|---|
| code_chunks | 9,388 | 6,736 | **-2,652** |
| chunk_symbol_bindings | 815,316 | 805,377 | -9,939 |
| chunk_dependencies | 3,158,992 | 3,076,021 | -82,971 |
| chunk_similarities | 10,353 | 4,696 | -5,657 |
| chunk_provenance | 15,611 | 15,543 | -68 |
| health_scores | 77,265 | 72,225 | -5,040 |
| chunk_fingerprints | 86,973 | 79,014 | -7,959 |

### FK Integrity

- `PRAGMA foreign_key_check` after prune: **no violations**
- `chunk_symbol_bindings.target_chunk_id` references to deleted IDs: **0** (correctly SET NULL)
- `code_chunks.parent_chunk_id` references to deleted IDs: **0** (correctly SET NULL)

**Cascade is clean.** The DELETE of 2,652 orphan chunks cascaded correctly through all 7 dependent tables with no dangling FKs.

---

## (4) Backup + Idempotency + Logging

### Pre-Prune Backup

**Path:** `{ANVIL_ROOT}/backups/anvil-backup-{YYYYMMDD-HHMMSS}.db`

**Location in code:** Inside `prune_deleted_file_orphans()`, before the DELETE, conditional on `len(orphan_fps) > 0` (function returns early if nothing to prune, so backup only fires when orphans exist).

The backup fires once per prune invocation, only when orphans exist. Since `prune_deleted_file_orphans()` runs once per `scan_project()` call, the first production cycle auto-backs-up. Subsequent cycles with no orphans skip the backup.

### Idempotency

- If no orphans exist (`orphan_fps` is empty), the function returns immediately with `{"pruned_files": 0, "pruned_chunks": 0}` — clean no-op.
- Re-running after a successful prune finds no orphan file_paths (they were all deleted) and is a no-op.
- The backup is only created when orphans exist, so re-runs don't pile up empty backups.

### Log Line

```
INFO: Pre-prune backup created: /Users/marklehn/Developer/GitHub/anvil/backups/anvil-backup-20260605-143022.db
INFO: Pruned 2652 orphan chunks (2400 modules, 252 children) for 1601 deleted files. Sample chunk IDs: [938, 725, 727, 782, 783]
```

---

## (5) Two-Surface Freshness Filter

### Evidence Gate Result

**(0) confirms:** 154 clone candidate rows and 154 best_practice_deviations chunks involve (a1) surviving-file orphans. **The filter IS load-bearing.**

**Recommendation: INCLUDE the filter.** The (a1) leak is substantial (154 rows on each surface). Without the filter, prune-only fixes (a2) but leaves (a1) orphans surfacing as clone candidates and best-practice deviations.

### "Current cycle" Definition

The `cycle_id` passed to `run_lab(conn, project_name, cycle_id)` from `run_cycle()` — the same integer used for EXTRACT stamping and SCORE filtering. Consistency with the phantom-fix substrate is guaranteed.

### find_clone_candidates (lab.py:187)

**Current query (line 189-196):**
```sql
SELECT cs.chunk_a_id, cs.chunk_b_id, cs.similarity_score,
       a.file_path, a.name, b.file_path, b.name
FROM chunk_similarities cs
JOIN code_chunks a ON cs.chunk_a_id = a.id
JOIN code_chunks b ON cs.chunk_b_id = b.id
WHERE cs.cycle_id = ? AND a.project_id = ?
ORDER BY cs.similarity_score DESC
```

**New query:**
```sql
SELECT cs.chunk_a_id, cs.chunk_b_id, cs.similarity_score,
       a.file_path, a.name, b.file_path, b.name
FROM chunk_similarities cs
JOIN code_chunks a ON cs.chunk_a_id = a.id
JOIN code_chunks b ON cs.chunk_b_id = b.id
WHERE cs.cycle_id = ? AND a.project_id = ?
  AND a.last_seen_cycle = ? AND b.last_seen_cycle = ?
ORDER BY cs.similarity_score DESC
```

Parameters: `(cycle_id, project_id, cycle_id, cycle_id)`

**Both sides filtered.** An (a1) orphan on either side of a similarity pair is excluded.

### find_best_practice_deviations (lab.py:316)

**Signature change:** `find_best_practice_deviations(conn, project_id)` -> `find_best_practice_deviations(conn, project_id, cycle_id)`

**Current query (line 320-324):**
```sql
SELECT id, file_path, name, content, structural_metadata, functional_role
FROM code_chunks WHERE project_id = ? AND functional_role IS NOT NULL
AND chunk_type NOT IN ('module', 'test_case')
```

**New query:**
```sql
SELECT id, file_path, name, content, structural_metadata, functional_role
FROM code_chunks WHERE project_id = ? AND functional_role IS NOT NULL
AND chunk_type NOT IN ('module', 'test_case')
AND last_seen_cycle = ?
```

Parameters: `(project_id, cycle_id)`

**Call site update** (lab.py:66): `find_best_practice_deviations(conn, project_id)` -> `find_best_practice_deviations(conn, project_id, cycle_id)`

### generate_specialist_update_data (lab.py:762)

**Signature change:** `generate_specialist_update_data(conn, project_id)` -> `generate_specialist_update_data(conn, project_id, cycle_id)`

**Queries to filter** (add `AND last_seen_cycle = ?` or `AND cc.last_seen_cycle = ?`):

1. **Chunk type counts (line 766):** `SELECT chunk_type, COUNT(*) FROM code_chunks WHERE project_id = ? AND last_seen_cycle = ? GROUP BY chunk_type`
2. **Dep count (line 773):** Add `AND cc.last_seen_cycle = ?` to the JOIN filter
3. **Sim count (line 781):** Add `AND cc.last_seen_cycle = ?` to the JOIN filter
4. **Avg composite (line 789):** Add `AND cc.last_seen_cycle = ?` to the JOIN filter
5. **High risk count (line 797):** Add `AND cc.last_seen_cycle = ?` to the JOIN filter
6. **Top 10 complex (line 806):** Add `AND cc.last_seen_cycle = ?` to the JOIN filter
7. **Top 10 coupled (line 822):** Add `AND cc.last_seen_cycle = ?` to the JOIN filter

**Call site update** (lab.py:90): `generate_specialist_update_data(conn, project_id)` -> `generate_specialist_update_data(conn, project_id, cycle_id)`

---

## (6) Scope-Boundary Confirmation

**(a1) surviving-file orphans are NOT pruned.** They remain in the database.

**Why:**
1. Their source files still exist on disk — they represent functions/classes that were removed or renamed in surviving files.
2. The existing `last_seen_cycle` stamping (phantom-fix, 2026-06-03) already excludes them from all `health_scores`-based finding surfaces (coverage gaps, coupling hotspots, staleness alerts, complexity hotspots, intent gaps).
3. The only residual exposure is the three bypass surfaces (`find_clone_candidates`, `find_best_practice_deviations`, `generate_specialist_update_data`), which are handled by the freshness filter in (5), not by deletion.
4. Deleting (a1) chunks from surviving files would be semantically incorrect — those files are actively tracked by the scanner, and their chunks may be recreated on the next EXTRACT cycle anyway.

**The prune touches ONLY:**
- Code chunks whose `file_path` is not present on disk (as determined by `discover_files()` using the scanner's exclusion rules)
- All chunk_types for those file_paths (modules AND children)
- For the scanned project only (`project_id` filter)

---

## (7) How to Verify This Was Implemented Correctly

### Prune Verification

1. **Backup file created:**
   ```bash
   ls anvil/backups/anvil-backup-*.db
   ```
   At least one backup should exist after the first post-fix scan. Verify timestamp is before the prune log line.

2. **Orphan modules pruned:**
   ```sql
   SELECT COUNT(*) FROM code_chunks
   WHERE project_id = 1 AND chunk_type = 'module'
   AND file_path = 'web/training.py';
   ```
   Expected: **0** (the named production orphan is gone).

3. **No orphan file_paths remain:**
   Walk the on-disk file set, query all module file_paths, confirm the difference is 0.

4. **Cascade left no dangling rows:**
   ```sql
   PRAGMA foreign_key_check;
   ```
   Expected: empty result set.

5. **generate_specialist_update_data counts dropped:**
   Compare pre- and post-prune `total_files` (module count). The delta should equal the pruned module count.

### Filter Verification (if included)

6. **find_clone_candidates excludes (a1) orphans:**
   Run `find_clone_candidates` for cycle 21+. Verify none of the 56 (a1) chunk IDs from the blueprint sizing appear in results. Specifically, chunks like `sandbox` (id=977), `_sandbox_removed` (id=4478) should not appear.

7. **find_best_practice_deviations excludes (a1) orphans:**
   Run the function for the current cycle. Verify `_table_exists` (id=953), `_determine_acc_alignment` (id=962), and other (a1) samples do not appear.

8. **Legitimate findings preserved:**
   Compare cycle N findings against cycle 20 findings. All findings that were NOT in the orphan set should still appear. Count delta should match the pruned + filtered orphan total.

### Full Pipeline Verification

9. **Run a full cycle (SCAN -> EXTRACT -> SCORE -> LAB):**
   Confirm the prune fires during SCAN, the backup is created, findings are clean of orphans, and all legitimate findings remain.

10. **Re-run is idempotent:**
    Run a second cycle immediately after. Prune should report 0 orphans, no backup created, identical findings.

---

## (8) Test Surface

### Files to Update/Add

| Test File | What to Test | Notes |
|---|---|---|
| `tests/test_scanner.py` | **Prune function:** Create a project with module chunks for files that exist and files that don't. Call `prune_deleted_file_orphans()`. Verify orphan modules and children are deleted; live chunks are untouched. **Backup:** Verify backup file is created before prune. **Idempotency:** Call prune twice — second call is a no-op. | New test function(s). The prune function is the core new code in scanner.py. |
| `tests/test_lab.py` | **find_clone_candidates filter:** Create two chunks: one with `last_seen_cycle = cycle_id`, one with `last_seen_cycle = NULL`. Create a similarity pair between them. Verify the pair is excluded from results. **find_best_practice_deviations filter:** Create a classified chunk with stale `last_seen_cycle`. Verify it does not appear in results. **generate_specialist_update_data filter:** Verify counts reflect only chunks with `last_seen_cycle = cycle_id`. | Signature changes: `find_best_practice_deviations` and `generate_specialist_update_data` now take `cycle_id`. Update existing test call sites. |
| `tests/test_db.py` | **Cascade on delete:** Create a chunk with symbol_bindings, dependencies, similarities, fingerprints, health_scores, and provenance. Delete the chunk. Verify all dependent rows are cascade-deleted and SET NULL references are nulled. | Confirms the schema-level cascade behavior that the prune relies on. |
| `tests/test_cycle.py` | **Full pipeline with prune:** If an integration test exists for `run_cycle()`, verify it still passes with the prune in the SCAN path. | May not need new tests if test_scanner covers the prune function. |

### Contract Changes

- **`find_best_practice_deviations(conn, project_id)`** -> **`find_best_practice_deviations(conn, project_id, cycle_id)`** — callers must now pass `cycle_id`. Only `run_lab()` calls this function; it already has `cycle_id`.
- **`generate_specialist_update_data(conn, project_id)`** -> **`generate_specialist_update_data(conn, project_id, cycle_id)`** — same situation, only called from `run_lab()`.
- **`find_clone_candidates`** — no signature change; it already receives `cycle_id`.
- **Full-suite QA required:** The filter changes affect all downstream finding types in the cycle report.

---

## Output Receipt

**Agent:** Anvil Systems Analyst
**Step:** Step 1
**Status:** Complete

### What Was Done
Sized both orphan populations at cycle 20: (a2) 2,652 chunks across 1,601 deleted file_paths; (a1) 235 surviving-file orphans with 154 rows leaking through each bypass surface. Confirmed cascade behavior on a DB copy (2,652 chunks deleted, all dependent rows cleaned, no FK violations). Designed the prune hook (scanner.py, after discover_files), backup mechanism (timestamped copy, conditional on orphans), freshness filter for the three bypass surfaces, and verification/test plan.

### Files Deposited
- `knowledge/architecture/orphan-chunk-reconciliation-blueprint-2026-06-05.md` — SA blueprint for deleted-file prune + bypass-surface freshness filters

### Files Created or Modified (Code)
- None (design-only step)

### Decisions Made
- Prune hook placed in scanner.py after discover_files() — earliest point with on-disk file set
- DELETE targets file_path (not chunk_id) to catch both modules and children in one operation
- Backup conditional on orphans existing (no empty backups on clean re-runs)
- Freshness filter INCLUDED (not deferred) — (a1) leak is 154 rows per surface, non-zero
- Signature changes to find_best_practice_deviations and generate_specialist_update_data to accept cycle_id
- Schema correction documented: chunk_dependencies.target_chunk_id is ON DELETE CASCADE (not SET NULL as stated in plan context)

### Flags for CEO
- **(a1) filter include/defer decision:** The (a1) surviving-file orphan leak is 154 clone candidate rows and 154 best_practice_deviations chunks. **This blueprint recommends INCLUDE.** If you prefer to defer, the prune alone fixes (a2) and the BACKLOG note would cover the remaining (a1) exposure.

### Flags for Next Step
- The DEV must update the call sites for the two renamed function signatures (both in run_lab, lines 66 and 90)
- The prune function should be added to scanner.py, called from scan_project() after discover_files()
- The backup path uses ANVIL_ROOT and ANVIL_DB_PATH from config — import these in scanner.py
- The prune function needs logging, shutil, and datetime imports in scanner.py
- compute_fingerprints (extractor.py:559) still processes all non-module chunks — minor inefficiency, not in scope
- classify_project (classifier.py:142) still classifies all chunks — minor, not in scope
