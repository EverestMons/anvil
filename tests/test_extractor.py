"""
Tests for Anvil extractor — orchestrator, dependency resolution, fingerprinting.
"""
import json
import os
import sqlite3
import textwrap

import pytest

from src.db import (
    init_db, create_project, create_chunk, create_fingerprint,
    create_symbol_binding, get_bindings_by_chunk, get_dependencies,
)
from src.extractor import (
    extract_project,
    store_symbols,
    resolve_dependencies,
    compute_fingerprints,
    store_structural_metadata,
)
from src.config import SCAN_TARGETS


@pytest.fixture
def conn():
    """In-memory database with schema initialized."""
    c = sqlite3.connect(":memory:")
    init_db(c)
    c.execute("PRAGMA foreign_keys=ON")
    yield c
    c.close()


@pytest.fixture
def mock_project(tmp_path, conn, monkeypatch):
    """Create a mock project with Python files and register it."""
    # Create source files
    (tmp_path / "main.py").write_text(textwrap.dedent("""\
        import os
        from utils import helper

        def main():
            \"\"\"Entry point.\"\"\"
            result = helper(1, 2)
            print(result)

        class App:
            def run(self):
                for i in range(10):
                    if i > 5:
                        print(i)
    """))

    (tmp_path / "utils.py").write_text(textwrap.dedent("""\
        def helper(a, b):
            \"\"\"Add two numbers.\"\"\"
            return a + b

        def unused():
            pass
    """))

    (tmp_path / "test_utils.py").write_text(textwrap.dedent("""\
        from utils import helper

        def test_helper_add():
            assert helper(1, 2) == 3

        def test_helper_zero():
            assert helper(0, 0) == 0
    """))

    # Register in SCAN_TARGETS
    monkeypatch.setitem(SCAN_TARGETS, "mock-project", str(tmp_path))

    # Create project and module chunks (simulating scanner output)
    pid = create_project(conn, "mock-project", str(tmp_path))

    for fname in ["main.py", "utils.py", "test_utils.py"]:
        fpath = tmp_path / fname
        with open(str(fpath), "r") as f:
            content = f.read()
        import hashlib
        h = hashlib.sha256(content.encode("utf-8")).hexdigest()
        cid = create_chunk(
            conn, project_id=pid, file_path=fname, chunk_type="module",
            name=fname, content=content, content_hash=h,
            start_line=1, end_line=content.count("\n") + 1,
        )
        create_fingerprint(conn, cid, h, None, None, 0)

    return pid, tmp_path


# --- extract_project ---

def test_extract_project_creates_chunks(conn, mock_project):
    pid, _ = mock_project
    result = extract_project(conn, "mock-project", 1)
    assert result["files_processed"] == 3
    assert result["chunks_created"] > 0


def test_extract_project_chunk_types(conn, mock_project):
    pid, _ = mock_project
    extract_project(conn, "mock-project", 1)

    cur = conn.execute(
        "SELECT chunk_type, COUNT(*) FROM code_chunks "
        "WHERE project_id = ? GROUP BY chunk_type", (pid,)
    )
    type_counts = dict(cur.fetchall())
    assert "function" in type_counts
    assert "class" in type_counts
    assert "method" in type_counts
    assert "module" in type_counts
    assert "test_case" in type_counts


def test_extract_project_parent_linkage(conn, mock_project):
    pid, _ = mock_project
    extract_project(conn, "mock-project", 1)

    # Methods should have class as parent
    cur = conn.execute(
        "SELECT c.name, c.chunk_type, p.name as parent_name, p.chunk_type as parent_type "
        "FROM code_chunks c "
        "JOIN code_chunks p ON c.parent_chunk_id = p.id "
        "WHERE c.project_id = ? AND c.chunk_type = 'method'",
        (pid,),
    )
    methods = cur.fetchall()
    assert len(methods) > 0
    for name, ctype, parent_name, parent_type in methods:
        assert parent_type == "class"

    # Top-level functions should have module as parent
    cur = conn.execute(
        "SELECT c.name, p.chunk_type as parent_type "
        "FROM code_chunks c "
        "JOIN code_chunks p ON c.parent_chunk_id = p.id "
        "WHERE c.project_id = ? AND c.chunk_type = 'function'",
        (pid,),
    )
    functions = cur.fetchall()
    for name, parent_type in functions:
        assert parent_type == "module"


def test_extract_project_unknown_project(conn):
    with pytest.raises(ValueError):
        extract_project(conn, "nonexistent", 1)


def test_extract_project_summary_keys(conn, mock_project):
    result = extract_project(conn, "mock-project", 1)
    expected_keys = {
        "files_processed", "chunks_created", "chunks_updated",
        "symbols_extracted", "dependencies_resolved",
        "fingerprints_created", "similarities_found",
    }
    assert set(result.keys()) == expected_keys


# --- store_symbols ---

def test_store_symbols(conn):
    init_db(conn)
    pid = create_project(conn, "sym-test", "/tmp/sym")
    cid = create_chunk(
        conn, project_id=pid, file_path="x.py", chunk_type="function",
        name="f", content="def f(): pass", content_hash="h1",
        start_line=1, end_line=1,
    )
    symbols = {
        "imports": [{"module": "os", "names": [], "is_from": False, "line": 1}],
        "definitions": [{"name": "f", "type": "function", "line": 1}],
        "calls": [{"caller": "f", "callee": "print", "line": 2}],
        "test_mappings": [],
    }
    count = store_symbols(conn, cid, symbols)
    assert count == 3

    bindings = get_bindings_by_chunk(conn, cid)
    types = {b["binding_type"] for b in bindings}
    assert "imports" in types
    assert "defines" in types
    assert "calls" in types


# --- resolve_dependencies ---

def test_resolve_import_dependency(conn):
    init_db(conn)
    pid = create_project(conn, "dep-test", "/tmp/dep")

    # Module A imports from Module B
    c_a = create_chunk(
        conn, project_id=pid, file_path="a.py", chunk_type="function",
        name="func_a", content="def func_a(): pass", content_hash="ha",
        start_line=1, end_line=1,
    )
    c_b = create_chunk(
        conn, project_id=pid, file_path="b.py", chunk_type="function",
        name="func_b", content="def func_b(): pass", content_hash="hb",
        start_line=1, end_line=1,
    )

    # A imports func_b
    create_symbol_binding(conn, c_a, "func_b", "imports")
    # B defines func_b
    create_symbol_binding(conn, c_b, "func_b", "defines")

    count = resolve_dependencies(conn, pid)
    assert count >= 1

    deps = get_dependencies(conn, c_a, direction="outbound")
    assert len(deps) >= 1
    assert deps[0]["target_chunk_id"] == c_b
    assert deps[0]["dependency_type"] == "import"
    assert deps[0]["scope"] == "cross_file"


def test_resolve_within_file_dependency(conn):
    init_db(conn)
    pid = create_project(conn, "dep-test2", "/tmp/dep2")

    c_a = create_chunk(
        conn, project_id=pid, file_path="mod.py", chunk_type="function",
        name="caller", content="def caller(): callee()", content_hash="h1",
        start_line=1, end_line=1,
    )
    c_b = create_chunk(
        conn, project_id=pid, file_path="mod.py", chunk_type="function",
        name="callee", content="def callee(): pass", content_hash="h2",
        start_line=3, end_line=3,
    )

    create_symbol_binding(conn, c_a, "callee", "calls")

    count = resolve_dependencies(conn, pid)
    assert count >= 1

    deps = get_dependencies(conn, c_a, direction="outbound")
    call_deps = [d for d in deps if d["dependency_type"] == "call"]
    assert len(call_deps) >= 1
    assert call_deps[0]["scope"] == "within_file"


# --- compute_fingerprints ---

def test_compute_fingerprints_creates_entries(conn):
    init_db(conn)
    pid = create_project(conn, "fp-test", "/tmp/fp")
    cid = create_chunk(
        conn, project_id=pid, file_path="x.py", chunk_type="function",
        name="big_func", content="def big_func():\n    x = 1\n    y = 2\n    z = 3\n    w = 4\n    return x+y+z+w\n",
        content_hash="hbig", start_line=1, end_line=6,
    )

    fp_count, sim_count = compute_fingerprints(conn, pid, 1)
    assert fp_count == 1

    cur = conn.execute(
        "SELECT COUNT(*) FROM chunk_fingerprints WHERE chunk_id = ?", (cid,)
    )
    assert cur.fetchone()[0] == 1


def test_compute_fingerprints_similarity_detection(conn):
    init_db(conn)
    pid = create_project(conn, "sim-test", "/tmp/sim")

    # Two chunks with identical content
    content = "def func():\n    x = 1\n    y = 2\n    z = 3\n    w = 4\n    return x + y + z + w\n"
    import hashlib
    h = hashlib.sha256(content.encode("utf-8")).hexdigest()

    c1 = create_chunk(
        conn, project_id=pid, file_path="a.py", chunk_type="function",
        name="func_a", content=content, content_hash=h,
        start_line=1, end_line=6,
    )
    c2 = create_chunk(
        conn, project_id=pid, file_path="b.py", chunk_type="function",
        name="func_b", content=content, content_hash=h + "x",
        start_line=1, end_line=6,
    )

    fp_count, sim_count = compute_fingerprints(conn, pid, 1)
    assert fp_count == 2
    # Identical content should produce similarity
    assert sim_count >= 1


# --- store_structural_metadata ---

def test_store_structural_metadata(conn):
    init_db(conn)
    pid = create_project(conn, "meta-test", "/tmp/meta")
    cid = create_chunk(
        conn, project_id=pid, file_path="x.py", chunk_type="function",
        name="f", content="def f(): pass", content_hash="hm",
        start_line=1, end_line=1,
    )

    meta = {
        "cyclomatic_complexity": 3,
        "nesting_depth": 2,
        "parameter_count": 1,
        "import_count": 0,
        "has_docstring": False,
        "line_count": 5,
    }
    store_structural_metadata(conn, cid, meta)

    cur = conn.execute(
        "SELECT structural_metadata FROM code_chunks WHERE id = ?", (cid,)
    )
    row = cur.fetchone()
    assert row[0] is not None
    stored = json.loads(row[0])
    assert stored["cyclomatic_complexity"] == 3
    assert stored["nesting_depth"] == 2


# --- idempotency ---

def test_extract_project_idempotent(conn, mock_project):
    pid, _ = mock_project
    r1 = extract_project(conn, "mock-project", 1)
    assert r1["chunks_created"] > 0

    r2 = extract_project(conn, "mock-project", 2)
    assert r2["chunks_created"] == 0  # All exist with same hash
    assert r2["chunks_updated"] == 0
