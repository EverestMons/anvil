# Archetype-ization + flask_service Migration — Dev Log

**Date:** 2026-06-09
**Plan:** `executable-anvil-archetype-flask-service-migration-2026-06-09`
**Blueprint:** `knowledge/architecture/archetype-flask-service-migration-blueprint-2026-06-09.md`

## Summary

Implemented the archetype pattern: all project-type-specific rules (classification, scoring weights, thresholds, best practices, detection checks) are now encapsulated in `ArchetypeDefinition` dataclasses registered in a central registry. The existing invoice-pulse / flask-service rules were migrated 1:1 into `src/archetypes/flask_service.py`. Hardcoded seeds removed from `db.py`; seeding now happens per-cycle via `seed_archetype_data()`. `SCAN_TARGETS` refactored from flat path strings to `{path, language, archetype}` dicts.

**Scope:** Archetype pattern + flask_service migration. No new archetypes added.

## Changes

### New Files

1. **`src/classifier_registry.py`** — `ArchetypeDefinition` dataclass (10 fields: name, roles, decorator_rules, name_rules, file_path_rules, scoring_weights, role_thresholds, best_practices, content_checks, structural_checks). Registry dict `ARCHETYPES` + `register_archetype()` / `get_archetype()`.

2. **`src/archetypes/__init__.py`** — Package init that imports flask_service to trigger registration.

3. **`src/archetypes/flask_service.py`** — Complete flask_service archetype: 4 decorator rules, 21 name rules, 30 file path rules, 25 roles (5 groups), 8 scoring weight profiles, 5 role thresholds, 15 best practices, 8 content check groups, 1 structural check group. All migrated 1:1 from prior module globals.

4. **`tests/test_classifier_registry.py`** — 8 tests: registry lookup, unknown archetype error, classify_chunk uses archetype rules, fallback to utility, init_db seeds nothing, seed_archetype_data populates, seed_archetype_data idempotent.

### Modified Files

5. **`src/config.py`** — `SCAN_TARGETS` changed from `{"name": "path_string"}` to `{"name": {"path": "...", "language": "python", "archetype": "flask_service"}}`. Removed `ROLE_SCORING_WEIGHTS` and `ROLE_THRESHOLDS` (moved to archetype).

6. **`src/classifier.py`** — Full rewrite. Removed module-global rule lists. `classify_chunk(chunk_dict, archetype)` takes archetype parameter. `classify_project` loads archetype from SCAN_TARGETS internally.

7. **`src/scorer.py`** — `score_project(conn, project_name, cycle_id, archetype=None)` — weight lookup from archetype. `ingest_test_results` updated for dict SCAN_TARGETS.

8. **`src/cycle.py`** — Added `seed_archetype_data(conn, archetype)` for idempotent INSERT OR IGNORE of roles + best practices. `run_cycle` loads archetype from SCAN_TARGETS, seeds, passes to score_project.

9. **`src/db.py`** — Removed `FUNCTIONAL_ROLE_SEEDS` (25 roles), `_seed_functional_roles`, `BEST_PRACTICE_SEEDS` (15 patterns), `_seed_best_practices`. Added archetype column migration to `init_db`.

10. **`src/detector.py`** — Full rewrite. `check_best_practice(chunk, practice, content_checks, structural_checks)` takes checks as parameters instead of using module globals.

11. **`src/lab.py`** — `find_coupling_hotspots` and `find_complexity_hotspots` accept optional `role_thresholds` parameter. `find_best_practice_deviations(conn, pid, cycle_id, archetype=None)` passes checks from archetype. `run_lab` loads archetype from SCAN_TARGETS.

12. **`src/scanner.py`** — `SCAN_TARGETS[project_name]` → `SCAN_TARGETS[project_name]["path"]`.

13. **`src/extractor.py`** — `SCAN_TARGETS.get(project_name)` → `SCAN_TARGETS.get(project_name, {}).get("path")`.

### Test File Updates

14. **`tests/test_classifier.py`** — Full rewrite. All classify_chunk calls pass archetype. SCAN_TARGETS patches use dict form. Fixture seeds via seed_archetype_data.

15. **`tests/test_scorer.py`** — SCAN_TARGETS patches use dict form. score_project calls pass archetype.

16. **`tests/test_cycle.py`** — SCAN_TARGETS patches use dict form.

17. **`tests/test_detector.py`** — Full rewrite. Module-level archetype extraction. check_best_practice calls pass content_checks/structural_checks. find_best_practice_deviations calls pass archetype.

18. **`tests/test_best_practices.py`** — Weights/thresholds sourced from archetype. Fixture seeds via seed_archetype_data.

19. **`tests/test_extractor.py`** — SCAN_TARGETS patch uses dict form.

20. **`tests/test_lab.py`** — Archetype imports + seeding. SCAN_TARGETS and deviation-finder patches.

21. **`tests/test_scanner.py`** — SCAN_TARGETS patches use dict form.

## Test Results

- **248 tests total**: 246 passed, 2 failed (pre-existing disk-space OSError in test_scanner prune tests, unrelated to this migration)
- New `test_classifier_registry.py`: 8/8 passed

## Design Decisions

- **Fallback chain preserved**: classify_chunk still returns "utility" as fallback for unmatched functions, None for module/test_case. No behavioral change.
- **Per-cycle seeding over init_db seeding**: Roles and best practices are now seeded at cycle start via INSERT OR IGNORE, making init_db archetype-agnostic.
- **Archetype as parameter vs. global lookup**: Functions that run within a cycle (classify_chunk, check_best_practice, score_project) take archetype as a parameter. Functions at the orchestration boundary (classify_project, run_lab, run_cycle) look up archetype from SCAN_TARGETS internally.
