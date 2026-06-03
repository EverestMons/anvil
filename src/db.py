"""
Anvil database layer — SQLite schema initialization and all CRUD operations.

All functions take a sqlite3.Connection as the first argument for testability.
Callers are responsible for opening/closing the connection.
"""
from __future__ import annotations

import sqlite3
from typing import Optional


def _row_to_dict(cursor: sqlite3.Cursor, row: tuple) -> dict:
    """Convert a row to a dict using column names from the cursor description."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def init_db(conn: sqlite3.Connection) -> None:
    """
    Create all tables if they don't exist.
    Enables WAL mode and foreign keys.
    """
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT    NOT NULL UNIQUE,
            path            TEXT    NOT NULL,
            last_scanned    TEXT,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS code_chunks (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id      INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            file_path       TEXT    NOT NULL,
            chunk_type      TEXT    NOT NULL CHECK (chunk_type IN ('function', 'class', 'method', 'module', 'config', 'test_case')),
            name            TEXT    NOT NULL,
            content         TEXT    NOT NULL,
            content_hash    TEXT    NOT NULL,
            start_line      INTEGER NOT NULL,
            end_line        INTEGER NOT NULL,
            parent_chunk_id INTEGER REFERENCES code_chunks(id) ON DELETE SET NULL,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            cycle_id        INTEGER,
            last_seen_cycle INTEGER
        );

        CREATE INDEX IF NOT EXISTS idx_code_chunks_project_file
            ON code_chunks(project_id, file_path);

        CREATE INDEX IF NOT EXISTS idx_code_chunks_chunk_type
            ON code_chunks(chunk_type);

        CREATE INDEX IF NOT EXISTS idx_code_chunks_parent
            ON code_chunks(parent_chunk_id);

        CREATE INDEX IF NOT EXISTS idx_code_chunks_content_hash
            ON code_chunks(content_hash);

        CREATE TABLE IF NOT EXISTS chunk_fingerprints (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            chunk_id        INTEGER NOT NULL REFERENCES code_chunks(id) ON DELETE CASCADE,
            content_hash    TEXT    NOT NULL,
            minhash_signature BLOB,
            shingle_count   INTEGER,
            cycle_id        INTEGER NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_chunk_fingerprints_chunk
            ON chunk_fingerprints(chunk_id);

        CREATE INDEX IF NOT EXISTS idx_chunk_fingerprints_cycle
            ON chunk_fingerprints(cycle_id);

        CREATE TABLE IF NOT EXISTS chunk_symbol_bindings (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            chunk_id        INTEGER NOT NULL REFERENCES code_chunks(id) ON DELETE CASCADE,
            symbol_name     TEXT    NOT NULL,
            binding_type    TEXT    NOT NULL CHECK (binding_type IN ('defines', 'imports', 'calls', 'tests', 'documents')),
            target_chunk_id INTEGER REFERENCES code_chunks(id) ON DELETE SET NULL,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_symbol_bindings_chunk
            ON chunk_symbol_bindings(chunk_id);

        CREATE INDEX IF NOT EXISTS idx_symbol_bindings_symbol
            ON chunk_symbol_bindings(symbol_name);

        CREATE INDEX IF NOT EXISTS idx_symbol_bindings_target
            ON chunk_symbol_bindings(target_chunk_id);

        CREATE INDEX IF NOT EXISTS idx_symbol_bindings_type
            ON chunk_symbol_bindings(binding_type);

        CREATE TABLE IF NOT EXISTS chunk_dependencies (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            source_chunk_id INTEGER NOT NULL REFERENCES code_chunks(id) ON DELETE CASCADE,
            target_chunk_id INTEGER NOT NULL REFERENCES code_chunks(id) ON DELETE CASCADE,
            dependency_type TEXT    NOT NULL CHECK (dependency_type IN ('import', 'call', 'inherit')),
            scope           TEXT    NOT NULL CHECK (scope IN ('within_file', 'cross_file')),
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_chunk_deps_source
            ON chunk_dependencies(source_chunk_id);

        CREATE INDEX IF NOT EXISTS idx_chunk_deps_target
            ON chunk_dependencies(target_chunk_id);

        CREATE TABLE IF NOT EXISTS chunk_similarities (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            chunk_a_id      INTEGER NOT NULL REFERENCES code_chunks(id) ON DELETE CASCADE,
            chunk_b_id      INTEGER NOT NULL REFERENCES code_chunks(id) ON DELETE CASCADE,
            similarity_score REAL   NOT NULL,
            cycle_id        INTEGER NOT NULL,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_chunk_similarities_a
            ON chunk_similarities(chunk_a_id);

        CREATE INDEX IF NOT EXISTS idx_chunk_similarities_b
            ON chunk_similarities(chunk_b_id);

        CREATE INDEX IF NOT EXISTS idx_chunk_similarities_cycle
            ON chunk_similarities(cycle_id);

        CREATE TABLE IF NOT EXISTS git_changes (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id      INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            file_path       TEXT    NOT NULL,
            commit_hash     TEXT    NOT NULL,
            commit_date     TEXT    NOT NULL,
            commit_message  TEXT,
            author          TEXT,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_git_changes_project_file
            ON git_changes(project_id, file_path);

        CREATE INDEX IF NOT EXISTS idx_git_changes_commit_hash
            ON git_changes(commit_hash);

        CREATE TABLE IF NOT EXISTS test_results (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id      INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            run_date        TEXT    NOT NULL,
            total_tests     INTEGER NOT NULL,
            passed          INTEGER NOT NULL,
            failed          INTEGER NOT NULL,
            skipped         INTEGER NOT NULL,
            failed_test_names TEXT,
            cycle_id        INTEGER,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_test_results_project
            ON test_results(project_id);

        CREATE TABLE IF NOT EXISTS health_scores (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            chunk_id        INTEGER NOT NULL REFERENCES code_chunks(id) ON DELETE CASCADE,
            volatility_score    REAL NOT NULL DEFAULT 0.0,
            coverage_score      REAL NOT NULL DEFAULT 0.0,
            complexity_score    REAL NOT NULL DEFAULT 0.0,
            coupling_score      REAL NOT NULL DEFAULT 0.0,
            staleness_score     REAL NOT NULL DEFAULT 0.0,
            composite_score     REAL NOT NULL DEFAULT 0.0,
            cycle_id        INTEGER NOT NULL,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_health_scores_chunk_cycle
            ON health_scores(chunk_id, cycle_id);

        CREATE TABLE IF NOT EXISTS cycle_reports (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id      INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            cycle_number    INTEGER NOT NULL,
            started_at      TEXT    NOT NULL,
            completed_at    TEXT,
            files_scanned   INTEGER NOT NULL DEFAULT 0,
            chunks_extracted INTEGER NOT NULL DEFAULT 0,
            chunks_scored   INTEGER NOT NULL DEFAULT 0,
            findings_count  INTEGER NOT NULL DEFAULT 0,
            report_path     TEXT,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_cycle_reports_project
            ON cycle_reports(project_id);

        CREATE UNIQUE INDEX IF NOT EXISTS idx_cycle_reports_project_cycle
            ON cycle_reports(project_id, cycle_number);

        CREATE TABLE IF NOT EXISTS functional_roles (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT    NOT NULL UNIQUE,
            description     TEXT,
            parent_role     TEXT,
            scoring_weights TEXT,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        );

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

        CREATE UNIQUE INDEX IF NOT EXISTS idx_best_practices_role_pattern
            ON best_practices(functional_role, pattern_name);
    """)
    conn.commit()

    # Migration: add structural_metadata column if not present
    try:
        conn.execute("ALTER TABLE code_chunks ADD COLUMN structural_metadata TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Migration: add functional_role column if not present
    try:
        conn.execute("ALTER TABLE code_chunks ADD COLUMN functional_role TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Migration: add last_seen_cycle column if not present
    try:
        conn.execute("ALTER TABLE code_chunks ADD COLUMN last_seen_cycle INTEGER")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists

    _seed_functional_roles(conn)
    _seed_best_practices(conn)


# --- projects ---

def create_project(conn: sqlite3.Connection, name: str, path: str) -> int:
    """Insert a new project. Returns the new row ID."""
    cur = conn.execute(
        "INSERT INTO projects (name, path) VALUES (?, ?)",
        (name, path),
    )
    conn.commit()
    return cur.lastrowid


def get_project(conn: sqlite3.Connection, name: str) -> Optional[dict]:
    """Retrieve a project by name. Returns dict or None."""
    conn.row_factory = _row_to_dict
    cur = conn.execute("SELECT * FROM projects WHERE name = ?", (name,))
    row = cur.fetchone()
    conn.row_factory = None
    return row


# --- code_chunks ---

def create_chunk(conn: sqlite3.Connection, **kwargs) -> int:
    """Insert a new code chunk. Returns the new row ID.

    Required kwargs: project_id, file_path, chunk_type, name, content,
                     content_hash, start_line, end_line
    Optional kwargs: parent_chunk_id, cycle_id
    """
    cols = ", ".join(kwargs.keys())
    placeholders = ", ".join(["?"] * len(kwargs))
    cur = conn.execute(
        f"INSERT INTO code_chunks ({cols}) VALUES ({placeholders})",
        tuple(kwargs.values()),
    )
    conn.commit()
    return cur.lastrowid


def get_chunks_by_project(conn: sqlite3.Connection, project_id: int) -> list[dict]:
    """Retrieve all chunks for a project."""
    conn.row_factory = _row_to_dict
    cur = conn.execute(
        "SELECT * FROM code_chunks WHERE project_id = ? ORDER BY file_path, start_line",
        (project_id,),
    )
    rows = cur.fetchall()
    conn.row_factory = None
    return rows


def get_chunks_by_file(conn: sqlite3.Connection, project_id: int,
                       file_path: str) -> list[dict]:
    """Retrieve all chunks for a specific file in a project."""
    conn.row_factory = _row_to_dict
    cur = conn.execute(
        "SELECT * FROM code_chunks WHERE project_id = ? AND file_path = ? "
        "ORDER BY start_line",
        (project_id, file_path),
    )
    rows = cur.fetchall()
    conn.row_factory = None
    return rows


# --- chunk_fingerprints ---

def create_fingerprint(conn: sqlite3.Connection, chunk_id: int,
                       content_hash: str, minhash_sig: Optional[bytes],
                       shingle_count: Optional[int], cycle_id: int) -> int:
    """Insert a chunk fingerprint. Returns the new row ID."""
    cur = conn.execute(
        "INSERT INTO chunk_fingerprints (chunk_id, content_hash, minhash_signature, "
        "shingle_count, cycle_id) VALUES (?, ?, ?, ?, ?)",
        (chunk_id, content_hash, minhash_sig, shingle_count, cycle_id),
    )
    conn.commit()
    return cur.lastrowid


# --- chunk_symbol_bindings ---

def create_symbol_binding(conn: sqlite3.Connection, chunk_id: int,
                          symbol_name: str, binding_type: str,
                          target_chunk_id: Optional[int] = None) -> int:
    """Insert a symbol binding. Returns the new row ID."""
    cur = conn.execute(
        "INSERT INTO chunk_symbol_bindings (chunk_id, symbol_name, binding_type, "
        "target_chunk_id) VALUES (?, ?, ?, ?)",
        (chunk_id, symbol_name, binding_type, target_chunk_id),
    )
    conn.commit()
    return cur.lastrowid


def get_bindings_by_chunk(conn: sqlite3.Connection, chunk_id: int) -> list[dict]:
    """Retrieve all symbol bindings for a chunk."""
    conn.row_factory = _row_to_dict
    cur = conn.execute(
        "SELECT * FROM chunk_symbol_bindings WHERE chunk_id = ? ORDER BY id",
        (chunk_id,),
    )
    rows = cur.fetchall()
    conn.row_factory = None
    return rows


# --- chunk_dependencies ---

def create_dependency(conn: sqlite3.Connection, source_id: int,
                      target_id: int, dep_type: str, scope: str) -> int:
    """Insert a chunk dependency. Returns the new row ID."""
    cur = conn.execute(
        "INSERT INTO chunk_dependencies (source_chunk_id, target_chunk_id, "
        "dependency_type, scope) VALUES (?, ?, ?, ?)",
        (source_id, target_id, dep_type, scope),
    )
    conn.commit()
    return cur.lastrowid


def get_dependencies(conn: sqlite3.Connection, chunk_id: int,
                     direction: str = "outbound") -> list[dict]:
    """Retrieve dependencies for a chunk.

    direction: 'outbound' (chunk depends on others) or 'inbound' (others depend on chunk)
    """
    conn.row_factory = _row_to_dict
    if direction == "outbound":
        cur = conn.execute(
            "SELECT * FROM chunk_dependencies WHERE source_chunk_id = ? ORDER BY id",
            (chunk_id,),
        )
    else:
        cur = conn.execute(
            "SELECT * FROM chunk_dependencies WHERE target_chunk_id = ? ORDER BY id",
            (chunk_id,),
        )
    rows = cur.fetchall()
    conn.row_factory = None
    return rows


# --- chunk_similarities ---

def create_similarity(conn: sqlite3.Connection, chunk_a_id: int,
                      chunk_b_id: int, score: float, cycle_id: int) -> int:
    """Insert a similarity pair. Returns the new row ID."""
    cur = conn.execute(
        "INSERT INTO chunk_similarities (chunk_a_id, chunk_b_id, similarity_score, "
        "cycle_id) VALUES (?, ?, ?, ?)",
        (chunk_a_id, chunk_b_id, score, cycle_id),
    )
    conn.commit()
    return cur.lastrowid


# --- git_changes ---

def create_git_change(conn: sqlite3.Connection, project_id: int,
                      file_path: str, commit_hash: str, commit_date: str,
                      commit_message: Optional[str],
                      author: Optional[str]) -> int:
    """Insert a git change record. Returns the new row ID."""
    cur = conn.execute(
        "INSERT INTO git_changes (project_id, file_path, commit_hash, commit_date, "
        "commit_message, author) VALUES (?, ?, ?, ?, ?, ?)",
        (project_id, file_path, commit_hash, commit_date, commit_message, author),
    )
    conn.commit()
    return cur.lastrowid


# --- test_results ---

def create_test_result(conn: sqlite3.Connection, project_id: int,
                       **kwargs) -> int:
    """Insert a test result. Returns the new row ID.

    Required kwargs: run_date, total_tests, passed, failed, skipped
    Optional kwargs: failed_test_names, cycle_id
    """
    all_kwargs = {"project_id": project_id, **kwargs}
    cols = ", ".join(all_kwargs.keys())
    placeholders = ", ".join(["?"] * len(all_kwargs))
    cur = conn.execute(
        f"INSERT INTO test_results ({cols}) VALUES ({placeholders})",
        tuple(all_kwargs.values()),
    )
    conn.commit()
    return cur.lastrowid


# --- health_scores ---

def create_health_score(conn: sqlite3.Connection, chunk_id: int,
                        **kwargs) -> int:
    """Insert a health score. Returns the new row ID.

    Required kwargs: cycle_id
    Optional kwargs: volatility_score, coverage_score, complexity_score,
                     coupling_score, staleness_score, composite_score
    """
    all_kwargs = {"chunk_id": chunk_id, **kwargs}
    cols = ", ".join(all_kwargs.keys())
    placeholders = ", ".join(["?"] * len(all_kwargs))
    cur = conn.execute(
        f"INSERT INTO health_scores ({cols}) VALUES ({placeholders})",
        tuple(all_kwargs.values()),
    )
    conn.commit()
    return cur.lastrowid


# --- cycle_reports ---

def create_cycle_report(conn: sqlite3.Connection, project_id: int,
                        **kwargs) -> int:
    """Insert a cycle report. Returns the new row ID.

    Required kwargs: cycle_number, started_at
    Optional kwargs: completed_at, files_scanned, chunks_extracted,
                     chunks_scored, findings_count, report_path
    """
    all_kwargs = {"project_id": project_id, **kwargs}
    cols = ", ".join(all_kwargs.keys())
    placeholders = ", ".join(["?"] * len(all_kwargs))
    cur = conn.execute(
        f"INSERT INTO cycle_reports ({cols}) VALUES ({placeholders})",
        tuple(all_kwargs.values()),
    )
    conn.commit()
    return cur.lastrowid


def get_cycle_report(conn: sqlite3.Connection, cycle_number: int) -> Optional[dict]:
    """Retrieve a cycle report by cycle number. Returns dict or None."""
    conn.row_factory = _row_to_dict
    cur = conn.execute(
        "SELECT * FROM cycle_reports WHERE cycle_number = ?", (cycle_number,)
    )
    row = cur.fetchone()
    conn.row_factory = None
    return row


# --- functional_roles ---

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


def _seed_functional_roles(conn: sqlite3.Connection) -> None:
    """Seed functional_roles table with the 25-role taxonomy."""
    for name, description, parent_role in FUNCTIONAL_ROLE_SEEDS:
        conn.execute(
            "INSERT OR IGNORE INTO functional_roles (name, description, parent_role) "
            "VALUES (?, ?, ?)",
            (name, description, parent_role),
        )
    conn.commit()


def get_functional_roles(conn: sqlite3.Connection) -> list[dict]:
    """Retrieve all functional roles."""
    conn.row_factory = _row_to_dict
    cur = conn.execute("SELECT * FROM functional_roles ORDER BY parent_role, name")
    rows = cur.fetchall()
    conn.row_factory = None
    return rows


# --- chunk_provenance ---

def create_provenance(conn: sqlite3.Connection, chunk_id: int,
                      plan_name: str, dev_log_path: Optional[str] = None,
                      plan_description: Optional[str] = None) -> int:
    """Insert a provenance entry. Returns the new row ID."""
    cur = conn.execute(
        "INSERT INTO chunk_provenance (chunk_id, plan_name, dev_log_path, "
        "plan_description) VALUES (?, ?, ?, ?)",
        (chunk_id, plan_name, dev_log_path, plan_description),
    )
    conn.commit()
    return cur.lastrowid


def get_provenance_by_chunk(conn: sqlite3.Connection,
                            chunk_id: int) -> list[dict]:
    """Retrieve all provenance entries for a chunk."""
    conn.row_factory = _row_to_dict
    cur = conn.execute(
        "SELECT * FROM chunk_provenance WHERE chunk_id = ? ORDER BY id",
        (chunk_id,),
    )
    rows = cur.fetchall()
    conn.row_factory = None
    return rows


# --- best_practices ---

BEST_PRACTICE_SEEDS = [
    # route_handler
    ("route_handler", "single_responsibility",
     "Each route function handles one concern without multi-step orchestration inline",
     "Function length > 80 lines or multiple DB write operations in one route",
     "curated", "medium"),
    ("route_handler", "input_validation_at_boundary",
     "All form/query params validated before DB operations with type coercion",
     "Missing type coercion on request.form values; raw request.form[] access",
     "curated", "high"),
    ("route_handler", "consistent_error_handling",
     "Flash messages for user errors, proper HTTP status codes, no bare except clauses",
     "Bare except: blocks; missing flash() on validation failure; 200 status on error",
     "curated", "medium"),
    # confidence_engine
    ("confidence_engine", "immutable_state_transitions",
     "All state transitions go through ALLOWED_TRANSITIONS check; no direct state assignment",
     "State column UPDATE without calling transition validation function",
     "curated", "high"),
    ("confidence_engine", "append_only_audit",
     "Every state change writes to confidence_log; no updates or deletes on log table",
     "UPDATE or DELETE on confidence_log table; missing log entry after state change",
     "curated", "high"),
    ("confidence_engine", "threshold_gated_automation",
     "Automated actions require minimum invoice count threshold before triggering",
     "Automation logic without checking min_invoices or sample_size threshold",
     "curated", "high"),
    # validation_gate
    ("validation_gate", "structured_return_type",
     "Every gate returns a GateResult dataclass with pass/fail, reason, and enrichment data",
     "Functions returning bool, tuple, or dict instead of GateResult",
     "curated", "high"),
    ("validation_gate", "error_accumulation",
     "Gates collect all failures within scope rather than short-circuiting on first error",
     "Early return on first failure within a single gate function",
     "curated", "medium"),
    ("validation_gate", "deterministic_output",
     "Same inputs produce same GateResult; no external API calls or datetime in comparisons",
     "External HTTP calls; datetime.now() used in value comparison; random module usage",
     "curated", "medium"),
    # utility
    ("utility", "pure_functions",
     "No side effects, no DB access, no file I/O; pure data transformation only",
     "Functions with conn parameter; file open() calls; global state mutation",
     "curated", "medium"),
    ("utility", "explicit_null_handling",
     "Return typed defaults rather than None; document nullable return values with type hints",
     "Bare return None without Optional type hint; undocumented None returns",
     "curated", "low"),
    ("utility", "no_domain_logic",
     "Helpers should be domain-agnostic; domain-specific logic belongs in its role module",
     "References to invoice, contract, carrier, or validation in utility functions",
     "curated", "medium"),
    # data_model
    ("data_model", "idempotent_schema",
     "All CREATE TABLE use IF NOT EXISTS; ALTER TABLE wrapped in try/except",
     "Missing IF NOT EXISTS; bare ALTER TABLE without error handling",
     "curated", "high"),
    ("data_model", "foreign_key_enforcement",
     "All cross-table references use REFERENCES with explicit ON DELETE policy",
     "Integer columns referencing other tables without FK constraint",
     "curated", "medium"),
    ("data_model", "migration_isolation",
     "Each migration in its own function with clear naming (_migrate_X_schema)",
     "Multiple unrelated ALTER TABLE in one function; unnamed migration logic",
     "curated", "medium"),
]


def _seed_best_practices(conn: sqlite3.Connection) -> None:
    """Seed best_practices table with 15 initial patterns."""
    for role, pattern, desc, hint, source, severity in BEST_PRACTICE_SEEDS:
        conn.execute(
            "INSERT OR IGNORE INTO best_practices "
            "(functional_role, pattern_name, description, detection_hint, source, severity) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (role, pattern, desc, hint, source, severity),
        )
    conn.commit()


def create_best_practice(conn: sqlite3.Connection, functional_role: str,
                         pattern_name: str, description: str,
                         detection_hint: Optional[str] = None,
                         source: str = "web_research",
                         severity: str = "medium") -> int:
    """Insert a new best practice. Returns the new row ID."""
    cur = conn.execute(
        "INSERT INTO best_practices "
        "(functional_role, pattern_name, description, detection_hint, source, severity) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (functional_role, pattern_name, description, detection_hint, source, severity),
    )
    conn.commit()
    return cur.lastrowid


def get_best_practices_by_role(conn: sqlite3.Connection,
                               role: str) -> list[dict]:
    """Retrieve all best practices for a functional role."""
    conn.row_factory = _row_to_dict
    cur = conn.execute(
        "SELECT * FROM best_practices WHERE functional_role = ? ORDER BY severity DESC, id",
        (role,),
    )
    rows = cur.fetchall()
    conn.row_factory = None
    return rows
