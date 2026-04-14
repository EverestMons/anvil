# Anvil — Phase 2.1 Refinement: Intent Injection + Test File Filter
**Date:** 2026-04-14 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 1

## How to Run This Plan

This plan is picked up and executed by Bellows automatically.

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/executable-phase21-refinement-2026-04-14.md", "anvil/knowledge/decisions/in-progress-executable-phase21-refinement-2026-04-14.md")`. Read your specialist file at `anvil/agents/ANVIL_DEVELOPER.md`. Working directory is `/Users/marklehn/Desktop/GitHub/`. Two targeted fixes to `find_intent_gaps()` in `anvil/src/lab.py`: **Fix 1 — Filter test file paths.** In the coupling hotspots query inside `find_intent_gaps`, add `AND cc.file_path NOT LIKE 'tests/%'` to the WHERE clause. In the complexity hotspots query inside `find_intent_gaps`, add `AND cc.file_path NOT LIKE 'tests/%'` to the WHERE clause. The coverage gaps query already filters `chunk_type != 'test_case'` but add the file path filter there too for consistency. **Fix 2 — Inject project intent into finding text.** Add a helper function `_extract_project_mission(brief_text: str) -> str` that: (1) looks for a line starting with `## Mission` or `## Overview` or `## Purpose` in the brief_text, (2) returns the next non-empty paragraph after that heading (up to 3 sentences), (3) returns an empty string if no such heading found. In `find_intent_gaps`, after loading `brief_text`, call `mission = _extract_project_mission(brief_text)`. Then for each finding dict, replace the generic `what_needs_discovering` template with a version that incorporates mission context when available: if `mission` is non-empty, `what_needs_discovering` becomes `f"Given that {mission.strip()} — does '{name}' perform logic critical to this mission? What scenarios does it need to handle that are currently {signal_description}?"` where `signal_description` is "untested" for coverage gaps, "a high-blast-radius risk" for coupling hotspots, and "a maintainability concern" for complexity hotspots. If `mission` is empty, keep the existing generic template. **Update tests in `anvil/tests/test_lab.py`:** Add `test_extract_project_mission_found` — creates a temp brief with a `## Mission\n\nSome mission text.` section, calls `_extract_project_mission`, asserts returns "Some mission text.". Add `test_extract_project_mission_not_found` — calls with plain text with no heading, asserts returns empty string. Add `test_find_intent_gaps_excludes_test_files` — uses a mock DB with one chunk in `tests/test_foo.py` and one in `app.py`, calls `find_intent_gaps`, asserts no finding has `chunk_file` starting with `tests/`. **Run full test suite:** `python3 -m pytest tests/ -v`. All must pass. Commit: `fix: Phase 2.1 refinement — test file filter + project intent injection`. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, read the Step 1 Output Receipt. If not Complete, stop and report to CEO. Read your specialist file at `anvil/agents/ANVIL_QA_ANALYST.md`. **Deliverable verification:** grep `anvil/src/lab.py` for `NOT LIKE 'tests/%'` (must appear 3 times — one per query), `_extract_project_mission`, `mission.strip()`. Grep `anvil/tests/test_lab.py` for `test_extract_project_mission_found`, `test_extract_project_mission_not_found`, `test_find_intent_gaps_excludes_test_files`. **Re-run full test suite:** `python3 -m pytest tests/ -v` — write raw output to `anvil/knowledge/qa/evidence/phase21-refinement/pytest_full.txt` via Python file I/O. **Live smoke test:** run `python3 -c "from anvil.src.lab import _extract_project_mission; result = _extract_project_mission('## Mission\n\nBuild great software.\n\n## Other section'); print(repr(result))"` from `/Users/marklehn/Desktop/GitHub/` — assert prints a non-empty string. Write to `anvil/knowledge/qa/evidence/phase21-refinement/smoke_mission.txt`. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Deposit QA report to `anvil/knowledge/qa/phase21-refinement-qa-2026-04-14.md`. **Run Rule 20 self-check:**
> ```python
> import os, sys
> qa_report_path = "anvil/knowledge/qa/phase21-refinement-qa-2026-04-14.md"
> evidence_dir = "anvil/knowledge/qa/evidence/phase21-refinement/"
> required_evidence_files = ["pytest_full.txt", "smoke_mission.txt"]
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
> If self-check fails, stop and report to CEO. If passes: update `anvil/PROJECT_STATUS.md` — add entry: "2026-04-14: Phase 2.1 refinement — test file filter + intent injection shipped." Move plan to Done: `import shutil; shutil.move("anvil/knowledge/decisions/in-progress-executable-phase21-refinement-2026-04-14.md", "anvil/knowledge/decisions/Done/executable-phase21-refinement-2026-04-14.md")`. Commit: `chore: QA report — Phase 2.1 refinement`. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.
>
> ---
> ## Output Receipt
> **Agent:** Anvil QA Analyst
> **Step:** 2
> **Status:** Complete
>
> ### Flags for CEO
> - None
