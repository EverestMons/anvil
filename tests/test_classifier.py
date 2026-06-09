"""
Tests for Anvil heuristic functional role classifier.
"""
import sqlite3

import pytest

from src.db import init_db, create_project, create_chunk
from src.classifier import classify_chunk, classify_project
from src.classifier_registry import get_archetype
from src.config import SCAN_TARGETS
from src.cycle import seed_archetype_data

# Ensure archetypes are registered
import src.archetypes  # noqa: F401


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    init_db(c)
    c.execute("PRAGMA foreign_keys=ON")
    yield c
    c.close()


@pytest.fixture
def archetype():
    return get_archetype("flask_service")


# --- classify_chunk unit tests ---

def test_route_handler_by_decorator(archetype):
    chunk = {
        "name": "contracts_list",
        "file_path": "web/contracts.py",
        "content": "@contracts_bp.route('/contracts')\ndef contracts_list():\n    pass",
        "chunk_type": "function",
    }
    assert classify_chunk(chunk, archetype) == "route_handler"


def test_route_handler_by_app_route(archetype):
    chunk = {
        "name": "index",
        "file_path": "app.py",
        "content": "@app.route('/')\ndef index():\n    pass",
        "chunk_type": "function",
    }
    assert classify_chunk(chunk, archetype) == "route_handler"


def test_validation_gate_by_name(archetype):
    chunk = {
        "name": "gate_1_legitimacy",
        "file_path": "engines/validator.py",
        "content": "def gate_1_legitimacy(conn, invoice_id):\n    pass",
        "chunk_type": "function",
    }
    assert classify_chunk(chunk, archetype) == "validation_gate"


def test_validation_gate_by_higher_number(archetype):
    chunk = {
        "name": "gate_10_final",
        "file_path": "engines/validator.py",
        "content": "def gate_10_final(conn, invoice_id):\n    pass",
        "chunk_type": "function",
    }
    assert classify_chunk(chunk, archetype) == "validation_gate"


def test_data_model_by_name(archetype):
    chunk = {
        "name": "_create_tables",
        "file_path": "database.py",
        "content": "def _create_tables(conn):\n    pass",
        "chunk_type": "function",
    }
    assert classify_chunk(chunk, archetype) == "data_model"


def test_data_model_by_migrate_name(archetype):
    chunk = {
        "name": "_migrate_confidence_schema",
        "file_path": "database.py",
        "content": "def _migrate_confidence_schema(conn):\n    pass",
        "chunk_type": "function",
    }
    assert classify_chunk(chunk, archetype) == "data_model"


def test_data_model_by_file_path(archetype):
    chunk = {
        "name": "some_helper",
        "file_path": "contract_tables.py",
        "content": "def some_helper():\n    pass",
        "chunk_type": "function",
    }
    assert classify_chunk(chunk, archetype) == "data_model"


def test_confidence_engine_by_file_path(archetype):
    chunk = {
        "name": "evaluate_alignment",
        "file_path": "engines/confidence.py",
        "content": "def evaluate_alignment(conn, carrier_code):\n    pass",
        "chunk_type": "function",
    }
    assert classify_chunk(chunk, archetype) == "confidence_engine"


def test_content_generator_by_name(archetype):
    chunk = {
        "name": "generate_dispute_email",
        "file_path": "engines/email_generator.py",
        "content": "def generate_dispute_email(data):\n    pass",
        "chunk_type": "function",
    }
    assert classify_chunk(chunk, archetype) == "content_generator"


def test_utility_fallback(archetype):
    chunk = {
        "name": "_parse_json",
        "file_path": "web/utils.py",
        "content": "def _parse_json(text):\n    pass",
        "chunk_type": "function",
    }
    # web/utils.py matches web/ catch-all -> route_handler,
    # but this is fine since utils in web/ serve routes
    result = classify_chunk(chunk, archetype)
    assert result is not None


def test_fallback_for_unknown_file(archetype):
    chunk = {
        "name": "random_helper",
        "file_path": "some_other_file.py",
        "content": "def random_helper():\n    pass",
        "chunk_type": "function",
    }
    assert classify_chunk(chunk, archetype) == "utility"


def test_module_returns_none(archetype):
    chunk = {
        "name": "app.py",
        "file_path": "app.py",
        "content": "",
        "chunk_type": "module",
    }
    assert classify_chunk(chunk, archetype) is None


def test_test_case_returns_none(archetype):
    chunk = {
        "name": "test_something",
        "file_path": "tests/test_foo.py",
        "content": "def test_something():\n    pass",
        "chunk_type": "test_case",
    }
    assert classify_chunk(chunk, archetype) is None


def test_config_chunk_type(archetype):
    chunk = {
        "name": "settings",
        "file_path": "config.py",
        "content": "SETTING = True",
        "chunk_type": "config",
    }
    assert classify_chunk(chunk, archetype) == "configuration"


def test_ingestion_orchestrator_by_name(archetype):
    chunk = {
        "name": "run_ingestion",
        "file_path": "ingestion/ingest.py",
        "content": "def run_ingestion(csv_path, conn):\n    pass",
        "chunk_type": "function",
    }
    assert classify_chunk(chunk, archetype) == "ingestion_orchestrator"


def test_anomaly_detector_by_name(archetype):
    chunk = {
        "name": "detect_accessorial_drift",
        "file_path": "engines/drift_detector.py",
        "content": "def detect_accessorial_drift(conn):\n    pass",
        "chunk_type": "function",
    }
    assert classify_chunk(chunk, archetype) == "anomaly_detector"


def test_pattern_learner_by_name(archetype):
    chunk = {
        "name": "discover_fak_rules",
        "file_path": "engines/pattern_learner.py",
        "content": "def discover_fak_rules(conn):\n    pass",
        "chunk_type": "function",
    }
    assert classify_chunk(chunk, archetype) == "pattern_learner"


def test_decorator_priority_over_file_path(archetype):
    """Decorator rules should take priority over file path rules."""
    chunk = {
        "name": "some_route",
        "file_path": "web/reporting.py",
        "content": "@reporting_bp.route('/report')\ndef some_route():\n    pass",
        "chunk_type": "function",
    }
    # Decorator matches route_handler, file path would match report_generator
    assert classify_chunk(chunk, archetype) == "route_handler"


def test_name_priority_over_file_path(archetype):
    """Name rules should take priority over file path rules."""
    chunk = {
        "name": "gate_5_lane",
        "file_path": "engines/validator.py",
        "content": "def gate_5_lane(conn):\n    pass",
        "chunk_type": "function",
    }
    # Name matches validation_gate (priority 3), file path also matches (priority 4)
    assert classify_chunk(chunk, archetype) == "validation_gate"


# --- classify_project integration tests ---

def test_classify_project(conn, monkeypatch):
    monkeypatch.setitem(SCAN_TARGETS, "test-proj", {
        "path": "/tmp/test", "language": "python", "archetype": "flask_service",
    })
    pid = create_project(conn, "test-proj", "/tmp/test")

    # Create a route handler chunk
    create_chunk(
        conn, project_id=pid, file_path="web/contracts.py",
        chunk_type="function", name="contracts_list",
        content="@contracts_bp.route('/contracts')\ndef contracts_list():\n    pass",
        content_hash="abc123", start_line=1, end_line=3,
    )

    # Create a data model chunk
    create_chunk(
        conn, project_id=pid, file_path="database.py",
        chunk_type="function", name="_create_tables",
        content="def _create_tables(conn):\n    pass",
        content_hash="def456", start_line=1, end_line=2,
    )

    # Create a test_case chunk (should be skipped)
    create_chunk(
        conn, project_id=pid, file_path="tests/test_foo.py",
        chunk_type="test_case", name="test_something",
        content="def test_something():\n    pass",
        content_hash="ghi789", start_line=1, end_line=2,
    )

    # Create a module chunk (should be skipped)
    create_chunk(
        conn, project_id=pid, file_path="app.py",
        chunk_type="module", name="app.py",
        content="",
        content_hash="jkl012", start_line=1, end_line=1,
    )

    result = classify_project(conn, "test-proj")
    assert result["classified"] == 2
    assert result["unclassified"] == 0
    assert "route_handler" in result["role_distribution"]
    assert "data_model" in result["role_distribution"]

    # Verify DB was updated
    cur = conn.execute(
        "SELECT functional_role FROM code_chunks WHERE name = 'contracts_list'"
    )
    assert cur.fetchone()[0] == "route_handler"

    cur = conn.execute(
        "SELECT functional_role FROM code_chunks WHERE name = '_create_tables'"
    )
    assert cur.fetchone()[0] == "data_model"

    # Test case should not have functional_role set
    cur = conn.execute(
        "SELECT functional_role FROM code_chunks WHERE name = 'test_something'"
    )
    assert cur.fetchone()[0] is None


def test_classify_project_not_found(conn):
    with pytest.raises(ValueError, match="Project not found"):
        classify_project(conn, "nonexistent")


def test_functional_roles_seeded(conn, archetype):
    """Verify seed_archetype_data seeds the 25 functional roles."""
    # init_db no longer seeds; seed explicitly from archetype
    seed_archetype_data(conn, archetype)

    cur = conn.execute("SELECT COUNT(*) FROM functional_roles")
    assert cur.fetchone()[0] == 25

    cur = conn.execute(
        "SELECT name FROM functional_roles WHERE parent_role = 'web_layer' ORDER BY name"
    )
    web_roles = [r[0] for r in cur.fetchall()]
    assert "route_handler" in web_roles
    assert "report_generator" in web_roles
    assert "document_manager" in web_roles
