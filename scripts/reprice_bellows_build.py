"""WALK-0 INSTRUMENT (Planner, 2026-09-09, session d04ebd33) for diagnostic-bellows-anvil-reprice - thread 255.
The DEV step extends this file per the plan's Item 2 (argparse: --checkout/--tmp for build; --checkout/--db/--tsv/--control
for analyze; the evidence column; the temp-dir assert). READ-ONLY over bellows. Writers never called, by name:
run_cycle, run_lab, write_intent_audit, write_cycle_report, ingest_test_results.
--- original walk-0 docstring ---
Walk-0 pin: build a scratch anvil DB over the bellows checkout (READ-ONLY over bellows).
Writers forbidden by name: run_lab, write_intent_audit, write_cycle_report, ingest_test_results (runs pytest).
Enters at the stage functions, not run_cycle, because run_cycle's Stage 4 (run_lab) writes into the target repo."""
import sys, os, sqlite3, time, json
sys.path.insert(0, "/Users/marklehn/Developer/anvil")
OUT = os.path.dirname(os.path.abspath(__file__))
import src.config as cfg
cfg.ANVIL_ROOT = OUT; cfg.ANVIL_DB_PATH = os.path.join(OUT, "anvil-scratch.db")
cfg.SCAN_TARGETS["bellows"]["path"] = "/Users/marklehn/Developer/bellows"
import src.scanner as sc; sc.ANVIL_ROOT = OUT; sc.ANVIL_DB_PATH = cfg.ANVIL_DB_PATH
from src.db import init_db
from src.extractor import extract_project
from src.classifier import classify_project
from src.scorer import score_project
from src.cycle import seed_archetype_data
from src.classifier_registry import get_archetype
if os.path.exists(cfg.ANVIL_DB_PATH): os.remove(cfg.ANVIL_DB_PATH)
conn = sqlite3.connect(cfg.ANVIL_DB_PATH); init_db(conn)
arch = get_archetype("daemon"); seed_archetype_data(conn, arch)
t=time.time(); r1 = sc.scan_project(conn, "bellows"); t1=time.time()-t
t=time.time(); r2 = extract_project(conn, "bellows", 1); t2=time.time()-t
r3 = classify_project(conn, "bellows")
t=time.time(); r4 = score_project(conn, "bellows", 1, arch); t3=time.time()-t
conn.commit()
def q(sql,*a): return conn.execute(sql,a).fetchall()
pid = q("select id from projects where name='bellows'")[0][0]
print("scan:", {k:v for k,v in r1.items() if not isinstance(v,(list,dict))}, f"{t1:.1f}s")
print("extract:", {k:v for k,v in r2.items() if not isinstance(v,(list,dict))}, f"{t2:.1f}s")
print("classify:", {k:v for k,v in r3.items() if not isinstance(v,(list,dict))})
print("score:", {k:v for k,v in r4.items() if not isinstance(v,(list,dict))}, f"{t3:.1f}s")
print("chunks by type:", q("select chunk_type,count(*) from code_chunks where project_id=? group by 1",pid))
print("files registered:", q("select count(distinct file_path) from code_chunks where project_id=?",pid))
print("deps by type/scope:", q("select dependency_type,scope,count(*) from chunk_dependencies d join code_chunks c on c.id=d.source_chunk_id where c.project_id=? group by 1,2",pid))
print("tests bindings w/ target:", q("select count(*), count(target_chunk_id) from chunk_symbol_bindings b join code_chunks c on c.id=b.chunk_id where c.project_id=? and binding_type='tests'",pid))
print("coverage dist (prod fn/method):", q("select h.coverage_score, count(*) from health_scores h join code_chunks c on c.id=h.chunk_id where c.project_id=? and c.chunk_type in ('function','method') and c.file_path not like 'tests/%' group by 1",pid))
print("roles:", q("select functional_role,count(*) from code_chunks where project_id=? group by 1 order by 2 desc",pid)[:8])
print("top inbound (prod):", q("""select c.file_path||'::'||c.name, count(*) n from chunk_dependencies d join code_chunks c on c.id=d.target_chunk_id
 where c.project_id=? and d.scope='cross_file' and c.chunk_type in ('function','method','class') group by 1 order by n desc limit 12""",pid))
