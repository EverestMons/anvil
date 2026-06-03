# Anvil — Executable: F9-Follow Scoring Methodology Fix (d2 + c)
**Date:** 2026-05-18 | **Tier:** Executable | **Test Scope:** unit + targeted regression | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 1

**auto_close:** false

## Execution Map

Step 1 (DEV) → Step 2 (QA). Sequential.

## Context

F9 and F9-follow (volatility-attribution-replay) established two findings:

1. **0:9 SELF_DECAYED.** All 9 anchor chunks displaced from cycle-17's top-20 dropped via genuine commit-frequency decline, not displacement. The functions really did go quiet. Their volatility scores reflect a real change in activity — but for zero-coverage functions, low activity is not evidence of low risk; it's evidence of neglect.

2. **Percentile normalization can invert signal direction** under population collapse. `action_queue` raw vol dropped 79% (commits 13→3) yet its normalized vol *increased* from 0.83 → 1.00 because the rest of the population collapsed harder. This means the primary ranking can be actively misleading.

This executable ships two complementary changes to `compute_composite()` and the cycle report writer:

**(d2) Volatility floor for zero-coverage chunks.** When `coverage_score = 1.0`, the volatility contribution to composite is capped at a minimum of 0.5. Encodes: "untested code can't be considered low-volatility no matter how stable its commit history."

**(c) Coverage × complexity secondary ranking.** Add an "Untested Complexity" section to the cycle report, listing top-20 chunks sorted by `coverage_score × complexity_score`. Volatility-independent backup view; resilient to population collapse and inversion artifacts.

**Scope guards:**
- `compute_composite` signature unchanged (still takes the 5 sub-scores + weights dict). The floor is applied INTERNALLY when coverage_score >= 0.99.
- Floor threshold: `coverage_score >= 0.99` (not strict equality) to handle float rounding from the scorer's `round(cov, 4)`.
- Floor value: 0.5 (matches SA's recommendation in F9 § 7 and the F9-follow reframing). Hardcoded constant in scorer.py, not a config knob — config sprawl is a separate decision.
- Cycle report change: new "Untested Complexity (top-20)" section inserted between "Coverage Gaps" and "Coupling Hotspots". Uses the SAME data source (current cycle's health_scores) but a different sort.

**Regression-test discipline:** This is a methodology fix. The test must prove the broken behavior would have surfaced. Specifically: a test that constructs a synthetic chunk with `coverage_score=1.0, volatility_score=0.1` and verifies composite under the new code is higher than composite under the old formula. If the regression test doesn't fail under the pre-fix code, it doesn't prove anything.

## How to Run This Plan

Paste the Step 1 bootstrap prompt into Claude Code. After DEV reports Complete, paste the Step 2 bootstrap prompt.

**Step 1 bootstrap prompt:**
```
Read the plan at anvil/knowledge/decisions/executable-f9-follow-scoring-methodology-fix-2026-05-18.md. Execute Step 1 ONLY. After completing Step 1, STOP and report.
```

**Step 2 bootstrap prompt:**
```
Read the plan at anvil/knowledge/decisions/in-progress-executable-f9-follow-scoring-methodology-fix-2026-05-18.md. Execute Step 2 ONLY (QA review).
```

---
---

## STEP 1 — ANVIL DEV

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/executable-f9-follow-scoring-methodology-fix-2026-05-18.md", "anvil/knowledge/decisions/in-progress-executable-f9-follow-scoring-methodology-fix-2026-05-18.md")`.
>
> Read your specialist file first. **You are the Anvil Developer.** Working directory is `/Users/marklehn/Developer/GitHub/`. **Context:** Two scoring methodology fixes from F9 and F9-follow. Read both diagnostics if you need context: `anvil/knowledge/research/scoring-weights-volatility-decay-audit-2026-05-18.md` and `anvil/knowledge/research/volatility-attribution-replay-2026-05-18.md`. The replay verified the scorer's actual logic (`compute_volatility` in `src/scorer.py` lines 145-176, percentile-norm at lines 87-90, composite at the function `compute_composite`).
>
> **Do exactly this:**
>
> **(1) Implement the volatility floor in `compute_composite`.** In `anvil/src/scorer.py`, locate `compute_composite`. Add a guard at the top: if `coverage >= 0.99`, set `volatility = max(volatility, 0.5)` BEFORE the weighted sum. Add a module-level constant `ZERO_COVERAGE_VOLATILITY_FLOOR = 0.5` for the magic number — don't hardcode 0.5 inline. Add an inline docstring/comment block (3-5 lines) at the top of `compute_composite` explaining: (a) what the floor does, (b) why it exists (link to F9 + F9-follow diagnostics by filename), (c) the threshold 0.99 handles float-rounding from upstream `round(score, 4)`.
>
> **(2) Add the regression test.** In `anvil/tests/test_scorer.py`, add a test `test_composite_volatility_floor_for_zero_coverage`. The test must:
> - Construct a chunk-like scenario with `coverage=1.0, volatility=0.1, complexity=0.9, coupling=0.5, staleness=0.0`
> - Call `compute_composite` with the global `SCORING_WEIGHTS`
> - Assert the result is HIGHER than what it would have been with `volatility=0.1` (i.e., floor was applied)
> - Add a second assertion: with `coverage=0.0` and otherwise identical inputs, the floor is NOT applied (volatility stays 0.1)
> - Add a third assertion: with `coverage=0.99` (edge), floor IS applied
> - Add a fourth: with `coverage=0.989` (just below threshold), floor is NOT applied
>
> Run `cd anvil && python3 -m pytest tests/test_scorer.py -v` and confirm the new test passes. Confirm ALL prior tests still pass (217 total per F9 session-end state).
>
> **(3) Add the "Untested Complexity" secondary ranking to the cycle report.** In `anvil/src/lab.py`, locate `write_cycle_report` (the function that builds `lines` and writes the markdown report). Find the existing "Coverage Gaps" section. Immediately AFTER it (before "Coupling Hotspots"), add a new section:
> - Heading: `## Untested Complexity (top-20 by coverage × complexity)`
> - Query the current cycle's health_scores joined with code_chunks, computing `coverage_score * complexity_score` as a derived sort key. Limit 20, descending. Filter: `chunk_type != 'module'` AND `chunk_type != 'test_case'` to match other findings sections' implicit population.
> - Render as a markdown table with columns: `File | Name | Coverage | Complexity | Cov×Comp | Composite`
> - If zero rows, output "No untested complexity findings."
>
> Implement the query inside `write_cycle_report` as a new local helper or inline block — do NOT add a new top-level `find_*` function in lab.py (this is a report-only view, not a findings category that flows into constraints).
>
> **(4) Update test_lab.py to cover the new section.** Add a test `test_cycle_report_includes_untested_complexity` that:
> - Sets up a minimal cycle with at least 2 chunks having coverage=1.0 and varying complexity (e.g., 0.95 and 0.5)
> - Calls `write_cycle_report` (or the report-writing helper)
> - Reads back the generated file
> - Asserts the file contains the literal string `## Untested Complexity` AND the higher-complexity chunk appears before the lower-complexity chunk in that section
>
> **(5) Run the full test suite.** `cd anvil && python3 -m pytest tests/ -v`. Confirm all tests pass. Report the pass/fail count.
>
> **(6) Verify no behavior change for cycles already in DB.** This change only affects FUTURE cycle runs. Do NOT run a new audit cycle. Do NOT modify any existing rows in `anvil.db`. Confirm in the deposit that the change is scorer-only and report-only, with no DB migration.
>
> **(7) Commit.** Conventional commit message: `feat(scorer): volatility floor for zero-coverage chunks + cov×comp secondary ranking (F9-follow)`. Stage `src/scorer.py`, `src/lab.py`, `tests/test_scorer.py`, `tests/test_lab.py`. Do NOT stage anything else. Push to main.
>
> **(8) Deposit DEV log.** Write a brief DEV log at `anvil/knowledge/dev-logs/2026-05-18-f9-follow-scoring-fix.md` (create the directory if it doesn't exist) noting: files changed, line counts added/removed, test count before vs after, commit SHA. One section: "What was done", one section: "What was NOT done" (no config knob, no DB migration, no new findings category, no cycle re-run).
>
> Standard prompt feedback protocol — append any prompt issues to `anvil/knowledge/research/agent-prompt-feedback.md` before reporting Complete.
>
> **Deposits:**
> - `anvil/src/scorer.py` (modified — `compute_composite` floor + constant)
> - `anvil/src/lab.py` (modified — "Untested Complexity" section in `write_cycle_report`)
> - `anvil/tests/test_scorer.py` (modified — new test)
> - `anvil/tests/test_lab.py` (modified — new test)
> - `anvil/knowledge/dev-logs/2026-05-18-f9-follow-scoring-fix.md` (new)

---
---

## STEP 2 — ANVIL QA

---

> Read your specialist file first. **You are the Anvil QA reviewer.** Working directory is `/Users/marklehn/Developer/GitHub/`. **Context:** DEV just shipped the F9-follow scoring methodology fix. Verify substance and discipline before the plan closes.
>
> **Do exactly this:**
>
> **(1) Read DEV's deposits.** Read `anvil/src/scorer.py` `compute_composite` and the new `ZERO_COVERAGE_VOLATILITY_FLOOR` constant. Read `anvil/src/lab.py` `write_cycle_report` and the new "Untested Complexity" section. Read both new tests in `tests/test_scorer.py` and `tests/test_lab.py`. Read the DEV log.
>
> **(2) Verify the regression test actually fails under the pre-fix code.** This is the critical check. Temporarily comment out the floor line in `compute_composite`. Run `cd anvil && python3 -m pytest tests/test_scorer.py::test_composite_volatility_floor_for_zero_coverage -v`. The test MUST fail. If it passes, the test is not exercising the fix and DEV's regression-test discipline failed. Restore the floor line. Run the test again and confirm it passes.
>
> If you cannot make the test fail by removing the fix, report this as a QA FAIL with details.
>
> **(3) Verify edge cases.** Re-read the test assertions. Confirm: floor applies at coverage=1.0, applies at coverage=0.99, does NOT apply at coverage=0.989, does NOT apply at coverage=0.0. If any edge case is missing or wrong, report as QA FAIL.
>
> **(4) Verify the cycle report section.** Manually trace through `write_cycle_report`: with the new section, does it correctly slot between "Coverage Gaps" and "Coupling Hotspots"? Does the SQL query exclude test_case and module chunks? Does it limit to 20 rows? If the section is out of order or the query is wrong, report as QA FAIL.
>
> **(5) Scope creep audit.** Read the git diff of DEV's commit. Confirm only `src/scorer.py`, `src/lab.py`, `tests/test_scorer.py`, `tests/test_lab.py`, and the new dev-log file are touched. If anything else is modified (config.py, db.py, classifier.py, etc.), report as QA FAIL with the unexpected file list.
>
> **(6) Run the full suite.** `cd anvil && python3 -m pytest tests/ -v`. Confirm all tests pass.
>
> **(7) Write QA verdict** to `anvil/knowledge/qa/2026-05-18-f9-follow-scoring-fix-qa.md` (create directory if needed). Two sections: "QA Result" (PASS / FAIL with reasoning) and "Observations" (anything notable that's not a failure — e.g., a code-style observation or an alternative-implementation note that didn't change the outcome).
>
> Standard prompt feedback protocol — append any prompt issues to `anvil/knowledge/research/agent-prompt-feedback.md` before reporting Complete.
>
> **Deposits:**
> - `anvil/knowledge/qa/2026-05-18-f9-follow-scoring-fix-qa.md` (new)
