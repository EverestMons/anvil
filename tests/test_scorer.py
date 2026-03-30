"""
Tests for Anvil scorer — volatility, coverage, complexity, coupling, staleness, composite.
"""
import json
import sqlite3
from datetime import datetime, timezone, timedelta

import pytest

from src.db import (
    init_db, create_project, create_chunk, create_fingerprint,
    create_symbol_binding, create_dependency, create_git_change,
)
from src.scorer import (
    score_project,
    compute_volatility,
    compute_coverage,
    compute_complexity,
    compute_coupling,
    compute_staleness,
    compute_composite,
    ingest_test_results,
    _parse_pytest_output,
)
from src.config import SCAN_TARGETS, SCORING_WEIGHTS


@pytest.fixture
def conn():
    """In-memory database with schema initialized."""
    c = sqlite3.connect(":memory:")
    init_db(c)
    c.execute("PRAGMA foreign_keys=ON")
    yield c
    c.close()


@pytest.fixture
def scored_project(conn):
    """Create a small project with chunks, deps, git history for scoring."""
    pid = create_project(conn, "test-proj", "/tmp/test")
    now = datetime.now(timezone.utc)

    # Module chunk
    mod_id = create_chunk(
        conn, project_id=pid, file_path="main.py", chunk_type="module",
        name="main.py", content="# module", content_hash="mod_h",
        start_line=1, end_line=1,
    )

    # Function chunk with structural metadata
    meta = json.dumps({
        "cyclomatic_complexity": 8,
        "nesting_depth": 3,
        "parameter_count": 2,
        "import_count": 1,
        "has_docstring": True,
        "line_count": 20,
    })
    c1 = create_chunk(
        conn, project_id=pid, file_path="main.py", chunk_type="function",
        name="process", content="def process(a, b): pass",
        content_hash="c1_h", start_line=1, end_line=20,
    )
    conn.execute(
        "UPDATE code_chunks SET structural_metadata = ? WHERE id = ?",
        (meta, c1),
    )
    conn.commit()

    # Simple function
    c2 = create_chunk(
        conn, project_id=pid, file_path="utils.py", chunk_type="function",
        name="helper", content="def helper(): pass",
        content_hash="c2_h", start_line=1, end_line=3,
    )
    simple_meta = json.dumps({
        "cyclomatic_complexity": 1,
        "nesting_depth": 0,
        "parameter_count": 0,
        "import_count": 0,
        "has_docstring": False,
        "line_count": 3,
    })
    conn.execute(
        "UPDATE code_chunks SET structural_metadata = ? WHERE id = ?",
        (simple_meta, c2),
    )
    conn.commit()

    # Test case chunk
    c3 = create_chunk(
        conn, project_id=pid, file_path="test_main.py", chunk_type="test_case",
        name="test_process", content="def test_process(): pass",
        content_hash="c3_h", start_line=1, end_line=2,
    )

    # Dependencies: c1 -> c2
    create_dependency(conn, c1, c2, "call", "cross_file")

    # Test binding: c3 tests "process"
    create_symbol_binding(conn, c3, "process", "tests")

    # Git history: main.py has many recent commits, utils.py has few
    for i in range(5):
        date = (now - timedelta(days=i * 2)).isoformat()
        create_git_change(conn, pid, "main.py", f"hash{i}", date,
                          f"commit {i}", "dev")

    create_git_change(conn, pid, "utils.py", "hash_old",
                      (now - timedelta(days=20)).isoformat(),
                      "old commit", "dev")

    return pid, c1, c2, c3


# --- compute_volatility ---

def test_volatility_with_recent_commits(conn, scored_project):
    pid, c1, c2, c3 = scored_project
    vol = compute_volatility(conn, pid, "main.py", 4)
    assert vol > 0  # Has commits, should have positive weight


def test_volatility_no_commits(conn, scored_project):
    pid, _, _, _ = scored_project
    vol = compute_volatility(conn, pid, "nonexistent.py", 4)
    assert vol == 0.5  # Neutral


def test_volatility_old_commits_lower(conn, scored_project):
    pid, _, _, _ = scored_project
    vol_main = compute_volatility(conn, pid, "main.py", 4)
    vol_utils = compute_volatility(conn, pid, "utils.py", 4)
    assert vol_main > vol_utils  # main.py has more recent commits


# --- compute_coverage ---

def test_coverage_no_tests(conn, scored_project):
    pid, _, c2, _ = scored_project
    cov = compute_coverage(conn, c2, "function")
    assert cov == 1.0  # No test bindings → highest risk


def test_coverage_with_tests(conn, scored_project):
    pid, c1, _, c3 = scored_project
    # c3 has a 'tests' binding with symbol_name="process" matching c1's name
    cov = compute_coverage(conn, c1, "function")
    assert cov < 1.0  # Has some coverage


def test_coverage_test_case_itself(conn, scored_project):
    pid, _, _, c3 = scored_project
    cov = compute_coverage(conn, c3, "test_case")
    assert cov == 0.0  # test_cases get 0.0


# --- compute_complexity ---

def test_complexity_high():
    meta = json.dumps({
        "cyclomatic_complexity": 20,
        "nesting_depth": 5,
        "parameter_count": 8,
    })
    score = compute_complexity(meta)
    assert 0.0 <= score <= 1.0
    assert score > 0.7  # Should be high


def test_complexity_low():
    meta = json.dumps({
        "cyclomatic_complexity": 1,
        "nesting_depth": 0,
        "parameter_count": 0,
    })
    score = compute_complexity(meta)
    assert 0.0 <= score <= 1.0
    assert score < 0.3  # Should be low


def test_complexity_none():
    assert compute_complexity(None) == 0.5


def test_complexity_center():
    # raw = 0.5*10 + 0.3*3 + 0.2*2 = 6.3 → sigmoid(-0.3*(6.3-10)) = sigmoid(1.11) ≈ 0.24
    meta = json.dumps({
        "cyclomatic_complexity": 10,
        "nesting_depth": 3,
        "parameter_count": 2,
    })
    score = compute_complexity(meta)
    assert 0.0 <= score <= 1.0


# --- compute_coupling ---

def test_coupling_with_deps(conn, scored_project):
    _, c1, c2, _ = scored_project
    coup = compute_coupling(conn, c1)
    assert coup >= 1  # c1 has outbound to c2

    coup2 = compute_coupling(conn, c2)
    assert coup2 >= 1  # c2 has inbound from c1


def test_coupling_no_deps(conn, scored_project):
    _, _, _, c3 = scored_project
    coup = compute_coupling(conn, c3)
    assert coup == 0.0  # test_case with no deps


# --- compute_staleness ---

def test_staleness_with_newer_dep(conn, scored_project):
    pid, c1, c2, _ = scored_project
    # c1 depends on c2. c1's file (main.py) has recent commits,
    # c2's file (utils.py) has an old commit.
    stale = compute_staleness(conn, c1, "main.py", pid)
    assert 0.0 <= stale <= 1.0


def test_staleness_no_deps(conn, scored_project):
    pid, _, _, c3 = scored_project
    stale = compute_staleness(conn, c3, "test_main.py", pid)
    assert stale == 0.5  # No git history for test_main.py → neutral


def test_staleness_no_git(conn):
    init_db(conn)
    pid = create_project(conn, "no-git", "/tmp/no-git")
    cid = create_chunk(
        conn, project_id=pid, file_path="x.py", chunk_type="function",
        name="f", content="def f(): pass", content_hash="h",
        start_line=1, end_line=1,
    )
    stale = compute_staleness(conn, cid, "x.py", pid)
    assert stale == 0.5  # Neutral


# --- compute_composite ---

def test_composite_weighted():
    score = compute_composite(0.8, 1.0, 0.5, 0.3, 0.1, SCORING_WEIGHTS)
    expected = (0.25 * 0.8 + 0.25 * 1.0 + 0.20 * 0.5 + 0.15 * 0.3 + 0.15 * 0.1)
    assert abs(score - expected) < 0.001


def test_composite_clamped():
    score = compute_composite(1.0, 1.0, 1.0, 1.0, 1.0, SCORING_WEIGHTS)
    assert score <= 1.0
    score2 = compute_composite(0.0, 0.0, 0.0, 0.0, 0.0, SCORING_WEIGHTS)
    assert score2 >= 0.0


# --- score_project ---

def test_score_project_end_to_end(conn, scored_project, monkeypatch):
    pid, _, _, _ = scored_project
    monkeypatch.setitem(SCAN_TARGETS, "test-proj", "/tmp/test")
    result = score_project(conn, "test-proj", 1)

    assert result["chunks_scored"] == 3  # c1, c2, c3 (non-module)
    assert result["avg_composite"] >= 0.0
    assert result["avg_composite"] <= 1.0

    dist = result["score_distribution"]
    assert dist["high_risk"] + dist["medium"] + dist["low_risk"] == 3

    # Verify all scores in range
    cur = conn.execute(
        "SELECT composite_score FROM health_scores WHERE cycle_id = 1"
    )
    for (score,) in cur.fetchall():
        assert 0.0 <= score <= 1.0


def test_score_project_unknown(conn):
    with pytest.raises(ValueError):
        score_project(conn, "nonexistent", 1)


# --- _parse_pytest_output ---

def test_parse_pytest_output_full():
    output = "collected 100 items\n\n95 passed, 3 failed, 2 skipped\n"
    passed, failed, skipped, total = _parse_pytest_output(output)
    assert passed == 95
    assert failed == 3
    assert skipped == 2
    assert total == 100


def test_parse_pytest_output_all_passed():
    output = "100 passed\n"
    passed, failed, skipped, total = _parse_pytest_output(output)
    assert passed == 100
    assert total == 100


def test_parse_pytest_output_with_errors():
    output = "50 passed, 2 failed, 1 error\n"
    passed, failed, skipped, total = _parse_pytest_output(output)
    assert passed == 50
    assert failed == 3  # 2 failed + 1 error
    assert total == 53
