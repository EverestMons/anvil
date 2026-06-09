"""
Tests for the archetype registry and flask_service archetype integration.

Verifies: registry returns flask_service, classify_chunk honors archetype,
init_db seeds nothing, cycle seeding is idempotent.
"""
import sqlite3

import pytest

from src.classifier_registry import get_archetype, register_archetype, ARCHETYPES, ArchetypeDefinition
from src.db import init_db
from src.classifier import classify_chunk
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


# --- Registry ---

def test_flask_service_registered():
    """get_archetype returns a valid flask_service archetype."""
    arch = get_archetype("flask_service")
    assert arch.name == "flask_service"
    assert len(arch.roles) > 0
    assert len(arch.decorator_rules) > 0
    assert len(arch.best_practices) > 0


def test_unknown_archetype_raises():
    with pytest.raises(ValueError, match="Unknown archetype"):
        get_archetype("nonexistent_archetype")


# --- classify_chunk honors archetype ---

def test_classify_chunk_uses_archetype_rules():
    """classify_chunk applies the archetype's rules, not hardcoded globals."""
    arch = get_archetype("flask_service")
    chunk = {
        "content": "@app.route('/test')\ndef test_handler():\n    pass",
        "name": "test_handler",
        "file_path": "web/views.py",
    }
    role = classify_chunk(chunk, arch)
    assert role == "route_handler"


def test_classify_chunk_falls_back_to_utility():
    """Chunk matching no specific rules falls back to utility."""
    arch = get_archetype("flask_service")
    chunk = {
        "content": "def something():\n    pass",
        "name": "something",
        "file_path": "misc.py",
    }
    role = classify_chunk(chunk, arch)
    assert role == "utility"


# --- init_db seeds nothing ---

def test_init_db_seeds_no_roles(conn):
    """After init_db, functional_roles table is empty (no hardcoded seeds)."""
    cur = conn.execute("SELECT COUNT(*) FROM functional_roles")
    assert cur.fetchone()[0] == 0


def test_init_db_seeds_no_best_practices(conn):
    """After init_db, best_practices table is empty (no hardcoded seeds)."""
    cur = conn.execute("SELECT COUNT(*) FROM best_practices")
    assert cur.fetchone()[0] == 0


# --- Cycle seeding is idempotent ---

def test_seed_archetype_data_populates(conn):
    """seed_archetype_data inserts roles and best practices."""
    arch = get_archetype("flask_service")
    seed_archetype_data(conn, arch)

    cur = conn.execute("SELECT COUNT(*) FROM functional_roles")
    assert cur.fetchone()[0] == len(arch.roles)

    cur = conn.execute("SELECT COUNT(*) FROM best_practices")
    assert cur.fetchone()[0] == len(arch.best_practices)


def test_seed_archetype_data_idempotent(conn):
    """Running seed_archetype_data twice produces the same row counts."""
    arch = get_archetype("flask_service")
    seed_archetype_data(conn, arch)
    seed_archetype_data(conn, arch)

    cur = conn.execute("SELECT COUNT(*) FROM functional_roles")
    assert cur.fetchone()[0] == len(arch.roles)

    cur = conn.execute("SELECT COUNT(*) FROM best_practices")
    assert cur.fetchone()[0] == len(arch.best_practices)
