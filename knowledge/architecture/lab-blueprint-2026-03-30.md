# Anvil Lab Blueprint
**Agent:** Anvil Systems Analyst
**Date:** 2026-03-30
**Source:** PROJECT_BRIEF Lab section, scorer QA data (3247 chunks, 29 high-risk)

---

## Design Decisions

### 1. Lab scope — findings only, not plans
**Decision:** The Lab produces findings and constraints. The Planner turns them into plans. Anvil is a data source, not a planning authority.

### 2. Co-change similarity
**Decision:** Jaccard similarity for co-change pairs. `jaccard(A, B) = |commits_with_both| / |commits_with_A_or_B|`. More meaningful than raw overlap for files with different change frequencies.

### 3. Report format
**Decision:** Markdown for human reading, DB row for historical tracking, structured dict for Planner consumption. Three outputs from one Lab run.

---

## Function Specifications

### `run_lab(conn, project_name, cycle_id) -> dict`

Main entry point.

**Logic:**
1. Look up project. Load stats from prior phases.
2. Run all 6 finding functions.
3. Generate Planner constraints from findings.
4. Generate specialist update data.
5. Write cycle report markdown.
6. Create cycle_reports DB row.
7. Return summary:

```python
{
    "findings": {
        "coverage_gaps": int,
        "coupling_hotspots": int,
        "clone_candidates": int,
        "staleness_alerts": int,
        "complexity_hotspots": int,
        "cochange_patterns": int,
    },
    "total_findings": int,
    "constraints_generated": int,
    "report_path": str,
}
```

---

### `find_coverage_gaps(conn, project_id, cycle_id) -> list[dict]`

Untested high-risk chunks.

**Query:**
```sql
SELECT cc.id, cc.file_path, cc.name, cc.chunk_type,
       hs.composite_score, hs.coverage_score, hs.volatility_score
FROM health_scores hs
JOIN code_chunks cc ON hs.chunk_id = cc.id
WHERE hs.cycle_id = ? AND hs.coverage_score >= COVERAGE_GAP_THRESHOLD
  AND hs.composite_score >= HIGH_RISK_THRESHOLD
  AND cc.chunk_type != 'test_case'
ORDER BY hs.composite_score DESC
```

**Returns:** List of dicts with file_path, name, chunk_type, composite_score, coverage_score, volatility_score.

---

### `find_coupling_hotspots(conn, project_id, cycle_id) -> list[dict]`

Highly coupled chunks where changes cascade.

**Query:** Join health_scores with chunk_dependencies, count inbound edges.

```sql
SELECT cc.id, cc.file_path, cc.name, hs.coupling_score, hs.composite_score,
       (SELECT COUNT(*) FROM chunk_dependencies WHERE target_chunk_id = cc.id) as inbound,
       (SELECT COUNT(*) FROM chunk_dependencies WHERE source_chunk_id = cc.id) as outbound
FROM health_scores hs
JOIN code_chunks cc ON hs.chunk_id = cc.id
WHERE hs.cycle_id = ? AND hs.coupling_score >= COUPLING_HOTSPOT_THRESHOLD
ORDER BY hs.coupling_score DESC
```

**Also return:** List of dependent chunk names (via inbound dependencies) for each hotspot.

---

### `find_clone_candidates(conn, project_id, cycle_id) -> list[dict]`

Near-duplicate chunks from MinHash similarity.

**Query:**
```sql
SELECT cs.chunk_a_id, cs.chunk_b_id, cs.similarity_score,
       a.file_path as file_a, a.name as name_a,
       b.file_path as file_b, b.name as name_b
FROM chunk_similarities cs
JOIN code_chunks a ON cs.chunk_a_id = a.id
JOIN code_chunks b ON cs.chunk_b_id = b.id
WHERE cs.cycle_id = ? AND cs.similarity_score >= SIMILARITY_THRESHOLD
ORDER BY cs.similarity_score DESC
```

---

### `find_staleness_alerts(conn, project_id, cycle_id) -> list[dict]`

Chunks whose dependencies have been updated more recently.

**Query:**
```sql
SELECT cc.id, cc.file_path, cc.name, hs.staleness_score, hs.composite_score
FROM health_scores hs
JOIN code_chunks cc ON hs.chunk_id = cc.id
WHERE hs.cycle_id = ? AND hs.staleness_score >= STALENESS_THRESHOLD
ORDER BY hs.staleness_score DESC
```

For each stale chunk, also return the dependency that triggered staleness (which dependency file was modified more recently).

---

### `find_complexity_hotspots(conn, project_id, cycle_id) -> list[dict]`

Overly complex functions.

**Query:**
```sql
SELECT cc.id, cc.file_path, cc.name, cc.structural_metadata,
       hs.complexity_score, hs.composite_score
FROM health_scores hs
JOIN code_chunks cc ON hs.chunk_id = cc.id
WHERE hs.cycle_id = ? AND hs.complexity_score >= COMPLEXITY_THRESHOLD
ORDER BY hs.complexity_score DESC
```

Extract cyclomatic_complexity, nesting_depth, parameter_count from structural_metadata JSON.

---

### `find_cochange_patterns(conn, project_id) -> list[dict]`

Files that frequently change together in git commits.

**Logic:**
1. For each commit_hash in git_changes for this project, get the list of files.
2. For each pair of files in the same commit, increment a co-change counter.
3. Compute Jaccard similarity: `|co_commits| / |commits_with_A ∪ commits_with_B|`.
4. Return pairs where co-change count >= `COCHANGE_MIN_COUNT`.

**Returns:** List of dicts with file_a, file_b, cochange_count, jaccard_score.

---

### `generate_planner_constraints(conn, project_name, cycle_id) -> list[dict]`

Assemble findings into structured constraints for Planner consumption.

**Constraint structure:**
```python
{
    "type": "coverage_required",  # or verify_dependents, investigation_needed, refactor_candidate
    "target": "engines/validator.py::gate_9_accessorials",
    "reason": "Composite score 0.79, no test coverage, cyclomatic complexity 25",
    "severity": "high",  # high/medium/low
}
```

**Mapping:**
- Coverage gaps → type `coverage_required`, severity based on composite score
- Coupling hotspots → type `verify_dependents`, severity based on inbound count
- Clone candidates → type `refactor_candidate`, severity `medium`
- Staleness alerts → type `investigation_needed`, severity based on staleness score
- Complexity hotspots → type `refactor_candidate`, severity based on complexity score

---

### `generate_specialist_update_data(conn, project_id) -> dict`

Aggregate stats for specialist file syncs.

**Returns:**
```python
{
    "total_files": int,
    "total_functions": int,
    "total_classes": int,
    "total_methods": int,
    "total_test_cases": int,
    "total_dependencies": int,
    "total_similarity_pairs": int,
    "avg_composite_score": float,
    "high_risk_count": int,
    "top_10_complex": [{"name": str, "file": str, "complexity": int}],
    "top_10_coupled": [{"name": str, "file": str, "coupling_score": float}],
}
```

---

### `write_cycle_report(conn, project_name, cycle_id, findings, constraints, specialist_data, report_path) -> None`

Generate markdown report and DB row.

**Markdown structure:**
```markdown
# Anvil Cycle Report — {project_name} — Cycle {cycle_id}
**Date:** {date}

## Executive Summary
- Total chunks analyzed: N
- Risk distribution: N high, N medium, N low
- Top 5 riskiest chunks: [table]

## Coverage Gaps (N findings)
[table of untested high-risk chunks]

## Coupling Hotspots (N findings)
[table of highly coupled chunks with dependent lists]

## Clone Candidates (N pairs)
[table of similar chunk pairs]

## Staleness Alerts (N findings)
[table of stale chunks with dependency dates]

## Complexity Hotspots (N findings)
[table of complex functions with metrics]

## Co-Change Patterns (N pairs)
[table of file pairs with co-change counts]

## Planner Constraints (N total)
[structured list of constraints by type]

## Specialist Update Data
[aggregate metrics for specialist file sync]
```

**DB row:** `create_cycle_report(conn, project_id, cycle_number=cycle_id, started_at=..., completed_at=..., files_scanned=N, chunks_extracted=N, chunks_scored=N, findings_count=total, report_path=path)`.

---

## Config Additions

```python
# Lab thresholds
HIGH_RISK_THRESHOLD = 0.6       # composite score to flag as high risk
COVERAGE_GAP_THRESHOLD = 0.8    # coverage_score above which chunk is "untested"
COUPLING_HOTSPOT_THRESHOLD = 0.8 # coupling_score above which chunk is a hotspot
STALENESS_THRESHOLD = 0.6       # staleness_score above which chunk is flagged
COMPLEXITY_THRESHOLD = 0.8      # complexity_score above which chunk is flagged
COCHANGE_MIN_COUNT = 3          # minimum co-commits to flag a pair
```

---

## How to Verify This Was Implemented Correctly

### 1. Cycle report exists
File at `anvil/knowledge/research/cycle-{N}-findings-YYYY-MM-DD.md` exists and contains all sections.

### 2. DB row created
`SELECT * FROM cycle_reports WHERE cycle_number = 1` returns a row with non-zero counts.

### 3. Finding count plausibility
Against invoice-pulse (29 high-risk chunks from scorer):
- Coverage gaps: should include gate_7/8/9 from validator.py
- Coupling hotspots: should include heavily-connected modules
- Clone candidates: 381 similarity pairs exist, some should be above threshold
- At least 3 of 6 finding categories should have results

### 4. Constraint structure
Each constraint has: type, target, reason, severity. All required fields present.

### 5. Specialist data completeness
All expected fields present: total_files, total_functions, etc.

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** Step 1
**Status:** Complete

### What Was Done
Designed the Lab blueprint with 10 functions covering 6 finding types (coverage gaps, coupling hotspots, clone candidates, staleness alerts, complexity hotspots, co-change patterns), Planner constraint generation, specialist update data, and cycle report writing. Specified threshold configuration, output formats, and 5-point verification checklist.

### Files Deposited
- `anvil/knowledge/architecture/lab-blueprint-2026-03-30.md` — Lab blueprint

### Files Created or Modified (Code)
- None (blueprint only)

### Decisions Made
- Lab produces findings only, not plans (Planner is planning authority)
- Jaccard similarity for co-change detection (normalized for different change frequencies)
- Three output modes: markdown report, DB row, structured constraint dict
- 6 configurable thresholds in config.py

### Flags for CEO
- None

### Flags for Next Step
- Add 6 threshold constants to config.py
- Co-change analysis may be slow for projects with many commits × many files — optimize with SQL GROUP BY
- The markdown report uses `with open()` per CLAUDE.md rule #1
