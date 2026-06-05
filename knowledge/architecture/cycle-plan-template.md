# Anvil Cycle Plan — Canonical Template
**Maintained at:** knowledge/architecture/cycle-plan-template.md
**Do NOT author a cycle by copying the previous cycle's executable.** Copy the
body below the `=== TEMPLATE BODY ===` divider instead. The prior-cycle-copy
habit is what propagated the cycle-18 gaps into cycle 19 (3 tripped gates) and
carried broken `WHERE project=...` queries forward silently.

## Authoring rules (read before filling placeholders)

**Placeholders:** `<N>` cycle number · `<LOCAL>` plan authoring date (your local
day, YYYY-MM-DD) · `<UTC>` UTC date at expected execution, YYYY-MM-DD.

1. **Dispatch Mode is mandatory (Rule 35).** The header MUST contain
   `**Dispatch Mode:** bellows`. Without it, `validate_at_claim`
   (`validators.check_missing_dispatch_mode`) moves the plan to `halted-` and it
   is never claimed. Valid values: `bellows` or `manual_bootstrap`; cycles are
   always `bellows`.

2. **run_cycle outputs are stamped UTC, not local.** Both deposits produced by
   `run_cycle` — the invoice-pulse audit-findings file (`lab.py:661`) and the
   canonical anvil cycle report (`lab.py:91-95`) — are named with
   `datetime.now(timezone.utc)`. The deposit gate (`_resolve_deposit_path`)
   matches literally via `os.path.isfile`; there is NO globbing, so a declared
   deposit dated in local time fails `deposit_exists` + `rule_22_verification`
   whenever you author after ~19:00 CDT / 18:00 CST (UTC has already rolled).
   Set `<UTC>` from `date -u +%F`. The plan filename and `**Date:**` header stay
   on `<LOCAL>` (plan identity follows your day); only the run_cycle deposit
   paths use `<UTC>`. Boundary risk: if you author within ~30 min of UTC
   midnight, the date run_cycle actually stamps may differ from your prediction;
   dispatch promptly and, if it misses, re-stamp the deposit declaration and
   re-dispatch (manual recovery — no source-side fix exists).

3. **The cycle report lands in the worktree, not canonical main.** `run_cycle`
   writes `knowledge/research/cycle-<N>-findings-<UTC>.md` to the runtime root
   (`ANVIL_RUNTIME_ROOT`), which resolves to the worktree during a Bellows
   dispatch. It is a git-tracked artifact (cycles 1–20 are all in
   `git ls-files`), so do NOT gitignore it. The report MUST be explicitly staged
   before the worktree commit — the DEV step contains an explicit `git add`
   instruction for this (see STEP 1 below). No Planner wrap-commit on main is
   needed; the report rides the worktree commit and lands on main at teardown.
   Declare it in the DEV step's `**Deposits:**` block.

4. **Verify <N>, <UTC>, and the produced filename from source of truth.** Cycle
   number is project-scoped: `cycle_id = MAX(cycle_number where project_id) + 1`
   (`cycle.py:31-38`), so `cycle_id == cycle_number`. Confirm the next number:
   `SELECT MAX(cycle_number) FROM cycle_reports WHERE project_id=(SELECT id FROM projects WHERE name='invoice-pulse')`
   then +1. After the run, confirm the actual produced cycle-report filename
   before the rule-3 commit (the UTC date is the run's, not your prediction).

5. **Schema note — there is no `project` text column and no `cycle_date`
   column.** `cycle_reports`, `code_chunks`, and `git_changes` key on
   `project_id` (resolve via `projects.name`). `health_scores` has neither
   `project` nor `cycle_number` — it keys on `chunk_id` + `cycle_id`; scope it by
   joining `code_chunks` on `chunk_id` and filtering `code_chunks.project_id`.
   Cycle date derives from `started_at`, not a `cycle_date` column. The embedded
   queries below are corrected and live-tested; do not revert them to
   `WHERE project='invoice-pulse'`.

6. **The (d2) volatility floor is NOT a DB invariant.** The floor
   (`scorer.py:332`: `if coverage >= 0.99: volatility = max(volatility, 0.5)`)
   is applied as a local variable inside `compute_composite` and is never
   written back to `health_scores.volatility_score`. A query asserting "no chunk
   with coverage>=0.99 and volatility_score<0.5" returns ~1200+ rows by design
   and is wrong-layer. The floor is covered by the scorer unit suite, which the
   QA pytest gate runs — so do NOT add a per-cycle DB floor-invariant check.
   (Cycles 18–19 carried such a check; it never evaluated because the `project`
   column error masked it.)

7. **Secondary (invoice-pulse, not an anvil-teardown blocker):** the
   audit-findings file lands untracked in `invoice-pulse/knowledge/anvil/`. It
   does not block anvil teardown (different repo) but should be committed in
   invoice-pulse during triage so a later invoice-pulse dispatch's dirty-tree
   check doesn't trip on it.

=== TEMPLATE BODY (copy from here down) ===

# Anvil Cycle <N> — routine on-demand cycle (invoice-pulse)
**Date:** <LOCAL> | **Tier:** Cycle | **Dispatch Mode:** bellows | **Test Scope:** smoke | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 2

**auto_close:** false
**pause_for_verdict:** after_step_1

## Context

Routine on-demand Anvil cycle against invoice-pulse. Goal: refresh structural
health scores and surface current findings. Findings get triaged by the Planner
after the run (the usual curated-backlog step), so this plan is DEV (run) → QA
(verify), with no in-plan triage memo.

Scope: full canonical pipeline (SCAN → EXTRACT → CLASSIFY → PROVENANCE → SCORE →
LAB) against invoice-pulse only. Anvil source and invoice-pulse source are NOT
modified by this cycle.

**Pre-cycle baseline:** last cycle = <N-1>. Cycle <N> bumps `cycle_number` to <N>.

**Known findings-quality caveat (carry into triage, not a blocker):** volatility
scoring can reach into git history beyond the current scan, so deleted functions
can surface as high-volatility intent gaps (BACKLOG 2026-05-18). Step 1 includes
a chunk-existence check on top findings so phantoms are flagged, not trusted.

## How to Run This Plan

Bellows dispatches this plan automatically when deposited. The daemon runs
Step 1, then pauses for the verdict (`pause_for_verdict: after_step_1`) before
Step 2 (QA). `auto_close: false` holds a terminal pause after Step 2 for the
Planner's Rule 22 close verdict and Bellows-side move to Done.

---
---

## STEP 1 — ANVIL DEVELOPER

---

> **Identity:** You are the Anvil Developer. **Reads (in order):** `agents/ANVIL_DEVELOPER.md`, `knowledge/research/domain-glossary.md`, `PROJECT_STATUS.md` (last cycle was <N-1>; this is cycle <N>), and the most recent completed cycle executable in `knowledge/decisions/Done/` as a worked example of cycle execution mechanics.
>
> **Working directory note:** Bellows runs this plan in a worktree at `anvil/.bellows-worktrees/anvil-cycle-<N>-<LOCAL>/`; the worktree IS the anvil root from your perspective. For Anvil source imports use relative paths (e.g., `from src.cycle import run_cycle`). **For DB access use the absolute canonical path** `/Users/marklehn/Developer/GitHub/anvil/anvil.db`. The cycle report lands in the WORKTREE at `knowledge/research/cycle-<N>-findings-<UTC>.md` (via `ANVIL_RUNTIME_ROOT`). The DB record stores the canonical path (`ANVIL_ROOT`), which becomes valid after teardown lands the worktree commits to main.
>
> **Task:** Run Anvil Cycle <N> against invoice-pulse.
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
> Expected: `last_cycle: <N-1>`.
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
> If it raises, capture the full traceback and STOP — do not patch as Developer.
>
> **Post-cycle verification (after `run_cycle` returns):**
>
> (1) Post-cycle snapshot (same queries as baseline); compute deltas. Confirm `cycle_number` bumped to <N>.
>
> (2) Locate the audit findings file. Per F8 + UTC stamping it is at `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-<UTC>.md` (canonical path, UTC date, NOT worktree-local). Confirm it exists there. If worktree-local, FLAG for CEO — F8 is not working.
>
> (3) Locate the cycle report at `knowledge/research/cycle-<N>-findings-<UTC>.md` (worktree-relative path, UTC date). Confirm it exists and print its exact filename verbatim. The file lands in the worktree via `ANVIL_RUNTIME_ROOT`; step (10) stages it for commit.
>
> (4) From the findings file: print all CRITICAL findings verbatim; count findings by severity.
>
> (5) Test-file filter regression: grep findings for `tests/` in `file_path` lines — expect zero.
>
> (6) Mission-context check: grep for `Given that` — expect ≥1.
>
> (7) Untested Complexity section: grep for `Untested Complexity` — expect exactly one match (the header). Print the section's row count.
>
> (8) Top-10 highest-composite findings as a table (function, file, composite, finding type).
>
> (9) **Phantom-function check (known-bug mitigation).** For each function in the top-10, verify it still exists in current invoice-pulse source: `grep -rn "def <function_name>" /Users/marklehn/Developer/GitHub/invoice-pulse/<file_path>`. Record EXISTS or DELETED per function. Any DELETED is a phantom (BACKLOG 2026-05-18) — list explicitly so the Planner excludes it at triage. Watch `web/action_queue.py` entries.
>
> **(10) Stage the cycle report for commit.** The report lands in the worktree and
> MUST be committed with the worktree's changes:
> ```bash
> git add knowledge/research/cycle-<N>-findings-<UTC>.md
> ```
> Verify staged: `git status` should show it as "new file" under "Changes to be
> committed." If it appears under "Untracked files," the add failed — retry.
>
> **Constraints:** Do NOT modify Anvil source. Do NOT modify invoice-pulse source. If findings count is suspiciously low (<5) or high (>250), flag without speculating.
>
> Standard prompt-feedback protocol — append issues to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `knowledge/development/cycle-<N>-run-<LOCAL>.md`
> - `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-<UTC>.md` (produced by `run_cycle`)
> - `knowledge/research/cycle-<N>-findings-<UTC>.md` (produced by `run_cycle`, canonical main path)

---
---

## STEP 2 — ANVIL QA ANALYST

---

> Before starting, read `knowledge/development/cycle-<N>-run-<LOCAL>.md` and check the Output Receipt status. If status is not Complete, stop and report the blocker before proceeding.
>
> **Identity:** You are the Anvil QA Analyst. **Reads (in order):** `agents/ANVIL_QA_ANALYST.md`, `knowledge/research/domain-glossary.md`, the Step 1 dev log, and the cycle <N> audit findings file at `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-<UTC>.md`.
>
> **Working directory note:** Worktree root IS anvil/. Use the absolute path `/Users/marklehn/Developer/GitHub/anvil/anvil.db` for DB access.
>
> **Do exactly this** (each check writes literal output to `knowledge/qa/evidence/executable-anvil-cycle-<N>-<LOCAL>/`; `mkdir -p` it first):
>
> **(1) Cycle <N> DB row landed.** `python3 -c "import sqlite3; conn=sqlite3.connect('/Users/marklehn/Developer/GitHub/anvil/anvil.db'); r=conn.execute('SELECT cycle_number, findings_count, started_at FROM cycle_reports WHERE project_id=(SELECT id FROM projects WHERE name=\"invoice-pulse\") AND cycle_number=<N>').fetchone(); print(r); conn.close()" > knowledge/qa/evidence/executable-anvil-cycle-<N>-<LOCAL>/cycle_<N>_row.txt 2>&1`. Expected: non-null tuple, cycle_number=<N>, started_at is today (UTC).
>
> **(2) Audit findings file at canonical path.** `ls -la /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-<UTC>.md > knowledge/qa/evidence/executable-anvil-cycle-<N>-<LOCAL>/findings_file_path.txt 2>&1`. Expected: exists. ❌ if missing or worktree-local.
>
> **(3) Cycle report in worktree.** `ls -la knowledge/research/cycle-<N>-findings-<UTC>.md > knowledge/qa/evidence/executable-anvil-cycle-<N>-<LOCAL>/cycle_report_path.txt 2>&1`. Expected: exists at worktree-relative path with UTC date. ❌ if missing. Also verify it is staged: `git diff --cached --name-only | grep cycle-<N>-findings > knowledge/qa/evidence/executable-anvil-cycle-<N>-<LOCAL>/cycle_report_staged.txt 2>&1`. Expected: ≥1 match.
>
> **(4) Untested Complexity section present.** `grep -n "Untested Complexity" /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-<UTC>.md > knowledge/qa/evidence/executable-anvil-cycle-<N>-<LOCAL>/untested_complexity_grep.txt 2>&1`. Expected: exactly one match.
>
> **(5) Test-file filter regression.** `grep -c "file_path.*tests/" /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/anvil/audit-findings-<UTC>.md > knowledge/qa/evidence/executable-anvil-cycle-<N>-<LOCAL>/test_filter_check.txt 2>&1`. Expected: 0.
>
> **(6) Full test suite (Rule 21 — the cycle exercises lab.py and scorer.py, including the (d2) volatility floor).** `python3 -m pytest tests/ -q > knowledge/qa/evidence/executable-anvil-cycle-<N>-<LOCAL>/pytest_full.txt 2>&1`. Expected: all pass (record exact count; flag if baseline moved).
>
> **(7) Write QA report** to `knowledge/qa/<LOCAL>-cycle-<N>-qa.md` with a verification table: `| Check | Expected | Status (✅/❌) | Evidence |`, one row per check (1)–(6), each citing its evidence file. Add an "Observations" section noting findings-by-severity from the dev log and any phantom (DELETED) functions flagged in the top-10. Do NOT mark a ❌ row ✅ — any hedging keyword ("pending", "inferred", "should pass", "not run") in a ✅ row auto-fails the self-check.
>
> **(8) Rule 20 self-check.** Run the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` with:
> - `plan_slug`: `executable-anvil-cycle-<N>-<LOCAL>`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/<LOCAL>-cycle-<N>-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/evidence/executable-anvil-cycle-<N>-<LOCAL>/`
> - `required_evidence_files`: `["cycle_<N>_row.txt", "findings_file_path.txt", "cycle_report_path.txt", "untested_complexity_grep.txt", "test_filter_check.txt", "pytest_full.txt"]`
>
> Include the literal stdout in the QA report. If `FAILED`, halt and report. The agent does NOT move the plan to Done — the Planner performs the terminal verdict after Rule 22 verification.
>
> Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/qa/<LOCAL>-cycle-<N>-qa.md`
> - `knowledge/qa/evidence/executable-anvil-cycle-<N>-<LOCAL>/`
