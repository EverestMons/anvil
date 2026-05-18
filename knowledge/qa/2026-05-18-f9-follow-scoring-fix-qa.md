# QA Verdict — F9-Follow Scoring Methodology Fix

**Date:** 2026-05-18
**Plan:** executable-f9-follow-scoring-methodology-fix-2026-05-18
**Commit:** d68191e

## QA Result

**PASS**

All checks passed:

1. **Regression test discipline verified.** Commenting out the floor guard (`if coverage >= 0.99: volatility = max(...)`) causes `test_composite_volatility_floor_for_zero_coverage` to fail with `assert 0.53 > 0.53`. Restoring the guard makes the test pass. The test genuinely exercises the fix.

2. **Edge cases complete.** Four assertions cover: coverage=1.0 (floor applied), coverage=0.0 (floor not applied), coverage=0.99 (edge — floor applied), coverage=0.989 (just below threshold — floor not applied). All four required by the plan are present and correct.

3. **Cycle report section correctly placed.** "Untested Complexity" section (lab.py lines 888-914) is between "Coverage Gaps" and "Coupling Hotspots". SQL query filters `chunk_type != 'module' AND chunk_type != 'test_case'`, sorts by `coverage_score * complexity_score` descending, limits to 20 rows. Empty-state fallback present.

4. **Scope clean.** Commit touches exactly 5 files: `src/scorer.py`, `src/lab.py`, `tests/test_scorer.py`, `tests/test_lab.py`, `knowledge/dev-logs/2026-05-18-f9-follow-scoring-fix.md`. No unexpected files.

5. **Full suite: 219 passed, 0 failed.**

## Observations

- The `ZERO_COVERAGE_VOLATILITY_FLOOR` constant is correctly module-level rather than inline, making it easy to find and adjust later without a config-sprawl decision now. Good discipline.
- The `compute_composite` signature is unchanged — callers are unaffected. The floor is purely internal.
- The existing `test_composite_weighted` test (vol=0.8, cov=1.0) is unaffected because vol=0.8 > floor=0.5 — the `max()` is a no-op. This confirms backward compatibility for chunks where volatility already exceeds the floor.
- DEV log accurately documents what was done and what was not done. Line counts match the git diff.
