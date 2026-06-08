# Lab Project Scope Fix — Dev Log
**Date:** 2026-06-08
**Agent:** Anvil Developer
**Plan:** executable-anvil-lab-project-scope-fix-v2-2026-06-08, Step 2
**Blueprint:** `knowledge/architecture/lab-project-scope-blueprint-2026-06-08.md`

## Changes Applied

### 1. `find_coverage_gaps` (src/lab.py, line ~127)

Added `AND cc.project_id = ?` to WHERE clause, appended `project_id` to params tuple.

**Before:**
```python
"AND cc.file_path NOT LIKE 'tests/%' "
"ORDER BY hs.composite_score DESC",
(cycle_id, COVERAGE_GAP_THRESHOLD, HIGH_RISK_THRESHOLD),
```

**After:**
```python
"AND cc.file_path NOT LIKE 'tests/%' "
"AND cc.project_id = ? "
"ORDER BY hs.composite_score DESC",
(cycle_id, COVERAGE_GAP_THRESHOLD, HIGH_RISK_THRESHOLD, project_id),
```

### 2. `find_coupling_hotspots` (src/lab.py, line ~157)

Added `AND cc.project_id = ?` to WHERE clause, appended `project_id` to params tuple.

**Before:**
```python
"AND cc.file_path NOT LIKE 'tests/%' "
"ORDER BY hs.coupling_score DESC",
(cycle_id, min_threshold),
```

**After:**
```python
"AND cc.file_path NOT LIKE 'tests/%' "
"AND cc.project_id = ? "
"ORDER BY hs.coupling_score DESC",
(cycle_id, min_threshold, project_id),
```

### 3. Regression Test

Added `test_finding_functions_project_scoped` to `tests/test_lab.py`. Seeds two projects (`proj_a`, `proj_b`) sharing `cycle_id=1` with distinct qualifying chunks + health_scores above all finding thresholds. Asserts:

- `find_coverage_gaps(conn, proj_a_id, 1)` returns only proj_a chunks (zero proj_b)
- `find_coverage_gaps(conn, proj_b_id, 1)` returns only proj_b chunks (zero proj_a)
- `find_coupling_hotspots(conn, proj_a_id, 1)` returns only proj_a chunks
- `find_coupling_hotspots(conn, proj_b_id, 1)` returns only proj_b chunks
- Non-regression: `find_staleness_alerts` and `find_complexity_hotspots` also scoped correctly

**This test would FAIL against pre-fix code** — without `cc.project_id = ?` in the coverage gaps and coupling hotspots queries, both projects' chunks would appear in both calls.

## Functions NOT Touched (already SCOPED per blueprint)

- `find_clone_candidates` — `a.project_id = ?`
- `find_staleness_alerts` — `cc.project_id = ?`
- `find_complexity_hotspots` — `cc.project_id = ?`
- `find_cochange_patterns` — `project_id = ?`
- `find_best_practice_deviations` — `project_id = ?`
- `find_intent_gaps` — `cc.project_id = ?` in all 3 sub-queries
- `generate_specialist_update_data` — `project_id = ?` in all 7 queries
- `generate_planner_constraints` — no SQL
- `write_cycle_report` Untested Complexity — `cc.project_id = ?`

## Test Results

```
240 passed in 2.93s
```

Baseline was 239, +1 new test = 240. All pass, zero failures.

---

## Output Receipt
**Agent:** Anvil Developer
**Step:** Step 2
**Status:** Complete

### What Was Done
Applied `cc.project_id = ?` constraints to `find_coverage_gaps` and `find_coupling_hotspots` in `src/lab.py`. Added regression test `test_finding_functions_project_scoped` to `tests/test_lab.py` that seeds two projects sharing `cycle_id=1` and asserts zero cross-project contamination. Full suite: 240 passed.

### Files Deposited
- `knowledge/development/lab-project-scope-fix-2026-06-08.md` — this dev log

### Files Created or Modified (Code)
- `src/lab.py` — added `AND cc.project_id = ?` to `find_coverage_gaps` (line ~127) and `find_coupling_hotspots` (line ~157)
- `tests/test_lab.py` — added `test_finding_functions_project_scoped` regression test

### Decisions Made
- Included non-regression assertions for `find_staleness_alerts` and `find_complexity_hotspots` in the same test to guard already-scoped functions under the two-project seed
- Used direct `conn.execute` lookups to verify chunk ownership rather than relying on name matching alone

### Flags for CEO
- None

### Flags for Next Step
- QA: regression test name is `test_finding_functions_project_scoped` — use `-k "project_scoped"` to select it
- QA: test count is 240 (baseline 239 + 1 new)
- The test would fail pre-fix: without `cc.project_id = ?`, both projects' chunks appear in each call
