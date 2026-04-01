# Phase 8 Blueprint — Best Practices Knowledge Base + Purpose-Aware Scoring
**Date:** 2026-04-01 | **Agent:** Anvil Systems Analyst | **Step:** 1
**Source plan:** executable-phase8-best-practices-2026-04-01.md
**Depends on:** Phase 7 (functional_roles table, code_chunks.functional_role column)

---

## 1. best_practices Table

```sql
CREATE TABLE IF NOT EXISTS best_practices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    functional_role TEXT    NOT NULL,
    pattern_name    TEXT    NOT NULL,
    description     TEXT    NOT NULL,
    detection_hint  TEXT,
    source          TEXT    NOT NULL DEFAULT 'curated',
    severity        TEXT    NOT NULL DEFAULT 'medium'
                    CHECK (severity IN ('low', 'medium', 'high')),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_best_practices_role
    ON best_practices(functional_role);
```

- `functional_role` references the role name from functional_roles but is TEXT (not strict FK) for flexibility.
- `detection_hint` is a human-readable description of how to detect violations (may contain regex patterns or AST descriptions). Used by Phase 9 Lab analysis.
- `source` is one of: "curated" (from diagnostic seed), "web_research" (from Claude Code research sessions), "cross_project" (discovered from analyzing multiple projects).
- `severity` constrains to low/medium/high.

Add to the main executescript() block in db.py, after chunk_provenance.

---

## 2. Best Practices Seed Data

15 patterns across 5 roles (3 each). INSERT OR IGNORE using (functional_role, pattern_name) uniqueness.

```python
BEST_PRACTICE_SEEDS = [
    # route_handler (3)
    (
        "route_handler",
        "single_responsibility",
        "Each route function handles one concern (render, submit, or API response) "
        "without multi-step orchestration inline",
        "Function length > 80 lines or multiple DB write operations in one route",
        "curated",
        "medium",
    ),
    (
        "route_handler",
        "input_validation_at_boundary",
        "All form/query params validated before DB operations; "
        "use request.form.get() with type coercion, not raw dict access",
        "Missing type coercion on request.form values; raw request.form[] access",
        "curated",
        "high",
    ),
    (
        "route_handler",
        "consistent_error_handling",
        "Flash messages for user errors, proper HTTP status codes for API routes, "
        "no bare except clauses",
        "Bare except: blocks; missing flash() on validation failure; 200 status on error",
        "curated",
        "medium",
    ),

    # confidence_engine (3)
    (
        "confidence_engine",
        "immutable_state_transitions",
        "All state transitions go through ALLOWED_TRANSITIONS check; "
        "no direct state assignment bypassing the transition validator",
        "State column UPDATE without calling transition validation function",
        "curated",
        "high",
    ),
    (
        "confidence_engine",
        "append_only_audit",
        "Every state change writes to confidence_log; no updates or deletes on log table",
        "UPDATE or DELETE on confidence_log table; missing log entry after state change",
        "curated",
        "high",
    ),
    (
        "confidence_engine",
        "threshold_gated_automation",
        "Automated actions (dispute routing) require minimum invoice count threshold "
        "before triggering; never auto-act on insufficient data",
        "Automation logic without checking min_invoices or sample_size threshold",
        "curated",
        "high",
    ),

    # validation_gate (3)
    (
        "validation_gate",
        "structured_return_type",
        "Every gate returns a GateResult dataclass with pass/fail, reason, "
        "and enrichment data; never raw booleans or tuples",
        "Functions returning bool, tuple, or dict instead of GateResult",
        "curated",
        "high",
    ),
    (
        "validation_gate",
        "error_accumulation",
        "Gates collect all failures within their scope rather than short-circuiting "
        "on first error; the orchestrator decides halt behavior",
        "Early return on first failure within a single gate function",
        "curated",
        "medium",
    ),
    (
        "validation_gate",
        "deterministic_output",
        "Same inputs produce same GateResult; no external API calls, no random state, "
        "no datetime.now() in comparison logic within gate functions",
        "External HTTP calls; datetime.now() used in value comparison; random module usage",
        "curated",
        "medium",
    ),

    # utility (3)
    (
        "utility",
        "pure_functions",
        "No side effects, no DB access, no file I/O; pure data transformation only",
        "Functions with conn parameter; file open() calls; global state mutation",
        "curated",
        "medium",
    ),
    (
        "utility",
        "explicit_null_handling",
        "Return typed defaults rather than None; document nullable return values "
        "with type hints",
        "Bare return None without Optional type hint; undocumented None returns",
        "curated",
        "low",
    ),
    (
        "utility",
        "no_domain_logic",
        "Helpers should be domain-agnostic; domain-specific logic belongs "
        "in its functional role module",
        "References to invoice, contract, carrier, or validation in utility functions",
        "curated",
        "medium",
    ),

    # data_model (3)
    (
        "data_model",
        "idempotent_schema",
        "All CREATE TABLE use IF NOT EXISTS; all ALTER TABLE wrapped in try/except "
        "for existing columns; migrations safe to re-run",
        "Missing IF NOT EXISTS; bare ALTER TABLE without error handling",
        "curated",
        "high",
    ),
    (
        "data_model",
        "foreign_key_enforcement",
        "All cross-table references use REFERENCES with explicit ON DELETE policy "
        "(CASCADE, SET NULL, or RESTRICT)",
        "Integer columns referencing other tables without FK constraint",
        "curated",
        "medium",
    ),
    (
        "data_model",
        "migration_isolation",
        "Each migration in its own function with clear naming (_migrate_X_schema); "
        "never mix multiple schema changes in one function",
        "Multiple unrelated ALTER TABLE in one function; unnamed migration logic",
        "curated",
        "medium",
    ),
]
```

Seed function:

```python
def _seed_best_practices(conn):
    for role, pattern, desc, hint, source, severity in BEST_PRACTICE_SEEDS:
        conn.execute(
            "INSERT OR IGNORE INTO best_practices "
            "(functional_role, pattern_name, description, detection_hint, source, severity) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (role, pattern, desc, hint, source, severity),
        )
    conn.commit()
```

Called from init_db() after _seed_functional_roles(). Uses INSERT OR IGNORE -- safe for re-runs.

To make INSERT OR IGNORE work, add a UNIQUE constraint:

```sql
CREATE UNIQUE INDEX IF NOT EXISTS idx_best_practices_role_pattern
    ON best_practices(functional_role, pattern_name);
```

---

## 3. Role-Specific Scoring Weights

Add to `src/config.py`:

```python
ROLE_SCORING_WEIGHTS = {
    "route_handler": {
        "volatility": 0.20, "coverage": 0.30, "complexity": 0.25,
        "coupling": 0.15, "staleness": 0.10,
    },
    "validation_gate": {
        "volatility": 0.15, "coverage": 0.35, "complexity": 0.10,
        "coupling": 0.15, "staleness": 0.25,
    },
    "confidence_engine": {
        "volatility": 0.20, "coverage": 0.25, "complexity": 0.15,
        "coupling": 0.20, "staleness": 0.20,
    },
    "data_model": {
        "volatility": 0.30, "coverage": 0.20, "complexity": 0.10,
        "coupling": 0.25, "staleness": 0.15,
    },
    "utility": {
        "volatility": 0.20, "coverage": 0.20, "complexity": 0.30,
        "coupling": 0.15, "staleness": 0.15,
    },
    "ingestion_orchestrator": {
        "volatility": 0.20, "coverage": 0.25, "complexity": 0.20,
        "coupling": 0.20, "staleness": 0.15,
    },
    "action_router": {
        "volatility": 0.20, "coverage": 0.30, "complexity": 0.20,
        "coupling": 0.15, "staleness": 0.15,
    },
    "report_generator": {
        "volatility": 0.15, "coverage": 0.20, "complexity": 0.25,
        "coupling": 0.15, "staleness": 0.25,
    },
}
```

**Design rationale:**
- **route_handler:** Higher coverage weight (0.30) -- routes are entry points that must be tested. Higher complexity (0.25) -- routes should stay simple. Lower staleness (0.10) -- routes change often but that's normal.
- **validation_gate:** Highest coverage (0.35) -- gates are the core correctness guarantee. Low complexity (0.10) -- gates are inherently complex; high CC is expected. High staleness (0.25) -- stale gates are dangerous.
- **confidence_engine:** Balanced with higher coupling (0.20) -- state machine changes ripple. Higher staleness (0.20) -- stale confidence logic is risky.
- **data_model:** Highest volatility (0.30) -- frequent schema changes are risky. Higher coupling (0.25) -- schema changes affect many modules.
- **utility:** Highest complexity (0.30) -- utilities should be simple. Balanced otherwise.

Roles not in ROLE_SCORING_WEIGHTS fall back to the global SCORING_WEIGHTS.

---

## 4. Purpose-Relative Thresholds

Store in config as a separate dict (not in functional_roles.scoring_weights JSON -- that's for Phase 8+):

```python
ROLE_THRESHOLDS = {
    "route_handler": {
        "complexity_threshold": 0.60,
        "coupling_hotspot_threshold": 0.80,
    },
    "validation_gate": {
        "complexity_threshold": 0.95,
        "coupling_hotspot_threshold": 0.80,
    },
    "confidence_engine": {
        "complexity_threshold": 0.85,
        "coupling_hotspot_threshold": 0.70,
    },
    "data_model": {
        "complexity_threshold": 0.90,
        "coupling_hotspot_threshold": 0.90,
    },
    "utility": {
        "complexity_threshold": 0.50,
        "coupling_hotspot_threshold": 0.80,
    },
}
```

**Rationale:**
- route_handler: lower complexity threshold (0.60) -- routes should be simple, flag early
- validation_gate: very high complexity threshold (0.95) -- gates are naturally complex, only flag extreme cases
- utility: lowest complexity threshold (0.50) -- utilities must be simple
- confidence_engine: lower coupling threshold (0.70) -- coupling in state machines is especially dangerous

---

## 5. Scorer Modifications

### 5.1 score_project() Changes

```python
def score_project(conn, project_name, cycle_id):
    # ... existing chunk loading ...

    for chunk in chunks:
        role = chunk.get("functional_role")

        # Select weights: role-specific or default
        weights = ROLE_SCORING_WEIGHTS.get(role, SCORING_WEIGHTS)

        # ... existing raw score computation (unchanged) ...

        composite = compute_composite(
            vol_score, cov_score, comp_score, coup_score, stale_score,
            weights,  # now role-specific
        )

        # ... existing health_score insertion ...
```

The key change is one line: `weights = ROLE_SCORING_WEIGHTS.get(role, SCORING_WEIGHTS)`.

### 5.2 compute_composite() -- No Changes

The existing function already takes a `weights` dict parameter. No modification needed.

### 5.3 Lab Threshold Adjustments

In `src/lab.py`, the find_complexity_hotspots() and find_coupling_hotspots() functions currently use global thresholds. For Phase 8, they should check role-specific thresholds:

```python
def find_complexity_hotspots(conn, project_id, cycle_id):
    # ... existing query ...
    for r in cur.fetchall():
        role = r[6]  # functional_role from joined code_chunks
        role_thresholds = ROLE_THRESHOLDS.get(role, {})
        threshold = role_thresholds.get(
            "complexity_threshold", COMPLEXITY_THRESHOLD
        )
        if r[4] >= threshold:  # complexity_score
            results.append(...)
```

This means the SQL query no longer pre-filters by threshold -- it fetches all scored chunks and Python applies role-specific thresholds. Alternatively, keep the SQL filter at a minimum threshold (e.g., 0.50) and let Python do the per-role check.

**Recommended approach:** Keep the SQL filter at the lowest possible role threshold (0.50 for utility) and do per-role filtering in Python. This avoids fetching all chunks while still supporting role-specific thresholds.

---

## 6. Web Research Hook

### Function Signature

```python
def research_best_practices(conn, role_name: str) -> dict:
    """Generate a research prompt for Claude Code to discover new best practices.

    Returns a dict with:
        role_name, role_description, existing_practices, research_prompt
    """
```

### Flow

1. Query functional_roles for role description
2. Query best_practices for existing patterns for this role
3. Build a structured prompt: "For a {role_name} ({description}), research established software engineering best practices. Current known patterns: {list}. Find 2-3 additional patterns not already listed."
4. Return the prompt as a dict -- Claude Code reads this, does web research, then calls:

```python
def add_best_practice(conn, functional_role: str, pattern_name: str,
                      description: str, detection_hint: str,
                      source: str = "web_research",
                      severity: str = "medium") -> int:
    """Insert a new best practice. Returns the new row ID."""
```

This is NOT automated. It runs when Claude Code is in a Lab session and decides a role needs more practices.

---

## 7. How to Verify

### Best Practices Table
```sql
SELECT COUNT(*) FROM best_practices;  -- expect 15
SELECT functional_role, COUNT(*) FROM best_practices GROUP BY functional_role;
-- expect 3 per role for 5 roles
```

### Role-Specific Scoring
Create two chunks with identical structural metrics but different functional_roles:
- Chunk A: role="route_handler", CC=10, no tests
- Chunk B: role="validation_gate", CC=10, no tests

Score both. Verify:
- Chunk A composite > Chunk B composite (because route_handler weights complexity higher at 0.25 vs validation_gate at 0.10)

### Threshold Adjustment
- validation_gate with complexity_score=0.90: should NOT be flagged (threshold is 0.95)
- route_handler with complexity_score=0.90: SHOULD be flagged (threshold is 0.60)

### Fallback
- Chunk with functional_role=NULL: composite should match what SCORING_WEIGHTS produces

### Pipeline
Run a full cycle. Verify:
- Some chunks now score differently than Phase 7 (role-specific weights applied)
- Existing finding types still work
- Lab complexity hotspots respect role thresholds

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** 1 (Phase 8 Blueprint)
**Status:** Complete

### What Was Done
Produced blueprint for Phase 8: best_practices table with 15 seed patterns, role-specific scoring weights for 8 roles, purpose-relative thresholds for 5 roles, scorer modifications (one-line weight lookup change), Lab threshold adjustments, and web research hook for Claude Code-driven practice discovery.

### Files Deposited
- anvil/knowledge/architecture/phase8-best-practices-blueprint-2026-04-01.md -- full blueprint

### Files Created or Modified (Code)
- None (blueprint only)

### Decisions Made
- best_practices uses TEXT functional_role (not strict FK) for flexibility
- UNIQUE index on (functional_role, pattern_name) enables INSERT OR IGNORE seeding
- Role-specific thresholds stored in config dict, not in DB (simpler, faster)
- Lab complexity filtering: SQL pre-filters at minimum threshold, Python applies per-role check
- Web research hook is manual (Claude Code decides when to research, not automated)

### Flags for CEO
- None

### Flags for Next Step
- Developer: the scorer change is minimal (one line for weight lookup). Most work is in db.py seeding and config additions.
- Lab threshold changes require modifying the SQL query to include functional_role in the SELECT and adjusting the filtering logic.
