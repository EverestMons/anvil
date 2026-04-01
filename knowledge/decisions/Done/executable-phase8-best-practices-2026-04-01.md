# anvil — Phase 8: Best Practices Knowledge Base + Purpose-Aware Scoring
**Date:** 2026-04-01 | **Tier:** Medium | **Execution:** Step 1 (SA) → Step 2 (DEV) → Step 3 (QA)
**Depends on:** `executable-phase7-classification-2026-04-01.md`

## How to Run This Plan

**Bootstrap:**
```
Read the plan at anvil/knowledge/decisions/executable-phase8-best-practices-2026-04-01.md. Execute Step 1. After completing Step 1, stop and wait for my confirmation before proceeding to Step 2.
```

---
---

## STEP 1 — ANVIL SYSTEMS ANALYST

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/executable-phase8-best-practices-2026-04-01.md", "/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/in-progress-executable-phase8-best-practices-2026-04-01.md")`. You are the Anvil Systems Analyst. Read your specialist file. Read the Phase 7 blueprint at `anvil/knowledge/architecture/phase7-classification-blueprint-2026-04-01.md` for the functional_roles schema. Read the diagnostic Q11 (best practices seed list) at `anvil/knowledge/research/execution-plan-archive-analysis-2026-04-01.md`. Read `src/scorer.py` for the current scoring formulas. **Produce a blueprint for best practices + purpose-aware scoring.**
>
> **Blueprint must cover:** (1) **`best_practices` table.** Schema: id, functional_role (FK), pattern_name, description, detection_hint (regex or AST pattern for checking if code follows the practice), source (where the practice comes from — "curated", "web_research", "cross_project"), severity (low/medium/high), created_at. (2) **Best practices seed data.** 15 initial patterns from the diagnostic (3 per top 5 role: route_handler, confidence_engine, validation_gate, utility, data_model). Exact INSERT statements. (3) **Role-specific scoring weights.** New config: `ROLE_SCORING_WEIGHTS` dict mapping functional_role → {volatility, coverage, complexity, coupling, staleness}. Default weights stay for unclassified. Proposed per-role weight adjustments (e.g., route_handler: higher complexity weight, lower coupling weight; validation_gate: lower complexity weight since gates are inherently complex, higher coverage weight). (4) **Purpose-relative thresholds.** Per-role threshold overrides — a route_handler flags at CC > 5, a validation_gate flags at CC > 20. Store in `functional_roles.scoring_weights` JSON alongside weights. (5) **Scorer modifications.** `score_project()` looks up chunk.functional_role, fetches role-specific weights and thresholds. Composite score computed with role weights. Findings thresholds adjusted per role. Fallback to default for NULL functional_role. (6) **Web research hook.** A function signature in the Lab that Claude Code calls when a role has <2 best practice entries: `research_best_practices(role_name, existing_practices) → new_practices`. Claude Code reads the role description, searches for established patterns, and inserts new best_practices rows. This is not automated — it runs when Claude Code is in a Lab session. (7) **How to verify.**
>
> Deposit blueprint to `anvil/knowledge/architecture/phase8-best-practices-blueprint-2026-04-01.md` using `with open()`. Standard prompt feedback protocol.

---
---

## STEP 2 — ANVIL DEVELOPER

---

> Before starting, read `anvil/knowledge/architecture/phase8-best-practices-blueprint-2026-04-01.md` and check the Output Receipt status. If not Complete, stop and report. You are the Anvil Developer. Read your specialist file.
>
> **Task 1 — Best practices table + seed.** Add `best_practices` table to `src/db.py`. Seed with 15 initial patterns. Runtime migration for live DB. Commit: `"feat: best_practices table + 15 seed patterns"`.
>
> **Task 2 — Role-specific scoring.** Add `ROLE_SCORING_WEIGHTS` and `ROLE_THRESHOLDS` to `src/config.py`. Modify `src/scorer.py` `score_project()` to use role-specific weights when chunk.functional_role is set. Fallback to defaults for NULL. Commit: `"feat: purpose-aware scoring — role-specific weights + thresholds"`.
>
> **Task 3 — Web research hook.** Add `research_best_practices(conn, role_name)` to `src/lab.py`. Queries existing practices for the role, returns a structured prompt for Claude Code to fill. Claude Code searches, then calls `add_best_practice(conn, role, pattern_name, description, source, detection_hint)`. Commit: `"feat: web research hook for best practices discovery"`.
>
> **Task 4 — Tests.** Test scoring with role-specific weights (same chunk, different roles → different scores). Test best practices CRUD. Test fallback to default weights. Commit: `"test: purpose-aware scoring + best practices tests"`.
>
> Run full test suite. Deposit dev log to `anvil/knowledge/development/phase8-best-practices-2026-04-01.md` using `with open()`. Standard prompt feedback protocol.

---
---

## STEP 3 — ANVIL QA ANALYST

---

> Before starting, read `anvil/knowledge/development/phase8-best-practices-2026-04-01.md` and check Output Receipt status. If not Complete, stop and report. **Verify across 6 areas:**
>
> **Area 1 — Best practices table.** Verify 15 seed entries across 5 roles. Query by role — verify 3 per role. PASS/FAIL.
> **Area 2 — Role-specific scoring.** Score a route_handler chunk and a validation_gate chunk with similar structural metrics. Verify they get different composite scores due to different weight profiles. PASS/FAIL.
> **Area 3 — Threshold adjustment.** Verify a validation_gate with CC=15 is NOT flagged as a complexity hotspot (role threshold is higher). Verify a route_handler with CC=15 IS flagged. PASS/FAIL.
> **Area 4 — Fallback.** Score an unclassified chunk (functional_role=NULL). Verify it uses default weights. PASS/FAIL.
> **Area 5 — Existing pipeline.** Run a full cycle. Verify scores change (some chunks now score differently due to role-specific weights). Verify existing finding types still work. PASS/FAIL.
> **Area 6 — Test suite.** Run full test suite. PASS/FAIL.
>
> Deposit QA report to `anvil/knowledge/qa/phase8-best-practices-qa-2026-04-01.md` using `with open()`. **Final:** Update `anvil/PROJECT_STATUS.md`. Move to Done: `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/in-progress-executable-phase8-best-practices-2026-04-01.md", "/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/Done/executable-phase8-best-practices-2026-04-01.md")`. Commit: `"chore: status update + move Phase 8 to Done"`.
