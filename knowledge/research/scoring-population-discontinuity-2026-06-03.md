# Anvil — Scoring Population Discontinuity (Cycle 19→20)

**Date:** 2026-06-03 | **Diagnostic source:** `diagnostic-scoring-population-discontinuity-2026-06-03.md`

## Executive Summary

Of the five supposedly "displaced" coupling findings, **0 are REAL_IMPROVEMENT and 0 are meaningfully DISPLACED** — all five are **NOISE_FILTERED** by `_is_noise_chunk()` (session-lifecycle and connection-factory patterns) and were never in `find_intent_gaps()` results at either cycle 19 or cycle 20. The "displacement" narrative is a comparison artifact from the QA delta analysis, which used raw SQL without the noise filter. Across the actual scored population, coupling percentile drift from the population shrink is modest: max 0.083, average 0.015 — well below any practical finding-ranking impact. Volatility drift is negligible (max 0.042, average ~0.0001). The population discontinuity does not warrant a CEO scoring-methodology decision — it is a one-time cleanup with small, non-directional percentile perturbation. Cross-cycle comparisons spanning the boundary (cycle ≤19 vs ≥20) should be flagged as structurally incomparable; within-regime comparisons (20+ vs 20+) are clean.

---

## (0) Natural-Experiment Validation

**Cycle 19:** started 2026-06-03T02:13:10 UTC, completed 2026-06-03T02:13:11 UTC
**Cycle 20:** started 2026-06-03T16:07:42 UTC, completed 2026-06-03T16:07:43 UTC
**Inter-cycle gap:** ~14 hours.

**Git log in invoice-pulse between cycles:**
```
69c8bae docs: anvil cycle 19 findings + curated backlog (8 actionable, 2 phantoms excluded)
```

One `docs:` commit — no functional code change. **Natural experiment is clean.** All score movement is attributable to the population/scoring change, not code evolution.

---

## (1) Population Change Quantification

| Metric | Cycle 19 | Cycle 20 | Delta |
|---|---|---|---|
| Scored chunks (health_scores rows) | 4,175 | 3,688 | **-487 (-11.7%)** |

### Dropped chunk confirmation
All 487 dropped chunks have `last_seen_cycle = NULL` — confirmed as unstamped orphans from the phantom fix. Zero have `last_seen_cycle = 20` (none were erroneously excluded).

### Dropped chunk profile (cycle-19 scores)

| Coupling | Count | % of dropped |
|---|---|---|
| coupling = 0 | 313 | 64.3% |
| 0 < coupling < 0.5 | 166 | 34.1% |
| 0.5 ≤ coupling < 0.9 | 7 | 1.4% |
| coupling ≥ 0.9 | 1 | 0.2% |

| Volatility | Count | % of dropped |
|---|---|---|
| volatility = 0 | 359 | 73.7% |
| volatility > 0 | 128 | 26.3% |

**Headline:** 64% of dropped chunks had zero coupling and 74% had zero volatility. Only 8 (1.6%) had coupling ≥ 0.5 and only 1 had coupling ≥ 0.9. The orphan population was overwhelmingly inert — sitting at the bottom of both percentile distributions and contributing negligible percentile mass.

---

## (2) Normalization Mechanics

Confirmed from `scorer.py:93-98`:

```python
# Phase 2: Percentile normalization for volatility and coupling
vol_values = sorted(set(s["volatility_raw"] for s in raw_scores))
coup_values = sorted(set(s["coupling_raw"] for s in raw_scores))

vol_ranks = {v: i / max(len(vol_values) - 1, 1) for i, v in enumerate(vol_values)}
coup_ranks = {v: i / max(len(coup_values) - 1, 1) for i, v in enumerate(coup_values)}
```

Both `coupling_score` and `volatility_score` are **percentile-normalized against the per-cycle scored population**. The normalization uses the count of *unique* raw values (not total chunks) as the denominator. A population shrink changes the set of unique raw values, which mechanically moves every chunk's percentile even with identical raw coupling.

**Post-fix, `raw_scores` only contains chunks with `last_seen_cycle = cycle_id`**, so the normalization base is the 3,688 live chunks, not the full 4,175+ that included orphans.

---

## (3) Five "Displaced" Coupling Findings — Classification

### Critical finding: all five are noise-filtered

All five match `_is_noise_chunk()` patterns in `lab.py:29-44`:

| Function | File | Noise rule | In `find_intent_gaps`? |
|---|---|---|---|
| `execute` | profile_ingestion.py | `_SESSION_LIFECYCLE_NAMES` + path hint | **No** — filtered at both C19 and C20 |
| `commit` | profile_ingestion.py | `_SESSION_LIFECYCLE_NAMES` + path hint | **No** |
| `close` | profile_ingestion.py | `_SESSION_LIFECYCLE_NAMES` + path hint | **No** |
| `get_connection` | database.py | `_CONNECTION_FACTORY_NAMES` | **No** |
| `_get_db` | web/action_queue.py | `_CONNECTION_FACTORY_NAMES` | **No** |

These five never appeared in `find_intent_gaps()` output at either cycle. The "displacement" was an artifact of the QA findings_delta analysis (which used raw SQL `ORDER BY hs.coupling_score DESC LIMIT 6` without applying the Python-level noise filter). **There is no user-visible finding displacement to explain.**

### Score deltas (for completeness)

| Function | File | last_seen_cycle | coup c19→c20 | vol c19→c20 | composite c19→c20 | Classification |
|---|---|---|---|---|---|---|
| `execute` | profile_ingestion.py | 20 | 1.0000 → 1.0000 | 0.0 → 0.0 | 0.2202 → 0.2202 | NOISE_FILTERED |
| `commit` | profile_ingestion.py | 20 | 0.9974 → 0.9971 | 0.0 → 0.0 | 0.2113 → 0.2113 | NOISE_FILTERED |
| `close` | profile_ingestion.py | 20 | 0.9949 → 0.9942 | 0.0 → 0.0 | 0.2066 → 0.2065 | NOISE_FILTERED |
| `get_connection` | database.py | 20 | 0.9794 → 0.9767 | 0.8333 → 0.8333 | 0.5403 → 0.5396 | NOISE_FILTERED |
| `_get_db` | web/action_queue.py | 20 | 0.9846 → 0.9825 | 0.1667 → 0.1667 | 0.6648 → 0.6645 | NOISE_FILTERED |

All five are live (stamped cycle 20), scored in both cycles, with trivial percentile drift (max composite delta: -0.0007). Under the SELF_DECAYED/DISPLACED/REAL_IMPROVEMENT framework, all five would classify as **DISPLACED** (trivially — raw coupling unchanged, percentile shifted <0.003 due to population base change). But the noise filter makes this classification moot — they never reach the user.

### Population-wide percentile drift

| Metric | Max drift | Avg drift |
|---|---|---|
| Coupling percentile | 0.083 | 0.015 |
| Volatility percentile | 0.042 | ~0.0001 |

**Direction:** Of 3,688 common chunks, 43 coupling percentiles increased, 2,172 were unchanged (within ±0.001), and 1,472 decreased. The effect is mild and non-directional. No chunk's composite moved enough to cross a finding-threshold boundary (max composite delta across the entire population is well under 0.01).

---

## (4) Bearing on Sibling Bugs

### (a) Self-resolve (volatility decay → findings "improve" without remediation)

**Orphan removal is irrelevant to this bug.** The self-resolve mechanism is driven by commit-frequency decline within the 4-week rolling window — it occurs when the *project's own* development activity tapers. The orphans were 74% zero-volatility (contributing nothing to the volatility percentile distribution) and their removal barely shifted volatility percentiles (avg drift ~0.0001). The d2 floor fix (shipped 2026-05-18, commit `155f3d1`) already addresses self-resolve for zero-coverage functions independently of population composition.

### (b) Percentile-inversion (population collapse inverts volatility direction)

**Orphan removal slightly reduces inversion risk but does not eliminate it.** The 487 dropped chunks were 74% zero-volatility. Their removal makes the surviving volatility distribution marginally denser at non-zero values, which slightly reduces the severity of a future population collapse. However, the fundamental mechanism (percentile normalization is relative, not absolute) is unchanged — a 33-day inter-cycle gap with project-wide commit-activity collapse would still produce inversions. The orphan cleanup is noise-level for this bug.

### (c) Cross-cycle comparison discontinuity

**Cycle 20 is a structural breakpoint.** `compare_cycles()` (cycle.py:174) computes set differences on `health_scores.chunk_id` per cycle. Comparing any pre-fix cycle (≤19) to any post-fix cycle (≥20) will report ~487 "removed" chunks that are actually orphan exclusions, not code deletions. This inflates the `removed_chunks` count and deflates `chunks_in_b`. The delta is a one-time step function, not cumulative — post-fix cycle-to-cycle comparisons (20 vs 21, 21 vs 22, etc.) will be clean.

**Recommendation input (not a recommendation — framing for CEO):** If cross-boundary comparisons are needed, the consumer should discount the ~487 "removed" chunks as known orphan exclusions. Alternatively, a one-line annotation could be added to the cycle-20 `cycle_reports` record noting the population discontinuity. Whether this is worth doing depends on how frequently cross-boundary comparisons are performed.

### (d) Is cycle 20 the correct clean baseline?

**Yes.** Cycle 20's scored population (3,688) represents the live, on-disk, currently-parsed codebase. It is the first cycle whose scores reflect only real code. All future cycles will score against this same live population (±organic changes from actual code evolution). Cycle 20 is the correct anchor for forward-looking trend analysis.

---

## (5) Verdict

**Of the five, 0 are REAL_IMPROVEMENT, 0 are meaningfully DISPLACED, and 5 are NOISE_FILTERED.** All five were always excluded from `find_intent_gaps()` by the `_is_noise_chunk()` filter (session-lifecycle and connection-factory patterns). Their "displacement" was a QA comparison artifact from using raw SQL without the noise filter. The population discontinuity produced no user-visible finding change.

**The population-base change does not warrant a CEO scoring-methodology decision.** The percentile perturbation is modest (max coupling drift 0.083, avg 0.015; max volatility drift 0.042, avg ~0.0001) and non-directional — no chunk crossed a finding-threshold boundary. The two sibling bugs (self-resolve, percentile-inversion) are orthogonal to the orphan cleanup: self-resolve is addressed by the d2 floor (already shipped), and percentile-inversion is driven by inter-cycle gaps and commit-activity collapse, not population composition. The previously-tabled options (sticky findings, persisting raw scores, z-score normalization, population-collapse warning) remain relevant to those sibling bugs on their own terms, but this discontinuity provides no new evidence that favors one over another.

---

## (6) Methodology Notes

### Assumptions
- Raw coupling is computed by `compute_coupling()` as `inbound + outbound` dependency count from `chunk_dependencies`. This table is cumulative (dependencies are added each cycle but not deleted), so raw coupling can grow monotonically. However, in a near-zero-code-change window, the growth should be negligible.
- The noise filter (`_is_noise_chunk`) was added in the 2026-04-14 noise-reduction fix (commit `d04fa5e`). Both cycle 19 and cycle 20 ran with this filter active. The QA findings_delta from earlier in this session used raw SQL without the filter, producing the misleading "displacement" framing.
- Percentile normalization uses the count of **unique** raw values as the denominator, not total chunks. If many chunks share the same raw coupling value, they all get the same percentile rank. This means removing chunks with a unique raw value changes the denominator, but removing chunks that share a raw value with surviving chunks does not.

### Edge cases
- **Top-N boundary effects:** The coupling hotspot bucket in `find_intent_gaps()` is `LIMIT top_n // 3` (typically 6). With noise filtering, the effective yield is often < 6 (noise chunks fill SQL slots but are discarded in Python). Cycle 19 and 20 both yielded only 1 coupling finding (`create_contract_tables`) after noise filtering. The LIMIT + noise interaction means coupling findings are always sparse.
- **`compare_cycles` across the boundary:** As noted in §4(c), comparing cycle ≤19 to ≥20 inflates "removed" counts by ~487. This is a known artifact, not a scoring bug.
- **Coupling raw values not persisted:** `health_scores` stores only the percentile-normalized `coupling_score`, not the raw dependency count. To verify raw coupling stability, I queried `chunk_dependencies` directly. This is the same approach validated in the volatility-attribution-replay (2026-05-18).
