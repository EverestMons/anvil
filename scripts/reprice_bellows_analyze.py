"""WALK-0 INSTRUMENT (Planner, 2026-09-09, session d04ebd33) for diagnostic-bellows-anvil-reprice - thread 255.
The DEV step extends this file per the plan's Item 2 (argparse: --checkout/--tmp for build; --checkout/--db/--tsv/--control
for analyze; the evidence column; the temp-dir assert). READ-ONLY over bellows. Writers never called, by name:
run_cycle, run_lab, write_intent_audit, write_cycle_report, ingest_test_results.
--- original walk-0 docstring ---
Walk-0 pin: dependents-untouched yield over the last ten bellows DEV commits, tests-for, and the stable/bound/reused ranking.
READ-ONLY over bellows (git show / git log only). Reads the scratch DB build.py wrote."""
import sys, os, sqlite3, subprocess, ast, re, collections, csv, argparse

ANVIL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ANVIL_ROOT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkout", default="/Users/marklehn/Developer/bellows")
    ap.add_argument("--db", default=None, help="Path to scratch DB (must be under /tmp or $TMPDIR)")
    ap.add_argument("--tsv", default=None, help="Output TSV path")
    ap.add_argument("--control", nargs="*", default=[], help="Additional SHAs to analyze (positive controls)")
    args = ap.parse_args()

    REPO = args.checkout
    db_path = args.db or os.path.join(os.environ.get("TMPDIR", "/tmp"), "anvil-scratch.db")

    # Assert DB path is under a temp dir
    allowed = ["/tmp", os.environ.get("TMPDIR", "/tmp"), "/private/tmp"]
    if not any(os.path.realpath(db_path).startswith(os.path.realpath(a)) for a in allowed if a):
        raise RuntimeError(f"DB path {db_path!r} is not under a temp dir — refusing to read")

    conn = sqlite3.connect(db_path)

    def q(sql, *a): return conn.execute(sql, a).fetchall()
    def git(*a): return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, check=True).stdout

    pid = q("select id from projects where name='bellows'")[0][0]
    log = git("log", "--format=%h%x09%ad%x09%s", "--date=short", "-120", "main")
    devs = []
    for line in log.splitlines():
        parts = line.split("\t", 2)
        if len(parts) < 3:
            continue
        h, d, s = parts
        if re.match(r"^(feat|fix)\(", s) and "[1000" in s and not re.search(r"dev-log|qa\(|wrap", s, re.I):
            devs.append((h, d, s))
    devs = devs[:10]

    def touched(sha):
        """(files_changed, {(file, qualname, bare_name)}) from post-image AST intersected with -U0 hunks."""
        try:
            diff = git("show", "--format=", "-U0", sha)
        except subprocess.CalledProcessError:
            return set(), set()
        files = set()
        fn = None
        hunks = collections.defaultdict(list)
        for l in diff.splitlines():
            m = re.match(r"^diff --git a/(\S+) b/(\S+)", l)
            if m:
                fn = m.group(2); files.add(fn); continue
            m = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", l)
            if m and fn:
                a = int(m.group(1)); n = int(m.group(2) or 1)
                hunks[fn].append((a, max(a, a + n - 1)))
        out = set()
        for f, ranges in hunks.items():
            if not f.endswith(".py"):
                continue
            try:
                src = git("show", f"{sha}:{f}")
            except subprocess.CalledProcessError:
                continue
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            def walk(node, prefix=""):
                for ch in ast.iter_child_nodes(node):
                    if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        qn = prefix + ch.name; s, e = ch.lineno, ch.end_lineno
                        if any(not (b < s or a > e) for a, b in ranges):
                            out.add((f, qn, ch.name))
                        walk(ch, qn + ".")
            walk(tree)
        return files, out

    all_shas = [l.split("\t")[0] for l in log.splitlines() if l.strip()]

    def chunk_ids(f, name):
        return [r[0] for r in q(
            "select id from code_chunks where project_id=? and file_path=? and name=? and chunk_type in ('function','method','class')",
            pid, f, name)]

    # Collect evidence for later-touched classification
    def classify_later(sha, dep_file, dep_name, newer_sha):
        """Classify a later-touched dependent: hub/planned/new-test/MISS."""
        try:
            subj = git("log", "--format=%s", "-1", newer_sha).strip()
        except Exception:
            subj = ""
        if dep_name == "run_plan" or dep_file == "bellows.py":
            return "hub", subj
        if dep_file.startswith("tests/") and "test" in dep_name.lower():
            return "new-test", subj
        # Check if newer commit's own plan or QA record mentions the dep
        if re.search(r"consumer|sibling|dependent|untouched", subj, re.I):
            return "planned", subj
        return "MISS", subj

    tsv_rows = []
    print("SAMPLE (newest first):")
    for h, d, s in devs:
        print(f"  {h} {d} {s[:90]}")

    rows = []
    all_commits = list(devs) + [(sha, "", "") for sha in args.control]

    for i, (h, d, s) in enumerate(all_commits):
        is_control = i >= len(devs)
        files, tset = touched(h)
        prod = [(f, qn, n) for f, qn, n in tset if not f.startswith("tests/")]
        ids = []
        for f, qn, n in prod:
            ids += chunk_ids(f, n)
        deps = set()
        for cid in ids:
            for (sf, sn, st) in q(
                "select c.file_path,c.name,c.chunk_type from chunk_dependencies dd join code_chunks c on c.id=dd.source_chunk_id where dd.target_chunk_id=? and dd.scope='cross_file'",
                cid
            ):
                deps.add((sf, sn))
        untouched = {(sf, sn) for sf, sn in deps if sf not in files}
        newer = [x for x in all_shas[:all_shas.index(h)] if all_shas.index(h) < len(all_shas)] if h in all_shas else []
        hit_map = {}  # (file, name) -> (newer_sha, class, evidence)
        for nh in newer:
            _, t2 = touched(nh)
            for f2, qn2, n2 in t2:
                key = (f2, n2)
                if key in untouched and key not in hit_map:
                    cls, ev = classify_later(h, f2, n2, nh)
                    hit_map[key] = (nh, cls, ev)
        tests_for = []
        for cid in ids:
            tests_for.append(q("select count(*) from chunk_symbol_bindings where target_chunk_id=? and binding_type='tests'", cid)[0][0])
        unbound = sum(1 for t in tests_for if t == 0)
        later_touched_count = len(hit_map)
        rows.append((h, len(files), len(prod), len(ids), len(deps), len(untouched), later_touched_count, unbound))

        label = "[CONTROL] " if is_control else ""
        print(f"\n{label}{h} files={len(files)} touched_prod_defs={len(prod)} matched_chunks={len(ids)} "
              f"cross_file_dependents={len(deps)} UNTOUCHED={len(untouched)} "
              f"later_touched={later_touched_count} touched_defs_with_zero_test_binding={unbound}/{len(ids)}")
        for x in sorted(untouched)[:8]:
            print("    untouched:", x)
        for key, (nh, cls, ev) in sorted(hit_map.items())[:6]:
            print(f"    LATER-TOUCHED: {key} sha={nh} class={cls}")

        # Accumulate TSV rows
        for dep_file, dep_name in untouched:
            if (dep_file, dep_name) in hit_map:
                later_sha, cls, ev = hit_map[(dep_file, dep_name)]
            else:
                later_sha, cls, ev = "", "", ""
            tsv_rows.append({
                "sha": h,
                "file": prod[0][0] if prod else "",
                "name": prod[0][2] if prod else "",
                "dependent_file": dep_file,
                "dependent_name": dep_name,
                "later_sha": later_sha,
                "class": cls,
                "evidence": ev[:200] if ev else "",
            })

    print("\nTABLE sha files prod_defs chunks deps untouched later_touched unbound")
    for r in rows:
        print("  " + " ".join(map(str, r)))

    print("\nSTABLE/BOUND/REUSED top 20 (prod fn/method/class; volatility<=0.2, coverage_score<1.0; ordered by cross-file inbound):")
    for r in q("""select c.file_path||'::'||c.name, c.functional_role, round(h.volatility_score,2), h.coverage_score, count(d.id) inbound
 from code_chunks c join health_scores h on h.chunk_id=c.id left join chunk_dependencies d on d.target_chunk_id=c.id and d.scope='cross_file'
 where c.project_id=? and c.chunk_type in ('function','method','class') and c.file_path not like 'tests/%' and h.volatility_score<=0.2 and h.coverage_score<1.0
 group by c.id order by inbound desc limit 20""", pid):
        print("  ", r)

    print("\nSTABLE/BOUND/REUSED top 20 (excluding non-source dirs):")
    excl = ("knowledge/", "logs/", "receipts/", ".claude/")
    for r in q("""select c.file_path||'::'||c.name, c.functional_role, round(h.volatility_score,2), h.coverage_score, count(d.id) inbound
 from code_chunks c join health_scores h on h.chunk_id=c.id left join chunk_dependencies d on d.target_chunk_id=c.id and d.scope='cross_file'
 where c.project_id=? and c.chunk_type in ('function','method','class') and c.file_path not like 'tests/%'
   and c.file_path not like 'knowledge/%' and c.file_path not like 'logs/%'
   and c.file_path not like 'receipts/%' and c.file_path not like '.claude/%'
   and c.file_path not like 'tools/%census%'
   and h.volatility_score<=0.2 and h.coverage_score<1.0
 group by c.id order by inbound desc limit 20""", pid):
        print("  ", r)

    prod_clone = q("""select count(*) from chunk_similarities s
 join code_chunks a on a.id=s.chunk_a_id join code_chunks b on b.id=s.chunk_b_id
 where a.project_id=? and a.file_path not like 'tests/%' and b.file_path not like 'tests/%'""", pid)
    print("\nclone pairs (prod only):", prod_clone)

    print("\nclone pairs detail (prod only, first 25):")
    for r in q("""select a.file_path||'::'||a.name, b.file_path||'::'||b.name, round(s.similarity_score,3)
 from chunk_similarities s
 join code_chunks a on a.id=s.chunk_a_id join code_chunks b on b.id=s.chunk_b_id
 where a.project_id=? and a.file_path not like 'tests/%' and b.file_path not like 'tests/%'
 order by s.similarity_score desc limit 25""", pid):
        print("  ", r)

    print("\nTop 10 complexity hotspots (prod fn/method by composite desc):")
    for r in q("""select c.file_path||'::'||c.name, round(h.composite_score,3), round(h.complexity_score,3)
 from code_chunks c join health_scores h on h.chunk_id=c.id
 where c.project_id=? and c.chunk_type in ('function','method') and c.file_path not like 'tests/%'
 order by h.composite_score desc limit 10""", pid):
        print("  ", r)

    # Q3 resolver block
    print("\nQ3 RESOLVER BLOCK (src/extractor.py 'Resolve call dependencies'):")
    try:
        extractor_path = os.path.join(ANVIL_ROOT, "src", "extractor.py")
        with open(extractor_path) as f:
            lines = f.readlines()
        in_resolve = False
        for i, line in enumerate(lines, 1):
            if "Resolve call dependencies" in line or (in_resolve and "by_name" in line and "get(callee_name" in line):
                in_resolve = True
            if in_resolve:
                print(f"  {i}: {line}", end="")
                if in_resolve and i > 5 and ("break" in line or "continue" in line or line.strip() == ""):
                    if "break" in line:
                        break
    except Exception as e:
        print(f"  ERROR reading extractor: {e}")

    # STANDARD_GATES check
    print("\nQ2 STANDARD_GATES chunk check:")
    sg = q("select id, file_path, name, chunk_type from code_chunks where project_id=? and name='STANDARD_GATES'", pid)
    print("  STANDARD_GATES rows:", sg)

    # Write TSV
    if args.tsv and tsv_rows:
        with open(args.tsv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["sha", "file", "name", "dependent_file", "dependent_name", "later_sha", "class", "evidence"], delimiter="\t")
            w.writeheader()
            w.writerows(tsv_rows)
        print(f"\nTSV written to: {args.tsv}")


if __name__ == "__main__":
    main()
