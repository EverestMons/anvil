# Anvil Cycle 13 — invoice-pulse fresh run after 33-day staleness
**Date:** 2026-05-20 | **Tier:** Cycle | **Test Scope:** smoke | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** after_each_step

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. Bellows dispatches each step; agent stops after each step and waits for CEO confirmation before the daemon advances.

Bootstrap prompt:
```
Read the plan at anvil/knowledge/decisions/in-progress-executable-anvil-cycle-13-2026-05-20.md. Execute the next unexecuted step ONLY. After completing the step, STOP and wait for my confirmation.
```

Note: Bellows handles plan claiming (renames `executable-` → `in-progress-`) and Done moves; agents do not run `shutil.move` for plan lifecycle.

---
---

## STEP 1 — ANVIL DEVELOPER

---

> **Identity:** You are the Anvil Developer. **Reads (in order):** `anvil/agents/ANVIL_DEVELOPER.md`, `anvil/PROJECT_STATUS.md` (focus: last cycle was Cycle 11/12 on 2026-04-14, 33+ days ago), the curated backlog at `invoice-pulse/knowledge/research/anvil-findings-backlog-2026-04-14.md` (this is the prior-cycle triage — useful context for what changed since), and the Cycle 11 plan at `anvil/knowledge/decisions/Done/executable-anvil-cycle-11-2026-04-14.md` (template for cycle execution).
>
> **Task:** Run Anvil Cycle 13 against invoice-pulse. The active project is invoice-pulse at `/Users/marklehn/Developer/GitHub/invoice-pulse`. Note that the working-directory paths in older cycle plans reference `~/Desktop/GitHub/` — that path is obsolete (Desktop was iCloud-synced and caused git corruption per 2026-05-14 LESSONS); the current root is `~/Developer/GitHub/`. Pipeline invocation:
>
> ```python
> import sys
> sys.path.insert(0, "anvil")
> from anvil.src.cycle import run_cycle
> import sqlite3
> conn = sqlite3.connect("anvil/anvil.db")
> result = run_cycle(conn, "invoice-pulse", "/Users/marklehn/Developer/GitHub/invoice-pulse")
> print(result)
> conn.close()
> ```
>
> **Pre-cycle snapshot.** Before invoking `run_cycle`, capture a baseline snapshot of the existing DB state for diff comparison in the dev log. Run this first and record the output:
>
> ```python
> import sqlite3
> conn = sqlite3.connect("anvil/anvil.db")
> baseline = {}
> baseline["chunks"] = conn.execute("SELECT COUNT(*) FROM code_chunks WHERE project='invoice-pulse'").fetchone()[0]
> baseline["last_cycle"] = conn.execute("SELECT MAX(cycle_number) FROM cycle_reports WHERE project='invoice-pulse'").fetchone()[0]
> baseline["last_cycle_date"] = conn.execute("SELECT cycle_date FROM cycle_reports WHERE project='invoice-pulse' AND cycle_number = (SELECT MAX(cycle_number) FROM cycle_reports WHERE project='invoice-pulse')").fetchone()[0]
> baseline["git_changes"] = conn.execute("SELECT COUNT(*) FROM git_changes WHERE project='invoice-pulse'").fetchone()[0]
> print(baseline)
> conn.close()
> ```
>
> **Post-cycle verification (after `run_cycle` returns).** (1) Read the newly-produced `invoice-pulse/knowledge/anvil/audit-findings-*.md` file (the timestamp will be today's date). Print all CRITICAL findings verbatim and count findings by severity. (2) Confirm no finding has `file_path` starting with `tests/` (Phase 2.1 test-file filter regression check). (3) Print the first `what_needs_discovering` field from any finding to confirm mission context injection is still present. (4) Run a post-cycle snapshot with the same queries as baseline; compute deltas (chunks delta, cycle number bumped to 13, git_changes delta). (5) Print the top 10 highest-composite findings as a table (function name, file, composite score, finding type) — this is the raw triage surface for the Planner to curate after cycle.
>
> **Constraints:** Do NOT modify any Anvil source files. Do NOT modify invoice-pulse source files (Anvil is read-only on targets). If `run_cycle` raises an exception, capture the full traceback in the dev log and STOP — do not attempt to patch the failure as the Developer. The Planner authors fixes via a new diagnostic. If the cycle completes but findings count is suspiciously low (<5) or suspiciously high (>200), flag for CEO without speculating on cause.
>
> **Deposit:** Write the dev log to `anvil/knowledge/development/cycle-13-run-2026-05-20.md`. Must include: baseline snapshot, post-cycle snapshot with deltas, total findings, findings by severity, all CRITICAL findings verbatim, top-10 highest-composite findings table, test-file-filter verification (yes/no), mission-context-injection verification (yes/no), `run_cycle` result return value, end-to-end runtime in seconds.
>
> **Feedback:** Standard prompt-feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md` if the prompt asks for something the actual pipeline can't deliver (e.g., schema column rename, deprecated function signature).
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO confirmation.**

---

## STEP 2 — ANVIL QA ANALYST

---

> **Identity:** You are the Anvil QA Analyst. **Reads (in order):** `anvil/agents/ANVIL_QA_ANALYST.md`, the dev log at `anvil/knowledge/development/cycle-13-run-2026-05-20.md`, and the audit findings file at `invoice-pulse/knowledge/anvil/audit-findings-2026-05-20.md` (or whatever date the cycle produced).
>
> **Task:** Verify Cycle 13 against the Cycle 11 verification template plus additions for this cycle's 33-day-staleness context.
>
> **(1) Deliverable verification.** (a) Confirm `invoice-pulse/knowledge/anvil/audit-findings-2026-05-20.md` exists and was modified today. (b) Grep for `tests/` in the file — assert zero matches (test-file filter regression check). (c) Grep for `Given that` or similar mission-context phrasing — assert at least one match. (d) Confirm `cycle_reports` has a row for cycle_number=13 via `python3 -c "import sqlite3; conn=sqlite3.connect('anvil/anvil.db'); r=conn.execute('SELECT cycle_number, findings_count, cycle_date FROM cycle_reports WHERE project=\"invoice-pulse\" AND cycle_number=13').fetchone(); print(r); conn.close()"`.
>
> **(2) Staleness-recovery sanity check.** Given 33+ days since Cycle 11, the cycle should have ingested substantial new git history. From the dev log, verify: git_changes delta is non-trivial (>50 new entries — invoice-pulse has had heavy churn). Chunks delta may go either direction (new chunks added, stale chunks removed). If both deltas are near-zero, that is a likely failure mode (cycle didn't actually re-scan) — flag it.
>
> **(3) Findings continuity check.** Open the prior curated backlog at `invoice-pulse/knowledge/research/anvil-findings-backlog-2026-04-14.md` and the new audit-findings file. For each of the 5 actionable findings from the prior backlog (`dispute_brief`, `run_validation`, `_validate_contract_json`, `contract_fuel_import_combined`, `gate_7_linehaul`), check whether the function still appears in this cycle's findings. Record three buckets: (a) still flagged (function present in new findings) — note the new composite score, (b) no longer flagged (function not in new findings) — could mean it was fixed OR scoring drift moved it below threshold, (c) function no longer exists in invoice-pulse (deleted/renamed) — note. This is the highest-value output of this QA step: it tells the Planner whether prior triage is still relevant.
>
> **(4) Noise check.** From the dev log's top-10 list, identify any obvious noise patterns the prior curation called out (session lifecycle methods like `execute`/`commit`/`close`, connection factories like `get_connection`/`get_session`/`get_db`, schema creation like `create_*_tables`). Note count of suspected-noise findings in the top 10. If >3, recommend a future Anvil refinement plan to suppress them.
>
> **Constraints:** QA is read-only on production code. Do NOT modify Anvil source. Do NOT modify the audit-findings file or the prior backlog. If a deliverable check fails, record the failure and continue with remaining checks — do not stop on first failure. Do NOT author the curated triage (that's the Planner's job after QA closes).
>
> **Deposit:** Write the QA report to `anvil/knowledge/qa/cycle-13-qa-2026-05-20.md`. Required sections: deliverable verification table, staleness-recovery sanity check, findings continuity check (the 5 prior-actionable functions with current status), noise check summary. Then update `anvil/PROJECT_STATUS.md` — append entry: `2026-05-20: Cycle 13 complete — first run after 33-day staleness, findings continuity vs Cycle 11 documented.`
>
> The QA report MUST end with the Rule 20 — QA Self-Check Results banner followed by `PASSED — SELF-CHECK PASSED` or `FAILED — SELF-CHECK FAILED`, with itemized check results.
>
> **Feedback:** Standard prompt-feedback protocol.
>
> **STOP. Wait for CEO confirmation before the Planner closes the plan.**

---

## Deposits

- `anvil/knowledge/development/cycle-13-run-2026-05-20.md`
- `anvil/knowledge/qa/cycle-13-qa-2026-05-20.md`
