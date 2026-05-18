# QA Recovery Report — F9-follow Scoring Methodology Fix

**Date:** 2026-05-18
**Plan:** `executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18`
**DEV Commit:** `d68191e` (on main as `155f3d1`, identical tree `79fd4a2`)
**Verdict:** PASS

---

## Verification Table

| Check | Expected | Status | Evidence |
|---|---|---|---|
| (1) Regression-test discipline | Test fails without floor guard, passes with it | ✅ | `knowledge/qa/evidence/executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18/regression_test_without_fix.txt`, `regression_test_with_fix.txt` |
| (2) Edge cases | Four coverage thresholds: 1.0 (floor applied), 0.0 (no floor), 0.99 (edge, floor applied), 0.989 (below threshold, no floor) | ✅ | `knowledge/qa/evidence/executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18/edge_cases.txt` |
| (3) Cycle report section placement | Untested Complexity between Coverage Gaps and Coupling Hotspots; SQL filters `chunk_type != 'module' AND chunk_type != 'test_case'`; LIMIT 20 | ✅ | `knowledge/qa/evidence/executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18/cycle_report_section.txt` |
| (4) Scope creep audit | Only 5 expected files changed: `src/scorer.py`, `src/lab.py`, `tests/test_scorer.py`, `tests/test_lab.py`, `knowledge/dev-logs/2026-05-18-f9-follow-scoring-fix.md` | ✅ | `knowledge/qa/evidence/executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18/git_diff_stat.txt` |
| (5) Full suite | All tests pass | ✅ | `knowledge/qa/evidence/executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18/pytest_full.txt` |
| (6) Commit landed on main | SHA present in main history | ✅ | `knowledge/qa/evidence/executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18/git_log.txt` |

---

## Observations

- The prior QA report at `knowledge/qa/2026-05-18-f9-follow-scoring-fix-qa.md` is preserved for audit. That report produced a substantive PASS verdict but lacked Rule 20 evidence files and the canonical self-check banner. This recovery is the Rule 20-compliant version.
- Check (1) confirmed the regression test is genuine: commenting out the floor guard at `src/scorer.py:332` causes `test_composite_volatility_floor_for_zero_coverage` to fail with `assert 0.53 > 0.53`. Restoring the guard makes it pass.
- Check (6) note: the plan references SHA `d68191e` as the DEV commit. On the current main branch, the equivalent commit is `155f3d1` (rebased). Both resolve to identical tree hash `79fd4a2e62cf1f770236cdde8eed54f748287bb7` with zero diff between them.
- Full suite: 219 tests passed, 0 failures.

---

## Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/anvil/.bellows-worktrees/f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18/knowledge/qa/evidence/executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18/
Files verified: 7
```

---

## Output Receipt
**Agent:** Anvil QA Analyst
**Step:** 1 (QA recovery)
**Status:** Complete

### What Was Done
QA recovery for F9-follow scoring methodology fix. All six verification checks passed. Evidence files deposited. Rule 20 self-check passed.

### Files Deposited
- `knowledge/qa/2026-05-18-f9-follow-scoring-fix-qa-recovery.md` — this QA recovery report
- `knowledge/qa/evidence/executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18/` — 7 evidence files

### Files Created or Modified (Code)
- None (QA-only step, no code changes)

### Decisions Made
- PASS verdict: all six checks verified independently

### Flags for CEO
- None

### Flags for Next Step
- None
