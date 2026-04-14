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

### 2026-04-14 — Cycle 11: mission heading mismatch — "Given that" not injected (RESOLVED)
**Plan step:** Step 1 — run_cycle then check mission context in what_needs_discovering.
**What happened:** `_extract_project_mission()` in `src/lab.py` looks for headings `## Mission`, `## Overview`, or `## Purpose`. invoice-pulse's PROJECT_BRIEF.md uses `## What This Project Is`. The function returns empty string; all 20 findings fall back to the non-mission template (references PROJECT_BRIEF conceptually but omits the "Given that {mission}" sentence). QA Step 2 grep-for-"Given that" will return zero matches.
**Resolution:** Heading pattern expanded to include `What This Project Is`, `About`, `Summary`, `Background`. Re-run confirmed "Given that" present in all findings.
**Recommendation:** Future project briefs should be aware that `_extract_project_mission` extracts from the first `## Mission`, `## Overview`, `## Purpose`, `## What This Project Is`, `## About`, `## Summary`, or `## Background` heading. If none match, mission context will be absent from findings.

### 2026-04-14 — Cycle 11 re-run: cycle_number DB offset
**Plan step:** Step 1 fix/re-run — re-ran cycle after heading fix.
**What happened:** The first Cycle 11 run (with empty mission) was stored as cycle_number=11. The fix re-run was stored as cycle_number=12. QA Step 2's DB check queries `WHERE cycle_number=11` — this will return the unfixed run, not the corrected one. The cycle number in cycle_reports does not match the plan name.
**Recommendation:** Plan prompts for QA that check `WHERE cycle_number=N` should reference the actual DB cycle number from the dev log, not the plan label. Or: re-run should delete the stale cycle_report row before re-running to preserve the expected cycle_number.

