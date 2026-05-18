# Scoring Weights & Volatility-Decay Population Audit

**Date:** 2026-05-18 | **Agent:** Anvil Systems Analyst | **Type:** Diagnostic (read-only)

---

## Executive Summary

**Headline ratio: 0 real remediation : 9 volatility-decayed** among the 9 anchor-top-20 chunks that fell out of the cycle-17 top-20. Zero findings were displaced by genuine test coverage gains or complexity reduction. Every single displacement was caused by volatility score decay while coverage and complexity remained unchanged. Across the full anchor population of 20 chunks, 13 (65%) are classified VOLATILITY-DECAYED, 7 (35%) are OTHER (mostly partial volatility decay below the 0.5 threshold or slight volatility increase), and 0 (0%) show any form of remediation. The problem is systemic, not limited to the two BACKLOG-cited functions.

Of the four BACKLOG options, **option (d) — conditional volatility decay with a floor of 0.5 when coverage_score = 1.0** produces the strongest anchor-chunk retention (13/20) while preserving volatility's signal for functions that have test coverage. Option (c) — secondary ranking by `coverage * complexity` — is the only option that places `dispute_brief` in the top-20 (rank 17) and is the cheapest to implement. These two options are complementary, not mutually exclusive. The CEO should evaluate whether to adopt one or both.

---

## (1) Cycle Range

Full `cycle_reports` table:

| Cycle | Date | Project |
|-------|------|---------|
| 1 | 2026-03-30 | invoice-pulse |
| 2 | 2026-04-01 | invoice-pulse |
| 3 | 2026-04-01 | invoice-pulse |
| 4 | 2026-04-01 | invoice-pulse |
| 5 | 2026-04-01 | invoice-pulse |
| 6 | 2026-04-03 | invoice-pulse |
| 7 | 2026-04-03 | invoice-pulse |
| 8 | 2026-04-04 | invoice-pulse |
| 9 | 2026-04-14 18:08 | invoice-pulse |
| 10 | 2026-04-14 18:16 | invoice-pulse |
| 11 | 2026-04-14 18:42 | invoice-pulse |
| 12 | 2026-04-14 18:47 | invoice-pulse |
| 13 | 2026-04-14 19:37 | invoice-pulse |
| 14 | 2026-04-14 19:43 | invoice-pulse |
| 15 | 2026-04-14 19:45 | invoice-pulse |
| 16 | 2026-04-14 19:46 | invoice-pulse |
| 17 | 2026-05-17 19:26 | invoice-pulse |

**Anchor cycle:** DB cycle 10 (2026-04-14 18:16 — second run on the Phase 2.1 production date, first with stable 3,836 health_scores; cycle 9 had 7,672 scores suggesting a double-count or schema anomaly).

**Most recent cycle:** DB cycle 17 (2026-05-17 19:26 — the cycle-13 plan run, 3,956 health_scores).

**Audit window:** Cycles 10 through 17.

---

## (2) Anchor Population — Top-20 Zero-Coverage at Cycle 10

| Rank | ID | Name | File | Role | Vol | Cov | Comp | Coup | Stale | Composite |
|------|----|------|------|------|-----|-----|------|------|-------|-----------|
| 1 | 3811 | carrier_import_accessorials | web/carrier_profiles.py | route_handler | 0.933 | 1.000 | 0.983 | 0.716 | 0.333 | 0.873 |
| 2 | 3812 | carrier_import_fuel | web/carrier_profiles.py | route_handler | 0.933 | 1.000 | 0.990 | 0.762 | 0.167 | 0.865 |
| 3 | 3929 | contract_fuel_import_combined | web/contracts.py | route_handler | 0.978 | 1.000 | 0.999 | 0.774 | 0.000 | 0.861 |
| 4 | 3881 | contracts_list | web/contracts.py | route_handler | 0.978 | 1.000 | 0.995 | 0.626 | 0.200 | 0.858 |
| 5 | 3770 | action_queue | web/action_queue.py | route_handler | 0.832 | 1.000 | 0.996 | 0.756 | 0.167 | 0.845 |
| 6 | 3813 | carrier_import_minimums | web/carrier_profiles.py | route_handler | 0.933 | 1.000 | 0.937 | 0.649 | 0.200 | 0.838 |
| 7 | 1353 | import_activity_history | ingestion/activity_import.py | utility | 0.618 | 1.000 | 0.998 | 0.919 | 0.500 | 0.836 |
| 8 | 3777 | record_response | web/action_queue.py | route_handler | 0.832 | 1.000 | 0.941 | 0.522 | 0.400 | 0.820 |
| 9 | 3920 | contract_lanes_bulk | web/contracts.py | route_handler | 0.978 | 1.000 | 0.921 | 0.620 | 0.000 | 0.819 |
| 10 | 4114 | rates_grid | web/rates.py | route_handler | 0.888 | 1.000 | 1.000 | 0.562 | 0.000 | 0.812 |
| 11 | 970 | dispute_brief | app.py | utility | 1.000 | 1.000 | 0.989 | 0.725 | 0.000 | 0.805 |
| 12 | 1337 | write_extraction_quality_report | extraction_tracking.py | utility | 0.899 | 1.000 | 0.981 | 0.867 | 0.000 | 0.804 |
| 13 | 983 | team_dashboard | app.py | utility | 1.000 | 1.000 | 0.998 | 0.675 | 0.000 | 0.801 |
| 14 | 960 | invoice_detail | app.py | utility | 1.000 | 1.000 | 1.000 | 0.603 | 0.000 | 0.790 |
| 15 | 1388 | _run_ingestion_rows | ingestion/ingest.py | ingestion_orchestrator | 0.876 | 1.000 | 0.935 | 0.739 | 0.200 | 0.790 |
| 16 | 3884 | contract_edit | web/contracts.py | route_handler | 0.978 | 1.000 | 0.774 | 0.664 | 0.000 | 0.788 |
| 17 | 3794 | _build_carrier_cards | web/carrier_profiles.py | route_handler | 0.933 | 1.000 | 0.826 | 0.617 | 0.000 | 0.786 |
| 18 | 3822 | _validate_contract_json | web/contract_import.py | route_handler | 0.730 | 1.000 | 1.000 | 0.586 | 0.000 | 0.784 |
| 19 | 3928 | contract_fuel_brackets_bulk | web/contracts.py | route_handler | 0.978 | 1.000 | 0.758 | 0.620 | 0.000 | 0.778 |
| 20 | 3795 | carrier_profile_detail | web/carrier_profiles.py | route_handler | 0.933 | 1.000 | 0.717 | 0.728 | 0.000 | 0.775 |

**Note:** `run_validation` (id=971, app.py, utility) was rank 21+ at cycle 10 with composite 0.773. It is not in the anchor top-20 but is tracked for BACKLOG context below.

---

## (3) Population Trajectories (Cycles 10-17)

### Chunks with volatility collapse (Vol ≥ 0.6 at anchor → ≤ 0.12 at cycle 17)

**dispute_brief (id=970):** Vol 1.000 → 1.000 → 1.000 → 1.000 → 1.000 → 1.000 → 1.000 → **0.111**. Cov and comp flat at 1.000/0.989 throughout. Composite dropped 0.805 → 0.630 solely via volatility.

**team_dashboard (id=983):** Vol 1.000 → constant → **0.111**. Cov 1.000, comp 0.998 flat. Composite 0.801 → 0.626.

**invoice_detail (id=960):** Vol 1.000 → constant → **0.111**. Cov 1.000, comp 1.000 flat. Composite 0.790 → 0.658.

**carrier_import_accessorials (id=3811):** Vol 0.933 → stable → **0.000**. Composite 0.873 → 0.706.

**carrier_import_fuel (id=3812):** Vol 0.933 → stable → **0.000**. Composite 0.865 → 0.698.

**carrier_import_minimums (id=3813):** Vol 0.933 → stable → **0.000**. Composite 0.838 → 0.676.

**_build_carrier_cards (id=3794):** Vol 0.933 → stable → **0.000**. Composite 0.786 → 0.602.

**carrier_profile_detail (id=3795):** Vol 0.933 → stable → **0.000**. Composite 0.775 → 0.617.

**rates_grid (id=4114):** Vol 0.888 → stable → **0.000**. Composite 0.812 → 0.650.

**write_extraction_quality_report (id=1337):** Vol 0.899 → stable → **0.000**. Composite 0.804 → 0.626.

**_run_ingestion_rows (id=1388):** Vol 0.876 → stable → **0.000**. Composite 0.790 → 0.619.

**import_activity_history (id=1353):** Vol 0.618 → stable → **0.000**. Composite 0.836 → 0.713.

**_validate_contract_json (id=3822):** Vol 0.730 → stable → **0.000**. Composite 0.784 → 0.678.

### Chunks with partial volatility decline (Vol drop ~0.42)

**contract_fuel_import_combined (id=3929):** Vol 0.978 → **0.556**. Composite 0.861 → 0.794.

**contracts_list (id=3881):** Vol 0.978 → **0.556**. Composite 0.858 → 0.800.

**contract_lanes_bulk (id=3920):** Vol 0.978 → **0.556**. Composite 0.819 → 0.754.

**contract_edit (id=3884):** Vol 0.978 → **0.556**. Composite 0.788 → 0.728.

**contract_fuel_brackets_bulk (id=3928):** Vol 0.978 → **0.556**. Composite 0.778 → 0.710.

### Chunks with stable or increasing volatility

**action_queue (id=3770):** Vol 0.832 → **1.000** (increased). Composite 0.845 → 0.850. This function got more volatile between cycles.

**record_response (id=3777):** Vol 0.832 → **1.000** (increased). Composite 0.820 → 0.800 (slight drop from coupling decline, offset by vol increase and staleness improvement).

### run_validation (id=971, BACKLOG-cited, not in anchor top-20)

Vol 1.000 → constant → **0.111**. Cov 1.000, comp 0.939 flat. Composite 0.773 → 0.597.

**Critical pattern:** All volatility changes happened between cycles 16 and 17 — the 33-day gap between 2026-04-14 and 2026-05-17. During cycles 10-16 (all on 2026-04-14), volatility was effectively frozen because the git history window was the same. The cycle-17 run re-evaluated volatility with a fresh 4-week git window, causing the mass re-ranking.

---

## (4) Classification

| Chunk | File | Role | Anchor Comp | Latest Comp | Delta Comp | Cov Delta | Comp Delta | Vol Delta | Bucket |
|-------|------|------|-------------|-------------|------------|-----------|------------|-----------|--------|
| carrier_import_accessorials | web/carrier_profiles.py | route_handler | 0.873 | 0.706 | -0.167 | 0.000 | 0.000 | -0.933 | VOLATILITY-DECAYED |
| carrier_import_fuel | web/carrier_profiles.py | route_handler | 0.865 | 0.698 | -0.167 | 0.000 | -0.001 | -0.933 | VOLATILITY-DECAYED |
| contract_fuel_import_combined | web/contracts.py | route_handler | 0.861 | 0.794 | -0.067 | 0.000 | 0.000 | -0.422 | OTHER |
| contracts_list | web/contracts.py | route_handler | 0.858 | 0.800 | -0.058 | 0.000 | 0.000 | -0.422 | OTHER |
| action_queue | web/action_queue.py | route_handler | 0.845 | 0.850 | +0.004 | 0.000 | -0.061 | +0.168 | OTHER |
| carrier_import_minimums | web/carrier_profiles.py | route_handler | 0.838 | 0.676 | -0.162 | 0.000 | 0.000 | -0.933 | VOLATILITY-DECAYED |
| import_activity_history | ingestion/activity_import.py | utility | 0.836 | 0.713 | -0.122 | 0.000 | 0.000 | -0.618 | VOLATILITY-DECAYED |
| record_response | web/action_queue.py | route_handler | 0.820 | 0.800 | -0.019 | 0.000 | 0.000 | +0.168 | OTHER |
| contract_lanes_bulk | web/contracts.py | route_handler | 0.819 | 0.754 | -0.065 | 0.000 | 0.000 | -0.422 | OTHER |
| rates_grid | web/rates.py | route_handler | 0.812 | 0.650 | -0.161 | 0.000 | 0.000 | -0.888 | VOLATILITY-DECAYED |
| dispute_brief | app.py | utility | 0.805 | 0.630 | -0.175 | 0.000 | 0.000 | -0.889 | VOLATILITY-DECAYED |
| write_extraction_quality_report | extraction_tracking.py | utility | 0.804 | 0.626 | -0.178 | 0.000 | 0.000 | -0.899 | VOLATILITY-DECAYED |
| team_dashboard | app.py | utility | 0.801 | 0.626 | -0.174 | 0.000 | 0.000 | -0.889 | VOLATILITY-DECAYED |
| invoice_detail | app.py | utility | 0.790 | 0.658 | -0.132 | 0.000 | 0.000 | -0.889 | VOLATILITY-DECAYED |
| _run_ingestion_rows | ingestion/ingest.py | ingestion_orchestrator | 0.790 | 0.619 | -0.172 | 0.000 | 0.000 | -0.876 | VOLATILITY-DECAYED |
| contract_edit | web/contracts.py | route_handler | 0.788 | 0.728 | -0.060 | 0.000 | 0.000 | -0.422 | OTHER |
| _build_carrier_cards | web/carrier_profiles.py | route_handler | 0.786 | 0.602 | -0.183 | 0.000 | 0.000 | -0.933 | VOLATILITY-DECAYED |
| _validate_contract_json | web/contract_import.py | route_handler | 0.784 | 0.678 | -0.106 | 0.000 | 0.000 | -0.730 | VOLATILITY-DECAYED |
| contract_fuel_brackets_bulk | web/contracts.py | route_handler | 0.778 | 0.710 | -0.068 | 0.000 | -0.029 | -0.422 | OTHER |
| carrier_profile_detail | web/carrier_profiles.py | route_handler | 0.775 | 0.617 | -0.158 | 0.000 | 0.000 | -0.933 | VOLATILITY-DECAYED |

### Bucket Summary

| Bucket | Count |
|--------|-------|
| VOLATILITY-DECAYED | 13 |
| OTHER | 7 |
| REMEDIATED-COVERAGE | 0 |
| REMEDIATED-COMPLEXITY | 0 |
| REMEDIATED-BOTH | 0 |
| STALE-NOISE | 0 |
| DELETED | 0 |

**Interpretation of OTHER:** The 7 OTHER chunks break into two sub-patterns:
- **5 partial volatility decay** (contracts.py functions): Vol dropped ~0.42, below the 0.5 threshold but still material. All went from 0.978 → 0.556. These are effectively "volatility-attenuated" — the same phenomenon as VOLATILITY-DECAYED, just not as extreme because these functions retained some recent commits.
- **2 volatility increases** (action_queue, record_response): Vol increased from 0.832 → 1.000. These functions had new commits in the cycle-17 git window, making them more volatile and partially masking the decay pattern.

If the classification threshold were lowered to 0.4, the VOLATILITY-DECAYED count would be **18/20** (90%).

---

## (5) Role-Weight Cross-Check

| Role | # Tracked Chunks | Vol | Cov | Comp | Coup | Stale | Vol >= 0.25 AND Cov <= 0.25? |
|------|-------------------|-----|-----|------|------|-------|------------------------------|
| route_handler | 14 | 0.20 | 0.30 | 0.25 | 0.15 | 0.10 | No |
| utility | 5 | 0.20 | 0.20 | 0.30 | 0.15 | 0.15 | No |
| ingestion_orchestrator | 1 | 0.20 | 0.25 | 0.20 | 0.20 | 0.15 | No |

**No tracked role has vol >= 0.25 AND cov <= 0.25.** All three roles use 0.20 for volatility, below the 0.25 susceptibility threshold.

However, two roles not represented in the tracked population ARE susceptible:
- **data_model:** vol = 0.30, cov = 0.20 — **FLAGGED** (highest vol weight of any role, lowest cov weight)
- **Global default** (roles not in `ROLE_SCORING_WEIGHTS`): vol = 0.25, cov = 0.25 — **BORDERLINE**

Despite the tracked roles having a relatively modest 0.20 volatility weight, the decay was still severe enough to cause mass displacement. This indicates that even 0.20 is too high when volatility can swing from 1.0 to 0.0 between cycles.

---

## (6) Top-N Displacement Check

### Cycle-17 invoice-pulse top-20 (coverage >= 0.99)

| Rank | ID | Name | File | Composite |
|------|----|------|------|-----------|
| 1 | 3770 | action_queue | web/action_queue.py | 0.850 |
| 2 | 3777 | record_response | web/action_queue.py | 0.800 |
| 3 | 3881 | contracts_list | web/contracts.py | 0.800 |
| 4 | 3929 | contract_fuel_import_combined | web/contracts.py | 0.794 |
| 5 | 3920 | contract_lanes_bulk | web/contracts.py | 0.754 |
| 6 | 3884 | contract_edit | web/contracts.py | 0.728 |
| 7 | 3883 | contract_new | web/contracts.py | 0.716 |
| 8 | 1353 | import_activity_history | ingestion/activity_import.py | 0.713 |
| 9 | 1448 | run_profiled_ingestion | profile_ingestion.py | 0.712 |
| 10 | 1196 | match_lane | engines/lane_matcher.py | 0.711 |
| 11 | 3928 | contract_fuel_brackets_bulk | web/contracts.py | 0.710 |
| 12 | 3941 | contract_fak_bulk | web/contracts.py | 0.707 |
| 13 | 3811 | carrier_import_accessorials | web/carrier_profiles.py | 0.706 |
| 14 | 4505 | contract_merge | web/contracts.py | 0.706 |
| 15 | 3812 | carrier_import_fuel | web/carrier_profiles.py | 0.698 |
| 16 | 3511 | run_test | tests/test_upload_5_lanes.py | 0.690 |
| 17 | 3888 | _save_contract | web/contracts.py | 0.688 |
| 18 | 3926 | contract_fuel_save | web/contracts.py | 0.687 |
| 19 | 4055 | _import_lanes_section | web/gap_dashboard.py | 0.678 |
| 20 | 3822 | _validate_contract_json | web/contract_import.py | 0.678 |

### Displacement summary

- **Anchor chunks still in cycle-17 top-20:** 11 of 20
- **Fell out:** 9 of 20

| Fell-out chunk | Bucket |
|---------------|--------|
| dispute_brief (970) | VOLATILITY-DECAYED |
| team_dashboard (983) | VOLATILITY-DECAYED |
| invoice_detail (960) | VOLATILITY-DECAYED |
| write_extraction_quality_report (1337) | VOLATILITY-DECAYED |
| _run_ingestion_rows (1388) | VOLATILITY-DECAYED |
| _build_carrier_cards (3794) | VOLATILITY-DECAYED |
| carrier_profile_detail (3795) | VOLATILITY-DECAYED |
| carrier_import_minimums (3813) | VOLATILITY-DECAYED |
| rates_grid (4114) | VOLATILITY-DECAYED |

**Result: 0 fell out via REMEDIATION. 9 fell out via VOLATILITY-DECAYED. The ratio is 0:9.**

---

## (7) Evaluation of Four BACKLOG Options

### Option (a): Reduce volatility weight

**Variant 1: vol = 0.15 (+0.05 each to coverage and complexity)**

| Rank | Name | Alt Composite | Actual Composite | Anchor? |
|------|------|---------------|------------------|---------|
| 1 | action_queue | 0.848 | 0.850 | Yes |
| 2 | contracts_list | 0.822 | 0.800 | Yes |
| 3 | contract_fuel_import_combined | 0.816 | 0.794 | Yes |
| 4 | record_response | 0.799 | 0.800 | Yes |
| 5 | contract_lanes_bulk | 0.775 | 0.754 | Yes |
| 6 | import_activity_history | 0.763 | 0.713 | Yes |
| 7 | run_profiled_ingestion | 0.760 | 0.712 | |
| 8 | carrier_import_accessorials | 0.756 | 0.706 | Yes |
| 9 | match_lane | 0.748 | 0.711 | |
| 10 | carrier_import_fuel | 0.747 | 0.698 | Yes |
| 11 | contract_edit | 0.745 | 0.728 | Yes |
| 12 | document_extract | 0.735 | 0.635 | |
| 13 | contract_new | 0.732 | 0.716 | |
| 14 | _validate_contract_json | 0.728 | 0.678 | Yes |
| 15 | run_test | 0.726 | 0.690 | |
| 16 | contract_fuel_brackets_bulk | 0.725 | 0.710 | Yes |
| 17 | carrier_import_minimums | 0.725 | 0.676 | Yes |
| 18 | contract_fak_bulk | 0.724 | 0.707 | |
| 19 | contract_merge | 0.719 | 0.706 | |
| 20 | training_batch_apply | 0.715 | 0.666 | |

Anchor chunks retained: **12/20**. `dispute_brief`: rank 30. `run_validation`: rank 49.

**Variant 2: vol = 0.10 (+0.075 each to coverage and complexity)**

Anchor chunks retained: **13/20**. `dispute_brief`: rank 28. `run_validation`: rank 43.

Notable new entrants at vol=0.10: `rates_grid` (rank 17), `invoice_detail` (rank 19) — both recovered from VOLATILITY-DECAYED status.

**Assessment:** Reducing volatility weight helps but does not fully solve the problem. Even at vol=0.10, 7 anchor chunks remain displaced. The root issue is that a score swinging from 1.0 to 0.0 contributes 0.10-0.25 composite points — enough to displace rankings even at reduced weight.

### Option (b): Sticky flag for high-impact findings

Two design variants:

**Variant B1: Cycle-count sticky.** A finding stays in the top-N for K cycles after first appearing, regardless of composite changes. Implementation sketch:
```python
# In health_scores or a new table:
ALTER TABLE health_scores ADD COLUMN first_appeared_cycle_id INTEGER;
ALTER TABLE health_scores ADD COLUMN sticky_until_cycle INTEGER;

# In scorer.py ranking logic:
def get_effective_top_n(cycle_id, n=20):
    # Get current top-N by composite
    current_top = query_top_n(cycle_id, n)
    # Get sticky findings still within their window
    sticky = query_sticky_findings(cycle_id)
    # Merge: sticky findings displace lowest-ranked current entries
    return merge_with_sticky(current_top, sticky, n)
```
**Pros:** Simple. **Cons:** Arbitrary K value; doesn't distinguish between findings that are genuinely resolving vs. volatility-decayed. A finding with improving coverage would stay sticky even though it's actually being remediated.

**Variant B2: Coverage-gated sticky.** A finding stays in top-N until `coverage_score` drops below a threshold (e.g., 0.5, meaning tests were added). Only coverage_score unlocks the sticky flag.
```python
# In scorer.py:
def should_unstick(chunk_id, cycle_id):
    current = get_health_scores(chunk_id, cycle_id)
    return current.coverage_score < 0.5  # Tests added = unstick

# When ranking:
def get_effective_top_n(cycle_id, n=20):
    current_top = query_top_n(cycle_id, n)
    sticky = [f for f in query_sticky_findings(cycle_id)
              if not should_unstick(f.chunk_id, cycle_id)]
    return merge_with_sticky(current_top, sticky, n)
```
**Pros:** Directly addresses the problem — findings only leave when the root cause (no test coverage) is fixed. **Cons:** More complex. Requires a new table or column. Doesn't handle complexity remediation.

**Design space note:** Variant B2 could be generalized to "unstick when any REMEDIATION-class event occurs" (coverage OR complexity improves beyond a threshold).

### Option (c): Secondary ranking by `coverage * complexity`

Top-20 by `coverage_score * complexity_score` at cycle 17:

| Rank | Name | cov * comp | Actual Composite | Anchor? |
|------|------|-----------|------------------|---------|
| 1 | invoice_detail | 1.000 | 0.658 | Yes |
| 2 | InvoiceXMLParser | 1.000 | 0.486 | |
| 3 | _validate_contract_json | 1.000 | 0.678 | Yes |
| 4 | rates_grid | 1.000 | 0.650 | Yes |
| 5 | contract_fuel_import_combined | 0.999 | 0.794 | Yes |
| 6 | import_contract_setup | 0.999 | 0.636 | |
| 7 | team_dashboard | 0.998 | 0.626 | Yes |
| 8 | import_activity_history | 0.998 | 0.713 | Yes |
| 9 | enrich_invoice | 0.998 | 0.673 | |
| 10 | TestScenario1_EnrichmentSucceeds | 0.996 | 0.499 | |
| 11 | _parse_generic_csv | 0.996 | 0.597 | |
| 12 | contracts_list | 0.995 | 0.800 | Yes |
| 13 | _import_fuel_section | 0.993 | 0.627 | |
| 14 | document_extract | 0.993 | 0.635 | |
| 15 | _import_lanes_section | 0.991 | 0.678 | |
| 16 | generate_pricing_ticket | 0.990 | 0.572 | |
| 17 | **dispute_brief** | **0.989** | 0.630 | **Yes** |
| 18 | carrier_import_fuel | 0.989 | 0.698 | Yes |
| 19 | debug_export | 0.987 | 0.582 | |
| 20 | TestImport | 0.984 | 0.495 | |

**`dispute_brief` is rank 17** — in the top-20 under this ranking. `run_validation` is rank 38.

**Assessment:** This is the cheapest option to implement (no weight changes, no schema changes — just an alternative sort). It directly surfaces the highest-risk functions (zero coverage + high complexity) regardless of volatility. However, it completely ignores volatility, coupling, and staleness, which are valuable signals for functions that DO have test coverage.

### Option (d): Conditional volatility decay

**Variant D1: Multiply volatility contribution by 0.5 when coverage = 1.0**

Anchor chunks retained: **13/20**. `dispute_brief`: rank 29. `run_validation`: rank 43.

**Variant D2: Floor volatility at 0.5 when coverage = 1.0**

| Rank | Name | Alt Composite | Actual Composite | Anchor? |
|------|------|---------------|------------------|---------|
| 1 | action_queue | 0.850 | 0.850 | Yes |
| 2 | import_activity_history | 0.813 | 0.713 | Yes |
| 3 | run_profiled_ingestion | 0.812 | 0.712 | |
| 4 | carrier_import_accessorials | 0.806 | 0.706 | Yes |
| 5 | record_response | 0.800 | 0.800 | Yes |
| 6 | contracts_list | 0.800 | 0.800 | Yes |
| 7 | carrier_import_fuel | 0.798 | 0.698 | Yes |
| 8 | contract_fuel_import_combined | 0.794 | 0.794 | Yes |
| 9 | _validate_contract_json | 0.778 | 0.678 | Yes |
| 10 | carrier_import_minimums | 0.777 | 0.676 | Yes |
| 11 | match_lane | 0.766 | 0.711 | |
| 12 | training_batch_apply | 0.766 | 0.666 | |
| 13 | document_extract | 0.760 | 0.635 | |
| 14 | contract_lanes_bulk | 0.754 | 0.754 | Yes |
| 15 | rates_grid | 0.751 | 0.650 | Yes |
| 16 | run_test | 0.746 | 0.690 | |
| 17 | get_attestation_requests | 0.736 | 0.636 | |
| 18 | invoice_detail | 0.736 | 0.658 | Yes |
| 19 | email_archiver | 0.735 | 0.635 | |
| 20 | contract_edit | 0.728 | 0.728 | Yes |

Anchor chunks retained: **13/20**. `dispute_brief`: rank 27. `run_validation`: rank 47.

**Assessment:** The floor variant (D2) is the strongest option structurally. It says: "if you have zero test coverage, your volatility score cannot drop below 0.50 — you are treated as at least moderately volatile regardless of actual commit history." This directly encodes the insight that untested functions are inherently risky even when stable. It retains 13/20 anchor chunks, recovers `rates_grid` and `invoice_detail` into the top-20, and preserves volatility's full signal range for functions that DO have test coverage.

---

## (8) Additional Options Surfaced by the Data

### Option (e): Time-aware volatility normalization

The audit reveals that the mass volatility collapse occurred because of a 33-day gap between cycles 16 (2026-04-14) and 17 (2026-05-17). During that gap, the git history window (`GIT_HISTORY_WEEKS = 4`) rolled forward, and many commits that were "recent" at cycle 16 aged out of the window by cycle 17. Percentile normalization then compressed the remaining commits into a smaller range.

A potential fix: normalize volatility not just within a cycle's snapshot but relative to the chunk's historical volatility trajectory. For example, a chunk's volatility score could be `max(current_percentile, 0.5 * previous_cycle_percentile)` — a momentum dampener that prevents single-cycle collapses exceeding 50%.

This is more complex than options (a)-(d) and requires storing previous-cycle volatility for comparison. However, it would be self-tuning and would not require different behavior based on coverage_score.

### No other additional options surfaced.

---

## (9) Methodology Limitations

1. **Raw volatility values are not accessible.** Only percentile-normalized scores are stored in `health_scores`. Therefore, this audit cannot distinguish between:
   - (a) A function's underlying commit frequency genuinely declining (fewer commits touching it), vs.
   - (b) Other functions' commit frequency increasing (pushing this function's percentile down).
   The `git_changes` table does store `commit_date` values (range: 2026-03-05 to 2026-05-15), so raw volatility could theoretically be reconstructed by replaying the scorer's git-history aggregation logic against `git_changes`. This was not done in this audit.

2. **Only invoice-pulse is covered.** This is the only project with multi-cycle history in the database.

3. **Forward-tracking only.** The audit tracks the anchor cycle-10 top-20 forward to cycle 17. It does not account for chunks that were newly ADDED to the top-20 between cycles (new entrants). The 9 new entrants in the cycle-17 top-20 that replaced the 9 displaced anchor chunks were not characterized.

4. **Cycle 9 anomaly.** Cycle 9 has 7,672 health_scores (double the 3,836 of cycles 10-16). This suggests a possible double-scoring or schema issue. The audit used cycle 10 as the anchor to avoid this anomaly. The root cause of the cycle-9 double-count was not investigated.

5. **The classification threshold (vol delta >= 0.5) is somewhat arbitrary.** Five chunks with vol delta of 0.422 were classified as OTHER but are functionally the same phenomenon. A threshold of 0.4 would classify 18/20 (90%) as VOLATILITY-DECAYED.

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** Step 1 (single-step diagnostic)
**Status:** Complete

### What Was Done
Population-scale audit of scoring-weight volatility decay across the cycle-10 to cycle-17 audit window. Tracked 20 anchor chunks, classified trajectories, evaluated four BACKLOG weight-change options plus one additional option surfaced by the data.

### Files Deposited
- `knowledge/research/scoring-weights-volatility-decay-audit-2026-05-18.md` — full diagnostic findings with 9 sections

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- Used cycle 10 (not cycle 9) as anchor due to cycle-9 double-count anomaly
- Classification threshold of vol delta >= 0.5 per diagnostic spec, with note that 0.4 threshold yields 90% VOLATILITY-DECAYED

### Flags for CEO
- **Headline finding: 0:9 remediation-to-decay ratio demands a scoring methodology change.** The current system silently drops critical zero-coverage findings solely via volatility decay. This is not a marginal effect — it affects 65-90% of the tracked population.
- **Option (d) floor variant + option (c) secondary ranking** appear complementary and could be adopted together. Option (d) fixes the composite formula; option (c) provides a volatility-independent backup view.
- **Scoring weight changes are gated to CEO authority** per the SA's decision matrix.

### Flags for Next Step
- None (diagnostic complete, no follow-on execution step)
