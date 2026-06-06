# Anvil — Cycle Report Writes to Worktree (record canonical, write runtime)
**Date:** 2026-06-05 | **Tier:** Executable | **Dispatch Mode:** bellows | **Test Scope:** full | **Execution:** Step 1 (SA) → Step 2 (DEV) → Step 3 (QA) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** always

## Execution Map
Step 1 (SA: edit map) → Step 2 (DEV: implement) → Step 3 (QA: full regression + Rule 20 self-check). Sequential.

## Context

`run_cycle` writes the cycle report via `write_cycle_report` (`lab.py:851`), which uses a single `report_path` for BOTH the file write (`:1057-1058`) and the DB record (`:1071`). Since F8 hardcoded `ANVIL_ROOT` to canonical (`config.py:6`), the file lands in canonical MAIN even when the cycle runs in a Bellows worktree — side-writing into main, dirtying/advancing it mid-run. That is the dominant trigger for the dirty-tree teardown failure class (see `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/teardown-dirty-main-rootcause-2026-06-05.md`) and the reason the anvil cycle template currently needs a Planner wrap-commit.

Fix: split write-target from recorded-path. WRITE to the runtime root (derived from `__file__` → resolves to the worktree during a worktree run), so the report lands in the worktree and rides the worktree's commit back to main. RECORD the canonical `ANVIL_ROOT` path in the DB, so `cycle_reports.report_path` stays alive after teardown (this is exactly what F8 was protecting; we keep that guarantee while fixing the write target). This removes the anvil main-advance trigger under the current cherry-pick model and is the precondition for the bellows merge-model redesign (Plan B).

**Critical guarantee (do not assume away):** writing the report into the worktree is only safe if it is actually COMMITTED there. The runner only guarantees "the final operation is a commit" — NOT `git add -A` — so a `run_cycle`-produced report can be left unstaged, uncommitted, and then LOST under the merge model (or copied to main untracked under cherry-pick, re-creating the dirty-main bug). The cycle template's DEV step must therefore EXPLICITLY stage the report. This plan makes that explicit; it is not optional.

The invoice-pulse audit-findings write (`lab.py:661`) lands in a DIFFERENT repo and does not affect anvil's teardown; it is out of scope here.

## How to Run This Plan
Bellows dispatches normally. No daemon restart needed (no Bellows code change). Pauses after every step for Planner verdict.

---
---

## STEP 1 — ANVIL SYSTEMS ANALYST

---

> **Identity:** You are the Anvil Systems Analyst. Begin with `SA claim: cycle-report worktree-write edit map` BEFORE any reads. **Reads (in order):** `agents/ANVIL_SYSTEMS_ANALYST.md`, `knowledge/research/domain-glossary.md`, `src/config.py` (ANVIL_ROOT), `src/lab.py` lines 85-115 and 845-1075 (`run_cycle` report block + `write_cycle_report`), and `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/teardown-dirty-main-rootcause-2026-06-05.md` R2-Source-A for the rationale. Ack each read.
>
> **Task:** Produce a precise edit map. No source changes. Prefix each section with a 1-line marker.
>
> (1) **Runtime vs canonical root.** Specify how to derive the runtime root (pre-F8 form: `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`), where to define it (`config.py` next to `ANVIL_ROOT`, named e.g. `ANVIL_RUNTIME_ROOT`), and confirm it resolves to the worktree when `lab.py` runs from a worktree. Keep `ANVIL_ROOT` hardcoded-canonical for records.
> (2) **`write_cycle_report` split.** Map the exact signature/caller change so the function writes the file to a `write_path` (runtime root) but stores `report_path` (canonical) in the DB. Show old→new for `lab.py:91-100` (the caller) and `:1057-1071` (the writer/recorder).
> (3) **Consumer check.** Confirm (grep) nothing reads `cycle_reports.report_path` expecting the runtime/worktree location during a run; confirm the recorded canonical path is only consumed (if at all) after teardown. State findings.
> (4) **Commit-capture — GUARANTEE, do not assume.** The runner only guarantees a final commit, NOT `git add -A`; deposit-declaration does not help (`deposit_exists` checks existence, not commit); there is no worktree-clean gate. Therefore an unstaged report is uncommitted → copied to main untracked under cherry-pick (dirty-main) or LOST under the merge model. The cycle template's DEV step MUST contain an EXPLICIT `git add knowledge/research/cycle-<N>-findings-<UTC>.md` immediately before its final commit. Specify that exact template edit here (the literal line and where it goes in the cycle-DEV step) and require §5 to include it. Do NOT conclude "no special declaration needed."
> (5) **Cycle-template impact.** The template at `knowledge/architecture/cycle-plan-template.md` currently (a) has authoring rule 3 requiring a Planner wrap-commit of the canonical report, (b) QA check (3) does `ls` on the CANONICAL path during the run, and (c) the working-dir note says the report "lands in MAIN." Under this change the report is at the WORKTREE path during the run and canonical only after teardown. Specify exact edits: retire the wrap-commit rule; correct the working-dir note; change QA check (3) to verify the worktree/runtime path during the run; AND add the explicit `git add <report>` instruction to the cycle-DEV step's commit (per §4).
> (6) **Test-impact list.** Tests that monkeypatch `ANVIL_ROOT` or assert the report write location (grep `tests/` for `ANVIL_ROOT`, `report_path`, `write_cycle_report`, `cycle.*findings`). keep/update/delete with new expectations. Any new test must use a tmp dir / monkeypatched root so it does NOT write a real `cycle-*-findings` file into the repo (an earlier run leaked a `cycle-1-findings` artifact this way).
>
> Mark unsettled items OPEN. Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/architecture/cycle-report-worktree-write-blueprint-2026-06-05.md`

---
---

## STEP 2 — ANVIL DEVELOPER

---

> Before starting, read `knowledge/architecture/cycle-report-worktree-write-blueprint-2026-06-05.md`; if any item is OPEN, STOP and report.
>
> **Identity:** You are the Anvil Developer. Begin with `DEV claim: cycle-report worktree-write impl`. **Reads:** `agents/ANVIL_DEVELOPER.md`, the blueprint, the cited `lab.py`/`config.py` regions. Ack each.
>
> **Task:** Implement the blueprint exactly, `pytest tests/ -q` after each change:
> 1. Add the runtime-root derivation (config.py) per blueprint §1.
> 2. Split `write_cycle_report` write-path vs recorded-path per §2; update the `run_cycle` caller.
> 3. Apply the cycle-template edits per §5 — including the explicit `git add <report>` line in the cycle-DEV step (§4). Verify that line is present in the template after your edit.
> 4. Update tests per §6. Any test that runs `run_cycle` MUST use a tmp dir / monkeypatched root so no real `cycle-*-findings` file is written into the repo.
> Do NOT change the invoice-pulse audit-findings write. Do NOT modify the recorded canonical path semantics (records must stay canonical).
>
> **Self-verify:** add/confirm a test proving the report file is written under the runtime root while `cycle_reports.report_path` records the canonical path; confirm the template now contains the explicit report `git add`; full `pytest tests/` green (baseline 238 — record exact); `git status` shows no stray `cycle-*-findings` artifact left in the repo.
>
> Standard prompt-feedback protocol.
>
> **Deposits:**
> - `src/config.py`, `src/lab.py`, updated test files (list them)
> - `knowledge/architecture/cycle-plan-template.md` (edited)
> - `knowledge/development/cycle-report-worktree-write-impl-2026-06-05.md` (changes, per-edit pytest, final count, the write-vs-record proof, confirmation the template `git add <report>` line is present, and a clean `git status`). Output Receipt at end.

---
---

## STEP 3 — ANVIL QA ANALYST

---

> Before starting, read `knowledge/development/cycle-report-worktree-write-impl-2026-06-05.md`; if Status not Complete, STOP.
>
> **Identity:** You are the Anvil QA Analyst. Begin with `QA claim: cycle-report worktree-write regression`. **Reads:** `agents/ANVIL_QA_ANALYST.md`, blueprint, dev log. Evidence → `knowledge/qa/evidence/executable-anvil-cycle-report-worktree-write-2026-06-05/` (`mkdir -p`).
>
> **MANDATORY — DO NOT SKIP (gate-enforced):** This step is REJECTED by the daemon's `rule_20_self_check` gate unless your QA report contains the literal Rule 20 self-check banner `Rule 20 — QA Self-Check Results` followed by `PASSED — SELF-CHECK PASSED`. The verification table does NOT satisfy this. You MUST run the canonical Rule 20 block (check (7) below) and paste its FULL literal stdout into the QA report under a `## Rule 20 Self-Check` heading. A prior run failed this gate by omitting it — do not repeat that. Before you finish, grep your own QA report for the banner string; if it is absent, you have NOT completed this step.
>
> (1) **Full suite (Rule 21).** `pytest tests/ -q > knowledge/qa/evidence/executable-anvil-cycle-report-worktree-write-2026-06-05/pytest_full.txt 2>&1`. All green; count ≥ 238 (flag if moved).
> (2) **Write-vs-record proof.** Run the cycle from a non-canonical root (tmp/sandbox) or the test that simulates it; capture that the file path written ≠ the recorded canonical path, and that the recorded path is canonical. Evidence to `.../write_vs_record.txt`.
> (3) **Report-commit guarantee.** `grep -n "git add knowledge/research/cycle" knowledge/architecture/cycle-plan-template.md > .../report_gitadd_check.txt 2>&1`. Expected: ≥1 match.
> (4) **No leaked artifact.** `git -C /Users/marklehn/Developer/GitHub/anvil status --porcelain | grep "cycle-.*-findings" > .../no_leak_check.txt 2>&1 || echo "no leak" >> .../no_leak_check.txt`. Expected: no stray findings file.
> (5) **Template edits landed.** `grep -n "wrap-commit\|worktree\|lands in MAIN" knowledge/architecture/cycle-plan-template.md > .../template_check.txt 2>&1` — confirm the wrap-commit rule is gone and the working-dir note no longer says "lands in MAIN."
> (6) **QA report** `knowledge/qa/2026-06-05-cycle-report-worktree-write-qa.md` with the `| Check | Expected | Status | Evidence |` table over (1)-(5). Hedging in a ✅ row auto-fails.
> (7) **Rule 20 self-check — REQUIRED, gate-enforced.** Open `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`, copy the Python block VERBATIM, replace ONLY the four `# PLACEHOLDER —` lines with:
>   - `plan_slug = "executable-anvil-cycle-report-worktree-write-2026-06-05"`
>   - `qa_report_path = "/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/2026-06-05-cycle-report-worktree-write-qa.md"`
>   - `evidence_dir = "/Users/marklehn/Developer/GitHub/anvil/knowledge/qa/evidence/executable-anvil-cycle-report-worktree-write-2026-06-05/"`
>   - `required_evidence_files = ["pytest_full.txt","write_vs_record.txt","report_gitadd_check.txt","no_leak_check.txt","template_check.txt"]`
>   Run it with `python3`. Paste its FULL literal stdout — including the `Rule 20 — QA Self-Check Results` banner and the `PASSED — SELF-CHECK PASSED` line — into the QA report under a `## Rule 20 Self-Check` heading. If it prints `FAILED`, fix the issue and re-run; do NOT deposit a failing self-check. The agent does NOT move the plan to Done — the Planner issues the terminal verdict.
>
> **Final self-verify before deposit:** `grep -c "Rule 20 — QA Self-Check Results" knowledge/qa/2026-06-05-cycle-report-worktree-write-qa.md` must return ≥1. If 0, you have not completed step (7).
>
> Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/qa/2026-06-05-cycle-report-worktree-write-qa.md` (MUST contain the Rule 20 self-check banner + PASSED line)
> - `knowledge/qa/evidence/executable-anvil-cycle-report-worktree-write-2026-06-05/`
