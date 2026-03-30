"""
Tests for Anvil Python parser — AST extraction, symbols, metadata, SQLAlchemy detection.
"""
import ast
import hashlib
import textwrap

import pytest

from src.parsers.python_parser import (
    parse_file,
    extract_symbols,
    compute_structural_metadata,
    detect_sqlalchemy_models,
)


@pytest.fixture
def simple_file(tmp_path):
    """A Python file with a function, a class, and a method."""
    code = textwrap.dedent("""\
        import os
        from pathlib import Path

        def helper(x, y):
            \"\"\"A helper function.\"\"\"
            if x > 0:
                return x + y
            return y

        class MyClass:
            def my_method(self, value):
                for i in range(value):
                    print(i)

            def another_method(self):
                pass
    """)
    f = tmp_path / "simple.py"
    f.write_text(code)
    return str(f), code


@pytest.fixture
def test_file(tmp_path):
    """A test file with test functions."""
    code = textwrap.dedent("""\
        import pytest
        from mymodule import helper

        def test_helper_positive():
            assert helper(1, 2) == 3

        def test_helper_zero():
            assert helper(0, 5) == 5

        class TestMyClass:
            def test_init(self):
                pass

            def test_method(self):
                pass
    """)
    f = tmp_path / "test_helper.py"
    f.write_text(code)
    return str(f), code


@pytest.fixture
def sqlalchemy_file(tmp_path):
    """A file with SQLAlchemy model patterns."""
    code = textwrap.dedent("""\
        from app import db

        class CarrierProfile(db.Model):
            __tablename__ = 'carrier_profiles'
            id = Column(db.Integer, primary_key=True)
            name = Column(db.String(100))
            code = Column(db.String(10))
            invoices = relationship('Invoice', back_populates='carrier')
    """)
    f = tmp_path / "models.py"
    f.write_text(code)
    return str(f), code


# --- parse_file ---

def test_parse_file_extracts_chunks(simple_file):
    path, _ = simple_file
    chunks = parse_file(path)
    names = [c["name"] for c in chunks]
    assert "helper" in names
    assert "MyClass" in names
    assert "my_method" in names
    assert "another_method" in names


def test_parse_file_chunk_types(simple_file):
    path, _ = simple_file
    chunks = parse_file(path)
    by_name = {c["name"]: c for c in chunks}
    assert by_name["helper"]["chunk_type"] == "function"
    assert by_name["MyClass"]["chunk_type"] == "class"
    assert by_name["my_method"]["chunk_type"] == "method"
    assert by_name["another_method"]["chunk_type"] == "method"


def test_parse_file_line_numbers(simple_file):
    path, _ = simple_file
    chunks = parse_file(path)
    by_name = {c["name"]: c for c in chunks}
    assert by_name["helper"]["start_line"] == 4
    assert by_name["helper"]["end_line"] == 8
    assert by_name["MyClass"]["start_line"] == 10


def test_parse_file_content_extraction(simple_file):
    path, _ = simple_file
    chunks = parse_file(path)
    by_name = {c["name"]: c for c in chunks}
    assert "def helper(x, y):" in by_name["helper"]["content"]
    assert "return x + y" in by_name["helper"]["content"]


def test_parse_file_content_hash(simple_file):
    path, _ = simple_file
    chunks = parse_file(path)
    for chunk in chunks:
        expected = hashlib.sha256(chunk["content"].encode("utf-8")).hexdigest()
        assert chunk["content_hash"] == expected


def test_parse_file_parent_name(simple_file):
    path, _ = simple_file
    chunks = parse_file(path)
    by_name = {c["name"]: c for c in chunks}
    assert by_name["helper"]["parent_name"] is None
    assert by_name["MyClass"]["parent_name"] is None
    assert by_name["my_method"]["parent_name"] == "MyClass"
    assert by_name["another_method"]["parent_name"] == "MyClass"


def test_parse_file_sorted_by_line(simple_file):
    path, _ = simple_file
    chunks = parse_file(path)
    lines = [c["start_line"] for c in chunks]
    assert lines == sorted(lines)


# --- parse_file: test files ---

def test_parse_file_test_functions(test_file):
    path, _ = test_file
    chunks = parse_file(path)
    by_name = {c["name"]: c for c in chunks}
    assert by_name["test_helper_positive"]["chunk_type"] == "test_case"
    assert by_name["test_helper_zero"]["chunk_type"] == "test_case"


def test_parse_file_test_class_methods(test_file):
    path, _ = test_file
    chunks = parse_file(path)
    by_name = {c["name"]: c for c in chunks}
    assert by_name["TestMyClass"]["chunk_type"] == "class"
    assert by_name["test_init"]["chunk_type"] == "test_case"
    assert by_name["test_method"]["chunk_type"] == "test_case"


# --- parse_file: edge cases ---

def test_parse_file_empty(tmp_path):
    f = tmp_path / "empty.py"
    f.write_text("")
    assert parse_file(str(f)) == []


def test_parse_file_syntax_error(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text("def broken(:\n    pass\n")
    assert parse_file(str(f)) == []


def test_parse_file_only_comments(tmp_path):
    f = tmp_path / "comments.py"
    f.write_text("# just a comment\n# another comment\n")
    assert parse_file(str(f)) == []


def test_parse_file_nonexistent():
    assert parse_file("/nonexistent/file.py") == []


# --- extract_symbols ---

def test_extract_symbols_imports(simple_file):
    path, code = simple_file
    tree = ast.parse(code)
    source_lines = code.splitlines(True)
    symbols = extract_symbols(path, source_lines, tree)
    modules = [i["module"] for i in symbols["imports"]]
    assert "os" in modules
    assert "pathlib" in modules


def test_extract_symbols_definitions(simple_file):
    path, code = simple_file
    tree = ast.parse(code)
    source_lines = code.splitlines(True)
    symbols = extract_symbols(path, source_lines, tree)
    def_names = [d["name"] for d in symbols["definitions"]]
    assert "helper" in def_names
    assert "MyClass" in def_names


def test_extract_symbols_class_bases(tmp_path):
    code = "class Child(Parent, Mixin):\n    pass\n"
    f = tmp_path / "child.py"
    f.write_text(code)
    tree = ast.parse(code)
    symbols = extract_symbols(str(f), code.splitlines(True), tree)
    class_def = [d for d in symbols["definitions"] if d["name"] == "Child"][0]
    assert "Parent" in class_def["bases"]
    assert "Mixin" in class_def["bases"]


def test_extract_symbols_calls(tmp_path):
    code = textwrap.dedent("""\
        def caller():
            helper()
            obj.method()
    """)
    f = tmp_path / "calls.py"
    f.write_text(code)
    tree = ast.parse(code)
    symbols = extract_symbols(str(f), code.splitlines(True), tree)
    callees = [c["callee"] for c in symbols["calls"]]
    assert "helper" in callees
    assert "method" in callees


def test_extract_symbols_test_mappings(test_file):
    path, code = test_file
    tree = ast.parse(code)
    symbols = extract_symbols(path, code.splitlines(True), tree)
    assert len(symbols["test_mappings"]) > 0
    assert symbols["test_mappings"][0]["tested_module"] == "helper"


# --- compute_structural_metadata ---

def test_metadata_cyclomatic_complexity(tmp_path):
    code = textwrap.dedent("""\
        def complex_func(x, y):
            if x > 0:
                for i in range(y):
                    if i % 2 == 0:
                        print(i)
            while x > 10:
                x -= 1
            assert x >= 0
    """)
    tree = ast.parse(code)
    func_node = tree.body[0]
    source_lines = code.splitlines(True)
    meta = compute_structural_metadata(func_node, source_lines)
    # Base 1 + if + for + if + while + assert = 6
    assert meta["cyclomatic_complexity"] == 6


def test_metadata_nesting_depth(tmp_path):
    code = textwrap.dedent("""\
        def nested():
            if True:
                for i in range(10):
                    if i > 5:
                        pass
    """)
    tree = ast.parse(code)
    func_node = tree.body[0]
    meta = compute_structural_metadata(func_node, code.splitlines(True))
    assert meta["nesting_depth"] == 3  # if -> for -> if


def test_metadata_parameter_count():
    code = "def func(a, b, c, *, d, e):\n    pass\n"
    tree = ast.parse(code)
    func_node = tree.body[0]
    meta = compute_structural_metadata(func_node, code.splitlines(True))
    assert meta["parameter_count"] == 5  # 3 args + 2 kwonly


def test_metadata_docstring_detection():
    code = 'def func():\n    """Docstring."""\n    pass\n'
    tree = ast.parse(code)
    meta = compute_structural_metadata(tree.body[0], code.splitlines(True))
    assert meta["has_docstring"] is True

    code2 = "def func():\n    pass\n"
    tree2 = ast.parse(code2)
    meta2 = compute_structural_metadata(tree2.body[0], code2.splitlines(True))
    assert meta2["has_docstring"] is False


def test_metadata_line_count():
    code = "def func():\n    x = 1\n    y = 2\n    return x + y\n"
    tree = ast.parse(code)
    meta = compute_structural_metadata(tree.body[0], code.splitlines(True))
    assert meta["line_count"] == 4


def test_metadata_class_has_zero_params():
    code = "class Foo:\n    pass\n"
    tree = ast.parse(code)
    meta = compute_structural_metadata(tree.body[0], code.splitlines(True))
    assert meta["parameter_count"] == 0


# --- detect_sqlalchemy_models ---

def test_detect_sqlalchemy_db_model(sqlalchemy_file):
    path, code = sqlalchemy_file
    tree = ast.parse(code)
    models = detect_sqlalchemy_models(tree, code.splitlines(True))
    assert len(models) == 1
    m = models[0]
    assert m["class_name"] == "CarrierProfile"
    assert m["table_name"] == "carrier_profiles"
    assert "name" in m["columns"]
    assert "code" in m["columns"]
    assert "invoices" in m["relationships"]


def test_detect_sqlalchemy_symbol_bindings(sqlalchemy_file):
    path, code = sqlalchemy_file
    tree = ast.parse(code)
    models = detect_sqlalchemy_models(tree, code.splitlines(True))
    binding_names = [b["symbol_name"] for b in models[0]["symbol_bindings"]]
    assert "table:carrier_profiles" in binding_names
    assert "column:carrier_profiles.name" in binding_names


def test_detect_sqlalchemy_no_models(simple_file):
    path, code = simple_file
    tree = ast.parse(code)
    models = detect_sqlalchemy_models(tree, code.splitlines(True))
    assert models == []


def test_detect_sqlalchemy_base_class(tmp_path):
    code = textwrap.dedent("""\
        class User(Base):
            __tablename__ = 'users'
            id = Column(Integer, primary_key=True)
            name = Column(String)
    """)
    f = tmp_path / "user.py"
    f.write_text(code)
    tree = ast.parse(code)
    models = detect_sqlalchemy_models(tree, code.splitlines(True))
    assert len(models) == 1
    assert models[0]["table_name"] == "users"
