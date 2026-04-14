# Anvil — Fix Pre-existing Test Failures (fixture threshold realignment)
**Date:** 2026-04-14 | **Tier:** Small | **Test Scope:** full-suite | **Priority:** 1 | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. This continues step by step until the plan is complete. The agent must never skip steps, auto-chain to the next step, or move the plan to Done without completing all steps including QA.

**Bootstrap:**
```
Read the plan at anvil/knowledge/decisions/executable-anvil-test-failures-fixture-2026-04-14.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — DEV (Anvil Developer)

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/executable-anvil-test-failures-fixture-2026-04-14.md", "anvil/knowledge/decisions/in-progress-executable-anvil-test-failures-fixture-2026-04-14.md")`. **Skip specialist file and glossary reads — this is a test fixture edit task.** You are the Anvil Developer fixing two pre-existing test failures in `tests/test_lab.py`. Root cause is locked in `anvil/knowledge/research/anvil-test-failures-diagnostic-2026-04-14.md` — threshold misconfiguration: `STALENESS_THRESHOLD=0.8` and `COCHANGE_MIN_COUNT=5` in `src/config.py` exceed what the `lab_project` fixture seeds (0.7 and 4 respectively). **Do NOT change `src/config.py`** — fix the fixture to align with production thresholds.
>
> **Pre-flight safety check (mandatory, do this BEFORE editing):** run `grep -n "staleness_score" tests/test_lab.py` and `grep -n "cochange_count\|hash3\|hash_other" tests/test_lab.py`. Read the surrounding context of every match. Confirm that (a) no test other than `test_find_staleness_alerts` asserts on the literal value `0.7` for risky_func's staleness, and (b) no test asserts on an exact cochange_count of 4 or on exactly 4 shared commits. If ANY match would be broken by the planned fixture changes, STOP and report findings to the CEO in your Output Receipt — do not proceed with edits. If the pre-flight check is clean, proceed.
>
> **Edit 1 — staleness fix:** in `tests/test_lab.py`, locate the `create_health_score` call for `c1` (risky_func) inside the `lab_project` fixture (around lines 65–68 per diagnostic). Change `staleness_score=0.7` to `staleness_score=0.85`. Also update the inline comment on `test_find_staleness_alerts` from `# staleness=0.7 >= 0.6 threshold` to `# staleness=0.85 >= 0.8 threshold`.
>
> **Edit 2 — cochange fix:** in the same fixture, after the existing 4 shared commits for main.py and utils.py (around line 115 per diagnostic), add a 5th pair of `create_git_change` calls: one for `main.py` and one for `utils.py`, both with `commit_hash="hash4"`, date `"2026-03-24"`, message `"commit 4"`, author `"dev"`. Match the exact calling convention of the existing 4 commits — copy the signature from the immediately preceding calls rather than inventing it.
>
> **Verify locally:** run `python -m pytest tests/test_lab.py::test_find_staleness_alerts tests/test_lab.py::test_find_cochange_patterns -xvs` and confirm both pass. Then run `python -m pytest tests/test_lab.py -x` and confirm the full lab test file is green (no regressions from the fixture change). Commit with message `test: realign lab_project fixture with STALENESS_THRESHOLD=0.8 and COCHANGE_MIN_COUNT=5`. **Deposit a development log** to `anvil/knowledge/development/anvil-test-failures-fixture-fix-2026-04-14.md` with the standard Output Receipt. In "Files Created or Modified (Code)" list `tests/test_lab.py` with a one-line description of each of the 3 edits (staleness value, comment update, new cochange commit pair). Include the git commit hash. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA (Anvil QA Analyst)

---

