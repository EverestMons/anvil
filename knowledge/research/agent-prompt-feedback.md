# Anvil — Agent Prompt Feedback Log

## Patterns Identified

### 2026-04-14 — Cycle 9: run_cycle() argument count mismatch
**Plan step:** Step 1 — run_cycle call specified 3 arguments: `run_cycle(conn, "invoice-pulse", "/Users/marklehn/Desktop/GitHub/invoice-pulse")`.
**What happened:** The current `run_cycle()` signature only accepts 2 args (`conn`, `project_name`). The project path is resolved internally via config. The call raised `TypeError: run_cycle() takes 2 positional arguments but 3 were given`. Corrected inline.
**Recommendation:** Plan prompts for `run_cycle` calls should match the current 2-arg signature. Consider adding a note in `cycle.py` docstring or PLANNER_TEMPLATE.md that the path arg was removed.

### 2026-04-14 — Specialist Sync: find-and-replace string mismatch
**Plan step:** Step 1B change (3) — replace `'SCAN → EXTRACT → SCORE → LAB'` in ANVIL_SYSTEMS_ANALYST.md Role Summary.
**What happened:** The plan's find string used arrow notation (`→`) but the file used comma notation `(SCAN, EXTRACT, SCORE, LAB)`. Python find-and-replace silently produced no match; the change was not applied. Caught in Step 2 QA.
**Recommendation:** Plan prompts should verify the exact text present in the file before specifying a find-and-replace string, or use a broader context anchor (e.g., surrounding sentence) rather than only the pipeline string itself.

### 2026-04-14 — Cycle 11: mission heading mismatch — "Given that" not injected
**Plan step:** Step 1 — run_cycle then check mission context in what_needs_discovering.
**What happened:** `_extract_project_mission()` in `src/lab.py` looks for headings `## Mission`, `## Overview`, or `## Purpose`. invoice-pulse's PROJECT_BRIEF.md uses `## What This Project Is`. The function returns empty string; all 20 findings fall back to the non-mission template (references PROJECT_BRIEF conceptually but omits the "Given that {mission}" sentence). QA Step 2 grep-for-"Given that" will return zero matches.
**Recommendation:** Either (a) expand the heading pattern in `_extract_project_mission` to include common variants like `## What This Project Is`, `## About`, `## Description`, or (b) update the QA check to grep for the actual fallback text. Option (a) is more robust across diverse project briefs.

