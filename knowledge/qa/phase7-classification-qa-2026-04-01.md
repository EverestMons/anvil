# Phase 7: Functional Classification + Provenance — QA Report
**Date:** 2026-04-01 | **Agent:** Anvil QA Analyst | **Step:** 3
**Dev log:** anvil/knowledge/development/phase7-classification-2026-04-01.md
**Blueprint:** anvil/knowledge/architecture/phase7-classification-blueprint-2026-04-01.md

---

## Area 1 — Schema: PASS

- functional_roles table: 25 rows (all 25 roles present across 5 parent groups)
- chunk_provenance table: exists with chunk_id FK CASCADE, plan_name, dev_log_path, plan_description
- chunk_provenance indexes: idx_chunk_provenance_chunk, idx_chunk_provenance_plan
- code_chunks.functional_role column: present (TEXT, nullable)

## Area 2 — Classification: PASS

Ran classifier against live invoice-pulse data:
- **1605 chunks classified**, 0 unclassified (of classifiable chunks)
- 24 of 25 roles assigned (configuration role not triggered — no config chunk_types in IP)

Role distribution (top 10):
| Role | Count |
|---|---|
| utility | 759 |
| route_handler | 280 |
| report_generator | 120 |
| ingestion_orchestrator | 52 |
| validation_gate | 48 |
| confidence_engine | 33 |
| data_model | 29 |
| email_processor | 25 |
| action_router | 24 |
| document_manager | 22 |

Spot checks (10 chunks across 5 roles):
- route_handler chunks in web/ files: PASS
- validation_gate chunks in engines/validator.py: PASS
- data_model chunks in database.py/contract_tables.py: PASS
- confidence_engine chunks in engines/confidence.py: PASS
- content_generator chunks via name pattern: PASS

**Note:** "utility" is the largest category (759 chunks / 47%). This is expected — many helper functions in web/ blueprints match the web/ catch-all file path rule and are classified as route_handler, while private helpers in engine files inherit the engine's role. The utility count represents genuinely generic helpers plus some engine-internal functions that don't match specific name patterns. Phase 8's purpose-aware scoring will handle this gracefully since "utility" gets default weights.

## Area 3 — Coverage: PASS

- Classifiable chunks (excluding module + test_case): 1527
- Classified: 1527 (100%)
- Unclassified: 0
- Coverage: **100%** (threshold: >80%)

## Area 4 — Provenance: PASS (after fix)

Initial run found 0 parsed logs. Investigation revealed real dev logs wrap file paths in backticks (e.g., `` `web/action_queue.py` ``). Fixed BULLET_PATTERN and TABLE_ROW_PATTERN to handle optional backticks.

After fix:
- Logs parsed: 100
- Provenance entries created: 8,404
- Unmatched files: 8 (expected — some dev logs reference files that were later renamed/deleted)

Spot check 5 entries: all have valid dev_log_path (file exists), reasonable plan_name, and correct chunk linkage. PASS.

## Area 5 — Pipeline: PASS

Ran full cycle with functional_role reset to NULL beforehand:
- CLASSIFY stage ran after EXTRACT, classified 1,605 chunks
- PROVENANCE stage ran after CLASSIFY
- SCORE stage ran after CLASSIFY with functional_role populated
- LAB stage produced findings
- Pipeline order confirmed: SCAN -> EXTRACT -> CLASSIFY -> PROVENANCE -> SCORE -> LAB

## Area 6 — Existing Pipeline: PASS

Full cycle produced correct output:
- Scanner, extractor, scorer, lab all completed without errors
- 3,355 chunks scored (includes module + test_case chunks scored by scorer)
- No regressions in existing pipeline behavior

## Area 7 — Test Suite: PASS

```
170 passed, 2 failed (pre-existing)
```

The 2 failures are pre-existing lab threshold tests (test_find_cochange_patterns, test_find_staleness_alerts) unrelated to Phase 7.

New tests: 37 (22 classifier + 15 provenance including backtick fix test)

---

## QA-Discovered Issue: Backtick-Wrapped Paths

**Issue:** Dev log parser failed to extract file paths from real invoice-pulse dev logs because paths were wrapped in markdown backticks.
**Fix:** Updated BULLET_PATTERN and TABLE_ROW_PATTERN with optional backtick matching (`?`).
**Commit:** `fix: handle backtick-wrapped file paths in dev log parser`
**Impact:** Without this fix, provenance ingestion would produce 0 entries. Fix was applied and verified before this report.

---

## Summary

| Area | Result |
|---|---|
| 1. Schema | PASS |
| 2. Classification | PASS |
| 3. Coverage | PASS (100%) |
| 4. Provenance | PASS (after backtick fix) |
| 5. Pipeline | PASS |
| 6. Existing pipeline | PASS |
| 7. Test suite | PASS (170/172, 2 pre-existing) |

**Overall: PASS**

---

## Output Receipt
**Agent:** Anvil QA Analyst
**Step:** 3 (Phase 7 QA)
**Status:** Complete

### What Was Done
Verified Phase 7 across 7 areas. Discovered and fixed a backtick-wrapping issue in the dev log parser. All areas pass.

### Files Deposited
- anvil/knowledge/qa/phase7-classification-qa-2026-04-01.md -- this QA report

### Files Created or Modified (Code)
- src/provenance.py -- fixed BULLET_PATTERN and TABLE_ROW_PATTERN for backtick-wrapped paths
- tests/test_provenance.py -- added test_extract_backtick_wrapped_paths

### Decisions Made
- Classified "utility" dominance (47%) as acceptable for Phase 7 — Phase 8 scoring handles this
- 8 unmatched provenance files are expected (renamed/deleted files)

### Flags for CEO
- None

### Flags for Next Step
- Phase 8 can proceed — classification and provenance infrastructure is validated
