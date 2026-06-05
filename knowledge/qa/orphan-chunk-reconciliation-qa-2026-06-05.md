# Anvil QA Report — Orphan-Chunk Reconciliation (Deleted-File Prune + Bypass-Surface Freshness Filters)

**Date:** 2026-06-05 | **Agent:** Anvil QA Analyst | **Plan:** `executable-anvil-orphan-chunk-reconciliation-2026-06-05.md` | **Blueprint:** `knowledge/architecture/orphan-chunk-reconciliation-blueprint-2026-06-05.md` | **Dev Log:** `knowledge/development/orphan-chunk-reconciliation-2026-06-05.md`

## Verification Summary

| Area | Expected | Status | Evidence |
|---|---|---|---|
| (a) Deliverable verification | All code items from dev log present in source | PASS | `evidence/.../grep_deliverables.txt` |
| (b) Prune correctness on DB copy | 2,652 orphan chunks pruned, cascade clean, live untouched | PASS | `evidence/.../prune_check.txt` |
| (c) Bypass-surface filter | (a1) orphans excluded from clone/bp/stats surfaces | PASS | `evidence/.../surface_check.txt` |
| (d) Full test suite | 238 passed, 0 failed | PASS | `evidence/.../pytest_full.txt` |

**Overall Verdict: PASS**

---

## (a) Deliverable Verification (Rule 17)

Every item in the Step 2 dev-log "Files Created or Modified (Code)" list was grep-verified in source:

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `prune_deleted_file_orphans()` in scanner.py | Function defined + called from scan_project() | PASS | scanner.py:107 (def), scanner.py:51 (call) |
| Scanner imports (logging, shutil, ANVIL_DB_PATH, ANVIL_ROOT) | All 4 imports present | PASS | scanner.py:11,13,20,21 |
| Backup logic in prune function | shutil.copy2 with ANVIL_DB_PATH guard | PASS | scanner.py:130-131 |
| `find_clone_candidates` filter | `a.last_seen_cycle = ? AND b.last_seen_cycle = ?` | PASS | lab.py:196 |
| `find_best_practice_deviations` signature + filter | `(conn, project_id, cycle_id)` + `AND last_seen_cycle = ?` | PASS | lab.py:317,325 |
| `generate_specialist_update_data` signature + filter | `(conn, project_id, cycle_id)` + 7 queries filtered | PASS | lab.py:764, 769/778/786/794/802/813/827 |
| Call site: `find_best_practice_deviations` | Passes `cycle_id` | PASS | lab.py:66 |
| Call site: `generate_specialist_update_data` | Passes `cycle_id` | PASS | lab.py:90 |
| 4 new prune tests in test_scanner.py | All 4 present | PASS | test_scanner.py:350,395,421,442 |
| 4 new filter tests in test_lab.py | All 4 present | PASS | test_lab.py:525,554,575,602 |
| 1 cascade test in test_db.py | Present | PASS | test_db.py:474 |
| 3 updated tests in test_detector.py | cycle_id + last_seen_cycle added | PASS | test_detector.py:186,194,218,226,240,243 |

**No missing deliverables.**

---

## (b) Prune Correctness (on DB copy)

Tested against `/tmp/anvil-qa-prune-test.db` (copy of `anvil/anvil.db`). `PRAGMA foreign_keys=ON`.

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

All deltas match the SA blueprint section (3) exactly.

### Key Checks

- **Named production orphan (`web/training.py`):** Present before (1 module chunk), gone after (0). PASS.
- **Orphan population:** 1,601 file_paths, 2,652 total chunks (2,400 modules + 252 children). Matches blueprint.
- **FK integrity:** `PRAGMA foreign_key_check` returns 0 violations. PASS.
- **Live chunks untouched:** 6,736 before and after prune (count of non-orphan chunks). PASS.
- **Count delta:** 9,388 - 2,652 = 6,736. Exact match. PASS.
- **Remaining orphan file_paths:** 0. PASS.

---

## (c) Bypass-Surface Check

Filter status: **INCLUDED** (per blueprint recommendation, CEO-approved).

### find_clone_candidates

- Without filter (old query): 279 rows
- With filter (new query): 191 rows
- (a1) orphans excluded: 88 rows

Blueprint pre-prune figure was 154 (a1) rows. Post-prune, cascade removed similarity rows where one/both sides were (a2), leaving 88 purely (a1) rows. Consistent.

### find_best_practice_deviations

- Without filter: 1,880 chunks
- With filter: 1,726 chunks
- (a1) orphans excluded: **154** (matches blueprint exactly)

Blueprint-named (a1) samples verified excluded:
- chunk 953 (`_table_exists`): last_seen_cycle=None -> EXCLUDED
- chunk 962 (`_determine_acc_alignment`): last_seen_cycle=None -> EXCLUDED
- chunk 976 (`patterns_page`): last_seen_cycle=None -> EXCLUDED

### generate_specialist_update_data

- All chunks post-prune: 6,736
- Filtered (last_seen_cycle=20): 3,940
- Stale chunks excluded from stats: 2,796

Stats now reflect only current-cycle chunks, as designed.

---

## (d) Full Test Suite

```
238 passed in 2.73s
```

All tests green. No pre-existing failures. No new failures. 9 new tests added by this plan (4 prune, 4 filter, 1 cascade). 3 existing tests updated for signature changes.

---

## Output Receipt

**Agent:** Anvil QA Analyst
**Step:** Step 3
**Status:** Complete

### What Was Done
Verified all deliverables from Step 2 implementation via grep. Ran prune correctness check against a DB copy — confirmed 2,652 orphan chunks pruned with clean cascade and zero FK violations. Verified all three bypass-surface freshness filters exclude (a1) orphans. Full test suite: 238/238 passed.

### Files Deposited
- `knowledge/qa/orphan-chunk-reconciliation-qa-2026-06-05.md` — this QA report
- `knowledge/qa/evidence/executable-anvil-orphan-chunk-reconciliation-2026-06-05/grep_deliverables.txt` — deliverable grep evidence
- `knowledge/qa/evidence/executable-anvil-orphan-chunk-reconciliation-2026-06-05/prune_check.txt` — prune correctness evidence
- `knowledge/qa/evidence/executable-anvil-orphan-chunk-reconciliation-2026-06-05/surface_check.txt` — bypass-surface filter evidence
- `knowledge/qa/evidence/executable-anvil-orphan-chunk-reconciliation-2026-06-05/pytest_full.txt` — full test suite evidence

### Files Created or Modified (Code)
- None (QA is read-only on source)

### Decisions Made
- PASS verdict: all 4 verification areas pass with evidence

### Flags for CEO
- None

### Flags for Next Step
- None — plan is ready for close
