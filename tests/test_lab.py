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
    find_best_practice_deviations,
    find_intent_gaps,
    write_intent_audit,
    generate_planner_constraints,
    write_cycle_report,
    generate_specialist_update_data,
    _extract_project_mission,
    _is_noise_chunk,
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
        start_line=1, end_line=1, last_seen_cycle=1,
    )

    # High-risk untested function
    c1 = create_chunk(
        conn, project_id=pid, file_path="main.py", chunk_type="function",
        name="risky_func", content="def risky_func(): pass",
        content_hash="c1_h", start_line=1, end_line=10, last_seen_cycle=1,
    )
    meta1 = json.dumps({"cyclomatic_complexity": 20, "nesting_depth": 5, "parameter_count": 4,
                         "import_count": 0, "has_docstring": False, "line_count": 10})
    conn.execute("UPDATE code_chunks SET structural_metadata = ? WHERE id = ?", (meta1, c1))
    conn.commit()
    create_health_score(conn, c1, cycle_id=1, volatility_score=0.9,
                        coverage_score=1.0, complexity_score=0.95,
                        coupling_score=0.85, staleness_score=0.85,
                        composite_score=0.75)

    # Low-risk tested function
    c2 = create_chunk(
        conn, project_id=pid, file_path="utils.py", chunk_type="function",
        name="safe_func", content="def safe_func(): pass",
        content_hash="c2_h", start_line=1, end_line=3, last_seen_cycle=1,
    )
    create_health_score(conn, c2, cycle_id=1, volatility_score=0.1,
                        coverage_score=0.2, complexity_score=0.1,
                        coupling_score=0.1, staleness_score=0.0,
                        composite_score=0.1)

    # Test case
    c3 = create_chunk(
        conn, project_id=pid, file_path="test_utils.py", chunk_type="test_case",
        name="test_safe", content="def test_safe(): pass",
        content_hash="c3_h", start_line=1, end_line=2, last_seen_cycle=1,
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
        content_hash="c4_h", start_line=1, end_line=3, last_seen_cycle=1,
    )
    create_health_score(conn, c4, cycle_id=1, volatility_score=0.5,
                        coverage_score=1.0, complexity_score=0.5,
                        coupling_score=0.0, staleness_score=0.0,
                        composite_score=0.4)
    create_similarity(conn, c1, c4, 0.85, cycle_id=1)

    # Git changes for co-change
    for i in range(5):
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
    assert "risky_func" in stale_names  # staleness=0.85 >= 0.8 threshold


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
    specialist_data = generate_specialist_update_data(conn, pid, 1)
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


# --- find_intent_gaps ---

REQUIRED_INTENT_KEYS = {
    "finding_type", "severity", "title", "what",
    "why_it_matters", "what_needs_discovering",
    "success_looks_like", "diagnostic_type", "chunk_ids",
}


def test_find_intent_gaps_missing_brief(conn, tmp_path):
    """Returns empty list when PROJECT_BRIEF.md is absent."""
    result = find_intent_gaps(conn, "no-such-project", str(tmp_path), top_n=5)
    assert result == []


def test_find_intent_gaps_returns_required_keys(conn, tmp_path):
    """Returns dicts with all required keys when minimal data exists."""
    # Write PROJECT_BRIEF and domain-glossary
    (tmp_path / "PROJECT_BRIEF.md").write_text("Test project brief.")
    glossary_dir = tmp_path / "knowledge" / "research"
    glossary_dir.mkdir(parents=True)
    (glossary_dir / "domain-glossary.md").write_text("# Glossary\n")

    # Create project and a coverage-gap chunk in the in-memory DB
    pid = create_project(conn, "intent-test", str(tmp_path))
    chunk_id = create_chunk(
        conn, project_id=pid, file_path="src/foo.py", chunk_type="function",
        name="do_thing", content="def do_thing(): pass",
        content_hash="abc123", start_line=1, end_line=3,
        last_seen_cycle=1,
    )
    create_health_score(
        conn, chunk_id, cycle_id=1,
        composite_score=0.80, coverage_score=0.90,
        volatility_score=0.85, coupling_score=0.50,
        complexity_score=0.40, staleness_score=0.30,
    )

    result = find_intent_gaps(conn, "intent-test", str(tmp_path), top_n=5)

    assert isinstance(result, list)
    assert len(result) > 0
    for finding in result:
        missing = REQUIRED_INTENT_KEYS - finding.keys()
        assert not missing, f"Missing keys: {missing}"
        assert isinstance(finding["chunk_ids"], list)
        assert finding["finding_type"] == "intent_gap"
        assert finding["severity"] in ("CRITICAL", "HIGH", "MEDIUM", "LOW")


def test_find_intent_gaps_excludes_stale_chunks(conn, tmp_path):
    """Belt-and-suspenders: chunks with wrong last_seen_cycle are excluded."""
    (tmp_path / "PROJECT_BRIEF.md").write_text("Test project brief.")
    glossary_dir = tmp_path / "knowledge" / "research"
    glossary_dir.mkdir(parents=True)
    (glossary_dir / "domain-glossary.md").write_text("# Glossary\n")

    pid = create_project(conn, "stale-test", str(tmp_path))

    # Live chunk — stamped for cycle 2
    live_id = create_chunk(
        conn, project_id=pid, file_path="src/live.py", chunk_type="function",
        name="live_fn", content="def live_fn(): pass",
        content_hash="live_h", start_line=1, end_line=3,
        last_seen_cycle=2,
    )
    create_health_score(
        conn, live_id, cycle_id=2,
        composite_score=0.80, coverage_score=0.90,
        volatility_score=0.85, coupling_score=0.50,
        complexity_score=0.40, staleness_score=0.30,
    )

    # Phantom chunk — last_seen_cycle=1, but has cycle-2 health_scores
    phantom_id = create_chunk(
        conn, project_id=pid, file_path="src/phantom.py", chunk_type="function",
        name="phantom_fn", content="def phantom_fn(): pass",
        content_hash="phantom_h", start_line=1, end_line=3,
        last_seen_cycle=1,
    )
    create_health_score(
        conn, phantom_id, cycle_id=2,
        composite_score=0.90, coverage_score=0.95,
        volatility_score=0.95, coupling_score=0.60,
        complexity_score=0.50, staleness_score=0.40,
    )

    result = find_intent_gaps(conn, "stale-test", str(tmp_path), top_n=10)

    names = [f["chunk_name"] for f in result]
    assert "live_fn" in names, "Live chunk should appear in findings"
    assert "phantom_fn" not in names, "Phantom chunk must be excluded by freshness guard"


# --- _extract_project_mission ---

def test_extract_project_mission_found():
    brief = "# My Project\n\n## Mission\n\nSome mission text.\n\n## Other\n\nOther stuff."
    result = _extract_project_mission(brief)
    assert result == "Some mission text."


def test_extract_project_mission_not_found():
    result = _extract_project_mission("This is plain text with no headings.")
    assert result == ""


def test_find_intent_gaps_excludes_test_files(conn, tmp_path):
    """Findings must not include chunks whose file_path starts with tests/."""
    (tmp_path / "PROJECT_BRIEF.md").write_text("## Mission\n\nProcess invoices.\n")
    glossary_dir = tmp_path / "knowledge" / "research"
    glossary_dir.mkdir(parents=True)
    (glossary_dir / "domain-glossary.md").write_text("# Glossary\n")

    pid = create_project(conn, "gap-filter-test", str(tmp_path))

    # Chunk in tests/ — should be excluded
    test_chunk = create_chunk(
        conn, project_id=pid, file_path="tests/test_foo.py", chunk_type="function",
        name="test_something", content="def test_something(): pass",
        content_hash="test_h1", start_line=1, end_line=3,
    )
    create_health_score(
        conn, test_chunk, cycle_id=1,
        composite_score=0.90, coverage_score=0.95,
        volatility_score=0.90, coupling_score=0.90,
        complexity_score=0.90, staleness_score=0.50,
    )

    # Chunk in app.py — should appear
    app_chunk = create_chunk(
        conn, project_id=pid, file_path="app.py", chunk_type="function",
        name="process_invoice", content="def process_invoice(): pass",
        content_hash="app_h1", start_line=1, end_line=5,
    )
    create_health_score(
        conn, app_chunk, cycle_id=1,
        composite_score=0.85, coverage_score=0.90,
        volatility_score=0.85, coupling_score=0.80,
        complexity_score=0.80, staleness_score=0.40,
    )

    result = find_intent_gaps(conn, "gap-filter-test", str(tmp_path), top_n=10)

    chunk_files = [f["chunk_file"] for f in result]
    for cf in chunk_files:
        assert not cf.startswith("tests/"), f"Test file leaked into findings: {cf}"


def test_is_noise_chunk_test_file():
    assert _is_noise_chunk({"name": "foo", "file_path": "tests/test_bar.py"}) is True


def test_is_noise_chunk_session_lifecycle():
    assert _is_noise_chunk({"name": "execute", "file_path": "profile_ingestion.py"}) is True
    assert _is_noise_chunk({"name": "execute", "file_path": "app.py"}) is False


def test_is_noise_chunk_connection_factory():
    assert _is_noise_chunk({"name": "get_connection", "file_path": "database.py"}) is True


# --- Untested Complexity section ---

def test_cycle_report_includes_untested_complexity(conn, tmp_path):
    """Cycle report must include Untested Complexity section with correct ordering."""
    pid = create_project(conn, "uc-test", "/tmp/uc-test")

    # High-complexity zero-coverage chunk
    c_high = create_chunk(
        conn, project_id=pid, file_path="core.py", chunk_type="function",
        name="complex_untested", content="def complex_untested(): pass",
        content_hash="uc_h1", start_line=1, end_line=10, last_seen_cycle=1,
    )
    create_health_score(
        conn, c_high, cycle_id=1, volatility_score=0.5,
        coverage_score=1.0, complexity_score=0.95,
        coupling_score=0.3, staleness_score=0.1,
        composite_score=0.6,
    )

    # Lower-complexity zero-coverage chunk
    c_low = create_chunk(
        conn, project_id=pid, file_path="helpers.py", chunk_type="function",
        name="simple_untested", content="def simple_untested(): pass",
        content_hash="uc_h2", start_line=1, end_line=3, last_seen_cycle=1,
    )
    create_health_score(
        conn, c_low, cycle_id=1, volatility_score=0.3,
        coverage_score=1.0, complexity_score=0.5,
        coupling_score=0.1, staleness_score=0.0,
        composite_score=0.35,
    )

    findings = {
        "coverage_gaps": [], "coupling_hotspots": [], "clone_candidates": [],
        "staleness_alerts": [], "complexity_hotspots": [],
        "cochange_patterns": [], "best_practice_deviations": [],
        "intent_gaps": [],
    }
    specialist_data = generate_specialist_update_data(conn, pid, 1)
    report_path = str(tmp_path / "uc-report.md")

    write_cycle_report(
        conn, "uc-test", 1, findings, [], specialist_data,
        report_path, "2026-05-18T10:00:00",
    )

    with open(report_path, "r") as f:
        content = f.read()

    assert "## Untested Complexity" in content
    # Higher cov×comp chunk should appear before lower one
    pos_high = content.index("complex_untested")
    pos_low = content.index("simple_untested")
    assert pos_high < pos_low, (
        "complex_untested (cov×comp=0.95) must appear before simple_untested (cov×comp=0.50)"
    )


# --- Freshness filter tests ---

def test_clone_candidates_excludes_stale_chunks(conn):
    """find_clone_candidates excludes chunks with stale last_seen_cycle."""
    pid = create_project(conn, "clone-filter-test", "/tmp/clone-filter-test")

    # Live chunk (last_seen_cycle=1)
    live = create_chunk(
        conn, project_id=pid, file_path="app.py", chunk_type="function",
        name="live_fn", content="def live_fn(): pass",
        content_hash="live_h", start_line=1, end_line=3, last_seen_cycle=1,
    )

    # Stale chunk (last_seen_cycle=None — orphan)
    stale = create_chunk(
        conn, project_id=pid, file_path="app.py", chunk_type="function",
        name="stale_fn", content="def stale_fn(): pass",
        content_hash="stale_h", start_line=5, end_line=7,
    )

    # Similarity between live and stale
    create_similarity(conn, live, stale, 0.95, cycle_id=1)

    clones = find_clone_candidates(conn, pid, 1)
    chunk_ids = set()
    for c in clones:
        chunk_ids.add(c["chunk_a_id"])
        chunk_ids.add(c["chunk_b_id"])
    assert stale not in chunk_ids, "Stale chunk must be excluded by freshness filter"


def test_clone_candidates_includes_fresh_pair(conn):
    """find_clone_candidates returns pairs where both sides are fresh."""
    pid = create_project(conn, "clone-fresh-test", "/tmp/clone-fresh-test")

    a = create_chunk(
        conn, project_id=pid, file_path="a.py", chunk_type="function",
        name="fn_a", content="def fn_a(): pass",
        content_hash="a_h", start_line=1, end_line=3, last_seen_cycle=1,
    )
    b = create_chunk(
        conn, project_id=pid, file_path="b.py", chunk_type="function",
        name="fn_b", content="def fn_b(): pass",
        content_hash="b_h", start_line=1, end_line=3, last_seen_cycle=1,
    )
    create_similarity(conn, a, b, 0.90, cycle_id=1)

    clones = find_clone_candidates(conn, pid, 1)
    assert len(clones) == 1
    assert clones[0]["similarity_score"] == 0.90


def test_best_practice_deviations_excludes_stale(conn):
    """find_best_practice_deviations excludes chunks with wrong last_seen_cycle."""
    pid = create_project(conn, "bp-filter-test", "/tmp/bp-filter-test")

    # Stale classified chunk (last_seen_cycle=None)
    create_chunk(
        conn, project_id=pid, file_path="app.py", chunk_type="function",
        name="stale_handler", content="def stale_handler(): pass",
        content_hash="sh", start_line=1, end_line=3,
        functional_role="route_handler",
    )

    # Fresh classified chunk (last_seen_cycle=2)
    create_chunk(
        conn, project_id=pid, file_path="app.py", chunk_type="function",
        name="fresh_handler", content="def fresh_handler(): pass",
        content_hash="fh", start_line=5, end_line=7,
        last_seen_cycle=2, functional_role="route_handler",
    )

    results = find_best_practice_deviations(conn, pid, 2)
    names = [r["name"] for r in results]
    assert "stale_handler" not in names, "Stale chunk must be filtered out"
    # fresh_handler may or may not have deviations depending on practice rules,
    # but stale_handler must never appear


def test_specialist_update_data_excludes_stale(conn):
    """generate_specialist_update_data only counts chunks with matching last_seen_cycle."""
    pid = create_project(conn, "stats-filter-test", "/tmp/stats-filter-test")

    # Fresh chunk
    create_chunk(
        conn, project_id=pid, file_path="a.py", chunk_type="function",
        name="fn_fresh", content="def fn_fresh(): pass",
        content_hash="fh1", start_line=1, end_line=3, last_seen_cycle=2,
    )

    # Stale chunk (should not count)
    create_chunk(
        conn, project_id=pid, file_path="b.py", chunk_type="function",
        name="fn_stale", content="def fn_stale(): pass",
        content_hash="sh1", start_line=1, end_line=3, last_seen_cycle=1,
    )

    data = generate_specialist_update_data(conn, pid, 2)
    assert data["total_functions"] == 1, "Only fresh chunk should be counted"
