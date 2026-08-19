# Anvil Cycle 21 — QA-only corrective (invoice-pulse)
**Date:** 2026-08-18 | **Tier:** Cycle | **Dispatch Mode:** bellows | **Test Scope:** full | **Execution:** Step 1 (QA) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_step_1

## Context

QA-only re-dispatch for Anvil Cycle 21. The DEV run completed under plan 447 and is durably committed to anvil `main` as **`20e56c4`** (cycle-21 dev log + `cycle-21-findings-2026-08-19.md` report + prompt-feedback). Cycle 21 landed in `anvil.db` (files_scanned=295 — the accurate invoice-pulse source-file count; chunks_scored=5166; findings_count=3283), and the audit-findings file is on disk at the canonical invoice-pulse path.

Plan 447 was stopped (not continued) because its declared deposit path and its Step-2 QA one-liners hardcoded the **local** date `2026-08-18`, whereas `src/lab.py:103` stamps the findings filename in **UTC** — so the file was correctly written as `audit-findings-2026-08-19.md`. That single date mismatch tripped the `deposit_exists`/`rule_22` gates (a false negative — the deposit exists) and would have cascaded into Step-2 QA. This plan re-runs QA only, against the already-committed HEAD, with the correct `2026-08-19` paths throughout. No DEV rework — the cycle product is complete.

**Do NOT re-run `run_cycle`.** This is verification of existing artifacts only.

**Schema reminders (the cycle-18/19/20 plans carried schema-wrong probes — do not reintroduce them):** project scoping is `project_id` (invoice-pulse=1), resolved as `project_id=(SELECT id FROM projects WHERE name='invoice-pulse')`; `cycle_reports` uses `completed_at` (no `cycle_date`); `health_scores` keys on `chunk_id`/`cycle_id` (no `project`/`cycle_number` columns). Do NOT add a persisted-`volatility_score` floor-invariant check — the `ZERO_COVERAGE_VOLATILITY_FLOOR` is applied inside `compute_composite()` at composite time only (never persisted), so such a probe is a guaranteed false positive (open CEO fork FORWARD #3); the floor's correctness is covered by the full pytest suite below.

**Long-gap triage caveat (carry into the Observations section, not a blocker):** the ~76-day gap since cycle 20 (2026-06-03) exceeds the ~14-day threshold at which percentile-normalized volatility can invert / let findings self-resolve via decay rather than remediation (FORWARD #1/#2). Volatility-dimension movement across cycles is suspect; the coverage × complexity "Untested Complexity" section is the volatility-independent backup view.

## How to Run This Plan

Bellows dispatches this plan automatically when deposited. Single QA step; `pause_for_verdict: after_step_1` and `auto_close: false` hold a terminal pause for the Planner's Rule 22 close verdict and move to Done.

---
---

## STEP 1 — ANVIL QA ANALYST

---

> **Identity:** You are the Anvil QA Analyst. **Reads (in order):** `agents/ANVIL_QA_ANALYST.md`, `knowledge/research/domain-glossary.md`, the DEV dev log `knowledge/development/cycle-21-run-2026-08-18.md` (committed on main at 20e56c4), and the cycle 21 audit findings file at `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-08-19.md`.
>
> **Working directory note:** Worktree root IS anvil/. Use the absolute path `/Users/marklehn/Developer/GitHub/anvil/anvil.db` for DB access. The DEV artifacts already exist on main — this step reads and verifies them, it does NOT re-run the cycle.
>
> **Before starting,** read the dev log and confirm its Output Receipt status is Complete. If not, stop and report.
>
> **Do exactly this** (each check writes literal output to `knowledge/qa/evidence/executable-anvil-cycle-21-qa-2026-08-18/`; `mkdir -p` it first):
>
> **(1) Cycle 21 DB row landed.** `python3 -c "import sqlite3; conn=sqlite3.connect('/Users/marklehn/Developer/GitHub/anvil/anvil.db'); r=conn.execute('SELECT cycle_number, files_scanned, chunks_scored, findings_count, completed_at FROM cycle_reports WHERE project_id=(SELECT id FROM projects WHERE name=\"invoice-pulse\") AND cycle_number=21').fetchone(); print(r); conn.close()" > knowledge/qa/evidence/executable-anvil-cycle-21-qa-2026-08-18/cycle_21_row.txt 2>&1`. Expected: non-null tuple, cycle_number=21, non-zero findings_count.
>
> **(2) Audit findings file at canonical path.** `ls -la /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-08-19.md > knowledge/qa/evidence/executable-anvil-cycle-21-qa-2026-08-18/findings_file_path.txt 2>&1`. Expected: exists (canonical invoice-pulse path, NOT worktree-local). ❌ if missing.
>
> **(3) Untested Complexity section present.** `grep -nF "Untested Complexity" /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-08-19.md > knowledge/qa/evidence/executable-anvil-cycle-21-qa-2026-08-18/untested_complexity_grep.txt 2>&1`. Expected: exactly one match (the header). `-F` is mandatory — grep is ugrep and a present line can exit 1 silently without it.
>
> **(4) Test-file filter regression.** `grep -nF "tests/" /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-2026-08-19.md > knowledge/qa/evidence/executable-anvil-cycle-21-qa-2026-08-18/test_filter_check.txt 2>&1; true`. Inspect: expected no `file_path:` finding entries under `tests/` (a file-name mention in prose is acceptable — confirm none are actual test-file findings). Record the verdict in the QA report.
>
> **(5) Full test suite (Rule 21 — the cycle exercised lab.py and scorer.py; this is the guard on the composite-time volatility floor).** `python3 -m pytest tests/ -q > knowledge/qa/evidence/executable-anvil-cycle-21-qa-2026-08-18/pytest_full.txt 2>&1; true`. Expected: all pass (≥219 — record the exact count; flag if the baseline moved).
>
> **(6) Phantom-finding cross-check.** From the dev log's Phantom-Function Check table, confirm the flagged phantom (`dispute_brief`, DELETED) is recorded for Planner triage exclusion, and spot-verify it: `grep -rncF "def dispute_brief" /Users/marklehn/Developer/GitHub/invoice-pulse/app.py > knowledge/qa/evidence/executable-anvil-cycle-21-qa-2026-08-18/phantom_dispute_brief.txt 2>&1; true`. Expected: 0 (function absent from source — confirms the phantom flag is correct).
>
> **(7) Write QA report** to `knowledge/qa/2026-08-18-cycle-21-qa.md` with a verification table: `| Check | Expected | Status (✅/❌) | Evidence |`, one row per check (1)–(6), each citing its evidence file. Add an "Observations" section noting findings-by-severity from the dev log (10 CRITICAL / 3 HIGH / 1 MEDIUM / 2 LOW per the DEV receipt — confirm against the dev log), the confirmed phantom (`dispute_brief`), the `files_scanned=295` accurate-source-count note, and an explicit percentile-inversion caveat (FORWARD #1/#2) for the ~76-day gap. Do NOT mark a ❌ row ✅ — any hedging keyword ("pending", "inferred", "should pass", "not run", etc.) in a ✅ row auto-fails the self-check.
>
> **(8) Rule 20 self-check.** Run the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` with these values:
> - `plan_slug`: `executable-anvil-cycle-21-qa-2026-08-18`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/2026-08-18-cycle-21-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/evidence/executable-anvil-cycle-21-qa-2026-08-18/`
> - `required_evidence_files`: `["cycle_21_row.txt", "findings_file_path.txt", "untested_complexity_grep.txt", "test_filter_check.txt", "pytest_full.txt", "phantom_dispute_brief.txt"]`
>
> Include the literal stdout of the block in the QA report. If `FAILED`, halt and report. The agent does NOT move the plan to Done — the Planner performs the terminal verdict after Rule 22 verification.
>
> Standard prompt-feedback protocol — append issues to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `knowledge/qa/2026-08-18-cycle-21-qa.md`
> - `knowledge/qa/evidence/executable-anvil-cycle-21-qa-2026-08-18/`
