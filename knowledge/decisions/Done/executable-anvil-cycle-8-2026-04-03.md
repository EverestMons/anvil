# Anvil Cycle 8 — Post-Session Codebase Health Check
**Date:** 2026-04-03

## Pre-Flight

Anvil operates on the Mac-side repos. Forge pre-scan-sync pulls the latest from Windows — run that first if not already done:

```bash
bash ~/Desktop/GitHub/forge/scripts/pre-scan-sync.sh
```

## Anvil Cycle Prompt

```
Run Anvil Cycle 8 against invoice-pulse. The last cycle was Cycle 7 (2026-04-01).

Today's IP session was massive — 30+ commits across the codebase. Key changes that affect health scoring:

1. **Parse CSV decomposition** — `_parse_csv_to_json` in gap_dashboard.py was the #1 risk chunk (cyclomatic 109). It's now a 13-line dispatcher + 6 named parsers. This should dramatically improve the composite score for gap_dashboard.py.

2. **New function: `strip_copilot_artifacts()`** — centralized paste sanitization at the import_section entry point. Replaced 3 scattered backslash patches. Should show as new chunk with low complexity.

3. **New function: `_persist_all_gates` now deletes before inserting** — validate_batch.py changed. Ghost gate result elimination.

4. **Live validation on page load** — app.py invoice detail route now calls validate_invoice + persist_results. New code path in a high-traffic route.

5. **32 new tests** across 15 functions (3 batches from codebase health Tier 2). Coverage gaps should have decreased.

6. **Contract type restriction** — contracts.py + contract_tables.py + startup migration. New VALID_CONTRACT_TYPES constant.

7. **Accessorial alias dedup** — contract_tables.py COALESCE UNIQUE index + seed guard. gap_dashboard.py upsert pattern in import handler.

8. **Timezone alignment** — 8 datetime calls changed across 4 files. 122 SQLite schema defaults changed from datetime('now') to datetime('now', 'localtime').

Run the full pipeline: SCAN → EXTRACT → CLASSIFY → PROVENANCE → SCORE → LAB. Compare to Cycle 7 metrics. Specifically interested in:
- Did gap_dashboard.py's composite score improve after the CSV decomposition?
- Did coverage gap findings decrease after the 32 new tests?
- Are there new high-risk chunks from the live validation code path?
- What's the overall health trend: Cycle 6 → 7 → 8?
```

## Expected Outputs
- Updated `anvil.db` with new scan data
- Health score comparison: Cycle 7 → Cycle 8
- New findings from changed code
- Planner constraints for any new high-risk areas
- Cycle report deposited to `anvil/knowledge/`
