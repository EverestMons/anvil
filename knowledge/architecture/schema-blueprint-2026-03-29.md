# Anvil Schema Blueprint
**Agent:** Anvil Systems Analyst
**Date:** 2026-03-29
**Source:** PROJECT_BRIEF data model (lines 92-116), Forge db.py conventions

---

## Design Decisions

### 1. `code_chunks.content` — Full source text or reference?
**Decision:** Store full source text. Phase 1 targets invoice-pulse only — DB size is manageable. Full text enables search and analysis without file I/O round-trips. This is consistent with Forge's `chunks` table which stores `content TEXT NOT NULL`.

### 2. `chunk_fingerprints` — Separate table or columns on `code_chunks`?
**Decision:** Separate table. Follows Study's pattern, keeps the core table lean, and allows independent update cycles for fingerprints (e.g., recompute MinHash without touching chunk records). MinHash signatures are BLOBs that would bloat row scans on `code_chunks`.

### 3. Index strategy
**Decision:** Indexes on all foreign keys (SQLite does not auto-index FK columns), plus composite indexes for common query patterns. Detailed below per table.

---

## Schema DDL

### Core Tables

#### `projects`
Registered project metadata. One row per analyzed project.

```sql
CREATE TABLE IF NOT EXISTS projects (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE,
    path            TEXT    NOT NULL,
    last_scanned    TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

#### `code_chunks`
Individual code units — the fundamental entity in Anvil's data model.

```sql
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
    cycle_id        INTEGER
);

CREATE INDEX IF NOT EXISTS idx_code_chunks_project_file
    ON code_chunks(project_id, file_path);

CREATE INDEX IF NOT EXISTS idx_code_chunks_chunk_type
    ON code_chunks(chunk_type);

CREATE INDEX IF NOT EXISTS idx_code_chunks_parent
    ON code_chunks(parent_chunk_id);

CREATE INDEX IF NOT EXISTS idx_code_chunks_content_hash
    ON code_chunks(content_hash);
```

**Notes:**
- `chunk_type` uses a CHECK constraint to enforce the six valid types from the domain glossary
- `parent_chunk_id` is a self-referential FK for methods inside classes (NULL for top-level chunks)
- `content_hash` is SHA-256 of the chunk's source text, indexed for dedup lookups
- `cycle_id` is a plain integer (not a FK to cycle_reports) — cycles may be created after chunks

#### `chunk_fingerprints`
SHA-256 content hashes and MinHash signatures per chunk, per cycle.

```sql
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
```

**Notes:**
- `minhash_signature` is a BLOB storing the serialized MinHash object from datasketch
- `shingle_count` records how many shingles were generated (useful for debugging small chunks)
- One row per chunk per cycle — enables historical comparison

#### `chunk_symbol_bindings`
Typed relationships between chunks and symbols.

```sql
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
```

**Notes:**
- `target_chunk_id` is nullable — bindings are created during EXTRACT before all chunks exist; resolution happens in a second pass
- `binding_type` CHECK constraint enforces the five valid types from the domain glossary

#### `chunk_dependencies`
Directed edges between chunks — import chains, call graphs, inheritance.

```sql
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
```

**Notes:**
- Both source and target are NOT NULL — dependencies are only created when both chunks are known
- `scope` tracks whether the dependency is within the same file or across files

#### `chunk_similarities`
MinHash similarity pairs above threshold.

```sql
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
```

**Notes:**
- Pairs are stored once (a < b by convention to avoid duplicates)
- `similarity_score` is the Jaccard similarity from MinHash comparison (0.0 to 1.0)
- Only pairs above the `MINHASH_THRESHOLD` (0.7) are stored

---

### Signal Tables

#### `git_changes`
Per-file change history from git log.

```sql
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
```

#### `test_results`
Per-run test outcomes.

```sql
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
```

**Notes:**
- `failed_test_names` stores JSON array of failed test identifiers (TEXT, not a separate table — keeps schema simple for Phase 1)
- `cycle_id` is nullable — test results can be imported independently of a full cycle

#### `health_scores`
Composite per-chunk scores from the five scoring dimensions.

```sql
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
```

**Notes:**
- All score columns default to 0.0 — dimensions are populated as data becomes available
- `composite_score` is the weighted combination (formula TBD by SA in scoring blueprint)
- One row per chunk per cycle — enables trend tracking

#### `cycle_reports`
Per-cycle summaries and Lab findings.

```sql
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
```

**Notes:**
- `cycle_number` is unique per project (enforced by unique index)
- `completed_at` is nullable — set when the cycle finishes
- `report_path` points to the Lab output file in the knowledge base

---

## Foreign Key Map

| Table | Column | References | On Delete |
|---|---|---|---|
| `code_chunks` | `project_id` | `projects(id)` | CASCADE |
| `code_chunks` | `parent_chunk_id` | `code_chunks(id)` | SET NULL |
| `chunk_fingerprints` | `chunk_id` | `code_chunks(id)` | CASCADE |
| `chunk_symbol_bindings` | `chunk_id` | `code_chunks(id)` | CASCADE |
| `chunk_symbol_bindings` | `target_chunk_id` | `code_chunks(id)` | SET NULL |
| `chunk_dependencies` | `source_chunk_id` | `code_chunks(id)` | CASCADE |
| `chunk_dependencies` | `target_chunk_id` | `code_chunks(id)` | CASCADE |
| `chunk_similarities` | `chunk_a_id` | `code_chunks(id)` | CASCADE |
| `chunk_similarities` | `chunk_b_id` | `code_chunks(id)` | CASCADE |
| `git_changes` | `project_id` | `projects(id)` | CASCADE |
| `test_results` | `project_id` | `projects(id)` | CASCADE |
| `health_scores` | `chunk_id` | `code_chunks(id)` | CASCADE |
| `cycle_reports` | `project_id` | `projects(id)` | CASCADE |

---

## Index Summary

| Table | Index Name | Columns | Type |
|---|---|---|---|
| `code_chunks` | `idx_code_chunks_project_file` | `project_id, file_path` | Composite |
| `code_chunks` | `idx_code_chunks_chunk_type` | `chunk_type` | Single |
| `code_chunks` | `idx_code_chunks_parent` | `parent_chunk_id` | Single |
| `code_chunks` | `idx_code_chunks_content_hash` | `content_hash` | Single |
| `chunk_fingerprints` | `idx_chunk_fingerprints_chunk` | `chunk_id` | Single |
| `chunk_fingerprints` | `idx_chunk_fingerprints_cycle` | `cycle_id` | Single |
| `chunk_symbol_bindings` | `idx_symbol_bindings_chunk` | `chunk_id` | Single |
| `chunk_symbol_bindings` | `idx_symbol_bindings_symbol` | `symbol_name` | Single |
| `chunk_symbol_bindings` | `idx_symbol_bindings_target` | `target_chunk_id` | Single |
| `chunk_symbol_bindings` | `idx_symbol_bindings_type` | `binding_type` | Single |
| `chunk_dependencies` | `idx_chunk_deps_source` | `source_chunk_id` | Single |
| `chunk_dependencies` | `idx_chunk_deps_target` | `target_chunk_id` | Single |
| `chunk_similarities` | `idx_chunk_similarities_a` | `chunk_a_id` | Single |
| `chunk_similarities` | `idx_chunk_similarities_b` | `chunk_b_id` | Single |
| `chunk_similarities` | `idx_chunk_similarities_cycle` | `cycle_id` | Single |
| `git_changes` | `idx_git_changes_project_file` | `project_id, file_path` | Composite |
| `git_changes` | `idx_git_changes_commit_hash` | `commit_hash` | Single |
| `test_results` | `idx_test_results_project` | `project_id` | Single |
| `health_scores` | `idx_health_scores_chunk_cycle` | `chunk_id, cycle_id` | Composite |
| `cycle_reports` | `idx_cycle_reports_project` | `project_id` | Single |
| `cycle_reports` | `idx_cycle_reports_project_cycle` | `project_id, cycle_number` | Unique |

---

## How to Verify This Was Implemented Correctly

The QA agent should run the following checks against a live database created by `init_db()`:

### 1. Table Completeness
```sql
SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;
```
**Expected (10 tables):** `chunk_dependencies`, `chunk_fingerprints`, `chunk_similarities`, `chunk_symbol_bindings`, `code_chunks`, `cycle_reports`, `git_changes`, `health_scores`, `projects`, `test_results`

### 2. Column Accuracy
For each table, run:
```sql
PRAGMA table_info(table_name);
```
Verify column names, types, NOT NULL constraints, and default values match the DDL above.

### 3. Foreign Key Integrity
For each table with FKs, run:
```sql
PRAGMA foreign_key_list(table_name);
```
Verify all FKs match the Foreign Key Map above. Test enforcement: inserting a `code_chunks` row with `project_id = 9999` (nonexistent) should raise `IntegrityError`.

### 4. Index Coverage
For each table, run:
```sql
PRAGMA index_list(table_name);
```
Verify all 21 indexes from the Index Summary exist (including the unique index on `cycle_reports`).

### 5. CHECK Constraint Enforcement
- Insert a `code_chunks` row with `chunk_type = 'invalid'` — should fail
- Insert a `chunk_symbol_bindings` row with `binding_type = 'invalid'` — should fail
- Insert a `chunk_dependencies` row with `dependency_type = 'invalid'` — should fail
- Insert a `chunk_dependencies` row with `scope = 'invalid'` — should fail

### 6. WAL Mode and Foreign Keys
```sql
PRAGMA journal_mode;
-- Expected: wal

PRAGMA foreign_keys;
-- Expected: 1
```

### 7. Forge Pattern Compliance
- `init_db(conn)` function exists and takes a connection as first argument
- `_row_to_dict(cursor, row)` helper exists
- All CRUD functions take `conn` as first argument

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** Step 1
**Status:** Complete

### What Was Done
Designed the complete SQLite schema blueprint for Anvil covering all 10 tables (6 core, 4 signal), 13 foreign keys, 21 indexes, and 4 CHECK constraints. Made three design decisions: store full source text in code_chunks, keep chunk_fingerprints as a separate table, and index all FK columns plus common query patterns.

### Files Deposited
- `anvil/knowledge/architecture/schema-blueprint-2026-03-29.md` — complete schema blueprint with DDL, foreign key map, index summary, and verification checklist

### Files Created or Modified (Code)
- None (blueprint only — implementation is Step 2)

### Decisions Made
- Store full source text in `code_chunks.content` (enables search without file I/O)
- Keep `chunk_fingerprints` as separate table (follows Study pattern, keeps core table lean)
- Index all FK columns plus composite indexes for common query patterns (21 total)
- `cycle_id` is a plain integer, not a FK to `cycle_reports` (cycles may be created after chunks)
- `cycle_reports(project_id, cycle_number)` has a UNIQUE index to enforce one report per cycle per project

### Flags for CEO
- None

### Flags for Next Step
- The Developer should use `executescript()` for the full DDL (same as Forge)
- `cycle_id` columns are plain integers — do not add FK constraints to `cycle_reports`
- CHECK constraints must be tested — see verification section item 5
