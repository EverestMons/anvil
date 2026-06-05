# Anvil — Fix: Orphan-Chunk Reconciliation (deleted-file prune + bypass-surface freshness filters)
**Date:** 2026-06-05 | **Tier:** Fix | **Dispatch Mode:** manual_bootstrap | **Test Scope:** full-suite | **Execution:** Step 1 (ANVIL SA) → Step 2 (ANVIL DEV) → Step 3 (ANVIL QA) | **qa_steps:** 3 | **pause_for_verdict:** after_step_1

**auto_close:** false

## Context

Two BACKLOG items (both 2026-06-03), one root: orphan `code_chunks` rows leak through Lab paths that bypass `health_scores`. The intent-gap phantom fix (`2421f83`, `last_seen_cycle`) scoped the **scorer** and **`find_intent_gaps()`** to the current snapshot, transitively protecting every finding type that flows through `health_scores` (coverage, coupling, staleness, complexity). But three readers touch `code_chunks` directly and bypass that protection:

- **`find_clone_candidates` (`lab.py:187`)** — joins `chunk_similarities → code_chunks a/b`, filtered only on `cs.cycle_id` and `a.project_id`. No `last_seen_cycle` predicate. Verified.
- **`find_best_practice_deviations` (`lab.py:316`)** — reads `code_chunks WHERE project_id=? AND functional_role IS NOT NULL AND chunk_type NOT IN ('module','test_case')`. No cycle or freshness predicate at all. **Second bypass surface — the BACKLOG only tagged this line as "audit"; it is structurally the same bug as clone_candidates.** Verified.
- **`generate_specialist_update_data` (`lab.py:768+`)** — aggregate chunk/dep/sim COUNTs with no freshness filter, so orphans inflate the "current DB stats" fed to specialist sync. Verified.

**Two orphan populations, two mechanisms:**
- **(a2) deleted-file orphans** — chunks whose source file no longer exists on disk (the BACKLOG's 1,599-figure population, pre-fix). These persist as dead rows and inflate stats. **Root fix: prune them during SCAN.**
- **(a1) surviving-file orphans** — chunks whose file still exists but whose function was removed/renamed on rebuild (the `rates_grid` case). The deleted-file prune does NOT touch these (their file exists), so they can still surface on the two bypass finding-surfaces. **Fix: a `last_seen_cycle = current` filter on the two surfaces.**

**CEO decision (2026-06-05): path (a) — DELETE deleted-file orphans during SCAN**, scoped to module-chunk orphans of deleted files (and their child chunks) only. Pre-prune DB backup + logged count required. The destructive-op authority is CEO-granted for this prune specifically — document the deviation from Anvil's non-destructive default in the blueprint with the CEO-approval flag; do NOT re-escalate the delete itself.

**Scope boundary:** the (a1) surviving-file orphans are NOT pruned (they stay; the phantom fix's stamping/filtering already excludes them from `health_scores` surfaces). For the two bypass surfaces, the (a1) case is handled by a freshness FILTER, not a delete. That filter is **evidence-gated**: Step 1 sizes whether (a1) orphans actually leak through clone/bp today; if the leak is zero the CEO may defer the filter at the after-step-1 pause.

**Cascade is already schema-handled:** `PRAGMA foreign_keys=ON` (`db.py:24`) plus `ON DELETE CASCADE` on `chunk_symbol_bindings`, `chunk_dependencies` (source), `chunk_similarities` (both sides), and `chunk_provenance`; `parent_chunk_id` and `chunk_dependencies.target_chunk_id` are `ON DELETE SET NULL`. A plain `DELETE FROM code_chunks WHERE id IN (orphans)` cascades cleanly — the BACKLOG's manual-cascade worry is largely moot, but Step 1 must confirm empirically on a DB copy.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan and executes Step 1 ONLY (the SA blueprint + sizing), then STOPS for CEO review before any code or DB write. Advance step-by-step on CEO confirmation.

**Bootstrap prompt:**
```
Read the plan at anvil/knowledge/decisions/executable-anvil-orphan-chunk-reconciliation-2026-06-05.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2, do NOT write any source code, do NOT run any DELETE against anvil.db, do NOT move the plan to Done.
```

---
---

## STEP 1 — ANVIL SA

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and your immediate next action.** Do NOT rename the plan file — manual_bootstrap dispatch.
>
> **You are the Anvil Systems Analyst.** Read your specialist file first for schema/scoring orientation. Skip the domain glossary. Working directory `/Users/marklehn/Developer/GitHub/`. **This step is design + read-only sizing only — write NO source code, run NO DELETE, make NO writes to `anvil/anvil.db`.** Cascade-testing happens against a COPY of the DB only (see (3)). `git --no-pager` on any git call.
>
> Read the two source surfaces before designing: `anvil/src/lab.py` (`find_clone_candidates` ~187, `find_best_practice_deviations` ~316, `generate_specialist_update_data` ~768), `anvil/src/scanner.py` (`discover_files` ~71), and how `anvil/src/cycle.py` sequences SCAN. The phantom-fix blueprint `anvil/knowledge/architecture/intent-gap-phantom-fix-blueprint-2026-06-03.md` is your reference for the `last_seen_cycle` substrate already in place.
>
> Produce a prune + filter blueprint that the DEV implements. Resolve every decision below — do not leave them to the implementer.
>
> **(0) Size both orphan populations at cycle 20 (read-only against `anvil.db`).**
> - **(a2) deleted-file orphans:** module chunks (`chunk_type='module'`) for invoice-pulse whose `file_path` is NOT present on disk under `invoice-pulse/` (walk the tree read-only, same exclusions Anvil's scanner uses). Report the module count, the total child-chunk count that would cascade, and a sample. The BACKLOG's pre-fix figure was 1,599 module chunks (1 production `.py`) — reconfirm at the current cycle.
> - **(a1) surviving-file orphans on the bypass surfaces:** of the chunks NOT stamped with the current `last_seen_cycle` whose file DOES still exist, how many currently carry a `chunk_similarities` row (would surface in `find_clone_candidates`) and how many satisfy the `find_best_practice_deviations` predicate. Report counts + samples. **This decides whether the two-surface filter in (5) is load-bearing or deferrable.**
>
> **(1) Bypass-surface enumeration.** Grep every reader of `code_chunks` across `anvil/src/` that does NOT join through `health_scores`. Confirm the three known surfaces and surface any others. Output a table: `| Reader | Location | Reads through health_scores? | Orphan exposure (a1/a2/both) | Fix (prune-resolves / needs-filter) |`.
>
> **(2) Prune design.** Specify the exact SCAN hook — file:function and insertion point — where deleted-file orphans are pruned (after `discover_files()` produces the on-disk file set, before EXTRACT). Scope: module-chunk orphans of DELETED files for the project being scanned, AND their child chunks. State precisely how the on-disk file set is computed (same exclusions as the scanner) and the exact DELETE (or DELETE set) issued. Confirm child chunks are removed via cascade vs explicit deletion.
>
> **(3) Cascade verification on a DB COPY.** `cp anvil/anvil.db /tmp/anvil-cascade-test.db`, open with `PRAGMA foreign_keys=ON`, run the prune DELETE for the (a2) set, and confirm rows in `chunk_symbol_bindings` / `chunk_dependencies` / `chunk_similarities` / `chunk_provenance` / `health_scores` for the deleted chunk_ids are gone (CASCADE) and that `parent_chunk_id` / `chunk_dependencies.target_chunk_id` SET-NULL links behave as expected (no dangling-FK errors). Dump before/after row counts to the blueprint. **Never run the DELETE against `anvil/anvil.db`.**
>
> **(4) Backup + idempotency + logging.** Specify a pre-prune timestamped backup of `anvil.db` (path/naming convention) that fires in the SCAN path BEFORE the first prune of a run, so the first production cycle auto-backs-up. Specify the log line (deleted module count + child count + sample chunk_ids). Confirm re-running with no orphans is a clean no-op.
>
> **(5) Two-surface freshness filter (evidence-gated by (0)/(1)).** Specify the exact WHERE-clause addition for `find_clone_candidates` (BOTH sides: `a.last_seen_cycle = ? AND b.last_seen_cycle = ?`) and `find_best_practice_deviations`, and whether `generate_specialist_update_data`'s count queries need the same. Define "current cycle" precisely. **If (0) shows zero (a1) leak through clone/bp today, recommend deferring the filter with a BACKLOG note and flag the defer/include decision for the CEO at the pause** — do not silently include or drop it.
>
> **(6) Scope-boundary confirmation.** State explicitly that (a1) surviving-file orphans are NOT pruned, and why (they remain excluded from `health_scores` surfaces by the existing stamping; the only residual exposure is the two bypass surfaces, handled by (5) not by deletion). Confirm the prune touches only deleted-file module chunks and their children.
>
> **(7) "How to verify this was implemented correctly"** — required section. Runnable checks: backup file is created before prune; a scan prunes the (a2) module orphans and their children; the named production orphan(s) from (0) no longer appear in `code_chunks`; cascade left no dangling rows; `generate_specialist_update_data` counts drop by exactly the pruned total; if the filter ships, clone/bp surfaces no longer return (a1) orphans; legitimate findings otherwise unchanged vs cycle 20.
>
> **(8) Test surface.** Enumerate the test files the DEV must update/add (`test_db.py` / `test_scanner.py` / `test_cycle.py` for the prune + backup, `test_lab.py` for the two-surface filter if included). Note the contract change and that full-suite QA is required.
>
> **Deposit the blueprint to** `anvil/knowledge/architecture/orphan-chunk-reconciliation-blueprint-2026-06-05.md` (`with open()`, never heredoc). Lead with a one-paragraph summary stating the (a2) count, the (a1)-leak count, and your filter include/defer recommendation. Include the CEO-approval flag for the destructive prune (path a, 2026-06-05) — document the non-destructive-default deviation; do NOT re-escalate the delete.
>
> Commit: `docs: SA blueprint — orphan-chunk reconciliation (deleted-file prune)`.
>
> Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md` before reporting Complete.
>
> **Deposits:**
> - `anvil/knowledge/architecture/orphan-chunk-reconciliation-blueprint-2026-06-05.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT write code or run any DELETE. Wait for CEO confirmation — the CEO reviews this blueprint (and the filter include/defer call) before implementation.**

---
---

## STEP 2 — ANVIL DEV

---

> Before starting, read `anvil/knowledge/architecture/orphan-chunk-reconciliation-blueprint-2026-06-05.md` and check its Output Receipt status. If not Complete, stop and report the blocker before proceeding.
>
> **You are the Anvil Developer.** Read your specialist file first; skip the domain glossary. Working directory `/Users/marklehn/Developer/GitHub/`. Implement the blueprint **exactly** — it has resolved the prune hook/scope, the backup mechanism, the cascade behavior, and the filter include/defer decision (honor the CEO's call recorded in the blueprint). If any instruction is ambiguous or reveals an implementation problem, STOP and flag to SA/CEO rather than improvising a schema or scope decision. Do NOT widen the prune beyond deleted-file module chunks + their children. Do NOT modify invoice-pulse source (Anvil is read-only on targets).
>
> Implement in this order: (1) the pre-prune timestamped `anvil.db` backup in the SCAN path, firing before any prune; (2) the deleted-file orphan prune at the blueprint's specified hook, relying on cascade for child/dependent rows, with the specified log line; (3) the two-surface freshness filter on `find_clone_candidates` and `find_best_practice_deviations` (and stats queries) — ONLY if the blueprint marks it included; if deferred, skip and confirm the BACKLOG note exists. All file writes use `with open()` — never heredoc.
>
> Verify cascade against a COPY, never prod, during development. Run the full suite: `cd anvil && python3 -m pytest tests/ -v`. Update/add tests per blueprint section (8); get to green. Commit with a descriptive message (no `git push` — the Planner pushes at session-wrap). Deposit an implementation log to `anvil/knowledge/development/orphan-chunk-reconciliation-2026-06-05.md` referencing the blueprint, with pass/fail counts and the exact prune/filter changes made.
>
> Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `anvil/knowledge/development/orphan-chunk-reconciliation-2026-06-05.md`
>
> **STOP. Do NOT proceed to Step 3. Do NOT move the plan to Done. Wait for CEO confirmation.**

---
---

## STEP 3 — ANVIL QA

---

> Before starting, read `anvil/knowledge/development/orphan-chunk-reconciliation-2026-06-05.md` and check its Output Receipt status. If not Complete, stop and report the blocker before proceeding.
>
> **You are the Anvil QA Analyst.** Read your specialist file first; skip the domain glossary. Working directory `/Users/marklehn/Developer/GitHub/`. **Read-only on source — verify, do not fix.** All DB-mutation verification runs against a COPY, never `anvil/anvil.db`. Evidence files go to `anvil/knowledge/qa/evidence/executable-anvil-orphan-chunk-reconciliation-2026-06-05/`.
>
> **(a) Deliverable verification (Rule 17) — do this FIRST.** Read the Step 2 dev-log "Files Created or Modified (Code)" list and verify EVERY item: grep the backup hook, the prune, and (if included) the two-surface filter exist in source (dump to `grep_deliverables.txt`). Output a table `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Any ❌ blocks the plan.
>
> **(b) Prune correctness — core check, on a DB COPY.** `cp anvil/anvil.db` to a scratch path; run a scan (or the prune path) against the copy. Confirm: the backup file is created before the prune; the (a2) deleted-file module orphans and their children are removed; the named production orphan(s) from the blueprint sizing no longer appear in `code_chunks`; no dangling-FK rows remain in `chunk_symbol_bindings` / `chunk_dependencies` / `chunk_similarities` / `chunk_provenance` / `health_scores`; live chunks are untouched (count delta equals exactly the pruned total). Dump to `prune_check.txt`.
>
> **(c) Bypass-surface check.** Confirm `generate_specialist_update_data` counts dropped by exactly the pruned total. If the filter shipped, confirm `find_clone_candidates` and `find_best_practice_deviations` no longer return the (a1) orphans identified in the blueprint; dump before/after to `surface_check.txt`. If the filter was deferred, confirm the BACKLOG note exists and state the residual (a1) exposure explicitly.
>
> **(d) Full suite (Test Scope: full-suite).** Run `cd anvil && python3 -m pytest tests/ -v`, dump to `pytest_full.txt`. All must pass; note any pre-existing-vs-new failures explicitly.
>
> **(e)** Deposit the QA report to `anvil/knowledge/qa/orphan-chunk-reconciliation-qa-2026-06-05.md` with the verification table and evidence-file paths (paths, not paraphrase). Update `anvil/PROJECT_STATUS.md` with a summary of all changes across the plan. Append prompt feedback → `anvil/knowledge/research/agent-prompt-feedback.md`. Make the final commit (no `git push`). Do NOT move the plan to Done — that is the close-path's job after CEO verification.
>
> **Deposits:**
> - `anvil/knowledge/qa/orphan-chunk-reconciliation-qa-2026-06-05.md`
> - evidence files under `anvil/knowledge/qa/evidence/executable-anvil-orphan-chunk-reconciliation-2026-06-05/`
>
> **STOP. Report Complete and wait for CEO verification.**
