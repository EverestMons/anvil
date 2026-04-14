# Anvil Phase 2.1 — Intent Cross-Reference Layer Blueprint
**Date:** 2026-04-14 | **Author:** Anvil Systems Analyst | **Status:** Complete

---

## 1. Purpose

Phase 2.1 adds `find_intent_gaps()` — an eighth Lab finding type that cross-references structural
signals from the existing Phase 1 pipeline against each project's stated intent (PROJECT_BRIEF.md
and domain glossary). The function assembles context packages deterministically; Claude Code applies
judgment when reviewing the output. Findings are written to `{project_path}/knowledge/anvil/` using
the Phase 2 finding format.

No new DB tables are required. Intent gaps are computed fresh each cycle from existing tables.

---

## 2. Function Signatures

```python
def find_intent_gaps(
    conn,
    project_name: str,
    project_path: str,
    top_n: int = 20,
) -> list[dict]:
    ...

def write_intent_audit(
    findings: list[dict],
    project_path: str,
    project_name: str,
) -> str:  # returns output_path
    ...
```

---

## 3. `find_intent_gaps()` — Detailed Design

### 3.1 Intent Loading

```python
brief_path    = os.path.join(project_path, "PROJECT_BRIEF.md")
glossary_path = os.path.join(project_path, "knowledge", "research", "domain-glossary.md")
```

- If **either file is missing**, log a warning via `logging.warning(...)` and `return []`.
- Both files are read with `with open(...) as f: content = f.read()`.
- The full text of each file is stored in local variables `brief_text` and `glossary_text`
  and included in every returned finding dict as `project_brief_text` and `domain_glossary_text`.
  This allows Claude Code to perform full intent cross-referencing when reviewing findings.

### 3.2 Project and Cycle Resolution

```python
project = db.get_project(conn, project_name)
if project is None:
    logging.warning("find_intent_gaps: project not found: %s", project_name)
    return []
project_id = project["id"]

# Resolve latest cycle_id for this project
cur = conn.execute(
    "SELECT MAX(hs.cycle_id) FROM health_scores hs "
    "JOIN code_chunks cc ON hs.chunk_id = cc.id "
    "WHERE cc.project_id = ?",
    (project_id,),
)
latest_cycle_id = cur.fetchone()[0]
if latest_cycle_id is None:
    logging.warning("find_intent_gaps: no health_scores found for project %s", project_name)
    return []
```

### 3.3 Structural Signal Queries

Three queries pull the top signals from the latest cycle. Slot allocation is:
- `n_coverage   = top_n // 3`
- `n_coupling   = top_n // 3`
- `n_complexity = top_n - n_coverage - n_coupling`

**Coverage gaps** (highest volatility + zero coverage):
```sql
SELECT cc.id, cc.name, cc.file_path, cc.functional_role, cc.structural_metadata,
       hs.composite_score, hs.volatility_score, hs.coverage_score
FROM health_scores hs
JOIN code_chunks cc ON hs.chunk_id = cc.id
WHERE hs.cycle_id = :cycle_id
  AND cc.project_id = :project_id
  AND hs.coverage_score >= 0.8
  AND cc.chunk_type != 'test_case'
ORDER BY hs.volatility_score DESC, hs.composite_score DESC
LIMIT :n_coverage
```

**Coupling hotspots** (highest coupling score):
```sql
SELECT cc.id, cc.name, cc.file_path, cc.functional_role, cc.structural_metadata,
       hs.composite_score, hs.coupling_score
FROM health_scores hs
JOIN code_chunks cc ON hs.chunk_id = cc.id
WHERE hs.cycle_id = :cycle_id
  AND cc.project_id = :project_id
ORDER BY hs.coupling_score DESC
LIMIT :n_coupling
```

**Complexity hotspots** (highest cyclomatic complexity, proxied by complexity_score):
```sql
SELECT cc.id, cc.name, cc.file_path, cc.functional_role, cc.structural_metadata,
       hs.composite_score, hs.complexity_score
FROM health_scores hs
JOIN code_chunks cc ON hs.chunk_id = cc.id
WHERE hs.cycle_id = :cycle_id
  AND cc.project_id = :project_id
  AND cc.structural_metadata IS NOT NULL
ORDER BY hs.complexity_score DESC
LIMIT :n_complexity
```

For complexity rows, parse `structural_metadata` JSON to extract `cyclomatic_complexity`,
`nesting_depth`, and `parameter_count` (default 0 if missing or parse fails).

### 3.4 Severity Mapping

Map `composite_score` to severity string (used in the `severity` field):

| composite_score | severity |
|---|---|
| >= 0.75 | `"CRITICAL"` |
| >= 0.60 | `"HIGH"` |
| >= 0.45 | `"MEDIUM"` |
| < 0.45 | `"LOW"` |

### 3.5 Output Dict Schema

Each finding dict **must** contain exactly these keys (required by test contract and QA):

| Key | Type | Description |
|---|---|---|
| `finding_type` | str | Always `"intent_gap"` |
| `severity` | str | `"CRITICAL"`, `"HIGH"`, `"MEDIUM"`, or `"LOW"` |
| `title` | str | Short human-readable title (see templates below) |
| `what` | str | Structural description of the signal |
| `why_it_matters` | str | Impact statement |
| `what_needs_discovering` | str | Diagnostic question |
| `success_looks_like` | str | Acceptance criterion |
| `diagnostic_type` | str | One of: `"Fix"`, `"Clarification"`, `"Knowledge gap"`, `"Architecture check"` |
| `chunk_ids` | list[int] | List of related chunk IDs (single-element for all current signals) |

**Additional context payload keys** (not in Phase 2 finding format, but required for Claude Code review):

| Key | Type | Description |
|---|---|---|
| `signal_type` | str | `"coverage_gap"`, `"coupling_hotspot"`, or `"complexity_hotspot"` |
| `chunk_name` | str | Chunk name from `code_chunks.name` |
| `chunk_file` | str | Relative file path |
| `functional_role` | str or None | Chunk's assigned functional role |
| `composite_score` | float | From health_scores |
| `project_brief_text` | str | Full content of PROJECT_BRIEF.md |
| `domain_glossary_text` | str | Full content of domain-glossary.md |

### 3.6 Field Templates by Signal Type

All fields are populated deterministically from the structural signal data. No LLM calls.

#### coverage_gap

```python
{
    "finding_type": "intent_gap",
    "severity": severity_from_composite(composite_score),
    "title": f"{name} ({file_path}) — uncovered high-volatility {chunk_type}",
    "what": (
        f"Function `{name}` in `{file_path}` has zero test coverage "
        f"(coverage_score={coverage_score:.2f}) and a volatility score of "
        f"{volatility_score:.2f}, indicating frequent change with no test safety net. "
        f"Functional role: {functional_role or 'unclassified'}."
    ),
    "why_it_matters": (
        f"High-volatility, untested code is the highest-risk class of finding. "
        f"Changes to `{name}` could introduce regressions with no test signal. "
        f"Composite score: {composite_score:.2f}."
    ),
    "what_needs_discovering": (
        f"Does `{name}` perform logic critical to the project's core goals "
        f"(as described in PROJECT_BRIEF)? If so, what scenarios does it need "
        f"to handle that are currently untested?"
    ),
    "success_looks_like": (
        f"Tests exist for `{name}` covering its primary execution paths, "
        f"or the function is confirmed non-critical and the gap is documented."
    ),
    "diagnostic_type": "Fix",
    "chunk_ids": [chunk_id],
}
```

#### coupling_hotspot

```python
{
    "finding_type": "intent_gap",
    "severity": severity_from_composite(composite_score),
    "title": f"{name} ({file_path}) — high-coupling node (coupling_score={coupling_score:.2f})",
    "what": (
        f"Chunk `{name}` has coupling score {coupling_score:.2f}. "
        f"It is a high-connectivity node in the dependency graph. "
        f"Functional role: {functional_role or 'unclassified'}. "
        f"Composite score: {composite_score:.2f}."
    ),
    "why_it_matters": (
        f"High-coupling nodes are high-blast-radius targets — changes propagate to "
        f"many dependents. If this node's behavior is ambiguous or undocumented, "
        f"that ambiguity ripples through all callers."
    ),
    "what_needs_discovering": (
        f"Does `{name}` represent a stable, well-understood abstraction? "
        f"Does its behavior align with what the domain glossary implies for "
        f"its role ({functional_role or 'unclassified'})?"
    ),
    "success_looks_like": (
        f"The coupling is understood and justified by the project's architecture, "
        f"or the node is refactored to reduce blast radius."
    ),
    "diagnostic_type": "Architecture check",
    "chunk_ids": [chunk_id],
}
```

#### complexity_hotspot

```python
{
    "finding_type": "intent_gap",
    "severity": severity_from_composite(composite_score),
    "title": (
        f"{name} ({file_path}) — high cyclomatic complexity "
        f"(complexity_score={complexity_score:.2f}, cyclomatic={cyclomatic_complexity})"
    ),
    "what": (
        f"Function `{name}` has complexity score {complexity_score:.2f} "
        f"with cyclomatic complexity {cyclomatic_complexity}, "
        f"nesting depth {nesting_depth}, and {parameter_count} parameters. "
        f"Functional role: {functional_role or 'unclassified'}."
    ),
    "why_it_matters": (
        f"High-complexity code is harder to reason about and more likely to "
        f"contain latent bugs, especially in domain-critical paths. "
        f"Composite score: {composite_score:.2f}."
    ),
    "what_needs_discovering": (
        f"Does `{name}` encode complex business rules that belong in this function, "
        f"or has incidental complexity accumulated over time? Does this function's "
        f"complexity align with the project's stated domain goals?"
    ),
    "success_looks_like": (
        f"The function is refactored to reduce complexity, or its complexity is "
        f"justified and documented as intentional domain logic."
    ),
    "diagnostic_type": "Fix",
    "chunk_ids": [chunk_id],
}
```

---

## 4. `write_intent_audit()` — Detailed Design

### 4.1 Directory and File

```python
audit_dir   = os.path.join(project_path, "knowledge", "anvil")
os.makedirs(audit_dir, exist_ok=True)
today       = datetime.now(timezone.utc).strftime("%Y-%m-%d")
output_path = os.path.join(audit_dir, f"audit-findings-{today}.md")
```

### 4.2 Output Format

Findings are grouped and sorted by severity order: CRITICAL → HIGH → MEDIUM → LOW.
Each finding uses the Phase 2 canonical format from the roadmap:

```markdown
# Anvil Audit Findings — {project_name}
**Date:** {today}  |  **Total findings:** {N}  |  **Source:** find_intent_gaps()

---

## CRITICAL — {title}

**What:** {what}

**Why it matters:** {why_it_matters}

**What needs to be discovered:** {what_needs_discovering}

**Success looks like:** {success_looks_like}

**Diagnostic type:** {diagnostic_type}

---
```

### 4.3 File Write

Always use `with open(output_path, "w") as f: f.write(content)`. Never bash heredocs.
Function returns `output_path` (str).

---

## 5. Integration into `run_lab()`

### 5.1 Changes to `run_lab()`

After the existing `bp_deviations = find_best_practice_deviations(...)` call:

```python
# Phase 2.1 — Intent gaps
project_path = project.get("path", "")
intent_gaps = []
if project_path:
    intent_gaps = find_intent_gaps(conn, project_name, project_path, top_n=20)
    if intent_gaps:
        write_intent_audit(intent_gaps, project_path, project_name)
```

Add `"intent_gaps": intent_gaps` to the `findings` dict:

```python
findings = {
    "coverage_gaps":          coverage_gaps,
    "coupling_hotspots":      coupling_hotspots,
    "clone_candidates":       clone_candidates,
    "staleness_alerts":       staleness_alerts,
    "complexity_hotspots":    complexity_hotspots,
    "cochange_patterns":      cochange_patterns,
    "best_practice_deviations": bp_deviations,
    "intent_gaps":            intent_gaps,      # NEW
}
```

The `total` calculation `sum(len(v) for v in findings.values())` automatically includes
`intent_gaps`. The return dict's `findings` key already handles any dict — no further
change needed for the return statement.

### 5.2 Changes to `write_cycle_report()`

Add an **Intent Gaps** section after the Research Recommendations section and before Planner
Constraints:

```python
# Intent gaps
intent_gaps_list = findings.get("intent_gaps", [])
lines.append(f"## Intent Gaps ({len(intent_gaps_list)} findings)")
if intent_gaps_list:
    lines.append("| Severity | Signal Type | Title | Diagnostic |")
    lines.append("|---|---|---|---|")
    for ig in intent_gaps_list[:20]:
        lines.append(
            f"| {ig['severity']} | {ig.get('signal_type', '')} | "
            f"{ig['title'][:80]} | {ig['diagnostic_type']} |"
        )
else:
    lines.append("No intent gaps found.")
lines.append("")
```

Update the Executive Summary `total findings` — already correct since `total_findings`
is computed from `sum(len(v) for v in findings.values())`.

---

## 6. No New DB Tables

Intent gaps are computed fresh each cycle from `health_scores`, `code_chunks`, and file I/O.
They are not persisted to the database. The output is written to the target project's
`knowledge/anvil/audit-findings-{date}.md`.

**Rationale:** Phase 2 findings are human-reviewed artifacts, not machine-queryable data.
The audit file is the source of truth. No schema migration is required.

---

## 7. Test Contract

Two required test behaviors in `tests/test_lab.py`:

### 7.1 `test_find_intent_gaps_missing_brief`

```python
def test_find_intent_gaps_missing_brief(tmp_path):
    """Returns empty list when PROJECT_BRIEF.md is absent."""
    conn = sqlite3.connect(":memory:")
    db.init_db(conn)
    result = find_intent_gaps(conn, "no-such-project", str(tmp_path), top_n=5)
    assert result == []
```

Setup: `tmp_path` is an empty directory — no PROJECT_BRIEF.md exists.
Expected: `find_intent_gaps()` returns `[]` (no exception raised).

### 7.2 `test_find_intent_gaps_returns_required_keys`

```python
REQUIRED_KEYS = {
    "finding_type", "severity", "title", "what",
    "why_it_matters", "what_needs_discovering",
    "success_looks_like", "diagnostic_type", "chunk_ids",
}

def test_find_intent_gaps_returns_required_keys(tmp_path):
    """Returns dicts with all required keys when minimal data exists."""
    # Setup: write PROJECT_BRIEF and domain-glossary
    (tmp_path / "PROJECT_BRIEF.md").write_text("Test project brief.")
    glossary_dir = tmp_path / "knowledge" / "research"
    glossary_dir.mkdir(parents=True)
    (glossary_dir / "domain-glossary.md").write_text("# Glossary\n")

    # Setup: in-memory DB with one coverage_gap chunk
    conn = sqlite3.connect(":memory:")
    db.init_db(conn)
    project_id = db.create_project(conn, "test-proj", str(tmp_path))

    # Insert one code_chunk
    conn.execute(
        "INSERT INTO code_chunks (project_id, file_path, chunk_type, name, content, "
        "line_start, line_end) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (project_id, "src/foo.py", "function", "do_thing", "def do_thing(): pass", 1, 3),
    )
    conn.commit()
    chunk_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    # Insert health_scores with high coverage_score + high composite
    conn.execute(
        "INSERT INTO health_scores (chunk_id, cycle_id, composite_score, "
        "coverage_score, volatility_score, coupling_score, complexity_score, "
        "staleness_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (chunk_id, 1, 0.80, 0.90, 0.85, 0.50, 0.40, 0.30),
    )
    conn.commit()

    result = find_intent_gaps(conn, "test-proj", str(tmp_path), top_n=5)

    assert isinstance(result, list)
    assert len(result) > 0
    for finding in result:
        missing = REQUIRED_KEYS - finding.keys()
        assert not missing, f"Missing keys: {missing}"
        assert isinstance(finding["chunk_ids"], list)
        assert finding["finding_type"] == "intent_gap"
        assert finding["severity"] in ("CRITICAL", "HIGH", "MEDIUM", "LOW")
```

---

## 8. Architecture Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Latest cycle resolution | `MAX(hs.cycle_id)` per project | Avoids requiring cycle_id parameter in Lab API |
| Brief + glossary in every dict | Yes | Enables full intent review per finding without re-reading files |
| Slot allocation (n/3 each type) | Equal split | Balanced signal across all three structural dimensions |
| No DB persistence | Fresh compute each cycle | Findings are human-reviewed, not machine-queried |
| `project["path"]` (not `project_path`) | `path` | DB column name verified from `CREATE TABLE projects` in db.py |
| `diagnostic_type` for coupling | `"Architecture check"` | Coupling hotspots indicate architectural concerns, not simple fixes |
| `diagnostic_type` for coverage/complexity | `"Fix"` | These are actionable remediation targets |

---

## 9. How to Verify This Was Implemented Correctly (QA Checklist)

```
[ ] grep src/lab.py find_intent_gaps              → function defined
[ ] grep src/lab.py write_intent_audit             → function defined
[ ] grep src/lab.py intent_gaps                    → present in run_lab() findings dict
[ ] grep src/lab.py knowledge/anvil               → present in write_intent_audit
[ ] grep tests/test_lab.py test_find_intent_gaps_missing_brief      → test present
[ ] grep tests/test_lab.py test_find_intent_gaps_returns_required_keys → test present
[ ] python3 -m pytest tests/ -v                   → all tests pass
[ ] smoke: find_intent_gaps returns list[dict] when brief exists
[ ] smoke: {project_path}/knowledge/anvil/ directory created after first non-empty run
[ ] smoke: audit-findings-{date}.md written to knowledge/anvil/ on non-empty result
```

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** 1 (Phase 2.1 SA Blueprint)
**Status:** Complete

### What Was Done
Designed the complete Phase 2.1 blueprint for `find_intent_gaps()` and `write_intent_audit()`.
Specified function signatures, DB queries, output dict schema (9 required keys + 7 context payload
keys), severity mapping, field templates by signal type (3 types), integration points in
`run_lab()` and `write_cycle_report()`, no-new-table rationale, two test contracts with full
code, and a QA verification checklist.

### Files Deposited
- `anvil/knowledge/architecture/phase21-intent-layer-blueprint-2026-04-14.md` — full SA blueprint

### Files Created or Modified (Code)
- None

### Decisions Made
- `project["path"]` (not `project_path`) — verified from `CREATE TABLE projects` DDL in `src/db.py`
- No new DB table — intent gaps are ephemeral audit artifacts written to the target project's `knowledge/anvil/` directory
- Latest cycle resolved via `MAX(hs.cycle_id)` — no cycle_id parameter required
- Equal slot allocation (top_n // 3 per signal type) for balanced structural signal coverage
- `"Architecture check"` diagnostic type for coupling hotspots; `"Fix"` for coverage and complexity hotspots

### Flags for CEO
- None

### Flags for Next Step
- DEV: Use `project["path"]` (not `project_path`) when retrieving project root from DB record
- DEV: `health_scores` table columns confirmed from existing `find_coverage_gaps()` query pattern — `coverage_score`, `volatility_score`, `coupling_score`, `complexity_score`, `composite_score`, `cycle_id` all present
- DEV: `code_chunks.structural_metadata` is JSON or None — always guard with try/except on json.loads
- DEV: The `find_intent_gaps()` function does NOT take `cycle_id` — it resolves the latest cycle internally
- DEV: The `project_path` parameter for `find_intent_gaps()` comes from `project["path"]` in `run_lab()`
