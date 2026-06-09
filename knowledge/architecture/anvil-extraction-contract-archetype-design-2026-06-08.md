# Anvil — Extraction Contract + Archetype-Pluggable Classifier Design Blueprint

**Date:** 2026-06-08
**Author:** Anvil Systems Analyst
**Status:** Design blueprint — read-only diagnostic, no source modifications
**Scope:** Formalise the extraction contract that decouples the core engine from any single language parser; design an archetype-keyed classifier registry so every Eluvian project classifies correctly instead of falling through to `utility`.

---

## A. Current De Facto Extraction Contract

### A.1 Chunk Record Produced by `python_parser.parse_file()`

`src/parsers/python_parser.py:15-58` emits a list of dicts, each with:

| Field | Type | Semantics | Populated by |
|---|---|---|---|
| `name` | `str` | AST node name (`node.name`) — function, class, or method identifier | Parser |
| `chunk_type` | `str` | One of `function`, `class`, `method`, `test_case` — determined by `_classify_function()` | Parser |
| `content` | `str` | Raw source text from `start_line` to `end_line` | Parser |
| `content_hash` | `str` | SHA-256 of `content` | Parser |
| `start_line` | `int` | `node.lineno` (1-based) | Parser |
| `end_line` | `int` | `node.end_lineno` | Parser |
| `parent_name` | `str \| None` | Class name for methods; `None` for top-level functions and classes | Parser |

### A.2 Symbol Data from `python_parser.extract_symbols()`

`src/parsers/python_parser.py:90-170` returns a dict with four keys:

| Key | Shape | Python-specific? |
|---|---|---|
| `imports` | `[{module, names, is_from, line}]` | Yes — uses `ast.Import`/`ast.ImportFrom` nodes |
| `definitions` | `[{name, type, line, bases?}]` | Yes — uses `ast.FunctionDef`/`ast.ClassDef` |
| `calls` | `[{caller, callee, line}]` | Yes — uses `ast.Call` node traversal |
| `test_mappings` | `[{test_name, tested_module}]` | Partially — naming convention (`test_*`) is cross-language, but AST walk is Python-specific |

### A.3 Structural Metadata from `python_parser.compute_structural_metadata()`

`src/parsers/python_parser.py:205-262` returns:

| Field | Type | Python-specific? |
|---|---|---|
| `cyclomatic_complexity` | `int` | **Yes** — counts `ast.If`, `ast.For`, `ast.While`, `ast.Try`, `ast.ExceptHandler`, `ast.With`, `ast.Assert`, `ast.BoolOp` nodes |
| `nesting_depth` | `int` | **Yes** — recurses through `ast.If`, `ast.For`, `ast.While`, `ast.Try`, `ast.With` |
| `parameter_count` | `int` | **Yes** — reads `ast_node.args.args + ast_node.args.kwonlyargs` |
| `import_count` | `int` | **Yes** — counts `ast.Import`/`ast.ImportFrom` |
| `has_docstring` | `bool` | **Yes** — checks `ast.Constant` string as first body statement |
| `line_count` | `int` | Language-agnostic (line arithmetic) |

### A.4 DB Schema: `code_chunks` Table

`src/db.py:35-50` — the persisted chunk record:

```
id, project_id, file_path, chunk_type, name, content, content_hash,
start_line, end_line, parent_chunk_id, created_at, updated_at,
cycle_id, last_seen_cycle
```

Plus migration-added columns:
- `structural_metadata TEXT` — JSON blob from `compute_structural_metadata()`
- `functional_role TEXT` — set by `classifier.py`

**`chunk_type` CHECK constraint:** `('function', 'class', 'method', 'module', 'config', 'test_case')` — this is Python-centric. A Swift extractor would need `struct`, `enum`, `extension`, `protocol`; a TS/JS extractor would need `arrow_function`, `component`, `hook`, `type_alias`.

### A.5 Where Each Piece Comes From

| Data | Origin | Language-bound? |
|---|---|---|
| Chunk record (7 fields) | `python_parser.parse_file()` | **Yes** — Python AST |
| Symbols (imports/defs/calls/tests) | `python_parser.extract_symbols()` | **Yes** — Python AST |
| Structural metadata (6 fields) | `python_parser.compute_structural_metadata()` | **Yes** — Python AST node types |
| SQLAlchemy model bindings | `python_parser.detect_sqlalchemy_models()` | **Yes** — Python-specific (framework-specific even) |
| Content hash for change detection | `scanner.compute_file_hash()` | No — byte-level SHA-256 |
| Git history for volatility | `scanner.ingest_git_history()` | No — git log parsing |
| Dependency resolution | `extractor.resolve_dependencies()` | Mostly no — resolves via symbol name matching, but **import resolution** strategy assumes Python module paths |
| MinHash fingerprints | `extractor.compute_fingerprints()` | No — text shingle-based |

### A.6 Downstream Consumer Field Access Map

**Classifier (`src/classifier.py:88-123` — `classify_chunk()`)**:
- `chunk_type` — skip module/test_case, override config
- `name` — NAME_RULES regex matching
- `file_path` — FILE_PATH_RULES regex matching
- `content` — DECORATOR_RULES regex on first 10 lines
- **All rules are invoice-pulse-specific** (Flask decorators, gate/validator names, IP file paths)

**Scorer (`src/scorer.py`)**:
- `file_path` → `compute_volatility()` queries `git_changes` — **language-agnostic**
- `chunk_id`, `chunk_type` → `compute_coverage()` queries `chunk_symbol_bindings` — **language-agnostic**
- `structural_metadata` (JSON) → `compute_complexity()` reads `cyclomatic_complexity`, `nesting_depth`, `parameter_count` — **language-agnostic at read time** (consumes normalised numbers; the numbers themselves were produced by Python-specific computation)
- `chunk_id` → `compute_coupling()` queries `chunk_dependencies` count — **language-agnostic**
- `chunk_id`, `file_path`, `project_id` → `compute_staleness()` queries git + deps — **language-agnostic**
- `functional_role` → `compute_composite()` selects weights via `ROLE_SCORING_WEIGHTS` — **archetype-specific** (weights currently tuned for invoice-pulse)

**Lab (`src/lab.py`)** — all finding functions:
- Read from `health_scores` + `code_chunks` joined on `chunk_id` — **language-agnostic**
- `find_best_practice_deviations()` reads `content`, `structural_metadata`, `functional_role` → calls `detector.check_best_practice()` — **content regex patterns are partially language-specific** (e.g., `request.form[` is Flask/Python)
- `find_complexity_hotspots()` reads `structural_metadata` JSON — **language-agnostic at read time**
- `find_intent_gaps()` reads PROJECT_BRIEF.md from project path — **language-agnostic**

**Detector (`src/detector.py`)**:
- CONTENT_CHECKS regex patterns: `except\s*:` (Python), `request.form[` (Flask), `\bconn\b` (generic), `\bopen\s*\(` (generic), `datetime.now()` (Python), `CREATE TABLE` (SQL, generic) — **mixed Python/Flask/generic**

### A.7 Summary: What Is Language-Agnostic vs Python-Specific

**Language-agnostic (the handle)**:
- Scanner (file discovery, content hashing, git history)
- DB schema (with chunk_type constraint loosened)
- Scorer (all five dimensions — consumes normalised data)
- Lab (all seven finding types — reads scores and metadata)
- MinHash fingerprinting and similarity detection
- Cycle orchestration (`cycle.py`)

**Python-specific (a head)**:
- `python_parser.py` — all four exported functions
- `extractor.py:52` — `py_modules = [m for m in module_chunks if m["file_path"].endswith(".py")]`
- `extractor.py:142-174` — direct `ast.parse()` calls for symbol extraction and metadata
- `extractor.py:395-547` — import resolution assumes Python module path conventions (`foo/bar.py` → `foo.bar`)

**Archetype-specific (a head)**:
- `classifier.py` — entire rule chain (DECORATOR_RULES, NAME_RULES, FILE_PATH_RULES)
- `db.py:520-551` — FUNCTIONAL_ROLE_SEEDS (25 invoice-pulse roles)
- `db.py:604-670` — BEST_PRACTICE_SEEDS (15 invoice-pulse practices)
- `config.py:75-132` — ROLE_SCORING_WEIGHTS and ROLE_THRESHOLDS
- `detector.py:15-63` — CONTENT_CHECKS and STRUCTURAL_CHECKS (mixed IP/generic)

---

## B. Proposed Extraction Contract (The Keystone)

### B.1 ChunkRecord Interface

The minimal normalised record the core requires from any language extractor:

```python
class ChunkRecord(TypedDict):
    # === Required (every extractor MUST emit) ===
    name: str                    # Chunk identifier (function/class/method name)
    file_path: str               # Relative path from project root
    chunk_type: str              # Normalised type (see B.2)
    content: str                 # Raw source text
    content_hash: str            # SHA-256 hex digest of content
    start_line: int              # First line (1-based)
    end_line: int                # Last line (1-based, inclusive)
    parent_name: str | None      # Enclosing scope name, or None for top-level

    # === Optional (extractor MAY emit; downstream defaults apply if absent) ===
    structural_metadata: StructuralMetadata | None
    symbols: SymbolData | None
```

```python
class StructuralMetadata(TypedDict):
    cyclomatic_complexity: int   # Branch count metric (language-specific computation,
                                 #   normalised meaning: 1=linear, higher=more branches)
    nesting_depth: int           # Max control-flow nesting depth
    parameter_count: int         # Input parameter count (args + kwargs equivalent)
    import_count: int            # Number of import statements in scope
    has_docstring: bool          # Whether the chunk has a leading doc comment
    line_count: int              # end_line - start_line + 1
```

```python
class SymbolData(TypedDict):
    imports: list[ImportRecord]
    definitions: list[DefinitionRecord]
    calls: list[CallRecord]
    test_mappings: list[TestMappingRecord]

class ImportRecord(TypedDict):
    module: str                  # Module/package being imported
    names: list[str]             # Specific symbols imported (empty = whole module)
    is_from: bool                # True for `from X import Y` style
    line: int

class DefinitionRecord(TypedDict):
    name: str
    type: str                    # 'function', 'class', 'method', etc.
    line: int
    bases: list[str]             # For classes: base class names (optional)

class CallRecord(TypedDict):
    caller: str                  # Enclosing function name, or '<module>'
    callee: str                  # Called function/method name
    line: int

class TestMappingRecord(TypedDict):
    test_name: str               # Name of the test function
    tested_module: str           # Module being tested (convention-based)
```

### B.2 Normalised `chunk_type` Vocabulary

The current CHECK constraint `('function', 'class', 'method', 'module', 'config', 'test_case')` must be relaxed. The core needs a small universal vocabulary that every language maps into:

| Core type | Python maps to | Swift maps to | TS/JS maps to |
|---|---|---|---|
| `function` | top-level function | free function | function / arrow function |
| `class` | class | class | class |
| `method` | method in class | method in class/struct/enum | method in class |
| `module` | file-level | file-level | file-level |
| `test_case` | `test_*` function | XCTest method | `it()`/`test()` |
| `config` | config file | — | — |
| `struct` | — | struct | — |
| `enum` | — | enum | enum |
| `protocol` | — | protocol | — |
| `component` | — | SwiftUI View body | React component |
| `type_alias` | — | typealias | type / interface |

**Decision:** Change the CHECK constraint to allow **any string** (drop the enum), and define the universal types in code as a set constant. Language extractors map their constructs into this vocabulary. The core only branches on `module` and `test_case` (which are universal); all other types flow through classification and scoring without type-specific logic.

### B.3 Producer Interface (Language Extractor "Head")

```python
class LanguageExtractor(Protocol):
    """Interface that every language extractor must implement."""

    language: str                # e.g. 'python', 'swift', 'typescript'
    file_extensions: set[str]    # e.g. {'.py'}, {'.swift'}, {'.ts', '.tsx', '.js', '.jsx'}

    def parse_file(self, file_path: str) -> list[ChunkRecord]:
        """Parse a source file and return chunk records."""
        ...

    def extract_symbols(self, file_path: str, source: str) -> SymbolData:
        """Extract symbol data from a source file."""
        ...

    def compute_structural_metadata(self, chunk_content: str,
                                     chunk_type: str) -> StructuralMetadata:
        """Compute structural metrics for a single chunk."""
        ...
```

**Registry:**
```python
# src/parsers/registry.py
EXTRACTORS: dict[str, LanguageExtractor] = {}

def register(extractor: LanguageExtractor) -> None:
    for ext in extractor.file_extensions:
        EXTRACTORS[ext] = extractor

def get_extractor(file_extension: str) -> LanguageExtractor | None:
    return EXTRACTORS.get(file_extension)
```

### B.4 What the Core Must STOP Assuming About Python

| Current assumption | Location | Required change |
|---|---|---|
| Only `.py` files are extracted | `extractor.py:52` (`file_path.endswith(".py")`) | Dispatch via `registry.get_extractor(ext)` instead of hardcoding `.py` |
| `ast.parse()` called directly in extractor | `extractor.py:143-148` | Delegate to `extractor.extract_symbols()` and `extractor.compute_structural_metadata()` |
| `_store_file_metadata()` walks Python AST | `extractor.py:342-374` | Call `extractor.compute_structural_metadata()` per chunk |
| `detect_sqlalchemy_models()` called for every file | `extractor.py:161-171` | Move into Python extractor as a post-parse hook; other extractors won't have SA models |
| `chunk_type` CHECK constraint is a closed Python set | `db.py:39` | Relax to allow any string, or expand the set to include all known types |
| `_classify_function()` uses Python conventions | `python_parser.py:61-68` | This stays inside the Python extractor — fine |
| Import resolution assumes `foo/bar.py` → `foo.bar` | `extractor.py:422-423` | Abstract into extractor interface or make `resolve_dependencies()` accept a module-path resolver callback |

### B.5 Concrete Decoupling Edits Required (Not Implemented Here)

1. **`src/parsers/registry.py`** — NEW FILE: extractor registry with `register()` and `get_extractor()`.

2. **`src/parsers/python_parser.py`** — Wrap in a class implementing `LanguageExtractor` protocol. No logic changes; just structural encapsulation. `language = "python"`, `file_extensions = {".py"}`.

3. **`src/extractor.py:52`** — Replace `file_path.endswith(".py")` with `registry.get_extractor(os.path.splitext(file_path)[1]) is not None`.

4. **`src/extractor.py:70`** — Replace `python_parser.parse_file(abs_path)` with `extractor_for_file.parse_file(abs_path)`.

5. **`src/extractor.py:142-174`** — Replace direct `ast.parse()` + `python_parser.extract_symbols()` + `python_parser.compute_structural_metadata()` with calls through the extractor instance obtained from the registry.

6. **`src/extractor.py:161-171`** — Move `detect_sqlalchemy_models()` call into `PythonExtractor.parse_file()` as a post-parse hook, or into a separate `post_extract_hooks` mechanism.

7. **`src/extractor.py:395-547` (`resolve_dependencies()`)** — Abstract the module-path resolution logic (`mod_name = c["file_path"].replace("/", ".").replace(".py", "")` at line 422-423) into a method on `LanguageExtractor` so each language can define its own module resolution. The core dependency resolution loop (matching symbol names to chunks) stays language-agnostic.

8. **`src/db.py:39`** — Change `chunk_type` CHECK constraint: either drop it (simplest) or expand to a broader set. Recommend dropping it: `chunk_type TEXT NOT NULL` (the constraint provides no safety benefit when multiple languages contribute types, and the valid set is defined in code).

---

## C. Archetype-Pluggable Classifier

### C.1 Current Classifier: Global Regex Chain

`src/classifier.py` implements a flat priority chain:

1. **chunk_type overrides** — `module`, `test_case` → skip; `config` → `configuration`
2. **DECORATOR_RULES** (4 rules) — all Flask `@route`-style patterns → `route_handler`
3. **NAME_RULES** (21 rules) — invoice-pulse naming conventions (`gate_\d+_`, `validate_invoice`, `run_ingestion`, etc.)
4. **FILE_PATH_RULES** (30 rules) — invoice-pulse directory structure (`engines/confidence.py`, `web/reporting.py`, etc.)
5. **Fallback** → `utility`

**Problem:** Every chunk in a non-invoice-pulse project falls through to step 5 and classifies as `utility`, because steps 2-4 are all invoice-pulse-specific. The bellows project (autonomous daemon) has no Flask routes, no validation gates, no `engines/` directory. Every function classifies as `utility`, making role-specific scoring weights and thresholds meaningless.

### C.2 Role → Scoring Coupling

`src/scorer.py:115`: `weights = ROLE_SCORING_WEIGHTS.get(role, SCORING_WEIGHTS)`

`src/config.py:75-108`: Override weights exist for 8 roles — all invoice-pulse roles. If a project classifies everything as `utility`, all chunks use the `utility` weights (`complexity: 0.30`, `coverage: 0.20`) regardless of their actual function.

`src/config.py:111-132`: ROLE_THRESHOLDS override complexity and coupling thresholds for 5 roles — again all invoice-pulse.

`src/lab.py:143-168` (`find_coupling_hotspots`): Uses `ROLE_THRESHOLDS.get(role, {})` to get per-role coupling thresholds.

`src/lab.py:238-280` (`find_complexity_hotspots`): Uses `ROLE_THRESHOLDS.get(role, {})` to get per-role complexity thresholds.

This means the classifier's output directly controls which scoring weights and lab thresholds apply. A bad classifier doesn't just produce wrong labels — it produces wrong scores and wrong findings.

### C.3 Proposed: Archetype-Keyed Classifier Registry

**Concept:** A project declares its `(language, archetype)`. The classifier loads the archetype's role taxonomy (roles + rules) and the archetype-specific scoring profiles (weights + thresholds).

#### Archetype Definition Structure

```python
class ArchetypeDefinition:
    name: str                    # e.g. 'flask_service', 'daemon', 'tauri_react_app'
    description: str
    roles: list[RoleDef]         # Role taxonomy for this archetype
    decorator_rules: list[tuple] # (compiled_regex, role_name)
    name_rules: list[tuple]      # (compiled_regex, role_name)
    file_path_rules: list[tuple] # (compiled_regex, role_name)
    scoring_weights: dict[str, dict]   # role -> {volatility, coverage, ...}
    role_thresholds: dict[str, dict]   # role -> {complexity_threshold, ...}
    best_practices: list[tuple]  # (role, pattern_name, description, hint, source, severity)
    content_checks: dict         # pattern_name -> [{pattern, message}]
```

#### Registry

```python
# src/classifier_registry.py
ARCHETYPES: dict[str, ArchetypeDefinition] = {}

def register_archetype(archetype: ArchetypeDefinition) -> None:
    ARCHETYPES[archetype.name] = archetype

def get_archetype(name: str) -> ArchetypeDefinition | None:
    return ARCHETYPES.get(name)
```

#### Modified `classify_chunk()`

```python
def classify_chunk(chunk_dict: dict, archetype: ArchetypeDefinition) -> str | None:
    chunk_type = chunk_dict.get("chunk_type", "")
    if chunk_type in ("module", "test_case"):
        return None
    if chunk_type == "config":
        return "configuration"

    # Use archetype-specific rules
    content_head = "\n".join(chunk_dict.get("content", "").split("\n")[:10])
    for pattern, role in archetype.decorator_rules:
        if pattern.search(content_head):
            return role
    for pattern, role in archetype.name_rules:
        if pattern.search(chunk_dict.get("name", "")):
            return role
    for pattern, role in archetype.file_path_rules:
        if pattern.search(chunk_dict.get("file_path", "")):
            return role

    return "utility"
```

#### Modified Scorer

```python
# scorer.py
def score_project(conn, project_name, cycle_id, archetype):
    ...
    weights = archetype.scoring_weights.get(role, SCORING_WEIGHTS)
    ...
```

### C.4 Rule Location: Three Options Evaluated

| Option | Description | Pros | Cons |
|---|---|---|---|
| **(a) Central** | All archetype defs live in `anvil/src/archetypes/` | Single source of truth; easy to test; versioned with anvil | Projects can't customise without modifying anvil |
| **(b) Per-project** | Each project has `knowledge/anvil-roles.toml` or similar | Full project autonomy; no anvil changes per project | Duplication across same-archetype projects; harder to test; version drift |
| **(c) Hybrid** | Archetype templates in anvil; per-project override file merges on top | Templates eliminate duplication; overrides allow customisation | Slightly more complex merge logic |

**Recommendation: (a) Central, with a path to (c) hybrid if needed.**

Rationale:
- The shop has ~7-10 projects across ~5 archetypes. This is a **small, controlled** population under one CEO's authority.
- Archetype templates are a shop-level concern — they should live with the tool, not scattered across projects.
- Per-project overrides add merge complexity for a benefit that may never materialise. If a project needs one extra role, adding it to the archetype template costs nothing (the other projects in the same archetype just ignore it if no chunks match).
- The SCAN_TARGETS dict already centralises project registration. Adding `(language, archetype)` metadata there is natural.
- **Escape hatch:** If a project truly needs unique rules beyond its archetype, we add (c) hybrid later — the central templates remain the base layer, and a `knowledge/anvil-overrides.toml` in the project merges on top. This is additive, not a rewrite.

### C.5 Project → (Language, Archetype) Declaration

Extend `SCAN_TARGETS` in `src/config.py`:

```python
# Current:
SCAN_TARGETS = {
    "invoice-pulse": "/Users/marklehn/Developer/GitHub/invoice-pulse",
    "bellows": "/Users/marklehn/Developer/GitHub/bellows",
}

# Proposed:
SCAN_TARGETS = {
    "invoice-pulse": {
        "path": "/Users/marklehn/Developer/GitHub/invoice-pulse",
        "language": "python",
        "archetype": "flask_service",
    },
    "bellows": {
        "path": "/Users/marklehn/Developer/GitHub/bellows",
        "language": "python",
        "archetype": "daemon",
    },
}
```

This is a breaking change for all code that reads `SCAN_TARGETS[name]` as a plain path. Required updates:
- `scanner.py:38` — `project_path = SCAN_TARGETS[project_name]` → `SCAN_TARGETS[project_name]["path"]`
- `scorer.py:356` — `project_path = SCAN_TARGETS.get(project_name)` → `SCAN_TARGETS.get(project_name, {}).get("path")`
- `extractor.py:39` — same pattern
- `config.py:136-138` (`DEV_LOG_PATHS`) — could be folded into SCAN_TARGETS as an optional `dev_log_dir` field

### C.6 Invoice-Pulse → First Archetype Head

The existing rules collapse to **one** archetype: `flask_service`.

Invoice-pulse is a Flask web application with a validation pipeline, intelligence engines, ingestion layer, and supporting infrastructure. All 25 roles, all classifier rules, all scoring weight overrides, all best practices, and all content checks describe this single archetype.

**Migration:**
1. Create `src/archetypes/flask_service.py` containing the current FUNCTIONAL_ROLE_SEEDS (as `roles`), DECORATOR_RULES/NAME_RULES/FILE_PATH_RULES (as rules), ROLE_SCORING_WEIGHTS/ROLE_THRESHOLDS (as scoring profiles), BEST_PRACTICE_SEEDS (as practices), and CONTENT_CHECKS/STRUCTURAL_CHECKS (as detection rules).
2. Register it via `register_archetype()` at module import.
3. Remove the seeds from `db.py` and `config.py` — they become archetype-specific data.

**The IP rules do NOT split across several archetypes.** They form a single coherent role taxonomy for a Flask service with domain-specific engines.

### C.7 Bellows → Second Archetype Head (Daemon)

Bellows is an autonomous CLI daemon that orchestrates plan dispatch, worktree management, and agent lifecycle. A preliminary role taxonomy:

| Role | Description | Group |
|---|---|---|
| `plan_dispatcher` | Reads decision files, resolves dependencies, dispatches to agents | orchestration |
| `worktree_manager` | Creates/tears down git worktrees for parallel execution | orchestration |
| `agent_lifecycle` | Spawns, monitors, and collects results from Claude Code agents | orchestration |
| `config_loader` | Reads `.bellows.toml`, SCAN_TARGETS, project manifests | configuration |
| `cache_manager` | Manages `.bellows-cache/` diagnostic and plan files | infrastructure |
| `git_operator` | Branch creation, commit, push, PR creation via `gh` | infrastructure |
| `template_engine` | Renders plan templates with variable substitution | infrastructure |
| `cli_command` | User-facing CLI entry points | interface |
| `utility` | Generic helpers | infrastructure |

Classifier rules would match bellows' file/naming conventions (e.g., `dispatch*.py` → `plan_dispatcher`, `worktree*.py` → `worktree_manager`). These need to be authored after reading bellows' source — this diagnostic does not attempt that; it defines the slot the bellows archetype will fill.

### C.8 Functional Role Seeding Migration

Currently `db.py:_seed_functional_roles()` and `db.py:_seed_best_practices()` run on every `init_db()` call with hardcoded invoice-pulse data. This must change:

1. `init_db()` creates empty `functional_roles` and `best_practices` tables (schema only, no seeds).
2. `cycle.py:run_cycle()` loads the archetype for the project being cycled and seeds the roles/practices for that archetype (idempotent via `INSERT OR IGNORE`).
3. The `functional_roles` table gets an `archetype TEXT` column so roles from different archetypes coexist.

---

## D. Study Cross-Repo Reference (Shape Only)

### D.1 Study's Chunk Schema

**Location:** `/Users/marklehn/Developer/GitHub/study/src-tauri/migrations/001_v2_schema.sql`

```sql
CREATE TABLE IF NOT EXISTS chunks (
    id                  TEXT PRIMARY KEY,
    material_id         TEXT NOT NULL,
    course_id           TEXT NOT NULL,
    label               TEXT,
    content             TEXT,
    content_hash        TEXT NOT NULL,
    char_count          INTEGER,
    source_format       TEXT,           -- 'epub', 'docx', 'text'
    heading_level       INTEGER,
    section_path        TEXT,
    structural_metadata TEXT,           -- JSON
    fidelity            TEXT DEFAULT 'full',
    page_start          INTEGER,
    page_end            INTEGER,
    ordering            INTEGER,
    status              TEXT DEFAULT 'pending',
    ...
    FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);
```

### D.2 Producer: `src/lib/chunker.js`

The chunker accepts parsed document content (from epub/docx/text parsers) and emits normalised chunk objects:

```javascript
// Output shape:
{
    materialId, courseId, label, content, contentHash,
    charCount, sourceFormat, headingLevel, sectionPath,
    structuralMetadata, fidelity, pageStart, pageEnd, ordering
}
```

The chunker is classification-aware: it uses `SPLIT_LEVELS[classification]` to decide heading-level splits (textbooks split at H2, syllabi don't split, etc.). But the **output schema is identical** regardless of input format — epub, docx, and plain text all produce the same chunk shape.

### D.3 Consumer: `src/lib/study.js`

The tutoring/retrieval path reads chunks through a binding layer (`chunk_facet_bindings`):

```javascript
// Consumer reads:
loadChunksForBindings(bindings, { charLimit: 24000 })
// Returns: { chunkId, label, content, bindingType, facetId, ordering, sectionPath, materialId }
```

The consumer is **completely source-agnostic**. It never checks `source_format`, never branches on whether the chunk came from an epub or a docx. It reads `content`, `label`, `ordering`, and `sectionPath` — all normalised by the chunker.

### D.4 Assessment: CLEAN Normalised Contract

**Verdict: CLEAN.** Evidence:

1. **One schema, multiple input types:** The `chunks` table stores content from epub, docx, text, and PDF sources. The consumer never knows or cares about the source format.

2. **Producer boundary is well-defined:** `chunker.js` is the single producer. It takes `(parsedDocument, options)` and returns `ChunkRecord[]`. The parsers (epub parser, docx parser, text parser) each produce a common intermediate format that the chunker consumes.

3. **Consumer is source-agnostic:** `study.js` queries chunks by facet bindings, never by source format. The retrieval path treats all chunks identically.

4. **Binding layer creates a clean seam:** `chunk_facet_bindings` decouples chunk content from its semantic role (what skills it teaches). This is analogous to Anvil's `functional_role` column + `chunk_symbol_bindings`.

### D.5 Transferable Shape Lessons for Anvil

1. **The chunker output object is the contract.** Study defined exactly what a chunk looks like (`id`, `content`, `contentHash`, `charCount`, `structuralMetadata`, etc.) and made every parser produce that shape. Anvil should do the same: `ChunkRecord` is the contract, every `LanguageExtractor` produces it.

2. **Classification-aware splitting, format-agnostic output.** Study's chunker uses `SPLIT_LEVELS[classification]` to vary splitting strategy by document type, but the output schema doesn't change. Anvil's analogue: language extractors may use different AST libraries (Python `ast`, Swift SourceKit, TS `typescript` compiler API) but must produce identical `ChunkRecord`s.

3. **Structural metadata as a JSON blob.** Study stores `structural_metadata` as a JSON column on the chunks table — same as Anvil. The consumer reads it without knowing how it was computed. This pattern is correct: keep the metadata schema stable, let the producer fill it language-specifically.

4. **The consumer never imports the producer.** Study's `study.js` never imports `chunker.js`. It reads from the database. This is already true in Anvil (scorer/lab read from DB, not from parser) and must remain true — the core must never import `python_parser` directly.

---

## E. Synthesis & Sequenced Build Plan

### E.1 Handle/Heads Architecture

```
                        ┌────────────────────────┐
                        │   ANVIL CORE (handle)   │
                        │                         │
                        │  Scanner (file discover) │
                        │  DB schema + CRUD        │
                        │  Scorer (5 dimensions)   │
                        │  Lab (7 finding types)   │
                        │  Cycle orchestrator      │
                        │  MinHash fingerprinting  │
                        │  Bellows integration     │
                        └────────┬───────┬────────┘
                                 │       │
                    ┌────────────┘       └────────────┐
                    │                                  │
          ┌─────────┴──────────┐            ┌─────────┴──────────┐
          │  Language Heads    │            │  Archetype Heads   │
          │                    │            │                    │
          │  PythonExtractor   │            │  flask_service     │
          │  [SwiftExtractor]  │            │  daemon            │
          │  [TSExtractor]     │            │  [tauri_react_app] │
          │                    │            │  [swiftui_app]     │
          └────────────────────┘            │  [cli_pipeline]    │
                                            └────────────────────┘
```

**Invariant core (handle):**
- ChunkRecord contract (TypedDict)
- LanguageExtractor protocol
- ArchetypeDefinition structure
- Registries (language + archetype)
- Scanner, DB, Scorer, Lab, Cycle, Fingerprinting
- Bellows integration (worktree dispatch, result collection)

**Variant heads:**
- Language extractors: Python (exists), Swift (future), TS/JS (future)
- Archetype classifiers: flask_service (from current IP rules), daemon (new for bellows), tauri_react_app (future), swiftui_app (future), cli_pipeline (future)

### E.2 Dependency-Ordered Build Sequence

#### Step 1: Contract Definition
**What:** Define `ChunkRecord`, `StructuralMetadata`, `SymbolData`, `LanguageExtractor` protocol, `ArchetypeDefinition` structure. Create `src/parsers/registry.py` and `src/classifier_registry.py`.
**Files:** NEW `src/contracts.py`, NEW `src/parsers/registry.py`, NEW `src/classifier_registry.py`
**Effort:** Small (data structure definitions, no logic changes)
**Risk:** Low. Pure additive — nothing breaks.
**Dependencies:** None.

#### Step 2: Core Decoupling
**What:** Modify `extractor.py` to dispatch through the language registry instead of hardcoding Python. Modify `cycle.py` to pass archetype to classifier and scorer. Relax `chunk_type` CHECK constraint. Refactor `SCAN_TARGETS` to carry `(language, archetype)`.
**Files:** MODIFY `src/extractor.py`, `src/cycle.py`, `src/db.py`, `src/config.py`, `src/scorer.py`, `src/classifier.py`
**Effort:** Medium. The extractor refactor is the largest piece (~200 lines touched). SCAN_TARGETS change propagates to scanner, scorer, extractor, provenance.
**Risk:** Medium. This is the riskiest step — it touches the hot path. Must be accompanied by full test suite run against invoice-pulse to verify no regression.
**Dependencies:** Step 1.

#### Step 3: Invoice-Pulse Rules → First Archetype Head (`flask_service`)
**What:** Extract FUNCTIONAL_ROLE_SEEDS, classifier rules, ROLE_SCORING_WEIGHTS, ROLE_THRESHOLDS, BEST_PRACTICE_SEEDS, CONTENT_CHECKS into `src/archetypes/flask_service.py`. Remove hardcoded seeds from `db.py`. Register archetype. Run cycle against invoice-pulse to verify identical results.
**Files:** NEW `src/archetypes/__init__.py`, NEW `src/archetypes/flask_service.py`, MODIFY `src/db.py`, `src/config.py`, `src/classifier.py`, `src/detector.py`
**Effort:** Medium. Mostly moving data, but the seeding lifecycle change (from init_db to per-cycle) needs care.
**Risk:** Medium. Regression risk on invoice-pulse scoring/findings if any rule is misplaced during migration. Mitigated by running a before/after cycle comparison.
**Dependencies:** Step 2.

#### Step 4: Bellows as Second Tenant (Daemon Archetype)
**What:** Author `src/archetypes/daemon.py` with bellows-specific role taxonomy, classifier rules, scoring weights, and thresholds. Register archetype. Run cycle against bellows and verify meaningful classification (not all `utility`).
**Files:** NEW `src/archetypes/daemon.py`
**Effort:** Medium. Requires reading bellows source to design rules. The framework is ready from Steps 1-3; this is just filling in the data.
**Risk:** Low. Additive — doesn't affect invoice-pulse.
**Dependencies:** Step 3.

#### Step 5: Python Extractor Encapsulation
**What:** Wrap `python_parser.py` functions in a `PythonExtractor` class implementing the `LanguageExtractor` protocol. Register it. Move `detect_sqlalchemy_models()` into the extractor as a post-parse hook.
**Files:** MODIFY `src/parsers/python_parser.py`
**Effort:** Small-to-medium. Structural refactor, no logic changes.
**Risk:** Low. The class just delegates to existing functions.
**Dependencies:** Step 1 (protocol defined), Step 2 (registry exists).

#### Step 6 (FUTURE, OUT OF SCOPE): Additional Language Extractors
**What:** Implement `SwiftExtractor`, `TypeScriptExtractor`, etc.
**Effort:** Large per language. Each requires: AST library integration, chunk boundary detection, symbol extraction, complexity computation, module resolution, test detection.
**Risk:** High per language. Each language has its own parsing quirks and module system.
**Dependencies:** Steps 1-5 complete.
**Explicit flag:** This is a large separate effort. Do not conflate with the contract/archetype work. Each language extractor is its own plan.

### E.3 Effort Summary

| Step | Description | Effort | Risk | Blocked by |
|---|---|---|---|---|
| 1 | Contract definition | S | Low | — |
| 2 | Core decoupling | M | Medium | 1 |
| 3 | flask_service archetype | M | Medium | 2 |
| 4 | daemon archetype | M | Low | 3 |
| 5 | Python extractor encapsulation | S-M | Low | 1, 2 |
| 6 | Future language extractors | L (each) | High | 1-5 |

Steps 1-4 are the critical path for making Anvil a multi-archetype tool. Step 5 can run in parallel with Steps 3-4 since it only depends on Steps 1-2. Step 6 is explicitly deferred.

### E.4 Rule-Location Recommendation (CEO Decision Point)

**Recommend: (a) Central — all archetype definitions live in `anvil/src/archetypes/`.**

Reasons:
1. Small, controlled project population (~7-10 projects, ~5 archetypes, one CEO).
2. Single source of truth — no version drift between projects.
3. Testable — `pytest` can verify archetype rules without touching target projects.
4. Natural evolution path — if per-project overrides are ever needed, (c) hybrid is additive.

The central location means adding a new project to an existing archetype costs zero archetype work — just add a SCAN_TARGETS entry with the right `archetype` key.

### E.5 Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Core decoupling breaks invoice-pulse scoring | Run before/after cycle comparison; diff findings reports |
| Archetype seeding lifecycle change drops existing roles | Idempotent `INSERT OR IGNORE`; add `archetype` column to `functional_roles` for coexistence |
| SCAN_TARGETS format change breaks multiple modules | Single PR with grep-verified update of all consumers |
| Bellows archetype rules are wrong (bad classification) | Iterate: run cycle, inspect role distribution, tune rules |
| Future language extractor complexity underestimated | Explicitly flagged as out-of-scope; each is its own plan |

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** Step 1 (diagnostic, single SA step)
**Status:** Complete

### What Was Done
Produced a comprehensive design blueprint covering: (A) the current de facto extraction contract with full field-by-field tracing through parser → DB → classifier → scorer → lab, (B) the proposed ChunkRecord contract and LanguageExtractor protocol with concrete decoupling edits listed, (C) an archetype-keyed classifier registry design with rule-location analysis and migration plan, (D) a study cross-repo shape assessment (verdict: CLEAN normalised contract with transferable lessons), and (E) a dependency-ordered 6-step build sequence with effort/risk ratings.

### Files Deposited
- `knowledge/architecture/anvil-extraction-contract-archetype-design-2026-06-08.md` — full design blueprint

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- Recommended central rule location (option a) over per-project or hybrid
- Recommended relaxing chunk_type CHECK constraint to allow any string
- Determined invoice-pulse rules collapse to one archetype (flask_service), not multiple
- Assessed study's chunk boundary as CLEAN normalised contract

### Flags for CEO
- Rule-location fork (central vs hybrid) needs CEO ratification
- SCAN_TARGETS format change is a breaking change requiring coordinated update
- Bellows archetype role taxonomy is preliminary — needs source reading to finalise

### Flags for Next Step
- This is a terminal diagnostic; no next step within this plan
- The build sequence (Steps 1-5) is ready for an implementation executable if the CEO approves
