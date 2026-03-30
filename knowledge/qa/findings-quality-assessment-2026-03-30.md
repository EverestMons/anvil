# Anvil Findings Quality Assessment — Cycle 1
**Date:** 2026-03-30
**Agent:** Anvil QA Analyst
**Source:** Cycle report at `knowledge/research/cycle-1-findings-2026-03-30.md`, cross-validation report at `knowledge/qa/first-cycle-validation-2026-03-30.md`

---

## 1. Coverage Gaps Quality — ACTIONABLE

**117 findings. Top items: validator gate functions, web route handlers, import functions.**

**(a) Actionability:** High. The Planner can write "add test coverage for `gate_9_accessorials` in `engines/validator.py`" directly — the target function, file, and risk rationale are all specified. No diagnostic needed first.

**(b) Accuracy:** High. Cross-validated in Step 2 — gate_7/8/9 confirmed to have zero test bindings. These are genuine gaps.

**(c) Priority:** Reasonable. The high-severity items (composite > 0.7) combine no-coverage with high volatility and high complexity — these genuinely are the riskiest untested code. Some lower-ranked items like `_get_db` (simple connection helpers) are flagged because they're untested AND volatile, which is technically correct but less urgent.

**Signal-to-noise:** ~80% signal. The top 30 are all genuinely high-risk untested functions. The bottom 20-30 include simple helpers that are untested but low-complexity — these are noise but not harmful (Planner can filter by composite score).

**Score: Actionable**

---

## 2. Coupling Hotspots Quality — PARTLY ACTIONABLE

**17 findings. Top items: profile_ingestion.py execute/commit/close, create_contract_tables, test fixtures.**

**(a) Actionability:** Medium. The "verify dependents" constraint is useful when modifying these functions, but it's a precaution rather than a fix. The Planner can include "verify these N dependents when modifying this module" in plans.

**(b) Accuracy:** High for production code. `execute` (4148 inbound) is genuinely the most-called function — it's a SQLite connection method used everywhere. `create_contract_tables` (212 outbound) genuinely creates most tables.

**(c) Priority:** Mixed. Three categories exist:
- **Expected infrastructure coupling** (profile_ingestion execute/commit/close, get_connection) — these SHOULD be highly coupled. Not risky, just important. Severity should be "informational."
- **Genuine fragile coupling** (create_contract_tables, _create_tables) — schema changes here cascade everywhere. High severity is correct.
- **Test fixture coupling** (test_main functions, _insert_invoice helpers) — test infrastructure, not production risk. Should be filtered out.

**Signal-to-noise:** ~40% signal. 7 of 17 are test fixtures, 3 are expected DB infrastructure. Only ~7 are genuinely worth tracking (create_contract_tables, extend_existing_tables, _create_tables, triangulate, and a few others).

**Recommendation for Cycle 2:** Filter test files from coupling hotspot analysis. Separate "expected infrastructure" from "fragile coupling" — high inbound on a utility function is expected; high outbound is the risk signal.

**Score: Partly Actionable**

---

## 3. Clone Candidates Quality — PARTLY ACTIONABLE

**381 pairs. Top items: DictRow duplication, _table_exists triplication, test fixture duplication.**

**(a) Actionability:** Medium. The production clones (`_table_exists` in 3 files, `DictRow` in test file) are real refactoring candidates. The Planner can write "consolidate `_table_exists` into a shared utility."

**(b) Accuracy:** High. Verified in Step 2 — top 1.0-similarity pairs are genuinely identical code.

**(c) Priority:** Mixed. Two categories:
- **Production duplicates** (~3-5 pairs): `_table_exists` in backtest.py, action_queue.py, reporting.py. DictRow copied into test file. These are worth consolidating.
- **Test fixture duplicates** (~370+ pairs): `db` fixtures, `app_client` fixtures, `_make_db` helpers intentionally duplicated across test files for isolation. Also many pairs from `test_auto_contract_phase2 2.py` which appears to be a literal file copy (note the space in the filename). These are acceptable or are file management issues, not code quality issues.

**Signal-to-noise:** ~5% signal. Out of 381 pairs, only ~15-20 are production code duplicates worth acting on. The vast majority are test fixtures.

**Recommendation for Cycle 2:** Filter test-to-test clone pairs from the report (or separate section). Flag files with spaces in names (`test_auto_contract_phase2 2.py`) as potential file cleanup issues. Raise SIMILARITY_THRESHOLD to 0.85 to reduce noise.

**Score: Partly Actionable**

---

## 4. Staleness Alerts Quality — PARTLY ACTIONABLE

**118 findings. Top items: confidence.py (10 functions), system_logger.py, circuit_breaker.py.**

**(a) Actionability:** Medium. "Dependencies updated but chunk unchanged" is a valid signal, but the appropriate action varies:
- For **confidence.py** (FROZEN module): staleness is expected and intentional. The module hasn't changed BECAUSE it's frozen. This is noise — not a bug.
- For **engines/backtest.py, circuit_breaker.py**: these may genuinely need review if their dependencies' interfaces changed.
- For **system_logger.py**: utility module that likely doesn't need updating when its callers change.

**(b) Accuracy:** Technically correct but semantically noisy. A function that imports a utility which changed doesn't necessarily need updating — it depends on whether the interface changed or just the implementation.

**(c) Priority:** Overweighted. 118 findings at staleness ≥ 0.6 is too many to be actionable. The confidence.py functions (10 of 118) are known-frozen and should not be flagged.

**Signal-to-noise:** ~30% signal. The confidence.py alerts are false positives (intentionally frozen). The system_logger.py alerts are mostly noise (utility module). ~35 findings are potentially worth investigating.

**Recommendation for Cycle 2:** Allow a "frozen modules" exclusion list in config.py — modules like confidence.py that are intentionally unchanged. Raise STALENESS_THRESHOLD to 0.8. Consider staleness only for functions with outbound call dependencies (not just import dependencies).

**Score: Partly Actionable**

---

## 5. Overall Assessment

### Signal-to-Noise Ratio
| Category | Findings | Signal | Noise | Ratio |
|---|---|---|---|---|
| Coverage gaps | 117 | ~95 | ~22 | 81% |
| Coupling hotspots | 17 | ~7 | ~10 | 41% |
| Clone candidates | 381 | ~20 | ~361 | 5% |
| Staleness alerts | 118 | ~35 | ~83 | 30% |
| Complexity hotspots | 76 | ~50 | ~26 | 66% |
| Co-change patterns | 503 | ~100 | ~403 | 20% |
| **Total** | **1212** | **~307** | **~905** | **25%** |

### Is Cycle 1 Ready for Planner Consumption?
**Yes, with filtering.** The coverage gaps and complexity hotspots are high-quality and directly actionable. The other categories need filtering before the Planner should consume them:

1. **Use now:** Coverage gaps (filter by composite > 0.7 for top priority)
2. **Use now:** Complexity hotspots (filter out test_main monoliths — those are test structure, not production risk)
3. **Use with caution:** Coupling hotspots (ignore test fixtures and expected DB infrastructure)
4. **Use with caution:** Staleness alerts (exclude frozen modules)
5. **Defer:** Clone candidates (too noisy — filter test-to-test pairs first)
6. **Defer:** Co-change patterns (informational for architect, not actionable for Planner)

### Threshold Adjustments for Cycle 2
| Threshold | Current | Recommended | Reason |
|---|---|---|---|
| HIGH_RISK_THRESHOLD | 0.6 | 0.65 | Reduce medium-noise findings |
| COVERAGE_GAP_THRESHOLD | 0.8 | 0.8 | Good as-is |
| COUPLING_HOTSPOT_THRESHOLD | 0.8 | 0.85 | Filter test fixtures |
| STALENESS_THRESHOLD | 0.6 | 0.8 | Reduce false positives |
| COMPLEXITY_THRESHOLD | 0.8 | 0.8 | Good as-is |
| COCHANGE_MIN_COUNT | 3 | 5 | Reduce noise |

---

## 6. Recommended Planner Integration Protocol

### Context Loading
When the Planner writes a plan for invoice-pulse, it should:
1. Read the latest cycle report's **Executive Summary** (5 lines — risk distribution + avg score)
2. Read the **Coverage Gaps** section (only entries with composite > 0.7)
3. Read the **Planner Constraints** section filtered to `coverage_required` and `verify_dependents` types with `severity: high`

### Translating Constraints into Plan Steps
- `coverage_required` → Add a test-writing step to the plan. Include the target function name and file path. The Developer agent writes the test; the QA agent verifies coverage improved.
- `verify_dependents` → Add a verification step after any modification to the flagged module. The Developer checks N dependents listed by Anvil.
- `refactor_candidate` → Only act on these when explicitly directed by CEO or when the plan naturally touches the duplicated code. Don't create standalone refactoring plans from Anvil findings.
- `investigation_needed` → Add as a diagnostic step only if the plan modifies the stale module's dependencies. Don't investigate proactively.

### When to Ignore Low-Severity Findings
- Ignore `severity: medium` constraints unless the plan already touches the relevant file
- Ignore clone candidates between test files entirely
- Ignore coupling hotspots for test_main functions
- Ignore staleness for modules on the frozen list

### Cycle Cadence
- Run Anvil cycle before writing any plan that touches > 3 files in invoice-pulse
- For single-file bug fixes, the Planner can reference the existing cycle report without a new run
- Compare cycles when the CEO asks "is the project healthier?"

---

## Output Receipt
**Agent:** Anvil QA Analyst
**Step:** Step 3
**Status:** Complete

### What Was Done
Assessed the quality of all 6 finding categories from Cycle 1 on actionability, accuracy, and priority. Produced signal-to-noise analysis (25% overall, 81% for coverage gaps). Recommended threshold adjustments for Cycle 2 and a specific Planner integration protocol.

### Files Deposited
- `anvil/knowledge/qa/findings-quality-assessment-2026-03-30.md`

### Files Created or Modified (Code)
- None

### Decisions Made
- Coverage gaps and complexity hotspots are directly actionable (Planner can consume now)
- Clone candidates and co-change patterns should be deferred (too noisy without filtering)
- Recommended 4 threshold adjustments for Cycle 2

### Flags for CEO
- Overall signal-to-noise is 25% — coverage gaps are the highest-value finding (81% signal). Recommend Planner consumes coverage_required constraints first.
- confidence.py staleness alerts are false positives (FROZEN module) — recommend adding a frozen modules exclusion list.
- `test_auto_contract_phase2 2.py` (space in filename) appears to be an accidental file copy — cleanup candidate.

### Flags for Next Step
- None — this is the final step of Phase 6.
