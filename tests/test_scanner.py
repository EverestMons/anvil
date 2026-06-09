"""
Tests for Anvil scanner — file discovery, change detection, git history, integration.
"""
import hashlib
import os
import sqlite3
import subprocess
import tempfile

import pytest

from src.db import init_db, create_project, create_chunk, create_fingerprint
from src.scanner import (
    scan_project,
    discover_files,
    compute_file_hash,
    detect_changes,
    ingest_git_history,
    register_file_chunks,
    prune_deleted_file_orphans,
)
from src.config import EXCLUDED_DIRS, EXCLUDED_EXTENSIONS


@pytest.fixture
def conn():
    """In-memory database with schema initialized."""
    c = sqlite3.connect(":memory:")
    init_db(c)
    c.execute("PRAGMA foreign_keys=ON")
    yield c
    c.close()


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory with some Python files."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("def hello():\n    print('hi')\n")
    (tmp_path / "src" / "utils.py").write_text("def add(a, b):\n    return a + b\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_main.py").write_text("def test_hello():\n    pass\n")
    (tmp_path / "README.md").write_text("# My Project\n")
    # Hidden file — should be excluded
    (tmp_path / ".env").write_text("SECRET=abc")
    # __pycache__ — should be excluded
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "main.cpython-39.pyc").write_bytes(b"\x00")
    return tmp_path


@pytest.fixture
def git_project(tmp_path):
    """Create a temporary project with a git repo and some commits."""
    subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.email", "test@test.com"],
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.name", "Test User"],
        capture_output=True,
    )
    # First commit
    (tmp_path / "main.py").write_text("def hello(): pass\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], capture_output=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "commit", "-m", "init: first commit"],
        capture_output=True,
    )
    # Second commit
    (tmp_path / "utils.py").write_text("def add(a, b): return a + b\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], capture_output=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "commit", "-m", "feat: add utils"],
        capture_output=True,
    )
    return tmp_path


# --- discover_files ---

def test_discover_files_finds_source_files(temp_project):
    files = discover_files(str(temp_project), EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)
    rel_paths = [f["relative_path"] for f in files]
    assert "src/main.py" in rel_paths
    assert "src/utils.py" in rel_paths
    assert "tests/test_main.py" in rel_paths
    assert "README.md" in rel_paths


def test_discover_files_excludes_pycache(temp_project):
    files = discover_files(str(temp_project), EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)
    rel_paths = [f["relative_path"] for f in files]
    for p in rel_paths:
        assert "__pycache__" not in p


def test_discover_files_excludes_hidden(temp_project):
    files = discover_files(str(temp_project), EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)
    rel_paths = [f["relative_path"] for f in files]
    assert ".env" not in rel_paths


def test_discover_files_sorted(temp_project):
    files = discover_files(str(temp_project), EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)
    rel_paths = [f["relative_path"] for f in files]
    assert rel_paths == sorted(rel_paths)


def test_discover_files_dict_keys(temp_project):
    files = discover_files(str(temp_project), EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)
    for f in files:
        assert "file_path" in f
        assert "relative_path" in f
        assert "extension" in f
        assert "size_bytes" in f
        assert isinstance(f["size_bytes"], int)


def test_discover_files_empty_dir(tmp_path):
    files = discover_files(str(tmp_path), EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)
    assert files == []


# --- compute_file_hash ---

def test_compute_file_hash_correct(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")
    expected = hashlib.sha256(b"hello world").hexdigest()
    assert compute_file_hash(str(test_file)) == expected


def test_compute_file_hash_nonexistent():
    assert compute_file_hash("/nonexistent/path/file.txt") is None


def test_compute_file_hash_binary(tmp_path):
    test_file = tmp_path / "test.bin"
    test_file.write_bytes(b"\x00\x01\x02\x03")
    expected = hashlib.sha256(b"\x00\x01\x02\x03").hexdigest()
    assert compute_file_hash(str(test_file)) == expected


# --- detect_changes ---

def test_detect_changes_all_new(conn, temp_project):
    pid = create_project(conn, "test", str(temp_project))
    discovered = discover_files(str(temp_project), EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)
    new, changed, unchanged = detect_changes(conn, pid, discovered)
    assert len(new) == len(discovered)
    assert len(changed) == 0
    assert len(unchanged) == 0


def test_detect_changes_unchanged(conn, temp_project):
    pid = create_project(conn, "test", str(temp_project))
    discovered = discover_files(str(temp_project), EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)

    # Register all files first
    for f in discovered:
        f["content_hash"] = compute_file_hash(f["file_path"])
        with open(f["file_path"], "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read()
        cid = create_chunk(
            conn, project_id=pid, file_path=f["relative_path"],
            chunk_type="module", name=f["relative_path"], content=content,
            content_hash=f["content_hash"], start_line=1, end_line=1,
        )
        create_fingerprint(conn, cid, f["content_hash"], None, None, 0)

    # Re-discover and detect — all should be unchanged
    discovered2 = discover_files(str(temp_project), EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)
    new, changed, unchanged = detect_changes(conn, pid, discovered2)
    assert len(new) == 0
    assert len(changed) == 0
    assert len(unchanged) == len(discovered2)


def test_detect_changes_detects_change(conn, temp_project):
    pid = create_project(conn, "test", str(temp_project))
    main_py = temp_project / "src" / "main.py"

    # Register the original
    original_hash = compute_file_hash(str(main_py))
    with open(str(main_py), "r") as fh:
        content = fh.read()
    cid = create_chunk(
        conn, project_id=pid, file_path="src/main.py",
        chunk_type="module", name="src/main.py", content=content,
        content_hash=original_hash, start_line=1, end_line=2,
    )
    create_fingerprint(conn, cid, original_hash, None, None, 0)

    # Modify the file
    main_py.write_text("def hello():\n    print('changed')\n")

    # Detect changes — only main.py should show as changed (others are new)
    discovered = discover_files(str(temp_project), EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)
    new, changed, unchanged = detect_changes(conn, pid, discovered)
    changed_paths = [f["relative_path"] for f in changed]
    assert "src/main.py" in changed_paths


# --- ingest_git_history ---

def test_ingest_git_history(conn, git_project):
    pid = create_project(conn, "test", str(git_project))
    count = ingest_git_history(conn, pid, str(git_project), 4)
    assert count == 2  # two commits

    cur = conn.execute("SELECT COUNT(*) FROM git_changes WHERE project_id = ?", (pid,))
    assert cur.fetchone()[0] > 0


def test_ingest_git_history_idempotent(conn, git_project):
    pid = create_project(conn, "test", str(git_project))
    count1 = ingest_git_history(conn, pid, str(git_project), 4)
    count2 = ingest_git_history(conn, pid, str(git_project), 4)
    assert count1 == 2
    assert count2 == 0  # all skipped

    # No duplicates
    cur = conn.execute(
        "SELECT commit_hash, file_path, COUNT(*) FROM git_changes "
        "WHERE project_id = ? GROUP BY commit_hash, file_path HAVING COUNT(*) > 1",
        (pid,),
    )
    assert cur.fetchall() == []


def test_ingest_git_history_no_git(conn, tmp_path):
    pid = create_project(conn, "test", str(tmp_path))
    count = ingest_git_history(conn, pid, str(tmp_path), 4)
    assert count == 0


# --- register_file_chunks ---

def test_register_new_files(conn, temp_project):
    pid = create_project(conn, "test", str(temp_project))
    discovered = discover_files(str(temp_project), EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)
    for f in discovered:
        f["content_hash"] = compute_file_hash(f["file_path"])

    count = register_file_chunks(conn, pid, discovered, [], cycle_id=None)
    assert count == len(discovered)

    # Check module chunks exist
    cur = conn.execute(
        "SELECT COUNT(*) FROM code_chunks WHERE project_id = ? AND chunk_type = 'module'",
        (pid,),
    )
    assert cur.fetchone()[0] == len(discovered)

    # Check fingerprints exist
    cur = conn.execute(
        "SELECT COUNT(*) FROM chunk_fingerprints cf "
        "JOIN code_chunks cc ON cf.chunk_id = cc.id "
        "WHERE cc.project_id = ?",
        (pid,),
    )
    assert cur.fetchone()[0] == len(discovered)


def test_register_changed_files(conn, temp_project):
    pid = create_project(conn, "test", str(temp_project))

    # Create an existing module chunk for main.py
    with open(str(temp_project / "src" / "main.py"), "r") as fh:
        content = fh.read()
    original_hash = compute_file_hash(str(temp_project / "src" / "main.py"))
    cid = create_chunk(
        conn, project_id=pid, file_path="src/main.py",
        chunk_type="module", name="src/main.py", content=content,
        content_hash=original_hash, start_line=1, end_line=2,
    )
    create_fingerprint(conn, cid, original_hash, None, None, 0)

    # Simulate change
    changed_file = {
        "file_path": str(temp_project / "src" / "main.py"),
        "relative_path": "src/main.py",
        "extension": ".py",
        "size_bytes": 100,
        "content_hash": "newhash123",
    }
    count = register_file_chunks(conn, pid, [], [changed_file], cycle_id=None)
    assert count == 1

    # Should have 2 fingerprints now
    cur = conn.execute(
        "SELECT COUNT(*) FROM chunk_fingerprints WHERE chunk_id = ?", (cid,)
    )
    assert cur.fetchone()[0] == 2


# --- scan_project (integration) ---

def test_scan_project_unknown_project(conn):
    with pytest.raises(ValueError, match="Unknown project"):
        scan_project(conn, "nonexistent-project")


def test_scan_project_summary_keys(conn, temp_project, monkeypatch):
    monkeypatch.setitem(
        __import__("src.config", fromlist=["SCAN_TARGETS"]).SCAN_TARGETS,
        "test-proj",
        {"path": str(temp_project), "language": "python", "archetype": "flask_service"},
    )
    summary = scan_project(conn, "test-proj")
    assert set(summary.keys()) == {
        "project_name", "files_total", "files_new",
        "files_changed", "files_unchanged", "git_commits_ingested",
    }
    assert summary["project_name"] == "test-proj"
    assert summary["files_total"] > 0
    assert summary["files_new"] == summary["files_total"]  # first scan
    assert summary["files_changed"] == 0
    assert summary["files_unchanged"] == 0


def test_scan_project_idempotent(conn, temp_project, monkeypatch):
    monkeypatch.setitem(
        __import__("src.config", fromlist=["SCAN_TARGETS"]).SCAN_TARGETS,
        "test-proj",
        {"path": str(temp_project), "language": "python", "archetype": "flask_service"},
    )
    s1 = scan_project(conn, "test-proj")
    s2 = scan_project(conn, "test-proj")
    assert s2["files_new"] == 0
    assert s2["files_unchanged"] == s1["files_total"]
    assert s2["files_changed"] == 0


def test_scan_project_updates_last_scanned(conn, temp_project, monkeypatch):
    monkeypatch.setitem(
        __import__("src.config", fromlist=["SCAN_TARGETS"]).SCAN_TARGETS,
        "test-proj",
        {"path": str(temp_project), "language": "python", "archetype": "flask_service"},
    )
    scan_project(conn, "test-proj")
    cur = conn.execute("SELECT last_scanned FROM projects WHERE name = 'test-proj'")
    assert cur.fetchone()[0] is not None


# --- prune_deleted_file_orphans ---

def test_prune_removes_orphan_chunks(conn, temp_project):
    """Orphan file_path chunks are deleted; live chunks are untouched."""
    pid = create_project(conn, "prune-test", str(temp_project))

    # Live module — file exists on disk
    live = create_chunk(
        conn, project_id=pid, file_path="src/main.py", chunk_type="module",
        name="src/main.py", content="# live", content_hash="lh",
        start_line=1, end_line=1,
    )

    # Orphan module — file does NOT exist on disk
    orphan_mod = create_chunk(
        conn, project_id=pid, file_path="deleted/gone.py", chunk_type="module",
        name="deleted/gone.py", content="# orphan", content_hash="oh",
        start_line=1, end_line=1,
    )

    # Orphan child function in the same deleted file
    orphan_child = create_chunk(
        conn, project_id=pid, file_path="deleted/gone.py", chunk_type="function",
        name="old_func", content="def old_func(): pass", content_hash="och",
        start_line=1, end_line=2,
    )

    on_disk = {f["relative_path"] for f in
               discover_files(str(temp_project), EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)}

    result = prune_deleted_file_orphans(conn, pid, on_disk)

    assert result["pruned_files"] == 1
    assert result["pruned_chunks"] == 2
    assert result["pruned_modules"] == 1
    assert result["pruned_children"] == 1

    # Live chunk still exists
    cur = conn.execute("SELECT id FROM code_chunks WHERE id = ?", (live,))
    assert cur.fetchone() is not None

    # Orphan chunks are gone
    cur = conn.execute("SELECT id FROM code_chunks WHERE id IN (?, ?)",
                       (orphan_mod, orphan_child))
    assert cur.fetchall() == []


def test_prune_creates_backup(conn, temp_project, tmp_path, monkeypatch):
    """Backup file is created before prune when orphans exist."""
    pid = create_project(conn, "backup-test", str(temp_project))

    # Create a fake anvil.db so shutil.copy2 works
    fake_db = tmp_path / "anvil.db"
    fake_db.write_text("fake db")
    monkeypatch.setattr("src.scanner.ANVIL_DB_PATH", str(fake_db))
    monkeypatch.setattr("src.scanner.ANVIL_ROOT", str(tmp_path))

    create_chunk(
        conn, project_id=pid, file_path="deleted/gone.py", chunk_type="module",
        name="deleted/gone.py", content="# orphan", content_hash="oh",
        start_line=1, end_line=1,
    )

    on_disk = {f["relative_path"] for f in
               discover_files(str(temp_project), EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)}

    prune_deleted_file_orphans(conn, pid, on_disk)

    backup_dir = tmp_path / "backups"
    backups = list(backup_dir.glob("anvil-backup-*.db"))
    assert len(backups) == 1


def test_prune_idempotent(conn, temp_project):
    """Second prune call with no orphans is a clean no-op."""
    pid = create_project(conn, "idem-test", str(temp_project))

    create_chunk(
        conn, project_id=pid, file_path="deleted/gone.py", chunk_type="module",
        name="deleted/gone.py", content="# orphan", content_hash="oh",
        start_line=1, end_line=1,
    )

    on_disk = {f["relative_path"] for f in
               discover_files(str(temp_project), EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)}

    r1 = prune_deleted_file_orphans(conn, pid, on_disk)
    assert r1["pruned_chunks"] == 1

    r2 = prune_deleted_file_orphans(conn, pid, on_disk)
    assert r2["pruned_files"] == 0
    assert r2["pruned_chunks"] == 0


def test_prune_no_orphans_no_backup(conn, temp_project, tmp_path, monkeypatch):
    """No backup is created when there are no orphans."""
    pid = create_project(conn, "noop-test", str(temp_project))

    monkeypatch.setattr("src.scanner.ANVIL_ROOT", str(tmp_path))

    on_disk = {f["relative_path"] for f in
               discover_files(str(temp_project), EXCLUDED_DIRS, EXCLUDED_EXTENSIONS)}

    result = prune_deleted_file_orphans(conn, pid, on_disk)
    assert result["pruned_files"] == 0

    backup_dir = tmp_path / "backups"
    assert not backup_dir.exists() or list(backup_dir.glob("*.db")) == []
