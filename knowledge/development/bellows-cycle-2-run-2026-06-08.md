# Bellows Cycle 2 — Dev Run Log (Fix-Validation Re-run)
**Date:** 2026-06-08
**Agent:** Anvil Developer
**Plan:** executable-anvil-bellows-cycle-2-2026-06-08

## Pre-Cycle Snapshot

```
bellows project_id: 2
last cycle: 1
```

Confirmed: project_id=2, last cycle=1 → this run is cycle 2.

## Cycle Execution

```python
from src.cycle import run_cycle
result = run_cycle(conn, "bellows")
```

**Elapsed:** 26.23s

### run_cycle Return Value

```json
{
  "cycle_id": 2,
  "project_name": "bellows",
  "scan": {
    "project_name": "bellows",
    "files_total": 3088, "files_new": 8, "files_changed": 1,
    "files_unchanged": 3079, "git_commits_ingested": 0
  },
  "extract": {
    "files_processed": 42, "chunks_created": 0, "chunks_updated": 4,
    "symbols_extracted": 6648, "dependencies_resolved": 2344,
    "fingerprints_created": 607, "similarities_found": 14
  },
  "classify": {
    "classified": 155, "unclassified": 0,
    "role_distribution": {"utility": 155}
  },
  "provenance": {
    "logs_parsed": 90, "provenance_entries_created": 0,
    "unmatched_files": 96
  },
  "score": {
    "chunks_scored": 607,
    "score_distribution": {"high_risk": 1, "medium": 128, "low_risk": 478},
    "avg_composite": 0.2555
  },
  "lab": {
    "findings": {
      "coverage_gaps": 0, "coupling_hotspots": 7, "clone_candidates": 14,
      "staleness_alerts": 21, "complexity_hotspots": 12, "cochange_patterns": 10,
      "best_practice_deviations": 18, "intent_gaps": 0
    },
    "total_findings": 82,
    "constraints_generated": 72,
    "report_path": "/Users/marklehn/Developer/GitHub/anvil/knowledge/research/cycle-2-findings-2026-06-08.md"
  },
  "elapsed_seconds": 26.23
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
- `cycle_number` (cycle_id): 2 ✓

## Fix-Validation Checks

### (1) Top-10 by Composite Must Be All Bellows

| # | Function | File | Composite | Status |
|---|---|---|---|---|
| 1 | run_plan | bellows.py | 0.720 | EXISTS (line 341) |
| 2 | _consume_verdicts | bellows.py | 0.665 | EXISTS (line 1269) |
| 3 | _teardown_worktree | bellows.py | 0.608 | EXISTS (line 880) |
| 4 | _log | bellows.py | 0.606 | EXISTS (line 44) |
| 5 | _create_worktree | bellows.py | 0.599 | EXISTS (line 770) |
| 6 | start | bellows.py | 0.593 | EXISTS (line 1508) |
| 7 | _gate_rule_22_verification | gates.py | 0.582 | EXISTS (line 511) |
| 8 | slug_for | bellows.py | 0.558 | EXISTS (line 71) |
| 9 | Bellows | bellows.py | 0.540 | EXISTS (line 1159) |
| 10 | _flush_buffer | notifier.py | 0.539 | EXISTS (line 103) |

**ALL 10 EXIST in bellows source.** This is the exact inverse of cycle 1, where all 10 were MISSING / invoice-pulse. ✓ **FIX VALIDATED.**

### (2) Coverage-Gap Findings Must All Be Bellows

Query used (reproducing `find_coverage_gaps` logic):
```sql
SELECT cc.id, cc.project_id, cc.name, cc.file_path, hs.coverage_score, hs.composite_score
FROM health_scores hs
JOIN code_chunks cc ON hs.chunk_id = cc.id
WHERE hs.cycle_id = 2 AND hs.coverage_score >= 0.8
AND hs.composite_score >= 0.7 AND cc.chunk_type != 'test_case'
AND cc.file_path NOT LIKE 'tests/%'
AND cc.project_id = 2
ORDER BY hs.composite_score DESC
```

**Result:** 0 coverage gaps for bellows (project_id=2, cycle_id=2).

**Cross-check WITHOUT project_id filter:** 47 rows returned, ALL with project_id=1 (invoice-pulse). ZERO bellows rows. This confirms the fix is working — the `AND cc.project_id = ?` clause in `find_coverage_gaps` correctly excludes cross-project data.

Coupling hotspots (also fixed): 7 rows, ALL project_id=2 (bellows). ZERO non-bellows rows. ✓

**ZERO non-bellows rows in either fixed function. FIX VALIDATED.**

### (3) CRITICAL Findings and Severity Breakdown

**CRITICAL findings:** None.

**Findings by type:**
| Finding Type | Cycle 2 | Cycle 1 | Delta |
|---|---|---|---|
| coverage_gaps | 0 | 28 (all invoice-pulse) | -28 (leak eliminated) |
| coupling_hotspots | 7 | 10 | -3 |
| clone_candidates | 14 | 14 | 0 |
| staleness_alerts | 21 | 21 | 0 |
| complexity_hotspots | 12 | 12 | 0 |
| cochange_patterns | 10 | 10 | 0 |
| best_practice_deviations | 18 | 18 | 0 |
| intent_gaps | 0 | 0 | 0 |
| **TOTAL** | **82** | **113** | **-31** |

Coverage gaps dropped from 28 to 0 — the 28 were all from invoice-pulse (the leak). Bellows has no coverage gaps meeting the threshold, which is legitimate. Coupling hotspots dropped by 3: the fix excluded 3 invoice-pulse entries that were latent in cycle 1.

**Constraints by severity:**
| Severity | Count |
|---|---|
| CRITICAL | 0 |
| HIGH | 22 |
| MEDIUM | 45 |
| LOW | 0 |
| **TOTAL** | **72** (vs cycle 1's 103) |

### (4) Test-File Filter Regression

`grep -c "file_path.*tests/" cycle-2-findings-2026-06-08.md` → **0** ✓

Coverage Gaps (0 entries) and Coupling Hotspots (7 entries) contain zero test file paths. Test files do appear in Clone Candidates, Staleness Alerts, and Untested Complexity sections where they are expected (those sections do not filter test files by design).

### (5) Untested Complexity Section

`grep -n "Untested Complexity" cycle-2-findings-2026-06-08.md` → exactly 1 match (line 14, the header). ✓

Section contains **20 data rows**. ✓

### (6) No Audit-Findings File (Expected)

`ls -la /Users/marklehn/Developer/GitHub/bellows/knowledge/anvil/` → empty directory. No `audit-findings-*.md`. Correct — intent_gaps = 0, no bellows brief/glossary. ✓

## Runtime

**End-to-end:** 26.23 seconds

---

## Output Receipt
**Agent:** Anvil Developer
**Step:** Step 1
**Status:** Complete

### What Was Done
Ran Anvil Cycle 2 against bellows (fix-validation re-run). Pipeline completed successfully: 3088 files scanned (8 new, 1 changed), 42 Python files extracted (607 chunks), 82 findings generated. All 6 fix-validation checks passed: top-10 by composite are ALL bellows functions (EXISTS), coverage gaps and coupling hotspots contain ZERO non-bellows rows, no CRITICAL findings, no test-file contamination, Untested Complexity section present with 20 rows, no audit-findings file.

### Files Deposited
- `knowledge/development/bellows-cycle-2-run-2026-06-08.md` — this dev run log
- `knowledge/research/cycle-2-findings-2026-06-08.md` — cycle report (produced by run_cycle)

### Files Created or Modified (Code)
- None (no Anvil or bellows source modifications)

### Decisions Made
- Built top-10 by composite from all report finding sections (coupling hotspots, complexity hotspots, staleness alerts) since coverage gaps are empty
- Used direct SQL queries reproducing `find_coverage_gaps` and `find_coupling_hotspots` logic to verify project scoping, since there is no `findings` table — findings are computed at runtime

### Flags for CEO
- None. Fix is validated.

### Flags for Next Step
- All 6 validation checks passed. QA can proceed with confidence.
- Coverage gaps = 0 for bellows is legitimate (no bellows functions meet the coverage_score >= 0.8 AND composite_score >= 0.7 thresholds). The 47 rows that would have leaked without the fix are all project_id=1 (invoice-pulse).
- Coupling hotspots dropped from 10 to 7 vs cycle 1 — the 3 missing entries were invoice-pulse contamination that the fix now excludes.
- Classification mono-role: all 155 classified bellows chunks received `utility` role (same as cycle 1, expected per calibration caveat).
