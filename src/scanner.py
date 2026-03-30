"""
Anvil Stage 1 — file discovery, content hashing, change detection, git history ingestion.

The scanner walks a project directory, discovers source files, detects changes
via content hashing, registers file-level module chunks in the database, and
ingests recent git history for volatility tracking.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
from datetime import datetime, timezone
from typing import Optional

from src import db
from src.config import (
    EXCLUDED_DIRS,
    EXCLUDED_EXTENSIONS,
    GIT_HISTORY_WEEKS,
    SCAN_TARGETS,
)


def scan_project(conn, project_name: str) -> dict:
    """
    Main entry point for scanning a project.

    Returns a summary dict with file counts and git commit count.
    """
    if project_name not in SCAN_TARGETS:
        raise ValueError(f"Unknown project: {project_name}")

    project_path = SCAN_TARGETS[project_name]
    if not os.path.isdir(project_path):
        raise FileNotFoundError(f"Project path does not exist: {project_path}")

    project = db.get_project(conn, project_name)
    if project is None:
        project_id = db.create_project(conn, project_name, project_path)
    else:
        project_id = project["id"]

    discovered = discover_files(project_path, EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)
    new_files, changed_files, unchanged_files = detect_changes(
        conn, project_id, discovered
    )

    register_file_chunks(conn, project_id, new_files, changed_files, cycle_id=None)

    git_commits = ingest_git_history(
        conn, project_id, project_path, GIT_HISTORY_WEEKS
    )

    conn.execute(
        "UPDATE projects SET last_scanned = ? WHERE id = ?",
        (datetime.now(timezone.utc).isoformat(), project_id),
    )
    conn.commit()

    return {
        "project_name": project_name,
        "files_total": len(discovered),
        "files_new": len(new_files),
        "files_changed": len(changed_files),
        "files_unchanged": len(unchanged_files),
        "git_commits_ingested": git_commits,
    }


def discover_files(project_path: str, excluded_dirs: set,
                   excluded_extensions: set) -> list[dict]:
    """
    Recursive directory walk that finds all source files.

    Returns a sorted list of file info dicts.
    """
    files = []
    for root, dirs, filenames in os.walk(project_path, topdown=True):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for fname in filenames:
            if fname.startswith("."):
                continue
            ext = os.path.splitext(fname)[1]
            if ext in excluded_extensions:
                continue
            abs_path = os.path.join(root, fname)
            rel_path = os.path.relpath(abs_path, project_path)
            files.append({
                "file_path": abs_path,
                "relative_path": rel_path,
                "extension": ext,
                "size_bytes": os.path.getsize(abs_path),
            })
    return sorted(files, key=lambda f: f["relative_path"])


def compute_file_hash(file_path: str) -> Optional[str]:
    """
    SHA-256 content hash of a file. Returns hex digest or None on error.
    """
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except (OSError, IOError):
        return None


def detect_changes(conn, project_id: int,
                   discovered_files: list[dict]) -> tuple[list, list, list]:
    """
    Compare discovered files against existing fingerprints.

    Returns (new_files, changed_files, unchanged_files).
    Each file dict gets a 'content_hash' key attached.
    """
    new_files = []
    changed_files = []
    unchanged_files = []

    for file_info in discovered_files:
        content_hash = compute_file_hash(file_info["file_path"])
        if content_hash is None:
            continue
        file_info["content_hash"] = content_hash

        cur = conn.execute(
            "SELECT id FROM code_chunks "
            "WHERE project_id = ? AND file_path = ? AND chunk_type = 'module'",
            (project_id, file_info["relative_path"]),
        )
        row = cur.fetchone()

        if row is None:
            new_files.append(file_info)
        else:
            chunk_id = row[0]
            fp_cur = conn.execute(
                "SELECT content_hash FROM chunk_fingerprints "
                "WHERE chunk_id = ? ORDER BY cycle_id DESC, id DESC LIMIT 1",
                (chunk_id,),
            )
            fp_row = fp_cur.fetchone()
            if fp_row is None or fp_row[0] != content_hash:
                changed_files.append(file_info)
            else:
                unchanged_files.append(file_info)

    return new_files, changed_files, unchanged_files


def ingest_git_history(conn, project_id: int, project_path: str,
                       weeks: int) -> int:
    """
    Parse git log and populate git_changes table. Idempotent via commit_hash dedup.

    Returns count of new commits ingested.
    """
    try:
        result = subprocess.run(
            [
                "git", "-C", project_path, "log",
                f"--since={weeks} weeks ago",
                "--format=%H|%aI|%an|%s",
                "--numstat",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 0

    if result.returncode != 0:
        return 0

    output = result.stdout.strip()
    if not output:
        return 0

    commits_ingested = 0
    current_header = None
    current_files = []

    for line in output.split("\n"):
        line = line.strip()
        if not line:
            if current_header and current_files:
                ingested = _store_commit(conn, project_id, current_header,
                                         current_files)
                if ingested:
                    commits_ingested += 1
            elif current_header:
                ingested = _store_commit(conn, project_id, current_header, [])
                if ingested:
                    commits_ingested += 1
            current_header = None
            current_files = []
            continue

        if "|" in line and not line.startswith("-") and "\t" not in line:
            if current_header:
                ingested = _store_commit(conn, project_id, current_header,
                                         current_files)
                if ingested:
                    commits_ingested += 1
                current_files = []
            current_header = line
        elif "\t" in line:
            parts = line.split("\t")
            if len(parts) == 3 and parts[0] != "-":
                current_files.append(parts[2])

    if current_header:
        ingested = _store_commit(conn, project_id, current_header, current_files)
        if ingested:
            commits_ingested += 1

    return commits_ingested


def _store_commit(conn, project_id: int, header: str,
                  file_paths: list[str]) -> bool:
    """
    Parse a commit header and store git_changes rows.
    Returns True if the commit was new (ingested), False if skipped (dedup).
    """
    parts = header.split("|", 3)
    if len(parts) < 4:
        return False

    commit_hash, commit_date, author, commit_message = parts

    cur = conn.execute(
        "SELECT 1 FROM git_changes WHERE project_id = ? AND commit_hash = ? LIMIT 1",
        (project_id, commit_hash),
    )
    if cur.fetchone():
        return False

    if file_paths:
        for fp in file_paths:
            db.create_git_change(
                conn, project_id, fp, commit_hash, commit_date,
                commit_message, author,
            )
    else:
        db.create_git_change(
            conn, project_id, "", commit_hash, commit_date,
            commit_message, author,
        )

    return True


def register_file_chunks(conn, project_id: int, new_files: list[dict],
                         changed_files: list[dict],
                         cycle_id: Optional[int] = None) -> int:
    """
    Create file-level entries in code_chunks and chunk_fingerprints.

    Returns count of files registered.
    """
    count = 0
    effective_cycle = cycle_id or 0

    for file_info in new_files:
        try:
            with open(file_info["file_path"], "r", encoding="utf-8",
                      errors="replace") as f:
                content = f.read()
        except (OSError, IOError):
            continue

        line_count = content.count("\n") + (1 if content and not content.endswith("\n") else 0)

        chunk_id = db.create_chunk(
            conn,
            project_id=project_id,
            file_path=file_info["relative_path"],
            chunk_type="module",
            name=file_info["relative_path"],
            content=content,
            content_hash=file_info["content_hash"],
            start_line=1,
            end_line=max(line_count, 1),
            cycle_id=cycle_id,
        )
        db.create_fingerprint(
            conn, chunk_id, file_info["content_hash"], None, None,
            effective_cycle,
        )
        count += 1

    for file_info in changed_files:
        cur = conn.execute(
            "SELECT id FROM code_chunks "
            "WHERE project_id = ? AND file_path = ? AND chunk_type = 'module'",
            (project_id, file_info["relative_path"]),
        )
        row = cur.fetchone()
        if row:
            db.create_fingerprint(
                conn, row[0], file_info["content_hash"], None, None,
                effective_cycle,
            )
            count += 1

    return count
