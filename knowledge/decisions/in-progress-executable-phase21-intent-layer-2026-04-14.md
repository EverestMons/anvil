# Anvil — Phase 2.1: Intent Cross-Reference Layer
**Date:** 2026-04-14 | **Tier:** Medium | **Test Scope:** targeted | **Execution:** Step 1 (SA) → Step 2 (DEV) → Step 3 (QA)
**Priority:** 1

## How to Run This Plan

This plan is picked up and executed by Bellows automatically.

---
---

## STEP 1 — SA (Blueprint)

---

> **FIRST — claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/executable-phase21-intent-layer-2026-04-14.md", "anvil/knowledge/decisions/in-progress-executable-phase21-intent-layer-2026-04-14.md")`. Read your specialist file at `anvil/agents/ANVIL_SYSTEMS_ANALYST.md` and domain glossary at `anvil/knowledge/research/domain-glossary.md`. Read the Phase 2 strategic audit roadmap at `anvil/knowledge/decisions/roadmap-anvil-phase-2-strategic-audit-2026-04-13.md` and the pre-flight diagnostic findings at `anvil/knowledge/research/phase2-preflight-diagnostic-2026-04-14.md`. Design the blueprint for `find_intent_gaps()` — a new finding type in `src/lab.py`. The blueprint must specify: (1) **Function signature:** `find_intent_gaps(conn, project_name: str, project_path: str, top_n: int = 20) -> list[dict]` where each dict has keys: `finding_type`, `severity`, `title`, `what`, `why_it_matters`, `what_needs_discovering`, `success_looks_like`, `diagnostic_type`, `chunk_ids` (list of related chunk IDs from DB). (2) **Intent loading:** reads `{project_path}/PROJECT_BRIEF.md` and `{project_path}/knowledge/research/domain-glossary.md` via Python file I/O — returns empty list with a warning log if either file is missing. (3) **Structural signal query:** queries DB for top N findings by composite score across three existing finding types: coverage_gaps (highest volatility + zero coverage), coupling_hotspots (highest coupling score), complexity_hotspots (highest cyclomatic complexity). Pulls chunk metadata: name, file_path, functional_role, composite_score, structural_metadata. (4) **Context assembly:** returns a structured list where each finding dict contains the project intent text (PROJECT_BRIEF content) and the structural signal (chunk facts) — Claude Code reads this and applies judgment about whether the structural signal represents an intent gap. The function does NOT make LLM calls — it assembles the context package deterministically. (5) **Output deposit:** `find_intent_gaps()` results are written to `{project_path}/knowledge/anvil/audit-findings-{date}.md` by a new function `write_intent_audit(findings, project_path, project_name)` using the Phase 2 finding format from the roadmap (CRITICAL/HIGH/MEDIUM/LOW — title, what, why, what-needs-discovering, success-looks-like, diagnostic-type). Create `{project_path}/knowledge/anvil/` directory if it doesn't exist. (6) **Integration into cycle:** `run_lab()` in `src/lab.py` calls `find_intent_gaps()` after all existing finding types and calls `write_intent_audit()` if results are non-empty. Add `intent_gaps` to the cycle report's finding counts. (7) **New DB table:** none required — intent gaps are computed fresh each cycle from existing tables, not persisted. (8) **Test contract:** two testable behaviors — (a) returns empty list when PROJECT_BRIEF missing, (b) returns list of dicts with all required keys when called with a mock DB containing at least one coverage_gap chunk. Deposit blueprint to `anvil/knowledge/architecture/phase21-intent-layer-blueprint-2026-04-14.md` via Python file I/O. Commit: `docs: Phase 2.1 SA blueprint — intent cross-reference layer`. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — DEV

---

> Before starting, read `anvil/knowledge/architecture/phase21-intent-layer-blueprint-2026-04-14.md` and check the Output Receipt status. If not Complete, stop and report to CEO. Read your specialist file at `anvil/agents/ANVIL_DEVELOPER.md`. Implement the Phase 2.1 intent layer per the SA blueprint exactly: (1) Add `find_intent_gaps(conn, project_name, project_path, top_n=20)` to `src/lab.py` — reads PROJECT_BRIEF.md and domain-glossary.md, queries DB for top N structural signals across coverage_gaps/coupling_hotspots/complexity_hotspots, assembles and returns list of finding dicts with all blueprint-specified keys. (2) Add `write_intent_audit(findings, project_path, project_name)` to `src/lab.py` — creates `{project_path}/knowledge/anvil/` directory, writes findings to `audit-findings-{YYYY-MM-DD}.md` using the Phase 2 finding format. (3) Integrate both functions into `run_lab()` — call after existing finding types, call `write_intent_audit()` if findings non-empty, add intent_gaps count to cycle report summary. (4) Add `intent_gaps` section to `write_cycle_report()` in `src/lab.py`. (5) Add `knowledge/anvil/` directory creation to `invoice-pulse` setup if running against invoice-pulse. (6) Write tests in `anvil/tests/test_lab.py`: `test_find_intent_gaps_missing_brief` — calls with a temp project path with no PROJECT_BRIEF.md, asserts returns empty list; `test_find_intent_gaps_returns_required_keys` — calls with a mock DB and temp project path containing a minimal PROJECT_BRIEF.md, asserts every returned dict has keys: finding_type, severity, title, what, why_it_matters, what_needs_discovering, success_looks_like, diagnostic_type, chunk_ids. Run full test suite: `python3 -m pytest tests/ -v`. All must pass. Commit: `feat: Phase 2.1 — intent cross-reference layer (find_intent_gaps + write_intent_audit)`. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 3. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 3 — QA

---

> Before starting, read `anvil/knowledge/architecture/phase21-intent-layer-blueprint-2026-04-14.md` and the DEV step Output Receipt. If either is not Complete, stop and report to CEO. Read your specialist file at `anvil/agents/ANVIL_QA_ANALYST.md`. **Deliverable verification:** grep `src/lab.py` for `find_intent_gaps`, `write_intent_audit`, `intent_gaps`, `knowledge/anvil` — all must be present. Grep `tests/test_lab.py` for `test_find_intent_gaps_missing_brief` and `test_find_intent_gaps_returns_required_keys`. **Re-run full test suite:** `python3 -m pytest tests/ -v` — write raw output to `anvil/knowledge/qa/evidence/phase21/pytest_full.txt` via Python file I/O. **Live smoke test:** run `python3 -c "from src.lab import find_intent_gaps; import sqlite3; conn = sqlite3.connect('anvil/anvil.db'); result = find_intent_gaps(conn, 'invoice-pulse', '/Users/marklehn/Desktop/GitHub/invoice-pulse', top_n=5); print(f'findings: {len(result)}'); print('keys ok:', all(k in result[0] for k in ['finding_type','severity','title','what']) if result else 'no findings — check PROJECT_BRIEF path')"` — write output to `anvil/knowledge/qa/evidence/phase21/smoke_intent_gaps.txt`. **Audit deposit verification:** confirm `invoice-pulse/knowledge/anvil/` directory exists after smoke test (or would be created on first run). Write to `anvil/knowledge/qa/evidence/phase21/smoke_deposit_dir.txt`. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Deposit QA report to `anvil/knowledge/qa/phase21-qa-2026-04-14.md`. **Run Rule 20 self-check:**
> ```python
> import os, sys
> qa_report_path = "anvil/knowledge/qa/phase21-qa-2026-04-14.md"
> evidence_dir = "anvil/knowledge/qa/evidence/phase21/"
> required_evidence_files = ["pytest_full.txt", "smoke_intent_gaps.txt", "smoke_deposit_dir.txt"]
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
> If self-check fails, stop and report to CEO. If passes: update `anvil/PROJECT_STATUS.md` — add entry: "2026-04-14: Phase 2.1 complete — intent cross-reference layer shipped. find_intent_gaps() + write_intent_audit() live. invoice-pulse/knowledge/anvil/ deposit folder established." Move plan to Done: `import shutil; shutil.move("anvil/knowledge/decisions/in-progress-executable-phase21-intent-layer-2026-04-14.md", "anvil/knowledge/decisions/Done/executable-phase21-intent-layer-2026-04-14.md")`. Commit: `chore: QA report — Phase 2.1 intent layer`. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
