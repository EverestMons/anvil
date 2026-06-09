# Bellows Daemon Archetype Implementation — Dev Log
**Date:** 2026-06-09 | **Agent:** Anvil Developer | **Plan:** BP3 daemon-archetype-impl

## Design Reference
`knowledge/architecture/bellows-daemon-archetype-design-2026-06-09.md` (BP3 diagnostic, Complete)

## Pre-Edit Verification (Rule 39)
All V1-V6 verification blocks passed before any edits:

| # | Claim | Expected | Actual | Status |
|---|---|---|---|---|
| V1 | Bellows project id=2 | 2 | 2 | PASS |
| V2 | Total chunks = 3695 | 3695 | 3695 | PASS |
| V3 | Classifiable = 155 | 155 | 155 | PASS |
| V4 | All classifiable = utility | utility\|155 | utility\|155 | PASS |
| V5 | No daemon archetype | False | False | PASS |
| V6 | bellows archetype = flask_service | flask_service | flask_service | PASS |

## Implementation Summary

Created the daemon archetype per design Sections 1-5, mirroring `flask_service.py` structure exactly:

- **13 roles** across 4 groups (orchestration, governance, configuration, infrastructure + interface)
- **33 name rules** (design header says 34 but code block has 33 — faithfully matched code block)
- **12 file_path rules**
- **0 decorator rules** (empty — daemon has no decorator-based routing)
- **8 scoring weight profiles** (plan_dispatcher, gate_checker, verdict_handler, agent_lifecycle, worktree_manager, notifier, plan_validator, utility)
- **6 role threshold sets** (plan_dispatcher, gate_checker, verdict_handler, agent_lifecycle, worktree_manager, utility)
- **8 best practice rules** across 5 roles (gate_checker, plan_dispatcher, worktree_manager, verdict_handler, data_model, utility)
- **3 content check practice IDs** (idempotent_schema, append_only_ledger, pure_functions)
- **1 structural check practice ID** (structured_gate_return)

## Files Modified

### New Files
- `src/archetypes/daemon.py` — daemon archetype definition with all rules, scoring, and best practices
- `tests/test_daemon_archetype.py` — 8 tests: registration, structure, role completeness, classification samples

### Modified Files
- `src/archetypes/__init__.py` — added `import src.archetypes.daemon  # noqa: F401`
- `src/config.py` — flipped `SCAN_TARGETS["bellows"]["archetype"]` from `"flask_service"` to `"daemon"`

## Test Results
256 passed (248 existing + 8 new daemon archetype tests) in 3.63s. Full green.

## Scope Compliance
Modified only the 4 files specified in the plan (2 new, 2 edited). No changes to flask_service.py, classifier.py, scorer.py, db.py, or any invoice-pulse-affecting logic.

## Notes for QA
- Design header says "34 name rules" but the authoritative code block lists 33 rules. Implementation matches the code block.
- Invoice-pulse regression and bellows classification distribution verification are QA Step 2 responsibilities.

---
## Output Receipt
**Agent:** Anvil Developer
**Step:** 1 (DEV)
**Status:** Complete

### What Was Done
Implemented the daemon archetype per BP3 design. Created daemon.py with 13 roles, 33 name rules, 12 file_path rules, 8 scoring profiles, 6 role thresholds, 8 best practices, 3 content checks, 1 structural check. Registered in __init__.py, flipped bellows SCAN_TARGET to daemon. All 256 tests pass.

### Files Deposited
- `knowledge/development/bellows-daemon-archetype-impl-2026-06-09.md` — this dev log

### Files Created or Modified (Code)
- `src/archetypes/daemon.py` — new daemon archetype definition (13 roles, 33 name rules, 12 file_path rules, scoring, best practices)
- `src/archetypes/__init__.py` — added daemon import
- `src/config.py` — bellows archetype flipped from flask_service to daemon
- `tests/test_daemon_archetype.py` — 8 new daemon archetype tests

### Decisions Made
- Matched design code block (33 name rules) over design header text (34) — code block is authoritative

### Flags for CEO
- None

### Flags for Next Step
- QA must verify invoice-pulse classify-only hash equals BP2 baseline 59cc0d80781ef03d8b8633c1bf605f578e9143be2503a221b5d39e449ba33078
- QA must verify bellows >=80% non-utility classification under daemon archetype
- Design name_rules count discrepancy (header 34 vs code 33) is cosmetic — does not affect classification
