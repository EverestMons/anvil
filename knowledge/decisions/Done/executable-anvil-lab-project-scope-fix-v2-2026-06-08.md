# Anvil — Project Scoping Fix for Lab Finding Queries (v2)
**Date:** 2026-06-08 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** full | **Execution:** Step 1 (SA) → Step 2 (DEV) → Step 3 (QA) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_qa_step

## Context

Supersedes the halted v1 (`halted-executable-anvil-lab-project-scope-fix-2026-06-08.md`), whose Step-1 SA blueprint was written untracked to `knowledge/architecture/` and lost when the worktree was removed at the header pause. v2 fixes that two ways: (1) SA → DEV → QA run **continuously in one worktree** with no mid-plan pause, so the SA blueprint persists on disk for DEV to read directly; (2) **every step explicitly `git add`s its deposits** so they survive the final teardown merge. Review happens at the terminal pause after QA (`pause_for_verdict: after_qa_step`, `auto_close: false`).

The bug being fixed (unchanged from v1): bellows cycle 1 returned 28/113 findings belonging to invoice-pulse because `find_coverage_gaps` filters on `cycle_id` alone, and `cycle_id` is per-project (`run_cycle` assigns `MAX(cycle_number WHERE project_id)+1`), so bellows cycle 1 collided with invoice-pulse cycle 1 (both `cycle_id=1`). `health_scores` has no project column. Any finding query filtering `cycle_id` alone without constraining to the target project's chunks leaks across projects sharing that cycle_id.

Scope: `src/lab.py` query surface + `tests/test_lab.py` only. No behavior change for single-project (invoice-pulse) runs.

## How to Run This Plan

Bellows dispatches automatically on deposit. All three steps run in sequence in one worktree, then the plan pauses after Step 3 (QA) for the Planner's Rule 22 close verdict. `auto_close: false` holds that terminal pause.

---
---

## STEP 1 — ANVIL SYSTEMS ANALYST

---

> **Identity:** You are the Anvil Systems Analyst. **Reads (in order):** `agents/ANVIL_SYSTEMS_ANALYST.md`, `src/lab.py`, `src/config.py`, `src/cycle.py` (lines 21–45 for the cycle_id assignment), and `knowledge/development/bellows-cycle-1-run-2026-06-08.md` (the dev log that surfaced the leak).
>
> **Working directory note:** the worktree IS the anvil root; use relative paths for source. This step does NOT modify source code — it only produces a blueprint document.
>
> **Task:** Audit the full Lab query surface in `src/lab.py` for project scoping and produce a fix blueprint.
>
> **Verified background (do not re-litigate):** `cycle_id = MAX(cycle_number WHERE project_id) + 1` (cycle.py), so `cycle_id` is per-project, not globally unique. `health_scores` has no project column — it keys on `chunk_id` + `cycle_id`. Any finding query filtering `cycle_id` alone, without constraining to the target project's chunks (e.g. `cc.project_id = ?`), returns rows from every project sharing that cycle_id. Confirmed offender: `find_coverage_gaps` receives `project_id` but its WHERE params are `(cycle_id, COVERAGE_GAP_THRESHOLD, HIGH_RISK_THRESHOLD)` — `project_id` is unused. 28/113 bellows-cycle-1 findings were invoice-pulse chunks.
>
> **Do exactly this:**
>
> (1) Enumerate every function in `lab.py` that produces findings or feeds the cycle report / specialist data. At minimum: `find_coverage_gaps`, `find_coupling_hotspots`, `find_clone_candidates`, `find_staleness_alerts`, `find_complexity_hotspots`, `find_cochange_patterns`, `find_best_practice_deviations`, `find_intent_gaps`, `generate_planner_constraints`, `generate_specialist_update_data`. For each, record in a table: (a) does it receive `project_id` / `project_name` / `project_path`? (b) does its SQL constrain results to that project — DIRECTLY (`cc.project_id = ?`), TRANSITIVELY (join through a project-scoped table/column), or NOT AT ALL? (c) verdict: **SCOPED** / **LEAKS** / **N/A**. Quote the governing WHERE/JOIN line(s) verbatim as evidence for each verdict.
>
> (2) For every **LEAKS** function, specify the exact edit: the precise WHERE-clause addition and the corresponding parameter-tuple change, quoting the current line(s) verbatim so DEV applies a surgical change.
>
> (3) Cross-check the orphan-chunk reconciliation (2026-06-05): `find_clone_candidates` and `generate_specialist_update_data` gained `last_seen_cycle` filters then. Confirm whether those filters ALSO project-scope the results, or whether `project_id` is still missing — `last_seen_cycle` equality does not imply project scoping.
>
> (4) List every function that is ALREADY correctly **SCOPED**, citing the exact line that scopes it, so DEV leaves it untouched.
>
> (5) Specify the regression-test design: seed two projects sharing one `cycle_id` with distinct qualifying `code_chunks` + `health_scores`, then assert each finding function returns ONLY the requested project's rows. List which functions the test must cover (every LEAKS function at minimum).
>
> **Constraints:** Do NOT modify any source file. If the cycle_id-collision premise turns out to be wrong (e.g. a project discriminator exists that the background missed), say so explicitly and stop — do not invent a fix for a non-bug.
>
> **Stage the deposit (required so it survives teardown):**
> ```bash
> git add knowledge/architecture/lab-project-scope-blueprint-2026-06-08.md
> git status --short knowledge/architecture/lab-project-scope-blueprint-2026-06-08.md
> ```
> Confirm it shows staged (`A ` prefix). If not staged, retry the `git add`.
>
> Standard prompt-feedback protocol — append issues to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `knowledge/architecture/lab-project-scope-blueprint-2026-06-08.md`

---
---

## STEP 2 — ANVIL DEVELOPER

---

> Read `knowledge/architecture/lab-project-scope-blueprint-2026-06-08.md` (produced by Step 1 in this same worktree). Implement EXACTLY the fix surface the blueprint identifies — no more, no less. If the blueprint marks a function SCOPED, do not touch it.
>
> **Identity:** You are the Anvil Developer. **Reads (in order):** `agents/ANVIL_DEVELOPER.md`, the SA blueprint, `src/lab.py`, `tests/test_lab.py`.
>
> **Working directory note:** the worktree IS the anvil root; use relative paths for source. For DB access in any ad-hoc check use the absolute canonical path `/Users/marklehn/Developer/GitHub/anvil/anvil.db`.
>
> **Task:**
>
> (1) Apply the `project_id` constraint to every **LEAKS** function per the blueprint — the WHERE-clause addition plus the matching parameter-tuple update, surgical per the quoted lines. Touch only functions the blueprint marks LEAKS.
>
> (2) Add a regression test to `tests/test_lab.py`: seed two projects (e.g. `proj_a`, `proj_b`) that share `cycle_id = 1`, each with distinct `code_chunks` + `health_scores` rows that qualify as findings; then assert each fixed finding function returns ONLY the requested project's rows (zero cross-project rows). Cover every function the blueprint lists under the test design. Write it so it would FAIL against the pre-fix code (i.e. it genuinely exercises the leak).
>
> (3) Run the full suite: `python3 -m pytest tests/ -q`. All must pass; record the exact count (baseline 238 — expect +N for the new test(s)).
>
> **Constraints:** `src/lab.py` and `tests/test_lab.py` ONLY. No other source. Do NOT modify `config.py`, `scorer.py`, or `cycle.py`. If a blueprint-identified edit doesn't match the current source verbatim, STOP and report rather than improvising.
>
> **Stage the deposits (required so they survive teardown):**
> ```bash
> git add src/lab.py tests/test_lab.py knowledge/development/lab-project-scope-fix-2026-06-08.md
> git status --short
> ```
> Confirm `src/lab.py`, `tests/test_lab.py`, and the dev log all show staged.
>
> Standard prompt-feedback protocol — append issues to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `knowledge/development/lab-project-scope-fix-2026-06-08.md`

---
---

## STEP 3 — ANVIL QA ANALYST

---

> Read `knowledge/development/lab-project-scope-fix-2026-06-08.md` and check the Output Receipt status. If status is not Complete, stop and report the blocker before proceeding.
>
> **Identity:** You are the Anvil QA Analyst. **Reads (in order):** `agents/ANVIL_QA_ANALYST.md`, the SA blueprint, the Step 2 dev log, `src/lab.py`.
>
> **Working directory note:** worktree IS anvil root. Use the absolute path `/Users/marklehn/Developer/GitHub/anvil/anvil.db` for DB access.
>
> **Do exactly this** (each check writes literal output to `knowledge/qa/evidence/executable-anvil-lab-project-scope-fix-v2-2026-06-08/`; `mkdir -p` it first):
>
> **(1) Every blueprint-LEAKS function now scopes by project.** For each function the blueprint marked LEAKS, show the fixed WHERE clause in `src/lab.py`: `grep -n -A2 "<anchor>" src/lab.py` → `knowledge/qa/evidence/executable-anvil-lab-project-scope-fix-v2-2026-06-08/scoped_<fn>.txt`. Expected: a project constraint present in each. ❌ if any LEAKS function still lacks one.
>
> **(2) Regression test present and passing.** `python3 -m pytest tests/test_lab.py -q -k "project_scope or project_leak or cross_project" > knowledge/qa/evidence/executable-anvil-lab-project-scope-fix-v2-2026-06-08/regression_test.txt 2>&1` (adjust `-k` to the actual test name from the dev log). Expected: ≥1 test selected, all pass.
>
> **(3) Full suite (Rule 21).** `python3 -m pytest tests/ -q > knowledge/qa/evidence/executable-anvil-lab-project-scope-fix-v2-2026-06-08/pytest_full.txt 2>&1`. Expected: all pass; record exact count and confirm it is baseline (238) + the new test(s), no regressions.
>
> **(4) Write QA report** to `knowledge/qa/2026-06-08-lab-project-scope-fix-qa.md` with a verification table `| Check | Expected | Status (✅/❌) | Evidence |`, one row per check (1)–(3) citing its evidence file. Add an "Observations" section listing which functions were fixed and confirming (per the dev log) the test would fail pre-fix. Do NOT mark a ❌ row ✅ — any hedging keyword ("pending", "inferred", "should pass", "not run") in a ✅ row auto-fails the self-check.
>
> **(5) Rule 20 self-check.** Run the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` with:
> - `plan_slug`: `executable-anvil-lab-project-scope-fix-v2-2026-06-08`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/2026-06-08-lab-project-scope-fix-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/evidence/executable-anvil-lab-project-scope-fix-v2-2026-06-08/`
> - `required_evidence_files`: `["regression_test.txt", "pytest_full.txt"]`
>
> Include the literal stdout in the QA report. If `FAILED`, halt and report. The agent does NOT move the plan to Done — the Planner performs the terminal verdict after Rule 22 verification.
>
> **Stage the deposits (required so they survive teardown):**
> ```bash
> git add knowledge/qa/2026-06-08-lab-project-scope-fix-qa.md knowledge/qa/evidence/executable-anvil-lab-project-scope-fix-v2-2026-06-08/
> git status --short
> ```
> Confirm the QA report and evidence files show staged.
>
> Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/qa/2026-06-08-lab-project-scope-fix-qa.md`
> - `knowledge/qa/evidence/executable-anvil-lab-project-scope-fix-v2-2026-06-08/`
