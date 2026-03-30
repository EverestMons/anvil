"""
Tests for Anvil Lab — findings analysis, cycle reports, planner constraints.
"""
import json
import os
import sqlite3

import pytest

from src.db import (
    init_db, create_project, create_chunk, create_health_score,
    create_dependency, create_symbol_binding, create_similarity,
    create_git_change, create_fingerprint,
)
from src.lab import (
    run_lab,
    find_coverage_gaps,
    find_coupling_hotspots,
    find_clone_candidates,
    find_cochange_patterns,
    find_staleness_alerts,
    find_complexity_hotspots,
    generate_planner_constraints,
    write_cycle_report,
    generate_specialist_update_data,
)
from src.config import SCAN_TARGETS


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    init_db(c)
    c.execute("PRAGMA foreign_keys=ON")
    yield c
    c.close()


@pytest.fixture
def lab_project(conn):
    """Create a project with scored chunks, deps, bindings for lab testing."""
    pid = create_project(conn, "lab-test", "/tmp/lab-test")

    # Module
    mod = create_chunk(
        conn, project_id=pid, file_path="main.py", chunk_type="module",
        name="main.py", content="# mod", content_hash="mod_h",
        start_line=1, end_line=1,
    )

    # High-risk untested function
    c1 = create_chunk(
        conn, project_id=pid, file_path="main.py", chunk_type="function",
        name="risky_func", content="def risky_func(): pass",
        content_hash="c1_h", start_line=1, end_line=10,
    )
    meta1 = json.dumps({"cyclomatic_complexity": 20, "nesting_depth": 5, "parameter_count": 4,
                         "import_count": 0, "has_docstring": False, "line_count": 10})
    conn.execute("UPDATE code_chunks SET structural_metadata = ? WHERE id = ?", (meta1, c1))
    conn.commit()
    create_health_score(conn, c1, cycle_id=1, volatility_score=0.9,
                        coverage_score=1.0, complexity_score=0.95,
                        coupling_score=0.85, staleness_score=0.7,
                        composite_score=0.75)

    # Low-risk tested function
    c2 = create_chunk(
        conn, project_id=pid, file_path="utils.py", chunk_type="function",
        name="safe_func", content="def safe_func(): pass",
        content_hash="c2_h", start_line=1, end_line=3,
    )
    create_health_score(conn, c2, cycle_id=1, volatility_score=0.1,
                        coverage_score=0.2, complexity_score=0.1,
                        coupling_score=0.1, staleness_score=0.0,
                        composite_score=0.1)

    # Test case
    c3 = create_chunk(
        conn, project_id=pid, file_path="test_utils.py", chunk_type="test_case",
        name="test_safe", content="def test_safe(): pass",
        content_hash="c3_h", start_line=1, end_line=2,
    )
    create_health_score(conn, c3, cycle_id=1, volatility_score=0.0,
                        coverage_score=0.0, complexity_score=0.1,
                        coupling_score=0.0, staleness_score=0.0,
                        composite_score=0.02)

    # Dependency c1 -> c2
    create_dependency(conn, c1, c2, "call", "cross_file")

    # Test binding
    create_symbol_binding(conn, c3, "safe_func", "tests")

    # Similarity pair
    c4 = create_chunk(
        conn, project_id=pid, file_path="other.py", chunk_type="function",
        name="clone_func", content="def clone_func(): pass",
        content_hash="c4_h", start_line=1, end_line=3,
    )
    create_health_score(conn, c4, cycle_id=1, volatility_score=0.5,
                        coverage_score=1.0, complexity_score=0.5,
                        coupling_score=0.0, staleness_score=0.0,
                        composite_score=0.4)
    create_similarity(conn, c1, c4, 0.85, cycle_id=1)

    # Git changes for co-change
    for i in range(4):
        create_git_change(conn, pid, "main.py", f"hash{i}",
                          f"2026-03-{20+i}", f"commit {i}", "dev")
        create_git_change(conn, pid, "utils.py", f"hash{i}",
                          f"2026-03-{20+i}", f"commit {i}", "dev")
    # Separate commit for other.py
    create_git_change(conn, pid, "other.py", "hash_other",
                      "2026-03-25", "other commit", "dev")

    return pid, c1, c2, c3, c4


# --- find_coverage_gaps ---

def test_find_coverage_gaps(conn, lab_project):
    pid, c1, _, _, _ = lab_project
    gaps = find_coverage_gaps(conn, pid, 1)
    assert len(gaps) >= 1
    names = [g["name"] for g in gaps]
    assert "risky_func" in names


def test_coverage_gaps_excludes_tested(conn, lab_project):
    pid, _, _, _, _ = lab_project
    gaps = find_coverage_gaps(conn, pid, 1)
    names = [g["name"] for g in gaps]
    assert "safe_func" not in names  # Low composite, below threshold


# --- find_coupling_hotspots ---

def test_find_coupling_hotspots(conn, lab_project):
    pid, c1, _, _, _ = lab_project
    hotspots = find_coupling_hotspots(conn, pid, 1)
    assert len(hotspots) >= 1
    for h in hotspots:
        assert "inbound" in h
        assert "outbound" in h


# --- find_clone_candidates ---

def test_find_clone_candidates(conn, lab_project):
    pid, _, _, _, _ = lab_project
    clones = find_clone_candidates(conn, pid, 1)
    assert len(clones) >= 1
    assert clones[0]["similarity_score"] >= 0.7


# --- find_cochange_patterns ---

def test_find_cochange_patterns(conn, lab_project):
    pid, _, _, _, _ = lab_project
    patterns = find_cochange_patterns(conn, pid)
    assert len(patterns) >= 1
    # main.py and utils.py share 4 commits
    pair = next(
        (p for p in patterns
         if {p["file_a"], p["file_b"]} == {"main.py", "utils.py"}),
        None,
    )
    assert pair is not None
    assert pair["cochange_count"] >= 3
    assert pair["jaccard_score"] > 0


# --- find_staleness_alerts ---

def test_find_staleness_alerts(conn, lab_project):
    pid, _, _, _, _ = lab_project
    alerts = find_staleness_alerts(conn, pid, 1)
    stale_names = [a["name"] for a in alerts]
    assert "risky_func" in stale_names  # staleness=0.7 >= 0.6 threshold


# --- find_complexity_hotspots ---

def test_find_complexity_hotspots(conn, lab_project):
    pid, _, _, _, _ = lab_project
    hotspots = find_complexity_hotspots(conn, pid, 1)
    assert len(hotspots) >= 1
    assert hotspots[0]["cyclomatic_complexity"] > 0


# --- generate_planner_constraints ---

def test_planner_constraints_structure(conn, lab_project):
    pid, _, _, _, _ = lab_project
    findings = {
        "coverage_gaps": find_coverage_gaps(conn, pid, 1),
        "coupling_hotspots": find_coupling_hotspots(conn, pid, 1),
        "clone_candidates": find_clone_candidates(conn, pid, 1),
        "staleness_alerts": find_staleness_alerts(conn, pid, 1),
        "complexity_hotspots": find_complexity_hotspots(conn, pid, 1),
        "cochange_patterns": find_cochange_patterns(conn, pid),
    }
    constraints = generate_planner_constraints(conn, "lab-test", 1, findings)
    assert len(constraints) > 0
    for c in constraints:
        assert "type" in c
        assert "target" in c
        assert "reason" in c
        assert "severity" in c
        assert c["type"] in ("coverage_required", "verify_dependents",
                             "refactor_candidate", "investigation_needed")
        assert c["severity"] in ("high", "medium", "low")


def test_planner_constraints_has_coverage_type(conn, lab_project):
    pid, _, _, _, _ = lab_project
    findings = {
        "coverage_gaps": find_coverage_gaps(conn, pid, 1),
        "coupling_hotspots": [],
        "clone_candidates": [],
        "staleness_alerts": [],
        "complexity_hotspots": [],
        "cochange_patterns": [],
    }
    constraints = generate_planner_constraints(conn, "lab-test", 1, findings)
    types = {c["type"] for c in constraints}
    assert "coverage_required" in types


# --- write_cycle_report ---

def test_write_cycle_report(conn, lab_project, tmp_path):
    pid, _, _, _, _ = lab_project
    findings = {
        "coverage_gaps": find_coverage_gaps(conn, pid, 1),
        "coupling_hotspots": find_coupling_hotspots(conn, pid, 1),
        "clone_candidates": find_clone_candidates(conn, pid, 1),
        "staleness_alerts": find_staleness_alerts(conn, pid, 1),
        "complexity_hotspots": find_complexity_hotspots(conn, pid, 1),
        "cochange_patterns": find_cochange_patterns(conn, pid),
    }
    constraints = generate_planner_constraints(conn, "lab-test", 1, findings)
    specialist_data = generate_specialist_update_data(conn, pid)
    report_path = str(tmp_path / "cycle-1-report.md")

    write_cycle_report(
        conn, "lab-test", 1, findings, constraints,
        specialist_data, report_path, "2026-03-30T10:00:00",
    )

    # Verify markdown file exists with sections
    assert os.path.isfile(report_path)
    with open(report_path, "r") as f:
        content = f.read()
    assert "Executive Summary" in content
    assert "Coverage Gaps" in content
    assert "Coupling Hotspots" in content
    assert "Clone Candidates" in content
    assert "Staleness Alerts" in content
    assert "Complexity Hotspots" in content
    assert "Co-Change Patterns" in content
    assert "Planner Constraints" in content
    assert "Specialist Update Data" in content

    # Verify DB row
    cur = conn.execute("SELECT * FROM cycle_reports WHERE cycle_number = 1")
    row = cur.fetchone()
    assert row is not None


# --- run_lab end-to-end ---

def test_run_lab_end_to_end(conn, lab_project, tmp_path, monkeypatch):
    monkeypatch.setitem(SCAN_TARGETS, "lab-test", "/tmp/lab-test")
    monkeypatch.setattr("src.lab.ANVIL_ROOT", str(tmp_path))

    # Create knowledge/research dir
    os.makedirs(str(tmp_path / "knowledge" / "research"), exist_ok=True)

    result = run_lab(conn, "lab-test", 1)

    assert result["total_findings"] > 0
    assert result["constraints_generated"] > 0
    assert result["report_path"].endswith(".md")

    # At least 3 finding categories should have results
    categories_with_findings = sum(
        1 for v in result["findings"].values() if v > 0
    )
    assert categories_with_findings >= 3


def test_run_lab_unknown_project(conn):
    with pytest.raises(ValueError):
        run_lab(conn, "nonexistent", 1)
