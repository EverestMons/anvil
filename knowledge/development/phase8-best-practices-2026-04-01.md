# Phase 8: Best Practices KB + Purpose-Aware Scoring — Dev Log
**Date:** 2026-04-01 | **Agent:** Anvil Developer | **Step:** 2
**Blueprint:** anvil/knowledge/architecture/phase8-best-practices-blueprint-2026-04-01.md

## What Was Built

### Task 1 — Best Practices Table + Seed
- Added `best_practices` table with severity CHECK constraint and UNIQUE(functional_role, pattern_name)
- Seeded 15 patterns: 3 each for route_handler, confidence_engine, validation_gate, utility, data_model
- CRUD helpers: create_best_practice(), get_best_practices_by_role()

### Task 2 — Role-Specific Scoring
- Added ROLE_SCORING_WEIGHTS config (8 role profiles, all sum to 1.0)
- Added ROLE_THRESHOLDS config (5 roles with per-role complexity and coupling thresholds)
- Modified scorer.py: one-line weight lookup (`ROLE_SCORING_WEIGHTS.get(role, SCORING_WEIGHTS)`)
- Modified lab.py: find_complexity_hotspots() and find_coupling_hotspots() use role-specific thresholds
- Lab functions pre-filter at minimum threshold in SQL, then apply per-role filtering in Python

### Task 3 — Web Research Hook
- Added research_best_practices() to lab.py
- Returns structured prompt for Claude Code to discover new patterns
- Lists existing practices to avoid duplicates

### Task 4 — Tests
- 16 tests covering: seed verification, CRUD, constraints, role-specific weight differences, threshold comparisons, weight sum validation, research hook

## Test Results
```
186 passed, 2 failed (pre-existing)
```

---

## Output Receipt
**Agent:** Anvil Developer
**Step:** 2 (Phase 8 Implementation)
**Status:** Complete

### Files Deposited
- anvil/knowledge/development/phase8-best-practices-2026-04-01.md -- this dev log

### Files Created or Modified (Code)
- src/db.py -- added best_practices table, seed data, CRUD helpers
- src/config.py -- added ROLE_SCORING_WEIGHTS and ROLE_THRESHOLDS
- src/scorer.py -- role-specific weight lookup in score_project()
- src/lab.py -- role-specific thresholds in hotspot finders, research_best_practices() hook
- tests/test_db.py -- updated EXPECTED_TABLES and EXPECTED_INDEXES
- tests/test_best_practices.py -- NEW, 16 tests

### Decisions Made
- Lab hotspot finders use min-threshold SQL pre-filter + Python per-role check (performance + correctness)
- All 8 role weight profiles verified to sum to 1.0

### Flags for CEO
- None

### Flags for Next Step
- QA should verify role-specific scoring produces different composites for same metrics
- QA should verify threshold adjustments (validation_gate at CC=15 not flagged, route_handler at CC=15 flagged)
