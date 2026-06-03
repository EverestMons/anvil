# Anvil — Diagnostic: Scoring Population Discontinuity (cycle 19→20)
**Date:** 2026-06-03 | **Tier:** Diagnostic | **Dispatch Mode:** manual_bootstrap | **Test Scope:** none (read-only) | **Execution:** Step 1 (ANVIL SA) | **Priority:** Medium

**auto_close:** false

## Context

The intent-gap phantom fix (`last_seen_cycle`, commit `2421f83`) scoped the scorer to current-snapshot chunks. Side effect: the invoice-pulse scored population dropped from ~5,700+ (cycle 19) to 3,688 (cycle 20), because the scorer now excludes ~2,000 unstamped orphan chunks (deleted/rebuilt files) that were previously in the percentile base. Five legitimate cycle-19 **coupling** findings displaced from cycle 20: `execute`, `commit`, `close` (`web/profile_ingestion.py`), `_get_db` (`web/action_queue.py`), `get_connection` (`web/database.py`). QA accepted these as threshold/ordering shifts but did not characterize them.

This diagnostic answers: **are those five genuinely lower-risk now, or merely displaced by percentile renormalization on the smaller population?** — the SELF_DECAYED-vs-DISPLACED question, here driven by a one-time population change rather than commit-frequency drift. It also assesses how the orphan-cleaned population bears on the two open sibling scoring bugs (self-resolve, percentile-inversion).

The cycle 19→20 interval is a near-zero-code-change window (cycle 20 was the QA validation run hours after cycle 19), so score movement is attributable to the population/scoring change, not real code evolution — a clean natural experiment. **This is read-only and characterization-only: no code changes, no DB writes, no `run_cycle`, and do NOT author or recommend a scoring fix — frame findings as input to a future CEO scoring-methodology decision.**

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file, executes Step 1 ONLY — read-only analysis of `anvil/anvil.db` (cycle 19 vs 20 health_scores), `scorer.py`, and the prior 2026-05-18 scoring research — deposits findings, and stops.

**Bootstrap prompt:**
```
Read the plan at anvil/knowledge/decisions/diagnostic-scoring-population-discontinuity-2026-06-03.md. Execute Step 1 ONLY. After completing Step 1, STOP and report. Do NOT modify any source code, do NOT run a cycle, do NOT modify the DB — this is a read-only characterization diagnostic.
```

---
---

## STEP 1 — ANVIL SA

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this diagnostic and your immediate next action.** Do NOT rename the plan file — manual_bootstrap dispatch.
>
> **You are the Anvil Systems Analyst.** Read your specialist file first for scoring orientation; skip the domain glossary. Also read these priors before analysis: `knowledge/research/volatility-attribution-replay-2026-05-18.md` (reuse its SELF_DECAYED/DISPLACED replay methodology), `knowledge/research/scoring-weights-volatility-decay-audit-2026-05-18.md`, `knowledge/research/cycle-18-comparison-memo-2026-05-18.md`, and the two open BACKLOG sibling entries ("Volatility-weighted composite scores cause findings to 'self-resolve'" and "Percentile normalization can invert volatility direction"). Working directory `/Users/marklehn/Developer/GitHub/`; DB `anvil/anvil.db`; source `anvil/src/`. **Read-only:** no source edits, no DB writes, no `run_cycle`. `git --no-pager` on every git call. **Characterization only — do NOT design or recommend a fix.**
>
> **(0) Validate the natural-experiment assumption.** Get cycle 19 and cycle 20 `started_at` from `cycle_reports`. Run `git --no-pager log --oneline --since=<c19> --until=<c20>` in `invoice-pulse/` and confirm the interval has no meaningful functional change (a few non-functional commits are fine). If there WAS substantive code change, flag it loudly — it confounds everything downstream — and proceed with that caveat stated.
>
> **(1) Quantify the population change.** Counts of scored chunks (rows in `health_scores`) for cycle_id=19 vs cycle_id=20, invoice-pulse. Of the chunks that were scored at 19 but NOT at 20, confirm they are now-unstamped orphans (`code_chunks.last_seen_cycle` NULL or <20). Break down the dropped set: how many had non-zero `coupling_score` and non-zero `volatility_score` at cycle 19 — i.e. how many were actually contributing to the active percentile base vs sitting at zero? This tells you whether the ~2,000 orphans materially shifted the percentile distribution or were mostly inert.
>
> **(2) Establish the normalization mechanics.** From `scorer.py`, confirm whether `coupling_score` (and `volatility_score`) are percentile-normalized against the per-cycle scored population. Quote the relevant lines. If coupling is percentile-relative, a population shrink mechanically moves every chunk's coupling percentile even with identical raw coupling — establish this precisely (it is the mechanism under test).
>
> **(3) Classify the five displaced coupling findings.** For `execute`, `commit`, `close` (profile_ingestion.py), `_get_db` (action_queue.py), `get_connection` (database.py): first confirm each is still live (stamped `last_seen_cycle=20`) — their displacement should be from ranking, not exclusion. Pull cycle-19 and cycle-20 `health_scores` (coupling, composite, volatility, coverage, complexity). Compute raw (pre-normalization) coupling at both cycles — if raw isn't persisted, replay it from source mirroring the volatility-attribution-replay approach. Classify each:
> - **REAL_IMPROVEMENT** — raw coupling genuinely dropped (or coverage rose);
> - **DISPLACED** — raw coupling ~unchanged, percentile fell only because the population shrank;
> - **OTHER** — describe (e.g. threshold-boundary, dropped below top-N by a competitor rising).
> Report a table: `Function | File | last_seen_cycle | Raw coupling c19 | Raw coupling c20 | Coupling pctile c19→c20 | Composite c19→c20 | Bucket`.
>
> **(4) Bearing on the sibling bugs.** Given the orphan-cleaned population, assess each open sibling entry: (a) **self-resolve** — does removing ~2,000 inert orphans change how zero-coverage findings decay, or was orphan pollution irrelevant to it? (b) **percentile-inversion** — was orphan pollution part of the population-collapse mechanism, and does the clean population reduce inversion risk? Also: is cycle 20 the correct clean baseline going forward, and does the cycle-20 discontinuity make cross-cycle comparisons (`compare_cycles`, any cycle-N-vs-19 delta) unreliable across the boundary? State findings; do NOT design the fix.
>
> **(5) Verdict.** One paragraph: of the five, how many are REAL vs DISPLACED (with counts). Then one paragraph stating whether the population-base change warrants a CEO scoring-methodology decision and which previously-tabled options the evidence now favors (e.g. the (d2) coverage-floor, persisting raw/absolute scores, z-score normalization, sticky findings) — framed strictly as decision input, NOT a recommendation.
>
> **(6) Methodology notes.** Assumptions, replay approximations, edge cases (e.g. coupling raw not persisted; chunks at exactly the top-N boundary; whether `compare_cycles` already filters by cycle).
>
> **Deposit findings to** `anvil/knowledge/research/scoring-population-discontinuity-2026-06-03.md` (`Filesystem:write_file` or `with open()`, never heredoc). Lead with a one-paragraph **Executive Summary** giving the REAL:DISPLACED count for the five and the headline on whether a scoring-methodology decision is warranted. Sections (0)–(6).
>
> Commit: `docs: diagnostic — scoring population discontinuity (cycle 19→20)`.
>
> Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md` before reporting Complete.
>
> **Deposits:**
> - `anvil/knowledge/research/scoring-population-discontinuity-2026-06-03.md`
>
> **STOP. This is a single-step diagnostic. Report Complete and wait — do NOT move the plan to Done.**
