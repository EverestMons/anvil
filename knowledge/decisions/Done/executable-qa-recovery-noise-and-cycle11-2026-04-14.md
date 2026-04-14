# Anvil — QA Recovery: Findings Noise Reduction + Cycle 11 Cleanup
**Date:** 2026-04-14 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (QA)
**Priority:** 1

## How to Run This Plan

This plan is picked up and executed by Bellows automatically.

## Context

Two Anvil housekeeping jobs, both QA-agent work, combined for efficiency.

**Job 1 — Noise Reduction QA Recovery.** The plan `executable-findings-noise-reduction-2026-04-14.md` shipped its DEV work cleanly (commit `d04fa5e fix: suppress test-file/session/connection noise in finding functions`). Pytest ran at `anvil/knowledge/qa/evidence/findings-noise-reduction/pytest_targeted.txt` — 18 passing including 3 new noise helper tests, 2 pre-existing failures carried forward as expected (`test_find_cochange_patterns`, `test_find_staleness_alerts`). The QA step then stopped before running the live cycle regression, top-20 filter check, QA report, and move-to-Done. The plan is still at `anvil/knowledge/decisions/in-progress-executable-findings-noise-reduction-2026-04-14.md`.

**Job 2 — Cycle 11 Stranded File Cleanup.** The plan `executable-anvil-cycle-11-2026-04-14.md` was executed (git commit `7b81560 fix: expand _extract_project_mission heading patterns; re-run Anvil Cycle 11`, findings file at `anvil/knowledge/research/cycle-11-findings-2026-04-14.md`). The mission-heading regex was patched mid-execution and a re-run happened as Cycle 12 (commit `924985e` territory). The original Cycle 11 plan file was never moved to Done — still sitting at `anvil/knowledge/decisions/in-progress-executable-anvil-cycle-11-2026-04-14.md`. Do NOT re-run Cycle 11 — that would create a new cycle row and worsen the cycle_number drift problem. Just move the file to Done with a note.

---
---

## STEP 1 — QA (Recovery + Housekeeping)

---

> **FIRST — claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/executable-qa-recovery-noise-and-cycle11-2026-04-14.md", "anvil/knowledge/decisions/in-progress-executable-qa-recovery-noise-and-cycle11-2026-04-14.md")`. Skip specialist file and glossary reads — pure housekeeping + verification task. Working directory is `/Users/marklehn/Desktop/GitHub/anvil/`. Two jobs in sequence.
>
> **JOB 1 — Noise Reduction QA Recovery (priority: complete before Job 2).** Verify DEV commit via `git --no-pager log --oneline -5` — confirm `d04fa5e fix: suppress test-file/session/connection noise in finding functions` is present. **Deliverable verification (same as original plan):** grep `src/lab.py` for `_is_noise_chunk` — must appear 5+ times (1 definition + 4 call sites); grep for `_SESSION_LIFECYCLE_NAMES`, `_CONNECTION_FACTORY_NAMES`, `_SESSION_LIFECYCLE_PATH_HINTS` — each ≥2 times; grep `NOT LIKE 'tests/%'` — must appear ≥6 times; grep `tests/test_lab.py` for `test_is_noise_chunk_test_file`, `test_is_noise_chunk_session_lifecycle`, `test_is_noise_chunk_connection_factory` — all three present. **Verify existing pytest evidence.** Confirm `knowledge/qa/evidence/findings-noise-reduction/pytest_targeted.txt` exists and contains "18 passed" and "2 failed" — this file is from the original QA run and does NOT need re-running. The 2 failures are pre-existing (`test_find_cochange_patterns`, `test_find_staleness_alerts`) and are treated as EXPECTED for this plan. **Expected-failure handling rule: if and only if exactly these 2 tests fail and all other tests pass (including the 3 new noise tests), treat the pytest evidence as PASS. Any other failure count is a FAIL.** **Live cycle regression test:** run `python3 -c "from src.cycle import run_cycle; import sqlite3; conn = sqlite3.connect('anvil.db'); run_cycle(conn, 'invoice-pulse'); conn.close(); print('cycle complete')"` from `/Users/marklehn/Desktop/GitHub/anvil/`. Write output to `knowledge/qa/evidence/findings-noise-reduction/cycle_run.txt` via Python file I/O. Note: `run_cycle` takes 2 args (conn, project_name), not 3 — the project path is resolved internally. **Top-20 filter check:** run `python3 -c "import sqlite3; from src.lab import find_coupling_hotspots; conn = sqlite3.connect('anvil.db'); cycle_id = conn.execute('SELECT MAX(id) FROM cycle_reports').fetchone()[0]; project_id = conn.execute('SELECT project_id FROM cycle_reports WHERE id=?', (cycle_id,)).fetchone()[0]; results = find_coupling_hotspots(conn, project_id, cycle_id); top20 = results[:20]; [print(r['name'], r['file_path'], r['coupling_score']) for r in top20]; noise = [r for r in top20 if r['file_path'].startswith('tests/') or 'profile_ingestion' in r['file_path']]; print(f'NOISE_COUNT={len(noise)}'); assert len(noise) == 0, f'FILTER FAILED: {len(noise)} noise rows in top 20'"` from `/Users/marklehn/Desktop/GitHub/anvil/`. Write output to `knowledge/qa/evidence/findings-noise-reduction/top20_filter_check.txt`. **Cycle report summary:** find the newest cycle findings markdown with `python3 -c "import os, glob; files = sorted(glob.glob('knowledge/research/cycle-*-findings-*.md'), key=os.path.getmtime, reverse=True); print(files[0])"`. Read that file, confirm its Coupling Hotspots table contains zero rows from `tests/` or `profile_ingestion.py`. Write a one-line summary `CYCLE_FILE={path} NOISE_IN_COUPLING_HOTSPOTS={count}` to `knowledge/qa/evidence/findings-noise-reduction/cycle_report_summary.txt`. **Produce verification table:** `| Deliverable | Expected | Status (✅/❌) | Evidence |` covering: DEV commit d04fa5e present, helper function defined, 4 call sites of _is_noise_chunk, 3 SQL test-file filters added to generic functions, 3 new noise tests present and passing in pytest evidence, pytest run shows exactly 2 pre-existing failures and 18 passes, live cycle ran clean, top20 filter assert passed, cycle report markdown shows zero noise. Deposit QA report to `knowledge/qa/findings-noise-reduction-qa-2026-04-14.md`.
>
> **JOB 1 Rule 20 self-check:**
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
> print("Rule 20 — QA Self-Check Results (Job 1)")
> print("="*60)
> if failures:
>     print(f"FAILED — {len(failures)} issue(s):")
>     for f in failures: print(f"  - {f}")
>     sys.exit(1)
> else:
>     print("PASSED — all evidence files present, no hedging keywords.")
> ```
> Run from `/Users/marklehn/Desktop/GitHub/anvil/`. If self-check fails, stop and report to CEO — do NOT proceed to Job 2. If passes: **Move original noise-reduction plan to Done:** `import shutil; shutil.move("knowledge/decisions/in-progress-executable-findings-noise-reduction-2026-04-14.md", "knowledge/decisions/Done/executable-findings-noise-reduction-2026-04-14.md")`.
>
> **JOB 2 — Cycle 11 Stranded File Cleanup.** Do NOT re-run Cycle 11. The work was already executed (commit `7b81560`, findings file at `knowledge/research/cycle-11-findings-2026-04-14.md`). Only move the stranded plan file. **Verify the cycle 11 work exists:** confirm `knowledge/research/cycle-11-findings-2026-04-14.md` exists via `os.path.isfile`. If it does NOT exist, stop and report to CEO — do NOT move the file blindly. **Move the stranded plan:** `import shutil; shutil.move("knowledge/decisions/in-progress-executable-anvil-cycle-11-2026-04-14.md", "knowledge/decisions/Done/executable-anvil-cycle-11-2026-04-14.md")`.
>
> **FINAL — PROJECT_STATUS update covering both jobs:** update `PROJECT_STATUS.md` with a single new entry: "2026-04-14: QA recovery — (1) Findings noise reduction shipped and closed: _is_noise_chunk helper + SQL test-file filters + 3 new tests; cycle report coupling hotspots now signal-dominant; DEV commit d04fa5e. (2) Cycle 11 stranded plan moved to Done (pre-empted by mission-heading re-run as Cycle 12, already executed, no re-run performed)." **Move this recovery plan to Done:** `import shutil; shutil.move("knowledge/decisions/in-progress-executable-qa-recovery-noise-and-cycle11-2026-04-14.md", "knowledge/decisions/Done/executable-qa-recovery-noise-and-cycle11-2026-04-14.md")`. Commit: `chore: QA recovery — findings noise reduction closed + cycle 11 cleanup`. Standard prompt feedback protocol → `knowledge/research/agent-prompt-feedback.md`.
