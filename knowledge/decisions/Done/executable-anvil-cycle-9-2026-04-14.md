# Anvil Cycle 9 — Phase 2.1 First Run
**Date:** 2026-04-14 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 1

## How to Run This Plan

This plan is picked up and executed by Bellows automatically.

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/executable-anvil-cycle-9-2026-04-14.md", "anvil/knowledge/decisions/in-progress-executable-anvil-cycle-9-2026-04-14.md")`. Read your specialist file at `anvil/agents/ANVIL_DEVELOPER.md`. Working directory is `/Users/marklehn/Desktop/GitHub/`. Run Anvil Cycle 9 against invoice-pulse. Execute the following Python in Claude Code: `import sys; sys.path.insert(0, "anvil"); from anvil.src.cycle import run_cycle; import sqlite3; conn = sqlite3.connect("anvil/anvil.db"); result = run_cycle(conn, "invoice-pulse", "/Users/marklehn/Desktop/GitHub/invoice-pulse"); print(result); conn.close()`. After the cycle completes: (1) Check if `invoice-pulse/knowledge/anvil/` directory was created and contains an `audit-findings-*.md` file — print its path and first 50 lines. (2) Print the cycle report path from result and first 30 lines of the cycle report. (3) Print intent_gaps count from result if present, or check the audit-findings file directly. Deposit a dev log to `anvil/knowledge/development/cycle-9-run-2026-04-14.md` with: cycle number, files scanned, chunks extracted, chunks scored, total findings, intent_gaps count, audit-findings file path and whether it was created. Commit: `feat: Anvil Cycle 9 — first run with Phase 2.1 intent gaps`. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, read `anvil/knowledge/development/cycle-9-run-2026-04-14.md` and check Output Receipt status. If not Complete, stop and report to CEO. Read your specialist file at `anvil/agents/ANVIL_QA_ANALYST.md`. **Deliverable verification:** (1) confirm `invoice-pulse/knowledge/anvil/` directory exists, (2) confirm an `audit-findings-*.md` file exists inside it — grep for `find_intent_gaps` or `Intent Gap` or `CRITICAL\|HIGH\|MEDIUM\|LOW` in that file, (3) confirm cycle_reports table has a new row with cycle_number=9 via `python3 -c "import sqlite3; conn = sqlite3.connect('anvil/anvil.db'); r = conn.execute('SELECT cycle_number, findings_count, chunks_scored FROM cycle_reports WHERE cycle_number=9').fetchone(); print(r)"`, (4) confirm a new cycle findings file exists in `anvil/knowledge/research/` dated today. Write all verification output to `anvil/knowledge/qa/evidence/cycle-9/verify.txt` via Python file I/O. **Read and summarize intent gaps:** read the full `invoice-pulse/knowledge/anvil/audit-findings-*.md` file — count findings by severity (CRITICAL/HIGH/MEDIUM/LOW), list the top 3 finding titles. Include in QA report. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Deposit QA report to `anvil/knowledge/qa/cycle-9-qa-2026-04-14.md`. **Final:** Update `anvil/PROJECT_STATUS.md` — add entry: "2026-04-14: Cycle 9 complete — first run with Phase 2.1 intent gaps. audit-findings deposited to invoice-pulse/knowledge/anvil/." Move plan to Done: `import shutil; shutil.move("anvil/knowledge/decisions/in-progress-executable-anvil-cycle-9-2026-04-14.md", "anvil/knowledge/decisions/Done/executable-anvil-cycle-9-2026-04-14.md")`. Commit: `chore: QA report — Anvil Cycle 9`. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
>
> ---
> ## Output Receipt
> **Agent:** Anvil QA Analyst
> **Step:** 2
> **Status:** Complete
>
> ### Flags for CEO
> - None
