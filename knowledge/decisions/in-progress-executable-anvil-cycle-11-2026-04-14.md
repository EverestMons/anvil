# Anvil Cycle 11 — Phase 2.1 Refined Intent Gaps
**Date:** 2026-04-14 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 1

## How to Run This Plan

This plan is picked up and executed by Bellows automatically.

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/executable-anvil-cycle-11-2026-04-14.md", "anvil/knowledge/decisions/in-progress-executable-anvil-cycle-11-2026-04-14.md")`. Read your specialist file at `anvil/agents/ANVIL_DEVELOPER.md`. Working directory is `/Users/marklehn/Desktop/GitHub/`. Run Anvil Cycle 11 against invoice-pulse: `import sys; sys.path.insert(0, "anvil"); from anvil.src.cycle import run_cycle; import sqlite3; conn = sqlite3.connect("anvil/anvil.db"); result = run_cycle(conn, "invoice-pulse", "/Users/marklehn/Desktop/GitHub/invoice-pulse"); print(result); conn.close()`. After the cycle completes: (1) Read the new `invoice-pulse/knowledge/anvil/audit-findings-*.md` file — print all CRITICAL findings and count findings by severity. (2) Confirm no finding has a file_path starting with `tests/`. (3) Print the first `what_needs_discovering` field from any finding to confirm mission context injection is present. Deposit dev log to `anvil/knowledge/development/cycle-11-run-2026-04-14.md` with: cycle number, total findings, findings by severity, whether test files were excluded (yes/no), whether mission context appeared in what_needs_discovering (yes/no). Commit: `feat: Anvil Cycle 11 — refined intent gaps`. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, read `anvil/knowledge/development/cycle-11-run-2026-04-14.md` and check Output Receipt status. If not Complete, stop and report to CEO. Read your specialist file at `anvil/agents/ANVIL_QA_ANALYST.md`. **Deliverable verification:** (1) confirm `invoice-pulse/knowledge/anvil/audit-findings-*.md` exists and was updated today, (2) grep it for `tests/` — assert no matches (test files excluded), (3) grep it for `Given that` — assert at least one match (mission context injected), (4) confirm cycle_reports has cycle_number=11 via `python3 -c "import sqlite3; conn = sqlite3.connect('anvil/anvil.db'); r = conn.execute('SELECT cycle_number, findings_count FROM cycle_reports WHERE cycle_number=11').fetchone(); print(r)"`. Write all output to `anvil/knowledge/qa/evidence/cycle-11/verify.txt` via Python file I/O. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Deposit QA report to `anvil/knowledge/qa/cycle-11-qa-2026-04-14.md`. **Final:** Update `anvil/PROJECT_STATUS.md` — add entry: "2026-04-14: Cycle 11 complete — refined intent gaps, test files excluded, mission context injected." Move plan to Done: `import shutil; shutil.move("anvil/knowledge/decisions/in-progress-executable-anvil-cycle-11-2026-04-14.md", "anvil/knowledge/decisions/Done/executable-anvil-cycle-11-2026-04-14.md")`. Commit: `chore: QA report — Anvil Cycle 11`. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
>
> ---
> ## Output Receipt
> **Agent:** Anvil QA Analyst
> **Step:** 2
> **Status:** Complete
>
> ### Flags for CEO
> - None
