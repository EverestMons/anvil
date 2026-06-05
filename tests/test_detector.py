"""
Tests for best practice detection engine and deviation finder.
"""
import json
import sqlite3

import pytest

from src.db import (
    init_db, create_project, create_chunk, create_health_score,
    get_best_practices_by_role,
)
from src.detector import check_best_practice
from src.lab import find_best_practice_deviations


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    init_db(c)
    c.execute("PRAGMA foreign_keys=ON")
    yield c
    c.close()


# --- Detection engine: content regex ---

def test_bare_except_detected():
    chunk = {
        "content": "def handle():\n    try:\n        x()\n    except:\n        pass",
        "structural_metadata": None,
    }
    practice = {"pattern_name": "consistent_error_handling"}
    result = check_best_practice(chunk, practice)
    assert result["compliant"] is False
    assert "Bare except" in result["observation"]


def test_specific_except_compliant():
    chunk = {
        "content": "def handle():\n    try:\n        x()\n    except ValueError:\n        pass",
        "structural_metadata": None,
    }
    practice = {"pattern_name": "consistent_error_handling"}
    result = check_best_practice(chunk, practice)
    assert result["compliant"] is True


def test_raw_form_access_detected():
    chunk = {
        "content": 'name = request.form["name"]',
        "structural_metadata": None,
    }
    practice = {"pattern_name": "input_validation_at_boundary"}
    result = check_best_practice(chunk, practice)
    assert result["compliant"] is False
    assert "request.form[]" in result["observation"]


def test_form_get_compliant():
    chunk = {
        "content": 'name = request.form.get("name", "")',
        "structural_metadata": None,
    }
    practice = {"pattern_name": "input_validation_at_boundary"}
    result = check_best_practice(chunk, practice)
    assert result["compliant"] is True


def test_conn_in_utility_detected():
    chunk = {
        "content": "def helper(conn, data):\n    conn.execute('SELECT 1')",
        "structural_metadata": None,
    }
    practice = {"pattern_name": "pure_functions"}
    result = check_best_practice(chunk, practice)
    assert result["compliant"] is False
    assert "connection" in result["observation"].lower() or "conn" in result["observation"].lower()


def test_pure_utility_compliant():
    chunk = {
        "content": "def parse_date(text):\n    return text.strip()",
        "structural_metadata": None,
    }
    practice = {"pattern_name": "pure_functions"}
    result = check_best_practice(chunk, practice)
    assert result["compliant"] is True


def test_domain_logic_in_utility_detected():
    chunk = {
        "content": "def format_invoice_number(num):\n    return str(num)",
        "structural_metadata": None,
    }
    practice = {"pattern_name": "no_domain_logic"}
    result = check_best_practice(chunk, practice)
    assert result["compliant"] is False
    assert "Domain-specific" in result["observation"]


def test_datetime_in_gate_detected():
    chunk = {
        "content": "def gate_1(conn):\n    cutoff = datetime.now()\n    return cutoff > threshold",
        "structural_metadata": None,
    }
    practice = {"pattern_name": "deterministic_output"}
    result = check_best_practice(chunk, practice)
    assert result["compliant"] is False
    assert "datetime.now()" in result["observation"]


def test_boolean_return_in_gate_detected():
    chunk = {
        "content": "def gate_2(conn, inv):\n    if valid:\n        return True\n    return False",
        "structural_metadata": None,
    }
    practice = {"pattern_name": "structured_return_type"}
    result = check_best_practice(chunk, practice)
    assert result["compliant"] is False
    assert "boolean" in result["observation"].lower()


def test_create_table_without_if_not_exists():
    chunk = {
        "content": "CREATE TABLE users (id INTEGER PRIMARY KEY)",
        "structural_metadata": None,
    }
    practice = {"pattern_name": "idempotent_schema"}
    result = check_best_practice(chunk, practice)
    assert result["compliant"] is False


def test_create_table_with_if_not_exists_compliant():
    chunk = {
        "content": "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)",
        "structural_metadata": None,
    }
    practice = {"pattern_name": "idempotent_schema"}
    result = check_best_practice(chunk, practice)
    assert result["compliant"] is True


# --- Detection engine: structural metadata ---

def test_long_function_detected():
    chunk = {
        "content": "def big():\n" + "    x = 1\n" * 100,
        "structural_metadata": json.dumps({"line_count": 101}),
    }
    practice = {"pattern_name": "single_responsibility"}
    result = check_best_practice(chunk, practice)
    assert result["compliant"] is False
    assert "101" in result["observation"]


def test_short_function_compliant():
    chunk = {
        "content": "def small():\n    return 1",
        "structural_metadata": json.dumps({"line_count": 2}),
    }
    practice = {"pattern_name": "single_responsibility"}
    result = check_best_practice(chunk, practice)
    assert result["compliant"] is True


# --- Unknown practice returns compliant ---

def test_unknown_practice_compliant():
    chunk = {"content": "def x():\n    pass", "structural_metadata": None}
    practice = {"pattern_name": "unknown_future_practice"}
    result = check_best_practice(chunk, practice)
    assert result["compliant"] is True


# --- Deviation finder integration ---

def test_find_deviations(conn):
    pid = create_project(conn, "test-proj", "/tmp/test")

    # Route handler with bare except (violates consistent_error_handling)
    cid = create_chunk(
        conn, project_id=pid, file_path="web/contracts.py",
        chunk_type="function", name="handle_form",
        content="@contracts_bp.route('/form')\ndef handle_form():\n    try:\n        x()\n    except:\n        pass",
        content_hash="h1", start_line=1, end_line=5, last_seen_cycle=1,
    )
    conn.execute(
        "UPDATE code_chunks SET functional_role = 'route_handler' WHERE id = ?",
        (cid,),
    )
    conn.commit()

    deviations = find_best_practice_deviations(conn, pid, 1)
    assert len(deviations) >= 1

    # Should find consistent_error_handling violation
    names = [d["practice_name"] for d in deviations]
    assert "consistent_error_handling" in names

    # Verify finding structure
    dev = next(d for d in deviations if d["practice_name"] == "consistent_error_handling")
    assert dev["file_path"] == "web/contracts.py"
    assert dev["name"] == "handle_form"
    assert dev["functional_role"] == "route_handler"
    assert "Bare except" in dev["observation"]
    assert dev["recommendation"]  # non-empty


def test_no_deviations_for_compliant_chunk(conn):
    pid = create_project(conn, "test-proj2", "/tmp/test2")

    # Clean route handler (no violations)
    cid = create_chunk(
        conn, project_id=pid, file_path="web/index.py",
        chunk_type="function", name="index",
        content="@app.route('/')\ndef index():\n    return 'ok'",
        content_hash="h2", start_line=1, end_line=3, last_seen_cycle=1,
    )
    conn.execute(
        "UPDATE code_chunks SET functional_role = 'route_handler' WHERE id = ?",
        (cid,),
    )
    conn.commit()

    deviations = find_best_practice_deviations(conn, pid, 1)
    # May still have some deviations from structural checks, but not error_handling
    error_devs = [d for d in deviations if d["practice_name"] == "consistent_error_handling"]
    assert len(error_devs) == 0


def test_unclassified_chunks_skipped(conn):
    pid = create_project(conn, "test-proj3", "/tmp/test3")

    # Chunk without functional_role
    create_chunk(
        conn, project_id=pid, file_path="random.py",
        chunk_type="function", name="random_func",
        content="def random_func():\n    try:\n        x()\n    except:\n        pass",
        content_hash="h3", start_line=1, end_line=4, last_seen_cycle=1,
    )

    deviations = find_best_practice_deviations(conn, pid, 1)
    assert len(deviations) == 0
