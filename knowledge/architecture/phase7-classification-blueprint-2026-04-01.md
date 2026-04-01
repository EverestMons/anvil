# Phase 7 Blueprint — Functional Classification + Provenance
**Date:** 2026-04-01 | **Agent:** Anvil Systems Analyst | **Step:** 1
**Source plan:** executable-phase7-classification-2026-04-01.md
**Diagnostic inputs:** research-pipeline-diagnostic-2026-04-01.md (Q1-Q6), execution-plan-archive-analysis-2026-04-01.md (Q7-Q11)

---

## 1. Schema Additions

### 1.1 functional_roles Table

```sql
CREATE TABLE IF NOT EXISTS functional_roles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE,
    description     TEXT,
    parent_role     TEXT,
    scoring_weights TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

- `name` is the canonical role identifier (snake_case). UNIQUE constraint.
- `parent_role` is nullable TEXT (not FK) -- stores the group name for hierarchy display but does not enforce referential integrity. Groups: web_layer, validation_pipeline, intelligence_layer, data_layer, infrastructure.
- `scoring_weights` is nullable TEXT storing JSON override for Phase 8. NULL means "use default weights."

### 1.2 chunk_provenance Table

```sql
CREATE TABLE IF NOT EXISTS chunk_provenance (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id        INTEGER NOT NULL REFERENCES code_chunks(id) ON DELETE CASCADE,
    plan_name       TEXT    NOT NULL,
    dev_log_path    TEXT,
    plan_description TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_chunk_provenance_chunk
    ON chunk_provenance(chunk_id);

CREATE INDEX IF NOT EXISTS idx_chunk_provenance_plan
    ON chunk_provenance(plan_name);
```

- `chunk_id` is FK with CASCADE delete -- if the chunk is deleted, provenance goes too.
- `plan_name` is the slug extracted from the dev log filename (e.g., "action-router-engine-2026-03-14").
- `dev_log_path` is the relative path to the dev log file.
- `plan_description` is the feature description extracted from the plan or dev log title. Used by Phase 8+ for semantic role enrichment on ambiguous chunks.

### 1.3 code_chunks.functional_role Column

```sql
ALTER TABLE code_chunks ADD COLUMN functional_role TEXT;
```

- Nullable TEXT. Not a strict FK -- the functional_roles table is a reference/seed table, not an enforced constraint. This avoids migration issues when adding new roles.
- Runtime migration: try/except OperationalError (column already exists), same pattern as the existing structural_metadata migration in db.py.

### 1.4 Runtime Migration

Add to `init_db()` in `src/db.py`, after the existing structural_metadata migration:

```python
# Migration: add functional_role column if not present
try:
    conn.execute("ALTER TABLE code_chunks ADD COLUMN functional_role TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass  # Column already exists
```

The functional_roles and chunk_provenance CREATE TABLE IF NOT EXISTS statements go inside the main executescript() block. Seeding happens in a separate `_seed_functional_roles()` function called after table creation.

---

## 2. Functional Role Taxonomy Seed

25 roles across 5 groups. INSERT OR IGNORE for idempotency.

```python
FUNCTIONAL_ROLE_SEEDS = [
    # Web Layer
    ("route_handler", "Flask blueprint route functions handling HTTP requests", "web_layer"),
    ("report_generator", "Analytics dashboards and Excel export routes", "web_layer"),
    ("document_manager", "Contract document hierarchy CRUD routes", "web_layer"),

    # Validation Pipeline
    ("validation_gate", "Sequential invoice validation gates returning GateResult", "validation_pipeline"),
    ("validation_orchestrator", "Runs gates in sequence and aggregates results", "validation_pipeline"),
    ("batch_validator", "Concurrent multi-invoice validation with caching", "validation_pipeline"),
    ("action_router", "Maps validation failures to action queue items", "validation_pipeline"),
    ("content_generator", "Text generation for dispute emails and tickets", "validation_pipeline"),

    # Intelligence Layer
    ("confidence_engine", "State machine for contract element confidence lifecycle", "intelligence_layer"),
    ("anomaly_detector", "Drift detection between paid data and contract terms", "intelligence_layer"),
    ("pattern_learner", "Discovers new contract terms from paid invoice patterns", "intelligence_layer"),
    ("circuit_breaker", "Contradiction spike detection to prevent feedback loops", "intelligence_layer"),
    ("exit_interviewer", "PRO resolution capture and pattern logging", "intelligence_layer"),

    # Data Layer
    ("ingestion_orchestrator", "Full CSV/XML ingestion pipeline orchestration", "data_layer"),
    ("data_parser", "XML/CSV parsing and format conversion", "data_layer"),
    ("data_model", "SQLite schema definitions and migrations", "data_layer"),
    ("lifecycle_tracker", "Invoice status transition detection and logging", "data_layer"),
    ("entity_matcher", "Carrier identity detection via fuzzy matching", "data_layer"),
    ("address_normalizer", "Bill-to normalization and fuzzy matching", "data_layer"),

    # Infrastructure
    ("pipeline_orchestrator", "Daily execution sequence coordinator", "infrastructure"),
    ("data_guardian", "Backup and integrity verification", "infrastructure"),
    ("email_processor", "PST import and email-to-invoice matching", "infrastructure"),
    ("configuration", "Centralized settings and constants", "infrastructure"),
    ("audit_logger", "Append-only event logging", "infrastructure"),
    ("utility", "Generic helpers with no domain logic", "infrastructure"),
]
```

Seed function:

```python
def _seed_functional_roles(conn):
    for name, description, parent_role in FUNCTIONAL_ROLE_SEEDS:
        conn.execute(
            "INSERT OR IGNORE INTO functional_roles (name, description, parent_role) "
            "VALUES (?, ?, ?)",
            (name, description, parent_role),
        )
    conn.commit()
```

Called from `init_db()` after the executescript block.

---

## 3. Heuristic Classifier Module -- src/classifier.py

### 3.1 Public API

```python
def classify_chunk(chunk_dict: dict) -> str | None:
    """Classify a single chunk into a functional role.

    chunk_dict keys used: name, file_path, content, chunk_type,
                          structural_metadata (JSON string or None)

    Returns functional role name string, or None for truly ambiguous.
    """

def classify_project(conn, project_name: str) -> dict:
    """Classify all chunks in a project. Updates code_chunks.functional_role.

    Returns {"classified": N, "unclassified": N, "role_distribution": {...}}.
    """
```

### 3.2 Classification Rules (Priority Order)

Rules are evaluated top-to-bottom. First match wins.

#### Priority 1 -- chunk_type overrides

Skip classification for test_case and module chunk_types. They get functional_role = None. These are already structurally typed and don't need functional classification.

Config chunks get functional_role = "configuration".

#### Priority 2 -- Decorator patterns (content-based)

Search the first 10 lines of chunk content for decorator signatures:

```python
DECORATOR_RULES = [
    (r"@\w+_bp\.route\(", "route_handler"),
    (r"@\w+_bp\.get\(", "route_handler"),
    (r"@\w+_bp\.post\(", "route_handler"),
    (r"@app\.route\(", "route_handler"),
]
```

#### Priority 3 -- Naming conventions

```python
NAME_RULES = [
    (r"^gate_\d+_", "validation_gate"),
    (r"^validate_invoice$", "validation_orchestrator"),
    (r"^validate_batch$", "batch_validator"),
    (r"^route_actions$", "action_router"),
    (r"^generate_\w+_email$", "content_generator"),
    (r"^generate_\w+_ticket$", "content_generator"),
    (r"^detect_\w+_drift$", "anomaly_detector"),
    (r"^discover_\w+", "pattern_learner"),
    (r"^learn_\w+_rules$", "pattern_learner"),
    (r"^check_contradictions$", "circuit_breaker"),
    (r"^run_pro_exit_interviews$", "exit_interviewer"),
    (r"^check_and_log_changes$", "lifecycle_tracker"),
    (r"^run_ingestion$", "ingestion_orchestrator"),
    (r"^run_pipeline$", "pipeline_orchestrator"),
    (r"^run_backup$", "data_guardian"),
    (r"^pre_ingestion_check$", "data_guardian"),
    (r"^post_ingestion_verify$", "data_guardian"),
    (r"^import_pst$", "email_processor"),
    (r"^validate_billto$", "address_normalizer"),
    (r"^_normalize_billto", "address_normalizer"),
    (r"^_create_tables$", "data_model"),
    (r"^_migrate_\w+", "data_model"),
    (r"^_safe_add_column", "data_model"),
    (r"^init_db$", "data_model"),
    (r"^log_event$", "audit_logger"),
]
```

#### Priority 4 -- File path patterns

```python
FILE_PATH_RULES = [
    (r"^engines/confidence\.py$", "confidence_engine"),
    (r"^engines/validator\.py$", "validation_gate"),
    (r"^engines/action_router\.py$", "action_router"),
    (r"^engines/email_generator\.py$", "content_generator"),
    (r"^engines/drift_detector\.py$", "anomaly_detector"),
    (r"^engines/pattern_learner\.py$", "pattern_learner"),
    (r"^engines/circuit_breaker\.py$", "circuit_breaker"),
    (r"^engines/exit_interview\.py$", "exit_interviewer"),
    (r"^engines/lifecycle\.py$", "lifecycle_tracker"),
    (r"^engines/carrier_identity\.py$", "entity_matcher"),
    (r"^engines/billto_validator\.py$", "address_normalizer"),
    (r"^engines/pst_importer\.py$", "email_processor"),
    (r"^engines/email_parser\.py$", "email_processor"),
    (r"^engines/email_matcher\.py$", "email_processor"),
    (r"^engines/backtest\.py$", "action_router"),
    (r"^ingestion/ingest\.py$", "ingestion_orchestrator"),
    (r"^ingestion/xml_parser\.py$", "data_parser"),
    (r"^ingestion/csv_reader\.py$", "data_parser"),
    (r"^web/reporting\.py$", "report_generator"),
    (r"^web/gap_dashboard\.py$", "report_generator"),
    (r"^web/intelligence\.py$", "report_generator"),
    (r"^web/documents\.py$", "document_manager"),
    (r"^web/", "route_handler"),
    (r"^database\.py$", "data_model"),
    (r"^contract_tables\.py$", "data_model"),
    (r"^config\.py$", "configuration"),
    (r"^run_pipeline\.py$", "pipeline_orchestrator"),
    (r"^validate_batch\.py$", "batch_validator"),
    (r"^backup\.py$", "data_guardian"),
    (r"^integrity\.py$", "data_guardian"),
]
```

Note: More specific file path rules come before general ones (e.g., `web/reporting.py` before `web/`).

#### Priority 5 -- Fallback

- For functions not matched by any rule: assign "utility"
- For methods: inherit from parent class role if the class was classifiable, else "utility"
- For classes: apply file path rules, then name heuristics
- Return None only for module-level chunks and test_case chunks

### 3.3 classify_project() Flow

```python
def classify_project(conn, project_name):
    project = db.get_project(conn, project_name)
    chunks = get_all_classifiable_chunks(conn, project["id"])
    # Excludes module and test_case chunk_types

    classified = 0
    unclassified = 0
    distribution = defaultdict(int)

    for chunk in chunks:
        role = classify_chunk(chunk)
        if role:
            conn.execute(
                "UPDATE code_chunks SET functional_role = ? WHERE id = ?",
                (role, chunk["id"]),
            )
            classified += 1
            distribution[role] += 1
        else:
            unclassified += 1

    conn.commit()
    return {
        "classified": classified,
        "unclassified": unclassified,
        "role_distribution": dict(distribution),
    }
```

---

## 4. Dev Log Parser Module -- src/provenance.py

### 4.1 Public API

```python
def parse_dev_logs(dev_log_dir: str) -> list[dict]:
    """Parse all .md files in dev_log_dir for Output Receipt file lists.

    Returns list of:
    {
        "dev_log_name": "action-router-engine-2026-03-14.md",
        "plan_slug": "action-router-engine-2026-03-14",
        "plan_description": "Action Router Engine",
        "file_paths": [
            {"path": "engines/action_router.py", "description": "Created, ~470 lines"},
            ...
        ]
    }
    """

def ingest_provenance(conn, project_name: str, dev_log_dir: str) -> dict:
    """Parse dev logs and populate chunk_provenance table.

    Returns {"logs_parsed": N, "provenance_entries_created": N, "unmatched_files": N}.
    """
```

### 4.2 Header Search Patterns

Multi-pattern search, in order of likelihood:

```python
HEADER_PATTERNS = [
    r"^###?\s*Files Created or Modified \(Code\)\s*$",
    r"^###?\s*Files Created/Modified\s*$",
    r"^###?\s*Files Modified\s*$",
    r"^\*\*Files Modified:\*\*\s*$",
    r"^###?\s*Files Created or Modified\s*$",
]
```

### 4.3 Entry Extraction Patterns

After finding the header, read lines until the next header (^# or ^--- or blank line after entries):

**Bullet format:**
```python
BULLET_PATTERN = r"^-\s+([a-zA-Z0-9_./-]+\.\w+)\s*(?:--|---|---)\s*(.*)$"
# group(1) = file path, group(2) = description
```

**Table format:**
```python
TABLE_ROW_PATTERN = r"^\|\s*([a-zA-Z0-9_./-]+\.\w+)\s*\|"
# group(1) = file path (first column)
# Skip header rows (containing "---" or "File")
```

### 4.4 Plan Slug and Description Extraction

```python
def _extract_plan_slug(filename: str) -> str:
    """Strip .md extension to get plan slug."""
    return filename.rsplit(".", 1)[0]

def _extract_plan_description(content: str) -> str:
    """Extract H1 title from dev log content."""
    for line in content.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return ""
```

---

## 5. Provenance Ingestion

```python
def ingest_provenance(conn, project_name, dev_log_dir):
    project = db.get_project(conn, project_name)
    project_id = project["id"]

    parsed = parse_dev_logs(dev_log_dir)
    entries_created = 0
    unmatched = 0

    for log_entry in parsed:
        for file_info in log_entry["file_paths"]:
            # Find matching chunks by file_path
            chunks = db.get_chunks_by_file(conn, project_id, file_info["path"])
            if chunks:
                for chunk in chunks:
                    # Dedup check
                    existing = conn.execute(
                        "SELECT id FROM chunk_provenance "
                        "WHERE chunk_id = ? AND plan_name = ?",
                        (chunk["id"], log_entry["plan_slug"]),
                    ).fetchone()
                    if not existing:
                        conn.execute(
                            "INSERT INTO chunk_provenance "
                            "(chunk_id, plan_name, dev_log_path, plan_description) "
                            "VALUES (?, ?, ?, ?)",
                            (chunk["id"], log_entry["plan_slug"],
                             log_entry["dev_log_name"],
                             log_entry["plan_description"]),
                        )
                        entries_created += 1
            else:
                unmatched += 1

    conn.commit()
    return {
        "logs_parsed": len(parsed),
        "provenance_entries_created": entries_created,
        "unmatched_files": unmatched,
    }
```

Note: get_chunks_by_file needs the relative file_path as stored in code_chunks. Dev logs use relative paths from repo root, which matches.

---

## 6. Pipeline Integration

### 6.1 New Stage: CLASSIFY

Updated pipeline order:

```
SCAN -> EXTRACT -> CLASSIFY -> SCORE -> LAB
```

### 6.2 Integration in src/cycle.py

Insert CLASSIFY stage between EXTRACT and SCORE in run_cycle():

```python
from src.classifier import classify_project
from src.provenance import ingest_provenance
from src.config import DEV_LOG_PATHS

# After EXTRACT succeeds:

# Stage 2.5: CLASSIFY
try:
    classify_result = classify_project(conn, project_name)
    results["classify"] = classify_result
except Exception as e:
    results["classify"] = {"error": str(e)}
    # Non-fatal -- scoring proceeds with functional_role = NULL

# Stage 2.5b: PROVENANCE
try:
    dev_log_dir = DEV_LOG_PATHS.get(project_name)
    if dev_log_dir:
        provenance_result = ingest_provenance(conn, project_name, dev_log_dir)
        results["provenance"] = provenance_result
except Exception as e:
    results["provenance"] = {"error": str(e)}

# Then SCORE and LAB continue as before
```

Classification is **non-fatal**. If it fails, scoring proceeds with functional_role = NULL and uses default weights (same as current behavior). This ensures backward compatibility.

Provenance dedup check (SELECT id WHERE chunk_id AND plan_name) handles idempotent re-runs.

### 6.3 Config Addition

Add to src/config.py:

```python
DEV_LOG_PATHS = {
    "invoice-pulse": "/Users/marklehn/Desktop/GitHub/invoice-pulse/knowledge/development/",
}
```

---

## 7. How to Verify

### Schema Verification
```sql
-- functional_roles table exists and has 25 rows
SELECT COUNT(*) FROM functional_roles;  -- expect 25

-- chunk_provenance table exists
SELECT sql FROM sqlite_master WHERE name = 'chunk_provenance';

-- code_chunks.functional_role column exists
PRAGMA table_info(code_chunks);  -- should list functional_role column
```

### Classifier Verification
```python
# Known test cases
assert classify_chunk({
    "name": "contracts_list",
    "file_path": "web/contracts.py",
    "content": "@contracts_bp.route('/contracts')\ndef contracts_list():",
    "chunk_type": "function",
}) == "route_handler"

assert classify_chunk({
    "name": "gate_1_legitimacy",
    "file_path": "engines/validator.py",
    "content": "def gate_1_legitimacy(conn, invoice_id):",
    "chunk_type": "function",
}) == "validation_gate"

assert classify_chunk({
    "name": "_parse_json",
    "file_path": "web/utils.py",
    "content": "def _parse_json(text):",
    "chunk_type": "function",
}) == "utility"

assert classify_chunk({
    "name": "_create_tables",
    "file_path": "database.py",
    "content": "def _create_tables(conn):",
    "chunk_type": "function",
}) == "data_model"
```

### Dev Log Parser Verification
Create a test markdown file with known "Files Created or Modified (Code)" section. Assert:
- Correct number of file entries extracted
- File paths match expected values
- Descriptions parsed correctly
- Handle both bullet and table formats

### Provenance Verification
After ingest_provenance():
```sql
SELECT COUNT(*) FROM chunk_provenance;  -- should be > 0
SELECT cp.plan_name, cp.dev_log_path, cc.file_path, cc.name
FROM chunk_provenance cp
JOIN code_chunks cc ON cp.chunk_id = cc.id
LIMIT 5;  -- spot check linkage
```

### Pipeline Verification
Run a full cycle. Check:
1. results["classify"] present with classified > 0
2. results["provenance"] present with provenance_entries_created > 0
3. code_chunks.functional_role populated before scorer runs
4. Scorer and Lab produce same output quality as before (no regressions)
5. Existing tests still pass

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** 1 (Phase 7 Blueprint)
**Status:** Complete

### What Was Done
Produced a complete blueprint for Phase 7: Functional Classification + Provenance. Covers schema additions (functional_roles table, chunk_provenance table, code_chunks.functional_role column), 25-role taxonomy seed, heuristic classifier with priority-ordered rules (decorators > naming > file paths > fallback), dev log parser with multi-pattern header search, provenance ingestion, and pipeline integration as a new CLASSIFY stage between EXTRACT and SCORE.

### Files Deposited
- anvil/knowledge/architecture/phase7-classification-blueprint-2026-04-01.md -- full implementation blueprint

### Files Created or Modified (Code)
- None (blueprint only)

### Decisions Made
- functional_role column is TEXT without strict FK constraint (avoids migration issues when adding new roles)
- test_case and module chunk_types are skipped during classification (already structurally typed)
- Classification is non-fatal in the pipeline (scoring falls back to default weights)
- Provenance uses dedup check for idempotent re-runs
- Dev log parser uses multi-pattern header search to handle format variations

### Flags for CEO
- None

### Flags for Next Step
- Developer should read this blueprint before implementing. Key implementation order: schema first, then classifier, then provenance, then pipeline wiring, then tests.
- The FUNCTIONAL_ROLE_SEEDS list and all rule tables are exact specifications -- implement as-is unless an edge case is discovered during testing.
- The 25 roles are a starting point. Future cycles may discover new roles; the INSERT OR IGNORE seeding pattern supports this.
