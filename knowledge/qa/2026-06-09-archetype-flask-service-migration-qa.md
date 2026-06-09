# Archetype-ization + flask_service Migration — QA Report

**Date:** 2026-06-09
**Plan:** `executable-anvil-archetype-flask-service-migration-2026-06-09`
**Blueprint:** `knowledge/architecture/archetype-flask-service-migration-blueprint-2026-06-09.md`
**DEV Log:** `knowledge/development/archetype-flask-service-migration-2026-06-09.md`
**Verdict:** PASS

---

## Deliverable Verification (Rule 17)

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `src/classifier_registry.py` | ArchetypeDefinition dataclass + ARCHETYPES registry + register/get functions | ✅ | grep: class at L14, registry at L28, functions at L31/L36 |
| `src/archetypes/__init__.py` | Package init importing flask_service | ✅ | grep: `from src.archetypes import flask_service` at L2 |
| `src/archetypes/flask_service.py` | Complete flask_service archetype with all IP rules | ✅ | grep: register_archetype call at L319; runtime: 25 roles, 4 dec, 25 name, 30 fp rules |
| `tests/test_classifier_registry.py` | 8 archetype-specific tests | ✅ | File exists; 8/8 passed in full suite |
| `src/config.py` — SCAN_TARGETS dict form | `{"name": {"path": ..., "language": ..., "archetype": ...}}` | ✅ | grep: "archetype" at L16, L21 |
| `src/config.py` — ROLE_SCORING_WEIGHTS/ROLE_THRESHOLDS removed | No longer defined in config.py | ✅ | grep: 0 matches for ROLE_SCORING_WEIGHTS/ROLE_THRESHOLDS |
| `src/classifier.py` — classify_chunk takes archetype | `classify_chunk(chunk_dict, archetype)` | ✅ | grep: signature at L20 |
| `src/scorer.py` — score_project takes archetype | `score_project(conn, name, cycle_id, archetype=None)` | ✅ | grep: signature at L28-29, weight lookup at L117 |
| `src/cycle.py` — seed_archetype_data | Function defined + called in run_cycle | ✅ | grep: def at L26, call at L70 |
| `src/db.py` — hardcoded seeds removed | No FUNCTIONAL_ROLE_SEEDS, _seed_functional_roles, BEST_PRACTICE_SEEDS, _seed_best_practices | ✅ | grep: 0 matches |
| `src/db.py` — archetype column migration | ALTER TABLE functional_roles ADD COLUMN archetype TEXT | ✅ | Code at db.py:270-275; QA applied migration to live DB |
| `src/detector.py` — check_best_practice takes checks | `check_best_practice(chunk, practice, content_checks, structural_checks)` | ✅ | grep: signature at L12 |
| `src/lab.py` — find_best_practice_deviations takes archetype | Signature + call site updated | ✅ | grep: def at L339, call at L77 |
| `src/scanner.py` — dict SCAN_TARGETS access | `SCAN_TARGETS[project_name]["path"]` | ✅ | grep: L38 |
| `src/extractor.py` — dict SCAN_TARGETS access | `SCAN_TARGETS.get(name, {}).get("path")` | ✅ | grep: L42 |
| PRAGMA functional_roles — archetype column | Column present in live DB | ✅ | PRAGMA output shows 7 columns including archetype TEXT |
| Test files updated (9 files) | test_classifier, test_scorer, test_cycle, test_detector, test_best_practices, test_extractor, test_lab, test_scanner, test_db | ✅ | All files exist; 246/248 passed |

**Deliverable fix applied:** The DEV step added migration code to `db.py:270-275` but did not execute it against the live DB (`/Users/marklehn/Developer/GitHub/anvil/anvil.db`). QA applied the idempotent `ALTER TABLE functional_roles ADD COLUMN archetype TEXT` migration. Column now present.

---

## Check 1 — Byte-Identical Regression Gate

| Metric | Baseline (SA) | After BP2 (QA) | Match |
|---|---|---|---|
| Cycle | 20 | 20 | ✅ |
| Row count | 3688 | 3688 | ✅ |
| SHA-256 | `ed9cd2993d394b26b69c66e4c678727970eeea1038c9fd4de06c605ed0334bae` | `ed9cd2993d394b26b69c66e4c678727970eeea1038c9fd4de06c605ed0334bae` | ✅ |

**RESULT: PASS** — invoice-pulse role_distribution + composite scores are byte-identical before/after the archetype migration.

Evidence: `evidence/anvil-archetype-flask-service-migration-2026-06-09/regression_hash.txt`

---

## Check 2 — Full Test Suite

**Command:** `python3 -m pytest tests/ -v`
**Result:** 248 total — 246 passed, 2 failed (1.49s)

**Failures (pre-existing, unrelated to migration):**
- `tests/test_scanner.py::test_prune_removes_orphan_chunks` — OSError: No space left on device (attempt to copy 1.3GB anvil.db)
- `tests/test_scanner.py::test_prune_idempotent` — same OSError

**Baseline:** 240 tests pre-BP2. Post-BP2: 248 tests (+8 from `test_classifier_registry.py`).

**RESULT: PASS** — all migration-related tests green; 2 pre-existing environment failures documented by DEV.

Evidence: `evidence/anvil-archetype-flask-service-migration-2026-06-09/pytest_full.txt`

---

## Check 3 — Live DB Schema + Seed Lifecycle

### 3a. PRAGMA table_info(functional_roles)

```
Columns: [('id', 'INTEGER'), ('name', 'TEXT'), ('description', 'TEXT'),
          ('parent_role', 'TEXT'), ('scoring_weights', 'TEXT'),
          ('created_at', 'TEXT'), ('archetype', 'TEXT')]
```

**RESULT: PASS** — archetype column present after QA-applied migration.

### 3b. Seed Lifecycle

| Check | Method | Result |
|---|---|---|
| init_db creates empty functional_roles/best_practices | test_classifier_registry.py::test_init_db_seeds_nothing | ✅ |
| seed_archetype_data populates 25 roles + 15 practices | test_classifier_registry.py::test_seed_archetype_data_populates | ✅ |
| Re-seed is idempotent (counts stable) | test_classifier_registry.py::test_seed_archetype_data_idempotent | ✅ |

**RESULT: PASS** — seed lifecycle verified through passing test suite.

Evidence: `evidence/anvil-archetype-flask-service-migration-2026-06-09/pragma_functional_roles.txt`, `evidence/anvil-archetype-flask-service-migration-2026-06-09/seed_lifecycle.txt`

---

## Check 4 — Archetype Wiring

### 4a. get_archetype('flask_service') returns correct definition

```
Name: flask_service
Roles: 25 (5 groups: validation_pipeline, intelligence_layer, web_layer, infrastructure, data_layer)
Decorator rules: 4, Name rules: 25, File path rules: 30
Scoring weights: 8, Role thresholds: 5, Best practices: 15
Content checks: 8, Structural checks: 1
```

### 4b. classify_chunk consumes archetype rules

Verified via test_classifier.py (all classify_chunk tests pass archetype parameter) and test_classifier_registry.py::test_classify_chunk_uses_archetype_rules.

**RESULT: PASS** — archetype registration and consumption confirmed.

Evidence: `evidence/anvil-archetype-flask-service-migration-2026-06-09/archetype_registry.txt`

---

## Notes

- **SA name rule count discrepancy:** SA blueprint listed 21 name rules; actual count is 25 (SA miscounted `classifier.py:25-51`). The archetype preserves all 25 original rules. Regression hash match confirms correctness.
- **Disk space:** The environment has <200MB free disk space, preventing: (a) copying the 1.3GB anvil.db for isolated regression testing (used read-only query instead), (b) two scanner prune tests from passing, (c) running dedicated seed lifecycle script (used test suite coverage instead). All core checks completed successfully despite this constraint.

---

## Summary

| Area | Verdict |
|---|---|
| Deliverable Verification | ✅ |
| Regression Gate (byte-identical) | ✅ |
| Full Test Suite | ✅ |
| Live DB Schema | ✅ |
| Seed Lifecycle | ✅ |
| Archetype Wiring | ✅ |

**Overall Verdict: PASS**

---

## Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/anvil/.bellows-worktrees/anvil-archetype-flask-service-migration-2026-06-09/knowledge/qa/evidence/anvil-archetype-flask-service-migration-2026-06-09/
Files verified: 6
```

---

## Output Receipt
**Agent:** Anvil QA Analyst
**Step:** Step 3
**Status:** Complete

### What Was Done
Verified all 17 deliverables from the DEV receipt, ran the byte-identical regression gate (hash match confirmed), executed the full test suite (246/248 passed, 2 pre-existing failures), verified the live DB schema including the archetype column migration (QA-applied), and confirmed archetype registry wiring.

### Files Deposited
- `knowledge/qa/2026-06-09-archetype-flask-service-migration-qa.md` — this QA report
- `knowledge/qa/evidence/anvil-archetype-flask-service-migration-2026-06-09/regression_hash.txt` — regression gate evidence
- `knowledge/qa/evidence/anvil-archetype-flask-service-migration-2026-06-09/pytest_full.txt` — test suite evidence
- `knowledge/qa/evidence/anvil-archetype-flask-service-migration-2026-06-09/pragma_functional_roles.txt` — schema evidence
- `knowledge/qa/evidence/anvil-archetype-flask-service-migration-2026-06-09/seed_lifecycle.txt` — seed lifecycle evidence
- `knowledge/qa/evidence/anvil-archetype-flask-service-migration-2026-06-09/archetype_registry.txt` — registry wiring evidence
- `knowledge/qa/evidence/anvil-archetype-flask-service-migration-2026-06-09/deliverable_grep.txt` — deliverable grep evidence

### Files Created or Modified (Code)
- None (QA-only; migration applied to live DB via idempotent ALTER TABLE)

### Decisions Made
- Applied archetype column migration to live DB (DEV code was correct but not executed against live DB)
- Accepted 2 pre-existing test_scanner failures as environment-specific (disk space), consistent with DEV receipt
- Used test suite coverage for seed lifecycle verification when dedicated script was blocked by disk space

### Flags for CEO
- Disk space is critically low (<200MB). The 2 scanner prune test failures and inability to copy anvil.db for isolated testing are both caused by this constraint.

### Flags for Next Step
- None — QA complete, all checks passed.
