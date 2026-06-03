# Anvil Cycle 19 — routine on-demand cycle (invoice-pulse)
**Date:** 2026-06-02 | **Tier:** Cycle | **Dispatch Mode:** bellows | **Test Scope:** smoke | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 2

**auto_close:** false
**pause_for_verdict:** after_step_1

## Context

Routine on-demand Anvil cycle against invoice-pulse — the first cycle since cycle 18 (2026-05-18, 15 days ago). No methodology change to validate this cycle; the goal is to refresh structural health scores and surface current findings against ~2 weeks of new invoice-pulse activity. Findings get triaged by the Planner after the run (the usual curated-backlog step), so this plan is DEV (run) → QA (verify), with no in-plan triage memo.

Scope: full canonical pipeline (SCAN → EXTRACT → CLASSIFY → PROVENANCE → SCORE → LAB) against invoice-pulse only. Findings deposited to `invoice-pulse/knowledge/anvil/audit-findings-2026-06-02.md`. Anvil source and invoice-pulse source are NOT modified by this cycle.

**Pre-cycle baseline (from PROJECT_STATUS cycle 18 closeout):** last cycle = 18 (2026-05-18). Cycle 19 should bump `cycle_number` to 19.

**Known findings-quality caveat (carry into triage, not a blocker):** Anvil has an open methodology bug (BACKLOG 2026-05-18) — volatility scoring reaches into git history beyond the current scan, so functions deleted from the codebase can still surface as high-volatility intent gaps. Cycle 18 flagged 5 `web/action_queue.py` functions, 3 of which were deleted 2026-04-01. Step 1 includes a chunk-existence check on the top findings so phantom (deleted) functions are flagged in the dev log rather than silently trusted.

## How to Run This Plan

Bellows dispatches this plan automatically when deposited; no manual bootstrap required. The daemon runs Step 1, then pauses for the CEO/Planner verdict (`pause_for_verdict: after_step_1`) before running Step 2 (QA). `auto_close: false` holds a terminal pause after Step 2 for the Planner's Rule 22 close verdict and Bellows-side move to Done.

---
---

## STEP 1 — ANVIL DEVELOPER

---

> **Identity:** You are the Anvil Developer. **Reads (in order):** `agents/ANVIL_DEVELOPER.md`, `knowledge/research/domain-glossary.md`, `PROJECT_STATUS.md` (cycle 18 was 2026-05-18; this is cycle 19), and the prior cycle plan `knowledge/decisions/Done/executable-anvil-cycle-18-2026-05-18.md` as the template for cycle execution mechanics.
>
> **Working directory note:** Bellows runs this plan in a worktree at `anvil/.bellows-worktrees/anvil-cycle-19-2026-06-02/`; the worktree IS the anvil root from your perspective. For Anvil source imports use relative paths (e.g., `from src.cycle import run_cycle`). **For DB access use the absolute canonical path** `/Users/marklehn/Developer/GitHub/anvil/anvil.db` — the cycle reads and writes the main-repo DB, not a worktree-local one. The F8 hardcode (`ANVIL_ROOT`, commit `86ba5fd`) ensures paths resolve to canonical main-repo locations automatically.
>
> **Task:** Run Anvil Cycle 19 against invoice-pulse.
>
> **Pre-cycle snapshot.** Run first and record output:
>
> ```python
> import sqlite3
> conn = sqlite3.connect("/Users/marklehn/Developer/GitHub/anvil/anvil.db")
> baseline = {}
> baseline["chunks"] = conn.execute("SELECT COUNT(*) FROM code_chunks WHERE project='invoice-pulse'").fetchone()[0]
> baseline["last_cycle"] = conn.execute("SELECT MAX(cycle_number) FROM cycle_reports WHERE project='invoice-pulse'").fetchone()[0]
> baseline["git_changes"] = conn.execute("SELECT COUNT(*) FROM git_changes WHERE project='invoice-pulse'").fetchone()[0]
> print(baseline)
> conn.close()
> ```
>
> Expected: `last_cycle: 18`.
>
> **Run the cycle.**
>
> ```python
> import sys, sqlite3
> sys.path.insert(0, ".")
> from src.cycle import run_cycle
> conn = sqlite3.connect("/Users/marklehn/Developer/GitHub/anvil/anvil.db")
> result = run_cycle(conn, "invoice-pulse")
> print(result)
> conn.close()
> ```
>
> `run_cycle(conn, project_name)` — path resolved internally via config. If it raises, capture the full traceback and STOP — do not patch as Developer.
>
> **Post-cycle verification (after `run_cycle` returns):**
>
> (1) Post-cycle snapshot using the same queries as baseline; compute deltas. Confirm `cycle_number` bumped to 19.
>
> (2) Locate the new audit findings file. Per F8, it must be at `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-06-02.md` (canonical path, NOT worktree-local). Confirm it exists there. If it landed under `.bellows-worktrees/...`, FLAG for CEO — F8 is not working.
>
> (3) From the findings file: print all CRITICAL findings verbatim; count findings by severity.
>
> (4) Test-file filter regression: grep the findings file for `tests/` in `file_path` lines — expect zero matches.
>
> (5) Mission-context check: grep for `Given that` — expect ≥1 match.
>
> (6) Untested Complexity section: grep the findings file for `Untested Complexity` — expect exactly one match (the header). Print the section's row count (rows between that header and the next `##`).
>
> (7) Volatility-floor invariant. Expect zero violations:
>
> ```python
> import sqlite3
> conn = sqlite3.connect("/Users/marklehn/Developer/GitHub/anvil/anvil.db")
> r = conn.execute("""
>     SELECT COUNT(*) FROM health_scores
>     WHERE project='invoice-pulse' AND cycle_number=19
>     AND coverage_score >= 0.99 AND volatility_score < 0.5
> """).fetchone()[0]
> print(f"Floor violations: {r}")
> conn.close()
> ```
>
> If non-zero, FLAG for CEO.
>
> (8) Top-10 highest-composite findings as a table (function, file, composite, finding type).
>
> (9) **Phantom-function check (known-bug mitigation).** For each function in the top-10 table from (8), verify it still exists in current invoice-pulse source: `grep -rn "def <function_name>" /Users/marklehn/Developer/GitHub/invoice-pulse/<file_path>` (use the finding's file path). Record, per function: EXISTS or DELETED. Any DELETED function is a phantom finding (scoring reached into git history beyond the current scan, per BACKLOG 2026-05-18) — list these explicitly so the Planner excludes them at triage. Pay particular attention to any `web/action_queue.py` entries.
>
> **Constraints:** Do NOT modify Anvil source. Do NOT modify invoice-pulse source. If findings count is suspiciously low (<5) or high (>250), flag without speculating.
>
> **Deposit:** `knowledge/development/cycle-19-run-2026-06-02.md` — must include: baseline snapshot, post-cycle snapshot with deltas, audit findings file path (confirming canonical not worktree), total findings, findings by severity, all CRITICAL findings verbatim, top-10 table, phantom-function check results (EXISTS/DELETED per top-10 entry), test-file-filter result, mission-context result, Untested Complexity row count, floor-violations count, `run_cycle` return value, end-to-end runtime in seconds. End with an Output Receipt (Status field).
>
> Standard prompt-feedback protocol — append issues to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `knowledge/development/cycle-19-run-2026-06-02.md`
> - `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-06-02.md` (produced by `run_cycle`)

---
---

## STEP 2 — ANVIL QA ANALYST

---

> Before starting, read `knowledge/development/cycle-19-run-2026-06-02.md` and check the Output Receipt status. If status is not Complete, stop and report the blocker before proceeding.
>
> **Identity:** You are the Anvil QA Analyst. **Reads (in order):** `agents/ANVIL_QA_ANALYST.md`, `knowledge/research/domain-glossary.md`, the Step 1 dev log, and the cycle 19 audit findings file at `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-06-02.md`.
>
> **Working directory note:** Worktree root IS anvil/. Use the absolute path `/Users/marklehn/Developer/GitHub/anvil/anvil.db` for DB access.
>
> **Do exactly this** (each check writes literal output to `knowledge/qa/evidence/executable-anvil-cycle-19-2026-06-02/`; `mkdir -p` it first):
>
> **(1) Cycle 19 DB row landed.** `python3 -c "import sqlite3; conn=sqlite3.connect('/Users/marklehn/Developer/GitHub/anvil/anvil.db'); r=conn.execute('SELECT cycle_number, findings_count, cycle_date FROM cycle_reports WHERE project=\"invoice-pulse\" AND cycle_number=19').fetchone(); print(r); conn.close()" > knowledge/qa/evidence/executable-anvil-cycle-19-2026-06-02/cycle_19_row.txt 2>&1`. Expected: non-null tuple, cycle_number=19, today's date.
>
> **(2) Audit findings file at canonical path.** `ls -la /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-06-02.md > knowledge/qa/evidence/executable-anvil-cycle-19-2026-06-02/findings_file_path.txt 2>&1`. Expected: exists, modified today. ❌ if missing or worktree-local.
>
> **(3) Untested Complexity section present.** `grep -n "Untested Complexity" /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-06-02.md > knowledge/qa/evidence/executable-anvil-cycle-19-2026-06-02/untested_complexity_grep.txt 2>&1`. Expected: exactly one match.
>
> **(4) Volatility-floor invariant.** `python3 -c "import sqlite3; conn=sqlite3.connect('/Users/marklehn/Developer/GitHub/anvil/anvil.db'); r=conn.execute('SELECT COUNT(*) FROM health_scores WHERE project=\"invoice-pulse\" AND cycle_number=19 AND coverage_score >= 0.99 AND volatility_score < 0.5').fetchone()[0]; print(f'Floor violations: {r}'); conn.close()" > knowledge/qa/evidence/executable-anvil-cycle-19-2026-06-02/floor_violations.txt 2>&1`. Expected: `Floor violations: 0`.
>
> **(5) Test-file filter regression.** `grep -c "file_path.*tests/" /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-06-02.md > knowledge/qa/evidence/executable-anvil-cycle-19-2026-06-02/test_filter_check.txt 2>&1`. Expected: 0.
>
> **(6) Full test suite (Rule 21 — the cycle exercises lab.py and scorer.py).** `python3 -m pytest tests/ -q > knowledge/qa/evidence/executable-anvil-cycle-19-2026-06-02/pytest_full.txt 2>&1`. Expected: all pass (≥219 — record the exact count; flag if the baseline moved).
>
> **(7) Write QA report** to `knowledge/qa/2026-06-02-cycle-19-qa.md` with a verification table: `| Check | Expected | Status (✅/❌) | Evidence |`, one row per check (1)–(6), each citing its evidence file. Add a brief "Observations" section noting findings-by-severity from the Step 1 dev log and any phantom (DELETED) functions the dev log flagged in the top-10. Do NOT mark a ❌ row ✅ — any hedging keyword ("pending", "inferred", "should pass", "not run", etc.) in a ✅ row auto-fails the self-check.
>
> **(8) Rule 20 self-check.** Run the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` with these values:
> - `plan_slug`: `executable-anvil-cycle-19-2026-06-02`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/2026-06-02-cycle-19-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/evidence/executable-anvil-cycle-19-2026-06-02/`
> - `required_evidence_files`: `["cycle_19_row.txt", "findings_file_path.txt", "untested_complexity_grep.txt", "floor_violations.txt", "test_filter_check.txt", "pytest_full.txt"]`
>
> Include the literal stdout of the block in the QA report. If `FAILED`, halt and report. The agent does NOT move the plan to Done — the Planner performs the terminal verdict after Rule 22 verification.
>
> Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/qa/2026-06-02-cycle-19-qa.md`
> - `knowledge/qa/evidence/executable-anvil-cycle-19-2026-06-02/`
