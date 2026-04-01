"""
Anvil dev log parser and provenance ingestion.

Parses markdown dev logs for "Files Created or Modified" sections,
extracts file paths, and populates the chunk_provenance table to
link code chunks back to their originating execution plans.
"""
from __future__ import annotations

import os
import re
from typing import Optional

from src import db

# Multi-pattern header search (order of likelihood)
HEADER_PATTERNS = [
    re.compile(r"^###?\s*Files Created or Modified \(Code\)\s*$"),
    re.compile(r"^###?\s*Files Created/Modified\s*$"),
    re.compile(r"^###?\s*Files Modified\s*$"),
    re.compile(r"^\*\*Files Modified:\*\*\s*$"),
    re.compile(r"^###?\s*Files Created or Modified\s*$"),
]

# Entry extraction patterns
BULLET_PATTERN = re.compile(
    r"^-\s+([a-zA-Z0-9_./-]+\.\w+)\s*(?:--|—)\s*(.*)$"
)
TABLE_ROW_PATTERN = re.compile(
    r"^\|\s*([a-zA-Z0-9_./-]+\.\w+)\s*\|"
)


def parse_dev_logs(dev_log_dir: str) -> list[dict]:
    """
    Parse all .md files in dev_log_dir for Output Receipt file lists.

    Returns list of dicts with keys:
        dev_log_name, plan_slug, plan_description, file_paths
    where file_paths is a list of {"path": str, "description": str}.
    """
    results = []

    if not os.path.isdir(dev_log_dir):
        return results

    for filename in sorted(os.listdir(dev_log_dir)):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(dev_log_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError:
            continue

        file_paths = _extract_file_paths(content)
        if not file_paths:
            continue

        results.append({
            "dev_log_name": filename,
            "plan_slug": _extract_plan_slug(filename),
            "plan_description": _extract_plan_description(content),
            "file_paths": file_paths,
        })

    return results


def _extract_plan_slug(filename: str) -> str:
    """Strip .md extension to get plan slug."""
    return filename.rsplit(".", 1)[0]


def _extract_plan_description(content: str) -> str:
    """Extract H1 title from dev log content."""
    for line in content.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _extract_file_paths(content: str) -> list[dict]:
    """
    Find the file modification section and extract file entries.

    Handles both bullet list and table formats.
    """
    lines = content.split("\n")
    section_start = None

    # Find the header line
    for i, line in enumerate(lines):
        stripped = line.strip()
        for pattern in HEADER_PATTERNS:
            if pattern.match(stripped):
                section_start = i + 1
                break
        if section_start is not None:
            break

    if section_start is None:
        return []

    # Extract entries until next section or end
    entries = []
    for i in range(section_start, len(lines)):
        line = lines[i].strip()

        # Stop at next header or horizontal rule (but skip empty lines)
        if line.startswith("#") or (line.startswith("---") and len(line) >= 3):
            break

        # Try bullet format
        m = BULLET_PATTERN.match(line)
        if m:
            entries.append({
                "path": m.group(1),
                "description": m.group(2).strip(),
            })
            continue

        # Try table format (skip header/separator rows)
        if line.startswith("|") and "---" not in line:
            m = TABLE_ROW_PATTERN.match(line)
            if m:
                path = m.group(1)
                # Skip table header rows
                if path.lower() in ("file", "filename", "path"):
                    continue
                entries.append({
                    "path": path,
                    "description": "",
                })

    return entries


def ingest_provenance(conn, project_name: str,
                      dev_log_dir: str) -> dict:
    """
    Parse dev logs and populate chunk_provenance table.

    Returns {"logs_parsed": N, "provenance_entries_created": N, "unmatched_files": N}.
    """
    project = db.get_project(conn, project_name)
    if project is None:
        raise ValueError(f"Project not found: {project_name}")

    project_id = project["id"]
    parsed = parse_dev_logs(dev_log_dir)
    entries_created = 0
    unmatched = 0

    for log_entry in parsed:
        for file_info in log_entry["file_paths"]:
            # Find matching chunks by file_path
            chunks = db.get_chunks_by_file(
                conn, project_id, file_info["path"]
            )
            if chunks:
                for chunk in chunks:
                    # Dedup check
                    existing = conn.execute(
                        "SELECT id FROM chunk_provenance "
                        "WHERE chunk_id = ? AND plan_name = ?",
                        (chunk["id"], log_entry["plan_slug"]),
                    ).fetchone()
                    if not existing:
                        db.create_provenance(
                            conn, chunk["id"],
                            plan_name=log_entry["plan_slug"],
                            dev_log_path=log_entry["dev_log_name"],
                            plan_description=log_entry["plan_description"],
                        )
                        entries_created += 1
            else:
                unmatched += 1

    return {
        "logs_parsed": len(parsed),
        "provenance_entries_created": entries_created,
        "unmatched_files": unmatched,
    }
