# Anvil Extractor Blueprint
**Agent:** Anvil Systems Analyst
**Date:** 2026-03-30
**Source:** PROJECT_BRIEF pipeline section, schema blueprint, scanner output, Forge extractor patterns

---

## Design Decisions

### 1. Chunk replacement strategy
**Decision:** Option (b) — keep the module chunk as a parent and insert sub-chunks with `parent_chunk_id` pointing to it. This preserves the file-level view (module chunk = whole file) while adding function/class/method granularity. The scanner already created module chunks with content and fingerprints; deleting them would lose that data and break fingerprint history. Methods inside classes get `parent_chunk_id` pointing to their class chunk (not the module chunk).

**Parent chain:** module → class → method (two levels max for Python). Top-level functions get `parent_chunk_id` pointing to the module chunk.

### 2. Structural metadata storage
**Decision:** Add a `structural_metadata` TEXT column to `code_chunks` (JSON blob). This follows Study's approach, keeps data co-located with chunks, and avoids a new table. Requires a schema migration in `init_db()` — use `ALTER TABLE code_chunks ADD COLUMN structural_metadata TEXT` wrapped in a try/except (column already exists → skip).

**JSON structure:**
```json
{
    "cyclomatic_complexity": 5,
    "nesting_depth": 3,
    "parameter_count": 2,
    "import_count": 0,
    "has_docstring": true,
    "line_count": 15
}
```

### 3. Dedup strategy for re-extraction
**Decision:** Before inserting a chunk, check if a chunk with the same `project_id`, `file_path`, `name`, and `chunk_type` already exists. If it does and the `content_hash` is the same → skip (unchanged). If it does but `content_hash` differs → update the existing chunk's content, content_hash, structural_metadata, and updated_at. This makes extraction idempotent.

### 4. MinHash configuration
**Decision:** Use `datasketch.MinHash` with `num_perm=128` (from config). Shingle size = 3 (3-word tokens from the source text). Store the serialized MinHash as BLOB in `chunk_fingerprints.minhash_signature`. Only compute MinHash for chunks with `line_count >= 5` — very small chunks produce unreliable signatures.

---

## Component A: `src/parsers/python_parser.py`

### `parse_file(file_path) -> list[dict]`

Parse a Python file using `ast.parse()` and extract code chunks.

**Logic:**
1. Read file content with `open(file_path, "r", encoding="utf-8", errors="replace")`.
2. Try `ast.parse(source, filename=file_path)`. On `SyntaxError`, return empty list (skip unparseable files).
3. Split source into lines for slicing: `source_lines = source.splitlines(True)`.
4. Walk top-level nodes of the AST tree:
   - `ast.FunctionDef` or `ast.AsyncFunctionDef`:
     - If name starts with `test_` or class name starts with `Test` → `chunk_type = "test_case"`
     - Else → `chunk_type = "function"`
   - `ast.ClassDef`:
     - `chunk_type = "class"`
     - Then walk the class body for methods:
       - `ast.FunctionDef` or `ast.AsyncFunctionDef` inside class → `chunk_type = "method"` (or `"test_case"` if in a Test class or name starts with `test_`)
       - Set `parent_name = class_name`
5. For each node, extract:
   - `name`: node.name
   - `chunk_type`: as above
   - `content`: `"".join(source_lines[node.lineno - 1 : node.end_lineno])`
   - `content_hash`: `hashlib.sha256(content.encode("utf-8")).hexdigest()`
   - `start_line`: `node.lineno`
   - `end_line`: `node.end_lineno`
   - `parent_name`: class name for methods, `None` for top-level
6. Return list of chunk dicts sorted by `start_line`.

**Edge cases:**
- Empty files → return empty list
- Files with only imports/assignments (no functions/classes) → return empty list (module chunk already exists from scanner)
- Decorated functions → `node.lineno` includes the decorator; use `node.lineno` for start (includes decorators)
- `ast.AsyncFunctionDef` → treat same as `ast.FunctionDef`

---

### `extract_symbols(file_path, source_lines, ast_tree) -> dict`

Walk the AST and return structured symbol data.

**Returns:**
```python
{
    "imports": [
        {"module": "os", "names": ["path"], "is_from": True, "line": 1},
        {"module": "sqlite3", "names": [], "is_from": False, "line": 2},
    ],
    "definitions": [
        {"name": "MyClass", "type": "class", "bases": ["Base", "db.Model"], "line": 10},
        {"name": "my_func", "type": "function", "line": 20},
    ],
    "calls": [
        {"caller": "my_func", "callee": "helper", "line": 25},
    ],
    "test_mappings": [
        {"test_name": "test_my_func", "tested_module": "my_module"},
    ],
}
```

**Parsing logic:**
- `ast.Import` → extract module names
- `ast.ImportFrom` → extract module + specific names
- `ast.FunctionDef` / `ast.ClassDef` → record definitions
- `ast.Call` → resolve callee name where possible:
  - `ast.Name` → `node.func.id`
  - `ast.Attribute` → `node.func.attr` (e.g., `obj.method`)
  - Nested → skip (too complex to resolve statically)
- Test mappings: for files named `test_*.py`, map `test_*` function names to the likely tested module by stripping `test_` prefix from the filename

---

### `compute_structural_metadata(ast_node, source_lines) -> dict`

Compute per-chunk structural metrics.

**Metrics:**
- `cyclomatic_complexity`: Count of decision points within the node: `if`, `elif`, `for`, `while`, `try`, `except`, `with`, `and`, `or`, `assert` → each adds 1. Base complexity = 1.
- `nesting_depth`: Maximum depth of nested control flow (if/for/while/try/with). Walk the subtree tracking depth.
- `parameter_count`: `len(node.args.args) + len(node.args.kwonlyargs)` for functions/methods. 0 for classes.
- `import_count`: Count of `ast.Import` + `ast.ImportFrom` nodes within the chunk.
- `has_docstring`: `isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, (ast.Str, ast.Constant))` — checks first statement is a string literal.
- `line_count`: `node.end_lineno - node.lineno + 1`

---

### `detect_sqlalchemy_models(ast_tree, source_lines) -> list[dict]`

Detect SQLAlchemy model patterns.

**Detection rules:**
1. Find classes where bases include `db.Model`, `Base`, `DeclarativeBase`, or any `*.Model`.
2. For each model class:
   - Extract class name → symbol_name `table:{class_name}` (e.g., `table:CarrierProfiles`)
   - Walk class body for `db.Column()`, `Column()` calls → symbol_name `column:{class_name}.{attr_name}`
   - Walk class body for `db.relationship()`, `relationship()` calls → symbol_name `relationship:{class_name}.{attr_name}`
   - Look for `__tablename__` assignment → use that as the actual table name

**Returns:**
```python
[
    {
        "class_name": "CarrierProfiles",
        "table_name": "carrier_profiles",  # from __tablename__ or None
        "columns": ["name", "code", "active"],
        "relationships": ["invoices"],
        "symbol_bindings": [
            {"symbol_name": "table:carrier_profiles", "binding_type": "defines"},
            {"symbol_name": "column:carrier_profiles.name", "binding_type": "defines"},
        ],
    }
]
```

---

## Component B: `src/extractor.py`

### `extract_project(conn, project_name, cycle_id) -> dict`

Main entry point for extracting all files in a project.

**Logic:**
1. Look up project in DB via `db.get_project(project_name)`. If not found, raise `ValueError`.
2. Query all module chunks: `SELECT * FROM code_chunks WHERE project_id = ? AND chunk_type = 'module'`.
3. Filter to `.py` files only (Phase 1 is Python-only).
4. For each `.py` module chunk:
   a. Resolve absolute path from `config.SCAN_TARGETS[project_name]` + `file_path`.
   b. Call `python_parser.parse_file(abs_path)` → list of chunk dicts.
   c. For each chunk dict:
      - **Dedup check:** Query existing chunks by `project_id`, `file_path`, `name`, `chunk_type`.
      - If exists with same `content_hash` → skip.
      - If exists with different `content_hash` → update content, hash, metadata, updated_at.
      - If new → insert via `db.create_chunk()`.
      - Set `parent_chunk_id`: for top-level functions → module chunk id. For methods → their class chunk id (look up by name + file_path).
   d. Call `python_parser.extract_symbols()` → store via `store_symbols()`.
   e. Call `python_parser.compute_structural_metadata()` → store via `store_structural_metadata()`.
   f. Call `python_parser.detect_sqlalchemy_models()` → store model bindings.
5. Call `resolve_dependencies(conn, project_id)`.
6. Call `compute_fingerprints(conn, project_id, cycle_id)`.
7. Return summary dict:

```python
{
    "files_processed": int,
    "chunks_created": int,
    "chunks_updated": int,
    "symbols_extracted": int,
    "dependencies_resolved": int,
    "fingerprints_created": int,
    "similarities_found": int,
}
```

---

### `store_symbols(conn, chunk_id, symbols, file_chunks) -> int`

Store symbol bindings for a chunk.

**Logic:**
- For each import → `create_symbol_binding(conn, chunk_id, module_name, "imports")`
- For each definition → `create_symbol_binding(conn, chunk_id, name, "defines")`
- For each call → `create_symbol_binding(conn, chunk_id, callee_name, "calls")`
- For each test mapping → `create_symbol_binding(conn, chunk_id, tested_module, "tests")`
- For each SQLAlchemy binding → `create_symbol_binding(conn, chunk_id, symbol_name, "defines")`

Returns count of bindings created.

---

### `resolve_dependencies(conn, project_id) -> int`

Second pass: resolve symbol bindings into chunk dependencies.

**Logic:**
1. Query all `chunk_symbol_bindings` for this project's chunks where `binding_type = "imports"`.
2. For each import binding:
   - Search for a chunk matching the imported module/symbol name.
   - Match strategies: (a) exact name match on a `defines` binding, (b) file_path match (module name → file path conversion: `engines.validator` → `engines/validator.py`).
   - If match found: `create_dependency(conn, source_chunk_id, target_chunk_id, "import", scope)`.
   - Scope: `within_file` if same `file_path`, `cross_file` otherwise.
3. Repeat for `binding_type = "calls"` → `dependency_type = "call"`.
4. For class inheritance: query class chunks, check their bases against other class chunks → `dependency_type = "inherit"`.

Returns count of dependencies created.

---

### `compute_fingerprints(conn, project_id, cycle_id) -> tuple[int, int]`

Compute MinHash signatures and detect similarities.

**Logic:**
1. Query all non-module chunks for this project (functions, classes, methods, test_cases).
2. For each chunk with `line_count >= 5`:
   a. Tokenize content into 3-word shingles.
   b. Create `datasketch.MinHash(num_perm=config.MINHASH_NUM_PERM)`.
   c. Update MinHash with each shingle.
   d. Store via `db.create_fingerprint(conn, chunk_id, content_hash, minhash.digest(), shingle_count, cycle_id)`.
3. For chunks with `line_count < 5`:
   a. Store fingerprint with `minhash_signature=None` (too small for reliable MinHash).
4. Similarity detection:
   a. For each pair of chunks with MinHash signatures, compute Jaccard similarity.
   b. If similarity >= `config.MINHASH_THRESHOLD` and chunks are different → `db.create_similarity()`.
   c. Optimization: use `datasketch.MinHashLSH` for approximate nearest neighbors instead of all-pairs comparison.

Returns `(fingerprints_created, similarities_found)`.

---

### `store_structural_metadata(conn, chunk_id, metadata_dict) -> None`

Store structural metadata as JSON on the chunk.

**Logic:**
```python
import json
conn.execute(
    "UPDATE code_chunks SET structural_metadata = ? WHERE id = ?",
    (json.dumps(metadata_dict), chunk_id),
)
conn.commit()
```

**Schema migration required in `init_db()`:**
```python
try:
    conn.execute("ALTER TABLE code_chunks ADD COLUMN structural_metadata TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass  # Column already exists
```

---

## Module Dependencies

```
parsers/python_parser.py
├── imports: ast, hashlib
└── no DB dependency — pure parsing

extractor.py
├── imports: json, os
├── from src.config: SCAN_TARGETS, MINHASH_NUM_PERM, MINHASH_THRESHOLD
├── from src.db: get_project, create_chunk, create_fingerprint, create_symbol_binding,
│                 create_dependency, create_similarity
├── from src.parsers.python_parser: parse_file, extract_symbols,
│                                    compute_structural_metadata, detect_sqlalchemy_models
└── from datasketch: MinHash (optional — graceful degradation if not installed)
```

---

## How to Verify This Was Implemented Correctly

### 1. Parser accuracy — validator.py
Parse `engines/validator.py` from invoice-pulse. Verify:
- Multiple function chunks extracted (gate functions)
- Correct start_line / end_line per chunk
- Content matches the actual source text at those lines

### 2. Chunk type distribution
After extracting invoice-pulse, query:
```sql
SELECT chunk_type, COUNT(*) FROM code_chunks WHERE project_id = 1 GROUP BY chunk_type;
```
Expected: all of function, class, method, module, test_case present. Module count should match scanner's 188 (Python files only among 939 total). Function + method + class count should be significantly larger.

### 3. Parent linkage
```sql
SELECT c.name, c.chunk_type, p.name as parent, p.chunk_type as parent_type
FROM code_chunks c
JOIN code_chunks p ON c.parent_chunk_id = p.id
WHERE c.chunk_type = 'method'
LIMIT 10;
```
Every method's parent should be a class. Top-level functions' parent should be a module.

### 4. Symbol bindings
```sql
SELECT binding_type, COUNT(*) FROM chunk_symbol_bindings GROUP BY binding_type;
```
Expected: imports, defines, calls all present with non-zero counts. Tests binding present if test files were processed.

### 5. SQLAlchemy detection
```sql
SELECT symbol_name FROM chunk_symbol_bindings
WHERE symbol_name LIKE 'table:%' OR symbol_name LIKE 'column:%'
LIMIT 20;
```
Expected: table and column entries from `database.py` and/or `contract_tables.py`.

### 6. Dependencies
```sql
SELECT dependency_type, scope, COUNT(*) FROM chunk_dependencies GROUP BY dependency_type, scope;
```
Expected: import dependencies present, both within_file and cross_file.

### 7. MinHash fingerprints
```sql
SELECT COUNT(*) FROM chunk_fingerprints WHERE minhash_signature IS NOT NULL;
```
Expected: > 0 (chunks with 5+ lines should have MinHash).

### 8. Structural metadata
```sql
SELECT name, structural_metadata FROM code_chunks
WHERE structural_metadata IS NOT NULL LIMIT 5;
```
Expected: valid JSON with cyclomatic_complexity, nesting_depth, parameter_count, etc.

### 9. Idempotency
Run `extract_project` twice. Second run should report `chunks_created = 0` (all exist with same hash). No duplicate chunks.

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** Step 1
**Status:** Complete

### What Was Done
Designed the extractor blueprint covering two components: python_parser.py (4 functions: parse_file, extract_symbols, compute_structural_metadata, detect_sqlalchemy_models) and extractor.py (5 functions: extract_project, store_symbols, resolve_dependencies, compute_fingerprints, store_structural_metadata). Made 4 design decisions: keep module chunks as parents, add structural_metadata column to code_chunks, dedup by content_hash for idempotency, MinHash only for chunks with 5+ lines.

### Files Deposited
- `anvil/knowledge/architecture/extractor-blueprint-2026-03-30.md` — full blueprint with function specs, design decisions, and 9-point verification checklist

### Files Created or Modified (Code)
- None (blueprint only)

### Decisions Made
- Keep module chunk as parent (option b) — preserves file-level view, maintains fingerprint history
- Add `structural_metadata TEXT` column to code_chunks via ALTER TABLE migration
- Dedup chunks by project_id + file_path + name + chunk_type + content_hash
- MinHash only for chunks with line_count >= 5 (small chunks produce unreliable signatures)
- Top-level functions get parent_chunk_id pointing to module chunk; methods point to class chunk

### Flags for CEO
- Schema migration: adding `structural_metadata TEXT` column to code_chunks. This is a column addition not in the original PROJECT_BRIEF — flagging for awareness. Low risk (nullable TEXT column, no constraints).

### Flags for Next Step
- Schema migration must be applied in init_db() before extraction runs
- datasketch may not be installed — Developer should handle graceful degradation
- Phase 1 extracts only .py files — filter module chunks by file_path extension
- SQLAlchemy detection targets classes inheriting from db.Model/Base — check invoice-pulse's actual patterns
