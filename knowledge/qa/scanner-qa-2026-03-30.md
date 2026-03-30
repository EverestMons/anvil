# Anvil Scanner QA Report
**Date:** 2026-03-30
**Agent:** Anvil QA Analyst
**Blueprint:** `anvil/knowledge/architecture/scanner-blueprint-2026-03-30.md`
**Dev Log:** `anvil/knowledge/development/scanner-implementation-2026-03-30.md`

---

## Verification Areas

### 1. Unit Test Suite — PASS
Ran `python3 -m pytest tests/test_scanner.py -v`. **21/21 tests passed** in 0.24s.

Coverage: discover_files (6 tests), compute_file_hash (3 tests), detect_changes (3 tests), ingest_git_history (3 tests), register_file_chunks (2 tests), scan_project integration (4 tests).

### 2. Live Scan Against invoice-pulse — PASS

First scan results:
```json
{
  "project_name": "invoice-pulse",
  "files_total": 939,
  "files_new": 939,
  "files_changed": 0,
  "files_unchanged": 0,
  "git_commits_ingested": 479
}
```

- files_total = 939 (188 Python + 663 Markdown + 79 HTML + 9 other)
- git_commits_ingested = 479 (4 weeks of history, 2168 git_changes rows — one per file per commit)
- Counts are reasonable for invoice-pulse's size

### 3. Exclusion Verification — PASS
```sql
SELECT file_path FROM code_chunks WHERE ... AND (file_path LIKE '%__pycache__%'
OR file_path LIKE '%.pyc' OR file_path LIKE '%.git/%' OR file_path LIKE '%.db'
OR file_path LIKE '%.db-shm' OR file_path LIKE '%.db-wal')
```
**Result: 0 rows.** No excluded files in the database.

**QA fix applied:** Added hidden directory exclusion (`dirs starting with .`) to `discover_files` and added binary/database extensions (`.db`, `.db-shm`, `.db-wal`, `.pdf`, `.docx`, `.bak`, `.log`, image/font formats) to `EXCLUDED_EXTENSIONS` in config.py. Without this fix, 2465 files were discovered including 1519 SQLite database artifacts.

### 4. Content Hash Consistency — PASS
Picked 3 Python files, independently computed SHA-256:
- `app.py`: MATCH
- `auth.py`: MATCH
- `backup.py`: MATCH

### 5. Git History Verification — PASS
- 2168 git_changes rows for invoice-pulse (479 distinct commits × multiple files each)
- Sample commit hashes cross-checked against `git log --oneline -5`:
  - `78b4575` — matches DB hash `78b45754367c...`
  - `a75e260` — matches DB
  - `8848bc2` — matches DB

### 6. Idempotency — PASS
Second scan results:
```json
{
  "files_total": 939,
  "files_new": 0,
  "files_changed": 0,
  "files_unchanged": 939,
  "git_commits_ingested": 0
}
```
- files_new = 0 (correct — all already registered)
- files_unchanged = 939 = first scan's files_total (correct)
- git_commits_ingested = 0 (correct — all already in DB)
- Duplicate check: `SELECT commit_hash, file_path, COUNT(*) ... HAVING COUNT(*) > 1` returned **0 rows**

### 7. Blueprint Compliance — PASS
All 6 functions exist with correct signatures:
- `scan_project(conn, project_name)` — PASS
- `discover_files(project_path, excluded_dirs, excluded_extensions)` — PASS
- `compute_file_hash(file_path)` — PASS
- `detect_changes(conn, project_id, discovered_files)` — PASS
- `ingest_git_history(conn, project_id, project_path, weeks)` — PASS
- `register_file_chunks(conn, project_id, new_files, changed_files, cycle_id)` — PASS

**Note:** `register_file_chunks` takes `new_files` and `changed_files` as separate params (blueprint specified a single `files` param). Functionally equivalent, clearer separation.

File-level chunk correctness: 939 module chunks, 939 fingerprints — 1:1 match. PASS.

### 8. Edge Case Handling — PASS
- `scan_project(conn, "nonexistent-project-xyz")` raises `ValueError("Unknown project: nonexistent-project-xyz")` — PASS

---

## QA Fixes Applied

1. **Hidden directory exclusion** — `discover_files` now also skips directories starting with `.` (e.g., `.claude/`, `.pytest_cache/`). Previously only named exclusions in `EXCLUDED_DIRS` were filtered.

2. **Binary extension exclusions** — Added to `config.EXCLUDED_EXTENSIONS`: `.db`, `.db-shm`, `.db-wal`, `.pdf`, `.docx`, `.bak`, `.log`, and common image/font formats. Without this, 1519 SQLite database artifacts were being scanned and stored as module chunks.

---

## Summary

**Overall Result: PASS**

All 8 verification areas pass. Two QA fixes applied (hidden dir exclusion + binary extension exclusions) to prevent scanning non-source-code files. Live scan against invoice-pulse verified: 939 files registered, 479 git commits ingested, idempotent on rescan, content hashes match, no excluded files in DB.

---

## Output Receipt
**Agent:** Anvil QA Analyst
**Step:** Step 3
**Status:** Complete

### What Was Done
Verified the scanner implementation against 8 verification areas from the SA blueprint. Applied 2 QA fixes: hidden directory exclusion in discover_files and expanded binary extension exclusions in config.py. All areas pass after fixes.

### Files Deposited
- `anvil/knowledge/qa/scanner-qa-2026-03-30.md` — scanner QA report

### Files Created or Modified (Code)
- `anvil/src/scanner.py` — added hidden directory exclusion in discover_files
- `anvil/src/config.py` — expanded EXCLUDED_EXTENSIONS with binary/database formats

### Decisions Made
- Hidden directories should be excluded from scanning (same logic as hidden files)
- SQLite artifacts and binary files are not source code and should not be chunked

### Flags for CEO
- None

### Flags for Next Step
- None — scanner is verified and ready for Phase 3 (Extractor)
