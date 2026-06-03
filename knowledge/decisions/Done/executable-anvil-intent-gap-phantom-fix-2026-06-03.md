# Anvil — Fix: Intent-Gap Phantom-Function Elimination (last_seen_cycle)
**Date:** 2026-06-03 | **Tier:** Fix | **Dispatch Mode:** manual_bootstrap | **Test Scope:** full-suite | **Execution:** Step 1 (ANVIL SA) → Step 2 (ANVIL DEV) → Step 3 (ANVIL QA) | **qa_steps:** 3 | **pause_for_verdict:** after_step_1

**auto_close:** false

## Context

Diagnostic `intent-gap-phantom-mechanism-2026-06-03.md` (in `knowledge/research/`, now closed to `decisions/Done/`) named the mechanism: **(a1) stale orphan chunks in surviving files**, uniform across all five phantoms. Chain: the extractor upserts functions the parser currently finds and never prunes removed ones (`extractor.py:59-115`); the scorer loads ALL non-module chunks with no cycle filter and mints fresh current-cycle `health_scores` for the dead ones (`scorer.py:41-46`); `find_intent_gaps()` joins `health_scores → code_chunks` filtered only to the latest cycle, with no freshness predicate (`lab.py:416`, query ~468-479). Identity comes from `code_chunks.name`, never `git_changes` — mechanism (b) ruled out. Mechanism (a2) (orphan from a fully-deleted file) was untested (the `rates_grid` specimen turned out to be a surviving rebuilt file) but the code is structurally vulnerable: no file-set reconciliation in SCAN.

**Schema facts from the diagnostic:** `code_chunks` has `cycle_id` (records the *creating* cycle, never updated on re-scan) and `updated_at`, but NO `last_seen_cycle` / `deleted_at` / active flag. The five phantom chunk_ids: `rates_grid` 4114, `import_contract_setup` 4051 (renamed; new `_import_contract_setup_section` 5384), `record_response` 3777, `_auto_route_after_response` 3778, `confirm_carrier` 3775 — all cycle_id ≤ 6, all carry cycle-19 `health_scores`.

**CEO decision (2026-06-03): fix philosophy A — soft-delete / freshness stamp, non-destructive.** Add a `last_seen_cycle` column to `code_chunks`, stamp it on every scan for chunks the parser currently finds, and scope the **scorer** (not just `find_intent_gaps`) to current-snapshot chunks. The CEO has pre-approved the column add (SA decision-authority schema-deviation gate is cleared for `last_seen_cycle` specifically) — document the deviation in the blueprint with the CEO-approval flag; do NOT re-escalate the column itself. This plan's scope is the **phantom (a1) fix only**; the `last_seen_cycle` substrate is noted as future groundwork for the sibling volatility bugs (self-resolve, percentile-inversion) but those are explicitly OUT of scope here.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY (the SA blueprint), then STOPS for CEO review of the design before any code is written. Advance step-by-step on CEO confirmation.

**Bootstrap prompt:**
```
Read the plan at anvil/knowledge/decisions/executable-anvil-intent-gap-phantom-fix-2026-06-03.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2, do NOT write any source code, do NOT move the plan to Done.
```

---
---

## STEP 1 — ANVIL SA

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and your immediate next action.** Do NOT rename the plan file — manual_bootstrap dispatch.
>
> **You are the Anvil Systems Analyst.** Read your specialist file first for schema/scoring orientation, and read the diagnostic findings at `anvil/knowledge/research/intent-gap-phantom-mechanism-2026-06-03.md` in full — it has the exact line refs, column lists, and chunk_ids you will design against. Skip the domain glossary. Working directory `/Users/marklehn/Developer/GitHub/`. **This step is design only — write NO source code, make NO DB writes.** `git --no-pager` on any git call.
>
> **Design the fix for philosophy A.** Produce a schema-migration + pipeline blueprint that the DEV will implement. The blueprint MUST resolve every decision below — do not leave them to the implementer.
>
> **(0) Size the (a2) population (read-only).** Before designing, run one read-only query against `anvil/anvil.db`: the set of `code_chunks` module file_paths (chunk_type='module') for the invoice-pulse project MINUS the set of files currently on disk under `invoice-pulse/` (walk the tree read-only, same exclusions Anvil's scanner uses). Report the count of module chunks whose files no longer exist, and a sample. This decides whether SCAN file-set reconciliation is load-bearing for v1 or can be deferred. State your recommendation: include reconciliation in this fix, or defer with a BACKLOG note.
>
> **(1) Schema migration.** DDL to add `last_seen_cycle INTEGER` to `code_chunks` (nullable; rationale for default). Migration must be idempotent and guard against re-application (check `PRAGMA table_info` before ALTER), per the DEV's "handle schema migrations gracefully" standard. Specify exactly where the migration runs (db.py schema-init path).
>
> **(2) Write-path stamping.** Specify precisely where `last_seen_cycle` gets set to the current cycle for every chunk the parser finds this scan — at the scanner level, the extractor upsert level, or both. The diagnostic showed the extractor's upsert branch (`extractor.py:59-115`) is where present-function chunks are touched (insert/update/skip-unchanged). The skip-unchanged branch is the trap: a chunk whose content_hash is identical is currently NOT touched, so it must STILL get its `last_seen_cycle` bumped. Design so unchanged chunks are stamped too.
>
> **(3) Backfill / cold-start.** The DB already holds 5,753 chunks with no `last_seen_cycle`. Resolve: how do existing live chunks acquire their first value — a one-time backfill pass at migration time (e.g. stamp every chunk whose file+function currently exists), OR rely on the first post-fix scan to stamp live chunks? State what `find_intent_gaps()` returns in the interim window if the latter. Pick one and justify; the DEV implements exactly this.
>
> **(4) Scorer scoping.** Specify the change to `scorer.py:41-46` so it scores only current-snapshot chunks (`last_seen_cycle = <current cycle>`), not all non-module chunks. Define "current cycle" precisely (the cycle_id being scored in this run). Confirm this does not strand legitimately-unchanged chunks (they are stamped per (2)).
>
> **(5) find_intent_gaps guard (belt-and-suspenders).** Specify the freshness predicate added to `lab.py:416`'s query so even if a stale chunk slips through scoring, it is not surfaced. State the exact WHERE clause.
>
> **(6) Cascade/blast-radius check.** Confirm philosophy A is non-destructive: no DELETEs, so `chunk_dependencies` / `chunk_similarities` / `chunk_symbol_bindings` / `chunk_provenance` / `health_scores` history are untouched. Note any consumer that reads `code_chunks` expecting all-rows-are-live and might need the same freshness filter (grep for readers of `code_chunks`).
>
> **(7) "How to verify this was implemented correctly"** — required section. Concrete, runnable checks: the migration added the column; a post-fix scan stamps live chunks with the current cycle; the five named phantom chunk_ids (4114, 4051, 3777, 3778, 3775) carry a `last_seen_cycle` < current after a scan; `find_intent_gaps()` no longer returns those five; legitimate current findings are unchanged in count/identity vs cycle 19 minus the known phantoms.
>
> **(8) Test surface.** Enumerate which test files the DEV must update/add (`test_db.py` migration, `test_extractor.py` stamping incl. skip-unchanged path, `test_scorer.py` scoping, `test_lab.py` guard). Note the contract change (scorer/lab now filter on freshness) and that full-suite QA is required.
>
> **Deposit the blueprint to** `anvil/knowledge/architecture/intent-gap-phantom-fix-blueprint-2026-06-03.md` (`Filesystem:write_file` or `with open()`, never heredoc). Lead with a one-paragraph summary stating the (a2) count and your reconciliation recommendation. Include the CEO-approval flag for the `last_seen_cycle` column.
>
> Commit: `docs: SA blueprint — intent-gap phantom fix (last_seen_cycle)`.
>
> Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md` before reporting Complete.
>
> **Deposits:**
> - `anvil/knowledge/architecture/intent-gap-phantom-fix-blueprint-2026-06-03.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT write code. Wait for CEO confirmation — the CEO reviews this blueprint before implementation.**

---
---

## STEP 2 — ANVIL DEV

---

> Before starting, read `anvil/knowledge/architecture/intent-gap-phantom-fix-blueprint-2026-06-03.md` and check its Output Receipt status. If not Complete, stop and report the blocker before proceeding.
>
> **You are the Anvil Developer.** Read your specialist file first; skip the domain glossary. Working directory `/Users/marklehn/Developer/GitHub/`. Implement the blueprint **exactly** — it has resolved the migration, stamping (including the skip-unchanged path), backfill/cold-start, scorer scoping, and the find_intent_gaps guard. If any blueprint instruction is ambiguous or reveals an implementation problem, STOP and flag to the SA/CEO rather than improvising a schema decision.
>
> Implement in this order: (1) the idempotent migration in the db.py schema path; (2) the backfill/cold-start exactly as the blueprint specifies; (3) write-path stamping in the extractor (and scanner if the blueprint says so), ensuring unchanged chunks are stamped; (4) scorer scoping; (5) the find_intent_gaps freshness guard. All file writes use `with open()` — never heredoc. Do NOT modify invoice-pulse source (Anvil is read-only on targets).
>
> Run the full suite: `cd anvil && python3 -m pytest tests/ -v`. Update/add tests per blueprint section (8). Get to green. Commit with a descriptive message (no `git push` — the Planner pushes at session-wrap). Deposit an implementation log to `anvil/knowledge/development/intent-gap-phantom-fix-2026-06-03.md` referencing the blueprint and including pass/fail counts.
>
> Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `anvil/knowledge/development/intent-gap-phantom-fix-2026-06-03.md`
>
> **STOP. Do NOT proceed to Step 3. Do NOT move the plan to Done. Wait for CEO confirmation.**

---
---

## STEP 3 — ANVIL QA

---

> Before starting, read `anvil/knowledge/development/intent-gap-phantom-fix-2026-06-03.md` and check its Output Receipt status. If not Complete, stop and report the blocker before proceeding.
>
> **You are the Anvil QA Analyst.** Read your specialist file first; skip the domain glossary. Working directory `/Users/marklehn/Developer/GitHub/`. **Read-only on source — verify, do not fix.** Evidence files go to `anvil/knowledge/qa/evidence/executable-anvil-intent-gap-phantom-fix-2026-06-03/`.
>
> **(a) Deliverable verification (Rule 17) — do this FIRST.** Read the Step 2 dev-log Output Receipt "Files Created or Modified (Code)" list and verify EVERY item: `PRAGMA table_info(code_chunks)` shows `last_seen_cycle` (dump to `pragma_code_chunks.txt`); grep the stamping, scorer-scoping, and lab guard changes exist in source (dump to `grep_deliverables.txt`). Output a table `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Any ❌ blocks the plan.
>
> **(b) Phantom elimination — the core check.** Following the blueprint's "How to verify" section, confirm a post-fix scan stamps live chunks and that `find_intent_gaps()` no longer returns the five phantom chunk_ids (4114, 4051, 3777, 3778, 3775). Dump the find_intent_gaps output before/after framing to `phantom_check.txt`. Confirm legitimate findings are otherwise unchanged vs cycle 19 (minus the known phantoms) — dump to `findings_delta.txt`.
>
> **(c) Full suite (Test Scope: full-suite).** Run `cd anvil && python3 -m pytest tests/ -v`, dump to `pytest_full.txt`. All must pass; note any pre-existing-vs-new failures explicitly.
>
> **(d)** Deposit the QA report to `anvil/knowledge/qa/intent-gap-phantom-fix-qa-2026-06-03.md` with the verification table and evidence-file paths in the Evidence column (paths, not paraphrase). Then update `anvil/PROJECT_STATUS.md` with a summary of all changes across the plan. Then append prompt feedback → `anvil/knowledge/research/agent-prompt-feedback.md`. Then make the final commit (no `git push`). Do NOT move the plan to Done — that is the close-path's job after CEO verification.
>
> **Deposits:**
> - `anvil/knowledge/qa/intent-gap-phantom-fix-qa-2026-06-03.md`
> - evidence files under `anvil/knowledge/qa/evidence/executable-anvil-intent-gap-phantom-fix-2026-06-03/`
>
> **STOP. Report Complete and wait for CEO verification.**
