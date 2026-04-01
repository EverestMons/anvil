# Phase 9 Blueprint — Research Recommendations in Lab
**Date:** 2026-04-01 | **Agent:** Anvil Systems Analyst | **Step:** 1
**Depends on:** Phase 8 (best_practices table, role-specific scoring)

---

## 1. New Finding Type: best_practice_deviation

### Finding Structure

```python
{
    "chunk_id": int,
    "file_path": str,
    "name": str,
    "functional_role": str,
    "practice_name": str,
    "practice_description": str,
    "practice_severity": str,         # low/medium/high
    "observation": str,               # what the code actually does
    "recommendation": str,            # specific action to improve
}
```

### Generation Flow

```
for each chunk with functional_role != NULL:
    practices = get_best_practices_by_role(conn, chunk.functional_role)
    for practice in practices:
        result = check_best_practice(chunk, practice)
        if not result["compliant"]:
            emit deviation finding
```

---

## 2. Recommendation Format

Each recommendation string follows this template:

```
"{name}" is a {functional_role}. Best practice: {pattern_name} -- {description}.
Current: {observation}. Recommendation: {action}.
```

- **observation** comes from the detection engine (what the code actually does wrong)
- **action** is derived from the practice description (what should change)

Example:
```
"contracts_list" is a route_handler. Best practice: single_responsibility --
Each route handles one concern. Current: Function has 120 lines with 4 DB write
operations. Recommendation: Extract orchestration logic into a service function.
```

---

## 3. Planner Constraint Type: pattern_recommendation

```python
{
    "type": "pattern_recommendation",
    "target": "web/contracts.py::contracts_list",
    "reason": "route_handler deviates from single_responsibility: "
              "120 lines, 4 DB writes. Extract orchestration logic.",
    "severity": "medium",  # from best_practice.severity
}
```

Added to generate_planner_constraints() alongside existing constraint types.

---

## 4. Cycle Report Section

New section after existing findings, before Planner Constraints:

```markdown
## Research Recommendations ({N} deviations across {K} roles)

### route_handler ({count} deviations)
- **[high]** `web/contracts.py::contracts_list` -- single_responsibility:
  120 lines, 4 DB writes. Extract orchestration logic.
- **[medium]** `web/action_queue.py::process_action` -- consistent_error_handling:
  Bare except clause at line 45. Add specific exception types.

### validation_gate ({count} deviations)
...
```

Grouped by functional_role, sorted by severity within each group.

---

## 5. Cross-Project Comparison (Future-Ready)

Schema hook only -- no implementation in Phase 9.

The existing schema already supports multi-project comparison:
- `projects` table holds multiple projects
- `code_chunks` are keyed by project_id
- `health_scores` are per-chunk
- `functional_roles` are project-agnostic

Future query pattern:
```sql
SELECT p.name, cc.functional_role,
       AVG(hs.composite_score) as avg_score,
       COUNT(*) as chunk_count
FROM health_scores hs
JOIN code_chunks cc ON hs.chunk_id = cc.id
JOIN projects p ON cc.project_id = p.id
WHERE cc.functional_role IS NOT NULL
GROUP BY p.name, cc.functional_role
ORDER BY cc.functional_role, avg_score
```

No new tables needed. The comparison logic lives in Lab as a future function.

---

## 6. Detection Hint Engine -- src/detector.py

### Public API

```python
def check_best_practice(chunk: dict, practice: dict) -> dict:
    """Check if a chunk complies with a best practice.

    Args:
        chunk: dict with keys: name, file_path, content, chunk_type,
               structural_metadata (JSON string), functional_role
        practice: dict with keys: pattern_name, description,
                  detection_hint, severity

    Returns:
        {"compliant": bool, "observation": str}
        observation is empty string if compliant, descriptive if not.
    """
```

### Three Detection Modes

The detection_hint field contains human-readable text describing what to look for. The engine parses this into checks:

#### Mode 1: Content Regex

Search chunk content for patterns indicating violations:

```python
CONTENT_CHECKS = {
    "single_responsibility": [
        # Check function length
        {"type": "line_count", "threshold": 80,
         "message": "Function has {value} lines (threshold: 80)"},
    ],
    "consistent_error_handling": [
        {"type": "content_regex", "pattern": r"except\s*:",
         "message": "Bare except clause found"},
    ],
    "input_validation_at_boundary": [
        {"type": "content_regex", "pattern": r"request\.form\[",
         "message": "Raw request.form[] access without .get()"},
    ],
    "pure_functions": [
        {"type": "content_regex", "pattern": r"\bconn\b",
         "message": "Database connection parameter found in utility function"},
        {"type": "content_regex", "pattern": r"\bopen\s*\(",
         "message": "File I/O found in utility function"},
    ],
    "no_domain_logic": [
        {"type": "content_regex",
         "pattern": r"\b(invoice|contract|carrier|validation)\b",
         "message": "Domain-specific term '{match}' found in utility function"},
    ],
    "deterministic_output": [
        {"type": "content_regex", "pattern": r"datetime\.now\(\)",
         "message": "datetime.now() used in gate function"},
        {"type": "content_regex", "pattern": r"\brequests\.",
         "message": "External HTTP call found in gate function"},
    ],
    "idempotent_schema": [
        {"type": "content_regex",
         "pattern": r"CREATE\s+TABLE\s+(?!IF\s+NOT\s+EXISTS)",
         "message": "CREATE TABLE without IF NOT EXISTS"},
    ],
}
```

#### Mode 2: Structural Metadata Threshold

Check structural_metadata JSON fields:

```python
STRUCTURAL_CHECKS = {
    "single_responsibility": [
        {"type": "metadata_threshold", "field": "line_count",
         "threshold": 80, "message": "Function has {value} lines (threshold: 80)"},
    ],
    "error_accumulation": [
        {"type": "metadata_threshold", "field": "cyclomatic_complexity",
         "threshold": 1, "direction": "min",
         "message": "Gate has CC={value}, may be too simple for error accumulation"},
    ],
}
```

#### Mode 3: Combined Check

Some practices require both content and structural checks. The engine runs all applicable checks for a practice and returns the first violation found.

### Check Resolution Order

1. Look up pattern_name in CONTENT_CHECKS -- run all matching checks
2. Look up pattern_name in STRUCTURAL_CHECKS -- run all matching checks
3. If no predefined check exists for this pattern, return compliant=True (no automated detection available)

This means new best practices added via web research won't have automated detection until someone adds a corresponding check entry. This is by design -- we want curated detection, not guessing.

---

## 7. How to Verify

### Detection Engine
```python
# Compliant chunk (simple route)
chunk = {"name": "index", "content": "def index():\n    return 'ok'",
         "structural_metadata": '{"line_count": 3}'}
practice = {"pattern_name": "single_responsibility", ...}
result = check_best_practice(chunk, practice)
assert result["compliant"] == True

# Non-compliant chunk (bare except)
chunk = {"name": "handle", "content": "def handle():\n    try:\n        x()\n    except:\n        pass"}
practice = {"pattern_name": "consistent_error_handling", ...}
result = check_best_practice(chunk, practice)
assert result["compliant"] == False
assert "Bare except" in result["observation"]
```

### Deviation Findings
Run find_best_practice_deviations() against invoice-pulse. Verify:
- Findings produced for known violations
- Each finding has all required fields
- Recommendations are specific (not generic)

### Planner Constraints
Verify pattern_recommendation constraints generated and include role + pattern + action.

### Cycle Report
Run full cycle. Verify:
- "Research Recommendations" section present
- Grouped by role
- Summary counts match finding count

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** 1 (Phase 9 Blueprint)
**Status:** Complete

### What Was Done
Blueprint for Phase 9: detection hint engine with 3 modes (content regex, structural threshold, combined), best_practice_deviation finding type, pattern_recommendation Planner constraint, cycle report Research Recommendations section, cross-project comparison schema hook (future-ready).

### Files Deposited
- anvil/knowledge/architecture/phase9-research-recs-blueprint-2026-04-01.md

### Decisions Made
- Detection engine uses predefined check tables per pattern_name, not dynamic parsing of detection_hint text
- Practices without predefined checks return compliant=True (safe default)
- Cross-project comparison deferred to future phase (schema already supports it)
- domain keyword check uses word boundary regex to avoid false positives

### Flags for CEO
- None

### Flags for Next Step
- Developer: CONTENT_CHECKS and STRUCTURAL_CHECKS are the exact specs -- implement as lookup dicts
- New practices from web research won't have automated detection until check entries are added
