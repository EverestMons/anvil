"""
Tests for Anvil dev log parser and provenance ingestion.
"""
import os
import sqlite3
import tempfile

import pytest

from src.db import init_db, create_project, create_chunk
from src.provenance import (
    parse_dev_logs,
    ingest_provenance,
    _extract_file_paths,
    _extract_plan_slug,
    _extract_plan_description,
)


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    init_db(c)
    c.execute("PRAGMA foreign_keys=ON")
    yield c
    c.close()


@pytest.fixture
def dev_log_dir():
    """Create a temp directory with sample dev logs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Dev log with bullet format
        bullet_log = """# Action Router Engine
**Date:** 2026-03-14
**Agent:** Invoice Developer

## Output Receipt
**Status:** Complete

### Files Created or Modified (Code)
- engines/action_router.py -- Created, ~470 lines
- engines/circuit_breaker.py -- Created, ~274 lines
- app.py -- Modified, +8 lines

### Decisions Made
- Used strategy pattern for action routing
"""
        with open(os.path.join(tmpdir, "action-router-engine-2026-03-14.md"), "w") as f:
            f.write(bullet_log)

        # Dev log with table format
        table_log = """# Carrier Identity Detection
**Date:** 2026-03-16

## Files Created/Modified

| File | Action | Lines |
|---|---|---|
| engines/carrier_identity.py | Created | ~200 |
| contract_tables.py | Modified | +30 |

## Output Receipt
**Status:** Complete
"""
        with open(os.path.join(tmpdir, "carrier-identity-2026-03-16.md"), "w") as f:
            f.write(table_log)

        # Dev log with no file section (diagnostic)
        diag_log = """# Carrier Aging Diagnostic
**Date:** 2026-03-23

## Investigation
No code changes needed.
"""
        with open(os.path.join(tmpdir, "carrier-aging-diagnostic-2026-03-23.md"), "w") as f:
            f.write(diag_log)

        # Dev log with em-dash format
        emdash_log = """# Autofill Features
**Date:** 2026-03-20

### Files Created or Modified (Code)
- web/contracts.py \u2014 added carrier-names datalist
- web/templates/contracts_list.html \u2014 added datalist element
"""
        with open(os.path.join(tmpdir, "autofill-features-2026-03-20.md"), "w") as f:
            f.write(emdash_log)

        yield tmpdir


# --- _extract_plan_slug ---

def test_extract_plan_slug():
    assert _extract_plan_slug("action-router-engine-2026-03-14.md") == "action-router-engine-2026-03-14"
    assert _extract_plan_slug("foo.md") == "foo"


# --- _extract_plan_description ---

def test_extract_plan_description():
    content = "# Action Router Engine\n**Date:** 2026-03-14\n"
    assert _extract_plan_description(content) == "Action Router Engine"


def test_extract_plan_description_missing():
    content = "No heading here\n"
    assert _extract_plan_description(content) == ""


# --- _extract_file_paths ---

def test_extract_bullet_format():
    content = """## Output Receipt

### Files Created or Modified (Code)
- engines/action_router.py -- Created, ~470 lines
- app.py -- Modified, +8 lines

### Decisions Made
- Something
"""
    paths = _extract_file_paths(content)
    assert len(paths) == 2
    assert paths[0]["path"] == "engines/action_router.py"
    assert "470" in paths[0]["description"]
    assert paths[1]["path"] == "app.py"


def test_extract_table_format():
    content = """## Files Created/Modified

| File | Action | Lines |
|---|---|---|
| engines/carrier_identity.py | Created | ~200 |
| contract_tables.py | Modified | +30 |

## Next Section
"""
    paths = _extract_file_paths(content)
    assert len(paths) == 2
    assert paths[0]["path"] == "engines/carrier_identity.py"
    assert paths[1]["path"] == "contract_tables.py"


def test_extract_no_section():
    content = """# Just a Title

Some text with no file section.
"""
    paths = _extract_file_paths(content)
    assert paths == []


def test_extract_emdash_format():
    content = """### Files Created or Modified (Code)
- web/contracts.py \u2014 added carrier-names datalist
- web/templates/contracts_list.html \u2014 added datalist element
"""
    paths = _extract_file_paths(content)
    assert len(paths) == 2
    assert paths[0]["path"] == "web/contracts.py"


# --- parse_dev_logs ---

def test_parse_dev_logs(dev_log_dir):
    results = parse_dev_logs(dev_log_dir)

    # Should find 3 logs with file paths (diagnostic has none)
    assert len(results) == 3

    slugs = {r["plan_slug"] for r in results}
    assert "action-router-engine-2026-03-14" in slugs
    assert "carrier-identity-2026-03-16" in slugs
    assert "autofill-features-2026-03-20" in slugs

    # Diagnostic should be excluded (no file paths)
    assert "carrier-aging-diagnostic-2026-03-23" not in slugs


def test_parse_dev_logs_descriptions(dev_log_dir):
    results = parse_dev_logs(dev_log_dir)
    by_slug = {r["plan_slug"]: r for r in results}

    assert by_slug["action-router-engine-2026-03-14"]["plan_description"] == "Action Router Engine"
    assert by_slug["carrier-identity-2026-03-16"]["plan_description"] == "Carrier Identity Detection"


def test_parse_dev_logs_nonexistent_dir():
    results = parse_dev_logs("/nonexistent/path")
    assert results == []


def test_parse_dev_logs_file_counts(dev_log_dir):
    results = parse_dev_logs(dev_log_dir)
    by_slug = {r["plan_slug"]: r for r in results}

    assert len(by_slug["action-router-engine-2026-03-14"]["file_paths"]) == 3
    assert len(by_slug["carrier-identity-2026-03-16"]["file_paths"]) == 2
    assert len(by_slug["autofill-features-2026-03-20"]["file_paths"]) == 2


# --- ingest_provenance ---

def test_ingest_provenance(conn, dev_log_dir):
    pid = create_project(conn, "test-proj", "/tmp/test")

    # Create module chunks for files referenced in dev logs
    create_chunk(
        conn, project_id=pid, file_path="engines/action_router.py",
        chunk_type="module", name="action_router",
        content="", content_hash="m1", start_line=1, end_line=1,
    )
    # Create a function chunk in that file
    cid = create_chunk(
        conn, project_id=pid, file_path="engines/action_router.py",
        chunk_type="function", name="route_actions",
        content="def route_actions():\n    pass",
        content_hash="f1", start_line=2, end_line=3,
    )
    # Create chunk for app.py
    create_chunk(
        conn, project_id=pid, file_path="app.py",
        chunk_type="module", name="app",
        content="", content_hash="m2", start_line=1, end_line=1,
    )

    result = ingest_provenance(conn, "test-proj", dev_log_dir)
    assert result["logs_parsed"] == 3
    assert result["provenance_entries_created"] > 0

    # Verify provenance entries exist
    cur = conn.execute("SELECT COUNT(*) FROM chunk_provenance")
    count = cur.fetchone()[0]
    assert count > 0

    # Check specific linkage
    cur = conn.execute(
        "SELECT plan_name, plan_description FROM chunk_provenance WHERE chunk_id = ?",
        (cid,),
    )
    row = cur.fetchone()
    assert row is not None
    assert row[0] == "action-router-engine-2026-03-14"
    assert row[1] == "Action Router Engine"


def test_ingest_provenance_idempotent(conn, dev_log_dir):
    """Running ingest twice should not create duplicate entries."""
    pid = create_project(conn, "test-proj", "/tmp/test")
    create_chunk(
        conn, project_id=pid, file_path="engines/action_router.py",
        chunk_type="function", name="route_actions",
        content="def route_actions():\n    pass",
        content_hash="f1", start_line=1, end_line=2,
    )

    result1 = ingest_provenance(conn, "test-proj", dev_log_dir)
    result2 = ingest_provenance(conn, "test-proj", dev_log_dir)

    # Second run should create 0 new entries
    assert result2["provenance_entries_created"] == 0

    cur = conn.execute("SELECT COUNT(*) FROM chunk_provenance")
    assert cur.fetchone()[0] == result1["provenance_entries_created"]


def test_ingest_provenance_project_not_found(conn, dev_log_dir):
    with pytest.raises(ValueError, match="Project not found"):
        ingest_provenance(conn, "nonexistent", dev_log_dir)
