# Anvil Scorer Blueprint
**Agent:** Anvil Systems Analyst
**Date:** 2026-03-30
**Source:** PROJECT_BRIEF scoring dimensions, schema blueprint health_scores table, extractor QA data

---

## Design Decisions

### 1. Scoring granularity
**Decision:** Chunk-level scoring. Volatility data is per-file (git_changes), so volatility scores are computed per file and propagated to all chunks in that file. All other dimensions are per-chunk natively.

### 2. Chunks with no git history
**Decision:** Neutral score (0.5). New files with no git history are neither high-risk nor safe — they're unknown. Extreme scores (0.0 or 1.0) would distort the distribution.

### 3. Score direction convention
**Decision:** Higher score = higher risk (worse health). This is consistent across all dimensions:
- Volatility 1.0 = extremely volatile (many recent changes)
- Coverage 1.0 = no test coverage
- Complexity 1.0 = very complex
- Coupling 1.0 = highly coupled
- Staleness 1.0 = very stale
- Composite 1.0 = highest risk

### 4. Normalization approach
**Decision:** Percentile-based normalization within the project. For each dimension, rank all chunks, then score = rank / total_chunks. This ensures scores are always in 0.0-1.0 and gives a uniform distribution. Exception: coverage is binary/graded (not percentile-based).

### 5. Test result ingestion
**Decision:** Run pytest via subprocess, parse the summary line. Store pass/fail/skip counts + failed test names as JSON. If pytest fails to run, log warning and skip — don't crash the scorer.

---

## Function Specifications

### `score_project(conn, project_name, cycle_id) -> dict`

Main entry point.

**Logic:**
1. Look up project via `db.get_project()`. If not found, raise `ValueError`.
2. Query all non-module chunks: `SELECT * FROM code_chunks WHERE project_id = ? AND chunk_type != 'module'`.
3. Compute raw scores for each dimension across all chunks.
4. Normalize scores (percentile-based for volatility, coupling, staleness; formula-based for complexity; binary/graded for coverage).
5. Compute composite score per chunk.
6. Insert `health_scores` rows via `db.create_health_score()`.
7. Return summary:

```python
{
    "chunks_scored": int,
    "score_distribution": {
        "high_risk": int,    # composite >= 0.7
        "medium": int,       # 0.3 <= composite < 0.7
        "low_risk": int,     # composite < 0.3
    },
    "avg_composite": float,
}
```

---

### `compute_volatility(conn, project_id, file_path, git_window_weeks) -> float`

Compute volatility for a file (propagated to all chunks in that file).

**Formula:**
1. Query: `SELECT commit_date FROM git_changes WHERE project_id = ? AND file_path = ?`
2. If no commits → return 0.5 (neutral/unknown).
3. For each commit, compute recency_weight: `weight = 1.0 - (days_ago / (git_window_weeks * 7))`. Clamp to 0.0 minimum.
4. `raw_volatility = sum(recency_weights)` — weighted commit count favoring recent changes.
5. Return raw value (normalized later via percentile across all files).

---

### `compute_coverage(conn, chunk_id) -> float`

Compute test coverage for a chunk.

**Formula:**
1. Query: `SELECT COUNT(*) FROM chunk_symbol_bindings WHERE binding_type = 'tests' AND target_chunk_id = ?` — direct test bindings.
2. If count == 0 → also check: does any test_case chunk in the same project have a 'tests' binding matching this chunk's name?
   - Query: `SELECT COUNT(*) FROM chunk_symbol_bindings csb JOIN code_chunks cc ON csb.chunk_id = cc.id WHERE csb.binding_type = 'tests' AND csb.symbol_name = (SELECT name FROM code_chunks WHERE id = ?) AND cc.chunk_type = 'test_case'`
3. Graded scoring:
   - 0 test bindings → 1.0 (no coverage, highest risk)
   - 1 test binding → 0.5 (partial coverage)
   - 2+ test bindings → 0.2 (good coverage)
   - test_case chunks themselves → 0.0 (tests don't need test coverage)

---

### `compute_complexity(structural_metadata_json) -> float`

Compute complexity from structural metadata.

**Formula:**
1. Parse JSON: extract `cyclomatic_complexity`, `nesting_depth`, `parameter_count`.
2. If JSON is None or empty → return 0.5 (neutral).
3. Weighted combination:
   - `raw = 0.5 * cyclomatic_complexity + 0.3 * nesting_depth + 0.2 * parameter_count`
4. Sigmoid normalization to 0.0-1.0: `score = 1.0 / (1.0 + exp(-0.3 * (raw - 10)))`.
   - This centers at raw=10 (a function with complexity 10 scores ~0.5), with diminishing returns at extremes.
5. Return score.

---

### `compute_coupling(conn, chunk_id) -> float`

Compute coupling for a chunk.

**Formula:**
1. `outbound = SELECT COUNT(*) FROM chunk_dependencies WHERE source_chunk_id = ?`
2. `inbound = SELECT COUNT(*) FROM chunk_dependencies WHERE target_chunk_id = ?`
3. `raw_coupling = outbound + inbound`
4. Return raw value (normalized later via percentile).

---

### `compute_staleness(conn, chunk_id, file_path, project_id) -> float`

Compute staleness: how outdated is this chunk relative to its dependencies.

**Formula:**
1. Find chunk's last commit: `SELECT MAX(commit_date) FROM git_changes WHERE project_id = ? AND file_path = ?`
2. Find all dependencies: `SELECT target_chunk_id FROM chunk_dependencies WHERE source_chunk_id = ?`
3. For each dependency, find its file's last commit date.
4. Count dependencies modified more recently than the chunk.
5. If no dependencies → return 0.0 (nothing to be stale against).
6. If no git history → return 0.5 (neutral).
7. `raw_staleness = stale_dep_count / total_dep_count` — fraction of dependencies that are newer.
8. Return raw_staleness (already 0.0-1.0).

---

### `compute_composite(volatility, coverage, complexity, coupling, staleness, weights) -> float`

Weighted combination of dimension scores.

**Default weights (add to config.py):**
```python
SCORING_WEIGHTS = {
    "volatility": 0.25,
    "coverage": 0.25,
    "complexity": 0.20,
    "coupling": 0.15,
    "staleness": 0.15,
}
```

**Rationale:** Volatility and coverage weighted highest — high-churn code without tests is the #1 risk pattern per PROJECT_BRIEF (schema drift from parallel implementations). Complexity is next — deeply nested code is harder to maintain. Coupling and staleness are supporting signals.

**Formula:**
```python
composite = (weights["volatility"] * volatility +
             weights["coverage"] * coverage +
             weights["complexity"] * complexity +
             weights["coupling"] * coupling +
             weights["staleness"] * staleness)
```

Clamp to 0.0-1.0.

---

### `ingest_test_results(conn, project_name, cycle_id) -> dict`

Run pytest against the target project and store results.

**Logic:**
1. Resolve project path from `config.SCAN_TARGETS`.
2. Run: `subprocess.run(["python3", "-m", "pytest", project_path, "--tb=no", "-q"], capture_output=True, text=True, timeout=300)`.
3. Parse the summary line (last non-empty line): `"X passed, Y failed, Z skipped"` or `"X passed"`.
4. Extract failed test names from the output (lines starting with `FAILED`).
5. Store via `db.create_test_result(conn, project_id, run_date=now, total_tests=total, passed=passed, failed=failed, skipped=skipped, failed_test_names=json.dumps(failed_names), cycle_id=cycle_id)`.
6. If subprocess fails or timeout → return `{"status": "skipped", "reason": str}`.
7. Return `{"status": "complete", "total": N, "passed": N, "failed": N, "skipped": N}`.

---

## Config Additions

```python
# Scoring weights (higher score = higher risk)
SCORING_WEIGHTS = {
    "volatility": 0.25,
    "coverage": 0.25,
    "complexity": 0.20,
    "coupling": 0.15,
    "staleness": 0.15,
}
```

---

## How to Verify This Was Implemented Correctly

### 1. Score range
```sql
SELECT MIN(composite_score), MAX(composite_score), AVG(composite_score)
FROM health_scores WHERE cycle_id = 1;
```
All values in 0.0-1.0.

### 2. All chunks scored
```sql
SELECT COUNT(*) FROM health_scores WHERE cycle_id = 1;
```
Should match non-module chunk count (~3,247).

### 3. Top-10 highest risk
```sql
SELECT cc.file_path, cc.name, cc.chunk_type, hs.composite_score
FROM health_scores hs JOIN code_chunks cc ON hs.chunk_id = cc.id
WHERE hs.cycle_id = 1
ORDER BY hs.composite_score DESC LIMIT 10;
```
Should be plausible (high-volatility or uncovered or complex chunks).

### 4. Volatility correlation
Most volatile files in git_changes should have highest volatility_score chunks.

### 5. Coverage binary check
Chunks with no test bindings should have coverage_score > 0.8. test_case chunks should have coverage_score = 0.0.

### 6. Coupling correlation
Chunks with most dependency edges should have highest coupling_score.

### 7. Composite formula
Spot-check 3 chunks: manually compute `weights * dimensions` and verify composite matches.

### 8. Dimension independence
Each dimension column should have variance > 0 (not all same value).

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** Step 1
**Status:** Complete

### What Was Done
Designed the scorer blueprint with 8 functions: score_project (main entry), compute_volatility (recency-weighted commit frequency), compute_coverage (graded test binding count), compute_complexity (sigmoid-normalized structural metrics), compute_coupling (dependency edge count), compute_staleness (dependency freshness comparison), compute_composite (weighted combination), ingest_test_results (pytest runner). Specified formulas, normalization approaches, and default weights.

### Files Deposited
- `anvil/knowledge/architecture/scorer-blueprint-2026-03-30.md` — scorer blueprint

### Files Created or Modified (Code)
- None (blueprint only)

### Decisions Made
- Higher score = higher risk (consistent across all dimensions)
- Percentile normalization for volatility, coupling (ensures 0.0-1.0 distribution)
- Sigmoid normalization for complexity (centered at raw=10)
- Binary/graded for coverage (0, 1, 2+ test bindings)
- Neutral 0.5 for unknown data (no git history)
- Weights: volatility 0.25, coverage 0.25, complexity 0.20, coupling 0.15, staleness 0.15

### Flags for CEO
- Scoring weights are configurable in config.py — CEO can adjust after seeing first cycle results

### Flags for Next Step
- Add SCORING_WEIGHTS to config.py
- Percentile normalization requires computing all raw scores first, then ranking — two-pass approach
- pytest ingestion may fail on invoice-pulse if dependencies aren't installed — handle gracefully
