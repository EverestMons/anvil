# Bellows Daemon Archetype Implementation — QA Report

**Date:** 2026-06-09
**Plan:** `executable-anvil-bellows-daemon-archetype-impl-2026-06-09`
**Design:** `knowledge/architecture/bellows-daemon-archetype-design-2026-06-09.md`
**DEV Log:** `knowledge/development/bellows-daemon-archetype-impl-2026-06-09.md`
**Verdict:** PASS

---

## Deliverable Verification (Rule 17)

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `src/archetypes/daemon.py` | New file: 13 roles, 33 name rules, 12 file_path rules | ✅ | grep: roles=13, name_rules=33, file_path_rules=12 |
| `src/archetypes/__init__.py` | daemon import added | ✅ | Line 3: `import src.archetypes.daemon  # noqa: F401` |
| `src/config.py` | bellows archetype flipped to daemon | ✅ | Line 21: `"archetype": "daemon"` |
| `tests/test_daemon_archetype.py` | New file: 8 daemon tests | ✅ | 8/8 passed in full suite |
| `get_archetype("daemon")` returns definition | 13-role ArchetypeDefinition | ✅ | name=daemon, roles=13 |

Evidence: `evidence/anvil-bellows-daemon-archetype-impl-2026-06-09/deliverable_grep.txt`

---

## Check 1 — Invoice-Pulse Classify-Identity (Additive Regression Gate)

| Metric | BP2 Baseline | BP3 (post-daemon) | Match |
|---|---|---|---|
| Row set | code_chunks JOIN health_scores, cycle 20 | Same | ✅ |
| Row count | 3688 | 3688 | ✅ |
| Classify-only hash | `59cc0d80781ef03d8b8633c1bf605f578e9143be2503a221b5d39e449ba33078` | `59cc0d80781ef03d8b8633c1bf605f578e9143be2503a221b5d39e449ba33078` | ✅ |

**RESULT: PASS** — invoice-pulse classify-only hash is byte-identical to BP2 baseline. The daemon archetype addition is purely additive; flask_service classification is untouched.

Evidence: `evidence/anvil-bellows-daemon-archetype-impl-2026-06-09/ip_classify_hash.txt`

---

## Check 2 — Bellows Classification Distribution

| Metric | Threshold | Actual | Status |
|---|---|---|---|
| Non-utility rate | >= 80% | 84.5% (131/155) | ✅ |
| Invalid roles (not in daemon ROLES) | 0 | 0 | ✅ |
| Utility residual = test helpers only | Yes | Yes (24 chunks, all in tests/) | ✅ |

Role distribution matches design projection exactly:

| Role | Count | % |
|---|---|---|
| plan_dispatcher | 25 | 16.1% |
| utility | 24 | 15.5% |
| gate_checker | 21 | 13.5% |
| notifier | 19 | 12.3% |
| verdict_handler | 13 | 8.4% |
| cli_script | 12 | 7.7% |
| plan_validator | 10 | 6.5% |
| agent_lifecycle | 10 | 6.5% |
| plan_parser | 7 | 4.5% |
| worktree_manager | 6 | 3.9% |
| cache_manager | 4 | 2.6% |
| config_loader | 2 | 1.3% |
| data_model | 2 | 1.3% |

**RESULT: PASS** — 84.5% non-utility classification rate exceeds 80% threshold. All assigned roles are in the daemon ROLES list. All 24 utility residual chunks are test helpers (22 in tests/*.py, 2 pytest fixtures in tests/conftest.py).

Evidence: `evidence/anvil-bellows-daemon-archetype-impl-2026-06-09/bellows_distribution.txt`

---

## Check 3 — Full Test Suite

**Command:** `python3 -m pytest tests/ -v`
**Result:** 256 passed in 2.40s

**Baseline:** 248 tests (BP2). Post-BP3: 256 tests (+8 from `test_daemon_archetype.py`).

**RESULT: PASS** — all 256 tests green.

Evidence: `evidence/anvil-bellows-daemon-archetype-impl-2026-06-09/pytest_full.txt`

---

## Check 4 — Registry Wiring

| Check | Expected | Actual | Status |
|---|---|---|---|
| `get_archetype("daemon")` returns definition | 13-role ArchetypeDefinition | name=daemon, roles=13 | ✅ |
| Both archetypes registered | flask_service + daemon | [daemon, flask_service] | ✅ |
| Daemon role names complete | 13 names | All 13 present | ✅ |

**RESULT: PASS** — daemon archetype correctly wired and both archetypes registered.

Evidence: `evidence/anvil-bellows-daemon-archetype-impl-2026-06-09/registry.txt`

---

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/anvil/.bellows-worktrees/anvil-bellows-daemon-archetype-impl-2026-06-09/knowledge/qa/evidence/anvil-bellows-daemon-archetype-impl-2026-06-09/
Files verified: 5
```

---

## Output Receipt
**Agent:** Anvil QA Analyst
**Step:** 2 (QA)
**Status:** Complete

### What Was Done
Verified all BP3 daemon archetype deliverables. Invoice-pulse classify-only hash matches BP2 baseline (byte-identical, 3688 rows). Bellows classifies at 84.5% non-utility under daemon archetype (131/155 chunks). All 256 tests pass. Both archetypes registered correctly.

### Files Deposited
- `knowledge/qa/2026-06-09-bellows-daemon-archetype-impl-qa.md` — this QA report
- `knowledge/qa/evidence/anvil-bellows-daemon-archetype-impl-2026-06-09/` — 5 evidence files

### Files Created or Modified (Code)
- None (QA only)

### Decisions Made
- Classify-only hash scope uses code_chunks JOIN health_scores (same row set as BP2 harness), hashing (file_path, name, functional_role) only
- conftest.py fixtures classified as test helpers (they reside in tests/)

### Flags for CEO
- None

### Flags for Next Step
- None
