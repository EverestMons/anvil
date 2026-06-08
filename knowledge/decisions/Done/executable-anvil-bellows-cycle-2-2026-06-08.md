# Anvil Cycle 2 — bellows (fix-validation re-run)
**Date:** 2026-06-08 | **Tier:** Cycle | **Dispatch Mode:** bellows | **Test Scope:** smoke | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 2

**auto_close:** false
**pause_for_verdict:** after_qa_step

## Context

Re-run of the bellows cycle against fixed code (`ff00ab8`: `find_coverage_gaps` and `find_coupling_hotspots` now constrain by `cc.project_id`). Bellows cycle 1 (`cycle_id=1`) returned 28 coverage-gap findings that all belonged to invoice-pulse, because `cycle_id` collided with invoice-pulse's historical cycle 1. Cycle 2 (`cycle_id=2`) validates the fix: coverage-gap and coupling findings must now be bellows-only, and the top-10 by composite must be all bellows functions — the exact inverse of cycle 1, whose top-10 were all invoice-pulse / MISSING.

This run uses the proven continuous pattern: DEV (the cycle) and QA run in one worktree; the plan pauses after QA for the Planner's terminal verdict (`pause_for_verdict: after_qa_step`, `auto_close: false`). Both steps stage their deposits so they survive teardown.

Unchanged from cycle 1: Anvil's role taxonomy / best-practice seeds are IP-derived, so coverage/complexity/coupling/clone/co-change/staleness are the trustworthy finding types; best-practice deviations and role-weighted composites are weak. **Intent gaps remain empty by design** (bellows has no `PROJECT_BRIEF.md`/`domain-glossary.md`), so `write_intent_audit` does not fire and there is NO `audit-findings-*.md` deposit. The deliverable is the cycle report `cycle-2-findings-2026-06-08.md`.

## How to Run This Plan

Bellows dispatches automatically on deposit. Both steps run in sequence in one worktree, then the plan pauses after Step 2 (QA) for the terminal verdict.

---
---

## STEP 1 — ANVIL DEVELOPER

---

> **Identity:** You are the Anvil Developer. **Reads (in order):** `agents/ANVIL_DEVELOPER.md`, `knowledge/research/domain-glossary.md`, `knowledge/development/bellows-cycle-1-run-2026-06-08.md` (the cycle-1 run that surfaced the leak), and `knowledge/architecture/lab-project-scope-blueprint-2026-06-08.md` (the fix blueprint).
>
> **Working directory note:** the worktree IS the anvil root. Use relative paths for Anvil source imports (`from src.cycle import run_cycle`). For DB access use the absolute canonical path `/Users/marklehn/Developer/GitHub/anvil/anvil.db`. The cycle report lands in the WORKTREE at `knowledge/research/cycle-2-findings-2026-06-08.md` (via `ANVIL_RUNTIME_ROOT`).
>
> **Task:** Run Anvil Cycle 2 against bellows and validate the project-scope fix.
>
> **Pre-cycle snapshot.** Record:
> ```python
> import sqlite3
> conn = sqlite3.connect("/Users/marklehn/Developer/GitHub/anvil/anvil.db")
> pid = conn.execute("SELECT id FROM projects WHERE name='bellows'").fetchone()[0]
> print("bellows project_id:", pid)
> print("last cycle:", conn.execute("SELECT MAX(cycle_number) FROM cycle_reports WHERE project_id=?", (pid,)).fetchone()[0])
> conn.close()
> ```
> Expected: project_id=2, last cycle=1 → this run will be cycle 2.
>
> **Run the cycle.**
> ```python
> import sys, sqlite3
> sys.path.insert(0, ".")
> from src.cycle import run_cycle
> conn = sqlite3.connect("/Users/marklehn/Developer/GitHub/anvil/anvil.db")
> result = run_cycle(conn, "bellows")
> print(result)
> conn.close()
> ```
> If it raises, capture the full traceback and STOP.
>
> **Inspect `result`:** confirm no `error` key on `scan`/`extract`/`score`/`lab`, no `aborted_at`, and `result["lab"]["findings"]["intent_gaps"]` == 0 (expected). Confirm `cycle_number` == 2.
>
> **Fix-validation checks (the point of this run):**
>
> (1) **Top-10 must be all bellows.** Build the top-10 by composite from the cycle-2 report. For each, `grep -rn "def <function_name>" /Users/marklehn/Developer/GitHub/bellows/<file_path>`. Expected: ALL EXIST in bellows source (inverse of cycle 1, where all 10 were MISSING / invoice-pulse). **If ANY top-10 function is MISSING from bellows or resolves to an invoice-pulse path, the fix regressed — STOP and report.**
>
> (2) **Coverage-gap findings must all be bellows.** Query the DB for cycle-2 coverage-gap chunks and confirm every one has `project_id = 2`:
> ```python
> conn = sqlite3.connect("/Users/marklehn/Developer/GitHub/anvil/anvil.db")
> # adapt table/column names to the actual findings schema discovered in the report/DB
> ```
> Record the count of coverage-gap findings and confirm ZERO belong to project_id != 2. Cite the exact query you used. If any non-bellows rows appear, STOP and report.
>
> (3) From the cycle report: print all CRITICAL findings verbatim (if any); count findings by type and by severity. Compare the coverage-gap count to cycle 1's 28 (which were all invoice-pulse) — cycle 2's should be bellows-only and likely a different number.
>
> (4) Test-file filter regression: grep the cycle report for `tests/` in `file_path` lines — expect zero.
>
> (5) Untested Complexity section: grep the cycle report for `Untested Complexity` — expect exactly one match (the header); print the section's row count.
>
> (6) Confirm NO audit-findings file was written: `ls -la /Users/marklehn/Developer/GitHub/bellows/knowledge/anvil/` — expect no `audit-findings-*.md` (intent gaps empty).
>
> **Constraints:** Do NOT modify Anvil or bellows source. If findings count is suspiciously low (<3) or high (>250), flag without speculating.
>
> **Stage the deposits (required so they survive teardown):**
> ```bash
> git add knowledge/research/cycle-2-findings-2026-06-08.md knowledge/development/bellows-cycle-2-run-2026-06-08.md
> git status --short
> ```
> Confirm both show staged.
>
> Standard prompt-feedback protocol — append issues to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `knowledge/development/bellows-cycle-2-run-2026-06-08.md`
> - `knowledge/research/cycle-2-findings-2026-06-08.md` (produced by `run_cycle`)

---
---

## STEP 2 — ANVIL QA ANALYST

---

> Read `knowledge/development/bellows-cycle-2-run-2026-06-08.md` and check the Output Receipt status. If status is not Complete, or if DEV reported a STOP (fix regression), stop and report before proceeding.
>
> **Identity:** You are the Anvil QA Analyst. **Reads (in order):** `agents/ANVIL_QA_ANALYST.md`, `knowledge/research/domain-glossary.md`, the Step 1 dev log, and the cycle-2 report `knowledge/research/cycle-2-findings-2026-06-08.md`.
>
> **Working directory note:** worktree IS anvil root. Use the absolute path `/Users/marklehn/Developer/GitHub/anvil/anvil.db` for DB access.
>
> **Context:** This is the fix-validation re-run. Intent gaps are empty by design (no bellows brief/glossary) — there is NO audit-findings file; do not check for one or fail on its absence.
>
> **Do exactly this** (each check writes literal output to `knowledge/qa/evidence/executable-anvil-bellows-cycle-2-2026-06-08/`; `mkdir -p` it first):
>
> **(1) Cycle 2 DB row landed for bellows.** `python3 -c "import sqlite3; conn=sqlite3.connect('/Users/marklehn/Developer/GitHub/anvil/anvil.db'); r=conn.execute('SELECT cycle_number, findings_count, started_at FROM cycle_reports WHERE project_id=(SELECT id FROM projects WHERE name=\"bellows\") AND cycle_number=2').fetchone(); print(r); conn.close()" > knowledge/qa/evidence/executable-anvil-bellows-cycle-2-2026-06-08/cycle_2_row.txt 2>&1`. Expected: non-null tuple, cycle_number=2, started_at = today.
>
> **(2) Cycle report exists and is staged.** `ls -la knowledge/research/cycle-2-findings-2026-06-08.md > knowledge/qa/evidence/executable-anvil-bellows-cycle-2-2026-06-08/cycle_report_path.txt 2>&1`. Then `git diff --cached --name-only | grep cycle-2-findings > knowledge/qa/evidence/executable-anvil-bellows-cycle-2-2026-06-08/cycle_report_staged.txt 2>&1`. Expected: exists and ≥1 staged match.
>
> **(3) Fix validation — DEV's top-10 and coverage-gap project checks passed.** From the Step 1 dev log, confirm: (a) all top-10 functions EXIST in bellows source (none MISSING / invoice-pulse); (b) DEV's coverage-gap query reported ZERO non-bellows (project_id != 2) rows. Copy DEV's literal query output and the top-10 existence results into `knowledge/qa/evidence/executable-anvil-bellows-cycle-2-2026-06-08/fix_validation.txt`. ❌ if either shows contamination.
>
> **(4) No audit-findings file (expected).** `ls -la /Users/marklehn/Developer/GitHub/bellows/knowledge/anvil/ > knowledge/qa/evidence/executable-anvil-bellows-cycle-2-2026-06-08/bellows_anvil_dir.txt 2>&1`. Expected: no `audit-findings-*.md`. Correct, not a failure.
>
> **(5) Untested Complexity + test-file filter.** `grep -n "Untested Complexity" knowledge/research/cycle-2-findings-2026-06-08.md > knowledge/qa/evidence/executable-anvil-bellows-cycle-2-2026-06-08/untested_complexity_grep.txt 2>&1` (expect 1 header). `grep -c "file_path.*tests/" knowledge/research/cycle-2-findings-2026-06-08.md > knowledge/qa/evidence/executable-anvil-bellows-cycle-2-2026-06-08/test_filter_check.txt 2>&1` (expect 0).
>
> **(6) Full suite (Rule 21).** `python3 -m pytest tests/ -q > knowledge/qa/evidence/executable-anvil-bellows-cycle-2-2026-06-08/pytest_full.txt 2>&1`. Expected: all pass; record count (baseline 240 from the project-scope fix).
>
> **(7) Write QA report** to `knowledge/qa/2026-06-08-bellows-cycle-2-qa.md` with a verification table `| Check | Expected | Status (✅/❌) | Evidence |`, one row per check (1)–(6) citing its evidence file. Observations: findings-by-type/severity from the dev log; confirm intent_gaps=0 (expected); state explicitly whether the fix is validated (top-10 all bellows + coverage gaps all project_id=2). Do NOT mark a ❌ row ✅; any hedging keyword in a ✅ row auto-fails the self-check.
>
> **(8) Rule 20 self-check** from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` with:
> - `plan_slug`: `executable-anvil-bellows-cycle-2-2026-06-08`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/2026-06-08-bellows-cycle-2-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/evidence/executable-anvil-bellows-cycle-2-2026-06-08/`
> - `required_evidence_files`: `["cycle_2_row.txt", "cycle_report_path.txt", "cycle_report_staged.txt", "fix_validation.txt", "bellows_anvil_dir.txt", "untested_complexity_grep.txt", "test_filter_check.txt", "pytest_full.txt"]`
>
> Include literal stdout in the QA report. If `FAILED`, halt. Do NOT move the plan to Done — the Planner performs the terminal verdict.
>
> **Stage the deposits (required so they survive teardown):**
> ```bash
> git add knowledge/qa/2026-06-08-bellows-cycle-2-qa.md knowledge/qa/evidence/executable-anvil-bellows-cycle-2-2026-06-08/
> git status --short
> ```
> Confirm the QA report and evidence show staged.
>
> Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/qa/2026-06-08-bellows-cycle-2-qa.md`
> - `knowledge/qa/evidence/executable-anvil-bellows-cycle-2-2026-06-08/`
