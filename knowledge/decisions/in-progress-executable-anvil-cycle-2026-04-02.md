# Anvil — Full Cycle Against Invoice-Pulse
**Date:** 2026-04-02 | **Tier:** Small | **Execution:** Step 1 (DEV)
**Priority:** 3

## How to Run This Plan

```
Read the plan at anvil/knowledge/decisions/executable-anvil-cycle-2026-04-02.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---
---

## STEP 1 — ANVIL DEVELOPER

---

> **FIRST — claim this plan:** `import shutil; shutil.move("knowledge/decisions/executable-anvil-cycle-2026-04-02.md", "knowledge/decisions/in-progress-executable-anvil-cycle-2026-04-02.md")`. **Run a full anvil cycle against invoice-pulse: SCAN → EXTRACT → CLASSIFY → PROVENANCE → SCORE → LAB.**
>
> **Step A — Pull latest invoice-pulse.** `cd /Users/marklehn/Desktop/GitHub/invoice-pulse && git pull --rebase origin main`. Anvil scans the live repo, so it needs to be current.
>
> **Step B — Run full cycle.** `cd /Users/marklehn/Desktop/GitHub/anvil && python3 -c "
import sqlite3, json
from src.cycle import run_cycle
from src.db import init_db
conn = sqlite3.connect('anvil.db')
init_db(conn)
result = run_cycle(conn, 'invoice-pulse')
conn.commit()
print(json.dumps(result, indent=2, default=str))
conn.close()
"`. Report: cycle_id, files scanned, chunks extracted, chunks scored, findings count, elapsed time. If any stage errors, report the error and continue.
>
> **Step C — Cycle summary.** `python3 -c "
import sqlite3, json
from src.cycle import get_cycle_summary
from src.db import init_db
conn = sqlite3.connect('anvil.db')
init_db(conn)
cycle_id = conn.execute('SELECT MAX(cycle_number) FROM cycle_reports WHERE project_id = (SELECT id FROM projects WHERE name = ?)', ('invoice-pulse',)).fetchone()[0]
summary = get_cycle_summary(conn, 'invoice-pulse', cycle_id)
print(json.dumps(summary, indent=2, default=str))
conn.close()
"`. Report: health score distribution (high/medium/low risk), top 5 riskiest chunks, avg/min/max composite scores.
>
> **Step D — Compare with prior cycle (if exists).** If cycle_id > 1: `python3 -c "
import sqlite3, json
from src.cycle import compare_cycles
from src.db import init_db
conn = sqlite3.connect('anvil.db')
init_db(conn)
cycle_id = conn.execute('SELECT MAX(cycle_number) FROM cycle_reports WHERE project_id = (SELECT id FROM projects WHERE name = ?)', ('invoice-pulse',)).fetchone()[0]
if cycle_id > 1:
    delta = compare_cycles(conn, 'invoice-pulse', cycle_id - 1, cycle_id)
    print(json.dumps(delta, indent=2, default=str))
else:
    print('First cycle — no comparison available')
conn.close()
"`. Report: new/removed chunks, improved/degraded scores, findings delta.
>
> **Step E — Generate planner constraints.** `python3 -c "
import sqlite3
from src.lab import generate_planner_constraints
from src.db import init_db
conn = sqlite3.connect('anvil.db')
init_db(conn)
cycle_id = conn.execute('SELECT MAX(cycle_number) FROM cycle_reports WHERE project_id = (SELECT id FROM projects WHERE name = ?)', ('invoice-pulse',)).fetchone()[0]
constraints = generate_planner_constraints(conn, 'invoice-pulse', cycle_id)
print(f'Generated {len(constraints)} planner constraints')
for c in constraints[:10]:
    print(f'  {c}')
conn.commit()
conn.close()
"`.
>
> **Step F — Commit + push.** `git --no-pager add -A && git commit -m "chore: anvil cycle $(date +%Y-%m-%d) against invoice-pulse" && git push origin main`.
>
> Report full cycle results. Move to Done: `import shutil; shutil.move("knowledge/decisions/in-progress-executable-anvil-cycle-2026-04-02.md", "knowledge/decisions/Done/executable-anvil-cycle-2026-04-02.md")`.
>
> **STOP. Do NOT proceed further.**
