"""
Tests for Anvil cycle runner — pipeline orchestration, summaries, comparison.
"""
import hashlib
import json
import os
import sqlite3
import subprocess
import textwrap

import pytest

from src.db import (
    init_db, create_project, create_chunk, create_fingerprint,
    create_health_score, create_cycle_report,
)
from src.cycle import run_cycle, get_cycle_summary, compare_cycles
from src.config import SCAN_TARGETS


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    init_db(c)
    c.execute("PRAGMA foreign_keys=ON")
    yield c
    c.close()


@pytest.fixture
def cycle_project(tmp_path, conn, monkeypatch):
    """Create a mock project with git repo for full cycle testing."""
    # Init git repo
    subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.email", "test@test.com"],
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.name", "Test"],
        capture_output=True,
    )

    # Create Python files
    (tmp_path / "main.py").write_text(textwrap.dedent("""\
        from utils import helper

        def process(data):
            \"\"\"Process data.\"\"\"
            result = helper(data, 10)
            if result > 0:
                return result
            return 0
    """))

    (tmp_path / "utils.py").write_text(textwrap.dedent("""\
        def helper(a, b):
            return a + b

        def unused():
            pass
    """))

    (tmp_path / "test_main.py").write_text(textwrap.dedent("""\
        from main import process

        def test_process_positive():
            assert process(5) == 15

        def test_process_zero():
            assert process(0) == 0
    """))

    # Git commit
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], capture_output=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "commit", "-m", "init"],
        capture_output=True,
    )

    monkeypatch.setitem(SCAN_TARGETS, "cycle-test", {
        "path": str(tmp_path), "language": "python", "archetype": "flask_service",
    })
    return tmp_path


# --- run_cycle ---

def test_run_cycle_end_to_end(conn, cycle_project, monkeypatch):
    # Patch ANVIL_ROOT so report writes to tmp
    monkeypatch.setattr("src.lab.ANVIL_ROOT", str(cycle_project))
    monkeypatch.setattr("src.lab.ANVIL_RUNTIME_ROOT", str(cycle_project))
    os.makedirs(str(cycle_project / "knowledge" / "research"), exist_ok=True)

    result = run_cycle(conn, "cycle-test")

    assert result["cycle_id"] == 1
    assert "scan" in result
    assert "extract" in result
    assert "score" in result
    assert "lab" in result
    assert "elapsed_seconds" in result
    assert "error" not in result.get("scan", {})
    assert result["scan"]["files_total"] == 3


def test_run_cycle_scanner_failure(conn, monkeypatch):
    # Unknown project should fail at scan
    monkeypatch.setitem(SCAN_TARGETS, "bad-proj", {
        "path": "/nonexistent/path", "language": "python", "archetype": "flask_service",
    })
    result = run_cycle(conn, "bad-proj")
    assert result.get("aborted_at") == "scan"


# --- get_cycle_summary ---

def test_get_cycle_summary(conn):
    pid = create_project(conn, "sum-test", "/tmp/sum")
    c1 = create_chunk(
        conn, project_id=pid, file_path="x.py", chunk_type="function",
        name="f", content="def f(): pass", content_hash="h1",
        start_line=1, end_line=1,
    )
    create_health_score(conn, c1, cycle_id=1, composite_score=0.5)
    create_cycle_report(conn, pid, cycle_number=1, started_at="2026-03-30T10:00:00",
                        completed_at="2026-03-30T10:01:00", files_scanned=10,
                        chunks_extracted=50, chunks_scored=50, findings_count=5)

    summary = get_cycle_summary(conn, "sum-test", 1)
    assert summary["cycle_number"] == 1
    assert summary["files_scanned"] == 10
    assert summary["chunks_scored"] == 1
    assert summary["findings_count"] == 5
    assert "health_scores" in summary
    assert "top_5_riskiest" in summary


def test_get_cycle_summary_not_found(conn):
    create_project(conn, "empty", "/tmp/empty")
    summary = get_cycle_summary(conn, "empty", 99)
    assert "error" in summary


# --- compare_cycles ---

def test_compare_cycles(conn):
    pid = create_project(conn, "cmp-test", "/tmp/cmp")

    # Create chunks and scores for cycle 1
    c1 = create_chunk(
        conn, project_id=pid, file_path="a.py", chunk_type="function",
        name="stable", content="def stable(): pass", content_hash="h1",
        start_line=1, end_line=1,
    )
    c2 = create_chunk(
        conn, project_id=pid, file_path="b.py", chunk_type="function",
        name="improving", content="def improving(): pass", content_hash="h2",
        start_line=1, end_line=1,
    )
    c3 = create_chunk(
        conn, project_id=pid, file_path="c.py", chunk_type="function",
        name="old_func", content="def old_func(): pass", content_hash="h3",
        start_line=1, end_line=1,
    )

    # Cycle 1 scores
    create_health_score(conn, c1, cycle_id=1, composite_score=0.5)
    create_health_score(conn, c2, cycle_id=1, composite_score=0.8)
    create_health_score(conn, c3, cycle_id=1, composite_score=0.6)
    create_cycle_report(conn, pid, cycle_number=1, started_at="2026-03-29",
                        findings_count=10)

    # Cycle 2: c1 unchanged, c2 improved, c3 removed, c4 new
    c4 = create_chunk(
        conn, project_id=pid, file_path="d.py", chunk_type="function",
        name="new_func", content="def new_func(): pass", content_hash="h4",
        start_line=1, end_line=1,
    )
    create_health_score(conn, c1, cycle_id=2, composite_score=0.5)
    create_health_score(conn, c2, cycle_id=2, composite_score=0.3)  # Improved
    create_health_score(conn, c4, cycle_id=2, composite_score=0.2)
    create_cycle_report(conn, pid, cycle_number=2, started_at="2026-03-30",
                        findings_count=7)

    result = compare_cycles(conn, "cmp-test", 1, 2)

    assert result["chunks_in_a"] == 3
    assert result["chunks_in_b"] == 3
    assert result["new_chunks"] == 1  # c4
    assert result["removed_chunks"] == 1  # c3
    assert result["score_changes"]["improved"] == 1  # c2: 0.8 → 0.3
    assert result["score_changes"]["unchanged"] == 1  # c1: 0.5 → 0.5
    assert result["findings_delta"] == -3  # 7 - 10


def test_compare_cycles_unknown_project(conn):
    with pytest.raises(ValueError):
        compare_cycles(conn, "nonexistent", 1, 2)
