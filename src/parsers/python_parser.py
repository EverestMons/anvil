"""
Anvil Python parser — AST-based source code analysis.

Pure parsing module with no DB dependency. Extracts code chunks, symbols,
structural metadata, and SQLAlchemy model patterns from Python source files.
"""
from __future__ import annotations

import ast
import hashlib
import os
from typing import Optional


def parse_file(file_path: str) -> list[dict]:
    """
    Parse a Python file and extract code chunks.

    Returns a list of chunk dicts sorted by start_line, each containing:
    name, chunk_type, content, content_hash, start_line, end_line, parent_name.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
    except (OSError, IOError):
        return []

    if not source.strip():
        return []

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        return []

    source_lines = source.splitlines(True)
    chunks = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            chunk_type = _classify_function(node.name, None)
            chunks.append(_node_to_chunk(node, source_lines, chunk_type, None))

        elif isinstance(node, ast.ClassDef):
            is_test_class = node.name.startswith("Test")
            chunks.append(_node_to_chunk(node, source_lines, "class", None))

            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    child_type = _classify_function(
                        child.name, node.name, is_test_class
                    )
                    chunks.append(
                        _node_to_chunk(child, source_lines, child_type, node.name)
                    )

    chunks.sort(key=lambda c: c["start_line"])
    return chunks


def _classify_function(name: str, class_name: Optional[str],
                       is_test_class: bool = False) -> str:
    """Determine chunk_type for a function/method node."""
    if name.startswith("test_") or is_test_class:
        return "test_case"
    if class_name is not None:
        return "method"
    return "function"


def _node_to_chunk(node, source_lines: list[str], chunk_type: str,
                   parent_name: Optional[str]) -> dict:
    """Convert an AST node to a chunk dict."""
    start = node.lineno
    end = node.end_lineno or start
    content = "".join(source_lines[start - 1:end])
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    return {
        "name": node.name,
        "chunk_type": chunk_type,
        "content": content,
        "content_hash": content_hash,
        "start_line": start,
        "end_line": end,
        "parent_name": parent_name,
    }


def extract_symbols(file_path: str, source_lines: list[str],
                    ast_tree: ast.Module) -> dict:
    """
    Walk the AST and return structured symbol data.

    Returns dict with keys: imports, definitions, calls, test_mappings.
    """
    imports = []
    definitions = []
    calls = []
    test_mappings = []

    basename = os.path.basename(file_path)
    is_test_file = basename.startswith("test_")
    if is_test_file:
        tested_module = basename.replace("test_", "", 1).replace(".py", "")

    for node in ast.walk(ast_tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({
                    "module": alias.name,
                    "names": [],
                    "is_from": False,
                    "line": node.lineno,
                })

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = [alias.name for alias in node.names]
            imports.append({
                "module": module,
                "names": names,
                "is_from": True,
                "line": node.lineno,
            })

        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            def_type = "function"
            bases = []
            definitions.append({
                "name": node.name,
                "type": def_type,
                "line": node.lineno,
            })
            if is_test_file and node.name.startswith("test_"):
                test_mappings.append({
                    "test_name": node.name,
                    "tested_module": tested_module,
                })

        elif isinstance(node, ast.ClassDef):
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(f"{_resolve_attr(base)}")
            definitions.append({
                "name": node.name,
                "type": "class",
                "bases": bases,
                "line": node.lineno,
            })

        elif isinstance(node, ast.Call):
            callee = _resolve_call_name(node)
            if callee:
                caller = _find_enclosing_function(node, ast_tree)
                calls.append({
                    "caller": caller or "<module>",
                    "callee": callee,
                    "line": node.lineno,
                })

    return {
        "imports": imports,
        "definitions": definitions,
        "calls": calls,
        "test_mappings": test_mappings,
    }


def _resolve_call_name(node: ast.Call) -> Optional[str]:
    """Resolve the callee name from a Call node."""
    if isinstance(node.func, ast.Name):
        return node.func.id
    elif isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _resolve_attr(node: ast.Attribute) -> str:
    """Resolve a dotted attribute like db.Model."""
    parts = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def _find_enclosing_function(node, tree: ast.Module) -> Optional[str]:
    """Find the function/class that encloses a given node by line number."""
    best = None
    for top_node in ast.iter_child_nodes(tree):
        if isinstance(top_node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if (hasattr(node, "lineno") and hasattr(top_node, "end_lineno")
                    and top_node.lineno <= node.lineno <= (top_node.end_lineno or 0)):
                best = top_node.name
    return best


def compute_structural_metadata(ast_node, source_lines: list[str]) -> dict:
    """
    Compute per-chunk structural metrics.

    Returns dict with: cyclomatic_complexity, nesting_depth, parameter_count,
    import_count, has_docstring, line_count.
    """
    complexity = 1
    import_count = 0

    for node in ast.walk(ast_node):
        if isinstance(node, (ast.If,)):
            complexity += 1
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            complexity += 1
        elif isinstance(node, (ast.While,)):
            complexity += 1
        elif isinstance(node, (ast.Try,)):
            complexity += 1
        elif isinstance(node, (ast.ExceptHandler,)):
            complexity += 1
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            complexity += 1
        elif isinstance(node, ast.Assert):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                complexity += len(node.values) - 1
            elif isinstance(node.op, ast.Or):
                complexity += len(node.values) - 1
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            import_count += 1

    nesting_depth = _compute_nesting_depth(ast_node)

    param_count = 0
    if isinstance(ast_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        param_count = len(ast_node.args.args) + len(ast_node.args.kwonlyargs)

    has_docstring = False
    if (ast_node.body
            and isinstance(ast_node.body[0], ast.Expr)
            and isinstance(ast_node.body[0].value, (ast.Constant,))):
        if isinstance(ast_node.body[0].value.value, str):
            has_docstring = True

    start = ast_node.lineno
    end = ast_node.end_lineno or start
    line_count = end - start + 1

    return {
        "cyclomatic_complexity": complexity,
        "nesting_depth": nesting_depth,
        "parameter_count": param_count,
        "import_count": import_count,
        "has_docstring": has_docstring,
        "line_count": line_count,
    }


def _compute_nesting_depth(node, depth=0) -> int:
    """Compute maximum nesting depth of control flow."""
    max_depth = depth
    control_flow = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try,
                    ast.With, ast.AsyncWith)

    for child in ast.iter_child_nodes(node):
        if isinstance(child, control_flow):
            child_depth = _compute_nesting_depth(child, depth + 1)
            max_depth = max(max_depth, child_depth)
        else:
            child_depth = _compute_nesting_depth(child, depth)
            max_depth = max(max_depth, child_depth)

    return max_depth


def detect_sqlalchemy_models(ast_tree: ast.Module,
                             source_lines: list[str]) -> list[dict]:
    """
    Detect SQLAlchemy model patterns in the AST.

    Returns list of model dicts with class_name, table_name, columns,
    relationships, and symbol_bindings.
    """
    models = []
    sa_base_names = {"Model", "Base", "DeclarativeBase"}

    for node in ast.iter_child_nodes(ast_tree):
        if not isinstance(node, ast.ClassDef):
            continue

        is_model = False
        for base in node.bases:
            base_name = ""
            if isinstance(base, ast.Name):
                base_name = base.id
            elif isinstance(base, ast.Attribute):
                base_name = _resolve_attr(base)

            if base_name in sa_base_names or base_name.endswith(".Model"):
                is_model = True
                break

        if not is_model:
            continue

        class_name = node.name
        table_name = None
        columns = []
        relationships = []

        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == "__tablename__":
                        if isinstance(item.value, ast.Constant):
                            table_name = item.value.value

                    elif isinstance(target, ast.Name) and isinstance(item.value, ast.Call):
                        call_name = _resolve_call_name(item.value)
                        if call_name in ("Column", "column"):
                            columns.append(target.id)
                        elif call_name in ("relationship", "Relationship"):
                            relationships.append(target.id)

        display_name = table_name or class_name
        bindings = [
            {"symbol_name": f"table:{display_name}", "binding_type": "defines"},
        ]
        for col in columns:
            bindings.append({
                "symbol_name": f"column:{display_name}.{col}",
                "binding_type": "defines",
            })
        for rel in relationships:
            bindings.append({
                "symbol_name": f"relationship:{display_name}.{rel}",
                "binding_type": "defines",
            })

        models.append({
            "class_name": class_name,
            "table_name": table_name,
            "columns": columns,
            "relationships": relationships,
            "symbol_bindings": bindings,
        })

    return models
