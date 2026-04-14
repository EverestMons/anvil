# Anvil — Fix: PROJECT_STATUS.md Last Updated Date
**Date:** 2026-04-14 | **Tier:** Small | **Test Scope:** n/a (no code change) | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 1

## How to Run This Plan

This plan is picked up and executed by Bellows automatically.

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("anvil/knowledge/decisions/executable-project-status-date-fix-2026-04-14.md", "anvil/knowledge/decisions/in-progress-executable-project-status-date-fix-2026-04-14.md")`. Skip specialist file and glossary reads — cosmetic single-field update. Working directory is `/Users/marklehn/Desktop/GitHub/anvil/`. Update the "Last Updated" field at the top of `PROJECT_STATUS.md`. The current value is `**Last Updated:** 2026-04-01` (stale). Replace it with `**Last Updated:** 2026-04-14`. Use Python file I/O to make the edit — read the file, replace the single line, write it back. Do not touch any other line. Do not change the "Status:" line. Do not add any other content. Verify the change via `grep "Last Updated" PROJECT_STATUS.md` — must print exactly `**Last Updated:** 2026-04-14`. Commit: `docs: update PROJECT_STATUS.md last updated date to 2026-04-14`. Standard prompt feedback protocol → `knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed via `git --no-pager log --oneline -3` from `/Users/marklehn/Desktop/GitHub/anvil/`. Skip specialist file and glossary reads — trivial verification. **Deliverable verification:** grep `PROJECT_STATUS.md` for `Last Updated` — must return exactly one line containing `2026-04-14`. Must NOT return any line containing `2026-04-01`. Write grep output to `knowledge/qa/evidence/project-status-date-fix/grep_last_updated.txt` via Python file I/O. Also run `git --no-pager show HEAD --stat` to confirm exactly one file changed (`PROJECT_STATUS.md`) with a 1-line delta. Write output to `knowledge/qa/evidence/project-status-date-fix/git_show_stat.txt`. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |` covering: Last Updated field now shows 2026-04-14, no stale 2026-04-01 reference remains, commit touched only PROJECT_STATUS.md, diff is 1 line. Deposit QA report to `knowledge/qa/project-status-date-fix-qa-2026-04-14.md`. **Run Rule 20 self-check:**
> ```python
> import os, sys
> qa_report_path = "knowledge/qa/project-status-date-fix-qa-2026-04-14.md"
> evidence_dir = "knowledge/qa/evidence/project-status-date-fix/"
> required_evidence_files = ["grep_last_updated.txt", "git_show_stat.txt"]
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
> Run from `/Users/marklehn/Desktop/GitHub/anvil/`. If self-check fails, stop and report to CEO. If passes: move plan to Done: `import shutil; shutil.move("knowledge/decisions/in-progress-executable-project-status-date-fix-2026-04-14.md", "knowledge/decisions/Done/executable-project-status-date-fix-2026-04-14.md")`. Commit: `chore: QA report — PROJECT_STATUS date fix`. Do NOT add a PROJECT_STATUS.md entry for this plan (it would be meta and trigger another staleness loop). Standard prompt feedback protocol → `knowledge/research/agent-prompt-feedback.md`.
