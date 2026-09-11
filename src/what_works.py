"""
Read-only entry generator for the 'what works' glossary definition.
Implements the three scoring definitions from #100072: (a) import-verified inbound,
(b) survived, (c) role-weighted. No function writes a file; no function imports
run_cycle, run_lab, write_intent_audit, write_cycle_report, or ingest_test_results.
"""
import ast
import os
import re
import subprocess
from datetime import date


# ROLE_WEIGHTS: the Planner's table from #100072, not derived from the archetype.
ROLE_WEIGHTS = {
    "plan_dispatcher": 2.0,
    "gate_checker": 2.0,
    "verdict_handler": 2.0,
    "agent_lifecycle": 2.0,
    "worktree_manager": 2.0,
    "plan_validator": 2.0,
    "plan_parser": 2.0,
    "notifier": 1.5,
    "config_loader": 1.5,
    "data_model": 1.5,
    "cache_manager": 1.5,
}

_EXCLUDED_PREFIXES = ("tests/", "knowledge/", "logs/", "receipts/", ".claude/")


def _module_from_path(file_path):
    """Derive module name from file path: 'src/scanner.py' -> 'src.scanner'."""
    p = file_path.replace("\\", "/")
    if p.endswith(".py"):
        p = p[:-3]
    return p.replace("/", ".")


def _check_import(source_text, target_module, target_name, caller_file):
    """
    Return (verified, path_loaded).
    verified: the source file's AST imports target_module (and for named-import form,
              the target's bare name or *).
    path_loaded: source file uses spec_from_file_location or runpy.
    """
    path_loaded = "spec_from_file_location" in source_text or "runpy" in source_text
    try:
        tree = ast.parse(source_text)
    except SyntaxError:
        return False, path_loaded

    # Derive caller's package for relative import resolution
    caller_parts = caller_file.replace("\\", "/").split("/")
    caller_pkg_parts = caller_parts[:-1]  # drop the file itself

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == target_module:
                    return True, path_loaded
                # 'import src.scanner' also matches target 'src.scanner'
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                mod = node.module or ""
                if mod == target_module:
                    # 'from target_module import name|*'
                    for alias in node.names:
                        if alias.name in ("*", target_name):
                            return True, path_loaded
                # 'from parent import leaf' where target_module == 'parent.leaf'
                parts = target_module.rsplit(".", 1)
                if len(parts) == 2 and mod == parts[0]:
                    for alias in node.names:
                        if alias.name == parts[1]:
                            return True, path_loaded
            else:
                # Relative import: resolve against caller's package
                level = node.level
                # Go up 'level - 1' from the package (level=1 means same package)
                up = level - 1
                pkg = caller_pkg_parts[:-up] if up > 0 else caller_pkg_parts
                if node.module:
                    resolved = ".".join(pkg + [node.module]) if pkg else node.module
                else:
                    resolved = ".".join(pkg)
                if resolved == target_module:
                    for alias in node.names:
                        if alias.name in ("*", target_name):
                            return True, path_loaded
                # Relative 'from . import leaf' matching 'parent.leaf'
                parts = target_module.rsplit(".", 1)
                if len(parts) == 2 and resolved == parts[0] and not node.module:
                    for alias in node.names:
                        if alias.name == parts[1]:
                            return True, path_loaded

    return False, path_loaded


def production_defs(checkout):
    """
    Return all FunctionDef/AsyncFunctionDef in production Python files at HEAD.
    Excludes files under tests/, knowledge/, logs/, receipts/, .claude/.
    Each entry: {file, name, lineno, end_lineno, def_line, docstring}.
    Files that fail to parse are listed with an error marker, not fatal.
    """
    result = subprocess.run(
        ["git", "ls-files", "--", "*.py"],
        cwd=checkout, capture_output=True, text=True,
    )
    files = [f for f in result.stdout.splitlines() if f]
    defs = []
    for file_path in files:
        # Exclude non-production paths
        if any(file_path.startswith(p) for p in _EXCLUDED_PREFIXES):
            continue
        abs_path = os.path.join(checkout, file_path)
        try:
            source = open(abs_path, encoding="utf-8", errors="replace").read()
            tree = ast.parse(source, filename=file_path)
        except Exception:
            continue
        lines = source.splitlines()
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            def_line = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
            docstring = None
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                raw = node.body[0].value.value.strip()
                docstring = raw.splitlines()[0] if raw else None
            defs.append({
                "file": file_path,
                "name": node.name,
                "lineno": node.lineno,
                "end_lineno": node.end_lineno,
                "def_line": def_line,
                "docstring": docstring,
            })
    return defs


def verified_inbound(conn, checkout, defs):
    """
    Return dict mapping 'file::name' -> verified inbound call count.
    Verified: cross-file call edge in chunk_dependencies whose caller's file,
    read at HEAD, imports the target's module. path_loaded edges are not counted
    as verified (but are tracked in path_loaded_counts separately).
    Only defs that appear in the DB (matched by file_path + name) are counted.
    """
    # Build a lookup: (file_path, name) -> key
    def_keys = {(d["file"], d["name"]): f"{d['file']}::{d['name']}" for d in defs}
    counts = {key: 0 for key in def_keys.values()}

    rows = conn.execute("""
        SELECT src_c.file_path AS caller_file,
               tgt_c.file_path AS target_file,
               tgt_c.name      AS target_name
          FROM chunk_dependencies d
          JOIN code_chunks tgt_c ON tgt_c.id = d.target_chunk_id
          JOIN code_chunks src_c ON src_c.id = d.source_chunk_id
         WHERE d.dependency_type = 'call'
           AND d.scope = 'cross_file'
    """).fetchall()

    # Cache source texts to avoid re-reading the same file repeatedly
    _source_cache = {}

    for caller_file, target_file, target_name in rows:
        key = def_keys.get((target_file, target_name))
        if key is None:
            continue
        if caller_file not in _source_cache:
            abs_path = os.path.join(checkout, caller_file)
            try:
                _source_cache[caller_file] = open(
                    abs_path, encoding="utf-8", errors="replace"
                ).read()
            except Exception:
                _source_cache[caller_file] = ""
        source = _source_cache[caller_file]
        target_module = _module_from_path(target_file)
        verified, _ = _check_import(source, target_module, target_name, caller_file)
        if verified:
            counts[key] += 1

    return counts


def survived(checkout, defs, today, conn=None):
    """
    Annotate defs with score_b fields: age_days, stable_commits, tests_bound, score_b.
    Uses 'git log -L <lineno>,<end_lineno>:<file>' range form (never :<name>:<file>).
    A def whose trace is its birth alone scores 0.
    If conn is provided, tests_bound is read from chunk_symbol_bindings; else 0.
    """
    today_date = date.fromisoformat(today)

    # Pre-fetch tests_bound from DB if available
    tests_bound_map = {}
    if conn is not None:
        for row in conn.execute("""
            SELECT c.file_path, c.name, COUNT(*) AS cnt
              FROM chunk_symbol_bindings b
              JOIN code_chunks c ON c.id = b.target_chunk_id
             WHERE b.binding_type = 'tests'
               AND b.target_chunk_id IS NOT NULL
             GROUP BY c.file_path, c.name
        """).fetchall():
            tests_bound_map[(row[0], row[1])] = row[2]

    sig_re = re.compile(r'^[-+]\s*(async )?def ')
    results = []
    for d in defs:
        file_path = d["file"]
        name = d["name"]
        lineno = d["lineno"]
        end_lineno = d["end_lineno"]

        spec = f"{lineno},{end_lineno}:{file_path}"
        proc = subprocess.run(
            ["git", "log", "-L", spec, "--format=%H %ad", "--date=short", "main"],
            cwd=checkout, capture_output=True, text=True,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            results.append({**d, "age_days": 0, "stable_commits": 0,
                            "tests_bound": 0, "score_b": 0})
            continue

        # Parse commits from git log -L output
        commits = []  # list of (date_str, is_stable)
        current_date = None
        current_hunk_lines = []
        for line in proc.stdout.splitlines():
            m = re.match(r'^([0-9a-f]{40}) (\d{4}-\d{2}-\d{2})$', line)
            if m:
                if current_date is not None:
                    sig_changed = any(
                        sig_re.match(h) and re.search(
                            r'def\s+' + re.escape(name) + r'\s*\(', h
                        )
                        for h in current_hunk_lines
                    )
                    commits.append((current_date, not sig_changed))
                current_date = m.group(2)
                current_hunk_lines = []
            elif line.startswith('+') or line.startswith('-'):
                current_hunk_lines.append(line)
        if current_date is not None:
            sig_changed = any(
                sig_re.match(h) and re.search(
                    r'def\s+' + re.escape(name) + r'\s*\(', h
                )
                for h in current_hunk_lines
            )
            commits.append((current_date, not sig_changed))

        if not commits:
            results.append({**d, "age_days": 0, "stable_commits": 0,
                            "tests_bound": 0, "score_b": 0})
            continue

        # Birth is the last commit in the log (oldest)
        birth_date_str = commits[-1][0]
        try:
            birth_date = date.fromisoformat(birth_date_str)
        except ValueError:
            birth_date = today_date
        age_days = (today_date - birth_date).days

        # stable_commits: commits excluding birth that have no signature change
        stable_commits = sum(1 for _, is_stable in commits[:-1] if is_stable)

        tests_bound = tests_bound_map.get((file_path, name), 0)
        score_b = age_days * (1 + tests_bound) * stable_commits

        results.append({**d, "age_days": age_days, "stable_commits": stable_commits,
                        "tests_bound": tests_bound, "score_b": score_b})
    return results


def rank(rows, definition):
    """
    Sort rows by score descending for the given definition; ties broken by
    'file::name' ascending. definition: 'a', 'b', or 'c'.
    """
    score_key = f"score_{definition}"
    return sorted(
        rows,
        key=lambda r: (-r.get(score_key, 0), f"{r['file']}::{r['name']}"),
    )


def precision_recall(ranked, reference, k):
    """
    Return (P@k, R@k) for the ranked list against reference set.
    ranked: list of dicts with 'file' and 'name'.
    reference: set of 'file::name' strings.
    """
    top_k = ranked[:k]
    hits = sum(1 for r in top_k if f"{r['file']}::{r['name']}" in reference)
    p = hits / k if k > 0 else 0.0
    r_val = hits / len(reference) if reference else 0.0
    return p, r_val


def entry(conn, checkout, row):
    """
    Build a 'what works' entry dict for one scored/ranked row.
    Fields: role, signature, verified_callers_count, verified_callers_sample,
            docstring, tests_bound_count, tests_bound_sample.
    """
    file_path = row["file"]
    name = row["name"]

    # Verified callers from chunk_dependencies — exclude module-level chunks
    # (whose name contains '/' because anvil stores them as file-path strings)
    callers = conn.execute("""
        SELECT DISTINCT src_c.file_path || '::' || src_c.name AS caller
          FROM chunk_dependencies d
          JOIN code_chunks src_c ON src_c.id = d.source_chunk_id
          JOIN code_chunks tgt_c ON tgt_c.id = d.target_chunk_id
         WHERE d.dependency_type = 'call'
           AND d.scope = 'cross_file'
           AND tgt_c.file_path = ?
           AND tgt_c.name = ?
           AND src_c.name NOT LIKE '%/%'
         ORDER BY caller
         LIMIT 3
    """, (file_path, name)).fetchall()
    callers_list = [r[0] for r in callers]
    verified_count = row.get("score_a", 0)

    # Test bindings
    test_rows = conn.execute("""
        SELECT DISTINCT b.symbol_name
          FROM chunk_symbol_bindings b
          JOIN code_chunks tgt ON tgt.id = b.target_chunk_id
         WHERE b.binding_type = 'tests'
           AND tgt.file_path = ?
           AND tgt.name = ?
         ORDER BY b.symbol_name
         LIMIT 2
    """, (file_path, name)).fetchall()
    test_sample = [r[0] for r in test_rows]
    tests_bound_count = row.get("tests_bound", 0)

    # Role from chunk_dependencies / code_chunks
    role_row = conn.execute(
        "SELECT functional_role FROM code_chunks WHERE file_path=? AND name=? LIMIT 1",
        (file_path, name),
    ).fetchone()
    role = role_row[0] if role_row else "utility"

    return {
        "file": file_path,
        "name": name,
        "role": role or "utility",
        "signature": row.get("def_line", f"def {name}(...)"),
        "verified_callers_count": verified_count,
        "verified_callers_sample": callers_list,
        "docstring": row.get("docstring") or "no docstring",
        "tests_bound_count": tests_bound_count,
        "tests_bound_sample": test_sample,
    }


def render_markdown(entries, meta):
    """Render entries as a markdown table."""
    lines = [
        f"# What Works — Definition ({meta.get('definition', 'c')})",
        f"Checkout: `{meta.get('checkout', '')}` | top-{meta.get('top_k', 20)}",
        "",
        "| # | file::name | role | signature | callers | docstring | tests |",
        "|---|------------|------|-----------|---------|-----------|-------|",
    ]
    for i, e in enumerate(entries, 1):
        callers = ", ".join(e.get("verified_callers_sample", []))
        tests = ", ".join(e.get("tests_bound_sample", []))
        fn_id = (f"{e['file']}::{e['name']}" if e.get("file") and e.get("name")
                 else e.get("name", ""))
        lines.append(
            f"| {i} | {fn_id} | {e['role']} "
            f"| `{e['signature']}` | {e['verified_callers_count']} ({callers}) "
            f"| {e['docstring']} | {e['tests_bound_count']} ({tests}) |"
        )
    return "\n".join(lines) + "\n"


def render_tsv(rows):
    """
    Render rows as TSV with 17 columns.
    Columns: rank, file, name, role, signature, score_a, score_b, score_c,
             age_days, stable_commits, tests_bound, verified_callers_count,
             caller_1, caller_2, caller_3, docstring, test_sample.
    """
    header = "\t".join([
        "rank", "file", "name", "role", "signature",
        "score_a", "score_b", "score_c",
        "age_days", "stable_commits", "tests_bound",
        "verified_callers_count", "caller_1", "caller_2", "caller_3",
        "docstring", "test_sample",
    ])
    lines = [header]
    for i, r in enumerate(rows, 1):
        callers = r.get("verified_callers_sample", [])
        tests = r.get("tests_bound_sample", [])
        lines.append("\t".join(str(x) for x in [
            i,
            r.get("file", ""),
            r.get("name", ""),
            r.get("role", ""),
            r.get("signature", ""),
            r.get("score_a", 0),
            r.get("score_b", 0),
            r.get("score_c", 0.0),
            r.get("age_days", 0),
            r.get("stable_commits", 0),
            r.get("tests_bound", 0),
            r.get("verified_callers_count", 0),
            callers[0] if len(callers) > 0 else "",
            callers[1] if len(callers) > 1 else "",
            callers[2] if len(callers) > 2 else "",
            r.get("docstring") or "no docstring",
            tests[0] if tests else "",
        ]))
    return "\n".join(lines) + "\n"
