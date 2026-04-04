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
    _store_file_symbols,
    _find_production_chunk,
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


# --- function-level test bindings ---

def test_test_case_gets_function_level_tests_binding(conn, mock_project):
    """test_case calling a production function gets a 'tests' binding with target_chunk_id."""
    pid, _ = mock_project
    extract_project(conn, "mock-project", 1)

    # test_helper_add calls helper() from utils.py
    cur = conn.execute(
        "SELECT id FROM code_chunks WHERE project_id = ? "
        "AND name = 'test_helper_add' AND chunk_type = 'test_case'",
        (pid,),
    )
    test_chunk_id = cur.fetchone()[0]

    # helper is in utils.py (production)
    cur = conn.execute(
        "SELECT id FROM code_chunks WHERE project_id = ? "
        "AND name = 'helper' AND chunk_type = 'function' "
        "AND file_path = 'utils.py'",
        (pid,),
    )
    prod_chunk_id = cur.fetchone()[0]

    # Should have a "tests" binding with target_chunk_id pointing to helper
    cur = conn.execute(
        "SELECT target_chunk_id, symbol_name FROM chunk_symbol_bindings "
        "WHERE chunk_id = ? AND binding_type = 'tests' AND target_chunk_id = ?",
        (test_chunk_id, prod_chunk_id),
    )
    row = cur.fetchone()
    assert row is not None, "Expected function-level 'tests' binding with target_chunk_id"
    assert row[0] == prod_chunk_id
    assert row[1] == "helper"


def test_test_helper_does_not_get_tests_binding(conn):
    """A helper function (chunk_type='function') in a test file should NOT get 'tests' bindings."""
    init_db(conn)
    pid = create_project(conn, "helper-test", "/tmp/ht")

    # Production chunk
    prod_id = create_chunk(
        conn, project_id=pid, file_path="utils.py", chunk_type="function",
        name="do_work", content="def do_work(): pass", content_hash="hp1",
        start_line=1, end_line=1,
    )

    # Test helper (chunk_type='function', not 'test_case')
    helper_id = create_chunk(
        conn, project_id=pid, file_path="tests/test_utils.py", chunk_type="function",
        name="_setup_data", content="def _setup_data(): do_work()", content_hash="hh1",
        start_line=1, end_line=1,
    )

    # Module chunk for the test file
    mod_id = create_chunk(
        conn, project_id=pid, file_path="tests/test_utils.py", chunk_type="module",
        name="tests/test_utils.py", content="", content_hash="hm1",
        start_line=1, end_line=1,
    )

    # Simulate symbols: helper calls do_work
    symbols = {
        "imports": [],
        "definitions": [{"name": "_setup_data", "type": "function", "line": 1}],
        "calls": [{"caller": "_setup_data", "callee": "do_work", "line": 1}],
        "test_mappings": [],
    }
    module_chunk = {"id": mod_id, "file_path": "tests/test_utils.py"}
    _store_file_symbols(conn, pid, module_chunk, symbols)

    # Should NOT have a "tests" binding (caller is function, not test_case)
    cur = conn.execute(
        "SELECT COUNT(*) FROM chunk_symbol_bindings "
        "WHERE chunk_id = ? AND binding_type = 'tests'",
        (helper_id,),
    )
    assert cur.fetchone()[0] == 0


def test_framework_calls_no_spurious_tests_binding(conn):
    """Calls to framework methods (execute, commit) that don't resolve to production chunks
    should not create 'tests' bindings."""
    init_db(conn)
    pid = create_project(conn, "fw-test", "/tmp/fw")

    # Test case chunk that calls framework methods
    tc_id = create_chunk(
        conn, project_id=pid, file_path="tests/test_db.py", chunk_type="test_case",
        name="test_insert", content="def test_insert(): db.execute('SELECT 1')",
        content_hash="htc1", start_line=1, end_line=1,
    )
    mod_id = create_chunk(
        conn, project_id=pid, file_path="tests/test_db.py", chunk_type="module",
        name="tests/test_db.py", content="", content_hash="hmod1",
        start_line=1, end_line=1,
    )

    symbols = {
        "imports": [],
        "definitions": [{"name": "test_insert", "type": "function", "line": 1}],
        "calls": [
            {"caller": "test_insert", "callee": "execute", "line": 1},
            {"caller": "test_insert", "callee": "commit", "line": 1},
        ],
        "test_mappings": [],
    }
    module_chunk = {"id": mod_id, "file_path": "tests/test_db.py"}
    _store_file_symbols(conn, pid, module_chunk, symbols)

    # No production chunks named "execute" or "commit" exist, so no "tests" bindings
    cur = conn.execute(
        "SELECT COUNT(*) FROM chunk_symbol_bindings "
        "WHERE chunk_id = ? AND binding_type = 'tests' AND target_chunk_id IS NOT NULL",
        (tc_id,),
    )
    assert cur.fetchone()[0] == 0


def test_module_level_tests_bindings_still_created(conn, mock_project):
    """Existing module-level 'tests' bindings (filename convention) still work."""
    pid, _ = mock_project
    extract_project(conn, "mock-project", 1)

    # test_utils.py should still produce module-level "tests" bindings
    # with symbol_name = "utils" (from filename convention)
    cur = conn.execute(
        "SELECT COUNT(*) FROM chunk_symbol_bindings csb "
        "JOIN code_chunks cc ON csb.chunk_id = cc.id "
        "WHERE cc.project_id = ? AND csb.binding_type = 'tests' "
        "AND csb.symbol_name = 'utils' AND csb.target_chunk_id IS NULL",
        (pid,),
    )
    count = cur.fetchone()[0]
    assert count >= 1, "Module-level 'tests' bindings should still be created"
