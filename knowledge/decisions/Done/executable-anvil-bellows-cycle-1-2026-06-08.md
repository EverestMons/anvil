# Anvil Cycle 1 — first exploratory cycle (bellows)
**Date:** 2026-06-08 | **Tier:** Cycle | **Dispatch Mode:** bellows | **Test Scope:** smoke | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 2

**auto_close:** false
**pause_for_verdict:** after_step_1

## Context

First Anvil cycle against bellows — a new scan target (config committed 2026-06-08, `dc2297b` + `4f65e8d`). Goal: a baseline structural-health read of the bellows daemon. Cycle numbering is project-scoped; bellows has no prior cycles, so this is cycle 1 (invoice-pulse stays at 20, untouched).

Scope: full canonical pipeline (SCAN → EXTRACT → CLASSIFY → PROVENANCE → SCORE → LAB) against bellows only. Bellows source and Anvil source are NOT modified by this cycle.

**Calibration caveat (exploratory run — carry into triage):** Anvil's role taxonomy, best-practice seeds, and role weight/threshold overrides are all derived from invoice-pulse. On bellows, the role-agnostic structural finding types — coverage gaps, complexity hotspots, coupling hotspots, clone candidates, co-change, staleness — are sound. The IP-calibrated layers will be weak: best-practice deviations near-empty, role-weighted composites falling back to default weights.

**Intent gaps are empty by design.** Bellows has no `PROJECT_BRIEF.md` or `knowledge/research/domain-glossary.md`, so `find_intent_gaps` returns `[]` (lab.py:436–440). `write_intent_audit` is only called when intent gaps are non-empty (lab.py:71–73), so **NO `audit-findings-<UTC>.md` file is produced for bellows.** The deliverable is the cycle report (`cycle-1-findings-2026-06-08.md`), which carries all structural findings. This plan declares and verifies ONLY the cycle report + dev log — there is no audit-findings deposit.

**Pre-cycle baseline:** bellows is not yet in the `projects` table; SCAN creates it. `cycle_number` will be 1.

## How to Run This Plan

Bellows dispatches this plan automatically when deposited. The daemon runs Step 1, then pauses for the verdict (`pause_for_verdict: after_step_1`) before Step 2 (QA). `auto_close: false` holds a terminal pause after Step 2 for the Planner's Rule 22 close verdict and Bellows-side move to Done.

---
---

## STEP 1 — ANVIL DEVELOPER

---

> **Identity:** You are the Anvil Developer. **Reads (in order):** `agents/ANVIL_DEVELOPER.md`, `knowledge/research/domain-glossary.md`, `PROJECT_STATUS.md`, and the most recent completed cycle executable in `knowledge/decisions/Done/` as a worked example of cycle execution mechanics. NOTE: this is the FIRST cycle against bellows (a new target); the invoice-pulse cycle examples show the mechanics, but bellows produces NO intent-gap audit-findings file (see Task).
>
> **Working directory note:** Bellows runs this plan in a worktree at `anvil/.bellows-worktrees/anvil-bellows-cycle-1-2026-06-08/`; the worktree IS the anvil root from your perspective. For Anvil source imports use relative paths (e.g., `from src.cycle import run_cycle`). **For DB access use the absolute canonical path** `/Users/marklehn/Developer/GitHub/anvil/anvil.db`. The cycle report lands in the WORKTREE at `knowledge/research/cycle-1-findings-2026-06-08.md` (via `ANVIL_RUNTIME_ROOT`). The DB record stores the canonical path (`ANVIL_ROOT`), which becomes valid after teardown lands the worktree commits to main.
>
> **Task:** Run Anvil Cycle 1 against bellows.
>
> **Pre-cycle snapshot.** bellows may not yet exist in `projects` (first cycle). Run first and record output:
>
> ```python
> import sqlite3
> conn = sqlite3.connect("/Users/marklehn/Developer/GitHub/anvil/anvil.db")
> row = conn.execute("SELECT id FROM projects WHERE name='bellows'").fetchone()
> if row is None:
>     baseline = {"project_id": None, "chunks": 0, "last_cycle": None, "git_changes": 0}
> else:
>     pid = row[0]
>     baseline = {
>         "project_id": pid,
>         "chunks": conn.execute("SELECT COUNT(*) FROM code_chunks WHERE project_id=?", (pid,)).fetchone()[0],
>         "last_cycle": conn.execute("SELECT MAX(cycle_number) FROM cycle_reports WHERE project_id=?", (pid,)).fetchone()[0],
>         "git_changes": conn.execute("SELECT COUNT(*) FROM git_changes WHERE project_id=?", (pid,)).fetchone()[0],
>     }
> print(baseline)
> conn.close()
> ```
>
> Expected: `last_cycle: None` (first cycle).
>
> **Run the cycle.**
>
> ```python
> import sys, sqlite3
> sys.path.insert(0, ".")
> from src.cycle import run_cycle
> conn = sqlite3.connect("/Users/marklehn/Developer/GitHub/anvil/anvil.db")
> result = run_cycle(conn, "bellows")
> print(result)
> conn.close()
> ```
>
> If it raises, capture the full traceback and STOP — do not patch as Developer.
>
> **Inspect `result` for silent stage failures.** Each stage is wrapped; a failure surfaces as `result["<stage>"]["error"]`. Confirm none of `scan` / `extract` / `score` / `lab` carries an `error` key and that `aborted_at` is absent. `result["lab"]["findings"]["intent_gaps"]` is EXPECTED to be `0` (no brief/glossary). If `scan` or `extract` carries an error or `aborted_at` is set, STOP and report.
>
> **Post-cycle verification (after `run_cycle` returns):**
>
> (1) Post-cycle snapshot: bellows now in `projects`; record project_id, chunk count, git_changes count; confirm `cycle_number` = 1 in `cycle_reports`.
>
> (2) **No audit-findings file is expected.** Confirm `result["lab"]["findings"]["intent_gaps"]` == 0, and that `/Users/marklehn/Developer/GitHub/bellows/knowledge/anvil/` contains NO `audit-findings-*.md`: `ls -la /Users/marklehn/Developer/GitHub/bellows/knowledge/anvil/`. Record the listing. (If an audit-findings file unexpectedly appears, note it — it would mean intent gaps fired.)
>
> (3) Locate the cycle report at `knowledge/research/cycle-1-findings-2026-06-08.md` (worktree-relative). Confirm it exists and print its exact filename verbatim. It lands in the worktree via `ANVIL_RUNTIME_ROOT`; step (9) stages it.
>
> (4) From the cycle report: print all CRITICAL findings verbatim (if any); count findings by type and by severity.
>
> (5) Test-file filter regression: grep the cycle report for `tests/` in `file_path` lines — expect zero.
>
> (6) Untested Complexity section: grep the cycle report for `Untested Complexity` — expect exactly one match (the header). Print the section's row count.
>
> (7) Top-10 highest-composite findings as a table (function, file, composite, finding type).
>
> (8) **Top-10 existence sanity check.** For each function in the top-10, verify it exists in current bellows source: `grep -rn "def <function_name>" /Users/marklehn/Developer/GitHub/bellows/<file_path>`. Record EXISTS or MISSING. On a first scan all should EXIST; any MISSING is unexpected — list it for the Planner.
>
> **(9) Stage the cycle report for commit.**
> ```bash
> git add knowledge/research/cycle-1-findings-2026-06-08.md
> ```
> Verify staged: `git status` should show it as "new file" under "Changes to be committed." If under "Untracked files," the add failed — retry.
>
> **Constraints:** Do NOT modify Anvil source. Do NOT modify bellows source. If findings count is suspiciously low (<3) or high (>250), flag without speculating. (Bellows is ~42 Python files; a modest finding count is expected.)
>
> Standard prompt-feedback protocol — append issues to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `knowledge/development/bellows-cycle-1-run-2026-06-08.md`
> - `knowledge/research/cycle-1-findings-2026-06-08.md` (produced by `run_cycle`, staged in worktree)

---
---

## STEP 2 — ANVIL QA ANALYST

---

> Before starting, read `knowledge/development/bellows-cycle-1-run-2026-06-08.md` and check the Output Receipt status. If status is not Complete, stop and report the blocker before proceeding.
>
> **Identity:** You are the Anvil QA Analyst. **Reads (in order):** `agents/ANVIL_QA_ANALYST.md`, `knowledge/research/domain-glossary.md`, the Step 1 dev log, and the cycle 1 report at `knowledge/research/cycle-1-findings-2026-06-08.md`.
>
> **Working directory note:** Worktree root IS anvil/. Use the absolute path `/Users/marklehn/Developer/GitHub/anvil/anvil.db` for DB access.
>
> **Context for this QA:** First cycle against bellows (new target). Intent gaps are empty by design (no bellows PROJECT_BRIEF/glossary), so there is NO audit-findings file — do not check for one as a deliverable and do not fail on its absence. All structural checks read the cycle report.
>
> **Do exactly this** (each check writes literal output to `knowledge/qa/evidence/executable-anvil-bellows-cycle-1-2026-06-08/`; `mkdir -p` it first):
>
> **(1) Cycle 1 DB row landed for bellows.** `python3 -c "import sqlite3; conn=sqlite3.connect('/Users/marklehn/Developer/GitHub/anvil/anvil.db'); r=conn.execute('SELECT cycle_number, findings_count, started_at FROM cycle_reports WHERE project_id=(SELECT id FROM projects WHERE name=\"bellows\") AND cycle_number=1').fetchone(); print(r); conn.close()" > knowledge/qa/evidence/executable-anvil-bellows-cycle-1-2026-06-08/cycle_1_row.txt 2>&1`. Expected: non-null tuple, cycle_number=1, started_at = today (UTC 2026-06-08).
>
> **(2) Cycle report exists in worktree and is staged.** `ls -la knowledge/research/cycle-1-findings-2026-06-08.md > knowledge/qa/evidence/executable-anvil-bellows-cycle-1-2026-06-08/cycle_report_path.txt 2>&1`. Expected: exists. ❌ if missing. Then: `git diff --cached --name-only | grep cycle-1-findings > knowledge/qa/evidence/executable-anvil-bellows-cycle-1-2026-06-08/cycle_report_staged.txt 2>&1`. Expected: ≥1 match.
>
> **(3) No audit-findings file (expected for bellows).** `ls -la /Users/marklehn/Developer/GitHub/bellows/knowledge/anvil/ > knowledge/qa/evidence/executable-anvil-bellows-cycle-1-2026-06-08/bellows_anvil_dir.txt 2>&1`. Expected: directory present, NO `audit-findings-*.md`. This is correct, not a failure.
>
> **(4) Untested Complexity section present.** `grep -n "Untested Complexity" knowledge/research/cycle-1-findings-2026-06-08.md > knowledge/qa/evidence/executable-anvil-bellows-cycle-1-2026-06-08/untested_complexity_grep.txt 2>&1`. Expected: exactly one match (the header).
>
> **(5) Test-file filter regression.** `grep -c "file_path.*tests/" knowledge/research/cycle-1-findings-2026-06-08.md > knowledge/qa/evidence/executable-anvil-bellows-cycle-1-2026-06-08/test_filter_check.txt 2>&1`. Expected: 0.
>
> **(6) Full test suite (Rule 21 — the cycle exercises lab.py and scorer.py).** `python3 -m pytest tests/ -q > knowledge/qa/evidence/executable-anvil-bellows-cycle-1-2026-06-08/pytest_full.txt 2>&1`. Expected: all pass; record exact count and flag if the baseline moved (last known green: 238).
>
> **(7) Write QA report** to `knowledge/qa/2026-06-08-bellows-cycle-1-qa.md` with a verification table: `| Check | Expected | Status (✅/❌) | Evidence |`, one row per check (1)–(6), each citing its evidence file. Add an "Observations" section noting: findings-by-type and by-severity from the dev log; explicit confirmation that intent_gaps = 0 (expected, no brief/glossary); and any MISSING top-10 functions flagged by DEV. Do NOT mark a ❌ row ✅ — any hedging keyword ("pending", "inferred", "should pass", "not run") in a ✅ row auto-fails the self-check.
>
> **(8) Rule 20 self-check.** Run the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` with:
> - `plan_slug`: `executable-anvil-bellows-cycle-1-2026-06-08`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/2026-06-08-bellows-cycle-1-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/evidence/executable-anvil-bellows-cycle-1-2026-06-08/`
> - `required_evidence_files`: `["cycle_1_row.txt", "cycle_report_path.txt", "cycle_report_staged.txt", "bellows_anvil_dir.txt", "untested_complexity_grep.txt", "test_filter_check.txt", "pytest_full.txt"]`
>
> Include the literal stdout in the QA report. If `FAILED`, halt and report. The agent does NOT move the plan to Done — the Planner performs the terminal verdict after Rule 22 verification.
>
> Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/qa/2026-06-08-bellows-cycle-1-qa.md`
> - `knowledge/qa/evidence/executable-anvil-bellows-cycle-1-2026-06-08/`
