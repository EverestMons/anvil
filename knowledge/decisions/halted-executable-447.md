# Anvil Cycle 21 — routine on-demand cycle (invoice-pulse)
**Date:** 2026-08-18 | **Tier:** Cycle | **Dispatch Mode:** bellows | **Test Scope:** smoke | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 2

**auto_close:** false
**pause_for_verdict:** after_step_1

## Context

Routine on-demand Anvil cycle against invoice-pulse — the first cycle since cycle 20 (2026-06-03, ~76 days ago). No methodology change to validate this cycle; the goal is to refresh structural health scores and surface current findings against ~2.5 months of new invoice-pulse activity. Findings get triaged by the Planner after the run (the usual curated-backlog step), so this plan is DEV (run) → QA (verify), with no in-plan triage memo.

Scope: full canonical pipeline (SCAN → EXTRACT → CLASSIFY → PROVENANCE → SCORE → LAB) against invoice-pulse only. Findings deposited to `invoice-pulse/knowledge/anvil/audit-findings-2026-08-18.md`. Anvil source and invoice-pulse source are NOT modified by this cycle.

**Pre-cycle baseline (from PROJECT_STATUS + live DB read 2026-08-18):** last cycle = 20 (2026-06-03). Cycle 21 should bump `cycle_number` to 21. invoice-pulse is `project_id=1` in `anvil.db`.

**Schema note for verification queries (corrected this cycle — the cycle-18/19/20 plans carried three schema-wrong probes that silently errored):**
- Project scoping is `project_id`, NOT a `project` text column. Resolve it as `project_id=(SELECT id FROM projects WHERE name='invoice-pulse')` (=1).
- `cycle_reports` has no `cycle_date`; use `completed_at` / `started_at`.
- `health_scores` has NO `project`/`cycle_number` columns — it keys on `chunk_id` and `cycle_id`. Join to `code_chunks` on `chunk_id` for project scoping; `cycle_id` maps directly to the cycle number.

**Volatility-floor caveat (do NOT re-add the old floor-invariant check):** `ZERO_COVERAGE_VOLATILITY_FLOOR` (`src/scorer.py:336`) is applied *inside* `compute_composite()` at composite time only — it is never persisted to the stored `volatility_score` column. A `SELECT COUNT(*) ... volatility_score < 0.5` invariant therefore returns a large non-zero count by design (1235 at cycle 20) and is a false positive. Whether to persist the floored value is open CEO fork FORWARD #3. The floor's correctness is already guarded by the unit suite (Rule 21 full pytest in Step 2).

**Long-gap methodology caveat (carry into triage, not a blocker):** the ~76-day gap between cycle 20 (2026-06-03) and this cycle far exceeds the ~14-day threshold at which Anvil's percentile-normalized volatility can (a) invert direction under population-wide commit collapse and (b) let functions self-resolve out of the top-N purely via volatility decay rather than remediation (FORWARD #1, #2; volatility-attribution-replay 2026-05-18). Treat cross-cycle "improvements" in the volatility dimension with suspicion; the coverage × complexity "Untested Complexity" section is the volatility-independent backup view for triage.

**Known phantom-finding caveat (carry into triage):** volatility scoring reaches into git history beyond the current scan, so functions deleted from the codebase can still surface as high-volatility findings. Step 1 includes a chunk-existence (phantom) check on the top-10 findings so deleted functions are flagged in the dev log rather than silently trusted.

## How to Run This Plan

Bellows dispatches this plan automatically when deposited; no manual bootstrap required. The daemon runs Step 1, then pauses for the CEO/Planner verdict (`pause_for_verdict: after_step_1`) before running Step 2 (QA). `auto_close: false` holds a terminal pause after Step 2 for the Planner's Rule 22 close verdict and Bellows-side move to Done.

---
---

## STEP 1 — ANVIL DEVELOPER

---

> **Identity:** You are the Anvil Developer. **Reads (in order):** `agents/ANVIL_DEVELOPER.md`, `knowledge/research/domain-glossary.md`, `PROJECT_STATUS.md` (cycle 20 was 2026-06-03; this is cycle 21), and the prior cycle plan `knowledge/decisions/Done/executable-anvil-cycle-19-2026-06-02.md` as the template for cycle execution mechanics — BUT use the corrected schema-accurate queries in THIS plan, not that one's (`project` → `project_id`, `cycle_date` → `completed_at`, and the dropped floor-invariant check).
>
> **Working directory note:** Bellows runs this plan in a worktree at `anvil/.bellows-worktrees/anvil-cycle-21-2026-08-18/`; the worktree IS the anvil root from your perspective. For Anvil source imports use relative paths (e.g., `from src.cycle import run_cycle`). **For DB access use the absolute canonical path** `/Users/marklehn/Developer/GitHub/anvil/anvil.db` — the cycle reads and writes the main-repo DB, not a worktree-local one. The F8 hardcode (`ANVIL_ROOT`, commit `86ba5fd`) ensures paths resolve to canonical main-repo locations automatically.
>
> **Task:** Run Anvil Cycle 21 against invoice-pulse.
>
> **Pre-cycle snapshot.** Run first and record output:
>
> ```python
> import sqlite3
> conn = sqlite3.connect("/Users/marklehn/Developer/GitHub/anvil/anvil.db")
> pid = conn.execute("SELECT id FROM projects WHERE name='invoice-pulse'").fetchone()[0]
> baseline = {}
> baseline["project_id"] = pid
> baseline["chunks"] = conn.execute("SELECT COUNT(*) FROM code_chunks WHERE project_id=?", (pid,)).fetchone()[0]
> baseline["last_cycle"] = conn.execute("SELECT MAX(cycle_number) FROM cycle_reports WHERE project_id=?", (pid,)).fetchone()[0]
> baseline["git_changes"] = conn.execute("SELECT COUNT(*) FROM git_changes WHERE project_id=?", (pid,)).fetchone()[0]
> print(baseline)
> conn.close()
> ```
>
> Expected: `project_id: 1`, `last_cycle: 20`.
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
> (1) Post-cycle snapshot using the same queries as baseline; compute deltas (chunks, git_changes). Confirm `cycle_number` bumped to 21 via `SELECT MAX(cycle_number) FROM cycle_reports WHERE project_id=1`.
>
> (2) Locate the new audit findings file. Per F8, it must be at `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-08-18.md` (canonical path, NOT worktree-local). Confirm it exists there. If it landed under `.bellows-worktrees/...`, or the date in the filename differs from 2026-08-18, FLAG for CEO (F8 or date-derivation issue).
>
> (3) From the findings file: print all CRITICAL findings verbatim; count findings by severity.
>
> (4) Test-file filter regression: grep the findings file for `tests/` in `file_path` lines — expect zero matches.
>
> (5) Mission-context check: grep for `Given that` — expect ≥1 match.
>
> (6) Untested Complexity section: grep the findings file for `Untested Complexity` — expect exactly one match (the header). Print the section's row count (rows between that header and the next `##`).
>
> (7) Cycle-report row landed. Print the `cycle_reports` row for cycle 21:
>
> ```python
> import sqlite3
> conn = sqlite3.connect("/Users/marklehn/Developer/GitHub/anvil/anvil.db")
> row = conn.execute("""
>     SELECT cycle_number, files_scanned, chunks_scored, findings_count, completed_at, report_path
>     FROM cycle_reports
>     WHERE project_id=(SELECT id FROM projects WHERE name='invoice-pulse') AND cycle_number=21
> """).fetchone()
> print(row)
> conn.close()
> ```
>
> Expect a non-null tuple with today's date in `completed_at`. Do NOT re-add a persisted-`volatility_score` floor-invariant check — the floor is composite-time only (see Context); its correctness is covered by the Step 2 full pytest suite.
>
> (8) Top-10 highest-composite findings as a table (function, file, composite, finding type). Source from the findings file or via `health_scores` joined to `code_chunks` on `chunk_id` filtered to `cycle_id=21` and `project_id=1`, ordered by `composite_score DESC`.
>
> (9) **Phantom-function check (known-bug mitigation).** For each function in the top-10 table from (8), verify it still exists in current invoice-pulse source: `grep -rn "def <function_name>" /Users/marklehn/Developer/GitHub/invoice-pulse/<file_path>` (use the finding's file path). Record, per function: EXISTS or DELETED. Any DELETED function is a phantom finding (scoring reached into git history beyond the current scan) — list these explicitly so the Planner excludes them at triage.
>
> **Constraints:** Do NOT modify Anvil source. Do NOT modify invoice-pulse source. If findings count is suspiciously low (<5) or high (>250), flag without speculating.
>
> **Deposit:** `knowledge/development/cycle-21-run-2026-08-18.md` — must include: baseline snapshot, post-cycle snapshot with deltas, audit findings file path (confirming canonical not worktree, and today's date), cycle_reports row, total findings, findings by severity, all CRITICAL findings verbatim, top-10 table, phantom-function check results (EXISTS/DELETED per top-10 entry), test-file-filter result, mission-context result, Untested Complexity row count, `run_cycle` return value, end-to-end runtime in seconds. End with an Output Receipt (Status field).
>
> Standard prompt-feedback protocol — append issues to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `knowledge/development/cycle-21-run-2026-08-18.md`
> - `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-08-18.md` (produced by `run_cycle`)

---
---

## STEP 2 — ANVIL QA ANALYST

---

> Before starting, read `knowledge/development/cycle-21-run-2026-08-18.md` and check the Output Receipt status. If status is not Complete, stop and report the blocker before proceeding.
>
> **Identity:** You are the Anvil QA Analyst. **Reads (in order):** `agents/ANVIL_QA_ANALYST.md`, `knowledge/research/domain-glossary.md`, the Step 1 dev log, and the cycle 21 audit findings file at `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-08-18.md`.
>
> **Working directory note:** Worktree root IS anvil/. Use the absolute path `/Users/marklehn/Developer/GitHub/anvil/anvil.db` for DB access.
>
> **Do exactly this** (each check writes literal output to `knowledge/qa/evidence/executable-anvil-cycle-21-2026-08-18/`; `mkdir -p` it first):
>
> **(1) Cycle 21 DB row landed.** `python3 -c "import sqlite3; conn=sqlite3.connect('/Users/marklehn/Developer/GitHub/anvil/anvil.db'); r=conn.execute('SELECT cycle_number, findings_count, completed_at FROM cycle_reports WHERE project_id=(SELECT id FROM projects WHERE name=\"invoice-pulse\") AND cycle_number=21').fetchone(); print(r); conn.close()" > knowledge/qa/evidence/executable-anvil-cycle-21-2026-08-18/cycle_21_row.txt 2>&1`. Expected: non-null tuple, cycle_number=21, today's date (2026-08-18) in completed_at.
>
> **(2) Audit findings file at canonical path.** `ls -la /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-08-18.md > knowledge/qa/evidence/executable-anvil-cycle-21-2026-08-18/findings_file_path.txt 2>&1`. Expected: exists, modified today. ❌ if missing or worktree-local.
>
> **(3) Untested Complexity section present.** `grep -nF "Untested Complexity" /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-08-18.md > knowledge/qa/evidence/executable-anvil-cycle-21-2026-08-18/untested_complexity_grep.txt 2>&1`. Expected: exactly one match. (Note: grep here is ugrep — the `-F` flag is mandatory or a present line can exit 1 silently.)
>
> **(4) Test-file filter regression.** `grep -cF "tests/" /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-08-18.md > knowledge/qa/evidence/executable-anvil-cycle-21-2026-08-18/test_filter_check.txt 2>&1; true`. Inspect: expected 0 matches in `file_path` lines (a file-name mention in prose is acceptable — confirm none are `file_path:` entries under `tests/`).
>
> **(5) Findings count sanity.** `python3 -c "import sqlite3; conn=sqlite3.connect('/Users/marklehn/Developer/GitHub/anvil/anvil.db'); r=conn.execute('SELECT findings_count FROM cycle_reports WHERE project_id=(SELECT id FROM projects WHERE name=\"invoice-pulse\") AND cycle_number=21').fetchone()[0]; print(r); conn.close()" > knowledge/qa/evidence/executable-anvil-cycle-21-2026-08-18/findings_count.txt 2>&1`. Expected: a plausible non-zero count (cycles 18–20 ranged ~1976–2114); flag if 0 or wildly outside that band.
>
> **(6) Full test suite (Rule 21 — the cycle exercises lab.py and scorer.py; this is also the guard on the composite-time volatility floor).** `python3 -m pytest tests/ -q > knowledge/qa/evidence/executable-anvil-cycle-21-2026-08-18/pytest_full.txt 2>&1; true`. Expected: all pass (≥219 — record the exact count; flag if the baseline moved).
>
> **(7) Write QA report** to `knowledge/qa/2026-08-18-cycle-21-qa.md` with a verification table: `| Check | Expected | Status (✅/❌) | Evidence |`, one row per check (1)–(6), each citing its evidence file. Add a brief "Observations" section noting findings-by-severity from the Step 1 dev log, any phantom (DELETED) functions the dev log flagged in the top-10, and — given the ~76-day inter-cycle gap — an explicit note that volatility-dimension movement should be treated with the percentile-inversion caveat (FORWARD #1/#2) at triage. Do NOT mark a ❌ row ✅ — any hedging keyword ("pending", "inferred", "should pass", "not run", etc.) in a ✅ row auto-fails the self-check.
>
> **(8) Rule 20 self-check.** Run the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` with these values:
> - `plan_slug`: `executable-anvil-cycle-21-2026-08-18`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/2026-08-18-cycle-21-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/evidence/executable-anvil-cycle-21-2026-08-18/`
> - `required_evidence_files`: `["cycle_21_row.txt", "findings_file_path.txt", "untested_complexity_grep.txt", "test_filter_check.txt", "findings_count.txt", "pytest_full.txt"]`
>
> Include the literal stdout of the block in the QA report. If `FAILED`, halt and report. The agent does NOT move the plan to Done — the Planner performs the terminal verdict after Rule 22 verification.
>
> Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/qa/2026-08-18-cycle-21-qa.md`
> - `knowledge/qa/evidence/executable-anvil-cycle-21-2026-08-18/`
