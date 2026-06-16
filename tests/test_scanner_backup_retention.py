"""
Tests for backup retention (_prune_old_backups) in src/scanner.py.
"""
import os
import time

import pytest

from src.scanner import _prune_old_backups


def _create_dummy_backups(directory, count):
    """Create count dummy backup files with distinct timestamps in name and mtime."""
    paths = []
    for i in range(count):
        name = f"anvil-backup-20260601-{100000 + i}.db"
        p = os.path.join(directory, name)
        with open(p, "w") as f:
            f.write(f"backup-{i}")
        # Ensure distinct mtime ordering matches filename ordering
        os.utime(p, (1_000_000 + i, 1_000_000 + i))
        paths.append(p)
    return paths


def test_prune_keeps_newest_n(tmp_path):
    """With N+2 backups and keep=3, only the 3 newest survive."""
    backup_dir = str(tmp_path)
    created = _create_dummy_backups(backup_dir, 5)

    deleted = _prune_old_backups(backup_dir, 3)

    assert len(deleted) == 2
    # The two oldest (lowest timestamps) should be deleted
    assert deleted == created[:2]
    remaining = sorted(
        f for f in os.listdir(backup_dir) if f.startswith("anvil-backup-")
    )
    assert len(remaining) == 3
    # The 3 newest files should still exist
    for p in created[2:]:
        assert os.path.exists(p)


def test_prune_empty_dir(tmp_path):
    """Empty directory returns empty list, no error."""
    deleted = _prune_old_backups(str(tmp_path), 3)
    assert deleted == []


def test_prune_missing_dir():
    """Non-existent directory returns empty list, no error."""
    deleted = _prune_old_backups("/nonexistent/path/backup", 3)
    assert deleted == []


def test_prune_fewer_than_keep(tmp_path):
    """Fewer backups than keep threshold: nothing deleted."""
    _create_dummy_backups(str(tmp_path), 2)
    deleted = _prune_old_backups(str(tmp_path), 3)
    assert deleted == []
    assert len(os.listdir(tmp_path)) == 2


def test_prune_exact_keep(tmp_path):
    """Exactly N backups with keep=N: nothing deleted."""
    _create_dummy_backups(str(tmp_path), 3)
    deleted = _prune_old_backups(str(tmp_path), 3)
    assert deleted == []
    assert len(os.listdir(tmp_path)) == 3


def test_prune_ignores_non_backup_files(tmp_path):
    """Non-matching files are not touched."""
    _create_dummy_backups(str(tmp_path), 5)
    other = os.path.join(str(tmp_path), "other-file.db")
    with open(other, "w") as f:
        f.write("not a backup")

    deleted = _prune_old_backups(str(tmp_path), 3)

    assert len(deleted) == 2
    assert os.path.exists(other)
