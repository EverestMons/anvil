# DEV Log — F9-Follow Scoring Methodology Fix

**Date:** 2026-05-18
**Plan:** executable-f9-follow-scoring-methodology-fix-2026-05-18

## What Was Done

**Files changed (4):**
- `src/scorer.py` — Added `ZERO_COVERAGE_VOLATILITY_FLOOR = 0.5` constant and volatility floor guard in `compute_composite`. When `coverage >= 0.99`, volatility is raised to at least 0.5 before the weighted sum. (+20 lines, -1 line)
- `src/lab.py` — Added "Untested Complexity (top-20 by coverage × complexity)" section to `write_cycle_report`, inserted between Coverage Gaps and Coupling Hotspots. Inline SQL query, no new top-level function. (+28 lines)
- `tests/test_scorer.py` — Added `test_composite_volatility_floor_for_zero_coverage` with 4 assertions: floor applied at coverage=1.0, NOT applied at coverage=0.0, applied at edge coverage=0.99, NOT applied at coverage=0.989. (+46 lines)
- `tests/test_lab.py` — Added `test_cycle_report_includes_untested_complexity` verifying section presence and correct descending sort order by cov×comp. (+58 lines)

**New file (1):**
- `knowledge/dev-logs/2026-05-18-f9-follow-scoring-fix.md` (this file)

**Test count:** 219 passed (217 prior + 2 new), 0 failed.

## What Was NOT Done

- **No config knob** — `ZERO_COVERAGE_VOLATILITY_FLOOR` is a hardcoded constant in `scorer.py`, not exposed in `config.py`. Config sprawl is a separate decision.
- **No DB migration** — No schema changes. The floor affects future `compute_composite` calls only; existing `health_scores` rows are untouched.
- **No new findings category** — The "Untested Complexity" section is report-only (read-side view), not a new findings category that flows into constraints.
- **No cycle re-run** — No existing data was modified; no new audit cycle was executed.
