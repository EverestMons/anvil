"""
Anvil Stage 3 — health scoring across 5 dimensions.

Reads data from code_chunks, chunk_dependencies, chunk_symbol_bindings,
git_changes, and structural_metadata. Writes composite health_scores per chunk.
"""
from __future__ import annotations

import json
import math
import subprocess
from datetime import datetime, timezone, timedelta
from typing import Optional

from src import db
from src.config import GIT_HISTORY_WEEKS, SCAN_TARGETS, SCORING_WEIGHTS


def score_project(conn, project_name: str, cycle_id: int) -> dict:
    """
    Main entry point for scoring all chunks in a project.

    Returns summary dict with chunks_scored, score_distribution, avg_composite.
    """
    project = db.get_project(conn, project_name)
    if project is None:
        raise ValueError(f"Project not found: {project_name}")

    project_id = project["id"]

    # Load all non-module chunks
    conn.row_factory = db._row_to_dict
    cur = conn.execute(
        "SELECT * FROM code_chunks WHERE project_id = ? AND chunk_type != 'module'",
        (project_id,),
    )
    chunks = cur.fetchall()
    conn.row_factory = None

    if not chunks:
        return {
            "chunks_scored": 0,
            "score_distribution": {"high_risk": 0, "medium": 0, "low_risk": 0},
            "avg_composite": 0.0,
        }

    # Phase 1: Compute raw scores
    raw_volatility = {}  # file_path -> raw value (cached per file)
    raw_coupling = {}    # chunk_id -> raw value
    raw_scores = []      # list of (chunk, vol, cov, comp, coup, stale)

    for chunk in chunks:
        fp = chunk["file_path"]

        # Volatility (cached per file)
        if fp not in raw_volatility:
            raw_volatility[fp] = compute_volatility(
                conn, project_id, fp, GIT_HISTORY_WEEKS
            )
        vol_raw = raw_volatility[fp]

        # Coverage
        cov = compute_coverage(conn, chunk["id"], chunk["chunk_type"])

        # Complexity
        comp = compute_complexity(chunk.get("structural_metadata"))

        # Coupling
        coup_raw = compute_coupling(conn, chunk["id"])
        raw_coupling[chunk["id"]] = coup_raw

        # Staleness
        stale = compute_staleness(conn, chunk["id"], fp, project_id)

        raw_scores.append({
            "chunk": chunk,
            "volatility_raw": vol_raw,
            "coverage": cov,
            "complexity": comp,
            "coupling_raw": coup_raw,
            "staleness": stale,
        })

    # Phase 2: Percentile normalization for volatility and coupling
    vol_values = sorted(set(s["volatility_raw"] for s in raw_scores))
    coup_values = sorted(set(s["coupling_raw"] for s in raw_scores))

    vol_ranks = {v: i / max(len(vol_values) - 1, 1) for i, v in enumerate(vol_values)}
    coup_ranks = {v: i / max(len(coup_values) - 1, 1) for i, v in enumerate(coup_values)}

    # Phase 3: Compute composite and insert
    high_risk = 0
    medium = 0
    low_risk = 0
    total_composite = 0.0

    for entry in raw_scores:
        chunk = entry["chunk"]
        vol_score = vol_ranks.get(entry["volatility_raw"], 0.5)
        cov_score = entry["coverage"]
        comp_score = entry["complexity"]
        coup_score = coup_ranks.get(entry["coupling_raw"], 0.5)
        stale_score = entry["staleness"]

        composite = compute_composite(
            vol_score, cov_score, comp_score, coup_score, stale_score,
            SCORING_WEIGHTS,
        )

        db.create_health_score(
            conn, chunk["id"],
            cycle_id=cycle_id,
            volatility_score=round(vol_score, 4),
            coverage_score=round(cov_score, 4),
            complexity_score=round(comp_score, 4),
            coupling_score=round(coup_score, 4),
            staleness_score=round(stale_score, 4),
            composite_score=round(composite, 4),
        )

        total_composite += composite
        if composite >= 0.7:
            high_risk += 1
        elif composite >= 0.3:
            medium += 1
        else:
            low_risk += 1

    return {
        "chunks_scored": len(raw_scores),
        "score_distribution": {
            "high_risk": high_risk,
            "medium": medium,
            "low_risk": low_risk,
        },
        "avg_composite": round(total_composite / len(raw_scores), 4),
    }


def compute_volatility(conn, project_id: int, file_path: str,
                       git_window_weeks: int) -> float:
    """
    Compute raw volatility for a file based on recency-weighted commit count.

    Returns raw value (to be percentile-normalized later).
    """
    cur = conn.execute(
        "SELECT commit_date FROM git_changes WHERE project_id = ? AND file_path = ?",
        (project_id, file_path),
    )
    rows = cur.fetchall()

    if not rows:
        return 0.5  # Neutral for unknown

    now = datetime.now(timezone.utc)
    window_days = git_window_weeks * 7
    total_weight = 0.0

    for (commit_date_str,) in rows:
        try:
            commit_date = datetime.fromisoformat(commit_date_str)
            if commit_date.tzinfo is None:
                commit_date = commit_date.replace(tzinfo=timezone.utc)
            days_ago = (now - commit_date).days
            weight = max(0.0, 1.0 - (days_ago / window_days))
            total_weight += weight
        except (ValueError, TypeError):
            continue

    return total_weight


def compute_coverage(conn, chunk_id: int, chunk_type: str) -> float:
    """
    Compute test coverage score for a chunk.

    Returns 0.0 (well tested) to 1.0 (no tests). test_case chunks return 0.0.
    """
    if chunk_type == "test_case":
        return 0.0

    # Direct test bindings (target_chunk_id)
    cur = conn.execute(
        "SELECT COUNT(*) FROM chunk_symbol_bindings "
        "WHERE binding_type = 'tests' AND target_chunk_id = ?",
        (chunk_id,),
    )
    direct_count = cur.fetchone()[0]

    # Name-based test bindings
    if direct_count == 0:
        cur = conn.execute(
            "SELECT COUNT(*) FROM chunk_symbol_bindings csb "
            "JOIN code_chunks cc ON csb.chunk_id = cc.id "
            "WHERE csb.binding_type = 'tests' "
            "AND csb.symbol_name = (SELECT name FROM code_chunks WHERE id = ?) "
            "AND cc.chunk_type = 'test_case'",
            (chunk_id,),
        )
        direct_count = cur.fetchone()[0]

    if direct_count == 0:
        return 1.0
    elif direct_count == 1:
        return 0.5
    else:
        return 0.2


def compute_complexity(structural_metadata_json: Optional[str]) -> float:
    """
    Compute complexity score from structural metadata JSON.

    Returns 0.0 (simple) to 1.0 (very complex). Sigmoid normalization.
    """
    if not structural_metadata_json:
        return 0.5

    try:
        meta = json.loads(structural_metadata_json)
    except (json.JSONDecodeError, TypeError):
        return 0.5

    cc = meta.get("cyclomatic_complexity", 1)
    nd = meta.get("nesting_depth", 0)
    pc = meta.get("parameter_count", 0)

    raw = 0.5 * cc + 0.3 * nd + 0.2 * pc
    score = 1.0 / (1.0 + math.exp(-0.3 * (raw - 10)))
    return score


def compute_coupling(conn, chunk_id: int) -> float:
    """
    Compute raw coupling for a chunk (inbound + outbound dependency count).

    Returns raw count (to be percentile-normalized later).
    """
    cur = conn.execute(
        "SELECT COUNT(*) FROM chunk_dependencies WHERE source_chunk_id = ?",
        (chunk_id,),
    )
    outbound = cur.fetchone()[0]

    cur = conn.execute(
        "SELECT COUNT(*) FROM chunk_dependencies WHERE target_chunk_id = ?",
        (chunk_id,),
    )
    inbound = cur.fetchone()[0]

    return float(outbound + inbound)


def compute_staleness(conn, chunk_id: int, file_path: str,
                      project_id: int) -> float:
    """
    Compute staleness: fraction of dependencies modified more recently than this chunk.

    Returns 0.0 (fresh) to 1.0 (very stale).
    """
    # Get chunk's last commit date
    cur = conn.execute(
        "SELECT MAX(commit_date) FROM git_changes "
        "WHERE project_id = ? AND file_path = ?",
        (project_id, file_path),
    )
    row = cur.fetchone()
    if not row or not row[0]:
        return 0.5  # No git history — neutral

    chunk_last_modified = row[0]

    # Get all outbound dependencies
    cur = conn.execute(
        "SELECT cc.file_path FROM chunk_dependencies cd "
        "JOIN code_chunks cc ON cd.target_chunk_id = cc.id "
        "WHERE cd.source_chunk_id = ?",
        (chunk_id,),
    )
    dep_files = [r[0] for r in cur.fetchall()]

    if not dep_files:
        return 0.0  # No dependencies — not stale

    stale_count = 0
    total_deps = 0

    for dep_file in set(dep_files):
        cur = conn.execute(
            "SELECT MAX(commit_date) FROM git_changes "
            "WHERE project_id = ? AND file_path = ?",
            (project_id, dep_file),
        )
        dep_row = cur.fetchone()
        if dep_row and dep_row[0]:
            total_deps += 1
            if dep_row[0] > chunk_last_modified:
                stale_count += 1

    if total_deps == 0:
        return 0.0

    return stale_count / total_deps


def compute_composite(volatility: float, coverage: float, complexity: float,
                      coupling: float, staleness: float,
                      weights: dict) -> float:
    """Weighted combination of dimension scores. Clamped to 0.0-1.0."""
    composite = (
        weights["volatility"] * volatility
        + weights["coverage"] * coverage
        + weights["complexity"] * complexity
        + weights["coupling"] * coupling
        + weights["staleness"] * staleness
    )
    return max(0.0, min(1.0, composite))


def ingest_test_results(conn, project_name: str,
                        cycle_id: int) -> dict:
    """
    Run pytest against the target project and store results.

    Returns status dict.
    """
    project = db.get_project(conn, project_name)
    if project is None:
        return {"status": "skipped", "reason": "Project not found"}

    project_path = SCAN_TARGETS.get(project_name)
    if not project_path:
        return {"status": "skipped", "reason": "No scan target"}

    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", project_path, "--tb=no", "-q"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=project_path,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return {"status": "skipped", "reason": str(e)}

    output = result.stdout + result.stderr
    passed, failed, skipped, total = _parse_pytest_output(output)

    # Extract failed test names
    failed_names = []
    for line in output.split("\n"):
        line = line.strip()
        if line.startswith("FAILED"):
            failed_names.append(line.replace("FAILED ", ""))

    now = datetime.now(timezone.utc).isoformat()
    db.create_test_result(
        conn, project["id"],
        run_date=now,
        total_tests=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        failed_test_names=json.dumps(failed_names),
        cycle_id=cycle_id,
    )

    return {
        "status": "complete",
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
    }


def _parse_pytest_output(output: str) -> tuple[int, int, int, int]:
    """
    Parse pytest summary line to extract pass/fail/skip counts.

    Returns (passed, failed, skipped, total).
    """
    passed = 0
    failed = 0
    skipped = 0

    for line in reversed(output.strip().split("\n")):
        line = line.strip()
        if not line:
            continue
        if "passed" in line or "failed" in line or "error" in line:
            import re
            m_passed = re.search(r"(\d+)\s+passed", line)
            m_failed = re.search(r"(\d+)\s+failed", line)
            m_skipped = re.search(r"(\d+)\s+skipped", line)
            m_error = re.search(r"(\d+)\s+error", line)
            if m_passed:
                passed = int(m_passed.group(1))
            if m_failed:
                failed = int(m_failed.group(1))
            if m_skipped:
                skipped = int(m_skipped.group(1))
            if m_error:
                failed += int(m_error.group(1))
            break

    total = passed + failed + skipped
    return passed, failed, skipped, total
