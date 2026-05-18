# Volatility Attribution Replay — F9-Follow Ambiguity Removal

**Date:** 2026-05-18 | **Agent:** Anvil Systems Analyst | **Type:** Diagnostic (read-only)

---

## Executive Summary

**SELF_DECAYED : DISPLACED : BOTH ratio for the 9 displaced chunks: 9 : 0 : 0.** For the full 20-chunk anchor population: 20 : 0 : 0.

The ambiguity is resolved unambiguously. Every single anchor chunk's volatility drop was caused by its own commit frequency declining — not by other functions gaining commits and pushing it down the percentile ranks. The dominant mechanism is not relative displacement but absolute silence: the 33-day gap between cycles 10 (2026-04-14) and 17 (2026-05-17) moved the 4-week rolling window past the April commit burst, causing most files to age out entirely. At cycle 10, 212/220 files (96%) had positive raw volatility. By cycle 17, only 38/225 files (17%) did. The population didn't get noisier; it went quiet.

**Headline reframing of the F9 option menu:** The SELF_DECAYED dominance strongly supports the (d2) floor framing. These functions genuinely became more stable (zero commits in the window), so the volatility score's decline is *mechanically correct* — but the scorer is answering the wrong question. Low volatility in a zero-coverage function is not evidence of low risk; it is evidence that the function is untested AND nobody is looking at it. Option (d2) — floor volatility at 0.5 when coverage = 1.0 — encodes precisely this insight. Option (c) remains complementary as a volatility-independent backup view. Option (e) — momentum dampener — is less motivated now that we know the raw drop is genuine, not a normalization artifact.

---

## (1) Scorer Volatility Aggregation Logic

**Source:** `src/scorer.py` lines 145-176 (`compute_volatility`)

```python
def compute_volatility(conn, project_id, file_path, git_window_weeks):
    cur = conn.execute(
        "SELECT commit_date FROM git_changes WHERE project_id = ? AND file_path = ?",
        (project_id, file_path),
    )
    rows = cur.fetchall()
    if not rows:
        return 0.5  # Neutral for unknown
    now = datetime.now(timezone.utc)
    window_days = git_window_weeks * 7  # 28
    total_weight = 0.0
    for (commit_date_str,) in rows:
        commit_date = datetime.fromisoformat(commit_date_str)
        if commit_date.tzinfo is None:
            commit_date = commit_date.replace(tzinfo=timezone.utc)
        days_ago = (now - commit_date).days
        weight = max(0.0, 1.0 - (days_ago / window_days))
        total_weight += weight
    return total_weight
```

**Key characteristics:**

| Property | Value |
|----------|-------|
| **Raw value per chunk** | Recency-weighted commit count for the chunk's *file* (not the chunk itself) |
| **Window** | `GIT_HISTORY_WEEKS = 4` → 28 days rolling from `datetime.now()` at runtime |
| **Per-commit weighting** | Linear decay: `weight = max(0, 1 - days_ago/28)`. A commit from today gets weight 1.0; from 14 days ago gets 0.5; from 28+ days ago gets 0.0 |
| **Author dedup** | None |
| **Granularity** | Per-file, not per-chunk. All chunks in the same file share the same raw volatility |
| **Normalization** | Percentile: `vol_ranks = {v: i / max(len(vol_values) - 1, 1) for i, v in enumerate(vol_values)}` across all scored chunks in the cycle (lines 87-90) |

**Critical design property:** The scorer uses `datetime.now()` at runtime, not the cycle's logical date. This means the raw volatility value is a function of *when the cycle physically runs*, not when it's "supposed to" run. The 33-day gap between cycles 10 and 17 means the 4-week window shifted by 33 days — longer than the window itself — so commits that were "recent" at cycle 10 were completely outside the window by cycle 17.

---

## (2) Cycle-17 Replay Verification

Replay mirrored the scorer's exact logic: same `git_changes` query, same linear-decay weighting, same percentile normalization across the full cycle-17 population. "Now" was set to cycle 17's `started_at` timestamp (2026-05-17T19:26:18+00:00).

| ID | Name | Raw Vol | Replay Norm | Persisted Norm | Delta | Status |
|----|------|---------|-------------|----------------|-------|--------|
| 3811 | carrier_import_accessorials | 0.0000 | 0.0000 | 0.0000 | 0.0000 | OK |
| 3812 | carrier_import_fuel | 0.0000 | 0.0000 | 0.0000 | 0.0000 | OK |
| 3929 | contract_fuel_import_combined | 0.7500 | 0.5556 | 0.5556 | 0.0000 | OK |
| 3881 | contracts_list | 0.7500 | 0.5556 | 0.5556 | 0.0000 | OK |
| 3770 | action_queue | 2.0000 | 1.0000 | 1.0000 | 0.0000 | OK |
| 3813 | carrier_import_minimums | 0.0000 | 0.0000 | 0.0000 | 0.0000 | OK |
| 1353 | import_activity_history | 0.0000 | 0.0000 | 0.0000 | 0.0000 | OK |
| 3777 | record_response | 2.0000 | 1.0000 | 1.0000 | 0.0000 | OK |
| 3920 | contract_lanes_bulk | 0.7500 | 0.5556 | 0.5556 | 0.0000 | OK |
| 4114 | rates_grid | 0.0000 | 0.0000 | 0.0000 | 0.0000 | OK |
| 970 | dispute_brief | 0.1071 | 0.1111 | 0.1111 | 0.0000 | OK |
| 1337 | write_extraction_quality_report | 0.0000 | 0.0000 | 0.0000 | 0.0000 | OK |
| 983 | team_dashboard | 0.1071 | 0.1111 | 0.1111 | 0.0000 | OK |
| 960 | invoice_detail | 0.1071 | 0.1111 | 0.1111 | 0.0000 | OK |
| 1388 | _run_ingestion_rows | 0.0000 | 0.0000 | 0.0000 | 0.0000 | OK |
| 3884 | contract_edit | 0.7500 | 0.5556 | 0.5556 | 0.0000 | OK |
| 3794 | _build_carrier_cards | 0.0000 | 0.0000 | 0.0000 | 0.0000 | OK |
| 3822 | _validate_contract_json | 0.0000 | 0.0000 | 0.0000 | 0.0000 | OK |
| 3928 | contract_fuel_brackets_bulk | 0.7500 | 0.5556 | 0.5556 | 0.0000 | OK |
| 3795 | carrier_profile_detail | 0.0000 | 0.0000 | 0.0000 | 0.0000 | OK |

**Result: 0/20 mismatches. Replay is validated for cycle 17.**

Cycle-10 replay was also run for reference: 17/20 matched within 0.01, with 3 chunks (action_queue, record_response, import_activity_history) diverging by 0.04-0.07. This divergence is explained by post-cycle-10 commits in `git_changes` that weren't present when cycle 10 actually ran but contribute nonzero weight in the retroactive replay. See Methodology Notes (section 8).

---

## (3) Cycle-10 Raw Volatility Replay

4-week window: ~2026-03-17 → 2026-04-14 (using `started_at` 2026-04-14T18:16:47+00:00).

| ID | Name | File | Raw Vol | Persisted Norm | Commits in Window |
|----|------|------|---------|----------------|-------------------|
| 3811 | carrier_import_accessorials | web/carrier_profiles.py | 13.4643 | 0.9326 | 28 |
| 3812 | carrier_import_fuel | web/carrier_profiles.py | 13.4643 | 0.9326 | 28 |
| 3929 | contract_fuel_import_combined | web/contracts.py | 33.5357 | 0.9775 | 69 |
| 3881 | contracts_list | web/contracts.py | 33.5357 | 0.9775 | 69 |
| 3770 | action_queue | web/action_queue.py | 9.3214 | 0.8315 | 13 |
| 3813 | carrier_import_minimums | web/carrier_profiles.py | 13.4643 | 0.9326 | 28 |
| 1353 | import_activity_history | ingestion/activity_import.py | 1.7857 | 0.6180 | 4 |
| 3777 | record_response | web/action_queue.py | 9.3214 | 0.8315 | 13 |
| 3920 | contract_lanes_bulk | web/contracts.py | 33.5357 | 0.9775 | 69 |
| 4114 | rates_grid | web/rates.py | 7.1071 | 0.8876 | 15 |
| 970 | dispute_brief | app.py | 43.1429 | 1.0000 | 88 |
| 1337 | write_extraction_quality_report | extraction_tracking.py | 7.4286 | 0.8989 | 15 |
| 983 | team_dashboard | app.py | 43.1429 | 1.0000 | 88 |
| 960 | invoice_detail | app.py | 43.1429 | 1.0000 | 88 |
| 1388 | _run_ingestion_rows | ingestion/ingest.py | 5.4286 | 0.8764 | 13 |
| 3884 | contract_edit | web/contracts.py | 33.5357 | 0.9775 | 69 |
| 3794 | _build_carrier_cards | web/carrier_profiles.py | 13.4643 | 0.9326 | 28 |
| 3822 | _validate_contract_json | web/contract_import.py | 2.5714 | 0.7303 | 6 |
| 3928 | contract_fuel_brackets_bulk | web/contracts.py | 33.5357 | 0.9775 | 69 |
| 3795 | carrier_profile_detail | web/carrier_profiles.py | 13.4643 | 0.9326 | 28 |

**Observation:** app.py was the most volatile file at cycle 10 (raw=43.14, 88 commits in window, normalized=1.0). web/contracts.py was second (raw=33.54, 69 commits). These files had intense development activity in late March / early April 2026.

---

## (4) Cycle-17 Raw Volatility Replay

4-week window: ~2026-04-19 → 2026-05-17 (using `started_at` 2026-05-17T19:26:18+00:00).

| ID | Name | File | Raw Vol | Persisted Norm | Commits in Window |
|----|------|------|---------|----------------|-------------------|
| 3811 | carrier_import_accessorials | web/carrier_profiles.py | 0.0000 | 0.0000 | 0 |
| 3812 | carrier_import_fuel | web/carrier_profiles.py | 0.0000 | 0.0000 | 0 |
| 3929 | contract_fuel_import_combined | web/contracts.py | 0.7500 | 0.5556 | 2 |
| 3881 | contracts_list | web/contracts.py | 0.7500 | 0.5556 | 2 |
| 3770 | action_queue | web/action_queue.py | 2.0000 | 1.0000 | 3 |
| 3813 | carrier_import_minimums | web/carrier_profiles.py | 0.0000 | 0.0000 | 0 |
| 1353 | import_activity_history | ingestion/activity_import.py | 0.0000 | 0.0000 | 0 |
| 3777 | record_response | web/action_queue.py | 2.0000 | 1.0000 | 3 |
| 3920 | contract_lanes_bulk | web/contracts.py | 0.7500 | 0.5556 | 2 |
| 4114 | rates_grid | web/rates.py | 0.0000 | 0.0000 | 0 |
| 970 | dispute_brief | app.py | 0.1071 | 0.1111 | 1 |
| 1337 | write_extraction_quality_report | extraction_tracking.py | 0.0000 | 0.0000 | 0 |
| 983 | team_dashboard | app.py | 0.1071 | 0.1111 | 1 |
| 960 | invoice_detail | app.py | 0.1071 | 0.1111 | 1 |
| 1388 | _run_ingestion_rows | ingestion/ingest.py | 0.0000 | 0.0000 | 0 |
| 3884 | contract_edit | web/contracts.py | 0.7500 | 0.5556 | 2 |
| 3794 | _build_carrier_cards | web/carrier_profiles.py | 0.0000 | 0.0000 | 0 |
| 3822 | _validate_contract_json | web/contract_import.py | 0.0000 | 0.0000 | 0 |
| 3928 | contract_fuel_brackets_bulk | web/contracts.py | 0.7500 | 0.5556 | 2 |
| 3795 | carrier_profile_detail | web/carrier_profiles.py | 0.0000 | 0.0000 | 0 |

**Observation:** The collapse is extreme. Files that had 13-88 commits in the cycle-10 window now have 0-3 commits in the cycle-17 window. 12/20 anchor chunks have zero commits in the cycle-17 window; the remaining 8 have 1-3. The development burst that drove the high volatility at cycle 10 was concentrated in March-April 2026 and did not continue into May.

---

## (5) Attribution Per Chunk

| ID | Name | File | Raw Δ | Commit Δ | Norm Δ | Bucket |
|----|------|------|-------|----------|--------|--------|
| 3811 | carrier_import_accessorials | web/carrier_profiles.py | -13.4643 (-100%) | -28 | -0.9326 | **SELF_DECAYED** |
| 3812 | carrier_import_fuel | web/carrier_profiles.py | -13.4643 (-100%) | -28 | -0.9326 | **SELF_DECAYED** |
| 3929 | contract_fuel_import_combined | web/contracts.py | -32.7857 (-98%) | -67 | -0.4219 | **SELF_DECAYED** |
| 3881 | contracts_list | web/contracts.py | -32.7857 (-98%) | -67 | -0.4219 | **SELF_DECAYED** |
| 3770 | action_queue | web/action_queue.py | -7.3214 (-79%) | -10 | +0.1685 | **SELF_DECAYED** |
| 3813 | carrier_import_minimums | web/carrier_profiles.py | -13.4643 (-100%) | -28 | -0.9326 | **SELF_DECAYED** |
| 1353 | import_activity_history | ingestion/activity_import.py | -1.7857 (-100%) | -4 | -0.6180 | **SELF_DECAYED** |
| 3777 | record_response | web/action_queue.py | -7.3214 (-79%) | -10 | +0.1685 | **SELF_DECAYED** |
| 3920 | contract_lanes_bulk | web/contracts.py | -32.7857 (-98%) | -67 | -0.4219 | **SELF_DECAYED** |
| 4114 | rates_grid | web/rates.py | -7.1071 (-100%) | -15 | -0.8876 | **SELF_DECAYED** |
| 970 | dispute_brief | app.py | -43.0357 (-100%) | -87 | -0.8889 | **SELF_DECAYED** |
| 1337 | write_extraction_quality_report | extraction_tracking.py | -7.4286 (-100%) | -15 | -0.8989 | **SELF_DECAYED** |
| 983 | team_dashboard | app.py | -43.0357 (-100%) | -87 | -0.8889 | **SELF_DECAYED** |
| 960 | invoice_detail | app.py | -43.0357 (-100%) | -87 | -0.8889 | **SELF_DECAYED** |
| 1388 | _run_ingestion_rows | ingestion/ingest.py | -5.4286 (-100%) | -13 | -0.8764 | **SELF_DECAYED** |
| 3884 | contract_edit | web/contracts.py | -32.7857 (-98%) | -67 | -0.4219 | **SELF_DECAYED** |
| 3794 | _build_carrier_cards | web/carrier_profiles.py | -13.4643 (-100%) | -28 | -0.9326 | **SELF_DECAYED** |
| 3822 | _validate_contract_json | web/contract_import.py | -2.5714 (-100%) | -6 | -0.7303 | **SELF_DECAYED** |
| 3928 | contract_fuel_brackets_bulk | web/contracts.py | -32.7857 (-98%) | -67 | -0.4219 | **SELF_DECAYED** |
| 3795 | carrier_profile_detail | web/carrier_profiles.py | -13.4643 (-100%) | -28 | -0.9326 | **SELF_DECAYED** |

**Notable case — action_queue / record_response (web/action_queue.py):** Raw vol dropped 79% (9.32 → 2.00, commits 13 → 3), yet normalized vol *increased* from 0.83 → 1.00. Why? Because the entire population collapsed even harder. action_queue retained 3 commits in the cycle-17 window, making it the *most* volatile file relative to the population. This is pure SELF_DECAYED at the raw level, masked by normalization. It confirms that normalization can *hide* the underlying signal direction — the file is objectively less active but looks maximally volatile.

---

## (6) Population-Wide Attribution

### Bucket Summary

| Bucket | 9 Displaced | Full 20 Anchor |
|--------|-------------|----------------|
| **SELF_DECAYED** | **9** (100%) | **20** (100%) |
| DISPLACED | 0 (0%) | 0 (0%) |
| BOTH | 0 (0%) | 0 (0%) |
| OTHER | 0 (0%) | 0 (0%) |

### SELF_DECAYED : DISPLACED : BOTH ratio

- **9 displaced chunks:** 9 : 0 : 0
- **Full 20 anchor chunks:** 20 : 0 : 0

### Population distribution collapse

| Metric | Cycle 10 | Cycle 17 |
|--------|----------|----------|
| Total unique files scored | 220 | 225 |
| Files with positive raw volatility | 212 (96%) | 38 (17%) |
| Files with zero raw volatility | 8 (4%) | 187 (83%) |

The population-level collapse is the key context. At cycle 10, almost every file had recent commits (96% nonzero). By cycle 17, 83% of files had *zero* commits in the 4-week window. The development pace for invoice-pulse dropped dramatically between the April burst and mid-May. This is why all 20 anchor chunks are SELF_DECAYED and none are DISPLACED: there was no population of "noisy newcomers" pushing the anchors down — the entire codebase went quiet.

### The F9 "7 OTHER" reclassification

The F9 audit classified 7 chunks as OTHER using a normalized vol delta threshold of 0.5. With raw data, all 7 are unambiguously SELF_DECAYED:

- **5 partial-decay (contracts.py):** Raw vol dropped 98% (33.54 → 0.75), commits 69 → 2. The normalized drop was only 0.42 because the 2 remaining commits kept them above the population median.
- **2 volatility-increased (action_queue, record_response):** Raw vol dropped 79% (9.32 → 2.00), commits 13 → 3. Normalized vol *increased* because they retained more commits than 83% of the population. The F9 classification was correct by normalized metrics but misleading at the raw level.

---

## (7) Implications for the F9 Option Menu

### (d2) Vol floor at 0.5 when coverage = 1.0

The SELF_DECAYED dominance *strongly supports* this option's framing. The 20 anchor functions genuinely became more stable — their commit frequency dropped 79-100%. The volatility score's decline is mechanically correct: these files really are less active. The problem is that the scorer treats "less active + untested" the same as "less active + well-tested." A floor of 0.5 when coverage = 1.0 encodes the insight that stability in untested code is not evidence of safety — it's evidence of neglect. The attribution data adds precision to the argument: these functions went from 4-88 commits in the window to 0-3, which means the "stability" is absolute silence, not marginal calming. The floor framing is appropriate because the risk hasn't changed (zero test coverage, high complexity), only the activity signal has changed.

### (c) coverage × complexity secondary ranking

This option is *unchanged in attractiveness* by the attribution result. Option (c) is volatility-independent by design, so whether the cause was SELF_DECAYED or DISPLACED was always irrelevant to its effectiveness. What the attribution *does* confirm is that option (c) provides a valuable orthogonal view: the scorer's primary ranking is dominated by a signal (volatility) that can collapse to near-zero for the entire population. A secondary ranking that ignores volatility entirely provides resilience against this collapse. If anything, the fact that the collapse was SELF_DECAYED (real) rather than DISPLACED (artifactual) makes option (c) slightly more important, because the primary ranking is now reflecting a genuinely changed state of the codebase, not a normalization anomaly.

### (a) Reduce volatility weight

The SELF_DECAYED finding *slightly weakens* the argument for weight reduction. When the F9 audit couldn't distinguish SELF_DECAYED from DISPLACED, weight reduction had a plausible rationale: "if normalization artifacts are distorting the signal, reduce the signal's influence." Now that we know the raw signal genuinely collapsed, reducing its weight is a blunter instrument: the scorer is correctly detecting that these files are less active, and the weight reduction just makes it care less about correctness. The floor approach (d2) is more surgical because it preserves volatility's full signal range for functions that DO have test coverage while capping the floor for functions that don't. That said, if (d2) is adopted, the weight reduction argument is moot for zero-coverage functions and remains viable as a general tuning parameter.

### (e) Time-aware momentum dampener

The SELF_DECAYED attribution *argues against* the complexity of this option. A momentum dampener (`max(current_percentile, 0.5 * previous_cycle_percentile)`) prevents single-cycle collapses. This made sense under a DISPLACED hypothesis — if the drop was a normalization artifact, dampening would preserve the "true" signal. But under SELF_DECAYED, the drop IS the true signal: commit frequency genuinely went from 88 to 1. A dampener would artificially delay the scorer's recognition of this genuine state change. The underlying problem isn't that volatility moved too fast — it's that the scorer doesn't account for coverage when interpreting what a volatility drop means. A momentum dampener adds implementation complexity (storing previous-cycle scores, a new comparison step) to solve the wrong problem.

---

## (8) Methodology Notes

### Replay assumptions

1. **"Now" approximation.** The scorer uses `datetime.now(timezone.utc)` at runtime; the replay uses `cycle_reports.started_at` for each cycle. These are effectively identical for cycle 17 (0/20 mismatches). For cycle 10, 3/20 chunks diverged by 0.04-0.07 in normalized score. The divergence is attributed to post-cycle-10 commits in `git_changes` that didn't exist when cycle 10 ran but do exist now and contribute nonzero weight in the retroactive replay (commits after 2026-04-14 but before 2026-04-14 + 28 days = 2026-05-12 would get positive weight under cycle 10's "now").

2. **File-level granularity.** The scorer computes volatility per *file*, not per chunk. All chunks in the same file share the same raw volatility. This means the replay attributes at file granularity. A commit that touched `app.py` increments volatility for `dispute_brief`, `team_dashboard`, AND `invoice_detail` equally, even if the commit only modified one of those functions. This is a property of the scorer's actual logic, not an approximation.

3. **Linear decay weighting.** The raw volatility value is not a simple commit count. Each commit is weighted by `max(0, 1 - days_ago/28)`: a commit from today has weight 1.0, a commit from 14 days ago has weight 0.5, and a commit from 28+ days ago has weight 0.0. The "Commits in Window" column counts commits with nonzero weight, but the raw value reflects the sum of *weighted* contributions.

### Edge cases this replay does NOT address

1. **Chunk-level commit attribution.** A commit to `app.py` that only touches `dispute_brief`'s lines would also inflate volatility for `team_dashboard` and `invoice_detail`. The scorer does not differentiate. The raw volatility values in this report reflect file-level activity, not function-level activity.

2. **Renamed or deleted functions.** If a function was renamed between cycles, the chunk_id may have changed. The replay tracks by chunk_id as persisted in `health_scores`, which should be stable across cycles unless the chunk was deleted and recreated.

3. **git_changes population drift.** Later SCAN phases may have added commit records to `git_changes` that weren't present when earlier cycles ran. This explains the minor cycle-10 replay divergence. For cycle 17 (the most recent cycle), this drift is negligible.

4. **Commits outside the git window.** Commits older than 28 days contribute zero weight and are invisible to the scorer. A function with 500 commits all older than 28 days has the same raw volatility as a function with zero commits: 0.0. The scorer's rolling window treats all historical activity as irrelevant.

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** Step 1 (single-step diagnostic)
**Status:** Complete

### What Was Done
Replayed the scorer's volatility aggregation logic against `git_changes` directly for cycles 10 and 17, computing raw (pre-normalization) volatility for all 20 anchor chunks. Verified the replay against cycle-17 persisted values (0/20 mismatches). Classified all 20 chunks into SELF_DECAYED / DISPLACED / BOTH / OTHER attribution buckets. Analyzed population-level distribution collapse and reframed each F9 option based on the attribution evidence.

### Files Deposited
- `knowledge/research/volatility-attribution-replay-2026-05-18.md` — full replay findings with 8 sections plus executive summary

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- Used `cycle_reports.started_at` as the "now" proxy for each cycle's volatility computation
- Retained all 20 chunks as SELF_DECAYED classification despite 2 chunks (action_queue, record_response) having normalized vol increase — the raw vol drop (79%) is unambiguous at the raw level
- Did not apply the diagnostic's DISPLACED/BOTH thresholds because they were unnecessary: all 20 chunks had raw delta ≥ -79% with commit delta negative, clearly exceeding the SELF_DECAYED threshold

### Flags for CEO
- **Attribution is definitive: 9:0:0 SELF_DECAYED for the 9 displaced chunks, 20:0:0 for the full anchor population.** The ambiguity raised in F9 § 9 is resolved. There is no displacement effect — the entire population went quiet.
- **The population collapse (212 → 38 files with positive raw vol) suggests a broader issue:** the scorer is highly sensitive to development pace. During active sprints, everything looks volatile; during quiet periods, everything looks stable. The (d2) floor approach addresses this specifically for zero-coverage functions.
- **Scoring weight changes remain gated to CEO authority** per the SA's decision matrix.

### Flags for Next Step
- None (diagnostic complete, no follow-on execution step)
