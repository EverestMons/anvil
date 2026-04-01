# anvil — Phase 7: Functional Classification + Provenance
**Date:** 2026-04-01 | **Tier:** Medium | **Execution:** Step 1 (SA) → Step 2 (DEV) → Step 3 (QA)
**Diagnostics:** `research-pipeline-diagnostic-2026-04-01.md`, `execution-plan-archive-analysis-2026-04-01.md`

## How to Run This Plan

**Bootstrap:**
```
Read the plan at anvil/knowledge/decisions/executable-phase7-classification-2026-04-01.md. Execute Step 1. After completing Step 1, stop and wait for my confirmation before proceeding to Step 2.
```

---
---

## STEP 1 — ANVIL SYSTEMS ANALYST

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/executable-phase7-classification-2026-04-01.md", "/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/in-progress-executable-phase7-classification-2026-04-01.md")`. You are the Anvil Systems Analyst. Read your specialist file at `anvil/agents/ANVIL_SYSTEMS_ANALYST.md`. Read both diagnostic deposits: `anvil/knowledge/research/research-pipeline-diagnostic-2026-04-01.md` (Q1-Q6) and `anvil/knowledge/research/execution-plan-archive-analysis-2026-04-01.md` (Q7-Q11). Read the current `src/db.py` for table creation patterns. **Produce a blueprint for functional classification + provenance.**
>
> **Blueprint must cover:** (1) **Schema additions.** `functional_roles` table (name UNIQUE, description, parent_role nullable, scoring_weights TEXT/JSON for Phase 8). `chunk_provenance` table (chunk_id FK CASCADE, plan_name, dev_log_path, plan_description). ALTER code_chunks ADD functional_role TEXT (FK-like but nullable, no strict FK constraint since roles are seeded separately). Runtime migration for live DB. (2) **Functional role taxonomy seed.** The 25 roles from Q10 with descriptions. Specify exact INSERT statements. (3) **Heuristic classifier module.** New `src/classifier.py`. Takes a code_chunk dict (name, file_path, content, chunk_type, structural_metadata) and returns a functional_role string. Classification rules in priority order: decorator patterns (highest — `@bp.route` → route_handler), naming conventions (gate_N_ → validation_gate, test_ → test_case, _migrate_ → data_model), file path patterns (engines/ → engine_module, web/templates/ → template, tests/ → test_case), base class patterns (from imports/AST). Fallback: "utility" for functions, "configuration" for module-level code in config files, None for truly ambiguous. Spec the exact rules as a config-driven lookup table. (4) **Dev log parser module.** New `src/provenance.py`. Reads markdown files from a dev log directory. For each file: extracts the "Files Created or Modified (Code)" section via multi-pattern header search, parses bullet entries (`- filepath -- description`) and table entries. Returns list of {dev_log_name, plan_slug, file_paths: [{path, description}]}. Spec the regex patterns. (5) **Provenance ingestion.** `ingest_provenance(conn, dev_log_dir)` — parses all dev logs, matches file_paths to code_chunks by file_path, populates chunk_provenance. Plan_slug derived from dev_log filename. (6) **Classification pipeline.** `classify_project(conn, project_name)` — runs heuristic classifier on all chunks, then enriches with provenance (provenance plan_description informs role for ambiguous cases). Stores on code_chunks.functional_role. (7) **Integration into cycle.** Where in the SCAN → EXTRACT → SCORE → LAB pipeline does classification run? After EXTRACT, before SCORE (scorer needs functional_role). (8) **How to verify.**
>
> Deposit blueprint to `anvil/knowledge/architecture/phase7-classification-blueprint-2026-04-01.md` using `with open()`. Standard prompt feedback protocol.

---
---

## STEP 2 — ANVIL DEVELOPER

---

> Before starting, read `anvil/knowledge/architecture/phase7-classification-blueprint-2026-04-01.md` and check the Output Receipt status. If not Complete, stop and report. You are the Anvil Developer. Read your specialist file at `anvil/agents/ANVIL_DEVELOPER.md`.
>
> **Task 1 — Schema + migrations.** Add `functional_roles`, `chunk_provenance` tables to `src/db.py`. Add `functional_role` column to `code_chunks`. Runtime migration for live anvil.db. Seed 25 roles on table creation. Commit: `"feat: functional_roles + chunk_provenance tables + code_chunks.functional_role column"`.
>
> **Task 2 — Heuristic classifier.** Create `src/classifier.py` per blueprint. Config-driven classification rules. `classify_chunk(chunk_dict) → str|None`. `classify_project(conn, project_name)` classifies all chunks and updates code_chunks.functional_role. Commit: `"feat: heuristic functional role classifier"`.
>
> **Task 3 — Dev log parser + provenance ingestion.** Create `src/provenance.py` per blueprint. `parse_dev_logs(dev_log_dir) → list[dict]`. `ingest_provenance(conn, dev_log_dir)` populates chunk_provenance. Commit: `"feat: dev log parser + provenance ingestion"`.
>
> **Task 4 — Pipeline integration.** Wire `classify_project()` into `src/cycle.py` after extraction, before scoring. Wire `ingest_provenance()` into the cycle (runs once on first cycle, then incremental on new dev logs). Commit: `"feat: wire classification + provenance into cycle pipeline"`.
>
> **Task 5 — Tests.** Test classifier: known chunks → expected roles (route_handler, validation_gate, test_case, utility). Test dev log parser: sample dev log → expected file list. Test provenance: mock dev logs + chunks → provenance populated. Test pipeline: full cycle includes classification step. Commit: `"test: classifier + provenance + pipeline integration tests"`.
>
> Run full Anvil test suite. Deposit dev log to `anvil/knowledge/development/phase7-classification-2026-04-01.md` using `with open()`. Standard prompt feedback protocol.

---
---

## STEP 3 — ANVIL QA ANALYST

---

> Before starting, read `anvil/knowledge/development/phase7-classification-2026-04-01.md` and check the Output Receipt status. If not Complete, stop and report. You are the Anvil QA Analyst. Read your specialist file at `anvil/agents/ANVIL_QA_ANALYST.md`. **Verify across 7 areas:**
>
> **Area 1 — Schema.** Verify `functional_roles` has 25 rows. Verify `chunk_provenance` table exists. Verify `code_chunks.functional_role` column exists. PASS/FAIL.
> **Area 2 — Classification.** Run classifier against invoice-pulse chunks. Verify: route_handler chunks are in web/ files with @route decorators, validation_gate chunks match gate_N_ naming, test_case chunks are in tests/ directory. Spot check 10 chunks across 5 roles. PASS/FAIL.
> **Area 3 — Coverage.** Count classified vs unclassified chunks. Verify >80% have a functional_role assigned. List the top unclassified chunks. PASS/FAIL.
> **Area 4 — Provenance.** Run provenance ingestion against invoice-pulse dev logs. Verify chunk_provenance has entries. Spot check 5 entries: dev_log_path is valid, plan_name is reasonable, linked chunk exists. PASS/FAIL.
> **Area 5 — Pipeline.** Run a full cycle. Verify classification runs after extraction, before scoring. Verify functional_role is populated before scorer reads it. PASS/FAIL.
> **Area 6 — Existing pipeline.** Verify scanner, extractor, scorer, lab still produce correct output (no regressions). PASS/FAIL.
> **Area 7 — Test suite.** Run full Anvil test suite. PASS/FAIL.
>
> Deposit QA report to `anvil/knowledge/qa/phase7-classification-qa-2026-04-01.md` using `with open()`. **Final:** Update `anvil/PROJECT_STATUS.md`. Move to Done: `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/in-progress-executable-phase7-classification-2026-04-01.md", "/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/Done/executable-phase7-classification-2026-04-01.md")`. Commit: `"chore: status update + move Phase 7 to Done"`.
