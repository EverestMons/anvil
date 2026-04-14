# Anvil Diagnostic — Coupling Hotspots Noise Profile
**Date:** 2026-04-14 | **Source:** diagnostic-coupling-hotspots-noise-2026-04-14.md

---

## (1) find_coupling_hotspots — Full Function, Line Range

**File:** `anvil/src/lab.py` — **Lines 118–161**

```python
def find_coupling_hotspots(conn, project_id: int, cycle_id: int) -> list[dict]:
    """Find highly coupled chunks, using role-specific thresholds."""
    min_threshold = min(
        (rt.get("coupling_hotspot_threshold", COUPLING_HOTSPOT_THRESHOLD)
         for rt in ROLE_THRESHOLDS.values()),
        default=COUPLING_HOTSPOT_THRESHOLD,
    )
    cur = conn.execute(
        "SELECT cc.id, cc.file_path, cc.name, hs.coupling_score, "
        "hs.composite_score, cc.functional_role "
        "FROM health_scores hs "
        "JOIN code_chunks cc ON hs.chunk_id = cc.id "
        "WHERE hs.cycle_id = ? AND hs.coupling_score >= ? "
        "ORDER BY hs.coupling_score DESC",
        (cycle_id, min_threshold),
    )
    results = []
    for r in cur.fetchall():
        role = r[5]
        role_thresh = ROLE_THRESHOLDS.get(role, {})
        threshold = role_thresh.get(
            "coupling_hotspot_threshold", COUPLING_HOTSPOT_THRESHOLD
        )
        if r[3] < threshold:
            continue

        chunk_id = r[0]
        in_cur = conn.execute(
            "SELECT COUNT(*) FROM chunk_dependencies WHERE target_chunk_id = ?",
            (chunk_id,),
        )
        out_cur = conn.execute(
            "SELECT COUNT(*) FROM chunk_dependencies WHERE source_chunk_id = ?",
            (chunk_id,),
        )
        inbound = in_cur.fetchone()[0]
        outbound = out_cur.fetchone()[0]

        results.append({
            "chunk_id": chunk_id, "file_path": r[1], "name": r[2],
            "coupling_score": r[3], "composite_score": r[4],
            "inbound": inbound, "outbound": outbound,
        })
    return results
```

**SQL WHERE clause (verbatim):**
```sql
WHERE hs.cycle_id = ? AND hs.coupling_score >= ?
```

No filter on `file_path`, `functional_role`, or `chunk_type`. Only cycle and score gates.

---

## (2) Structural Comparison to find_intent_gaps

`find_coupling_hotspots` vs the coupling sub-query in `find_intent_gaps` (lines 495–504):

| Attribute | find_coupling_hotspots | find_intent_gaps (coupling sub-query) |
|---|---|---|
| Number of queries | Single primary + 2 dependency-count sub-queries per row | Single query |
| Test file filter | **ABSENT** | `AND cc.file_path NOT LIKE 'tests/%'` (line 501) |
| functional_role filter | **ABSENT** (role used only for threshold selection) | **ABSENT** |
| Session/connection name filter | **ABSENT** | **ABSENT** |
| chunk_type filter | **ABSENT** | **ABSENT** |
| Fetches inbound/outbound counts | Yes (per-row sub-queries) | No |

**Summary:** `find_intent_gaps`'s coupling sub-query has the test file filter; `find_coupling_hotspots` has none at all. Neither filters SESSION_LIFECYCLE or CONNECTION_FACTORY names.

---

## (3) Top 30 Coupling Hotspot Rows (Live DB Query)

Query run against `anvil/anvil.db` (tables are `code_chunks` and `health_scores`, not `chunks`/`chunk_scores` as noted in the diagnostic plan):

```
SELECT cc.name, cc.file_path, cc.functional_role, hs.coupling_score, hs.composite_score
FROM code_chunks cc JOIN health_scores hs ON cc.id = hs.chunk_id
WHERE hs.coupling_score >= 0.9 ORDER BY hs.coupling_score DESC LIMIT 30
```

**Output:**
```
('execute', 'profile_ingestion.py', 'utility', 1.0, 0.4404)
('execute', 'profile_ingestion.py', 'utility', 1.0, 0.435)
('execute', 'profile_ingestion.py', 'utility', 1.0, 0.392)
('execute', 'profile_ingestion.py', 'utility', 1.0, 0.3921)
('execute', 'profile_ingestion.py', 'utility', 1.0, 0.3918)
('execute', 'profile_ingestion.py', 'utility', 1.0, 0.3929)
('execute', 'profile_ingestion.py', 'utility', 1.0, 0.3934)
('execute', 'profile_ingestion.py', 'utility', 1.0, 0.3932)
('execute', 'profile_ingestion.py', 'utility', 1.0, 0.2224)
('execute', 'profile_ingestion.py', 'utility', 1.0, 0.2224)
('execute', 'profile_ingestion.py', 'utility', 1.0, 0.2224)
('execute', 'profile_ingestion.py', 'utility', 1.0, 0.2224)
('execute', 'profile_ingestion.py', 'utility', 1.0, 0.2224)
('commit', 'profile_ingestion.py', 'utility', 0.9971, 0.2135)
('commit', 'profile_ingestion.py', 'utility', 0.9971, 0.2135)
('commit', 'profile_ingestion.py', 'utility', 0.997, 0.2135)
('commit', 'profile_ingestion.py', 'utility', 0.9969, 0.2135)
('commit', 'profile_ingestion.py', 'utility', 0.9969, 0.2135)
('commit', 'profile_ingestion.py', 'utility', 0.9962, 0.3841)
('commit', 'profile_ingestion.py', 'utility', 0.9957, 0.3837)
('commit', 'profile_ingestion.py', 'utility', 0.9956, 0.3842)
('close', 'profile_ingestion.py', 'utility', 0.9942, 0.2087)
('close', 'profile_ingestion.py', 'utility', 0.9942, 0.2087)
('close', 'profile_ingestion.py', 'utility', 0.994, 0.2087)
('close', 'profile_ingestion.py', 'utility', 0.9937, 0.2086)
('close', 'profile_ingestion.py', 'utility', 0.9937, 0.2086)
('close', 'profile_ingestion.py', 'utility', 0.9924, 0.3792)
('commit', 'profile_ingestion.py', 'utility', 0.9923, 0.3825)
('commit', 'profile_ingestion.py', 'utility', 0.9918, 0.3821)
('commit', 'profile_ingestion.py', 'utility', 0.9915, 0.4281)
```

**Observation:** All 30 rows are `execute`/`commit`/`close` methods from `profile_ingestion.py` with `functional_role = 'utility'`. Zero test files and zero connection factory names in the top 30. The genuine signal is entirely buried.

---

## (4) Noise Category Classification

**Across all 315 rows with coupling_score >= 0.9 (all cycles, all chunks):**

| Category | Criteria | Count |
|---|---|---|
| **TEST_FILE** | `file_path LIKE 'tests/%'` | **151** |
| **SESSION_LIFECYCLE** | name IN (execute, commit, close, rollback, begin) AND file_path matches session/ingestion patterns | **42** |
| **CONNECTION_FACTORY** | name IN (get_connection, get_session, get_db, _get_db, connect, get_engine) | **37** |
| **GENUINE** | None of the above | **98** |
| **TOTAL** | | **315** |

**Noise ratio: 69% of all rows are noise. Only 31% are genuine.**

**Top 30 classification:** 30/30 = SESSION_LIFECYCLE (execute×13, commit×10, close×7 — all `profile_ingestion.py`).

Test files (151 rows) are the largest noise category by volume but score lower, so they do not dominate the top 30 in the current dataset. SESSION_LIFECYCLE dominates the top slots because `execute`/`commit`/`close` on a shared session wrapper are called from virtually every function in the codebase — maximizing their coupling score.

---

## (5) functional_role Distribution

```
(None, 6610)
('utility', 1003)
('route_handler', 332)
('report_generator', 140)
('ingestion_orchestrator', 52)
('validation_gate', 50)
('data_model', 44)
('confidence_engine', 33)
('email_processor', 25)
('action_router', 24)
('document_manager', 22)
('data_parser', 21)
('data_guardian', 16)
('pattern_learner', 15)
('entity_matcher', 15)
('exit_interviewer', 13)
('batch_validator', 10)
('content_generator', 9)
('anomaly_detector', 9)
('pipeline_orchestrator', 8)
('address_normalizer', 7)
('lifecycle_tracker', 6)
('circuit_breaker', 5)
('validation_orchestrator', 1)
('audit_logger', 1)
```

**Assessment: `functional_role` is NOT usable as a standalone noise filter.**

- 6610 chunks (majority) have `NULL` functional_role — a role-based filter misses all of them.
- Session lifecycle methods (`execute`, `commit`, etc.) are classified as `'utility'` alongside 1003 other legitimate utility chunks. Filtering `functional_role = 'utility'` would be far too aggressive.
- No `session_lifecycle` or `connection_factory` role values exist in the current dataset.

**Conclusion:** functional_role cannot replace name-based noise filtering without a new role-assignment pass that does not currently exist.

---

## (6) NOT LIKE 'tests/%' Filter Coverage in find_intent_gaps

```
grep -n "NOT LIKE 'tests/%'" anvil/src/lab.py
```

Output:
```
449:        "AND cc.file_path NOT LIKE 'tests/%' "
501:        "AND cc.file_path NOT LIKE 'tests/%' "
554:        "AND cc.file_path NOT LIKE 'tests/%' "
```

**Count: 3 occurrences** — one in each of the three `find_intent_gaps` sub-queries:
- Line 449: coverage_gaps sub-query
- Line 501: coupling hotspots sub-query
- Line 554: complexity hotspots sub-query

The test file filter is fully and consistently applied within `find_intent_gaps`.

---

## (7) find_coverage_gaps and find_complexity_hotspots — Filter Audit

### find_coverage_gaps (lines 96–115)

Full WHERE clause:
```sql
WHERE hs.cycle_id = ? AND hs.coverage_score >= ?
AND hs.composite_score >= ? AND cc.chunk_type != 'test_case'
```

- Test file filter (`NOT LIKE 'tests/%'`): **ABSENT** — only `chunk_type != 'test_case'` present, which excludes test case chunks by type but does not exclude test files by path. A function defined in `tests/conftest.py` with `chunk_type = 'function'` would still pass.
- Session/connection noise filter: **ABSENT**

### find_complexity_hotspots (lines 208–247)

Full WHERE clause:
```sql
WHERE hs.cycle_id = ? AND hs.complexity_score >= ?
AND cc.project_id = ?
```

- Test file filter: **ABSENT**
- Session/connection noise filter: **ABSENT**

### Summary

| Function | Test File Filter | Session/Connection Filter |
|---|---|---|
| `find_coverage_gaps` | ✗ (chunk_type != test_case only) | ✗ |
| `find_coupling_hotspots` | ✗ | ✗ |
| `find_complexity_hotspots` | ✗ | ✗ |
| `find_intent_gaps` (coverage sub-query, line 449) | ✓ | ✗ |
| `find_intent_gaps` (coupling sub-query, line 501) | ✓ | ✗ |
| `find_intent_gaps` (complexity sub-query, line 554) | ✓ | ✗ |

All three generic finding functions are completely unfiltered for test files. No function anywhere filters SESSION_LIFECYCLE or CONNECTION_FACTORY names.

---

## (8) write_cycle_report Code Path Trace

`write_cycle_report` (line 813) receives the `findings` dict assembled in `run_lab()`:

```python
# run_lab() line 44:
coupling_hotspots = find_coupling_hotspots(conn, project_id, cycle_id)

# findings dict line 61:
findings = {
    ...
    "coupling_hotspots": coupling_hotspots,
    ...
}

# write_cycle_report line 857:
hotspots = findings.get("coupling_hotspots", [])
# → renders directly into the cycle report markdown table
```

**There is exactly one code path.** The cycle report's Coupling Hotspots table renders directly from `find_coupling_hotspots()` output. There is no separate SQL query in `write_cycle_report`. **Fixing `find_coupling_hotspots` will fully fix the cycle report coupling hotspots section.**

Confirmed: `cycle-12-findings-2026-04-14.md` shows test files and session methods in Coupling Hotspots because `find_coupling_hotspots` returns them unfiltered, and `write_cycle_report` renders all returned rows.

---

## (9) Recommendations

### Minimum Change Set

Four locations need filtering. The test file filter must be added to the three generic functions. SESSION_LIFECYCLE and CONNECTION_FACTORY filters must be added everywhere (generic functions + the coupling sub-query in `find_intent_gaps`).

**Noise targets:**
1. **TEST_FILE** — `file_path LIKE 'tests/%'` → suppress 151 rows (48%)
2. **SESSION_LIFECYCLE** — names: `execute`, `commit`, `close`, `rollback`, `begin` in session/ingestion wrapper files → suppress 42 rows (13%)
3. **CONNECTION_FACTORY** — names: `get_connection`, `get_session`, `get_db`, `_get_db`, `connect`, `get_engine` → suppress 37 rows (12%)

### Filter Level: SQL vs Python

**Recommendation: SQL for test file filter; shared Python helper for SESSION_LIFECYCLE + CONNECTION_FACTORY.**

Rationale:
- Test file filter is a single `LIKE` on an indexed column — cheap to push into SQL, eliminates 151/315 rows before any Python processing. Add `AND cc.file_path NOT LIKE 'tests/%'` to all three generic function WHERE clauses.
- Session/connection noise requires combined name × file_path heuristic. SESSION_LIFECYCLE names (`execute`, etc.) are legitimate outside session wrapper contexts. A Python-level helper can apply compound logic (name AND file_path pattern) without requiring a complex multi-condition SQL expression duplicated across 4+ locations.

### Shared Helper: YES — Strongly Recommended

**Recommend a shared `_is_noise_chunk(chunk: dict) -> bool` helper in `lab.py`.**

Called from:
1. `find_coupling_hotspots` post-fetch loop
2. `find_coverage_gaps` post-fetch loop (in addition to adding SQL test-file filter)
3. `find_complexity_hotspots` post-fetch loop (in addition to adding SQL test-file filter)
4. `find_intent_gaps` coupling sub-query result loop (already has test file SQL filter; add helper call for session/connection)
5. `find_intent_gaps` complexity sub-query result loop (same)

**Why shared helper over four separate WHERE clauses:**
- Single definition of what counts as noise — update once, applies everywhere
- Current divergence (intent_gaps has test filter, generics do not) proves that duplicated SQL strings drift. A helper cannot drift.
- Name-based compound logic (`name in set AND path contains pattern`) is readable as Python; it is fragile and verbose as embedded SQL string copies.
- Post-fetch filtering on already-score-filtered lists is negligible overhead.

**Proposed helper signature:**

```python
_SESSION_LIFECYCLE_NAMES = frozenset({"execute", "commit", "close", "rollback", "begin"})
_SESSION_LIFECYCLE_PATH_HINTS = ("profile_ingestion", "database", "_session", "_engine", "session_manager")
_CONNECTION_FACTORY_NAMES = frozenset({"get_connection", "get_session", "get_db", "_get_db", "connect", "get_engine"})

def _is_noise_chunk(chunk: dict) -> bool:
    name = chunk.get("name", "")
    path = chunk.get("file_path", "")
    if path.startswith("tests/"):
        return True
    if name in _CONNECTION_FACTORY_NAMES:
        return True
    if name in _SESSION_LIFECYCLE_NAMES:
        if any(pat in path for pat in _SESSION_LIFECYCLE_PATH_HINTS):
            return True
    return False
```

**Estimated effect after applying both SQL test filter + Python helper:**
- TEST_FILE suppressed: ~151 rows (−48%)
- SESSION_LIFECYCLE suppressed: ~42 rows (−13%)
- CONNECTION_FACTORY suppressed: ~37 rows (−12%)
- Total noise removed: ~230/315 rows (73%)
- Genuine signal retained: ~98 rows (100% of genuine hotspots, up from 31% signal-to-noise)

---

## Appendix: Diagnostic Notes

- The diagnostic plan specified table names `chunks` and `chunk_scores`. The actual DB uses `code_chunks` and `health_scores`. All queries were adapted accordingly; findings are unaffected.
- The `find_coupling_hotspots` function does not accept `project_id` in its WHERE clause — it filters only by `cycle_id`. This means it can return chunks from other projects if multiple projects share cycle IDs. Not a noise issue per se, but noted for completeness.
- The 315-row count includes multiple cycles (same chunk appearing in cycle N and cycle N+1). The noise categories hold per-cycle as well — the SESSION_LIFECYCLE chunks are the top scorers every cycle.
