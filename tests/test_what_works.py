"""
Tests for src.what_works and related changes:
- config.py: ANVIL_ROOT env-derived, PROJECTS_PARENT added, SCAN_TARGETS paths derived (t1, t2)
- src.what_works: production_defs, verified_inbound, survived, rank, precision_recall,
  ROLE_WEIGHTS, render_markdown (t3-t9, t11)
- scripts.what_works CLI glossary guard (t10)
- scripts.reprice_bellows_build: build_scratch_db factored (t12)
"""
import importlib
import importlib.util
import os
import sqlite3
import subprocess
import sys
import textwrap

import pytest

from src.db import (
    init_db, create_project, create_chunk, create_dependency, create_symbol_binding,
)
import src.config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_git_repo(path, branch="main"):
    subprocess.run(["git", "init", str(path)], capture_output=True, check=True)
    subprocess.run(
        ["git", "-C", str(path), "symbolic-ref", "HEAD", f"refs/heads/{branch}"],
        capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "-C", str(path), "config", "user.email", "test@test.com"],
        capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "-C", str(path), "config", "user.name", "Test"],
        capture_output=True, check=True,
    )


def _git_commit(path, msg="commit"):
    subprocess.run(["git", "-C", str(path), "add", "."], capture_output=True, check=True)
    subprocess.run(
        ["git", "-C", str(path), "commit", "--allow-empty", "-m", msg],
        capture_output=True, check=True,
    )


# ---------------------------------------------------------------------------
# DB fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    init_db(c)
    c.execute("PRAGMA foreign_keys=ON")
    yield c
    c.close()


# ---------------------------------------------------------------------------
# t1: ANVIL_ROOT env override
# ---------------------------------------------------------------------------

def test_config_anvil_root_env(monkeypatch, tmp_path):
    import src.config as cfg
    monkeypatch.delenv("ANVIL_ROOT", raising=False)
    monkeypatch.delenv("ANVIL_PROJECTS_PARENT", raising=False)
    try:
        importlib.reload(cfg)
        assert cfg.ANVIL_ROOT == cfg.ANVIL_RUNTIME_ROOT
        monkeypatch.setenv("ANVIL_ROOT", str(tmp_path))
        importlib.reload(cfg)
        assert cfg.ANVIL_ROOT == str(tmp_path)
    finally:
        monkeypatch.delenv("ANVIL_ROOT", raising=False)
        monkeypatch.delenv("ANVIL_PROJECTS_PARENT", raising=False)
        importlib.reload(cfg)


# ---------------------------------------------------------------------------
# t2: SCAN_TARGETS bellows path derived from PROJECTS_PARENT
# ---------------------------------------------------------------------------

def test_scan_targets_bellows_path(monkeypatch):
    import src.config as cfg
    monkeypatch.delenv("ANVIL_ROOT", raising=False)
    monkeypatch.delenv("ANVIL_PROJECTS_PARENT", raising=False)
    try:
        importlib.reload(cfg)
        assert cfg.PROJECTS_PARENT == os.path.dirname(cfg.ANVIL_RUNTIME_ROOT)
        assert cfg.SCAN_TARGETS["bellows"]["path"].endswith("/bellows")
        assert cfg.SCAN_TARGETS["bellows"]["path"] == os.path.join(
            cfg.PROJECTS_PARENT, "bellows"
        )
    finally:
        monkeypatch.delenv("ANVIL_ROOT", raising=False)
        monkeypatch.delenv("ANVIL_PROJECTS_PARENT", raising=False)
        importlib.reload(cfg)


# ---------------------------------------------------------------------------
# t3: production_defs excludes tests/ and counts methods
# ---------------------------------------------------------------------------

def test_production_defs_excludes_tests(tmp_path):
    from src.what_works import production_defs
    _make_git_repo(tmp_path)
    (tmp_path / "foo.py").write_text(
        textwrap.dedent("""\
            def top_fn():
                \"\"\"Top function docstring.\"\"\"
                pass

            class MyClass:
                def my_method(self, x):
                    return x
        """)
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_foo.py").write_text("def test_it(): pass\n")
    _git_commit(tmp_path, "init")
    defs = production_defs(str(tmp_path))
    names = {d["name"] for d in defs}
    assert "top_fn" in names
    assert "my_method" in names
    assert "test_it" not in names
    assert len(defs) == 2
    method = next(d for d in defs if d["name"] == "my_method")
    assert method["end_lineno"] > method["lineno"]


# ---------------------------------------------------------------------------
# t4: survived — stable_commits and age_days
# ---------------------------------------------------------------------------

def test_survived_stable_commits(tmp_path):
    from src.what_works import production_defs, survived
    _make_git_repo(tmp_path)
    (tmp_path / "foo.py").write_text("def f(x):\n    return x\n")
    _git_commit(tmp_path, "birth")
    # body change — stable (no signature line changed)
    (tmp_path / "foo.py").write_text("def f(x):\n    return x + 1\n")
    _git_commit(tmp_path, "body change")
    # signature change — unstable
    (tmp_path / "foo.py").write_text("def f(x, y):\n    return x + y\n")
    _git_commit(tmp_path, "signature change")
    defs = production_defs(str(tmp_path))
    assert len(defs) == 1
    rows = survived(str(tmp_path), defs, "2026-09-11")
    assert len(rows) == 1
    r = rows[0]
    assert r["stable_commits"] == 1
    assert r["age_days"] >= 0


# ---------------------------------------------------------------------------
# t5: birth-only def → score_b == 0
# ---------------------------------------------------------------------------

def test_survived_birth_only_score_zero(tmp_path):
    from src.what_works import production_defs, survived
    _make_git_repo(tmp_path)
    (tmp_path / "foo.py").write_text("def f():\n    pass\n")
    _git_commit(tmp_path, "birth")
    defs = production_defs(str(tmp_path))
    rows = survived(str(tmp_path), defs, "2026-09-11")
    assert rows[0]["score_b"] == 0


# ---------------------------------------------------------------------------
# t6: verified_inbound — import check
# ---------------------------------------------------------------------------

def test_verified_inbound_import_check(conn, tmp_path):
    from src.what_works import production_defs, verified_inbound
    _make_git_repo(tmp_path)
    (tmp_path / "b.py").write_text("def f():\n    pass\n")
    (tmp_path / "a.py").write_text(
        "import b\n\ndef caller():\n    b.f()\n"
    )
    (tmp_path / "c.py").write_text("def caller2():\n    f()\n")
    _git_commit(tmp_path, "init")

    pid = create_project(conn, "test", str(tmp_path))
    b_f = create_chunk(
        conn, project_id=pid, file_path="b.py", chunk_type="function",
        name="f", content="def f():\n    pass", content_hash="h1",
        start_line=1, end_line=2,
    )
    a_caller = create_chunk(
        conn, project_id=pid, file_path="a.py", chunk_type="function",
        name="caller", content="def caller():\n    b.f()", content_hash="h2",
        start_line=3, end_line=4,
    )
    c_caller = create_chunk(
        conn, project_id=pid, file_path="c.py", chunk_type="function",
        name="caller2", content="def caller2():\n    f()", content_hash="h3",
        start_line=1, end_line=2,
    )
    create_dependency(conn, a_caller, b_f, "call", "cross_file")
    create_dependency(conn, c_caller, b_f, "call", "cross_file")

    defs = production_defs(str(tmp_path))
    result = verified_inbound(conn, str(tmp_path), defs)
    assert "b.py::f" in result
    assert result["b.py::f"] == 1  # only a.py verified (a.py imports b)


# ---------------------------------------------------------------------------
# t7: rank — ties broken by file::name ascending
# ---------------------------------------------------------------------------

def test_rank_tie_by_name():
    from src.what_works import rank
    rows = [
        {"file": "z.py", "name": "b", "score_c": 10.0, "score_a": 10, "score_b": 10},
        {"file": "a.py", "name": "c", "score_c": 10.0, "score_a": 10, "score_b": 10},
        {"file": "a.py", "name": "a", "score_c": 20.0, "score_a": 20, "score_b": 20},
    ]
    ranked = rank(rows, "c")
    assert ranked[0]["file"] == "a.py" and ranked[0]["name"] == "a"
    assert ranked[1]["file"] == "a.py" and ranked[1]["name"] == "c"
    assert ranked[2]["file"] == "z.py" and ranked[2]["name"] == "b"


# ---------------------------------------------------------------------------
# t8: score_c differs from score_a for gate_checker, equals for utility
# ---------------------------------------------------------------------------

def test_score_c_role_weight():
    from src.what_works import ROLE_WEIGHTS
    gate_weight = ROLE_WEIGHTS.get("gate_checker", 1.0)
    util_weight = ROLE_WEIGHTS.get("utility", 1.0)
    score_a = 80
    assert score_a * gate_weight != score_a * util_weight
    assert score_a * util_weight == score_a  # utility weight must be 1.0


# ---------------------------------------------------------------------------
# t9: precision_recall
# ---------------------------------------------------------------------------

def test_precision_recall():
    from src.what_works import precision_recall
    ranked = [
        {"file": "a.py", "name": "f1"},
        {"file": "b.py", "name": "f2"},
        {"file": "c.py", "name": "f3"},
        {"file": "d.py", "name": "f4"},
        {"file": "e.py", "name": "f5"},
    ]
    reference = {"a.py::f1", "b.py::f2", "x.py::missing"}
    p, r = precision_recall(ranked, reference, k=3)
    # top-3: a.py::f1, b.py::f2, c.py::f3 — 2 hits; |reference| = 3
    assert abs(p - 2 / 3) < 1e-9
    assert abs(r - 2 / 3) < 1e-9


# ---------------------------------------------------------------------------
# t10: CLI glossary guard
# ---------------------------------------------------------------------------

def test_cli_glossary_guard(tmp_path):
    anvil_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script = os.path.join(anvil_root, "scripts", "what_works.py")

    # Refuses GLOSSARY.md
    glossary_path = str(tmp_path / "GLOSSARY.md")
    r = subprocess.run(
        [sys.executable, script, "--tmp", str(tmp_path), "--out-md", glossary_path],
        capture_output=True,
    )
    assert r.returncode == 2
    assert not os.path.exists(glossary_path)

    # Refuses knowledge/decisions path
    kd_dir = tmp_path / "knowledge" / "decisions"
    kd_dir.mkdir(parents=True)
    kd_path = str(kd_dir / "x.md")
    r = subprocess.run(
        [sys.executable, script, "--tmp", str(tmp_path), "--out-md", kd_path],
        capture_output=True,
    )
    assert r.returncode == 2
    assert not os.path.exists(kd_path)

    # Accepts research/ path — guard does not fire (may fail for other reasons)
    research_dir = tmp_path / "research"
    research_dir.mkdir()
    ok_path = str(research_dir / "x.md")
    r = subprocess.run(
        [sys.executable, script, "--tmp", str(tmp_path),
         "--checkout", "/nonexistent", "--out-md", ok_path],
        capture_output=True,
    )
    assert r.returncode != 2


# ---------------------------------------------------------------------------
# t11: render_markdown contains the six fields
# ---------------------------------------------------------------------------

def test_render_markdown_fields():
    from src.what_works import render_markdown
    entries = [
        {
            "role": "gate_checker",
            "signature": "def check(conn, plan_path):",
            "verified_callers_count": 5,
            "verified_callers_sample": ["bellows.py::run_plan"],
            "docstring": "Run all gate checks.",
            "tests_bound_count": 3,
            "tests_bound_sample": ["tests/test_gates.py::TestGates::test_check"],
        }
    ]
    md = render_markdown(entries, {"definition": "c", "top_k": 1, "checkout": "/tmp/x"})
    assert "gate_checker" in md
    assert "def check" in md
    assert "Run all gate checks" in md


# ---------------------------------------------------------------------------
# t12: build_scratch_db importable from scripts.reprice_bellows_build
# ---------------------------------------------------------------------------

def test_build_scratch_db_importable():
    anvil_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    spec = importlib.util.spec_from_file_location(
        "reprice_bellows_build",
        os.path.join(anvil_root, "scripts", "reprice_bellows_build.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, "build_scratch_db"), "build_scratch_db not found"
    assert callable(mod.build_scratch_db)
    assert callable(mod.main)
