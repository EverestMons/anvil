# QA Report — Anvil Test Failures Fixture Fix

**Plan:** `executable-anvil-test-failures-fixture-2026-04-14`
**DEV Commit:** `c49f060` — `fix: realign lab_project fixture thresholds (staleness, cochange)`
**QA Analyst:** Anvil QA Analyst (manual recovery)
**Date:** 2026-04-14

## Context

This QA run is a **manual recovery** from a stranded Bellows plan. The original plan was deposited but stranded due to a write-race during the Bellows plan deposit phase. DEV's fix commit (`c49f060`) landed successfully, but the plan was never routed through Bellows for QA. This manual bootstrap verifies deliverables, runs the full test suite, and closes out the plan.

## Verification Table

| # | Check | Expected | Actual | Status | Evidence |
|---|-------|----------|--------|--------|----------|
| a | `staleness_score=0.85` in test_lab.py | ≥1 hit | 1 hit (line 67) | PASS | `knowledge/qa/evidence/executable-anvil-test-failures-fixture-2026-04-14/grep_deliverables.txt` |
| b | `staleness_score=0.7` absent from lab_project fixture | 0 hits | 0 hits | PASS | `knowledge/qa/evidence/executable-anvil-test-failures-fixture-2026-04-14/grep_deliverables.txt` |
| c | Updated comment `staleness=0.85 >= 0.8 threshold` | 1 hit | 1 hit (line 183) | PASS | `knowledge/qa/evidence/executable-anvil-test-failures-fixture-2026-04-14/grep_deliverables.txt` |
| d | `hash4` dynamically generated for main.py and utils.py | 2 files in loop | Loop at lines 112-115 creates hash0..hash4 for both files (5 commits each) | PASS | `knowledge/qa/evidence/executable-anvil-test-failures-fixture-2026-04-14/grep_deliverables.txt` |
| e | Latest commit is DEV fix | `c49f060 fix: realign lab_project fixture thresholds` | `c49f0601e... fix: realign lab_project fixture thresholds (staleness, cochange)` | PASS | `knowledge/qa/evidence/executable-anvil-test-failures-fixture-2026-04-14/grep_deliverables.txt` |
| f | Targeted run: test_find_staleness_alerts | PASS | PASS | PASS | `knowledge/qa/evidence/executable-anvil-test-failures-fixture-2026-04-14/pytest_targeted.txt` |
| g | Targeted run: test_find_cochange_patterns | PASS | PASS | PASS | `knowledge/qa/evidence/executable-anvil-test-failures-fixture-2026-04-14/pytest_targeted.txt` |
| h | Targeted run: no regressions in test_lab.py | 20/20 pass | 20 passed in 0.04s | PASS | `knowledge/qa/evidence/executable-anvil-test-failures-fixture-2026-04-14/pytest_targeted.txt` |
| i | Full suite: zero failures, zero errors | 217 passed | 217 passed in 0.91s | PASS | `knowledge/qa/evidence/executable-anvil-test-failures-fixture-2026-04-14/pytest_full.txt` |

## Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/executable-anvil-test-failures-fixture-2026-04-14/
Files verified: 3
```

## Summary

All deliverable checks pass. Both previously-failing tests (`test_find_staleness_alerts`, `test_find_cochange_patterns`) now pass with the realigned fixture thresholds. The full Anvil test suite is GREEN: **217 passed, 0 failures, 0 errors**. No regressions detected.
