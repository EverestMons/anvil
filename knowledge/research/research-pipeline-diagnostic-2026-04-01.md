# Research Pipeline Evolution Diagnostic — Findings
**Date:** 2026-04-01 | **Source:** diagnostic-research-pipeline-2026-04-01.md (Step 1)

---

## Q1 — Current Schema

### Tables and Columns

| Table | Key Columns | Purpose |
|---|---|---|
| **projects** | id, name, path, last_scanned, created_at | Registered project metadata |
| **code_chunks** | id, project_id, file_path, chunk_type, name, content, content_hash, start_line, end_line, parent_chunk_id, cycle_id, structural_metadata (TEXT/JSON, added via migration) | Individual code units |
| **chunk_fingerprints** | id, chunk_id, content_hash, minhash_signature (BLOB), shingle_count, cycle_id | Content hashing + MinHash |
| **chunk_symbol_bindings** | id, chunk_id, symbol_name, binding_type, target_chunk_id | Typed relationships |
| **chunk_dependencies** | id, source_chunk_id, target_chunk_id, dependency_type, scope | Directed edges |
| **chunk_similarities** | id, chunk_a_id, chunk_b_id, similarity_score, cycle_id | Clone detection |
| **git_changes** | id, project_id, file_path, commit_hash, commit_date, commit_message, author | Per-file change history |
| **test_results** | id, project_id, run_date, total_tests, passed, failed, skipped, failed_test_names, cycle_id | Per-run test outcomes |
| **health_scores** | id, chunk_id, volatility_score, coverage_score, complexity_score, coupling_score, staleness_score, composite_score, cycle_id | Per-chunk health |
| **cycle_reports** | id, project_id, cycle_number, started_at, completed_at, files_scanned, chunks_extracted, chunks_scored, findings_count, report_path | Cycle summaries |

### Classification/Tagging in code_chunks
- **chunk_type** is constrained to: function, class, method, module, config, test_case
- **No functional_role column exists.** There is no field for "route_handler", "validation_gate", etc.
- **structural_metadata** (TEXT, JSON) stores: cyclomatic_complexity, nesting_depth, parameter_count, import_count, has_docstring, line_count — purely structural, no semantic/purpose data.
- **No provenance fields.** No execution_plan_id, no origin_commit, no creation_context.

### Binding Types in chunk_symbol_bindings
- Constrained to: defines, imports, calls, tests, documents
- No "implements", "configures", or purpose-oriented binding types.

### Extension Points Identified
- structural_metadata is already a flexible JSON field — could add purpose metadata alongside structural metrics without schema change.
- chunk_type CHECK constraint would need ALTER TABLE to add new types.
- No unused columns.

---

## Q2 — Current Extractor

### Per-Chunk Extraction Output
The extractor (`src/extractor.py` + `src/parsers/python_parser.py`) produces per chunk:
- **name** — function/class/method name
- **chunk_type** — function, class, method, test_case (classified by name prefix)
- **content** — raw source code
- **content_hash** — SHA-256 of content
- **start_line / end_line** — line range
- **parent_name** — enclosing class name (for methods)

### structural_metadata Fields
Computed by `python_parser.compute_structural_metadata()`:
- cyclomatic_complexity (weighted: If, For, While, Try, ExceptHandler, With, Assert, BoolOp)
- nesting_depth (max control flow nesting)
- parameter_count (args + kwonlyargs)
- import_count
- has_docstring (bool)
- line_count

### Symbol Extraction
`python_parser.extract_symbols()` returns:
- **imports** — module name, names, is_from, line
- **definitions** — name, type (function/class), bases (for classes), line
- **calls** — caller, callee, line
- **test_mappings** — test_name to tested_module (by filename convention)

### Existing Classification
Only name-based: `_classify_function()` returns "test_case" if name starts with `test_` or class starts with `Test`, "method" if inside a class, else "function". No semantic/purpose classification.

### What Would Need to Change for functional_role
1. Add a `functional_role` column to code_chunks (or store in structural_metadata JSON).
2. Create a classification function that takes chunk content + context (file path, imports, decorators, parent class bases) and maps to a taxonomy.
3. For provenance-based classification: a separate ingestion step that reads execution plan archives and dev logs to map {plan -> files_modified -> chunks}.
4. For heuristic classification: pattern matching on decorators (@app.route -> route_handler), naming conventions (test_ -> test_case, validate_ -> validation_gate), base classes (db.Model -> data_model), file path patterns (engines/ -> engine_module, templates/ -> template).

---

## Q3 — Current Scorer

### 5 Scoring Dimensions

| Dimension | Formula | Score Range | Meaning |
|---|---|---|---|
| **Volatility** | Recency-weighted commit count (exponential decay over GIT_HISTORY_WEEKS=4), then percentile-normalized | 0.0-1.0 | Higher = more frequently changed recently |
| **Coverage** | Binary: 0.0 if test_case, 1.0 if no test bindings, 0.5 if 1 test, 0.2 if 2+ tests | 0.0-1.0 | Higher = less tested |
| **Complexity** | Sigmoid(0.5*CC + 0.3*ND + 0.2*PC - 10) where CC=cyclomatic, ND=nesting depth, PC=param count | 0.0-1.0 | Higher = more complex |
| **Coupling** | Count(inbound deps + outbound deps), then percentile-normalized | 0.0-1.0 | Higher = more coupled |
| **Staleness** | Fraction of outbound dependencies whose files were modified more recently than this chunk's file | 0.0-1.0 | Higher = more stale |

### Composite Score
```
composite = 0.25*volatility + 0.25*coverage + 0.20*complexity + 0.15*coupling + 0.15*staleness
```
Clamped to [0.0, 1.0]. Higher = higher risk.

### What Would Need to Change for Purpose-Relative Scoring
Currently, all chunks are scored identically regardless of purpose. To make scoring purpose-aware:

1. **Role-specific weight profiles.** Example: a validation_gate chunk might weight complexity higher (complex validation is a smell), while an engine_module might tolerate higher complexity but weight coupling more.
2. **Role-specific thresholds.** A route_handler with CC > 5 is a problem; an engine_module with CC > 15 might be acceptable.
3. **Best-practices deviation scoring.** Compare chunk patterns against known best practices for its functional role. A validation_gate not using the strategy pattern would score higher risk.
4. Implementation: `SCORING_WEIGHTS` would become a dict of {functional_role: weights} instead of a flat dict. The `score_project()` function would look up the chunk's functional_role to select the appropriate weight profile.

---

## Q4 — Current Lab

### Finding Types (6 total)
1. **coverage_gaps** — untested chunks with high composite score (coverage >= 0.8 AND composite >= 0.7)
2. **coupling_hotspots** — chunks with coupling score >= 0.8, with inbound/outbound counts
3. **clone_candidates** — MinHash similarity pairs from chunk_similarities
4. **staleness_alerts** — chunks with staleness >= 0.8
5. **complexity_hotspots** — chunks with complexity score >= 0.8, with CC/depth/param details
6. **cochange_patterns** — file pairs that change together >= 5 times, with Jaccard similarity

### Cycle Report Format
Markdown report with:
- Executive Summary (total files, chunks, high risk count, avg composite, total findings)
- 6 finding sections with tables (capped at 30 entries each)
- Planner Constraints section (structured by type: coverage_required, verify_dependents, refactor_candidate, investigation_needed)
- Specialist Update Data (aggregate stats: function/class/method/test counts, deps, sims, avg score)

### Planner Constraint Types
- coverage_required — "file::name needs tests, composite X, volatility Y"
- verify_dependents — "file::name has N inbound + M outbound deps, verify before changes"
- refactor_candidate — "file_a::name <-> file_b::name similarity X" or "file::name complexity CC=Y depth=Z"
- investigation_needed — "file::name staleness X, deps updated but chunk unchanged"

### What Would Need to Change for Research-Backed Recommendations
Currently the Lab produces structural findings ("this is complex", "this has no tests") but not research-backed improvement recommendations ("for a validation_gate, use the strategy pattern to reduce complexity").

To evolve:
1. **Best practices lookup.** After identifying a finding (e.g., complexity hotspot), look up the chunk's functional_role in a best_practices table and produce a specific recommendation.
2. **Pattern matching.** Check if the chunk already follows known patterns (strategy, factory, etc.) or deviates.
3. **Research citations.** Link recommendations to sources (web research, established patterns).
4. New constraint types: "best_practice_deviation", "pattern_recommendation".

---

## Q5 — Config

### Current Configurables
| Setting | Default | Purpose |
|---|---|---|
| ANVIL_ROOT | (computed from file path) | Root directory |
| ANVIL_DB_PATH | anvil.db | Database location |
| SCAN_TARGETS | {"invoice-pulse": "/Users/.../invoice-pulse"} | Registered projects |
| EXCLUDED_DIRS | .git, __pycache__, node_modules, .venv, .vexp, target, .tox | Directory exclusions |
| EXCLUDED_EXTENSIONS | .pyc, .pyo, .so, .dylib, .db, etc. | File type exclusions |
| MINHASH_NUM_PERM | 128 | MinHash permutation count |
| MINHASH_THRESHOLD | 0.7 | Similarity threshold |
| GIT_HISTORY_WEEKS | 4 | Volatility window |
| SCORING_WEIGHTS | {vol: 0.25, cov: 0.25, comp: 0.20, coup: 0.15, stale: 0.15} | Composite weights |
| HIGH_RISK_THRESHOLD | 0.7 | Lab finding thresholds |
| COVERAGE_GAP_THRESHOLD | 0.8 | |
| COUPLING_HOTSPOT_THRESHOLD | 0.8 | |
| STALENESS_THRESHOLD | 0.8 | |
| COMPLEXITY_THRESHOLD | 0.8 | |
| COCHANGE_MIN_COUNT | 5 | |

### What Would Need to Be Added

1. **Functional role taxonomy:** List of roles with descriptions and optional hierarchy.
2. **Role-specific scoring weights:** Override weights per functional_role.
3. **Classification heuristics:** Decorator patterns, naming patterns, file path patterns, base class patterns for heuristic role assignment.
4. **Best practices patterns per role:** Either in config or in a new DB table.
5. **Dev log / plan archive paths:** For provenance ingestion.

---

## Q6 — Execution Plan Format Analysis

### Plan Archive Overview
- **297 files** in `invoice-pulse/knowledge/decisions/Done/`
- **~171 executable plans**, **~95 diagnostics**, rest are orchestration/roadmap/prompt files
- Date range: 2026-03-12 through 2026-04-01

### Plan Format (Markdown Structure)
Highly standardized:
- H1 title with feature name
- Metadata header: Date, Tier, Execution (role sequence)
- "How to Run This Plan" bootstrap section
- H2 per step: `## STEP N -- ROLE_NAME (Description)`
- Blockquotes (`>`) containing detailed role instructions
- Horizontal dividers between steps
- References to external knowledge files (diagnostics, blueprints, design specs)

### Do Plans Reference Specific Files?
**Yes, prescriptively** — plans tell agents which files to modify ("In `web/templates/contracts_list.html`, add...", "Create `web/static/copilot-inline.js`"). But this is scattered through prose instructions, not in a structured list. **Not reliably machine-parseable from plan text alone.**

### Feature Descriptions as Functional Purpose Labels
**Excellent quality.** Plans contain rich functional descriptions:
- "Carrier name autofill using datalist on contracts search input"
- "Rules Tariff dashboard with card-grid layout for data categories"
- "Copilot Inline Redesign -- rebuild widget using design system classes"

These descriptions directly serve as functional purpose labels for the code they produce.

### Can We Parse Plan -> Files Mapping?
**Not reliably from plans.** Plans use prescriptive language with conditional logic ("If yes, separate table. If no, columns on existing table"). The actual files created/modified are documented in **dev logs**, not plans.

### Dev Log Output Receipts — The Reliable Source
**Every dev log** contains a structured "Output Receipt" with a "Files Created or Modified (Code)" section:
```
### Files Created or Modified (Code)
- contract_tables.py -- added table 54 activity_note_classifications + 3 indexes
- engines/note_classifier.py -- NEW, 410 lines, full classifier engine
- tests/test_note_classifier.py -- NEW, 51 tests
```

This is **consistently formatted, machine-parseable, and the source of truth** for what each execution plan actually produced.

### Provenance Chain
```
execution plan (feature description + instructions)
    -> dev log (Output Receipt with exact files modified)
        -> code_chunks (parsed from those files)
```

To build provenance: parse dev logs, not plans. The dev log names reference the plan names (by date and feature slug), making the linkage traceable.

---

## Schema Extension Proposal

### New Tables

#### 1. `functional_roles` (taxonomy table)
```sql
CREATE TABLE functional_roles (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    description TEXT,
    parent_role TEXT REFERENCES functional_roles(name),
    scoring_weights TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
```

#### 2. `chunk_provenance` (execution plan lineage)
```sql
CREATE TABLE chunk_provenance (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id        INTEGER NOT NULL REFERENCES code_chunks(id) ON DELETE CASCADE,
    plan_name       TEXT NOT NULL,
    dev_log_path    TEXT,
    plan_description TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
```

#### 3. `best_practices` (knowledge base)
```sql
CREATE TABLE best_practices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    functional_role TEXT NOT NULL REFERENCES functional_roles(name),
    pattern_name    TEXT NOT NULL,
    description     TEXT NOT NULL,
    detection_hint  TEXT,
    source          TEXT,
    severity        TEXT DEFAULT 'medium',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### New Columns on Existing Tables

#### code_chunks
```sql
ALTER TABLE code_chunks ADD COLUMN functional_role TEXT REFERENCES functional_roles(name);
```
- Stores the classified functional purpose of each chunk.
- Nullable — chunks without provenance or heuristic match get NULL (handled as "unclassified").

### New Config Entries

- `FUNCTIONAL_ROLES` — initial taxonomy seed list
- `ROLE_SCORING_WEIGHTS` — per-role weight overrides
- `DEV_LOG_PATHS` — paths to dev log archives for provenance ingestion
- `PLAN_ARCHIVE_PATHS` — paths to execution plan archives

### Minimal Pipeline Changes for Phases 7-9

| Phase | Pipeline Stage | Change |
|---|---|---|
| **7: Classification** | Extractor (new post-step) | Add `classify_chunks()` that assigns functional_role via heuristics (decorator patterns, naming, file paths, base classes). Store on code_chunks.functional_role. |
| **7: Provenance** | New ingestion module | Add `ingest_provenance()` that parses dev log Output Receipts, extracts {plan -> files}, and populates chunk_provenance table. |
| **8: Best Practices** | New knowledge module | Add `best_practices_kb.py` that seeds and queries the best_practices table. Initial seed from config; later enriched via web research. |
| **8: Purpose-Aware Scoring** | Scorer | Modify `score_project()` to look up chunk.functional_role and use role-specific weights from ROLE_SCORING_WEIGHTS. Fallback to default weights for unclassified. |
| **9: Research Recommendations** | Lab | Modify Lab finding generators to cross-reference best_practices table. New finding type: "best_practice_deviation". Lab report includes specific recommendations per functional role. |

### Key Design Decision: Dev Logs as Provenance Source
Parse dev log Output Receipts ("Files Created or Modified (Code)" sections), NOT execution plan prose. Dev logs are structured, consistent, and the source of truth for what was actually built. Plans describe intent; dev logs describe outcome.
