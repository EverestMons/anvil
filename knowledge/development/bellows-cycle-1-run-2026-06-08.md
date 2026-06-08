# Bellows Cycle 1 — Dev Run Log
**Date:** 2026-06-08
**Agent:** Anvil Developer
**Plan:** executable-anvil-bellows-cycle-1-2026-06-08

## Pre-Cycle Snapshot

```
{'project_id': None, 'chunks': 0, 'last_cycle': None, 'git_changes': 0}
```

bellows not yet in `projects` table — first cycle. Expected.

## Cycle Execution

```python
from src.cycle import run_cycle
result = run_cycle(conn, "bellows")
```

**Elapsed:** 19.1s

### run_cycle Return Value

```json
{
  "cycle_id": 1,
  "project_name": "bellows",
  "scan": {
    "files_total": 3080, "files_new": 3080, "files_changed": 0,
    "files_unchanged": 0, "git_commits_ingested": 326
  },
  "extract": {
    "files_processed": 42, "chunks_created": 607, "chunks_updated": 2,
    "symbols_extracted": 7005, "dependencies_resolved": 1172,
    "fingerprints_created": 607, "similarities_found": 14
  },
  "classify": {
    "classified": 155, "unclassified": 0,
    "role_distribution": {"utility": 155}
  },
  "provenance": {
    "logs_parsed": 90, "provenance_entries_created": 5041,
    "unmatched_files": 96
  },
  "score": {
    "chunks_scored": 607,
    "score_distribution": {"high_risk": 1, "medium": 133, "low_risk": 473},
    "avg_composite": 0.2583
  },
  "lab": {
    "findings": {
      "coverage_gaps": 28, "coupling_hotspots": 10, "clone_candidates": 14,
      "staleness_alerts": 21, "complexity_hotspots": 12, "cochange_patterns": 10,
      "best_practice_deviations": 18, "intent_gaps": 0
    },
    "total_findings": 113,
    "constraints_generated": 103,
    "report_path": "/Users/marklehn/Developer/GitHub/anvil/knowledge/research/cycle-1-findings-2026-06-08.md"
  },
  "elapsed_seconds": 19.11
}
```

### Silent Stage Failure Check

- `scan`: No error key ✓
- `extract`: No error key ✓
- `classify`: No error key ✓
- `provenance`: No error key ✓
- `score`: No error key ✓
- `lab`: No error key ✓
- `aborted_at`: absent ✓
- `intent_gaps`: 0 (expected — no bellows PROJECT_BRIEF.md or domain-glossary.md) ✓

## Post-Cycle Snapshot

```
{'project_id': 2, 'chunks': 3687, 'last_cycle': 1, 'git_changes': 1348}
```

**Deltas:** project_id None→2 (created), chunks 0→3687, last_cycle None→1, git_changes 0→1348.

- `cycle_number = 1` in `cycle_reports` ✓
- `cycle_reports` row: `(1, 113, '2026-06-08T19:42:04.059622+00:00')` ✓

## Verification Steps

### (2) No audit-findings file (expected)

`/Users/marklehn/Developer/GitHub/bellows/knowledge/anvil/` listing:
```
total 0 (empty directory)
```
No `audit-findings-*.md`. Correct — intent_gaps = 0, no brief/glossary for bellows. ✓

### (3) Cycle report location

File exists at worktree path: `knowledge/research/cycle-1-findings-2026-06-08.md` (22,164 bytes). ✓

### (4) CRITICAL findings and severity breakdown

**CRITICAL findings:** None.

**Findings by type:**
| Finding Type | Count |
|---|---|
| coverage_gaps | 28 |
| coupling_hotspots | 10 |
| clone_candidates | 14 |
| staleness_alerts | 21 |
| complexity_hotspots | 12 |
| cochange_patterns | 10 |
| best_practice_deviations | 18 |
| intent_gaps | 0 |
| **TOTAL** | **113** |

**Constraints by severity:**
| Severity | Count |
|---|---|
| CRITICAL | 0 |
| HIGH | 59 |
| MEDIUM | 44 |
| LOW | 0 |
| **TOTAL** | **103** |

### (5) Test-file filter regression

`grep -c "file_path.*tests/" cycle-1-findings-2026-06-08.md` → **0** ✓

### (6) Untested Complexity section

Exactly 1 match for "Untested Complexity" (the header, line 43). Section contains **20 data rows**. ✓

### (7) Top-10 Highest-Composite Findings (from cycle report)

| Function | File | Composite | Finding Type |
|---|---|---|---|
| gate_9_accessorials | engines/validator.py | 0.793 | Coverage Gaps |
| gate_8_fuel | engines/validator.py | 0.785 | Coverage Gaps |
| training_batch_apply | web/training.py | 0.783 | Coverage Gaps |
| gate_7_linehaul | engines/validator.py | 0.783 | Coverage Gaps |
| _build_dashboard_cards | web/contracts.py | 0.778 | Coverage Gaps |
| _identify_training_gaps | web/training.py | 0.773 | Coverage Gaps |
| action_queue | web/action_queue.py | 0.766 | Coverage Gaps |
| carrier_import_accessorials | web/carrier_profiles.py | 0.752 | Coverage Gaps |
| contract_fuel_import_combined | web/contracts.py | 0.743 | Coverage Gaps |
| dispute_brief | app.py | 0.733 | Coverage Gaps |

### (8) Top-10 Existence Sanity Check

**ALL 10 MISSING** — none of these files exist in bellows source.

| Function | File | Status | Reason |
|---|---|---|---|
| gate_9_accessorials | engines/validator.py | MISSING | File does not exist in bellows |
| gate_8_fuel | engines/validator.py | MISSING | File does not exist in bellows |
| training_batch_apply | web/training.py | MISSING | File does not exist in bellows |
| gate_7_linehaul | engines/validator.py | MISSING | File does not exist in bellows |
| _build_dashboard_cards | web/contracts.py | MISSING | File does not exist in bellows |
| _identify_training_gaps | web/training.py | MISSING | File does not exist in bellows |
| action_queue | web/action_queue.py | MISSING | File does not exist in bellows |
| carrier_import_accessorials | web/carrier_profiles.py | MISSING | File does not exist in bellows |
| contract_fuel_import_combined | web/contracts.py | MISSING | File does not exist in bellows |
| dispute_brief | app.py | MISSING | File does not exist in bellows |

**Root cause: CROSS-PROJECT DATA LEAK.** All 10 are invoice-pulse functions (project_id=1) that leaked into the bellows cycle report. The Lab's finding functions (at minimum `find_coverage_gaps`) are not filtering by `project_id`. DB verification confirmed all 10 entries map to `code_chunks.project_id=1` (invoice-pulse).

### True Bellows Top-10 (from DB, production code only)

| Function | File | Composite | Coverage | Volatility |
|---|---|---|---|---|
| run_plan | bellows.py | 0.720 | 0.200 | 1.000 |
| _consume_verdicts | bellows.py | 0.665 | 0.200 | 1.000 |
| _teardown_worktree | bellows.py | 0.608 | 0.200 | 1.000 |
| _log | bellows.py | 0.606 | 1.000 | 1.000 |
| _create_worktree | bellows.py | 0.599 | 0.200 | 1.000 |
| start | bellows.py | 0.593 | 0.500 | 1.000 |
| _gate_rule_22_verification | gates.py | 0.582 | 0.200 | 0.824 |
| slug_for | bellows.py | 0.558 | 1.000 | 1.000 |
| Bellows | bellows.py | 0.540 | 0.200 | 1.000 |
| _flush_buffer | notifier.py | 0.539 | 1.000 | 0.176 |

**All 10 true bellows functions: EXISTS** ✓

### (9) Cycle report staged

```
Changes to be committed:
  new file:   knowledge/research/cycle-1-findings-2026-06-08.md
```
✓

## Cross-Project Data Leak Analysis

**Bug discovered:** The Lab's finding functions are not filtering queries by `project_id` (or equivalent project scope). When bellows cycle 1 ran, the Coverage Gaps section populated with 28 entries from invoice-pulse (project_id=1). Verified by checking `code_chunks.project_id` for each Coverage Gap entry — all map to project_id=1.

**Sections affected in the cycle report:**
- **Coverage Gaps (28):** ALL from invoice-pulse — zero bellows entries
- **Coupling Hotspots (10):** All bellows entries (bellows.py, gates.py, contract_tables.py, runner.py, etc.) ✓
- **Complexity Hotspots (12):** All bellows entries ✓
- **Untested Complexity (20):** Mix — includes test files from bellows ✓
- **Staleness Alerts (21):** All bellows entries ✓
- **Clone Candidates (14):** All bellows entries ✓
- **Co-Change Patterns (10):** All bellows entries ✓
- **Best Practice Deviations (18):** All bellows entries ✓

Coverage Gaps is the only section with cross-project contamination. The other 7 finding types are correctly scoped.

**Impact:** 28 of 113 findings (24.8%) are from the wrong project. The total_findings count of 113 overstates bellows findings by 28.

**Classification caveat note:** All 155 classified chunks received role=`utility` — this is the calibration caveat noted in the plan context. Bellows has no role_weight or role_threshold overrides, so the classifier falls back to default rules. The `utility` assignment is the fallback for unrecognized file patterns.

## Runtime

**End-to-end:** 19.1 seconds

---

## Output Receipt
**Agent:** Anvil Developer
**Step:** Step 1
**Status:** Complete

### What Was Done
Ran Anvil Cycle 1 against bellows (first cycle for this target). Pipeline completed successfully: 3080 files scanned, 42 Python files extracted (607 chunks), 326 git commits ingested, 113 findings generated, cycle report written. Discovered cross-project data leak in Coverage Gaps — all 28 coverage gap findings belong to invoice-pulse, not bellows. True bellows top-10 all verified EXISTS.

### Files Deposited
- `knowledge/development/bellows-cycle-1-run-2026-06-08.md` — this dev run log
- `knowledge/research/cycle-1-findings-2026-06-08.md` — cycle report (produced by run_cycle, staged in worktree)

### Files Created or Modified (Code)
- None (no Anvil source modifications)

### Decisions Made
- Reported findings from cycle report as-is while flagging cross-project leak
- Performed supplemental "true bellows top-10" existence check since report top-10 was contaminated

### Flags for CEO
- **CROSS-PROJECT DATA LEAK:** Lab `find_coverage_gaps` query is not filtered by `project_id`. All 28 Coverage Gap entries in the bellows cycle 1 report belong to invoice-pulse. This is a pre-existing Anvil bug exposed by the first multi-project run. Needs a fix plan (add project_id filter to coverage gap query and audit other finding functions).
- **Classification mono-role:** All 155 classified bellows chunks received `utility` role — expected per calibration caveat (no bellows-specific role overrides).

### Flags for Next Step
- QA should note the 28 contaminated Coverage Gap findings when verifying the cycle report. The true bellows findings are in the other 7 sections (85 findings, all bellows-scoped).
- The cross-project leak does NOT block QA — the cycle completed, report exists, DB row landed — but the Coverage Gaps section of the report is not trustworthy for bellows.
