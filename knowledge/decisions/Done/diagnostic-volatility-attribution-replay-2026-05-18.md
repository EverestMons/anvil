# Anvil — Diagnostic: Volatility Attribution Replay (F9-follow ambiguity removal)
**Date:** 2026-05-18 | **Tier:** Diagnostic | **Test Scope:** none (read-only) | **Execution:** Step 1 (ANVIL SA) | **Priority:** 1

**auto_close:** false

## Context

The F9 audit (`anvil/knowledge/research/scoring-weights-volatility-decay-audit-2026-05-18.md`) established a 0:9 displacement ratio: all 9 anchor-top-20 chunks that fell out of the cycle-17 top-20 dropped via volatility decay, zero via remediation. Section 9 of that audit, however, surfaced an attribution ambiguity that the F9 query design could not resolve: only percentile-normalized volatility is persisted in `health_scores`, so the audit could not distinguish:

- **(SELF_DECAYED)** — this function's underlying commit frequency genuinely dropped (fewer commits touched it in cycle-17's window than in cycle-10's window)
- **(DISPLACED)** — this function's underlying commit frequency was stable, but other functions gained commits, pushing this one down the percentile ranks
- **(BOTH)** — some of each

Without this disambiguation, the F9 option menu (d2 / c / a / etc.) is being chosen on incomplete evidence. If the dominant cause is SELF_DECAYED, the (d2) floor framing — "untested code can't be low-volatility no matter how stable" — is the right framing because the function genuinely became more stable. If the dominant cause is DISPLACED, the framing shifts: the function isn't actually more stable, it's just being out-shouted by code that got noisier. That argues differently for the fix design (DISPLACED dominance suggests percentile-normalization itself is the issue, not the weight).

This diagnostic resolves the ambiguity by replaying the scorer's volatility aggregation logic against `git_changes` directly, where `commit_date` IS stored. The output is per-chunk raw volatility at cycle 10 and cycle 17, plus a classification.

**This is a read-only diagnostic.** No code changes, no new audit cycle, no DB writes.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file, executes Step 1 ONLY — a read-only replay against `anvil/anvil.db` `git_changes` table mirroring the scorer's volatility aggregation — deposits findings, and stops.

**Bootstrap prompt:**
```
Read the plan at anvil/knowledge/decisions/diagnostic-volatility-attribution-replay-2026-05-18.md. Execute Step 1 ONLY. After completing Step 1, STOP and report. Do NOT modify any source code, do NOT run a new audit cycle, do NOT modify the DB — this is a read-only diagnostic.
```

---
---

## STEP 1 — ANVIL SA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/diagnostic-volatility-attribution-replay-2026-05-18.md", "anvil/knowledge/decisions/in-progress-diagnostic-volatility-attribution-replay-2026-05-18.md")`.
>
> Read your specialist file and domain glossary first. **You are the Anvil Systems Analyst.** Working directory is `/Users/marklehn/Developer/GitHub/`. **Context:** F9 produced a population characterization but left one attribution question open. This follow-up resolves it by reconstructing raw volatility values for the 20 anchor chunks at cycle 10 and cycle 17 directly from `git_changes`, where `commit_date` is stored. The goal is to mechanically attribute each anchor chunk's volatility drop to **SELF_DECAYED** (own commit frequency dropped) vs **DISPLACED** (own commit frequency stable, others rose) vs **BOTH**.
>
> **Critical context to internalize before writing queries:**
> - Read `anvil/src/scorer.py` lines 150-200 (or wherever the volatility aggregation lives — find it via grep) BEFORE writing replay queries. The replay must mirror the scorer's actual logic: same `GIT_HISTORY_WEEKS = 4` window, same per-chunk commit-count aggregation, same percentile-normalization step. If the scorer applies decay weights, exponential recency, or any other transform, the replay must apply the same. **Do not approximate.** If you cannot find the exact aggregation, report what you found and stop — do NOT guess.
> - Volatility is percentile-normalized per cycle in `scorer.py` (~lines 178-181 per F9 audit notes): `vol_ranks = {v: i / max(len(vol_values) - 1, 1) for i, v in enumerate(vol_values)}`. Raw volatility for the replay is whatever value is fed INTO that normalization step — typically a commit count or weighted commit-recency sum.
> - The `git_changes` table stores commit_date. Verify schema: `PRAGMA table_info(git_changes)`. Identify the column linking commits to chunks (likely `chunk_id` or a file_path lookup through `code_chunks`).
> - **The two cycles to replay:** cycle 10 (DB cycle_number 10, dated 2026-04-14 18:16) and cycle 17 (DB cycle_number 17, dated 2026-05-17 19:26). The 4-week window for cycle 10 is 2026-03-17 → 2026-04-14; for cycle 17 is 2026-04-19 → 2026-05-17.
> - **Population:** the same 20 anchor chunks from the F9 audit's section (2). Pull them by querying cycle 10's top-20 invoice-pulse zero-coverage chunks by composite score, identical to F9's anchor query.
>
> **Do exactly this:**
>
> **(1) Locate the scorer's volatility aggregation.** Grep `anvil/src/scorer.py` for the function or block that computes volatility from `git_changes`. Quote the relevant lines in the deposit. Identify: (a) what raw value is computed per chunk before normalization (commit count? recency-weighted sum?), (b) the window definition (rolling 4 weeks from cycle date), (c) any per-commit weighting (recency decay, author dedup, etc.). If the implementation differs from the F9 audit's assumption (simple commit count in a 4-week window), state the actual logic clearly. The replay must mirror this exactly.
>
> **(2) Verify the replay against cycle 17's persisted normalized values.** Before trusting the replay for cycle 10 (which we can't directly verify since F9 already characterized the displacement), run it for cycle 17 and confirm that the percentile-normalized output matches the `health_scores.volatility_score` values stored for those 20 chunks at cycle 17. If the replay output diverges from persisted values by more than rounding error on more than 2/20 chunks, stop and report the divergence — the replay logic is wrong and the rest of the diagnostic is invalid.
>
> **(3) Replay cycle 10 raw volatility.** For each of the 20 anchor chunks, compute raw volatility (using the cycle-10 4-week window: 2026-03-17 → 2026-04-14, or whatever exact window the scorer derives from `cycle_reports.cycle_date` for cycle 10). Report a table: `Chunk | File | Raw vol cycle 10 | Persisted normalized vol cycle 10 | Commit count in window`.
>
> **(4) Replay cycle 17 raw volatility.** Same as (3) but for the cycle-17 window. Report: `Chunk | File | Raw vol cycle 17 | Persisted normalized vol cycle 17 | Commit count in window`.
>
> **(5) Compute attribution per chunk.** For each of the 20 anchor chunks, compute:
> - `raw_delta` = raw_vol_cycle_17 - raw_vol_cycle_10 (negative = chunk became less active)
> - `commit_delta` = commits_in_cycle_17_window - commits_in_cycle_10_window
> - `normalized_delta` = persisted_normalized_cycle_17 - persisted_normalized_cycle_10
>
> Classify each chunk into one of:
> - **SELF_DECAYED** — raw_delta ≤ -0.5 * raw_vol_cycle_10 (own raw volatility dropped by at least 50% of its cycle-10 value) AND commit_delta < 0
> - **DISPLACED** — |raw_delta| < 0.2 * raw_vol_cycle_10 (own raw volatility roughly unchanged) AND normalized_delta ≤ -0.3 (but normalized rank still dropped substantially)
> - **BOTH** — raw_delta is meaningfully negative AND normalized_delta is more negative than raw_delta alone would explain
> - **OTHER** — describe in prose (e.g., raw volatility increased, indicating active editing)
>
> Report as a markdown table: `Chunk | File | Raw vol Δ | Commit Δ | Normalized vol Δ | Bucket`.
>
> **(6) Population-wide attribution.** Sum the buckets. Report:
> - Total chunks that displaced from cycle-17 top-20 (the 9 from F9, plus context for the 4 borderline OTHERs from F9's 7/20 OTHER classification)
> - For the 9 displaced chunks specifically: what is the SELF_DECAYED : DISPLACED : BOTH ratio?
> - For the full 20 anchor chunks: same ratio
>
> Headline question the audit must answer in one paragraph: **"Among the 9 anchor chunks displaced from cycle-17's top-20, was the dominant cause their own commit frequency dropping (SELF_DECAYED) or other chunks' commit frequencies rising (DISPLACED)?"**
>
> **(7) Implications for the F9 option menu.** In ONE paragraph per option, state how the attribution result reframes (or doesn't) each F9 option:
> - **(d2) Vol floor at 0.5 when coverage = 1.0:** does the attribution support the "untested code can't be low-volatility no matter how stable" framing, or does it reveal that the functions weren't actually more stable?
> - **(c) coverage × complexity secondary ranking:** is this option more or less attractive given the attribution result? (It is volatility-independent, so DISPLACED dominance would make it MORE attractive.)
> - **(a) Reduce volatility weight:** does the attribution change the calculus on weight reduction?
> - **(e) Time-aware momentum dampener:** does the attribution argue for or against this larger fix?
>
> Do NOT recommend an option. State how the attribution evidence reframes each.
>
> **(8) Methodology notes.** What did this replay assume? What edge cases might it miss? (E.g., commits that touched the file but not the specific chunk; renamed functions; deleted-then-restored files.) Be explicit about any approximations made.
>
> **Deposit findings to** `anvil/knowledge/research/volatility-attribution-replay-2026-05-18.md` using `Filesystem:write_file` or `with open()`. Structure with sections matching (1)-(8) plus a one-paragraph **Executive Summary** at the top stating the SELF_DECAYED : DISPLACED : BOTH ratio for the 9 displaced chunks and the headline reframing of the F9 option menu.
>
> Commit: `docs: diagnostic — volatility attribution replay (F9-follow)`.
>
> Standard prompt feedback protocol — append any prompt issues to `anvil/knowledge/research/agent-prompt-feedback.md` before reporting Complete.
>
> **Deposits:**
> - `anvil/knowledge/research/volatility-attribution-replay-2026-05-18.md`
