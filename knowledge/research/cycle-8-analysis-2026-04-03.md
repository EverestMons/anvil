# Anvil Cycle 8 — Post-Session Health Check Analysis
**Date:** 2026-04-03
**Project:** invoice-pulse
**Previous cycle:** Cycle 7 (2026-04-01)

## Pipeline Results

| Stage | Result |
|---|---|
| SCAN | 2238 total files, 176 new, 55 changed, 2007 unchanged |
| EXTRACT | 186 files processed, 60 new chunks, 75 updated, 33551 symbols, 96123 deps |
| CLASSIFY | 1669 classified (0 unclassified), 25-role taxonomy fully mapped |
| PROVENANCE | 126 dev logs parsed, 488 provenance entries created |
| SCORE | 3476 chunks scored (61 high-risk, 1395 medium, 2020 low-risk) |
| LAB | 1760 findings across 7 categories |

## 3-Cycle Trend (6 → 7 → 8)

| Metric | Cycle 6 | Cycle 7 | Cycle 8 | Trend |
|---|---|---|---|---|
| Chunks | 3404 | 3416 | 3476 | +72 since C6 |
| Avg composite | 0.2613 | 0.2613 | 0.2666 | +0.0053 (slight uptick) |
| High risk (>=0.7) | 59 | 60 | 61 | +2 |
| Medium (0.3-0.7) | 1353 | 1361 | 1395 | +42 |
| Low risk (<0.3) | 1992 | 1995 | 2020 | +28 |
| Total findings | 1728 | 1728 | 1760 | +32 |

**Trend verdict:** Slightly upward risk. The +60 new chunks (mostly tests and small helpers) increased the medium bucket. The avg composite nudged up 0.005 — not alarming given 30+ commits of active development. The codebase is growing, not degrading.

## CEO Question 1: Did gap_dashboard.py Improve After CSV Decomposition?

**Mixed.** The _parse_csv_to_json function itself shows complexity=0.1091 (very low) — the decomposition succeeded in making the dispatcher thin. However:

- The old monolith's score was already low (0.4312) because the complexity was already split across sub-parsers in C7
- The **surrounding functions grew more complex** during this cycle:
  - _split_combined_csv: 0.4202 → 0.5278 (+0.1076), complexity 0.2650 → 0.6857
  - _import_contract_header_section: 0.5072 → 0.6146 (+0.1074), complexity 0.3894 → 0.7990
  - _sanitize_and_read_csv: 0.3815 → 0.4849 (+0.1034), complexity 0.1312 → 0.5300
- import_section (the entry point): 0.6837 → 0.7214 (+0.0377), crossed into high-risk

**Interpretation:** The CSV decomposition cleaned up _parse_csv_to_json but the refactoring moved complexity into the helper functions. The strip_copilot_artifacts centralization is visible (new chunk, score 0.3648, low complexity 0.0724) — that's clean. But _split_combined_csv and _sanitize_and_read_csv absorbed logic that increased their complexity scores significantly.

**Constraint:** gap_dashboard.py import_section is now high-risk (0.7214). The three degraded helpers (_split_combined_csv, _import_contract_header_section, _sanitize_and_read_csv) need complexity review.

## CEO Question 2: Did Coverage Gaps Decrease After 32 New Tests?

**No measurable improvement in coverage scores.** Zero chunks transitioned from coverage=1.0 (gap) to coverage<1.0 (covered) between C7 and C8.

This is because Anvil's coverage detection works through symbol bindings (chunk_symbol_bindings with type='tests') — the 32 new tests need their test files to have symbol bindings resolved back to the production chunks they exercise. The new test chunks are visible:
- tests/test_coverage_batch1.py (test_reshape_for_apply, test_parse_charge_csv, etc.)
- tests/test_coverage_batch2.py (TestCarrierImportAccessorials, TestCarrierImportMinimums, etc.)
- tests/test_coverage_batch3.py (TestImportContractJson, TestContractsList, etc.)

The tests exist as chunks with low composite scores (0.11-0.36), which is healthy. But the symbol binding resolver hasn't linked them back to the production functions they cover. This is a known limitation of the current extractor — it resolves 'tests' bindings by naming convention, not by import analysis.

**Action needed:** Extractor enhancement to detect pytest fixtures and direct function calls in test bodies to create 'tests' bindings.

## CEO Question 3: New High-Risk Chunks From Live Validation Code Path?

No new high-risk chunks from the live validation changes. The new chunks from validate_batch.py and engines/validator.py are all medium or low risk:
- revalidate_contract_invoices: 0.5037 (medium)
- MatchResult class: 0.4996 (medium)
- __bool__ method: 0.4999 (medium)

The invoice_detail route (app.py) was already high-risk in C7 (0.764) and ticked up slightly to 0.770. The live validation call doesn't add enough complexity to push it over any new threshold.

## CEO Question 4: Overall Health Trend

**Stable with controlled growth.** The codebase grew by 72 chunks across 3 cycles while maintaining a near-flat average composite (~0.266). The risk distribution stayed proportional — no explosion of high-risk code. The 30+ commit session added functionality without significantly degrading the health envelope.

## 5 Degraded Chunks (Composites Worsened >0.05)

| File | Function | C7 → C8 | Primary Driver |
|---|---|---|---|
| extraction_tracking.py | _compute_fields_from_data | 0.50 → 0.67 | Complexity 0.41 → 0.93 |
| engines/confidence.py | get_contradicting_invoices | 0.31 → 0.43 | Staleness 0.0 → 0.5 |
| web/gap_dashboard.py | _split_combined_csv | 0.42 → 0.53 | Complexity 0.27 → 0.69 |
| web/gap_dashboard.py | _import_contract_header_section | 0.51 → 0.61 | Complexity 0.39 → 0.80 |
| web/gap_dashboard.py | _sanitize_and_read_csv | 0.38 → 0.48 | Complexity 0.13 → 0.53 |

## New Chunks Summary (60 total)

- **Production code:** 9 new functions/classes (database migrations, validator helpers, gap_dashboard decomposition outputs)
- **Test code:** 51 new test cases/classes across 3 batch files (test_coverage_batch1/2/3.py)

## Planner Constraints

1. **gap_dashboard.py import_section** crossed the high-risk threshold (0.7214). Consider decomposing the entry point — it's now the gateway for strip_copilot_artifacts, _sanitize_and_read_csv, and the section dispatchers.

2. **extraction_tracking.py _compute_fields_from_data** had the largest single-chunk degradation (+0.1634). Complexity jumped from 0.41 to 0.93 — this function likely absorbed new field computation logic that should be split.

3. **Coverage binding gap:** 32 new tests were written but Anvil can't resolve them to production chunks. The extractor's symbol binding resolver needs enhancement to handle pytest-style test patterns (fixture injection, direct function calls in test bodies).

4. **Top 5 riskiest unchanged** from C7: _reshape_for_apply (0.889), _build_dashboard_cards (0.875), validate_invoice (0.868), contract_fuel_import_combined (0.854), carrier_import_fuel (0.832). These remain the priority coverage targets.

---
## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** standalone (Cycle 8 post-session health check)
**Status:** Complete

### What Was Done
Ran full SCAN → EXTRACT → CLASSIFY → PROVENANCE → SCORE → LAB pipeline as Cycle 8 against invoice-pulse. Compared results against Cycle 7 and tracked 3-cycle trend (6→7→8). Analyzed all 4 CEO questions with data-backed findings.

### Files Deposited
- knowledge/research/cycle-8-findings-2026-04-04.md — Lab-generated findings report (auto-generated by pipeline)
- knowledge/research/cycle-8-analysis-2026-04-03.md — This analysis with CEO answers and planner constraints

### Files Created or Modified (Code)
- anvil.db — Updated with Cycle 8 scan data, health scores, findings

### Decisions Made
- Ran pipeline against local invoice-pulse state (pre-scan-sync had unstaged changes, expected from 30+ commit session)
- Classified all 3 degraded gap_dashboard.py helpers as complexity-driven rather than coupling-driven

### Flags for CEO
- Coverage scores did NOT improve despite 32 new tests — extractor limitation, not a test quality issue
- import_section in gap_dashboard.py is now high-risk (0.7214) — the CSV decomposition shifted complexity into the dispatcher entry point

### Flags for Next Step
- Extractor enhancement needed for pytest symbol binding resolution
- None of the top 5 riskiest chunks changed between cycles — they remain the highest-leverage improvement targets
