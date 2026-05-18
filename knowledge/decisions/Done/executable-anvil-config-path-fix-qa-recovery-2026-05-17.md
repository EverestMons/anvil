# Anvil — QA verification for config path fix (Step 2 recovery)
**Date:** 2026-05-17 | **Tier:** small | **Test Scope:** targeted | **Execution:** Step 1 (QA) | **pause_for_verdict:** after_step_1 | **Priority:** 10 | **auto_close:** false

## Context

The original plan `executable-anvil-config-path-fix-2026-05-17` had its Step 1 DEV completed successfully — the agent edited `anvil/src/config.py`, deposited a dev log, committed (`74c6dce`), and pushed to origin/main. However, the original plan was halted before Step 2 (QA) could run, due to a Bellows-side bug unrelated to the DEV work. This plan is the QA recovery: a fresh QA step that reads the existing DEV deposit and verifies the work.

The original DEV deposit lives at `anvil/knowledge/development/2026-05-17-config-path-fix-dev-log.md`. The halted original plan is at `anvil/knowledge/decisions/halted-executable-anvil-config-path-fix-2026-05-17.md` (untracked, kept for audit).

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok"). Single-step QA-only recovery — no Step 2.

**Bootstrap prompt:**
```
Read the plan at anvil/knowledge/decisions/executable-anvil-config-path-fix-qa-recovery-2026-05-17.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT move the plan to Done.
```

---
---

## STEP 1 — QA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/executable-anvil-config-path-fix-qa-recovery-2026-05-17.md", "anvil/knowledge/decisions/in-progress-executable-anvil-config-path-fix-qa-recovery-2026-05-17.md")`.
>
> **Read your specialist file and domain glossary first.** Open `anvil/agents/` (QA specialist file if present) and prior QA reports in `anvil/knowledge/qa/`.
>
> **Read the existing DEV deposit.** Open `anvil/knowledge/development/2026-05-17-config-path-fix-dev-log.md`. The DEV log records: two lines edited (11 and 131), pytest exit 0 (217 passed), commit SHA `74c6dce`, pushed to origin/main. Verify each claim.
>
> **Task.**
>
> 1. **Grep verification (no Desktop/GitHub left):** `grep -rn "Desktop/GitHub" anvil/src/` — expected exit 1 (no matches). Capture stdout+stderr to `anvil/knowledge/qa/evidence/executable-anvil-config-path-fix-qa-recovery-2026-05-17/grep_no_desktop.txt`.
> 2. **Grep verification (new path present):** `grep -n "Developer/GitHub" anvil/src/config.py` — expected exactly 2 matches (lines 11 and 131). Capture to `grep_developer_present.txt`.
> 3. **Commit landed on main:** Read SHA `74c6dce` from the DEV log, then `git --no-pager log --oneline -10` and confirm that SHA is present in current main history. Capture to `git_log.txt`. Anchor on the SHA, NOT HEAD position.
> 4. **Tests pass:** `pytest anvil/tests/` (targeted). Capture full output to `pytest_targeted.txt`. Expected: all 217 tests pass.
>
> Write the QA report to `anvil/knowledge/qa/2026-05-17-config-path-fix-qa.md` with a verification table: `| Check | Expected | Status (✅/❌) | Evidence (file path) |`. Cite evidence files by path. No hedging keywords in ✅ rows.
>
> **Rule 20 self-check.** Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:
> - `plan_slug`: `executable-anvil-config-path-fix-qa-recovery-2026-05-17`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/2026-05-17-config-path-fix-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/evidence/executable-anvil-config-path-fix-qa-recovery-2026-05-17/`
> - `required_evidence_files`: `["grep_no_desktop.txt", "grep_developer_present.txt", "git_log.txt", "pytest_targeted.txt"]`
>
> Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, do not proceed with closure — halt and report to CEO.
>
> **Deposit:**
> - `anvil/knowledge/qa/2026-05-17-config-path-fix-qa.md`
> - `anvil/knowledge/qa/evidence/executable-anvil-config-path-fix-qa-recovery-2026-05-17/grep_no_desktop.txt`
> - `anvil/knowledge/qa/evidence/executable-anvil-config-path-fix-qa-recovery-2026-05-17/grep_developer_present.txt`
> - `anvil/knowledge/qa/evidence/executable-anvil-config-path-fix-qa-recovery-2026-05-17/git_log.txt`
> - `anvil/knowledge/qa/evidence/executable-anvil-config-path-fix-qa-recovery-2026-05-17/pytest_targeted.txt`
>
> **Output Receipt.**
> - Files Created or Modified (Code): none
> - Files Deposited: (5 files listed above)
> - Receipt Status: Complete
>
> **Prompt Feedback.** If anything in this prompt was unclear, deposit a brief note to `anvil/knowledge/qa/agent-prompt-feedback.md`.
>
> **STOP. Do NOT move the plan to Done. Wait for CEO confirmation.**
