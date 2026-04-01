# Phase 7: Functional Classification + Provenance — Dev Log
**Date:** 2026-04-01 | **Agent:** Anvil Developer | **Step:** 2
**Blueprint:** anvil/knowledge/architecture/phase7-classification-blueprint-2026-04-01.md

## What Was Built

### Task 1 — Schema + Migrations
- Added `functional_roles` table (name UNIQUE, description, parent_role, scoring_weights)
- Added `chunk_provenance` table (chunk_id FK CASCADE, plan_name, dev_log_path, plan_description) with indexes
- Added `code_chunks.functional_role` TEXT column via runtime migration
- Seeded 25 functional roles across 5 groups (web_layer, validation_pipeline, intelligence_layer, data_layer, infrastructure)
- Updated test_db.py EXPECTED_TABLES and EXPECTED_INDEXES

### Task 2 — Heuristic Classifier
- Created `src/classifier.py` with priority-ordered classification rules
- Priority chain: chunk_type overrides > decorator patterns > naming conventions > file path patterns > fallback ("utility")
- `classify_chunk()` for single chunks, `classify_project()` for bulk project classification
- All rules implemented as pre-compiled regex for performance

### Task 3 — Dev Log Parser + Provenance
- Created `src/provenance.py` with multi-pattern header search
- Handles bullet format (`- file.py -- description`) and table format (`| file.py | ... |`)
- Handles em-dash variant (Unicode U+2014)
- `parse_dev_logs()` extracts plan slug, description, and file paths from all .md files
- `ingest_provenance()` links parsed files to code_chunks via chunk_provenance table with dedup

### Task 4 — Pipeline Integration
- Wired CLASSIFY stage into `src/cycle.py` between EXTRACT and SCORE
- Wired PROVENANCE ingestion after CLASSIFY
- Both stages are non-fatal (scoring proceeds with NULL functional_role on failure)
- Added `DEV_LOG_PATHS` config to `src/config.py`

### Task 5 — Tests
- 22 classifier tests covering all priority levels, edge cases, and project-level classification
- 14 provenance tests covering bullet/table/emdash parsing, dev log parsing, ingestion, idempotency
- All 36 new tests pass

## Test Results
```
169 passed, 2 failed (pre-existing lab threshold tests)
```

## Key Implementation Decisions
1. Regex rules are pre-compiled at module level for performance
2. `classify_chunk()` returns None for module/test_case (not "utility") — these are structurally typed
3. Em-dash (U+2014) handling added to BULLET_PATTERN alongside double-dash
4. Provenance dedup uses (chunk_id, plan_name) pair check before INSERT

---

## Output Receipt
**Agent:** Anvil Developer
**Step:** 2 (Phase 7 Implementation)
**Status:** Complete

### What Was Done
Implemented all 5 tasks from the Phase 7 blueprint: schema additions with 25-role seed, heuristic classifier with 4-priority rule chain, dev log parser with multi-format support, pipeline integration as non-fatal CLASSIFY stage, and 36 tests.

### Files Deposited
- anvil/knowledge/development/phase7-classification-2026-04-01.md -- this dev log

### Files Created or Modified (Code)
- src/db.py -- added functional_roles table, chunk_provenance table, functional_role column, seed function, CRUD helpers
- src/classifier.py -- NEW, heuristic functional role classifier
- src/provenance.py -- NEW, dev log parser + provenance ingestion
- src/cycle.py -- added CLASSIFY + PROVENANCE stages between EXTRACT and SCORE
- src/config.py -- added DEV_LOG_PATHS config
- tests/test_db.py -- updated EXPECTED_TABLES and EXPECTED_INDEXES
- tests/test_classifier.py -- NEW, 22 tests
- tests/test_provenance.py -- NEW, 14 tests

### Decisions Made
- Pre-compiled regex for all classification rules (performance)
- module/test_case chunks return None from classifier (not "utility")
- Added em-dash support to provenance parser beyond blueprint spec
- Both new pipeline stages are non-fatal per blueprint

### Flags for CEO
- None

### Flags for Next Step
- QA should run classifier against live invoice-pulse data to verify role distribution
- QA should verify provenance ingestion against real dev logs in invoice-pulse
- The 2 pre-existing test_lab failures are unrelated to Phase 7 (threshold tuning)
