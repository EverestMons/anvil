# Anvil — Phase 2 Pre-Flight Diagnostic
**Date:** 2026-04-14 | **Type:** diagnostic | **Status:** Pending

## Purpose

Two goals: (1) audit Anvil specialist files for staleness against the current pipeline (Phases 0-9 complete), (2) produce a structured current-state summary that Phase 2.1 planning can reference directly — pipeline shape, schema tables, finding types, scoring dimensions, and any gaps.

---

## STEP 1 — Investigation

---

> **FIRST — claim this diagnostic:** `import shutil; shutil.move("anvil/knowledge/decisions/diagnostic-phase2-preflight-2026-04-14.md", "anvil/knowledge/decisions/in-progress-diagnostic-phase2-preflight-2026-04-14.md")`. Skip specialist file and glossary reads — this IS the specialist audit. Working directory is `/Users/marklehn/Desktop/GitHub/`. **Section A — Specialist file audit.** Read all three specialist files: `anvil/agents/ANVIL_SYSTEMS_ANALYST.md`, `anvil/agents/ANVIL_DEVELOPER.md`, `anvil/agents/ANVIL_QA_ANALYST.md`. For each file check: (1) does the Domain Focus mention classification, provenance, best practices, research recommendations? (2) does the Key Sources list reference Phase 7-9 blueprints (`phase7-classification-blueprint`, `phase8-best-practices-blueprint`, `phase9-research-recs-blueprint`)? (3) does the Project-Specific Context describe the full pipeline as `SCAN → EXTRACT → CLASSIFY → PROVENANCE → SCORE → LAB`? (4) are test counts, chunk counts, or table counts mentioned — and if so, are they current? Produce a staleness table: `| File | Stale Facts | Missing Sections | Severity |`. **Section B — Current pipeline shape.** Read `anvil/src/cycle.py` and `anvil/src/lab.py` — list the exact pipeline stages in order, all finding types lab produces, all Planner constraint types generated, and all cycle report sections written. **Section C — Current schema tables.** Run `python3 -c "import sqlite3; conn = sqlite3.connect('anvil/anvil.db'); tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table' ORDER BY name\").fetchall(); [print(t[0]) for t in tables]; conn.close()"` — list all tables. Cross-check against what the SA specialist file claims exists. **Section D — Live stats snapshot.** Run `python3 -c "import sqlite3; conn = sqlite3.connect('anvil/anvil.db'); print('chunks:', conn.execute('SELECT COUNT(*) FROM code_chunks').fetchone()[0]); print('symbols:', conn.execute('SELECT COUNT(*) FROM chunk_symbol_bindings').fetchone()[0]); print('health_scores:', conn.execute('SELECT COUNT(*) FROM health_scores').fetchone()[0]); print('best_practices:', conn.execute('SELECT COUNT(*) FROM best_practices').fetchone()[0]); conn.close()"` — capture current counts. **Section E — Phase 2 readiness gaps.** Based on Sections A-D, list what the Phase 2 strategic audit layer needs that doesn't exist yet: does `src/` have any file that reads PROJECT_BRIEF.md or domain glossary? Does any finding type currently cross-reference project intent? Is there a `knowledge/anvil/` deposit folder in invoice-pulse? Produce a gaps table: `| Gap | Impact on Phase 2.1 | Priority |`. Deposit full findings to `anvil/knowledge/research/phase2-preflight-diagnostic-2026-04-14.md` via Python file I/O using `with open()`. Include all five sections with tables. Commit: `docs: phase2 preflight diagnostic`. Standard prompt feedback protocol → `anvil/knowledge/research/agent-prompt-feedback.md`.

---
## Output Receipt
**Agent:** Anvil Developer
**Step:** 1
**Status:** Complete

### Flags for CEO
- None
