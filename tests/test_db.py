"""
Tests for Anvil database layer — schema creation, CRUD, constraints, indexes.
"""
import sqlite3

import pytest

from src.db import (
    init_db,
    create_project,
    get_project,
    create_chunk,
    get_chunks_by_project,
    get_chunks_by_file,
    create_fingerprint,
    create_symbol_binding,
    get_bindings_by_chunk,
    create_dependency,
    get_dependencies,
    create_similarity,
    create_git_change,
    create_test_result,
    create_health_score,
    create_cycle_report,
    get_cycle_report,
    create_provenance,
)


@pytest.fixture
def conn():
    """Create an in-memory database with schema initialized."""
    c = sqlite3.connect(":memory:")
    init_db(c)
    # Re-enable foreign keys after executescript (executescript issues implicit COMMIT
    # which can reset PRAGMA foreign_keys in some SQLite versions)
    c.execute("PRAGMA foreign_keys=ON")
    yield c
    c.close()


@pytest.fixture
def project_id(conn):
    """Create a test project and return its ID."""
    return create_project(conn, "test-project", "/tmp/test-project")


@pytest.fixture
def chunk_id(conn, project_id):
    """Create a test chunk and return its ID."""
    return create_chunk(
        conn,
        project_id=project_id,
        file_path="src/main.py",
        chunk_type="function",
        name="do_stuff",
        content="def do_stuff():\n    pass",
        content_hash="abc123",
        start_line=1,
        end_line=2,
    )


# --- Schema creation ---

EXPECTED_TABLES = [
    "best_practices",
    "chunk_dependencies",
    "chunk_fingerprints",
    "chunk_provenance",
    "chunk_similarities",
    "chunk_symbol_bindings",
    "code_chunks",
    "cycle_reports",
    "functional_roles",
    "git_changes",
    "health_scores",
    "projects",
    "test_results",
]


def test_init_db_creates_all_tables(conn):
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in cur.fetchall()
              if not row[0].startswith("sqlite_")]
    assert tables == EXPECTED_TABLES


def test_wal_mode_enabled(conn):
    cur = conn.execute("PRAGMA journal_mode")
    mode = cur.fetchone()[0]
    # In-memory DBs may report 'memory' instead of 'wal'
    assert mode in ("wal", "memory")


def test_foreign_keys_enabled(conn):
    cur = conn.execute("PRAGMA foreign_keys")
    assert cur.fetchone()[0] == 1


# --- Index existence ---

EXPECTED_INDEXES = {
    "code_chunks": [
        "idx_code_chunks_chunk_type",
        "idx_code_chunks_content_hash",
        "idx_code_chunks_parent",
        "idx_code_chunks_project_file",
    ],
    "chunk_fingerprints": [
        "idx_chunk_fingerprints_chunk",
        "idx_chunk_fingerprints_cycle",
    ],
    "chunk_symbol_bindings": [
        "idx_symbol_bindings_chunk",
        "idx_symbol_bindings_symbol",
        "idx_symbol_bindings_target",
        "idx_symbol_bindings_type",
    ],
    "chunk_dependencies": [
        "idx_chunk_deps_source",
        "idx_chunk_deps_target",
    ],
    "chunk_similarities": [
        "idx_chunk_similarities_a",
        "idx_chunk_similarities_b",
        "idx_chunk_similarities_cycle",
    ],
    "git_changes": [
        "idx_git_changes_commit_hash",
        "idx_git_changes_project_file",
    ],
    "test_results": [
        "idx_test_results_project",
    ],
    "health_scores": [
        "idx_health_scores_chunk_cycle",
    ],
    "cycle_reports": [
        "idx_cycle_reports_project",
        "idx_cycle_reports_project_cycle",
    ],
    "chunk_provenance": [
        "idx_chunk_provenance_chunk",
        "idx_chunk_provenance_plan",
    ],
    "best_practices": [
        "idx_best_practices_role",
        "idx_best_practices_role_pattern",
    ],
}


def test_indexes_exist(conn):
    for table, expected in EXPECTED_INDEXES.items():
        cur = conn.execute(f"PRAGMA index_list({table})")
        actual = sorted(row[1] for row in cur.fetchall()
                        if not row[1].startswith("sqlite_autoindex"))
        assert actual == sorted(expected), f"Index mismatch for {table}: {actual}"


# --- CRUD: projects ---

def test_create_and_get_project(conn):
    pid = create_project(conn, "my-project", "/tmp/my-project")
    assert pid is not None
    proj = get_project(conn, "my-project")
    assert proj["name"] == "my-project"
    assert proj["path"] == "/tmp/my-project"
    assert proj["id"] == pid


def test_get_project_not_found(conn):
    assert get_project(conn, "nonexistent") is None


def test_project_name_unique(conn):
    create_project(conn, "dup", "/tmp/dup")
    with pytest.raises(sqlite3.IntegrityError):
        create_project(conn, "dup", "/tmp/dup2")


# --- CRUD: code_chunks ---

def test_create_and_get_chunk(conn, project_id):
    cid = create_chunk(
        conn,
        project_id=project_id,
        file_path="src/main.py",
        chunk_type="function",
        name="hello",
        content="def hello(): pass",
        content_hash="hash1",
        start_line=1,
        end_line=1,
    )
    chunks = get_chunks_by_project(conn, project_id)
    assert len(chunks) == 1
    assert chunks[0]["name"] == "hello"
    assert chunks[0]["id"] == cid


def test_get_chunks_by_file(conn, project_id):
    create_chunk(conn, project_id=project_id, file_path="a.py",
                 chunk_type="function", name="f1", content="x",
                 content_hash="h1", start_line=1, end_line=1)
    create_chunk(conn, project_id=project_id, file_path="b.py",
                 chunk_type="class", name="C1", content="y",
                 content_hash="h2", start_line=1, end_line=5)
    assert len(get_chunks_by_file(conn, project_id, "a.py")) == 1
    assert len(get_chunks_by_file(conn, project_id, "b.py")) == 1


def test_chunk_parent_self_ref(conn, project_id):
    parent = create_chunk(conn, project_id=project_id, file_path="m.py",
                          chunk_type="class", name="MyClass", content="class MyClass: pass",
                          content_hash="p1", start_line=1, end_line=10)
    child = create_chunk(conn, project_id=project_id, file_path="m.py",
                         chunk_type="method", name="my_method",
                         content="def my_method(self): pass",
                         content_hash="c1", start_line=2, end_line=3,
                         parent_chunk_id=parent)
    chunks = get_chunks_by_file(conn, project_id, "m.py")
    child_row = [c for c in chunks if c["name"] == "my_method"][0]
    assert child_row["parent_chunk_id"] == parent


# --- Foreign key enforcement ---

def test_chunk_fk_requires_valid_project(conn):
    with pytest.raises(sqlite3.IntegrityError):
        create_chunk(conn, project_id=9999, file_path="x.py",
                     chunk_type="function", name="bad", content="x",
                     content_hash="h", start_line=1, end_line=1)


def test_fingerprint_fk_requires_valid_chunk(conn):
    with pytest.raises(sqlite3.IntegrityError):
        create_fingerprint(conn, chunk_id=9999, content_hash="h",
                           minhash_sig=None, shingle_count=0, cycle_id=1)


def test_binding_fk_requires_valid_chunk(conn):
    with pytest.raises(sqlite3.IntegrityError):
        create_symbol_binding(conn, chunk_id=9999, symbol_name="foo",
                              binding_type="defines")


def test_dependency_fk_requires_valid_chunks(conn, chunk_id):
    with pytest.raises(sqlite3.IntegrityError):
        create_dependency(conn, source_id=chunk_id, target_id=9999,
                          dep_type="import", scope="cross_file")


def test_similarity_fk_requires_valid_chunks(conn, chunk_id):
    with pytest.raises(sqlite3.IntegrityError):
        create_similarity(conn, chunk_a_id=chunk_id, chunk_b_id=9999,
                          score=0.9, cycle_id=1)


def test_git_change_fk_requires_valid_project(conn):
    with pytest.raises(sqlite3.IntegrityError):
        create_git_change(conn, project_id=9999, file_path="x.py",
                          commit_hash="abc", commit_date="2026-03-29",
                          commit_message="test", author="dev")


def test_test_result_fk_requires_valid_project(conn):
    with pytest.raises(sqlite3.IntegrityError):
        create_test_result(conn, project_id=9999, run_date="2026-03-29",
                           total_tests=10, passed=10, failed=0, skipped=0)


def test_health_score_fk_requires_valid_chunk(conn):
    with pytest.raises(sqlite3.IntegrityError):
        create_health_score(conn, chunk_id=9999, cycle_id=1)


def test_cycle_report_fk_requires_valid_project(conn):
    with pytest.raises(sqlite3.IntegrityError):
        create_cycle_report(conn, project_id=9999, cycle_number=1,
                            started_at="2026-03-29T10:00:00")


# --- CHECK constraint enforcement ---

def test_chunk_type_check_constraint(conn, project_id):
    with pytest.raises(sqlite3.IntegrityError):
        create_chunk(conn, project_id=project_id, file_path="x.py",
                     chunk_type="invalid", name="bad", content="x",
                     content_hash="h", start_line=1, end_line=1)


def test_binding_type_check_constraint(conn, chunk_id):
    with pytest.raises(sqlite3.IntegrityError):
        create_symbol_binding(conn, chunk_id=chunk_id, symbol_name="foo",
                              binding_type="invalid")


def test_dependency_type_check_constraint(conn, chunk_id):
    with pytest.raises(sqlite3.IntegrityError):
        create_dependency(conn, source_id=chunk_id, target_id=chunk_id,
                          dep_type="invalid", scope="within_file")


def test_dependency_scope_check_constraint(conn, chunk_id):
    with pytest.raises(sqlite3.IntegrityError):
        create_dependency(conn, source_id=chunk_id, target_id=chunk_id,
                          dep_type="import", scope="invalid")


# --- CRUD: chunk_fingerprints ---

def test_create_fingerprint(conn, chunk_id):
    fid = create_fingerprint(conn, chunk_id=chunk_id, content_hash="hash1",
                             minhash_sig=b"\x00\x01\x02", shingle_count=10,
                             cycle_id=1)
    assert fid is not None


# --- CRUD: chunk_symbol_bindings ---

def test_create_and_get_bindings(conn, chunk_id):
    create_symbol_binding(conn, chunk_id, "my_func", "defines")
    create_symbol_binding(conn, chunk_id, "os", "imports")
    bindings = get_bindings_by_chunk(conn, chunk_id)
    assert len(bindings) == 2
    types = {b["binding_type"] for b in bindings}
    assert types == {"defines", "imports"}


def test_binding_with_target(conn, project_id):
    c1 = create_chunk(conn, project_id=project_id, file_path="a.py",
                      chunk_type="function", name="caller", content="x",
                      content_hash="h1", start_line=1, end_line=1)
    c2 = create_chunk(conn, project_id=project_id, file_path="a.py",
                      chunk_type="function", name="callee", content="y",
                      content_hash="h2", start_line=5, end_line=5)
    bid = create_symbol_binding(conn, c1, "callee", "calls", target_chunk_id=c2)
    bindings = get_bindings_by_chunk(conn, c1)
    assert bindings[0]["target_chunk_id"] == c2


# --- CRUD: chunk_dependencies ---

def test_create_and_get_dependencies(conn, project_id):
    c1 = create_chunk(conn, project_id=project_id, file_path="a.py",
                      chunk_type="function", name="f1", content="x",
                      content_hash="h1", start_line=1, end_line=1)
    c2 = create_chunk(conn, project_id=project_id, file_path="b.py",
                      chunk_type="function", name="f2", content="y",
                      content_hash="h2", start_line=1, end_line=1)
    create_dependency(conn, c1, c2, "import", "cross_file")
    outbound = get_dependencies(conn, c1, direction="outbound")
    assert len(outbound) == 1
    assert outbound[0]["target_chunk_id"] == c2
    inbound = get_dependencies(conn, c2, direction="inbound")
    assert len(inbound) == 1
    assert inbound[0]["source_chunk_id"] == c1


# --- CRUD: chunk_similarities ---

def test_create_similarity(conn, project_id):
    c1 = create_chunk(conn, project_id=project_id, file_path="a.py",
                      chunk_type="function", name="f1", content="x",
                      content_hash="h1", start_line=1, end_line=1)
    c2 = create_chunk(conn, project_id=project_id, file_path="b.py",
                      chunk_type="function", name="f2", content="y",
                      content_hash="h2", start_line=1, end_line=1)
    sid = create_similarity(conn, c1, c2, 0.85, cycle_id=1)
    assert sid is not None


# --- CRUD: git_changes ---

def test_create_git_change(conn, project_id):
    gid = create_git_change(conn, project_id, "src/main.py", "abc123",
                            "2026-03-29", "fix bug", "dev")
    assert gid is not None


# --- CRUD: test_results ---

def test_create_test_result(conn, project_id):
    tid = create_test_result(conn, project_id, run_date="2026-03-29",
                             total_tests=100, passed=95, failed=3, skipped=2,
                             failed_test_names='["test_a", "test_b", "test_c"]')
    assert tid is not None


# --- CRUD: health_scores ---

def test_create_health_score(conn, chunk_id):
    hid = create_health_score(conn, chunk_id, cycle_id=1,
                              volatility_score=0.8, coverage_score=0.5,
                              complexity_score=0.3, coupling_score=0.4,
                              staleness_score=0.1, composite_score=0.6)
    assert hid is not None


# --- CRUD: cycle_reports ---

def test_create_and_get_cycle_report(conn, project_id):
    cid = create_cycle_report(conn, project_id, cycle_number=1,
                              started_at="2026-03-29T10:00:00",
                              files_scanned=50, chunks_extracted=200)
    report = get_cycle_report(conn, 1)
    assert report is not None
    assert report["cycle_number"] == 1
    assert report["files_scanned"] == 50


def test_cycle_report_unique_per_project(conn, project_id):
    create_cycle_report(conn, project_id, cycle_number=1,
                        started_at="2026-03-29T10:00:00")
    with pytest.raises(sqlite3.IntegrityError):
        create_cycle_report(conn, project_id, cycle_number=1,
                            started_at="2026-03-29T11:00:00")


def test_get_cycle_report_not_found(conn):
    assert get_cycle_report(conn, 999) is None


# --- last_seen_cycle migration and usage ---

def test_last_seen_cycle_column_exists(conn):
    """Migration adds last_seen_cycle column to code_chunks."""
    cur = conn.execute("PRAGMA table_info(code_chunks)")
    columns = {row[1] for row in cur.fetchall()}
    assert "last_seen_cycle" in columns


def test_last_seen_cycle_migration_idempotent(conn):
    """Calling init_db twice does not error on last_seen_cycle column."""
    init_db(conn)  # second call
    cur = conn.execute("PRAGMA table_info(code_chunks)")
    columns = [row[1] for row in cur.fetchall()]
    assert columns.count("last_seen_cycle") == 1


def test_create_chunk_with_last_seen_cycle(conn, project_id):
    """create_chunk accepts last_seen_cycle kwarg."""
    cid = create_chunk(
        conn, project_id=project_id, file_path="a.py", chunk_type="function",
        name="foo", content="def foo(): pass", content_hash="h1",
        start_line=1, end_line=1, last_seen_cycle=5,
    )
    cur = conn.execute(
        "SELECT last_seen_cycle FROM code_chunks WHERE id = ?", (cid,),
    )
    assert cur.fetchone()[0] == 5


def test_create_chunk_without_last_seen_cycle_defaults_null(conn, project_id):
    """Chunks created without last_seen_cycle have NULL."""
    cid = create_chunk(
        conn, project_id=project_id, file_path="a.py", chunk_type="function",
        name="bar", content="def bar(): pass", content_hash="h2",
        start_line=1, end_line=1,
    )
    cur = conn.execute(
        "SELECT last_seen_cycle FROM code_chunks WHERE id = ?", (cid,),
    )
    assert cur.fetchone()[0] is None


# --- Cascade on DELETE ---

def test_cascade_delete_removes_all_dependent_rows(conn, project_id):
    """Deleting a code_chunk cascades to all dependent tables and SET NULLs references."""
    # Create two chunks so we can test cross-references
    c1 = create_chunk(
        conn, project_id=project_id, file_path="x.py", chunk_type="function",
        name="target", content="def target(): pass", content_hash="t1",
        start_line=1, end_line=2,
    )
    c2 = create_chunk(
        conn, project_id=project_id, file_path="y.py", chunk_type="function",
        name="caller", content="def caller(): pass", content_hash="t2",
        start_line=1, end_line=2,
    )

    # Create dependent rows pointing to c1
    create_fingerprint(conn, c1, "fp_hash", None, None, 1)
    create_symbol_binding(conn, c1, "target", "defines")
    create_symbol_binding(conn, c2, "target", "calls", target_chunk_id=c1)
    create_dependency(conn, c2, c1, "call", "cross_file")
    create_similarity(conn, c1, c2, 0.80, cycle_id=1)
    create_health_score(conn, c1, cycle_id=1, composite_score=0.5)
    create_provenance(conn, c1, "test-plan", dev_log_path="log.md")

    # Verify rows exist before delete
    assert conn.execute("SELECT COUNT(*) FROM chunk_fingerprints WHERE chunk_id = ?", (c1,)).fetchone()[0] > 0
    assert conn.execute("SELECT COUNT(*) FROM chunk_symbol_bindings WHERE chunk_id = ?", (c1,)).fetchone()[0] > 0
    assert conn.execute("SELECT COUNT(*) FROM chunk_dependencies WHERE target_chunk_id = ?", (c1,)).fetchone()[0] > 0
    assert conn.execute("SELECT COUNT(*) FROM chunk_similarities WHERE chunk_a_id = ?", (c1,)).fetchone()[0] > 0
    assert conn.execute("SELECT COUNT(*) FROM health_scores WHERE chunk_id = ?", (c1,)).fetchone()[0] > 0
    assert conn.execute("SELECT COUNT(*) FROM chunk_provenance WHERE chunk_id = ?", (c1,)).fetchone()[0] > 0

    # DELETE chunk c1
    conn.execute("DELETE FROM code_chunks WHERE id = ?", (c1,))
    conn.commit()

    # Cascade: all dependent rows gone
    assert conn.execute("SELECT COUNT(*) FROM chunk_fingerprints WHERE chunk_id = ?", (c1,)).fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM chunk_symbol_bindings WHERE chunk_id = ?", (c1,)).fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM chunk_dependencies WHERE target_chunk_id = ?", (c1,)).fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM chunk_similarities WHERE chunk_a_id = ?", (c1,)).fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM health_scores WHERE chunk_id = ?", (c1,)).fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM chunk_provenance WHERE chunk_id = ?", (c1,)).fetchone()[0] == 0

    # SET NULL: c2's binding that targeted c1 should now be NULL
    cur = conn.execute(
        "SELECT target_chunk_id FROM chunk_symbol_bindings WHERE chunk_id = ? AND symbol_name = 'target'",
        (c2,),
    )
    row = cur.fetchone()
    assert row is not None
    assert row[0] is None, "target_chunk_id should be SET NULL after cascade"

    # No FK violations
    violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    assert violations == []
