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

### 2026-04-14 — Diagnostic: table name mismatch in plan query
**Plan step:** diagnostic-coupling-hotspots-noise — item (3) query.
**What happened:** The diagnostic plan specified `chunks` and `chunk_scores` as table names. The actual DB uses `code_chunks` and `health_scores`. The query raised `sqlite3.OperationalError: no such table: chunks`. Adapted inline before proceeding.
**Recommendation:** Future diagnostic plans that embed SQL queries should use the canonical table names: `code_chunks`, `health_scores`, `chunk_dependencies`, `chunk_similarities`. The mismatch suggests the plan was authored from an earlier schema draft.

### 2026-04-14 — Cycle 11 re-run: cycle_number DB offset
**Plan step:** Step 1 fix/re-run — re-ran cycle after heading fix.
**What happened:** The first Cycle 11 run (with empty mission) was stored as cycle_number=11. The fix re-run was stored as cycle_number=12. QA Step 2's DB check queries `WHERE cycle_number=11` — this will return the unfixed run, not the corrected one. The cycle number in cycle_reports does not match the plan name.
**Recommendation:** Plan prompts for QA that check `WHERE cycle_number=N` should reference the actual DB cycle number from the dev log, not the plan label. Or: re-run should delete the stale cycle_report row before re-running to preserve the expected cycle_number.

### 2026-04-14 — QA manual recovery: Bellows write-race stranded plan
**Agent:** Anvil QA Analyst
**Prompt type:** Manual Bellows-recovery bootstrap (not a plan file routed through Bellows).
**What happened:** The `executable-anvil-test-failures-fixture-2026-04-14` plan was deposited but stranded due to a write-race during the Bellows plan deposit phase. DEV's fix commit (`c49f060`) landed successfully, but the plan was never routed to QA via Bellows. A manual QA bootstrap prompt was used to verify deliverables, run the full test suite, deposit evidence, write the QA report, pass Rule 20, update PROJECT_STATUS.md, and move the plan to Done.
**Recommendation:** Write-races during plan deposit can strand plans in a limbo state where DEV work is done but QA never executes. When this happens, a manual QA bootstrap prompt can recover the closeout. Consider adding a Bellows health-check that detects plans with completed DEV commits but no QA evidence after a timeout period.

### 2026-05-18 — Diagnostic: working directory mismatch in Bellows worktree
**Agent:** Anvil Systems Analyst
**Prompt type:** Bellows-dispatched diagnostic via worktree.
**What happened:** The diagnostic plan references paths as `anvil/knowledge/...` and `anvil/anvil.db`, but the Bellows worktree root IS the anvil directory (no `anvil/` subdirectory). The DB (`anvil.db`) is not in the worktree at all — it's in the main repo at `/Users/marklehn/Developer/GitHub/anvil/anvil.db`. Agent had to discover this and adapt paths.
**Recommendation:** Diagnostic plans dispatched through Bellows worktrees should: (1) not assume an `anvil/` prefix in paths — use relative paths from repo root, and (2) explicitly state whether the DB is in the worktree or in the main repo, since worktrees may not include untracked/gitignored files like `.db`.

### 2026-05-18 — Diagnostic: cycle 9 double-count anomaly not pre-documented
**Agent:** Anvil Systems Analyst
**What happened:** Cycle 9 has 7,672 health_scores vs. 3,836 for cycles 10-16. The diagnostic had to choose cycle 10 as anchor instead of cycle 9 (the "first production run on 2026-04-14") to avoid data quality issues. This anomaly was not mentioned in PROJECT_STATUS or the BACKLOG entry.
**Recommendation:** Known data quality issues in the DB should be documented in PROJECT_STATUS or a data-quality knowledge file so that future diagnostics can reference them rather than discovering them ad hoc.

### 2026-05-18 — Diagnostic: volatility-attribution-replay plan quality — strong
**Agent:** Anvil Systems Analyst
**Prompt type:** Bellows-dispatched diagnostic via worktree.
**What happened:** The plan was well-structured and specific. The 8-part investigation sequence was logical and the verification step (part 2) was critical — it caught potential replay errors before the analysis began. The classification thresholds (SELF_DECAYED: raw_delta ≤ -50%, DISPLACED: |raw_delta| < 20%) were reasonable but unnecessary — the actual data was so extreme (79-100% raw drops across all 20 chunks) that any reasonable threshold would have produced the same result.
**Minor issue:** The plan specified that raw volatility is "typically a commit count or weighted commit-recency sum" — the scorer actually uses a linear-decay weighted sum (`max(0, 1 - days_ago/28)`), which is meaningfully different from a simple commit count. The plan's instruction to "read scorer.py before writing replay queries" correctly anticipated this.
**No path issues:** The worktree path issue noted in the previous entry also applied here. The DB was at `/Users/marklehn/Developer/GitHub/anvil/anvil.db`, not in the worktree.

### 2026-05-18 — QA recovery: DEV commit SHA mismatch due to rebase
**Agent:** Anvil QA Analyst
**Prompt type:** Bellows-dispatched QA recovery via worktree.
**What happened:** The plan references DEV commit `d68191e`, but on main the equivalent commit is `155f3d1` (rebased). Tree hashes are identical (`79fd4a2`), `git diff` between them is empty. The SHA `d68191e` exists on branch `f9-follow-scoring-methodology-fix-2026-05-18` but is not an ancestor of HEAD/main. Check (6) ("commit landed on main") required interpreting "present" as "content-equivalent commit present" rather than exact SHA match.
**Recommendation:** When Bellows worktrees rebase feature branches onto main, the plan's DEV commit SHA may no longer match main's history. QA plans that reference a specific SHA for verification should either: (1) include the main-branch SHA as a fallback, or (2) specify tree-hash verification as an acceptable alternative to exact SHA matching.
