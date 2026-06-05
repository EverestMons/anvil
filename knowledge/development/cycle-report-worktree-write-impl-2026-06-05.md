# Cycle Report Worktree-Write Implementation Log

**Date:** 2026-06-05 | **Agent:** Anvil Developer | **Step:** 2
**Blueprint:** `knowledge/architecture/cycle-report-worktree-write-blueprint-2026-06-05.md`

---

## Changes Made

### 1. `src/config.py` — Added `ANVIL_RUNTIME_ROOT` (§1)

Added `ANVIL_RUNTIME_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` immediately after `ANVIL_ROOT` (line 8). Resolves to the worktree root when `config.py` runs from a worktree copy; equals `ANVIL_ROOT` in canonical context.

**pytest after:** 238 passed (baseline preserved).

### 2. `src/lab.py` — Split write-path vs recorded-path (§2)

- **Import (line 19):** Added `ANVIL_RUNTIME_ROOT` to the `src.config` import.
- **`run_lab` caller (lines 93-105):** Split single `report_path` into `write_path` (using `ANVIL_RUNTIME_ROOT`) and `report_path` (using `ANVIL_ROOT`). Both passed to `write_cycle_report`. Return dict keeps canonical `report_path`.
- **`write_cycle_report` signature (line 855):** Added `write_path: str` parameter before `report_path: str`.
- **Docstring:** Updated to `"""Generate markdown report at write_path; record report_path (canonical) in DB."""`
- **File write block (lines 1061-1063):** Changed `report_path` → `write_path` for `os.makedirs` and `open()`.
- **DB record:** Unchanged — `report_path=report_path` stays canonical.

**pytest after:** 236 passed, 2 failed (expected — tests needed signature update).

### 3. `tests/test_lab.py` — Updated tests (§6)

- **`test_write_cycle_report`:** Added `write_path` param, changed file assertions to use `write_path`, added DB assertion that recorded path equals canonical `report_path`.
- **`test_run_lab_end_to_end`:** Added `monkeypatch.setattr("src.lab.ANVIL_RUNTIME_ROOT", str(tmp_path))`.
- **`test_cycle_report_includes_untested_complexity`:** Added `write_path` param, changed file read to use `write_path`.
- **NEW `test_write_vs_record_path_split`:** Proves the file is written to `write_path` (runtime), NOT written to `report_path` (canonical), and DB records canonical path. Uses separate `runtime/` and `canonical/` tmp dirs.

### 4. `tests/test_cycle.py` — Updated test (§6)

- **`test_run_cycle_end_to_end`:** Added `monkeypatch.setattr("src.lab.ANVIL_RUNTIME_ROOT", str(cycle_project))`.

**pytest after all test updates:** 239 passed (238 baseline + 1 new).

### 5. `knowledge/architecture/cycle-plan-template.md` — Template edits (§5)

- **Edit (a):** Authoring rule 3 rewritten — removed wrap-commit requirement, states report lands in worktree via `ANVIL_RUNTIME_ROOT`, references DEV step `git add`.
- **Edit (b):** Working-dir note rewritten — states report lands in WORKTREE, DB record stores canonical path valid after teardown.
- **Edit (c):** QA check (3) rewritten — verifies worktree-relative path and staging status instead of canonical main path.
- **Edit (d):** Added step (10) to DEV step — explicit `git add knowledge/research/cycle-<N>-findings-<UTC>.md` with staging verification.
- **Edit (e):** DEV verification (3) rewritten — checks worktree-relative path, references step (10) for staging.

---

## Write-vs-Record Proof

The new `test_write_vs_record_path_split` test proves:
1. File is written to `write_path` (`runtime/knowledge/research/cycle-1-findings-2026-06-05.md`) — `assert os.path.isfile(write_path)` passes.
2. File is NOT written to `report_path` (`canonical/knowledge/research/cycle-1-findings-2026-06-05.md`) — `assert not os.path.isfile(report_path)` passes.
3. DB `cycle_reports.report_path` records the canonical path — `assert row[0] == report_path` passes.

---

## Template `git add` Confirmation

`grep -n "git add knowledge/research/cycle" knowledge/architecture/cycle-plan-template.md` returns:
```
175:> git add knowledge/research/cycle-<N>-findings-<UTC>.md
```
The explicit staging instruction is present in DEV step (10).

---

## Final Test Count

```
239 passed in 1.53s
```
Baseline was 238; +1 from new `test_write_vs_record_path_split`.

---

## Clean `git status`

```
 M knowledge/architecture/cycle-plan-template.md
 M src/config.py
 M src/lab.py
 M tests/test_cycle.py
 M tests/test_lab.py
```
No stray `cycle-*-findings` artifact. A pre-existing `cycle-1-findings-2026-06-05.md` from a prior cycle run was found and removed; tests confirmed they do not produce it.

---

## Output Receipt
**Agent:** Anvil Developer
**Step:** 2
**Status:** Complete

### What Was Done
Implemented the cycle report worktree-write split per blueprint: `ANVIL_RUNTIME_ROOT` added to `config.py`, `write_cycle_report` signature split into `write_path` (runtime, for file write) and `report_path` (canonical, for DB record), `run_lab` caller updated, 4 existing tests updated, 1 new write-vs-record proof test added (239 total), and 5 cycle-plan-template edits applied (wrap-commit retired, working-dir note corrected, QA check updated, explicit `git add` added to DEV step).

### Files Deposited
- `knowledge/development/cycle-report-worktree-write-impl-2026-06-05.md` — this implementation log

### Files Created or Modified (Code)
- `src/config.py` — added `ANVIL_RUNTIME_ROOT`
- `src/lab.py` — split `write_cycle_report` write-path vs recorded-path, updated `run_lab` caller and import
- `tests/test_lab.py` — updated 3 tests, added `test_write_vs_record_path_split`
- `tests/test_cycle.py` — updated `test_run_cycle_end_to_end` with `ANVIL_RUNTIME_ROOT` monkeypatch
- `knowledge/architecture/cycle-plan-template.md` — 5 edits per §5

### Decisions Made
- Removed pre-existing stray `cycle-1-findings-2026-06-05.md` artifact (from a prior cycle run, not produced by tests)
- All test updates use `tmp_path` — no real cycle-findings files written into the repo

### Flags for CEO
- None

### Flags for Next Step
- All 5 template edits landed and verified
- Write-vs-record proof test passes
- 239 tests green, no leaked artifacts
