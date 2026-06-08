# Lab Project Scope Blueprint — 2026-06-08
**Date:** 2026-06-08
**Agent:** Anvil Systems Analyst
**Plan:** executable-anvil-lab-project-scope-fix-v2-2026-06-08, Step 1
**Scope:** `src/lab.py` query surface audit for project scoping

## Background

`cycle_id` is per-project, not globally unique (`cycle.py` line 32–38: `MAX(cycle_number) WHERE project_id`). `health_scores` has no `project_id` column — it keys on `chunk_id` + `cycle_id`. Any finding query joining `health_scores` on `cycle_id` alone, without constraining `code_chunks.project_id`, returns rows from every project sharing that `cycle_id`. Bellows cycle 1 (`cycle_id=1`) collided with invoice-pulse cycle 1, causing 28/113 findings to belong to the wrong project.

---

## 1. Full Query Surface Audit

| # | Function | Line | Receives `project_id`? | SQL constrains to project? | Mechanism | Verdict |
|---|---|---|---|---|---|---|
| 1 | `find_coverage_gaps` | 117 | Yes (`project_id` param) | **NO** | No `cc.project_id = ?` in WHERE; params are `(cycle_id, COVERAGE_GAP_THRESHOLD, HIGH_RISK_THRESHOLD)` | **LEAKS** |
| 2 | `find_coupling_hotspots` | 142 | Yes (`project_id` param) | **NO** | No `cc.project_id = ?` in WHERE; params are `(cycle_id, min_threshold)` | **LEAKS** |
| 3 | `find_clone_candidates` | 191 | Yes (`project_id` param) | Yes — DIRECTLY | `a.project_id = ?` at line 199 | **SCOPED** |
| 4 | `find_staleness_alerts` | 215 | Yes (`project_id` param) | Yes — DIRECTLY | `cc.project_id = ?` at line 223 | **SCOPED** |
| 5 | `find_complexity_hotspots` | 236 | Yes (`project_id` param) | Yes — DIRECTLY | `cc.project_id = ?` at line 250 | **SCOPED** |
| 6 | `find_cochange_patterns` | 281 | Yes (`project_id` param) | Yes — DIRECTLY | `project_id = ?` at line 286 (queries `git_changes`, not `health_scores`) | **SCOPED** |
| 7 | `find_best_practice_deviations` | 321 | Yes (`project_id` param) | Yes — DIRECTLY | `project_id = ?` at line 327 (queries `code_chunks` directly) | **SCOPED** |
| 8 | `find_intent_gaps` | 422 | Via `project_name` → internal lookup | Yes — DIRECTLY | `cc.project_id = ?` at lines 479, 535, 590 (all 3 sub-queries) | **SCOPED** |
| 9 | `generate_planner_constraints` | 704 | Via `project_name` | No SQL — processes `findings` dict | Scoping depends on upstream finding functions | **N/A** |
| 10 | `generate_specialist_update_data` | 768 | Yes (`project_id` param) | Yes — DIRECTLY | `project_id = ?` or `cc.project_id = ?` in all 7 queries (lines 773, 781, 789, 797, 805, 816, 830) | **SCOPED** |
| 11 | `write_cycle_report` (Untested Complexity query) | 900 | Via `project_id` from caller | Yes — DIRECTLY | `cc.project_id = ?` at line 908 | **SCOPED** |

---

## 2. Exact Edits for LEAKS Functions

### 2a. `find_coverage_gaps` (line 117)

**Current code (lines 124–128):**
```python
        "WHERE hs.cycle_id = ? AND hs.coverage_score >= ? "
        "AND hs.composite_score >= ? AND cc.chunk_type != 'test_case' "
        "AND cc.file_path NOT LIKE 'tests/%' "
        "ORDER BY hs.composite_score DESC",
        (cycle_id, COVERAGE_GAP_THRESHOLD, HIGH_RISK_THRESHOLD),
```

**Fix — add `AND cc.project_id = ?` before ORDER BY, append `project_id` to params:**
```python
        "WHERE hs.cycle_id = ? AND hs.coverage_score >= ? "
        "AND hs.composite_score >= ? AND cc.chunk_type != 'test_case' "
        "AND cc.file_path NOT LIKE 'tests/%' "
        "AND cc.project_id = ? "
        "ORDER BY hs.composite_score DESC",
        (cycle_id, COVERAGE_GAP_THRESHOLD, HIGH_RISK_THRESHOLD, project_id),
```

### 2b. `find_coupling_hotspots` (line 142)

**Current code (lines 154–157):**
```python
        "WHERE hs.cycle_id = ? AND hs.coupling_score >= ? "
        "AND cc.file_path NOT LIKE 'tests/%' "
        "ORDER BY hs.coupling_score DESC",
        (cycle_id, min_threshold),
```

**Fix — add `AND cc.project_id = ?` before ORDER BY, append `project_id` to params:**
```python
        "WHERE hs.cycle_id = ? AND hs.coupling_score >= ? "
        "AND cc.file_path NOT LIKE 'tests/%' "
        "AND cc.project_id = ? "
        "ORDER BY hs.coupling_score DESC",
        (cycle_id, min_threshold, project_id),
```

---

## 3. Orphan-Chunk Reconciliation Cross-Check (2026-06-05)

### `find_clone_candidates` (line 191)
The 2026-06-05 reconciliation added `a.last_seen_cycle = ?` and `b.last_seen_cycle = ?` (lines 200–201). These filter for currency (only chunks seen in the current cycle) but do **NOT** imply project scoping — two different projects can share the same `last_seen_cycle` value if they share the same `cycle_id`. However, `a.project_id = ?` (line 199) **does** project-scope the results by constraining chunk A to the target project. Chunk B is not project-constrained, which is architecturally correct: cross-project clone detection is intentional. **Verdict: `last_seen_cycle` does not scope; `a.project_id` does. Function is SCOPED.**

### `generate_specialist_update_data` (line 768)
The 2026-06-05 reconciliation added `cc.last_seen_cycle = ?` to all sub-queries. As above, `last_seen_cycle` alone does not imply project scoping. However, every query in this function **also** includes `cc.project_id = ?` (or `project_id = ?` on `code_chunks` directly). **Verdict: `last_seen_cycle` adds currency filtering; `project_id` provides the scope. Function is SCOPED.**

**Conclusion:** The `last_seen_cycle` filter from the orphan-chunk reconciliation is a correctness filter (excludes stale/deleted chunks) but is **not** a project discriminator. Project scoping requires an explicit `project_id` constraint, which both functions already have.

---

## 4. Functions Already Correctly SCOPED (leave untouched)

| Function | Scoping line(s) | Evidence |
|---|---|---|
| `find_clone_candidates` (line 191) | `a.project_id = ?` (line 199) | `"WHERE cs.cycle_id = ? AND a.project_id = ?"` |
| `find_staleness_alerts` (line 215) | `cc.project_id = ?` (line 223) | `"AND cc.project_id = ?"` in params `(cycle_id, STALENESS_THRESHOLD, project_id)` |
| `find_complexity_hotspots` (line 236) | `cc.project_id = ?` (line 250) | `"AND cc.project_id = ?"` in params `(cycle_id, min_threshold, project_id)` |
| `find_cochange_patterns` (line 281) | `project_id = ?` (line 286) | `"WHERE project_id = ? AND file_path != ''"` on `git_changes` table |
| `find_best_practice_deviations` (line 321) | `project_id = ?` (line 327) | `"WHERE project_id = ? AND functional_role IS NOT NULL"` on `code_chunks` |
| `find_intent_gaps` (line 422) | `cc.project_id = ?` (lines 479, 535, 590) | All 3 sub-queries: `"WHERE hs.cycle_id = ? AND cc.project_id = ?"` |
| `generate_specialist_update_data` (line 768) | `project_id = ?` / `cc.project_id = ?` (7 queries) | Every query includes project_id constraint |
| `write_cycle_report` Untested Complexity (line 900) | `cc.project_id = ?` (line 908) | `"WHERE hs.cycle_id = ? AND cc.project_id = ?"` |
| `generate_planner_constraints` (line 704) | N/A — no SQL | Processes pre-computed findings dict; scoping is upstream |

---

## 5. Regression Test Design

### Setup
Seed two projects sharing `cycle_id = 1`:
- **proj_a** (`project_id=1`): Insert qualifying `code_chunks` + `health_scores` rows that meet finding thresholds (e.g., `coverage_score >= 0.8`, `composite_score >= 0.7` for coverage gaps; `coupling_score >= 0.8` for coupling hotspots).
- **proj_b** (`project_id=2`): Insert distinct qualifying `code_chunks` + `health_scores` rows with the same `cycle_id = 1` that also meet thresholds.

### Assertions
For each **LEAKS** function (now fixed), call with `(conn, proj_a_id, cycle_id=1)` and assert:
1. All returned `chunk_id` values belong to proj_a (via lookup in `code_chunks`).
2. Zero rows from proj_b appear in the results.
3. Repeat with `(conn, proj_b_id, cycle_id=1)` — all returned chunks belong to proj_b.

### Functions the test MUST cover
1. **`find_coverage_gaps`** — the confirmed offender (28/113 bellows findings were invoice-pulse)
2. **`find_coupling_hotspots`** — same pattern as coverage gaps (LEAKS)

### Optional but recommended
Also verify that already-SCOPED functions (`find_staleness_alerts`, `find_complexity_hotspots`) continue to return project-scoped results under the same two-project seed — serves as a non-regression guard.

### Test structure
A single parametrized or multi-assertion test function (e.g., `test_finding_functions_project_scoped`) that:
1. Creates an in-memory DB with the test schema
2. Inserts `proj_a` and `proj_b` into `projects`
3. Inserts code_chunks for each project (distinct `file_path` / `name` to distinguish)
4. Inserts `health_scores` for each project's chunks at `cycle_id=1`, all above thresholds
5. Calls each finding function with `(conn, proj_a_id, 1)` and asserts zero proj_b chunks
6. Calls each finding function with `(conn, proj_b_id, 1)` and asserts zero proj_a chunks

---

## How to Verify This Was Implemented Correctly

1. For `find_coverage_gaps`: `grep -n "project_id" src/lab.py` should show `cc.project_id = ?` in the coverage gaps query (around line 127).
2. For `find_coupling_hotspots`: same grep should show `cc.project_id = ?` in the coupling hotspots query (around line 156).
3. Run the new regression test: `python3 -m pytest tests/test_lab.py -k "project_scope" -v` — must pass.
4. Run full suite: `python3 -m pytest tests/ -q` — all pass, no regressions.

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** Step 1
**Status:** Complete

### What Was Done
Audited all 11 functions/queries in `src/lab.py` that produce findings or feed cycle report / specialist data. Identified 2 LEAKS functions (`find_coverage_gaps`, `find_coupling_hotspots`), 8 SCOPED functions, and 1 N/A (no SQL). Specified exact surgical edits for each LEAKS function. Cross-checked the orphan-chunk reconciliation — confirmed `last_seen_cycle` is a currency filter, not a project discriminator. Designed regression test covering both LEAKS functions.

### Files Deposited
- `knowledge/architecture/lab-project-scope-blueprint-2026-06-08.md` — this blueprint

### Files Created or Modified (Code)
- None (SA step — no source modifications)

### Decisions Made
- Classified `find_coupling_hotspots` as LEAKS even though the dev log's manual check (step 8) found "all bellows entries" in coupling hotspots. The SQL has no `cc.project_id = ?` constraint — the apparent correct results in the bellows run were coincidental (invoice-pulse coupling hotspots happened to fall below the threshold at `cycle_id=1`, so they didn't surface). The query is structurally unsound and must be fixed.
- Classified `generate_planner_constraints` as N/A rather than SCOPED because it contains no SQL — its correctness depends entirely on upstream finding functions.
- Did not flag `find_clone_candidates` chunk B as a leak: cross-project clone detection (where chunk A is project-scoped but chunk B may be from another project) is architecturally intentional.

### Flags for CEO
- None

### Flags for Next Step
- DEV must fix exactly 2 functions: `find_coverage_gaps` and `find_coupling_hotspots`. All other functions are already correctly scoped — do not touch them.
- The `find_coupling_hotspots` leak was latent in the bellows run (no invoice-pulse rows surfaced due to threshold coincidence) but is structurally identical to the `find_coverage_gaps` bug and will leak under different data conditions.
