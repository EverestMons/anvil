"""
Anvil pipeline orchestrator — runs the full SCAN → EXTRACT → SCORE → LAB cycle.

Wires all pipeline stages together, manages cycle numbering, and provides
cycle comparison for tracking project health over time.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone

from src import db
from src.classifier import classify_project
from src.classifier_registry import get_archetype
from src.config import DEV_LOG_PATHS, SCAN_TARGETS
from src.scanner import scan_project
from src.extractor import extract_project
from src.provenance import ingest_provenance
from src.scorer import score_project
from src.lab import run_lab

# Ensure archetypes are registered
import src.archetypes  # noqa: F401


def seed_archetype_data(conn, archetype) -> None:
    """Seed functional_roles and best_practices from archetype (idempotent)."""
    for name, description, parent_role in archetype.roles:
        conn.execute(
            "INSERT OR IGNORE INTO functional_roles (name, description, parent_role) "
            "VALUES (?, ?, ?)",
            (name, description, parent_role),
        )
    for role, pattern, desc, hint, source, severity in archetype.best_practices:
        conn.execute(
            "INSERT OR IGNORE INTO best_practices "
            "(functional_role, pattern_name, description, detection_hint, source, severity) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (role, pattern, desc, hint, source, severity),
        )
    conn.commit()


def run_cycle(conn, project_name: str) -> dict:
    """
    Run the full SCAN → EXTRACT → SCORE → LAB pipeline.

    Assigns a new cycle_id, runs all stages in sequence.
    Returns combined summary with per-stage results and elapsed time.
    """
    start_time = time.time()

    # Determine next cycle_id
    cur = conn.execute(
        "SELECT MAX(cycle_number) FROM cycle_reports "
        "WHERE project_id = (SELECT id FROM projects WHERE name = ?)",
        (project_name,),
    )
    row = cur.fetchone()
    cycle_id = (row[0] or 0) + 1

    results = {"cycle_id": cycle_id, "project_name": project_name}

    # Load and seed archetype
    target = SCAN_TARGETS.get(project_name, {})
    archetype_name = target.get("archetype") if isinstance(target, dict) else None
    archetype = None
    if archetype_name:
        archetype = get_archetype(archetype_name)
        seed_archetype_data(conn, archetype)

    # Stage 1: SCAN
    try:
        scan_result = scan_project(conn, project_name)
        results["scan"] = scan_result
    except Exception as e:
        results["scan"] = {"error": str(e)}
        results["aborted_at"] = "scan"
        results["elapsed_seconds"] = round(time.time() - start_time, 2)
        return results

    # Stage 2: EXTRACT
    try:
        extract_result = extract_project(conn, project_name, cycle_id)
        results["extract"] = extract_result
    except Exception as e:
        results["extract"] = {"error": str(e)}
        results["elapsed_seconds"] = round(time.time() - start_time, 2)
        return results

    # Stage 2.5: CLASSIFY (non-fatal — scoring works without it)
    try:
        classify_result = classify_project(conn, project_name)
        results["classify"] = classify_result
    except Exception as e:
        results["classify"] = {"error": str(e)}

    # Stage 2.5b: PROVENANCE (non-fatal)
    try:
        dev_log_dir = DEV_LOG_PATHS.get(project_name)
        if dev_log_dir:
            provenance_result = ingest_provenance(
                conn, project_name, dev_log_dir
            )
            results["provenance"] = provenance_result
    except Exception as e:
        results["provenance"] = {"error": str(e)}

    # Stage 3: SCORE
    try:
        score_result = score_project(conn, project_name, cycle_id, archetype)
        results["score"] = score_result
    except Exception as e:
        results["score"] = {"error": str(e)}

    # Stage 4: LAB (run even if scorer failed)
    try:
        lab_result = run_lab(conn, project_name, cycle_id)
        results["lab"] = lab_result
    except Exception as e:
        results["lab"] = {"error": str(e)}

    results["elapsed_seconds"] = round(time.time() - start_time, 2)
    return results


def get_cycle_summary(conn, project_name: str, cycle_number: int) -> dict:
    """
    Read cycle_reports row + health_scores stats for a given cycle.

    Returns a summary dict for CEO consumption.
    """
    project = db.get_project(conn, project_name)
    if project is None:
        raise ValueError(f"Project not found: {project_name}")

    project_id = project["id"]
    report = db.get_cycle_report(conn, cycle_number)

    if report is None:
        return {"error": f"No cycle report found for cycle {cycle_number}"}

    # Health score stats
    cur = conn.execute(
        "SELECT COUNT(*), AVG(composite_score), MIN(composite_score), "
        "MAX(composite_score) FROM health_scores "
        "WHERE cycle_id = ?",
        (cycle_number,),
    )
    row = cur.fetchone()
    score_count = row[0] or 0
    avg_score = round(row[1] or 0.0, 4)
    min_score = round(row[2] or 0.0, 4)
    max_score = round(row[3] or 0.0, 4)

    # Risk distribution
    cur = conn.execute(
        "SELECT "
        "SUM(CASE WHEN composite_score >= 0.7 THEN 1 ELSE 0 END), "
        "SUM(CASE WHEN composite_score >= 0.3 AND composite_score < 0.7 THEN 1 ELSE 0 END), "
        "SUM(CASE WHEN composite_score < 0.3 THEN 1 ELSE 0 END) "
        "FROM health_scores WHERE cycle_id = ?",
        (cycle_number,),
    )
    dist = cur.fetchone()

    # Top 5 riskiest
    conn.row_factory = db._row_to_dict
    cur = conn.execute(
        "SELECT cc.file_path, cc.name, cc.chunk_type, hs.composite_score "
        "FROM health_scores hs "
        "JOIN code_chunks cc ON hs.chunk_id = cc.id "
        "WHERE hs.cycle_id = ? "
        "ORDER BY hs.composite_score DESC LIMIT 5",
        (cycle_number,),
    )
    top_risk = cur.fetchall()
    conn.row_factory = None

    return {
        "project_name": project_name,
        "cycle_number": cycle_number,
        "files_scanned": report["files_scanned"],
        "chunks_extracted": report["chunks_extracted"],
        "chunks_scored": score_count,
        "findings_count": report["findings_count"],
        "report_path": report["report_path"],
        "started_at": report["started_at"],
        "completed_at": report["completed_at"],
        "health_scores": {
            "avg": avg_score,
            "min": min_score,
            "max": max_score,
            "distribution": {
                "high_risk": dist[0] or 0,
                "medium": dist[1] or 0,
                "low_risk": dist[2] or 0,
            },
        },
        "top_5_riskiest": top_risk,
    }


def compare_cycles(conn, project_name: str, cycle_a: int,
                   cycle_b: int) -> dict:
    """
    Compare two cycle runs: new/removed chunks, score changes.

    cycle_a is the older cycle, cycle_b is the newer.
    """
    project = db.get_project(conn, project_name)
    if project is None:
        raise ValueError(f"Project not found: {project_name}")

    project_id = project["id"]

    # Get chunks scored in each cycle
    cur = conn.execute(
        "SELECT chunk_id, composite_score FROM health_scores WHERE cycle_id = ?",
        (cycle_a,),
    )
    scores_a = {r[0]: r[1] for r in cur.fetchall()}

    cur = conn.execute(
        "SELECT chunk_id, composite_score FROM health_scores WHERE cycle_id = ?",
        (cycle_b,),
    )
    scores_b = {r[0]: r[1] for r in cur.fetchall()}

    chunks_a = set(scores_a.keys())
    chunks_b = set(scores_b.keys())

    new_chunks = chunks_b - chunks_a
    removed_chunks = chunks_a - chunks_b
    common_chunks = chunks_a & chunks_b

    improved = 0
    degraded = 0
    unchanged = 0

    for cid in common_chunks:
        diff = scores_b[cid] - scores_a[cid]
        if diff < -0.05:
            improved += 1  # Lower score = healthier
        elif diff > 0.05:
            degraded += 1
        else:
            unchanged += 1

    # Get cycle report stats
    report_a = db.get_cycle_report(conn, cycle_a)
    report_b = db.get_cycle_report(conn, cycle_b)

    findings_a = report_a["findings_count"] if report_a else 0
    findings_b = report_b["findings_count"] if report_b else 0

    return {
        "project_name": project_name,
        "cycle_a": cycle_a,
        "cycle_b": cycle_b,
        "chunks_in_a": len(chunks_a),
        "chunks_in_b": len(chunks_b),
        "new_chunks": len(new_chunks),
        "removed_chunks": len(removed_chunks),
        "score_changes": {
            "improved": improved,
            "degraded": degraded,
            "unchanged": unchanged,
        },
        "findings_a": findings_a,
        "findings_b": findings_b,
        "findings_delta": findings_b - findings_a,
    }
