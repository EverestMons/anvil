# Anvil — Diagnostic: Pytest Symbol Binding Gap
**Date:** 2026-04-04 | **Type:** Diagnostic Research | **Source:** diagnostic-pytest-bindings-2026-04-04.md

---

## Q1 — Test Mapping Current Behavior

**Confirmed:** `"tests"` bindings are created through exactly ONE path.

In `src/parsers/python_parser.py:extract_symbols()` (lines 103-139), the `test_mappings` list is populated when:
1. The file is a test file (`basename.startswith("test_")`)
2. A function definition starts with `test_`

The mapping records `{"test_name": node.name, "tested_module": tested_module}` where `tested_module` is derived from the filename: `test_foo.py` → `"foo"`.

In `src/extractor.py:_store_file_symbols()` (lines 276-285), these are stored as:
- `binding_type = "tests"`
- `symbol_name = tested_module` (e.g., `"ingest"`, `"xml_parser"`)
- `target_chunk_id = NULL` (never set)

There is also `store_symbols()` (extractor.py line 325) which has the same logic but appears to be an unused alternative entry point. **No other path creates "tests" bindings.**

---

## Q2 — Call Bindings in Test Files

When a test file has `from web.gap_dashboard import _reshape_for_apply` and then calls `_reshape_for_apply(args)`:

**In `extract_symbols()`:**
1. `ImportFrom` node → import entry: `{"module": "web.gap_dashboard", "names": ["_reshape_for_apply"], "is_from": True}`
2. `Call` node → call entry: `{"caller": "test_something", "callee": "_reshape_for_apply"}`

**In `_store_file_symbols()`:**
1. Import stored on **module** chunk as `binding_type = "imports"`, `symbol_name = "web.gap_dashboard._reshape_for_apply"`
2. Call stored on **test_case** chunk as `binding_type = "calls"`, `symbol_name = "_reshape_for_apply"`
3. Test mapping stored on **test_case** chunk as `binding_type = "tests"`, `symbol_name = "gap_dashboard"` (module name only)

**Key finding:** The test_case chunk gets a `"calls"` binding with the specific function name (`"_reshape_for_apply"`), but the `"tests"` binding only points to the module name (`"gap_dashboard"`). There is no `"tests"` binding that references the specific production function being tested.

---

## Q3 — Coverage Scorer Input

`src/scorer.py:compute_coverage()` (lines 179-213) uses TWO queries, both looking ONLY at `binding_type = "tests"`:

**Query 1 — Direct target_chunk_id match (line 189-193):**
```sql
SELECT COUNT(*) FROM chunk_symbol_bindings
WHERE binding_type = 'tests' AND target_chunk_id = ?
```
This always returns 0 because `target_chunk_id` is never populated for tests bindings.

**Query 2 — Name-based fallback (line 198-206):**
```sql
SELECT COUNT(*) FROM chunk_symbol_bindings csb
JOIN code_chunks cc ON csb.chunk_id = cc.id
WHERE csb.binding_type = 'tests'
AND csb.symbol_name = (SELECT name FROM code_chunks WHERE id = ?)
AND cc.chunk_type = 'test_case'
```
This looks for tests bindings where `symbol_name` matches the **production chunk's name**. But tests bindings have `symbol_name = module_name` (e.g., `"ingest"`), not function names (e.g., `"process_batch"`).

**The scorer does NOT consider `"calls"` bindings from test chunks.** Only `"tests"` binding type is queried.

**Scoring logic:**
- 0 matches → coverage_score = 1.0 (no coverage, high risk)
- 1 match → coverage_score = 0.5
- 2+ matches → coverage_score = 0.2

---

## Q4 — Fixture Injection Pattern

**Confirmed: The current parser extracts ZERO information about pytest fixture parameters.**

When a test function is defined as `def test_foo(db, app_client):`, the parameters `db` and `app_client` appear in the AST as function arguments, not as `Call` nodes. The parser:
- Counts parameters via `compute_structural_metadata()` → `parameter_count` (numeric only)
- Does NOT extract parameter names as symbols
- Does NOT create any bindings for fixture references

The conftest fixtures are parsed as regular functions (chunk_type = "function"):
- `tests/conftest.py::db`
- `tests/conftest.py::app_client`
- `tests/conftest.py::seeded_db`
- `tests/conftest.py::_insert_invoice`
- `tests/conftest.py::_insert_contract`

There is no mechanism to link test_case chunks to the fixtures they use.

---

## Q5 — Quantify the Gap

### Test-Side Bindings (test_case chunks)
| Metric | Count |
|---|---|
| Total test_case chunks | 1,807 |
| test_case chunks WITH "tests" bindings | 1,783 (98.7%) |
| test_case chunks with calls but NO "tests" bindings | 0 |
| test_case chunks with neither tests nor calls | 24 |

The test-side binding rate is high — almost all test_case chunks get a "tests" binding via the filename convention.

### Production-Side Coverage (the actual gap)
| Metric | Count |
|---|---|
| Total production chunks (function/method/class) | 12,904 |
| Production chunks with coverage_score = 1.0 (NO coverage detected) | 12,834 (99.5%) |
| Production chunks with coverage_score < 1.0 | 70 (0.5%) |

**99.5% of production code is scored as having zero test coverage**, even though 1,807 test functions exist.

### Root Cause Analysis
The gap has TWO compounding causes:

1. **target_chunk_id is never set:** All 13,398 "tests" bindings have `target_chunk_id = NULL`. The scorer's first query (direct target match) always returns 0.

2. **Name mismatch in fallback:** "tests" bindings use `symbol_name = module_name` (e.g., `"ingest"`), but the scorer matches against the production chunk's `name` (e.g., `"process_batch"`). Only 9 production chunks accidentally have a name matching a tests symbol_name.

### Call-Based Coverage Potential
| Metric | Count |
|---|---|
| Unique callees from test_case chunks | 183 |
| Of those matching a production function name | 103 (56%) |

If "calls" from test_case chunks were counted as coverage, 103 production functions would gain coverage signal. However, many test calls are to framework methods (`execute`, `commit`, `get`, `post`) rather than production code.

### Test Helper Functions (edge case)
| Metric | Count |
|---|---|
| Non-test functions in test files | 231 |

These include fixtures (`db`, `app_client`, `seeded_db`), local helpers (`_make_db`, `_insert_invoice`, `_create_test_xlsx`), and utility functions (`is_setup_route`, `build_url`). Some of these call production code but are NOT test functions — they should not create "tests" bindings themselves.

---

## Q6 — Proposed Fix Validation

### The Proposed Fix
Enhance the pipeline so that when a test_case chunk calls a function defined in a non-test file, a `"tests"` binding is created (in addition to the existing `"calls"` binding), with `symbol_name` set to the production chunk's name and ideally `target_chunk_id` set to the production chunk's ID.

### Conflict Analysis

**Scorer (`compute_coverage`):** No conflict. The fix would populate either `target_chunk_id` (enabling Query 1) or use function-level `symbol_name` (enabling Query 2). Both paths are already coded and waiting for the data.

**Lab (`lab.py`):** No conflict. The lab reads `coverage_score` from `health_scores`, not raw bindings. Better scoring data flows through automatically.

**Dependency resolution (`resolve_dependencies`):** No conflict. It reads `"imports"` and `"calls"` bindings, not `"tests"`.

**Existing "tests" bindings:** The module-level bindings would remain. The fix adds function-level bindings alongside them — no removal needed.

### Edge Cases

1. **Test helpers calling production code:** Functions like `_make_db()` or `seed_invoice()` in test files are chunk_type = "function", not "test_case". The fix should key on `chunk_type = "test_case"` only, which naturally excludes helpers. ✅ Safe.

2. **Framework method calls:** Tests call `execute()`, `commit()`, `get()`, `post()` — these are SQLite/Flask methods, not production code. The fix should only create "tests" bindings when the callee resolves to a production chunk in the same project. The existing `resolve_dependencies` strategy (name lookup in `by_name`) provides the pattern. ✅ Needs filtering but pattern exists.

3. **Conftest fixtures:** Not visible as calls in the AST (they're parameter injection). A separate enhancement would be needed for fixture-based coverage. Out of scope for this fix. ⚠️ Known limitation, not a conflict.

4. **Duplicate bindings:** Multiple test functions calling the same production function would create multiple "tests" bindings for that production chunk. This is actually desirable — `compute_coverage` returns better scores (0.2) for 2+ tests. ✅ Correct behavior.

5. **Cross-project calls:** If a test imports from outside the project, those calls won't resolve to local chunks, so no spurious bindings. ✅ Safe.

### Recommended Implementation Location
The best insertion point is in `extractor.py:_store_file_symbols()` after line 273 (after storing "calls" bindings). For each call binding where:
- The caller chunk has `chunk_type = "test_case"`
- The callee resolves to a chunk with `chunk_type IN ("function", "method", "class")`
- The target chunk's `file_path` does NOT start with `"tests/"`

Create: `db.create_symbol_binding(conn, caller_chunk_id, target_chunk.name, "tests", target_chunk_id=target_chunk.id)`

This would give the scorer both the `target_chunk_id` (for Query 1) AND the correct `symbol_name` (for Query 2).

---

## Summary

The pytest bindings gap is a **data flow problem**, not a logic problem. The scorer correctly looks for "tests" bindings, but the extractor only creates module-level "tests" bindings (filename convention), never function-level ones. The fix is to use call resolution (already implemented for dependency resolution) to create function-targeted "tests" bindings when a test_case calls production code.

**Estimated impact:** Would add coverage signal for ~103 production functions (from 70 to ~170+ chunks with coverage_score < 1.0). The remaining ~12,700 production chunks would need either (a) indirect coverage tracing (test → helper → production) or (b) fixture-based coverage detection — both larger scope enhancements.

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** Step 1 (Investigation)
**Status:** Complete

### What Was Done
Investigated all 6 questions about the pytest symbol binding gap. Traced the full pipeline from test file extraction through coverage scoring. Quantified the gap: 99.5% of production chunks show no test coverage due to module-level-only "tests" bindings and never-populated target_chunk_id. Validated the proposed fix approach.

### Files Deposited
- `anvil/knowledge/research/pytest-bindings-diagnostic-2026-04-04.md` — full investigation findings (this file)

### Files Created or Modified (Code)
- None (diagnostic only)

### Decisions Made
- Recommended implementation location: `extractor.py:_store_file_symbols()` after the calls binding loop
- Recommended keying fix on `chunk_type = "test_case"` to exclude test helpers
- Recommended populating BOTH `target_chunk_id` and function-level `symbol_name`

### Flags for CEO
- The 99.5% coverage blind spot means ALL health scores currently have inflated coverage_score (1.0) for production code — this affects composite scores and lab findings across the board
- Fixture-based coverage (Q4) is a separate enhancement beyond this fix scope

### Flags for Next Step
- The fix should be implemented in `extractor.py:_store_file_symbols()`, not in the parser
- Existing module-level "tests" bindings should be preserved (backward compatible)
- After implementing, a re-extraction cycle is needed to populate the new bindings
- Consider adding a dedup check — the same test calling the same function shouldn't create duplicate "tests" bindings across cycles
