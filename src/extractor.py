"""
Anvil Stage 2 — code extraction orchestrator.

Processes scanned files through the Python parser, stores chunks with parent
linkage, creates symbol bindings and dependencies, computes MinHash fingerprints,
and detects similarities.
"""
from __future__ import annotations

import ast
import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from src import db
from src.config import MINHASH_NUM_PERM, MINHASH_THRESHOLD, SCAN_TARGETS
from src.parsers import python_parser

try:
    from datasketch import MinHash, MinHashLSH
    HAS_DATASKETCH = True
except ImportError:
    HAS_DATASKETCH = False


def extract_project(conn, project_name: str, cycle_id: int) -> dict:
    """
    Main entry point for extracting all files in a project.

    Returns summary dict with extraction counts.
    """
    project = db.get_project(conn, project_name)
    if project is None:
        raise ValueError(f"Project not found: {project_name}")

    project_id = project["id"]
    project_path = SCAN_TARGETS.get(project_name)
    if project_path is None:
        raise ValueError(f"No scan target for project: {project_name}")

    # Query all module chunks (file-level), filter to .py
    conn.row_factory = db._row_to_dict
    cur = conn.execute(
        "SELECT * FROM code_chunks WHERE project_id = ? AND chunk_type = 'module'",
        (project_id,),
    )
    module_chunks = cur.fetchall()
    conn.row_factory = None

    py_modules = [m for m in module_chunks if m["file_path"].endswith(".py")]

    files_processed = 0
    chunks_created = 0
    chunks_updated = 0
    symbols_extracted = 0

    for module_chunk in py_modules:
        abs_path = os.path.join(project_path, module_chunk["file_path"])
        if not os.path.isfile(abs_path):
            continue

        parsed_chunks = python_parser.parse_file(abs_path)
        if not parsed_chunks:
            files_processed += 1
            continue

        # Track class chunks for parent linkage
        class_chunk_ids = {}

        for chunk_dict in parsed_chunks:
            parent_chunk_id = None
            if chunk_dict["parent_name"] is not None:
                # Method inside a class — look up class chunk
                parent_chunk_id = class_chunk_ids.get(chunk_dict["parent_name"])
            elif chunk_dict["chunk_type"] != "class":
                # Top-level function/test_case — parent is module
                parent_chunk_id = module_chunk["id"]

            # Dedup check
            existing = _find_existing_chunk(
                conn, project_id, module_chunk["file_path"],
                chunk_dict["name"], chunk_dict["chunk_type"],
            )

            if existing:
                if existing["content_hash"] == chunk_dict["content_hash"]:
                    chunk_id = existing["id"]
                    if chunk_dict["chunk_type"] == "class":
                        class_chunk_ids[chunk_dict["name"]] = chunk_id
                else:
                    _update_chunk(conn, existing["id"], chunk_dict, parent_chunk_id)
                    chunk_id = existing["id"]
                    chunks_updated += 1
                    if chunk_dict["chunk_type"] == "class":
                        class_chunk_ids[chunk_dict["name"]] = chunk_id
            else:
                chunk_id = db.create_chunk(
                    conn,
                    project_id=project_id,
                    file_path=module_chunk["file_path"],
                    chunk_type=chunk_dict["chunk_type"],
                    name=chunk_dict["name"],
                    content=chunk_dict["content"],
                    content_hash=chunk_dict["content_hash"],
                    start_line=chunk_dict["start_line"],
                    end_line=chunk_dict["end_line"],
                    parent_chunk_id=parent_chunk_id,
                    cycle_id=cycle_id,
                )
                chunks_created += 1
                if chunk_dict["chunk_type"] == "class":
                    class_chunk_ids[chunk_dict["name"]] = chunk_id

        # Fix parent linkage for classes (class → module)
        for class_name, class_id in class_chunk_ids.items():
            existing_class = _find_existing_chunk(
                conn, project_id, module_chunk["file_path"], class_name, "class"
            )
            if existing_class and existing_class.get("parent_chunk_id") is None:
                conn.execute(
                    "UPDATE code_chunks SET parent_chunk_id = ? WHERE id = ?",
                    (module_chunk["id"], class_id),
                )
                conn.commit()

        # Extract symbols for this file
        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                source = f.read()
            tree = ast.parse(source, filename=abs_path)
            source_lines = source.splitlines(True)

            file_symbols = python_parser.extract_symbols(
                abs_path, source_lines, tree
            )
            symbols_extracted += _store_file_symbols(
                conn, project_id, module_chunk, file_symbols
            )

            # Structural metadata for each chunk in this file
            _store_file_metadata(
                conn, project_id, module_chunk["file_path"], tree, source_lines
            )

            # SQLAlchemy models
            sa_models = python_parser.detect_sqlalchemy_models(tree, source_lines)
            for model in sa_models:
                class_cid = class_chunk_ids.get(model["class_name"])
                if class_cid:
                    for binding in model["symbol_bindings"]:
                        db.create_symbol_binding(
                            conn, class_cid,
                            binding["symbol_name"],
                            binding["binding_type"],
                        )
                        symbols_extracted += 1

        except (SyntaxError, OSError):
            pass

        files_processed += 1

    deps = resolve_dependencies(conn, project_id)
    fp_created, sims = compute_fingerprints(conn, project_id, cycle_id)

    return {
        "files_processed": files_processed,
        "chunks_created": chunks_created,
        "chunks_updated": chunks_updated,
        "symbols_extracted": symbols_extracted,
        "dependencies_resolved": deps,
        "fingerprints_created": fp_created,
        "similarities_found": sims,
    }


def _find_existing_chunk(conn, project_id: int, file_path: str,
                         name: str, chunk_type: str) -> Optional[dict]:
    """Find an existing chunk by project, file, name, and type."""
    conn.row_factory = db._row_to_dict
    cur = conn.execute(
        "SELECT * FROM code_chunks WHERE project_id = ? AND file_path = ? "
        "AND name = ? AND chunk_type = ?",
        (project_id, file_path, name, chunk_type),
    )
    row = cur.fetchone()
    conn.row_factory = None
    return row


def _find_production_chunk(conn, project_id: int,
                           callee_name: str) -> Optional[dict]:
    """Find a production chunk by name, excluding test files."""
    conn.row_factory = db._row_to_dict
    cur = conn.execute(
        "SELECT * FROM code_chunks WHERE project_id = ? AND name = ? "
        "AND chunk_type IN ('function', 'method', 'class') "
        "AND file_path NOT LIKE 'tests/%'",
        (project_id, callee_name),
    )
    row = cur.fetchone()
    conn.row_factory = None
    return row


def _update_chunk(conn, chunk_id: int, chunk_dict: dict,
                  parent_chunk_id: Optional[int]) -> None:
    """Update an existing chunk with new content."""
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE code_chunks SET content = ?, content_hash = ?, "
        "start_line = ?, end_line = ?, parent_chunk_id = ?, updated_at = ? "
        "WHERE id = ?",
        (chunk_dict["content"], chunk_dict["content_hash"],
         chunk_dict["start_line"], chunk_dict["end_line"],
         parent_chunk_id, now, chunk_id),
    )
    conn.commit()


def _store_file_symbols(conn, project_id: int, module_chunk: dict,
                        symbols: dict) -> int:
    """Store symbol bindings for all chunks in a file."""
    count = 0

    # Store imports on the module chunk
    for imp in symbols["imports"]:
        module_name = imp["module"]
        if imp["is_from"] and imp["names"]:
            for name in imp["names"]:
                db.create_symbol_binding(
                    conn, module_chunk["id"], f"{module_name}.{name}", "imports"
                )
                count += 1
        else:
            db.create_symbol_binding(
                conn, module_chunk["id"], module_name, "imports"
            )
            count += 1

    # Store definitions on their respective chunks
    for defn in symbols["definitions"]:
        chunk = _find_existing_chunk(
            conn, project_id, module_chunk["file_path"],
            defn["name"],
            "class" if defn["type"] == "class" else "function",
        )
        if not chunk:
            # Try method or test_case
            chunk = _find_existing_chunk(
                conn, project_id, module_chunk["file_path"],
                defn["name"], "method",
            )
        if not chunk:
            chunk = _find_existing_chunk(
                conn, project_id, module_chunk["file_path"],
                defn["name"], "test_case",
            )
        if chunk:
            db.create_symbol_binding(conn, chunk["id"], defn["name"], "defines")
            count += 1

    # Store calls on caller chunks + function-level test bindings
    for call in symbols["calls"]:
        caller_name = call["caller"]
        caller_chunk_type = None
        if caller_name == "<module>":
            chunk_id = module_chunk["id"]
        else:
            chunk = _find_existing_chunk(
                conn, project_id, module_chunk["file_path"],
                caller_name, "function",
            )
            if not chunk:
                chunk = _find_existing_chunk(
                    conn, project_id, module_chunk["file_path"],
                    caller_name, "method",
                )
            if not chunk:
                chunk = _find_existing_chunk(
                    conn, project_id, module_chunk["file_path"],
                    caller_name, "test_case",
                )
            chunk_id = chunk["id"] if chunk else module_chunk["id"]
            if chunk:
                caller_chunk_type = chunk["chunk_type"]

        db.create_symbol_binding(conn, chunk_id, call["callee"], "calls")
        count += 1

        # Function-level test binding: when a test_case calls a production
        # function, create a "tests" binding with target_chunk_id populated
        if caller_chunk_type == "test_case":
            target = _find_production_chunk(
                conn, project_id, call["callee"]
            )
            if target:
                dup = conn.execute(
                    "SELECT COUNT(*) FROM chunk_symbol_bindings "
                    "WHERE chunk_id = ? AND binding_type = 'tests' "
                    "AND target_chunk_id = ?",
                    (chunk_id, target["id"]),
                ).fetchone()[0]
                if dup == 0:
                    db.create_symbol_binding(
                        conn, chunk_id, target["name"], "tests",
                        target_chunk_id=target["id"],
                    )
                    count += 1

    # Store test mappings
    for tm in symbols["test_mappings"]:
        chunk = _find_existing_chunk(
            conn, project_id, module_chunk["file_path"],
            tm["test_name"], "test_case",
        )
        if chunk:
            db.create_symbol_binding(
                conn, chunk["id"], tm["tested_module"], "tests"
            )
            count += 1

    return count


def _store_file_metadata(conn, project_id: int, file_path: str,
                         tree: ast.Module, source_lines: list[str]) -> None:
    """Compute and store structural metadata for all chunks in a file."""
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            chunk_type = "test_case" if node.name.startswith("test_") else "function"
            chunk = _find_existing_chunk(
                conn, project_id, file_path, node.name, chunk_type,
            )
            if chunk:
                meta = python_parser.compute_structural_metadata(node, source_lines)
                store_structural_metadata(conn, chunk["id"], meta)

        elif isinstance(node, ast.ClassDef):
            chunk = _find_existing_chunk(
                conn, project_id, file_path, node.name, "class",
            )
            if chunk:
                meta = python_parser.compute_structural_metadata(node, source_lines)
                store_structural_metadata(conn, chunk["id"], meta)

            is_test_class = node.name.startswith("Test")
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    child_type = "test_case" if (child.name.startswith("test_") or is_test_class) else "method"
                    child_chunk = _find_existing_chunk(
                        conn, project_id, file_path, child.name, child_type,
                    )
                    if child_chunk:
                        meta = python_parser.compute_structural_metadata(
                            child, source_lines
                        )
                        store_structural_metadata(conn, child_chunk["id"], meta)


def store_symbols(conn, chunk_id: int, symbols: dict) -> int:
    """Store symbol bindings for a single chunk. Returns count created."""
    count = 0
    for imp in symbols.get("imports", []):
        db.create_symbol_binding(conn, chunk_id, imp["module"], "imports")
        count += 1
    for defn in symbols.get("definitions", []):
        db.create_symbol_binding(conn, chunk_id, defn["name"], "defines")
        count += 1
    for call in symbols.get("calls", []):
        db.create_symbol_binding(conn, chunk_id, call["callee"], "calls")
        count += 1
    for tm in symbols.get("test_mappings", []):
        db.create_symbol_binding(conn, chunk_id, tm["tested_module"], "tests")
        count += 1
    return count


def resolve_dependencies(conn, project_id: int) -> int:
    """
    Second pass: resolve symbol bindings into chunk dependencies.

    Returns count of dependencies created.
    """
    count = 0

    # Get all chunks for this project (for lookup)
    conn.row_factory = db._row_to_dict
    cur = conn.execute(
        "SELECT id, name, file_path, chunk_type FROM code_chunks WHERE project_id = ?",
        (project_id,),
    )
    all_chunks = cur.fetchall()
    conn.row_factory = None

    # Build lookup maps
    by_name = {}
    for c in all_chunks:
        by_name.setdefault(c["name"], []).append(c)

    # file_path lookup: convert module path to file_path
    by_file = {}
    for c in all_chunks:
        if c["chunk_type"] == "module":
            # Strip .py and convert to dot notation
            mod_name = c["file_path"].replace("/", ".").replace(".py", "")
            by_file[mod_name] = c

    # Get all import bindings for this project
    cur = conn.execute(
        "SELECT csb.id, csb.chunk_id, csb.symbol_name, cc.file_path "
        "FROM chunk_symbol_bindings csb "
        "JOIN code_chunks cc ON csb.chunk_id = cc.id "
        "WHERE cc.project_id = ? AND csb.binding_type = 'imports'",
        (project_id,),
    )
    import_bindings = cur.fetchall()

    for binding in import_bindings:
        _, source_chunk_id, symbol_name, source_file = binding
        # Try to resolve: strip submodule (e.g., "os.path" → "os")
        base_name = symbol_name.split(".")[0] if "." in symbol_name else symbol_name

        target_chunk = None

        # Strategy 1: match by file path (module import)
        if symbol_name in by_file:
            target_chunk = by_file[symbol_name]
        elif base_name in by_file:
            target_chunk = by_file[base_name]

        # Strategy 2: match by chunk name (from X import Y)
        if not target_chunk:
            leaf_name = symbol_name.split(".")[-1] if "." in symbol_name else symbol_name
            candidates = by_name.get(leaf_name, [])
            # Prefer defines bindings
            for c in candidates:
                if c["chunk_type"] != "module" and c["id"] != source_chunk_id:
                    target_chunk = c
                    break

        if target_chunk and target_chunk["id"] != source_chunk_id:
            scope = ("within_file" if source_file == target_chunk["file_path"]
                     else "cross_file")
            try:
                db.create_dependency(
                    conn, source_chunk_id, target_chunk["id"], "import", scope
                )
                count += 1
            except sqlite3.IntegrityError:
                pass  # Duplicate dependency

    # Resolve call dependencies
    cur = conn.execute(
        "SELECT csb.chunk_id, csb.symbol_name, cc.file_path "
        "FROM chunk_symbol_bindings csb "
        "JOIN code_chunks cc ON csb.chunk_id = cc.id "
        "WHERE cc.project_id = ? AND csb.binding_type = 'calls'",
        (project_id,),
    )
    call_bindings = cur.fetchall()

    for source_chunk_id, callee_name, source_file in call_bindings:
        candidates = by_name.get(callee_name, [])
        for c in candidates:
            if c["id"] != source_chunk_id and c["chunk_type"] in ("function", "method"):
                scope = ("within_file" if source_file == c["file_path"]
                         else "cross_file")
                try:
                    db.create_dependency(
                        conn, source_chunk_id, c["id"], "call", scope
                    )
                    count += 1
                except sqlite3.IntegrityError:
                    pass
                break  # Take first match

    # Resolve inheritance
    conn.row_factory = db._row_to_dict
    cur = conn.execute(
        "SELECT csb.chunk_id, csb.symbol_name, cc.file_path "
        "FROM chunk_symbol_bindings csb "
        "JOIN code_chunks cc ON csb.chunk_id = cc.id "
        "WHERE cc.project_id = ? AND csb.binding_type = 'defines' "
        "AND cc.chunk_type = 'class'",
        (project_id,),
    )
    class_defines = cur.fetchall()
    conn.row_factory = None

    # For classes, check if their bases resolve to other class chunks
    for class_chunk_id, class_name, class_file in class_defines:
        # Get the AST bases from the class (stored as definitions with bases)
        # Look for class definitions in symbols
        conn.row_factory = db._row_to_dict
        cur = conn.execute(
            "SELECT content FROM code_chunks WHERE id = ?", (class_chunk_id,)
        )
        row = cur.fetchone()
        conn.row_factory = None

        if row:
            try:
                class_tree = ast.parse(row["content"])
                for node in ast.walk(class_tree):
                    if isinstance(node, ast.ClassDef):
                        for base in node.bases:
                            base_name = None
                            if isinstance(base, ast.Name):
                                base_name = base.id
                            elif isinstance(base, ast.Attribute):
                                base_name = base.attr
                            if base_name:
                                candidates = by_name.get(base_name, [])
                                for c in candidates:
                                    if c["chunk_type"] == "class" and c["id"] != class_chunk_id:
                                        scope = ("within_file" if class_file == c["file_path"]
                                                 else "cross_file")
                                        try:
                                            db.create_dependency(
                                                conn, class_chunk_id, c["id"],
                                                "inherit", scope
                                            )
                                            count += 1
                                        except sqlite3.IntegrityError:
                                            pass
                                        break
            except SyntaxError:
                pass

    return count


def compute_fingerprints(conn, project_id: int,
                         cycle_id: int) -> tuple[int, int]:
    """
    Compute MinHash signatures and detect similarities.

    Returns (fingerprints_created, similarities_found).
    """
    conn.row_factory = db._row_to_dict
    cur = conn.execute(
        "SELECT id, content, content_hash FROM code_chunks "
        "WHERE project_id = ? AND chunk_type != 'module'",
        (project_id,),
    )
    chunks = cur.fetchall()
    conn.row_factory = None

    fp_created = 0
    minhash_store = {}  # chunk_id -> MinHash object

    for chunk in chunks:
        content = chunk["content"]
        line_count = content.count("\n") + 1

        if HAS_DATASKETCH and line_count >= 5:
            mh = MinHash(num_perm=MINHASH_NUM_PERM)
            shingles = _make_shingles(content, 3)
            for s in shingles:
                mh.update(s.encode("utf-8"))
            sig = bytes(mh.digest())
            db.create_fingerprint(
                conn, chunk["id"], chunk["content_hash"],
                sig, len(shingles), cycle_id,
            )
            minhash_store[chunk["id"]] = mh
        else:
            db.create_fingerprint(
                conn, chunk["id"], chunk["content_hash"],
                None, 0, cycle_id,
            )
        fp_created += 1

    # Similarity detection via LSH
    sims_found = 0
    if HAS_DATASKETCH and minhash_store:
        try:
            lsh = MinHashLSH(threshold=MINHASH_THRESHOLD,
                             num_perm=MINHASH_NUM_PERM)
            for cid, mh in minhash_store.items():
                try:
                    lsh.insert(str(cid), mh)
                except ValueError:
                    pass  # Duplicate key

            seen_pairs = set()
            for cid, mh in minhash_store.items():
                results = lsh.query(mh)
                for r in results:
                    other_id = int(r)
                    if other_id != cid:
                        pair = tuple(sorted((cid, other_id)))
                        if pair not in seen_pairs:
                            seen_pairs.add(pair)
                            score = minhash_store[cid].jaccard(
                                minhash_store[other_id]
                            )
                            if score >= MINHASH_THRESHOLD:
                                db.create_similarity(
                                    conn, pair[0], pair[1], score, cycle_id
                                )
                                sims_found += 1
        except Exception:
            pass  # LSH errors shouldn't crash extraction

    return fp_created, sims_found


def _make_shingles(text: str, k: int) -> list[str]:
    """Create k-word shingles from text."""
    words = text.split()
    if len(words) < k:
        return [text] if text.strip() else []
    return [" ".join(words[i:i + k]) for i in range(len(words) - k + 1)]


def store_structural_metadata(conn, chunk_id: int,
                              metadata_dict: dict) -> None:
    """Store structural metadata as JSON on the chunk."""
    conn.execute(
        "UPDATE code_chunks SET structural_metadata = ? WHERE id = ?",
        (json.dumps(metadata_dict), chunk_id),
    )
    conn.commit()
