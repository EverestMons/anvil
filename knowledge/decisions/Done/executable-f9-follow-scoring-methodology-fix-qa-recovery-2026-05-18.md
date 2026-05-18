# Anvil — QA recovery for F9-follow scoring methodology fix
**Date:** 2026-05-18 | **Tier:** small | **Test Scope:** targeted | **Execution:** Step 1 (QA) | **Priority:** 1

**auto_close:** false

## Context

The original plan `executable-f9-follow-scoring-methodology-fix-2026-05-18` had Step 1 (DEV) complete successfully — agent shipped the volatility floor and Untested Complexity section, all tests pass, scope clean (`d68191e`). Step 2 (QA) ran and produced a substantively-PASS verdict at `anvil/knowledge/qa/2026-05-18-f9-follow-scoring-fix-qa.md`, but Bellows tripped `rule_20_self_check` gate failure because the original QA step did not include the Rule 20 canonical self-check block. The QA report exists; the Rule 20 banner does not. Planner authoring error (missed Rule 20 § "plan-side template" requirement).

This plan is the QA recovery: a fresh QA pass that adds the missing evidence files and Rule 20 self-check banner, leaving the original QA prose findings intact (DEV's work was already verified by the original QA agent — this recovery exists to satisfy the gate, not to re-verify substance).

The original DEV commit is `d68191e`. The original (insufficient) QA report is at `anvil/knowledge/qa/2026-05-18-f9-follow-scoring-fix-qa.md`. The halted original plan is at `anvil/knowledge/decisions/halted-executable-f9-follow-scoring-methodology-fix-2026-05-18.md` (kept for audit).

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. Single-step QA-only recovery.

**Bootstrap prompt:**
```
Read the plan at anvil/knowledge/decisions/executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18.md. Execute Step 1 ONLY.
```

---
---

## STEP 1 — ANVIL QA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18.md", "anvil/knowledge/decisions/in-progress-executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18.md")`.
>
> Read your specialist file first. **You are the Anvil QA reviewer.** Working directory is `/Users/marklehn/Developer/GitHub/`. **Context:** DEV's F9-follow scoring methodology fix shipped at commit `d68191e`. The prior QA run produced a substantive PASS report at `anvil/knowledge/qa/2026-05-18-f9-follow-scoring-fix-qa.md` but lacked Rule 20 evidence files and the canonical self-check banner. This recovery adds the missing evidence + banner. Re-run all checks; do NOT trust the prior report's claims without verifying.
>
> **Do exactly this:**
>
> **(1) Regression-test discipline check.** Temporarily comment out the floor guard line (`volatility = max(volatility, ZERO_COVERAGE_VOLATILITY_FLOOR)` or equivalent) in `anvil/src/scorer.py::compute_composite`. Run `cd anvil && python3 -m pytest tests/test_scorer.py::test_composite_volatility_floor_for_zero_coverage -v 2>&1`. The test MUST fail. Capture stdout+stderr to `anvil/knowledge/qa/evidence/executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18/regression_test_without_fix.txt`. Restore the floor line. Re-run the same test and capture to `regression_test_with_fix.txt`. The second run MUST pass. If you cannot make the test fail by removing the fix, mark this row ❌.
>
> **(2) Edge cases.** Read `anvil/tests/test_scorer.py` and locate `test_composite_volatility_floor_for_zero_coverage`. Confirm it covers four cases: coverage=1.0 (floor applied), coverage=0.0 (floor NOT applied), coverage=0.99 (edge, floor applied), coverage=0.989 (just below threshold, floor NOT applied). Capture the test source via `grep -A 30 "test_composite_volatility_floor_for_zero_coverage" anvil/tests/test_scorer.py` to `edge_cases.txt`. Mark ✅ if all four cases present; ❌ if any missing.
>
> **(3) Cycle report section placement.** Read `anvil/src/lab.py` lines 880-920 (or grep for "Untested Complexity"). Confirm the new section: (a) is between "Coverage Gaps" and "Coupling Hotspots", (b) the SQL query filters `chunk_type != 'module' AND chunk_type != 'test_case'`, (c) limits to 20 rows. Capture the grep output to `cycle_report_section.txt`. Mark ✅ only if all three sub-checks pass.
>
> **(4) Scope creep audit.** Run `git --no-pager show --stat d68191e 2>&1`. Capture to `git_diff_stat.txt`. Confirm only these 5 files: `src/scorer.py`, `src/lab.py`, `tests/test_scorer.py`, `tests/test_lab.py`, and `knowledge/dev-logs/2026-05-18-f9-follow-scoring-fix.md`. Mark ❌ if any unexpected file appears.
>
> **(5) Full suite.** Run `cd anvil && python3 -m pytest tests/ -v 2>&1`. Capture to `pytest_full.txt`. Expected: all tests pass (219 per prior QA claim, plus or minus the new tests added in this fix).
>
> **(6) Commit landed on main.** Run `cd anvil && git --no-pager log --oneline -10 2>&1`. Capture to `git_log.txt`. Confirm SHA `d68191e` is present in current main history.
>
> **(7) Write QA report** to `anvil/knowledge/qa/2026-05-18-f9-follow-scoring-fix-qa-recovery.md` with a verification table: `| Check | Expected | Status (✅/❌) | Evidence (file path) |`. Six rows matching checks (1)-(6). Cite evidence files by relative path under `knowledge/qa/evidence/executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18/`. Include a brief "Observations" section noting that the prior QA report at `2026-05-18-f9-follow-scoring-fix-qa.md` is preserved for audit; this recovery is the Rule 20-compliant version. NO hedging keywords in ✅ rows.
>
> **(8) Rule 20 self-check.** Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:
> - `plan_slug`: `executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/2026-05-18-f9-follow-scoring-fix-qa-recovery.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/evidence/executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18/`
> - `required_evidence_files`: `["regression_test_without_fix.txt", "regression_test_with_fix.txt", "edge_cases.txt", "cycle_report_section.txt", "git_diff_stat.txt", "pytest_full.txt", "git_log.txt"]`
>
> Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, do not proceed with closure — halt and report to CEO.
>
> Standard prompt feedback protocol — append any prompt issues to `anvil/knowledge/research/agent-prompt-feedback.md` before reporting Complete.
>
> **Deposits:**
> - `anvil/knowledge/qa/2026-05-18-f9-follow-scoring-fix-qa-recovery.md`
> - `anvil/knowledge/qa/evidence/executable-f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18/`
