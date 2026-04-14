# Anvil — Fix: Coupling/Coverage/Complexity Noise Reduction
**Date:** 2026-04-14 | **Tier:** Medium | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 2

## How to Run This Plan

This plan is picked up and executed by Bellows automatically.

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/executable-findings-noise-reduction-2026-04-14.md", "anvil/knowledge/decisions/in-progress-executable-findings-noise-reduction-2026-04-14.md")`. Skip specialist file and glossary reads — implementation task. Working directory is `/Users/marklehn/Desktop/GitHub/`. Context from diagnostic at `anvil/knowledge/research/coupling-hotspots-noise-diagnostic-2026-04-14.md`: three generic finding functions in `anvil/src/lab.py` return 69% noise (test files + session lifecycle methods + connection factories). Only `find_intent_gaps` has the test-file filter; none filter session/connection noise. The fix adds SQL test-file filters to the three generic functions AND a shared Python helper `_is_noise_chunk` called from four locations. Tables are `code_chunks` and `health_scores` (NOT `chunks`/`chunk_scores` as some older plans state). **Three changes to `anvil/src/lab.py`:** **Change 1 — Add shared helper.** Add this near the top of the module, after imports but before the first function definition: `_SESSION_LIFECYCLE_NAMES = frozenset({"execute","commit","close","rollback","begin"})`, `_SESSION_LIFECYCLE_PATH_HINTS = ("profile_ingestion","database","_session","_engine","session_manager")`, `_CONNECTION_FACTORY_NAMES = frozenset({"get_connection","get_session","get_db","_get_db","connect","get_engine"})`. Then define `def _is_noise_chunk(chunk: dict) -> bool:` that returns True if any of: (a) `chunk.get("file_path","").startswith("tests/")`, (b) `chunk.get("name","") in _CONNECTION_FACTORY_NAMES`, (c) `chunk.get("name","") in _SESSION_LIFECYCLE_NAMES` AND any `pat in chunk.get("file_path","")` for pat in `_SESSION_LIFECYCLE_PATH_HINTS`. Otherwise returns False. **Change 2 — Add SQL test-file filter to three generic functions.** In `find_coupling_hotspots` (line ~118), add `AND cc.file_path NOT LIKE 'tests/%'` to the WHERE clause. In `find_coverage_gaps` (line ~96), add the same clause. In `find_complexity_hotspots` (line ~208), add the same clause. The existing `chunk_type != 'test_case'` in find_coverage_gaps stays — the new path filter is additive. **Change 3 — Call the helper post-fetch in all four finding functions.** In `find_coupling_hotspots`: after building the `results.append({...})` dict, check `if _is_noise_chunk({"name": r[2], "file_path": r[1]}): continue` BEFORE the append (not after). In `find_coverage_gaps`: same pattern — check noise before appending. In `find_complexity_hotspots`: same. In `find_intent_gaps`: find the three sub-query result loops (coverage at ~line 449, coupling at ~line 501, complexity at ~line 554) and add `if _is_noise_chunk({"name": name, "file_path": file_path}): continue` before each loop's finding dict is constructed — use whatever local variable names the existing code already has for name and file_path. Do not modify the SQL in find_intent_gaps (it already has the test-file filter; the helper catches session/connection noise that SQL doesn't). **Update `anvil/tests/test_lab.py`:** Add three new tests. `test_is_noise_chunk_test_file`: asserts `_is_noise_chunk({"name":"foo","file_path":"tests/test_bar.py"}) is True`. `test_is_noise_chunk_session_lifecycle`: asserts `_is_noise_chunk({"name":"execute","file_path":"profile_ingestion.py"}) is True` AND `_is_noise_chunk({"name":"execute","file_path":"app.py"}) is False` (execute in non-session file is genuine). `test_is_noise_chunk_connection_factory`: asserts `_is_noise_chunk({"name":"get_connection","file_path":"database.py"}) is True`. **Run targeted tests:** `python3 -m pytest tests/test_lab.py -v` from `/Users/marklehn/Desktop/GitHub/anvil/`. The 3 new tests must pass. Pre-existing failures `test_find_cochange_patterns` and `test_find_staleness_alerts` are expected to remain failing — do NOT attempt to fix them, they are out of scope for this plan. All other tests must pass. Commit: `fix: suppress test-file/session/connection noise in finding functions`. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed via `git --no-pager log --oneline -3` from `/Users/marklehn/Desktop/GitHub/anvil/`. Skip specialist file and glossary reads — mechanical verification + live cycle validation. **Deliverable verification:** grep `anvil/src/lab.py` for `_is_noise_chunk` — must appear 5+ times (1 definition + 4 call sites minimum: find_coupling_hotspots, find_coverage_gaps, find_complexity_hotspots, find_intent_gaps sub-queries). Grep for `_SESSION_LIFECYCLE_NAMES`, `_CONNECTION_FACTORY_NAMES`, `_SESSION_LIFECYCLE_PATH_HINTS` — each must appear at least twice (definition + use in helper). Grep `NOT LIKE 'tests/%'` — must appear at least 6 times (3 from existing find_intent_gaps sub-queries + 3 new in generic functions). Grep `anvil/tests/test_lab.py` for `test_is_noise_chunk_test_file`, `test_is_noise_chunk_session_lifecycle`, `test_is_noise_chunk_connection_factory` — all three present. **Re-run targeted tests:** `python3 -m pytest tests/test_lab.py -v` from `/Users/marklehn/Desktop/GitHub/anvil/` — write raw output to `anvil/knowledge/qa/evidence/findings-noise-reduction/pytest_targeted.txt` via Python file I/O. All non-pre-existing-failure tests must pass. **Live cycle regression test:** run `python3 -c "from src.cycle import run_cycle; import sqlite3; conn = sqlite3.connect('anvil.db'); run_cycle(conn, 'invoice-pulse'); conn.close(); print('cycle complete')"` from `/Users/marklehn/Desktop/GitHub/anvil/`. Write output to `anvil/knowledge/qa/evidence/findings-noise-reduction/cycle_run.txt`. This triggers a live cycle against invoice-pulse and produces a new cycle report. **Post-cycle noise check:** after the cycle completes, query the top 20 coupling hotspots from the most recent cycle and verify ZERO rows from `profile_ingestion.py` and ZERO rows with `file_path LIKE 'tests/%'`. Run: `python3 -c "import sqlite3; conn = sqlite3.connect('anvil.db'); cur = conn.execute('SELECT cc.name, cc.file_path, hs.coupling_score FROM code_chunks cc JOIN health_scores hs ON cc.id = hs.chunk_id WHERE hs.cycle_id = (SELECT MAX(id) FROM cycle_reports) ORDER BY hs.coupling_score DESC LIMIT 20'); rows = cur.fetchall(); [print(r) for r in rows]; noise = [r for r in rows if r[1].startswith('tests/') or 'profile_ingestion' in r[1]]; print(f'NOISE_COUNT={len(noise)}'); assert len(noise) == 0, f'EXPECTED 0 NOISE, GOT {len(noise)}'"` — this query checks the raw health_scores (not the filtered find_coupling_hotspots output), so it will still return profile_ingestion rows if they still score high. **THIS IS EXPECTED** — the filter is in `find_coupling_hotspots`, not in the scoring layer. Instead, verify by calling `find_coupling_hotspots` directly: `python3 -c "import sqlite3; from src.lab import find_coupling_hotspots; conn = sqlite3.connect('anvil.db'); cycle_id = conn.execute('SELECT MAX(id) FROM cycle_reports').fetchone()[0]; project_id = conn.execute('SELECT project_id FROM cycle_reports WHERE id=?', (cycle_id,)).fetchone()[0]; results = find_coupling_hotspots(conn, project_id, cycle_id); top20 = results[:20]; [print(r['name'], r['file_path'], r['coupling_score']) for r in top20]; noise = [r for r in top20 if r['file_path'].startswith('tests/') or 'profile_ingestion' in r['file_path']]; print(f'NOISE_COUNT={len(noise)}'); assert len(noise) == 0, f'FILTER FAILED: {len(noise)} noise rows in top 20'"` from `/Users/marklehn/Desktop/GitHub/anvil/`. Write to `anvil/knowledge/qa/evidence/findings-noise-reduction/top20_filter_check.txt`. **Read the latest cycle report markdown** at `anvil/knowledge/research/cycle-N-findings-2026-04-14.md` where N is the newest cycle number — find the filename by `ls -t anvil/knowledge/research/cycle-*-findings-*.md | head -1`. Confirm the Coupling Hotspots table does NOT contain rows from `tests/` or `profile_ingestion.py`. Write a one-line summary of the cycle number and filename to `anvil/knowledge/qa/evidence/findings-noise-reduction/cycle_report_summary.txt`. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |` covering: helper function defined, 4 call sites, 3 SQL filters added, 3 new tests pass, live cycle runs clean, filter check assert passes, cycle report markdown shows zero noise. Deposit QA report to `anvil/knowledge/qa/findings-noise-reduction-qa-2026-04-14.md`. **Run Rule 20 self-check:**
> ```python
> import os, sys
> qa_report_path = "knowledge/qa/findings-noise-reduction-qa-2026-04-14.md"
> evidence_dir = "knowledge/qa/evidence/findings-noise-reduction/"
> required_evidence_files = ["pytest_targeted.txt", "cycle_run.txt", "top20_filter_check.txt", "cycle_report_summary.txt"]
> hedging_keywords = ["pending","inferred","extrapolated","estimated","approximate","skipped","assumed","close enough","should pass","would pass","not run"]
> POSITIVE_STATUS_TOKENS = ["✅","OK","PASS","[x]","done","complete","verified"]
> def is_positive_row(line):
>     if "|" not in line: return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell: return True
>             elif cell.lower() == token.lower(): return True
>     return False
> failures = []
> if not os.path.isdir(evidence_dir): failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
> else:
>     for fname in required_evidence_files:
>         fpath = os.path.join(evidence_dir, fname)
>         if not os.path.isfile(fpath): failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif os.path.getsize(fpath) == 0: failures.append(f"CRITICAL: evidence file empty: {fpath}")
> if os.path.isfile(qa_report_path):
>     with open(qa_report_path) as f: report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower: failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}"); break
> else: failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("="*60)
> print("Rule 20 — QA Self-Check Results")
> print("="*60)
> if failures:
>     print(f"FAILED — {len(failures)} issue(s):")
>     for f in failures: print(f"  - {f}")
>     sys.exit(1)
> else:
>     print("PASSED — all evidence files present, no hedging keywords.")
> ```
> Run from `/Users/marklehn/Desktop/GitHub/anvil/`. If self-check fails, stop and report to CEO. If passes: update `anvil/PROJECT_STATUS.md` — add entry: "2026-04-14: Findings noise reduction shipped. _is_noise_chunk helper added; test-file filter applied to find_coupling_hotspots, find_coverage_gaps, find_complexity_hotspots via SQL; session-lifecycle and connection-factory suppression applied to all 4 finding functions via Python helper. Cycle report coupling hotspots now signal-dominant." Move plan to Done: `import shutil; shutil.move("anvil/knowledge/decisions/in-progress-executable-findings-noise-reduction-2026-04-14.md", "anvil/knowledge/decisions/Done/executable-findings-noise-reduction-2026-04-14.md")`. Commit: `chore: QA report — findings noise reduction`. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
