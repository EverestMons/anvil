# Anvil Scanner Blueprint
**Agent:** Anvil Systems Analyst
**Date:** 2026-03-30
**Source:** PROJECT_BRIEF pipeline section, Forge scanner.py patterns, config.py values

---

## Design Decisions

### 1. File content reading for hashing
**Decision:** Read file content fully into memory. Phase 1 targets invoice-pulse where all source files are under 1MB. Streaming adds complexity with no benefit at this scale.

### 2. Git log format
**Decision:** Use `--format=%H|%aI|%an|%s` (commit hash, ISO date, author, subject) with `--numstat` for per-file line stats. The `|` delimiter is safe — commit hashes are hex, ISO dates use colons/dashes, and author names rarely contain pipes. Parse the numstat lines to get per-file additions/deletions.

### 3. Per-file stats in git_changes
**Decision:** Store one row per file per commit in `git_changes`. The current schema has `file_path` per row, which naturally supports this. Line addition/deletion counts from `--numstat` are not in the current schema — defer adding `lines_added`/`lines_removed` columns to a future schema update (requires CEO approval). For now, volatility scoring can count commit frequency per file, which is the primary signal.

---

## Function Specifications

### `scan_project(conn, project_name) -> dict`

Main entry point for scanning a project.

**Logic:**
1. Look up `project_name` in `config.SCAN_TARGETS`. If not found, raise `ValueError(f"Unknown project: {project_name}")`.
2. Resolve project path. Verify it exists on disk. If not, raise `FileNotFoundError`.
3. Get or create the project in DB via `db.get_project()` / `db.create_project()`.
4. Call `discover_files(project_path, config.EXCLUDED_DIRS, config.EXCLUDED_EXTENSIONS)`.
5. Call `detect_changes(conn, project_id, discovered_files)` → three lists: new, changed, unchanged.
6. Call `register_file_chunks(conn, project_id, new + changed, cycle_id=None)` — cycle_id is None during standalone scans, set during full pipeline runs.
7. Call `ingest_git_history(conn, project_id, project_path, config.GIT_HISTORY_WEEKS)` → commit count.
8. Update `projects.last_scanned` to current ISO datetime.
9. Return summary dict:

```python
{
    "project_name": str,
    "files_total": int,        # len(discovered_files)
    "files_new": int,          # len(new)
    "files_changed": int,      # len(changed)
    "files_unchanged": int,    # len(unchanged)
    "git_commits_ingested": int,
}
```

---

### `discover_files(project_path, excluded_dirs, excluded_extensions) -> list[dict]`

Recursive directory walk that finds all source files.

**Logic:**
1. Use `os.walk(project_path)` with `topdown=True`.
2. In-place filter `dirs` to skip any directory name in `excluded_dirs`.
3. For each file, skip if extension is in `excluded_extensions`.
4. Skip hidden files (name starts with `.`).
5. Compute relative path from `project_path`.
6. Return list of dicts:

```python
{
    "file_path": str,       # absolute path
    "relative_path": str,   # relative to project root
    "extension": str,       # e.g., ".py"
    "size_bytes": int,      # os.path.getsize()
}
```

**Sort:** Return sorted by `relative_path` for deterministic ordering.

---

### `compute_file_hash(file_path) -> str`

SHA-256 content hash of a file.

**Logic:**
1. `open(file_path, "rb")` — read binary to avoid encoding issues.
2. `hashlib.sha256(content).hexdigest()` — return hex digest string.

**Edge case:** If file cannot be read (permissions, symlink), return `None` and the caller should skip the file with a warning.

---

### `detect_changes(conn, project_id, discovered_files) -> tuple[list, list, list]`

Compare discovered files against existing fingerprints to categorize changes.

**Logic:**
1. For each discovered file:
   a. Call `compute_file_hash(file["file_path"])`.
   b. If hash is `None`, skip (unreadable file).
   c. Query existing `code_chunks` for this project + relative_path where `chunk_type = 'module'` (file-level chunks).
   d. If no prior chunk exists → **new**.
   e. If prior chunk exists, query its `chunk_fingerprints` for the most recent `content_hash` (ORDER BY cycle_id DESC, id DESC LIMIT 1).
   f. If `content_hash` matches → **unchanged**.
   g. If `content_hash` differs → **changed**.
2. Attach `content_hash` to each file dict for later use by `register_file_chunks`.
3. Return `(new_files, changed_files, unchanged_files)`.

**Note:** Uses `chunk_type = 'module'` for file-level entries (not `'file'` — the CHECK constraint allows `module` but not `file`). Module is the correct domain term: a Python file is a module.

---

### `ingest_git_history(conn, project_id, project_path, weeks) -> int`

Parse git log and populate `git_changes` table.

**Git command:**
```bash
git -C {project_path} log --since="{weeks} weeks ago" --format=%H|%aI|%an|%s --numstat
```

**Output format:**
```
abc123|2026-03-28T14:30:00-05:00|Mark Lehn|fix: validation bug
5	2	engines/validator.py
1	0	tests/test_validator.py

def456|2026-03-27T10:00:00-05:00|Mark Lehn|feat: new gate
```

**Parsing logic:**
1. Run `subprocess.run(["git", "-C", project_path, "log", ...], capture_output=True, text=True)`.
2. If return code != 0 (git not initialized, no commits, etc.), print warning and return 0.
3. Split output into commit blocks. Each block starts with the `%H|%aI|%an|%s` line, followed by numstat lines, separated by blank lines.
4. For each commit block:
   a. Parse the header line: split on `|` to get `commit_hash`, `commit_date`, `author`, `commit_message`.
   b. **Dedup check:** Query `SELECT 1 FROM git_changes WHERE project_id = ? AND commit_hash = ? LIMIT 1`. If exists, skip this commit entirely (idempotent).
   c. Parse numstat lines: each line is `{added}\t{deleted}\t{file_path}`. Extract `file_path`.
   d. For each file in the commit, call `db.create_git_change(conn, project_id, file_path, commit_hash, commit_date, commit_message, author)`.
5. Return count of new commits ingested (not skipped).

**Edge cases:**
- Binary files in numstat show `-\t-\tfilename` — skip these (we only care about text files).
- Merge commits may have empty numstat — still record the commit for files listed.
- If `git` command not found or project has no git repo, catch the exception, print a warning, return 0.

---

### `register_file_chunks(conn, project_id, files, cycle_id) -> int`

Create file-level entries in `code_chunks` and `chunk_fingerprints` for new/changed files.

**Logic:**
1. For each file in `files`:
   a. If this is a **changed** file (prior chunk exists), the existing module-level chunk will be updated by the Extractor in Phase 3. For now, create a new fingerprint entry to track the new hash.
      - Query the existing chunk: `SELECT id FROM code_chunks WHERE project_id = ? AND file_path = ? AND chunk_type = 'module'`.
      - If found, call `db.create_fingerprint(conn, chunk_id, file["content_hash"], None, None, cycle_id or 0)`.
   b. If this is a **new** file:
      - Read file content: `open(file["file_path"], "r", encoding="utf-8", errors="replace").read()`.
      - Call `db.create_chunk(conn, project_id=project_id, file_path=file["relative_path"], chunk_type="module", name=file["relative_path"], content=content, content_hash=file["content_hash"], start_line=1, end_line=line_count, cycle_id=cycle_id)`.
      - Call `db.create_fingerprint(conn, chunk_id, file["content_hash"], None, None, cycle_id or 0)`.
2. Return count of files registered.

**Note:** `chunk_type="module"` is used for file-level chunks — this is semantically correct for Python files and fits the CHECK constraint. The Extractor (Phase 3) will parse each module chunk and add function/class/method child chunks.

---

## Module Dependencies

```
scanner.py
├── imports: os, hashlib, subprocess
├── from src.config: SCAN_TARGETS, EXCLUDED_DIRS, EXCLUDED_EXTENSIONS, GIT_HISTORY_WEEKS
└── from src.db: get_project, create_project, create_chunk, create_fingerprint, create_git_change
```

---

## How to Verify This Was Implemented Correctly

### 1. Function existence and signatures
Verify all 6 functions exist in `scanner.py` with correct parameter names:
- `scan_project(conn, project_name)`
- `discover_files(project_path, excluded_dirs, excluded_extensions)`
- `compute_file_hash(file_path)`
- `detect_changes(conn, project_id, discovered_files)`
- `ingest_git_history(conn, project_id, project_path, weeks)`
- `register_file_chunks(conn, project_id, files, cycle_id)`

### 2. Exclusion verification
Scan invoice-pulse, then query:
```sql
SELECT file_path FROM code_chunks
WHERE project_id = (SELECT id FROM projects WHERE name = 'invoice-pulse')
AND (file_path LIKE '%__pycache__%' OR file_path LIKE '%.pyc' OR file_path LIKE '%.git/%');
```
Expected: 0 rows.

### 3. Content hash consistency
Pick 3 files from scan results. Independently compute `hashlib.sha256(open(path,'rb').read()).hexdigest()`. Compare against `chunk_fingerprints.content_hash`. All must match.

### 4. Git history idempotency
Run `scan_project` twice. Second run should have `files_new = 0`, `files_unchanged = files_total` from first run. Query:
```sql
SELECT commit_hash, file_path, COUNT(*) FROM git_changes
WHERE project_id = (SELECT id FROM projects WHERE name = 'invoice-pulse')
GROUP BY commit_hash, file_path HAVING COUNT(*) > 1;
```
Expected: 0 rows (no duplicates).

### 5. Summary dict completeness
Verify `scan_project` returns all 6 keys: `project_name`, `files_total`, `files_new`, `files_changed`, `files_unchanged`, `git_commits_ingested`. All values should be non-negative integers (except `project_name`).

### 6. Error handling
- `scan_project(conn, "nonexistent")` should raise `ValueError`.
- `scan_project` with a path that doesn't exist should raise `FileNotFoundError`.

### 7. File-level chunk correctness
After scanning, every file should have exactly one `chunk_type = 'module'` entry in `code_chunks` and at least one entry in `chunk_fingerprints`.

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** Step 1
**Status:** Complete

### What Was Done
Designed the scanner blueprint specifying 6 functions: scan_project (main entry), discover_files (directory walk), compute_file_hash (SHA-256), detect_changes (new/changed/unchanged categorization), ingest_git_history (git log parsing with dedup), register_file_chunks (file-level chunk creation). Made 3 design decisions: full file reads for hashing, git log format with numstat, defer per-file line stats to future schema update.

### Files Deposited
- `anvil/knowledge/architecture/scanner-blueprint-2026-03-30.md` — scanner blueprint with function specs, design decisions, and verification checklist

### Files Created or Modified (Code)
- None (blueprint only — implementation is Step 2)

### Decisions Made
- Use `chunk_type = 'module'` for file-level chunks (semantically correct for Python, fits CHECK constraint)
- Read files fully for hashing (no streaming — all invoice-pulse files under 1MB)
- Git log format: `--format=%H|%aI|%an|%s --numstat`
- Defer lines_added/lines_removed columns to future schema migration (current schema sufficient for commit-frequency volatility)
- Dedup git history by commit_hash (idempotent ingestion)

### Flags for CEO
- Future schema update needed to add `lines_added`/`lines_removed` to `git_changes` for richer volatility scoring. Not blocking — commit frequency is the primary signal for Phase 1.

### Flags for Next Step
- Use `chunk_type = 'module'` (not `'file'`) — the CHECK constraint on code_chunks only allows: function, class, method, module, config, test_case
- `cycle_id` can be None for standalone scans — pass `cycle_id or 0` to `create_fingerprint` which requires NOT NULL
- Git log parsing: split on `|` for header, `\t` for numstat lines
- Binary files in numstat show `-\t-\tfilename` — skip these
