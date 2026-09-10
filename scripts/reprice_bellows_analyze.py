"""WALK-0 INSTRUMENT (Planner, 2026-09-09, session d04ebd33) for diagnostic-bellows-anvil-reprice - thread 255.
The DEV step extends this file per the plan's Item 2 (argparse: --checkout/--tmp for build; --checkout/--db/--tsv/--control
for analyze; the evidence column; the temp-dir assert). READ-ONLY over bellows. Writers never called, by name:
run_cycle, run_lab, write_intent_audit, write_cycle_report, ingest_test_results.
--- original walk-0 docstring ---
Walk-0 pin: dependents-untouched yield over the last ten bellows DEV commits, tests-for, and the stable/bound/reused ranking.
READ-ONLY over bellows (git show / git log only). Reads the scratch DB build.py wrote."""
import sys, os, sqlite3, subprocess, ast, re, collections
OUT = os.path.dirname(os.path.abspath(__file__)); REPO = "/Users/marklehn/Developer/bellows"
conn = sqlite3.connect(os.path.join(OUT, "anvil-scratch.db"))
def q(sql,*a): return conn.execute(sql,a).fetchall()
def git(*a): return subprocess.run(["git","-C",REPO,*a],capture_output=True,text=True,check=True).stdout
pid = q("select id from projects where name='bellows'")[0][0]
log = git("log","--format=%h%x09%ad%x09%s","--date=short","-120","main")
devs=[]
for line in log.splitlines():
    h,d,s = line.split("\t",2)
    if re.match(r"^(feat|fix)\(", s) and "[1000" in s and not re.search(r"dev-log|qa\(|wrap", s, re.I):
        devs.append((h,d,s))
devs = devs[:10]
def touched(sha):
    """(files_changed, {(file, qualname)}) from the post-image AST intersected with -U0 hunks."""
    diff = git("show","--format=","-U0",sha)
    files=set(); fn=None; hunks=collections.defaultdict(list)
    for l in diff.splitlines():
        m=re.match(r"^diff --git a/(\S+) b/(\S+)",l)
        if m: fn=m.group(2); files.add(fn); continue
        m=re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@",l)
        if m and fn: a=int(m.group(1)); n=int(m.group(2) or 1); hunks[fn].append((a,max(a,a+n-1)))
    out=set()
    for f,ranges in hunks.items():
        if not f.endswith(".py"): continue
        try: src=git("show",f"{sha}:{f}")
        except subprocess.CalledProcessError: continue
        try: tree=ast.parse(src)
        except SyntaxError: continue
        def walk(node,prefix=""):
            for ch in ast.iter_child_nodes(node):
                if isinstance(ch,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                    qn=prefix+ch.name; s,e=ch.lineno,ch.end_lineno
                    if any(not(b<s or a>e) for a,b in ranges): out.add((f,qn,ch.name))
                    walk(ch,qn+".")
        walk(tree)
    return files,out
later_index={}  # (file, name) -> first later sha touching it
all_shas=[l.split("\t")[0] for l in log.splitlines()]
def chunk_ids(f,name):
    return [r[0] for r in q("select id from code_chunks where project_id=? and file_path=? and name=? and chunk_type in ('function','method','class')",pid,f,name)]
print("SAMPLE (newest first):")
for h,d,s in devs: print(f"  {h} {d} {s[:90]}")
rows=[]
for i,(h,d,s) in enumerate(devs):
    files,tset = touched(h)
    ids=[]; prod=[(f,qn,n) for f,qn,n in tset if not f.startswith("tests/")]
    for f,qn,n in prod: ids += chunk_ids(f,n)
    deps=set()
    for cid in ids:
        for (sf,sn,st) in q("select c.file_path,c.name,c.chunk_type from chunk_dependencies dd join code_chunks c on c.id=dd.source_chunk_id where dd.target_chunk_id=? and dd.scope='cross_file'",cid):
            deps.add((sf,sn))
    untouched={(sf,sn) for sf,sn in deps if sf not in files}
    # later-fix signal: any LATER commit (newer than h, i.e. earlier in the log) whose touched set hits an untouched dependent
    newer=[x for x in all_shas[:all_shas.index(h)]]
    hit=set()
    for nh in newer:
        _,t2=touched(nh)
        for f,qn,n in t2:
            if (f,n) in untouched or (f,qn) in untouched: hit.add((f,n,nh))
    tests_for=[]
    for cid in ids:
        tests_for.append(q("select count(*) from chunk_symbol_bindings where target_chunk_id=? and binding_type='tests'",cid)[0][0])
    unbound=sum(1 for t in tests_for if t==0)
    rows.append((h,len(files),len(prod),len(ids),len(deps),len(untouched),len({(a,b) for a,b,_ in hit}),unbound))
    print(f"\n{h} files={len(files)} touched_prod_defs={len(prod)} matched_chunks={len(ids)} cross_file_dependents={len(deps)} UNTOUCHED={len(untouched)} later_touched={len({(a,b) for a,b,_ in hit})} touched_defs_with_zero_test_binding={unbound}/{len(ids)}")
    for x in sorted(untouched)[:8]: print("    untouched:",x)
    for x in sorted(hit)[:6]: print("    LATER-TOUCHED:",x)
print("\nTABLE sha files prod_defs chunks deps untouched later_touched unbound")
for r in rows: print("  "+" ".join(map(str,r)))
print("\nSTABLE/BOUND/REUSED top 20 (prod fn/method/class; volatility<=0.2, coverage_score<1.0 i.e. some test binding, ordered by cross-file inbound):")
for r in q("""select c.file_path||'::'||c.name, c.functional_role, round(h.volatility_score,2), h.coverage_score, count(d.id) inbound
 from code_chunks c join health_scores h on h.chunk_id=c.id left join chunk_dependencies d on d.target_chunk_id=c.id and d.scope='cross_file'
 where c.project_id=? and c.chunk_type in ('function','method','class') and c.file_path not like 'tests/%' and h.volatility_score<=0.2 and h.coverage_score<1.0
 group by c.id order by inbound desc limit 20""",pid): print("  ",r)
print("\nclone pairs (prod only):", q("select count(*) from chunk_similarities s join code_chunks a on a.id=s.chunk_a_id join code_chunks b on b.id=s.chunk_b_id where a.project_id=? and a.file_path not like 'tests/%' and b.file_path not like 'tests/%'",pid) if q("select count(*) from pragma_table_info('chunk_similarities') where name='chunk_a_id'")[0][0] else "col names differ")
