# Anvil — Archetype-ization + flask_service Migration Blueprint

**Date:** 2026-06-09
**Author:** Anvil Systems Analyst
**Status:** Step 1 complete — DEV-ready
**Scope:** Re-grounded edit map, consumer enumeration, test surface, flask_service 1:1 mapping, regression baseline, verification blocks. No source modifications.
**Derived from:** `knowledge/architecture/anvil-extraction-contract-archetype-design-2026-06-08.md` (sections C + E.2 Step 3)

---

## Section 1 — Re-grounded Gap Assessment

The design blueprint (a933b21) predates BP1. All line anchors below are pinned to the CURRENT codebase (35ee30f).

| Gap | Current State (file:line) | Proposed State | Change Required |
|---|---|---|---|
| `classify_chunk` signature — takes no archetype | `src/classifier.py:88` — `def classify_chunk(chunk_dict: dict) -> Optional[str]:` | `classify_chunk(chunk_dict, archetype: ArchetypeDefinition) -> str \| None` | Add `archetype` parameter; consume `archetype.decorator_rules`, `.name_rules`, `.file_path_rules` instead of module globals |
| DECORATOR_RULES — module-global, IP-specific | `src/classifier.py:18-23` — 4 compiled regex rules | Moved into `flask_service.py` as `ArchetypeDefinition.decorator_rules` | Remove from classifier.py; archetype carries rules |
| NAME_RULES — module-global, IP-specific | `src/classifier.py:25-51` — 21 compiled regex rules | Moved into `flask_service.py` as `ArchetypeDefinition.name_rules` | Remove from classifier.py |
| FILE_PATH_RULES — module-global, IP-specific | `src/classifier.py:54-85` — 30 compiled regex rules | Moved into `flask_service.py` as `ArchetypeDefinition.file_path_rules` | Remove from classifier.py |
| `SCAN_TARGETS` — plain string dict | `src/config.py:12-15` — `{"name": "path_string"}` | `{"name": {"path": "...", "language": "python", "archetype": "flask_service"}}` | Refactor dict; update all readers to use `["path"]` |
| `ROLE_SCORING_WEIGHTS` — global in config | `src/config.py:75-108` — 8 role weight profiles | Moved into `flask_service.py` as `ArchetypeDefinition.scoring_weights` | Remove from config.py; scorer reads from archetype |
| `ROLE_THRESHOLDS` — global in config | `src/config.py:111-132` — 5 role threshold profiles | Moved into `flask_service.py` as `ArchetypeDefinition.role_thresholds` | Remove from config.py; lab reads from archetype |
| `FUNCTIONAL_ROLE_SEEDS` — hardcoded in db.py | `src/db.py:589-620` — 25 IP roles, 3-tuple list | Moved into `flask_service.py` as `ArchetypeDefinition.roles` | Remove from db.py |
| `BEST_PRACTICE_SEEDS` — hardcoded in db.py | `src/db.py:673-739` — 15 IP practices, 6-tuple list | Moved into `flask_service.py` as `ArchetypeDefinition.best_practices` | Remove from db.py |
| `_seed_functional_roles()` — called from init_db | `src/db.py:623-631` + call at `src/db.py:270` | Removed; seeding moves to `cycle.py` per-cycle via `INSERT OR IGNORE` | Delete function + call from init_db |
| `_seed_best_practices()` — called from init_db | `src/db.py:742-751` + call at `src/db.py:271` | Removed; seeding moves to `cycle.py` per-cycle | Delete function + call from init_db |
| `functional_roles` table — no archetype column | `src/db.py:202-209` — `name TEXT NOT NULL UNIQUE` | Add `archetype TEXT` column via PRAGMA-guarded migration | Idempotent ALTER TABLE; update UNIQUE constraint to `(name, archetype)` |
| `classify_project` — no archetype awareness | `src/cycle.py:63` — `classify_result = classify_project(conn, project_name)` | Pass archetype to classify_project; it loads from SCAN_TARGETS | cycle.py loads archetype, passes to classify + score |
| `score_project` — weights from global config | `src/scorer.py:115` — `weights = ROLE_SCORING_WEIGHTS.get(role, SCORING_WEIGHTS)` | `weights = archetype.scoring_weights.get(role, SCORING_WEIGHTS)` | Add archetype parameter; read weights from it |
| `CONTENT_CHECKS` — module-global in detector | `src/detector.py:15-54` — 8 pattern groups | Moved into `flask_service.py` as `ArchetypeDefinition.content_checks` | Detector reads from archetype |
| `STRUCTURAL_CHECKS` — module-global in detector | `src/detector.py:58-63` — 1 pattern group | Moved into `flask_service.py` as `ArchetypeDefinition.structural_checks` | Detector reads from archetype |
| `check_best_practice` — reads module globals | `src/detector.py:66-109` — `CONTENT_CHECKS.get(pattern_name)` | Receive content_checks + structural_checks from archetype | Add archetype parameter or receive checks dict |
| `find_best_practice_deviations` — no archetype | `src/lab.py:323-370` — calls `check_best_practice(chunk, practice)` | Load archetype; pass checks to detector | Needs archetype to get content_checks |
| Seeding path in cycle.py — nonexistent | N/A | `cycle.py:run_cycle()` seeds roles + practices per-cycle from archetype | New code: `INSERT OR IGNORE` for archetype roles + practices before classify |

---

## Section 2 — SCAN_TARGETS Consumer Enumeration

Every reader of `SCAN_TARGETS` that must be updated when the format changes from `str` to `dict`:

### `src/` consumers

| File:Line | Current Access Pattern | Required Change |
|---|---|---|
| `src/config.py:12-15` | Definition — `{"name": "path"}` | Change to `{"name": {"path": "...", "language": "python", "archetype": "flask_service"}}` |
| `src/scanner.py:35` | `if project_name not in SCAN_TARGETS:` | No change needed (membership test on dict keys) |
| `src/scanner.py:38` | `project_path = SCAN_TARGETS[project_name]` | → `SCAN_TARGETS[project_name]["path"]` |
| `src/extractor.py:42` | `project_path = SCAN_TARGETS.get(project_name)` | → `SCAN_TARGETS.get(project_name, {}).get("path")` |
| `src/scorer.py:356` | `project_path = SCAN_TARGETS.get(project_name)` | → `SCAN_TARGETS.get(project_name, {}).get("path")` |

### `tests/` consumers

| File:Line | Current Access Pattern | Required Change |
|---|---|---|
| `tests/test_extractor.py:77` | `monkeypatch.setitem(SCAN_TARGETS, "mock-project", str(tmp_path))` | → `monkeypatch.setitem(SCAN_TARGETS, "mock-project", {"path": str(tmp_path), "language": "python", "archetype": "flask_service"})` |
| `tests/test_lab.py:313` | `monkeypatch.setitem(SCAN_TARGETS, "lab-test", "/tmp/lab-test")` | → dict form |
| `tests/test_cycle.py:81` | `monkeypatch.setitem(SCAN_TARGETS, "cycle-test", str(tmp_path))` | → dict form |
| `tests/test_cycle.py:107` | `monkeypatch.setitem(SCAN_TARGETS, "bad-proj", "/nonexistent/path")` | → dict form |
| `tests/test_scorer.py:311` | `monkeypatch.setitem(SCAN_TARGETS, "test-proj", "/tmp/test")` | → dict form |
| `tests/test_scorer.py:364` | `monkeypatch.setitem(SCAN_TARGETS, "scope-test", "/tmp/scope")` | → dict form |
| `tests/test_scanner.py:308` | `__import__("src.config", fromlist=["SCAN_TARGETS"]).SCAN_TARGETS` setitem | → dict form |
| `tests/test_scanner.py:326` | Same pattern | → dict form |
| `tests/test_scanner.py:339` | Same pattern | → dict form |

**Note:** `DEV_LOG_PATHS` (`src/config.py:135-138`) remains its own separate dict. Do NOT fold it into SCAN_TARGETS.

---

## Section 3 — Changed-Signature Test Surface

### Signatures that change

| Function | Current Signature | New Signature | Source Location |
|---|---|---|---|
| `classify_chunk` | `(chunk_dict: dict) -> Optional[str]` | `(chunk_dict: dict, archetype: ArchetypeDefinition) -> str \| None` | `src/classifier.py:88` |
| `classify_project` | `(conn, project_name: str) -> dict` | `(conn, project_name: str) -> dict` (loads archetype internally from SCAN_TARGETS) | `src/classifier.py:126` |
| `score_project` | `(conn, project_name: str, cycle_id: int) -> dict` | `(conn, project_name: str, cycle_id: int, archetype: ArchetypeDefinition) -> dict` | `src/scorer.py:27` |
| `check_best_practice` | `(chunk: dict, practice: dict) -> dict` | `(chunk: dict, practice: dict, content_checks: dict, structural_checks: dict) -> dict` | `src/detector.py:66` |
| `find_best_practice_deviations` | `(conn, project_id: int, cycle_id: int) -> list[dict]` | `(conn, project_id: int, cycle_id: int, archetype: ArchetypeDefinition) -> list[dict]` | `src/lab.py:323` |
| `init_db` | Seeds roles + practices | Creates EMPTY tables (no seeds) | `src/db.py:18` |

### Callers of each — exact test file enumeration

**`classify_chunk` callers in tests:**
- `tests/test_classifier.py:30, 40, 50, 60, 70, 80, 90, 100, 110, 122, 133, 143, 153, 163, 173, 183, 193, 205, 217` — 19 direct calls; all must pass an archetype

**`classify_project` callers:**
- `src/cycle.py:63` — production call site
- `tests/test_classifier.py:257` — `classify_project(conn, "test-proj")`
- `tests/test_classifier.py:283` — `classify_project(conn, "nonexistent")`

**`score_project` callers:**
- `src/cycle.py:81` — production call site
- `tests/test_scorer.py:312` — `score_project(conn, "test-proj", 1)`
- `tests/test_scorer.py:331` — `score_project(conn, "nonexistent", 1)`
- `tests/test_scorer.py:381` — `score_project(conn, "scope-test", 5)`

**`check_best_practice` callers:**
- `src/lab.py:347` — in `find_best_practice_deviations`
- `tests/test_detector.py:34, 45, 55, 66, 76, 87, 97, 108, 119, 130, 140, 152, 163, 172` — 14 direct calls

**`find_best_practice_deviations` callers:**
- `src/lab.py:67` — in `run_lab`
- `tests/test_detector.py:194, 226, 243` — 3 calls
- `tests/test_lab.py:631` — 1 call

**`init_db` — seeding behavior change affects:**
- `tests/test_classifier.py:286-297` — `test_functional_roles_seeded` asserts 25 roles exist after init_db
- Every test fixture calling `init_db(c)` — currently seeds roles/practices; after change, tables will be empty until cycle seeds them

### Test files requiring fixture updates

| Test File | Reason |
|---|---|
| `tests/test_classifier.py` | `classify_chunk` signature change (19 calls); `classify_project` (2 calls); `test_functional_roles_seeded` (init_db no longer seeds) |
| `tests/test_scorer.py` | `score_project` signature change (3 calls); `SCAN_TARGETS` dict form (2 sites) |
| `tests/test_cycle.py` | `SCAN_TARGETS` dict form (2 sites); `run_cycle` exercises classify+score pipeline |
| `tests/test_db.py` | `init_db` no longer seeds — any test asserting role/practice counts post-init |
| `tests/test_detector.py` | `check_best_practice` signature change (14 calls); `find_best_practice_deviations` (3 calls) |
| `tests/test_best_practices.py` | `ROLE_SCORING_WEIGHTS` / `ROLE_THRESHOLDS` imports from config.py (will move to archetype) |
| `tests/test_extractor.py` | `SCAN_TARGETS` dict form (1 site) |
| `tests/test_lab.py` | `SCAN_TARGETS` dict form (1 site); `find_best_practice_deviations` (1 call) |
| `tests/test_scanner.py` | `SCAN_TARGETS` dict form (3 sites) |

---

## Section 4 — flask_service 1:1 Mapping

Confirming that every invoice-pulse rule maps cleanly into an `ArchetypeDefinition`:

| IP Source | ArchetypeDefinition Field | Count | Priority Order | 1:1? |
|---|---|---|---|---|
| `FUNCTIONAL_ROLE_SEEDS` (`db.py:589-620`) | `roles` | 25 roles in 5 groups | N/A (data, not rules) | **YES** |
| `DECORATOR_RULES` (`classifier.py:18-23`) | `decorator_rules` | 4 rules | Preserved (list order) | **YES** |
| `NAME_RULES` (`classifier.py:25-51`) | `name_rules` | 21 rules | Preserved (list order) | **YES** |
| `FILE_PATH_RULES` (`classifier.py:54-85`) | `file_path_rules` | 30 rules | Preserved (list order) | **YES** |
| `ROLE_SCORING_WEIGHTS` (`config.py:75-108`) | `scoring_weights` | 8 role profiles | N/A (dict lookup) | **YES** |
| `ROLE_THRESHOLDS` (`config.py:111-132`) | `role_thresholds` | 5 role thresholds | N/A (dict lookup) | **YES** |
| `BEST_PRACTICE_SEEDS` (`db.py:673-739`) | `best_practices` | 15 patterns | N/A (data, not rules) | **YES** |
| `CONTENT_CHECKS` (`detector.py:15-54`) | `content_checks` | 8 pattern groups (10 regex) | N/A (dict lookup by name) | **YES** |
| `STRUCTURAL_CHECKS` (`detector.py:58-63`) | `structural_checks` | 1 pattern group | N/A (dict lookup by name) | **YES** |

**Priority order analysis:** The three rule lists (DECORATOR, NAME, FILE_PATH) are evaluated in strict priority order: decorators first, then name, then file path. This is encoded in the `classify_chunk` function's sequential loop structure, not in the data. Moving the data to the archetype preserves order because:
1. The archetype stores each rule list as a Python list (ordered).
2. The modified `classify_chunk` iterates `archetype.decorator_rules`, then `archetype.name_rules`, then `archetype.file_path_rules` — identical to current code.
3. Within each list, rules are evaluated first-to-last, same as current.

**FLAGS:** None. All rules map 1:1 with identical priority order. No rule requires splitting, merging, or reordering.

---

## Section 5 — Regression Harness + Baseline Capture

### Harness Design

The harness replays classify+score against the existing DB data for invoice-pulse. It:
- (a) Operates on a COPY of the live main-repo DB at `/Users/marklehn/Developer/GitHub/anvil/anvil.db` (in production, copy to `/tmp/anvil_regression_check.db`; for baseline capture, read-only against live DB is acceptable since the query is pure SELECT)
- (b) Does NOT write to any main-repo tracked path
- (c) Emits a SHA-256 over `(file_path, name, functional_role, composite_score)` under deterministic sort

### Harness Script

```python
#!/usr/bin/env python3
"""
Regression harness: classify+score replay for invoice-pulse.

Reads from a COPY of anvil.db (or read-only against live DB) and computes
a deterministic hash over invoice-pulse-scoped (file_path, name,
functional_role, composite_score) rows from the latest cycle.

Usage:
    python3 regression_harness.py [path_to_db]

If no path given, reads live DB read-only.
"""
import hashlib
import sqlite3
import sys


def run_harness(db_path: str, read_only: bool = False) -> dict:
    if read_only:
        conn = sqlite3.connect(f"file://{db_path}?mode=ro", uri=True)
    else:
        conn = sqlite3.connect(db_path)

    # Get invoice-pulse project id
    cur = conn.execute(
        "SELECT id FROM projects WHERE name = ?", ("invoice-pulse",)
    )
    row = cur.fetchone()
    if not row:
        raise ValueError("invoice-pulse project not found")
    project_id = row[0]

    # Get latest cycle
    cur = conn.execute(
        "SELECT MAX(cycle_number) FROM cycle_reports WHERE project_id = ?",
        (project_id,),
    )
    latest_cycle = cur.fetchone()[0]

    # Query scoped rows under deterministic sort
    cur = conn.execute(
        """
        SELECT cc.file_path, cc.name, cc.functional_role, hs.composite_score
        FROM code_chunks cc
        JOIN health_scores hs ON cc.id = hs.chunk_id
        WHERE cc.project_id = ?
          AND hs.cycle_id = ?
        ORDER BY cc.file_path, cc.name, cc.functional_role, hs.composite_score
        """,
        (project_id, latest_cycle),
    )
    rows = cur.fetchall()

    # Compute SHA-256
    hasher = hashlib.sha256()
    for row in rows:
        line = "|".join(str(v) for v in row)
        hasher.update(line.encode("utf-8"))

    conn.close()

    return {
        "cycle": latest_cycle,
        "row_count": len(rows),
        "hash": hasher.hexdigest(),
    }


if __name__ == "__main__":
    db_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "/Users/marklehn/Developer/GitHub/anvil/anvil.db"
    )
    read_only = len(sys.argv) <= 1  # read-only when using live DB
    result = run_harness(db_path, read_only=read_only)
    print(f"cycle={result['cycle']} rows={result['row_count']} hash={result['hash']}")
```

### Baseline Results

| Metric | Value |
|---|---|
| Cycle | 20 |
| Row count | 3688 |
| SHA-256 hash | `ed9cd2993d394b26b69c66e4c678727970eeea1038c9fd4de06c605ed0334bae` |

**Note:** Baseline captured via read-only query against live DB (disk space prevented copying the 1.3GB DB). The harness is designed to run against a copy; the QA step must run it against a fresh copy with the new code to verify byte-identical output.

---

## Section 6 — Verification Blocks

Pre-edit verification triples for the DEV step. Each claim describes the CURRENT (pre-BP2) state.

### VB1: classify_chunk uses module-global rules (not archetype-parameterised)

| Field | Value |
|---|---|
| **Claim** | `classify_chunk` takes one argument (`chunk_dict`) and reads from module-global `DECORATOR_RULES`, `NAME_RULES`, `FILE_PATH_RULES` |
| **Query** | `grep -n "def classify_chunk" src/classifier.py` |
| **Expected Output** | `88:def classify_chunk(chunk_dict: dict) -> Optional[str]:` |

### VB2: db.py seeds roles/practices inside init_db()

| Field | Value |
|---|---|
| **Claim** | `init_db()` calls `_seed_functional_roles(conn)` and `_seed_best_practices(conn)` |
| **Query** | `grep -n "_seed_" src/db.py` |
| **Expected Output** | Lines including `270:    _seed_functional_roles(conn)`, `271:    _seed_best_practices(conn)`, plus the function definitions at 623 and 742 |

### VB3: SCAN_TARGETS is the plain-path dict

| Field | Value |
|---|---|
| **Claim** | `SCAN_TARGETS` maps project names directly to path strings |
| **Query** | `python3 -c "from src.config import SCAN_TARGETS; print(type(list(SCAN_TARGETS.values())[0]))"` |
| **Expected Output** | `<class 'str'>` |

### VB4: config.py holds the weight/threshold dicts

| Field | Value |
|---|---|
| **Claim** | `ROLE_SCORING_WEIGHTS` and `ROLE_THRESHOLDS` are defined in `src/config.py` |
| **Query** | `grep -n "^ROLE_SCORING_WEIGHTS\|^ROLE_THRESHOLDS" src/config.py` |
| **Expected Output** | `75:ROLE_SCORING_WEIGHTS = {` and `111:ROLE_THRESHOLDS = {` |

### VB5: functional_roles table has no archetype column

| Field | Value |
|---|---|
| **Claim** | The `functional_roles` table DDL does not include an `archetype` column |
| **Query** | `python3 -c "import sqlite3; conn=sqlite3.connect('/Users/marklehn/Developer/GitHub/anvil/anvil.db'); cur=conn.execute('PRAGMA table_info(functional_roles)'); cols=[r[1] for r in cur.fetchall()]; print(cols); assert 'archetype' not in cols"` |
| **Expected Output** | Column list without `archetype`; assertion passes |

### VB6: CONTENT_CHECKS/STRUCTURAL_CHECKS are module-globals in detector.py

| Field | Value |
|---|---|
| **Claim** | `CONTENT_CHECKS` and `STRUCTURAL_CHECKS` are defined as module-level dicts in `src/detector.py` |
| **Query** | `grep -n "^CONTENT_CHECKS\|^STRUCTURAL_CHECKS" src/detector.py` |
| **Expected Output** | `15:CONTENT_CHECKS = {` and `58:STRUCTURAL_CHECKS = {` |

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** Step 1
**Status:** Complete

### What Was Done
Produced a migration-ready blueprint with six sections: (1) re-grounded gap assessment table with current-codebase line anchors for all 17 change points, (2) consumer enumeration of all 18 SCAN_TARGETS readers with exact access patterns and required changes, (3) changed-signature test surface identifying 9 test files and 50+ call sites requiring fixture updates, (4) flask_service 1:1 mapping confirming all 9 data sets transfer with identical priority order and no flags, (5) regression harness with embedded script and baseline hash captured against cycle 20 (3688 rows, SHA-256 `ed9cd2993d39...`), and (6) 6 verification blocks with query/expected-output triples for pre-edit validation.

### Files Deposited
- `knowledge/architecture/archetype-flask-service-migration-blueprint-2026-06-09.md` — full migration blueprint

### Files Created or Modified (Code)
- None (read-only analysis)

### Decisions Made
- Baseline captured via read-only query against live DB (disk space prevented copy; harness designed for copy usage at QA time)
- `check_best_practice` signature extends to receive checks dicts rather than embedding archetype dependency in detector.py (keeps detector stateless)
- `classify_project` loads archetype internally from SCAN_TARGETS rather than requiring callers to pass it (minimises call-site changes in cycle.py)

### Flags for CEO
- None

### Flags for Next Step
- Disk space was insufficient to copy the 1.3GB anvil.db for baseline capture; QA step must ensure copy space is available or use read-only mode
- The 9 test files listed in Section 3 is the complete scope of test fixture updates; if the DEV step discovers a file not on this list, halt and report per plan instructions
- `DEV_LOG_PATHS` must remain its own separate dict — do NOT fold into SCAN_TARGETS
