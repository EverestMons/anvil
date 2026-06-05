# Cycle Report Worktree-Write Blueprint — Edit Map

**Date:** 2026-06-05 | **Agent:** Anvil Systems Analyst | **Step:** 1
**Plan:** executable-anvil-cycle-report-worktree-write-2026-06-05

---

## §1 — Runtime vs Canonical Root

**Derivation:** `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` — the
pre-F8 form. This resolves `config.py`'s `__file__` up two directories (out of
`src/`) to the project root. In canonical context this equals `ANVIL_ROOT`. In a
Bellows worktree, `__file__` resolves to the worktree copy of `config.py`, so the
result is the worktree root.

**Definition site:** `config.py`, immediately after `ANVIL_ROOT` (line 6).

```python
# OLD (config.py:6)
ANVIL_ROOT = "/Users/marklehn/Developer/GitHub/anvil"

# NEW (config.py:6-8)
ANVIL_ROOT = "/Users/marklehn/Developer/GitHub/anvil"

ANVIL_RUNTIME_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

**Confirmation:** When `lab.py` imports `ANVIL_RUNTIME_ROOT` from the worktree copy
of `config.py`, `__file__` is `<worktree>/src/config.py`, so
`ANVIL_RUNTIME_ROOT` → `<worktree>/`. In canonical context,
`ANVIL_RUNTIME_ROOT` == `ANVIL_ROOT`. Keep `ANVIL_ROOT` hardcoded-canonical for
all DB records.

---

## §2 — `write_cycle_report` Split

### Caller: `run_lab` (`lab.py:92-100`)

```python
# OLD (lab.py:92-100)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = os.path.join(
        ANVIL_ROOT, "knowledge", "research",
        f"cycle-{cycle_id}-findings-{today}.md",
    )

    write_cycle_report(
        conn, project_name, cycle_id, findings, constraints,
        specialist_data, report_path, started_at,
    )

# NEW (lab.py:92-104)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_filename = f"cycle-{cycle_id}-findings-{today}.md"
    write_path = os.path.join(
        ANVIL_RUNTIME_ROOT, "knowledge", "research", report_filename,
    )
    report_path = os.path.join(
        ANVIL_ROOT, "knowledge", "research", report_filename,
    )

    write_cycle_report(
        conn, project_name, cycle_id, findings, constraints,
        specialist_data, write_path, report_path, started_at,
    )
```

The return dict (`lab.py:109`) keeps `"report_path": report_path` (canonical).
This is what the DB records and what deposit gates match post-teardown.

### Import change: `lab.py:17-18`

```python
# OLD
from src.config import (
    ANVIL_ROOT,

# NEW
from src.config import (
    ANVIL_ROOT,
    ANVIL_RUNTIME_ROOT,
```

### Function: `write_cycle_report` (`lab.py:851-1072`)

**Signature:**

```python
# OLD (lab.py:851-854)
def write_cycle_report(conn, project_name: str, cycle_id: int,
                       findings: dict, constraints: list[dict],
                       specialist_data: dict, report_path: str,
                       started_at: str) -> None:

# NEW
def write_cycle_report(conn, project_name: str, cycle_id: int,
                       findings: dict, constraints: list[dict],
                       specialist_data: dict, write_path: str,
                       report_path: str, started_at: str) -> None:
```

**Docstring update:**

```python
# OLD
    """Generate markdown report and create cycle_reports DB row."""

# NEW
    """Generate markdown report at write_path; record report_path (canonical) in DB."""
```

**File write (`lab.py:1057-1059`):**

```python
# OLD
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        f.write(content)

# NEW
    os.makedirs(os.path.dirname(write_path), exist_ok=True)
    with open(write_path, "w") as f:
        f.write(content)
```

**DB record (`lab.py:1062-1072`):** NO CHANGE — `report_path=report_path` stays
canonical.

---

## §3 — Consumer Check

**Grep results for anything that reads `cycle_reports.report_path` or opens a file
at that path during a worktree run:**

| Location | Usage | Opens the file? | Affected? |
|----------|-------|-----------------|-----------|
| `lab.py:109` | Returns canonical path in `run_lab` result dict | No — pass-through | No |
| `cycle.py:88-89` | `run_lab` result captured in `results["lab"]` | No — pass-through | No |
| `cycle.py:157` | `get_cycle_summary` reads `report["report_path"]` from DB, returns in summary | No — pass-through for display | No |
| `db.py:192` | Schema DDL — column definition | N/A | No |
| `db.py:494` | `create_cycle_report` INSERT — stores the path | No — write only | No |

**Finding:** No code reads `cycle_reports.report_path` and attempts to open/read
the file at that path during a worktree run. The only consumer is
`get_cycle_summary` (`cycle.py:157`), which includes the path in a summary dict
for display — it does NOT open the file. The canonical recorded path is valid
after teardown (when the worktree commit has been landed to main). Safe to split.

---

## §4 — Commit-Capture Guarantee

**Problem:** The Bellows runner guarantees "the final operation is a commit"
(`runner.py:23`) but does NOT guarantee `git add -A`. The `deposit_exists` gate
checks `os.path.isfile()`, not git staging status. There is no worktree-clean
gate. Therefore:

1. Under the old model: the report landed in canonical main (outside the worktree)
   — it was never in the worktree's working tree, so worktree commit couldn't
   capture it anyway. The Planner wrap-committed it on main.

2. Under the new model: the report lands in the worktree's working tree (at
   `knowledge/research/cycle-<N>-findings-<UTC>.md`). If not explicitly staged,
   it is uncommitted. On teardown:
   - **Cherry-pick model:** the file is copied to main untracked by step (d)
     copy-back → re-creates the dirty-main bug this fix targets.
   - **Merge model (Plan B):** the file is LOST — the worktree is deleted and
     the uncommitted file goes with it.

**Required template edit:** The cycle-plan-template's STEP 1 (DEV) must contain an
explicit staging instruction. Place it after the post-cycle verification checks
and before the deposits block:

```
> **Stage the cycle report for commit.** The report lands in the worktree
> (not canonical main) and MUST be committed with the worktree's changes.
> Run:
> ```bash
> git add knowledge/research/cycle-<N>-findings-<UTC>.md
> ```
> Verify it is staged: `git status` should show the file as "new file" under
> "Changes to be committed." If it is under "Untracked files," the add failed.
```

This goes in the DEV step body, after verification item (9) and before the
`**Constraints:**` line. The exact template location is specified in §5 below.

**Do NOT conclude "no special declaration needed."** The explicit `git add` is
mandatory — without it the report is uncommitted and either re-creates dirty-main
(cherry-pick) or is lost (merge).

---

## §5 — Cycle-Template Impact

Target: `knowledge/architecture/cycle-plan-template.md`

### Edit (a): Authoring rule 3 (lines 33-49) — REWRITE

**OLD (lines 33-49):**
```
3. **Declare the canonical cycle report as a deposit, and commit it before the
   close verdict.** `run_cycle` writes
   `knowledge/research/cycle-<N>-findings-<UTC>.md` to the canonical anvil MAIN
   path (ANVIL_ROOT is hardcoded — F8), NOT the worktree. It is a git-tracked
   artifact (cycles 1–20 are all in `git ls-files`), so do NOT gitignore it.
   Because the run executes in a worktree but the file lands in main, it sits
   untracked in main and trips worktree-teardown's dirty-tree pre-check. Two
   required actions:
   (a) declare it in the DEV step's `**Deposits:**` block (below), and
   (b) at session wrap, AFTER Step 2 (QA) completes and BEFORE depositing the
   terminal close verdict (verdict consumption triggers teardown), commit it on
   main:
   `git add knowledge/research/cycle-<N>-findings-<UTC>.md && git commit -m "chore: cycle <N> canonical report"`
   Residual: if teardown later hits parallel-SHA divergence and you recover via
   `git fetch origin && git reset --hard origin/main`, that reset discards the
   local commit AND deletes the tracked file from the working tree — re-stage and
   re-commit (or push) the report after recovery.
```

**NEW:**
```
3. **The cycle report lands in the worktree, not canonical main.** `run_cycle`
   writes `knowledge/research/cycle-<N>-findings-<UTC>.md` to the runtime root
   (`ANVIL_RUNTIME_ROOT`), which resolves to the worktree during a Bellows
   dispatch. It is a git-tracked artifact (cycles 1–20 are all in
   `git ls-files`), so do NOT gitignore it. The report MUST be explicitly staged
   before the worktree commit — the DEV step contains an explicit `git add`
   instruction for this (see STEP 1 below). No Planner wrap-commit on main is
   needed; the report rides the worktree commit and lands on main at teardown.
   Declare it in the DEV step's `**Deposits:**` block.
```

### Edit (b): Working-dir note in STEP 1 (line 125) — REWRITE

**OLD (line 125):**
```
> **Working directory note:** Bellows runs this plan in a worktree at `anvil/.bellows-worktrees/anvil-cycle-<N>-<LOCAL>/`; the worktree IS the anvil root from your perspective. For Anvil source imports use relative paths (e.g., `from src.cycle import run_cycle`). **For DB access use the absolute canonical path** `/Users/marklehn/Developer/GitHub/anvil/anvil.db`. The F8 hardcode (`ANVIL_ROOT`, commit `86ba5fd`) means run_cycle deposits resolve to canonical main-repo locations automatically — including the cycle report, which lands in MAIN, not the worktree.
```

**NEW:**
```
> **Working directory note:** Bellows runs this plan in a worktree at `anvil/.bellows-worktrees/anvil-cycle-<N>-<LOCAL>/`; the worktree IS the anvil root from your perspective. For Anvil source imports use relative paths (e.g., `from src.cycle import run_cycle`). **For DB access use the absolute canonical path** `/Users/marklehn/Developer/GitHub/anvil/anvil.db`. The cycle report lands in the WORKTREE at `knowledge/research/cycle-<N>-findings-<UTC>.md` (via `ANVIL_RUNTIME_ROOT`). The DB record stores the canonical path (`ANVIL_ROOT`), which becomes valid after teardown lands the worktree commits to main.
```

### Edit (c): QA check (3) in STEP 2 (line 208) — REWRITE

**OLD (line 208):**
```
> **(3) Canonical cycle report at main path.** `ls -la /Users/marklehn/Developer/GitHub/anvil/knowledge/research/cycle-<N>-findings-<UTC>.md > knowledge/qa/evidence/executable-anvil-cycle-<N>-<LOCAL>/cycle_report_path.txt 2>&1`. Expected: exists at canonical main path with UTC date. ❌ if missing or worktree-local.
```

**NEW:**
```
> **(3) Cycle report in worktree.** `ls -la knowledge/research/cycle-<N>-findings-<UTC>.md > knowledge/qa/evidence/executable-anvil-cycle-<N>-<LOCAL>/cycle_report_path.txt 2>&1`. Expected: exists at worktree-relative path with UTC date. ❌ if missing. Also verify it is staged: `git diff --cached --name-only | grep cycle-<N>-findings > knowledge/qa/evidence/executable-anvil-cycle-<N>-<LOCAL>/cycle_report_staged.txt 2>&1`. Expected: ≥1 match.
```

### Edit (d): DEV step — add explicit `git add` instruction

Insert AFTER verification item (9) (the phantom-function check, line 178) and
BEFORE the `**Constraints:**` line (line 180):

```
>
> **(10) Stage the cycle report for commit.** The report lands in the worktree and
> MUST be committed with the worktree's changes:
> ```bash
> git add knowledge/research/cycle-<N>-findings-<UTC>.md
> ```
> Verify staged: `git status` should show it as "new file" under "Changes to be
> committed." If it appears under "Untracked files," the add failed — retry.
```

### Edit (e): DEV step verification (3) (line 166) — REWRITE

**OLD (line 166):**
```
> (3) Locate the canonical cycle report at `/Users/marklehn/Developer/GitHub/anvil/knowledge/research/cycle-<N>-findings-<UTC>.md` (canonical MAIN path, UTC date). Confirm it exists there and print its exact filename verbatim — the date is UTC; the Planner needs it for the wrap commit.
```

**NEW:**
```
> (3) Locate the cycle report at `knowledge/research/cycle-<N>-findings-<UTC>.md` (worktree-relative path, UTC date). Confirm it exists and print its exact filename verbatim. The file lands in the worktree via `ANVIL_RUNTIME_ROOT`; step (10) stages it for commit.
```

---

## §6 — Test-Impact List

### Tests to UPDATE

| Test | File | What changes |
|------|------|-------------|
| `test_write_cycle_report` | `tests/test_lab.py:237` | Signature call gains `write_path` param before `report_path`. Both can point to `tmp_path` (tests the write). Optionally add assertion that DB row `report_path` matches the passed `report_path` arg. |
| `test_run_lab_end_to_end` | `tests/test_lab.py:278` | Add `monkeypatch.setattr("src.lab.ANVIL_RUNTIME_ROOT", str(tmp_path))` alongside the existing `ANVIL_ROOT` monkeypatch. |
| `test_write_cycle_report_untested_complexity` | `tests/test_lab.py:504` | Signature call gains `write_path` param before `report_path`. Both can point to `tmp_path`. |
| `test_run_cycle_end_to_end` | `tests/test_cycle.py:87` | Add `monkeypatch.setattr("src.lab.ANVIL_RUNTIME_ROOT", str(cycle_project))` alongside the existing `ANVIL_ROOT` monkeypatch. |

### Tests to KEEP (no change)

| Test | File | Reason |
|------|------|--------|
| `test_scanner.py:403,446` | `tests/test_scanner.py` | Monkeypatches `src.scanner.ANVIL_ROOT` — scanner does not use `ANVIL_RUNTIME_ROOT`. |

### NEW test required

**`test_write_vs_record_path_split`** in `tests/test_lab.py`:

Purpose: prove the report file is written under `write_path` (runtime root) while
`cycle_reports.report_path` records the canonical `report_path`.

```python
def test_write_vs_record_path_split(conn, lab_project, tmp_path):
    """File writes to write_path; DB records report_path (canonical)."""
    pid, _, _, _, _ = lab_project
    findings = {k: [] for k in [
        "coverage_gaps", "coupling_hotspots", "clone_candidates",
        "staleness_alerts", "complexity_hotspots", "cochange_patterns",
        "best_practice_deviations", "intent_gaps",
    ]}
    specialist_data = generate_specialist_update_data(conn, pid, 1)

    runtime_dir = tmp_path / "runtime" / "knowledge" / "research"
    canonical_dir = tmp_path / "canonical" / "knowledge" / "research"
    # Do NOT create canonical_dir — the file should NOT land there

    write_path = str(runtime_dir / "cycle-1-findings-2026-06-05.md")
    report_path = str(canonical_dir / "cycle-1-findings-2026-06-05.md")

    write_cycle_report(
        conn, "lab-test", 1, findings, [],
        specialist_data, write_path, report_path, "2026-06-05T10:00:00",
    )

    # File written to write_path (runtime)
    assert os.path.isfile(write_path)
    # File NOT written to report_path (canonical)
    assert not os.path.isfile(report_path)
    # DB records canonical path
    row = conn.execute(
        "SELECT report_path FROM cycle_reports WHERE cycle_number = 1"
    ).fetchone()
    assert row[0] == report_path
```

Must use `tmp_path` — must NOT write a real `cycle-*-findings` file into the repo.

---

## Open Items

None. All items settled.

---

## How to Verify This Was Implemented Correctly

1. `ANVIL_RUNTIME_ROOT` is defined in `config.py` immediately after `ANVIL_ROOT`,
   using the `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` form.
2. `write_cycle_report` has a `write_path` param before `report_path` in its
   signature; the file write uses `write_path`; the DB INSERT uses `report_path`.
3. `run_lab` builds both paths and passes them correctly.
4. The new `test_write_vs_record_path_split` test proves the split: file at
   `write_path`, DB record at `report_path`, and they differ.
5. All existing tests updated and passing.
6. Cycle-plan-template: authoring rule 3 rewritten (no wrap-commit), working-dir
   note corrected, QA check (3) checks worktree path, DEV step (10) has explicit
   `git add`.
7. No `cycle-*-findings` artifact left in repo by tests (`git status --porcelain`
   clean).
8. Full `pytest tests/ -v` green with baseline count preserved or increased.

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Produced a precise edit map for splitting the cycle report write-target (runtime
root, resolves to worktree) from the recorded-path (canonical root, stored in DB).
Covers config change, `write_cycle_report` signature/caller split, consumer safety
check, commit-capture guarantee with explicit staging, cycle-plan-template edits
(5 locations), and test-impact analysis with a new split-proof test.

### Files Deposited
- `knowledge/architecture/cycle-report-worktree-write-blueprint-2026-06-05.md` — this edit map

### Files Created or Modified (Code)
- None (edit map only — no source changes)

### Decisions Made
- Named the runtime root `ANVIL_RUNTIME_ROOT` (consistent with `ANVIL_ROOT` naming)
- Chose to add `write_path` as a new param before `report_path` in the function signature (minimal disruption, clear semantics)
- Return dict keeps canonical `report_path` (matches DB record, valid post-teardown)
- Template QA check (3) changed to verify worktree-relative path AND staging status
- New test uses separate runtime/canonical tmp dirs to prove the split

### Flags for CEO
- None

### Flags for Next Step
- All items are settled — no OPEN items for DEV to resolve
- The 4 existing test updates are straightforward signature changes + monkeypatch additions
- The new `test_write_vs_record_path_split` test is specified with full code — DEV can copy it directly
- Template edits are specified with full old→new text for each location
