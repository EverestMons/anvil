# Anvil — ANVIL_ROOT hardcode (F8 close-out)
**Date:** 2026-05-18 | **Tier:** small | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_step_1

## Context

F1 (2026-05-17) and F4 (2026-05-17) closed two corners of a triangle: `SCAN_TARGETS` and `DEV_LOG_PATHS` are hardcoded to absolute `/Users/marklehn/Developer/GitHub/...` paths. The third corner — `ANVIL_ROOT` itself — still resolves dynamically from `__file__`:

```python
ANVIL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

Inside a Bellows worktree, `__file__` resolves to `/Users/marklehn/Developer/GitHub/anvil/.bellows-worktrees/<slug>/src/config.py`, which makes `ANVIL_ROOT` point at the worktree and `ANVIL_DB_PATH` point at a worktree-local `anvil.db` that does not exist. F2 (2026-05-18 morning) found cycle 17 had recorded a `.bellows-worktrees/...` path that disappeared at teardown — same root cause.

This plan replaces the dynamic resolution with a hardcoded canonical path, symmetric with the F1/F4 fixes. It is a one-line constant change plus an audit of any test that monkey-patches `ANVIL_ROOT` for isolation.

**Why hardcoding is the right shape:** All Anvil DB writes and config-relative paths must address the canonical main-repo location regardless of the calling context. Dynamic resolution is what produced the worktree-path leak; preserving dynamism while patching the symptom would be fragile.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. Step 1 runs DEV. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2 (QA).

**Bootstrap prompt:**
```
Read the plan at anvil/knowledge/decisions/executable-anvil-root-hardcode-2026-05-18.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — ANVIL DEV

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/executable-anvil-root-hardcode-2026-05-18.md", "anvil/knowledge/decisions/in-progress-executable-anvil-root-hardcode-2026-05-18.md")`.
>
> Read your specialist file and `anvil/knowledge/research/domain-glossary.md` first. **You are the Anvil DEV.** Working directory is `/Users/marklehn/Developer/GitHub/`. Note that Bellows runs plans in a worktree at `anvil/.bellows-worktrees/anvil-root-hardcode-2026-05-18/`; the worktree IS the anvil root from the agent's perspective. Use paths relative to the worktree root (e.g., `src/config.py`, not `anvil/src/config.py`). The DB `anvil.db` is not in the worktree — it lives at `/Users/marklehn/Developer/GitHub/anvil/anvil.db` (main repo).
>
> **Context recap:** `ANVIL_ROOT` on line 6 of `src/config.py` resolves dynamically via `__file__`. Inside a Bellows worktree this resolves to the worktree path, not the main repo path. This plan hardcodes `ANVIL_ROOT` to `/Users/marklehn/Developer/GitHub/anvil`, symmetric with the existing F1 hardcodes for `SCAN_TARGETS` and `DEV_LOG_PATHS`.
>
> **Do exactly this:**
>
> **(1) Audit before changing.** Run `grep -rn "ANVIL_ROOT" src/ tests/ 2>&1` and capture every usage. Read each call site (production AND tests). Specifically identify: (a) any test that monkey-patches `ANVIL_ROOT` for isolation (e.g., `monkeypatch.setattr`, fixture overrides, `tmp_path` substitution), (b) any production code that relies on `ANVIL_ROOT` being mutable at runtime. If any test mutates `ANVIL_ROOT`, the hardcode change is still safe (mutation still works on the new literal), but document the find for the dev log. Halt and report if you discover a production code path that REQUIRES dynamic resolution (e.g., for portability across environments) — that would change the fix shape.
>
> **(2) Apply the one-line change.** Edit `src/config.py` line 6: replace `ANVIL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` with `ANVIL_ROOT = "/Users/marklehn/Developer/GitHub/anvil"`. The `import os` on line 4 may now be unused — check via `grep -n "os\." src/config.py`. If `os.path.join` is still used on `ANVIL_DB_PATH` line 8 (it is), keep the import. Do not delete the import unless it becomes genuinely unused.
>
> **(3) Run the full test suite.** `python3 -m pytest tests/ -v 2>&1 | tail -50`. Expected: 219 tests pass (same as the F9-follow recovery's baseline). If any test fails, investigate before proceeding. A failure here likely means a test relied on `ANVIL_ROOT` resolving to a test-temp path — examine and decide whether the test or the fix needs adjustment.
>
> **(4) Confirm new value resolves correctly inside the worktree.** Run a one-liner Python check: `python3 -c "from src.config import ANVIL_ROOT, ANVIL_DB_PATH; print(repr(ANVIL_ROOT)); print(repr(ANVIL_DB_PATH))" 2>&1`. Both should print the canonical main-repo path, not the worktree path. This is the proof the fix is doing what it claims.
>
> **(5) Commit.** Single commit with message `fix(config): hardcode ANVIL_ROOT to canonical main-repo path (F8 close-out)`. Include the dev log (next step) in the same commit OR a follow-up commit — either is fine, document which in the dev log.
>
> **(6) Write a dev log** at `knowledge/development/2026-05-18-anvil-root-hardcode-dev-log.md`. Include: SHA, files changed (with line numbers), audit findings from step (1), output of step (4), test result summary, and any prompt-feedback observations.
>
> Standard prompt feedback protocol — append any prompt issues to `knowledge/research/agent-prompt-feedback.md` before reporting Complete.
>
> **Deposits:**
> - `src/config.py`
> - `knowledge/development/2026-05-18-anvil-root-hardcode-dev-log.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — ANVIL QA

---

> Before starting, read `knowledge/development/2026-05-18-anvil-root-hardcode-dev-log.md` and check the Output Receipt status. If status is not Complete, stop and report the blocker before proceeding.
>
> Read your specialist file and `knowledge/research/domain-glossary.md` first. **You are the Anvil QA reviewer.** Working directory is `/Users/marklehn/Developer/GitHub/`. Note: Bellows runs plans in a worktree at `anvil/.bellows-worktrees/anvil-root-hardcode-2026-05-18/`; the worktree IS the anvil root from your perspective. Use paths relative to worktree root.
>
> **Do exactly this:**
>
> **(1) Hardcode landed.** Run `grep -n "ANVIL_ROOT" src/config.py 2>&1`. Expected: line 6 reads `ANVIL_ROOT = "/Users/marklehn/Developer/GitHub/anvil"`. Capture to `knowledge/qa/evidence/executable-anvil-root-hardcode-2026-05-18/grep_anvil_root.txt`. Mark ❌ if the literal string is absent or differs.
>
> **(2) No dynamic resolution remains.** Run `grep -n "os.path.dirname.*__file__" src/config.py 2>&1`. Expected: no matches. Capture exit code via `grep -c "os.path.dirname.*__file__" src/config.py; echo "exit:$?"` to `grep_no_dynamic.txt`. Mark ❌ if any match found.
>
> **(3) Runtime value correctness.** Run `python3 -c "from src.config import ANVIL_ROOT, ANVIL_DB_PATH; print('ROOT:', ANVIL_ROOT); print('DB:', ANVIL_DB_PATH)" 2>&1`. Expected: `ROOT: /Users/marklehn/Developer/GitHub/anvil` and `DB: /Users/marklehn/Developer/GitHub/anvil/anvil.db`. Capture to `runtime_values.txt`. Mark ❌ if either prints a worktree path.
>
> **(4) Scope creep audit.** Run `git --no-pager show --stat HEAD 2>&1` (or the SHA cited in the dev log if HEAD is not the fix commit). Capture to `git_diff_stat.txt`. Expected files: `src/config.py` and `knowledge/development/2026-05-18-anvil-root-hardcode-dev-log.md`. The dev log MAY be in a separate commit — if so, run `git --no-pager log --oneline -5` and capture to `git_log.txt`, and verify both commits are present. Mark ❌ if any unexpected file appears.
>
> **(5) Full suite.** Run `python3 -m pytest tests/ -v 2>&1` and capture to `pytest_full.txt`. Expected: all tests pass (219 ± new tests if any). Mark ❌ if any failure.
>
> **(6) Commit landed on main.** Run `git --no-pager log --oneline -10 2>&1`. Capture to `git_log.txt` (may already exist from check 4 — append or re-use). Confirm the fix SHA cited in the dev log is present in current HEAD ancestry. Mark ❌ if the commit is not findable.
>
> **(7) Write QA report** to `knowledge/qa/2026-05-18-anvil-root-hardcode-qa.md` with a verification table: `| Check | Expected | Status (✅/❌) | Evidence (file path) |`. Six rows matching checks (1)-(6). Cite evidence files by relative path under `knowledge/qa/evidence/executable-anvil-root-hardcode-2026-05-18/`. Brief "Observations" section noting whether the audit in DEV step (1) surfaced any tests that mutate `ANVIL_ROOT` and whether they still pass. NO hedging keywords in ✅ rows.
>
> **(8) Rule 20 self-check.** Run the canonical Rule 20 self-check from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. Use these values:
> - `plan_slug`: `executable-anvil-root-hardcode-2026-05-18`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/2026-05-18-anvil-root-hardcode-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/evidence/executable-anvil-root-hardcode-2026-05-18/`
> - `required_evidence_files`: `["grep_anvil_root.txt", "grep_no_dynamic.txt", "runtime_values.txt", "git_diff_stat.txt", "pytest_full.txt", "git_log.txt"]`
>
> Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, do not proceed with closure — halt and report to CEO.
>
> Standard prompt feedback protocol — append any prompt issues to `knowledge/research/agent-prompt-feedback.md` before reporting Complete.
>
> **Deposits:**
> - `knowledge/qa/2026-05-18-anvil-root-hardcode-qa.md`
> - `knowledge/qa/evidence/executable-anvil-root-hardcode-2026-05-18/`
