# QA Report — Lab Project Scope Fix
**Date:** 2026-06-08
**Agent:** Anvil QA Analyst
**Plan:** executable-anvil-lab-project-scope-fix-v2-2026-06-08, Step 3
**Blueprint:** `knowledge/architecture/lab-project-scope-blueprint-2026-06-08.md`
**Dev Log:** `knowledge/development/lab-project-scope-fix-2026-06-08.md`

---

## Verification Table

| Check | Expected | Status | Evidence |
|---|---|---|---|
| (1) `find_coverage_gaps` now scopes by project | `AND cc.project_id = ?` present in WHERE clause (line 127) | ✅ | `evidence/executable-anvil-lab-project-scope-fix-v2-2026-06-08/scoped_find_coverage_gaps.txt` |
| (1) `find_coupling_hotspots` now scopes by project | `AND cc.project_id = ?` present in WHERE clause (line 157) | ✅ | `evidence/executable-anvil-lab-project-scope-fix-v2-2026-06-08/scoped_find_coupling_hotspots.txt` |
| (2) Regression test present and passing | 1 test selected (`test_finding_functions_project_scoped`), all pass | ✅ | `evidence/executable-anvil-lab-project-scope-fix-v2-2026-06-08/regression_test.txt` |
| (3) Full suite — all pass, no regressions | 240 passed (baseline 239 + 1 new), 0 failures | ✅ | `evidence/executable-anvil-lab-project-scope-fix-v2-2026-06-08/pytest_full.txt` |

---

## Observations

### Functions Fixed (2)
1. **`find_coverage_gaps`** (src/lab.py line 127): Added `AND cc.project_id = ?` to WHERE clause, `project_id` appended to params tuple. This was the confirmed offender — 28/113 bellows cycle-1 findings were invoice-pulse chunks due to the missing project constraint.
2. **`find_coupling_hotspots`** (src/lab.py line 157): Same fix pattern. This was a latent leak — no cross-project rows surfaced in the bellows run due to threshold coincidence, but the query was structurally unsound.

### Functions Untouched (correctly SCOPED per blueprint)
- `find_clone_candidates` — `a.project_id = ?` (line 199)
- `find_staleness_alerts` — `cc.project_id = ?` (line 225)
- `find_complexity_hotspots` — `cc.project_id = ?` (line 252)
- `find_cochange_patterns` — `project_id = ?` (line 286)
- `find_best_practice_deviations` — `project_id = ?` (line 327)
- `find_intent_gaps` — `cc.project_id = ?` in all 3 sub-queries
- `generate_specialist_update_data` — `project_id = ?` in all 7 queries
- `write_cycle_report` Untested Complexity — `cc.project_id = ?` (line 908)
- `generate_planner_constraints` — N/A (no SQL)

### Regression Test Design
The test `test_finding_functions_project_scoped` seeds two projects (`proj_a`, `proj_b`) sharing `cycle_id=1` with distinct qualifying chunks and health_scores above all finding thresholds. It asserts zero cross-project contamination for both `find_coverage_gaps` and `find_coupling_hotspots`, plus non-regression guards for `find_staleness_alerts` and `find_complexity_hotspots`. Per the dev log, this test would FAIL against pre-fix code — without `cc.project_id = ?`, both projects' chunks appear in each call.

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/anvil/.bellows-worktrees/anvil-lab-project-scope-fix-v2-2026-06-08/knowledge/qa/evidence/executable-anvil-lab-project-scope-fix-v2-2026-06-08/
Files verified: 2
```

---

## Output Receipt
**Agent:** Anvil QA Analyst
**Step:** Step 3
**Status:** Complete

### What Was Done
Verified both LEAKS functions (`find_coverage_gaps`, `find_coupling_hotspots`) now include `cc.project_id = ?` constraints. Ran regression test (1 passed) and full suite (240 passed, 0 failures). All evidence deposited. QA report written with verification table.

### Files Deposited
- `knowledge/qa/2026-06-08-lab-project-scope-fix-qa.md` — this QA report
- `knowledge/qa/evidence/executable-anvil-lab-project-scope-fix-v2-2026-06-08/` — evidence directory (4 files)

### Files Created or Modified (Code)
- None (QA step — no source modifications)

### Decisions Made
- Verified line numbers in fixed source match the dev log's claimed locations
- Confirmed test count of 240 = baseline 239 + 1 new regression test

### Flags for CEO
- None

### Flags for Next Step
- None — all checks pass, plan ready for terminal verdict
