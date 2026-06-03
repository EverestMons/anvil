# Anvil — Diagnostic: Intent-Gap Phantom-Function Mechanism
**Date:** 2026-06-03 | **Tier:** Diagnostic | **Dispatch Mode:** manual_bootstrap | **Test Scope:** none (read-only) | **Execution:** Step 1 (ANVIL SA) | **Priority:** Medium

**auto_close:** false

## Context

`find_intent_gaps()` surfaces high-volatility, zero-coverage functions that no longer exist in the current codebase. Confirmed persisting cycle 17 → 18 → 19 (BACKLOG entry "2026-05-18 — Intent-gap findings include functions that no longer exist", update 2026-06-02). The cycle-19 phantoms were filtered manually at triage (`invoice-pulse/knowledge/research/anvil-findings-backlog-2026-06-03.md`, Excluded section); every cycle currently requires this manual phantom filter.

This diagnostic names the mechanism. It must **discriminate**, not just re-confirm the symptom. Two hypotheses are on the table, and they are NOT mutually exclusive — the diagnostic must be able to report (a), (b), both, or neither, and whether the answer differs by phantom class:

- **(a) Stale chunk** — the chunk row persists in `anvil.db` across cycles and is not pruned when the file no longer contains the function. This splits into two sub-mechanisms that the phantom set deliberately separates: **(a1) orphan in a surviving file** — SCAN re-scans the changed file and upserts present functions but leaves the removed function's chunk behind; **(a2) orphan from a deleted file** — SCAN walks only current files, never revisits a deleted file, so its chunks are never touched and no file-set reconciliation removes them. These require *different* fixes.
- **(b) Git-history scoring** — EXTRACT/SCORE derives volatility from commit history (`git_changes`) rather than current-scan chunks, so `find_intent_gaps()` surfaces a function whose identity comes from git history independent of any current chunk row.

**Discriminator:** for each phantom, does a current chunk row exist, and was it produced by the most recent SCAN? A phantom that surfaces with NO current chunk implicates (b). A phantom that surfaces with a stale chunk (row exists but not stamped by the current cycle) implicates (a) — and the rename case gives direct dual-chunk_id proof.

**This is a read-only diagnostic.** No source changes, no DB writes, no `run_cycle`, no cross-repo deposit. Do NOT author or propose the fix code — name the mechanism and the fix surface only.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file, executes Step 1 ONLY — a read-only investigation of `anvil/anvil.db` and the `find_intent_gaps()` / SCAN source — deposits findings, and stops.

**Bootstrap prompt:**
```
Read the plan at anvil/knowledge/decisions/diagnostic-intent-gap-phantom-mechanism-2026-06-03.md. Execute Step 1 ONLY. After completing Step 1, STOP and report. Do NOT modify any source code, do NOT run an audit cycle, do NOT modify the DB — this is a read-only diagnostic.
```

---
---

## STEP 1 — ANVIL SA

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this diagnostic and stating your immediate next action.** Do NOT rename the plan file — this is a manual_bootstrap dispatch, no watcher requires a rename.
>
> **You are the Anvil Systems Analyst.** Read your specialist file first for schema/scoring orientation. **Skip the domain glossary read — this is a schema-audit and code-trace task.** Working directory is `/Users/marklehn/Developer/GitHub/`. The DB is `anvil/anvil.db`; source is under `anvil/src/`. **Read-only:** no source edits, no DB writes, no `run_cycle`. All `git` commands use `git --no-pager`.
>
> **Goal:** name the mechanism that causes `find_intent_gaps()` to surface functions that no longer exist, discriminating between **(a1)** orphan chunk in a surviving file (SCAN upserts without pruning), **(a2)** orphan chunk from a deleted file (no file-set reconciliation), and **(b)** git-history-driven scoring that surfaces a function independent of any current chunk. These are not mutually exclusive — report per phantom, then in aggregate.
>
> **Phantoms to investigate** — five functions across three deliberately-chosen classes:
> - `rates_grid` — `web/rates.py` — **deleted file** (whole file removed in Phase 4 kill-dead-rate-routes). Tests (a2).
> - `import_contract_setup` — `web/gap_dashboard.py` — **renamed** to `_import_contract_setup_section` (file survives; old chunk_id reportedly persists alongside a new chunk_id for the renamed function). Tests (a1) with dual-chunk_id proof.
> - `record_response`, `_auto_route_after_response`, `confirm_carrier` — `web/action_queue.py` — **functions deleted** 2026-04-01 (commit `abaaa3f`, dead-code sweep; the file itself survives with other functions). Cycle-18 regression anchors. Test (a1).
>
> **(1) Bind the schema to real names.** Run `SELECT name FROM sqlite_master WHERE type='table'`. The BACKLOG uses informal names (`chunks`, `commits`, `volatility_scores`); the live schema is believed to be `code_chunks`, `git_changes`, `health_scores`, `cycle_reports` — confirm and bind to the actual names, do not assume. Run `PRAGMA table_info(<table>)` for the chunk table, the git-history table, the health/score table, and the cycle table. In the chunk table specifically, hunt for any scan/cycle-stamp or lifecycle column — e.g. `last_seen_cycle`, `deleted_at`, `scan_cycle`, `cycle_number`, `cycle_id`, `content_hash`, `updated_at`, `is_current`/active flag — and report exactly which exist (and which do NOT). From `cycle_reports`, report the most-recent `cycle_number` and its `cycle_date` (expected: cycle 19, dated 2026-06-03 UTC). Quote the column lists verbatim.
>
> **(2) Per-phantom chunk existence + freshness.** For each of the five phantoms, query the chunk table by name + file_path. Report: does a row exist; how many rows (the rename case may return two — old `import_contract_setup` and new `_import_contract_setup_section`); each `chunk_id`; and for each row the value of every scan/cycle-stamp column found in (1) — i.e. was the row produced/updated by cycle 19's SCAN, or carried over from an earlier cycle? If the chunk table has no cycle stamp at all, say so plainly — that absence is itself a key finding (it means chunk rows carry no scan provenance). Output a table: `Phantom | File | Class (deleted-file / renamed / deleted-func) | Row exists? | chunk_id(s) | Scan/cycle stamp value(s) | Produced by cycle-19 SCAN?`. Optionally confirm current non-existence with a read-only grep against the invoice-pulse working tree (e.g. `grep -rn "def rates_grid" invoice-pulse/web/` — Anvil is read-only on targets; do not modify anything).
>
> **(3) Trace `find_intent_gaps()`.** Grep `anvil/src/` for `find_intent_gaps` (likely `lab.py` or `detector.py`). Quote the full query/join. Answer precisely: (a) what is the FROM table, what is JOINed, on what keys, with what WHERE/HAVING; (b) does the finding's surfaced identity (the function name + file shown in the audit) come FROM the chunk table, or from `git_changes`/`health_scores` independent of a live chunk; (c) is there ANY predicate restricting results to current-scan chunks (a join to the latest cycle's scan set, a `last_seen_cycle = current` filter, an existence check against on-disk files) — or none. Draw the join graph in text.
>
> **(4) Trace SCAN orphan handling.** Grep `anvil/src/scanner.py` and `anvil/src/cycle.py` for the SCAN write path (content-hash change detection per the DEV brief). Answer: (a1) when a *surviving* file is re-scanned and a function was removed/renamed, does SCAN DELETE or flag the old chunk, or only upsert present functions (leaving orphans)? (a2) when a file is *deleted entirely*, does SCAN visit it at all, and is there any reconciliation that removes chunks for files no longer on disk? Quote the relevant lines. This is what distinguishes (a1) from (a2).
>
> **(5) Verdict — per-phantom truth table + mechanism + fix surface.** Produce a table: `Phantom | Class | Chunk exists & stale? | Surfaced via chunk or git-history? | Mechanism (a1 / a2 / b / combination)`. Then the aggregate answer in one paragraph: across the five, **is (a) true, is (b) true, both, or neither — and does the mechanism differ by phantom class?** For each named mechanism, state which candidate fix would actually catch it — **do not write the fix, just map mechanism → surface**: (a1) → either a current-scan/chunk-existence join in `find_intent_gaps()` OR prune-orphan-chunks-during-SCAN-of-surviving-files; (a2) → file-set reconciliation during SCAN (prune chunks for files no longer on disk) — note explicitly whether a prune-on-rescan fix alone would MISS (a2) since deleted files are never re-scanned; (b) → the chunk-existence join is the only thing that helps, pruning does not, because the identity isn't coming from chunks. Call out any phantom whose mechanism is a combination.
>
> **(6) Methodology notes.** What did the queries assume? Edge cases that could mislead (e.g. a function name reused across files; a chunk table keyed by content-hash so a rename produces a genuinely new row while the old row's hash lingers; commits touching a file but not the specific chunk). Be explicit about anything you could not determine from the DB + source alone.
>
> **Deposit findings to** `anvil/knowledge/research/intent-gap-phantom-mechanism-2026-06-03.md` using `Filesystem:write_file` or `with open()` (never heredoc). Lead with a one-paragraph **Executive Summary** stating, in plain terms, which mechanism(s) are confirmed and whether the answer is uniform across phantom classes. Then sections matching (1)–(6).
>
> Commit: `docs: diagnostic — intent-gap phantom-function mechanism`.
>
> Standard prompt feedback protocol — append any prompt issues to `anvil/knowledge/research/agent-prompt-feedback.md` before reporting Complete.
>
> **Deposits:**
> - `anvil/knowledge/research/intent-gap-phantom-mechanism-2026-06-03.md`
>
> **STOP. This is a single-step diagnostic. Report Complete and wait — do NOT move the plan to Done.**
