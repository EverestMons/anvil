---
project: anvil
date: 2026-05-17
author: Planner
total_steps: 2
pause_for_verdict: after_step_1
priority: 10
test_scope: targeted
auto_close: false
---

# Anvil — Fix stale `Desktop/GitHub` paths in `src/config.py`
**Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. This continues step by step until the plan is complete. The agent must never skip steps, auto-chain to the next step, or move the plan to Done without completing all steps including QA.

**Bootstrap prompt:**
```
Read the plan at anvil/knowledge/decisions/executable-anvil-config-path-fix-2026-05-17.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — DEV

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/executable-anvil-config-path-fix-2026-05-17.md", "anvil/knowledge/decisions/in-progress-executable-anvil-config-path-fix-2026-05-17.md")`.
>
> **Read your specialist file and domain glossary first.** Open `anvil/agents/ANVIL_DEVELOPER.md` (or the equivalent dev specialist file for this project) and `anvil/knowledge/research/` for any existing path-related research. Compounds context across sessions.
>
> **Context.** The 2026-05-17 Anvil Cycle 13 dev log flagged that `anvil/src/config.py` references the obsolete `~/Desktop/GitHub/` path in two constants: `SCAN_TARGETS` (line ~11) and `DEV_LOG_PATHS` (line ~199). The Developer monkeypatched at runtime mid-cycle, but the source is still wrong. If Anvil runs from cron or any future automation, the runtime monkeypatch is gone and `find_intent_gaps` returns 0 — silent failure mode. Fix the source.
>
> **Task.** Edit `anvil/src/config.py` to replace both occurrences of `/Users/marklehn/Desktop/GitHub/` with `/Users/marklehn/Developer/GitHub/`. There are exactly two known sites: line ~11 (`SCAN_TARGETS["invoice-pulse"]`) and line ~199 (`DEV_LOG_PATHS["invoice-pulse"]`). Before editing, run `grep -n "Desktop/GitHub" anvil/src/config.py` to confirm exactly two matches, and `grep -rn "Desktop/GitHub" anvil/src/` to confirm no other source files reference the obsolete path. If grep across `anvil/src/` returns matches outside `config.py`, STOP and report to CEO — scope exceeded.
>
> **Constraints.** No other changes. No formatting changes. Do not refactor `SCAN_TARGETS` or `DEV_LOG_PATHS` into a single base-path constant — that is a separate refactor decision out of scope here.
>
> **After editing.** Run `pytest anvil/tests/` (targeted — anvil only) and confirm all 217 tests still pass. Commit with message `fix(config): update SCAN_TARGETS and DEV_LOG_PATHS to Developer/GitHub root` and push to origin/main.
>
> **Deposit:**
> - `anvil/knowledge/development/2026-05-17-config-path-fix-dev-log.md` — DEV log with: exact lines edited (before/after), grep output confirming only 2 sites, pytest exit code, commit SHA.
>
> **Output Receipt.**
> - Files Created or Modified (Code): `anvil/src/config.py`
> - Files Deposited:
>   - `anvil/knowledge/development/2026-05-17-config-path-fix-dev-log.md`
> - Receipt Status: Complete
>
> **Prompt Feedback.** If anything in this prompt was unclear, ambiguous, or led you to make assumptions you had to recover from, deposit a brief note to `anvil/knowledge/development/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> **Before starting, read `anvil/knowledge/development/2026-05-17-config-path-fix-dev-log.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.**
>
> **Read your specialist file and domain glossary first.** Open the Anvil QA specialist file at `anvil/agents/` (e.g., `ANVIL_QA.md` if present) and prior QA reports in `anvil/knowledge/qa/` for pattern context.
>
> **Task.** Verify the config path fix. Specifically:
>
> 1. **Grep verification (no Desktop/GitHub left):** `grep -rn "Desktop/GitHub" anvil/src/` — expected exit 1 (no matches). Capture stdout+stderr to `anvil/knowledge/qa/evidence/executable-anvil-config-path-fix-2026-05-17/grep_no_desktop.txt`.
> 2. **Grep verification (new path present):** `grep -n "Developer/GitHub" anvil/src/config.py` — expected exactly 2 matches (SCAN_TARGETS and DEV_LOG_PATHS). Capture to `grep_developer_present.txt`.
> 3. **Commit landed:** Read the commit SHA from the DEV log, then `git --no-pager log --oneline -10` and confirm that SHA is present. Capture to `git_log.txt`. Anchor on the SHA cited in the DEV log, NOT on HEAD position.
> 4. **Tests pass:** `pytest anvil/tests/` (targeted). Capture full output to `pytest_targeted.txt`. Expected: all 217 tests pass.
>
> Write the QA report to `anvil/knowledge/qa/2026-05-17-config-path-fix-qa.md` with a verification table: `| Check | Expected | Status (✅/❌) | Evidence (file path) |`. Cite evidence files by path. No hedging keywords in ✅ rows.
>
> **Rule 20 self-check.** Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:
> - `plan_slug`: `executable-anvil-config-path-fix-2026-05-17`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/2026-05-17-config-path-fix-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/evidence/executable-anvil-config-path-fix-2026-05-17/`
> - `required_evidence_files`: `["grep_no_desktop.txt", "grep_developer_present.txt", "git_log.txt", "pytest_targeted.txt"]`
>
> Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, do not proceed with closure — halt and report to CEO.
>
> **Final housekeeping.** After Rule 20 PASSED, update `anvil/PROJECT_STATUS.md` with a one-line session entry under today's date noting the config path fix. Then move the plan: `import shutil; shutil.move("anvil/knowledge/decisions/in-progress-executable-anvil-config-path-fix-2026-05-17.md", "anvil/knowledge/decisions/Done/executable-anvil-config-path-fix-2026-05-17.md")`.
>
> **Deposit:**
> - `anvil/knowledge/qa/2026-05-17-config-path-fix-qa.md`
> - `anvil/knowledge/qa/evidence/executable-anvil-config-path-fix-2026-05-17/grep_no_desktop.txt`
> - `anvil/knowledge/qa/evidence/executable-anvil-config-path-fix-2026-05-17/grep_developer_present.txt`
> - `anvil/knowledge/qa/evidence/executable-anvil-config-path-fix-2026-05-17/git_log.txt`
> - `anvil/knowledge/qa/evidence/executable-anvil-config-path-fix-2026-05-17/pytest_targeted.txt`
>
> **Output Receipt.**
> - Files Created or Modified (Code): none
> - Files Deposited: (5 files listed above)
> - Receipt Status: Complete
>
> **Prompt Feedback.** If anything in this prompt was unclear, deposit a brief note to `anvil/knowledge/qa/agent-prompt-feedback.md`.
