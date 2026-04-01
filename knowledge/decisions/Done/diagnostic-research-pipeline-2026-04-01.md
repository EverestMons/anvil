# anvil — Research Pipeline Evolution Diagnostic
**Date:** 2026-04-01 | **Tier:** Medium | **Execution:** Step 1 (DEV) → Step 2 (DEV)
**Priority:** 1
**Feeds:** Anvil Phase 7-9 roadmap

## How to Run This Plan

**Bootstrap:**
```
Read the plan at anvil/knowledge/decisions/diagnostic-research-pipeline-2026-04-01.md. Execute Step 1. After completing Step 1, stop and wait for my confirmation before proceeding to Step 2.
```

---
---

## STEP 1 — ANVIL DEVELOPER (Current Pipeline Analysis)

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/diagnostic-research-pipeline-2026-04-01.md", "/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/in-progress-diagnostic-research-pipeline-2026-04-01.md")`. You are working in the Anvil project. Read `anvil/PROJECT_BRIEF.md` first. **The CEO wants to evolve Anvil from structural analysis into purpose-aware code quality research. Three new capabilities: (1) functional classification via execution plan lineage, (2) best practices knowledge base with web research, (3) purpose-aware scoring. Before building, we need a complete map of the current pipeline.**
>
> **Q1 — Current schema.** Read `src/db.py`. List every table with its columns. Focus on: `code_chunks` (what fields exist for classification/tagging?), `health_scores` (what dimensions are scored?), `chunk_symbol_bindings` (what binding types exist?). Are there any unused columns or extension points?
>
> **Q2 — Current extractor.** Read `src/extractor.py` and `src/parsers/python_parser.py`. What does extraction currently produce per chunk? What structural_metadata fields are computed? Is there any existing classification or tagging? What would need to change to add a `functional_role` field during extraction?
>
> **Q3 — Current scorer.** Read `src/scorer.py`. What are the 5 scoring dimensions? What are the current formulas/weights? What's the composite score calculation? What would need to change to make scoring purpose-relative (e.g., "complexity is acceptable for a validation gate but not for a route handler")?
>
> **Q4 — Current Lab.** Read `src/lab.py`. What finding types does it produce? What's the cycle report format? How does it generate Planner constraints? What would the Lab need to produce research-backed improvement recommendations instead of just findings?
>
> **Q5 — Config.** Read `src/config.py`. What's configurable? What scoring thresholds exist? What would need to be added for a functional role taxonomy and best practices patterns?
>
> **Q6 — Execution plan format analysis.** Read 5 representative execution plans from `invoice-pulse/knowledge/decisions/Done/` — pick one early (2026-03-14), one mid (2026-03-20), one recent (2026-04-01). Document: (a) what format are they in (markdown structure, step headers), (b) do they reference specific files that were created/modified, (c) do they contain feature descriptions that could serve as functional purpose labels, (d) can we reliably parse "this plan created/modified these files" from the plan text? Also check: do the dev logs in `invoice-pulse/knowledge/development/` contain `Files Created or Modified` sections in their Output Receipts that would be a more reliable source than parsing plans?
>
> **Output:** A findings document covering Q1-Q6 with a "Schema Extension Proposal" section at the end recommending: new tables, new columns on existing tables, new config entries, and the minimal pipeline changes needed for Phases 7-9.
>
> Deposit findings to `anvil/knowledge/research/research-pipeline-diagnostic-2026-04-01.md` using `with open()`. Commit: `"docs: research pipeline evolution diagnostic"`.

---
---

## STEP 2 — ANVIL DEVELOPER (Execution Plan Archive Analysis)

---

> Before starting, verify `anvil/knowledge/research/research-pipeline-diagnostic-2026-04-01.md` exists. You are working in the Anvil project. **Deep analysis of the execution plan archive to validate the provenance-based classification approach.**
>
> **Q7 — Plan archive statistics.** Count all files in `invoice-pulse/knowledge/decisions/Done/`. Break down by type: executable-*, diagnostic-*, roadmap-*, other. Count by month (2026-03-* vs 2026-04-*). How many executable plans exist (these are the ones that create/modify code)?
>
> **Q8 — Dev log Output Receipts.** Read 10 dev logs from `invoice-pulse/knowledge/development/` (mix of dates). Check each for the "Files Created or Modified (Code)" section in the Output Receipt. How many have it? Is the file path format consistent? Could we reliably extract a mapping of {plan_name → [files_modified]} from these receipts? This is potentially more reliable than parsing plans directly since Output Receipts are structured.
>
> **Q9 — Coverage estimate.** Based on Q7-Q8, estimate: what percentage of invoice-pulse's 939 source files could be traced back to an execution plan? Files that predate the orchestration system (before 2026-03-12) won't have plan lineage. Files created by direct CEO commits won't either. What's the coverage gap, and how should Anvil handle chunks with no provenance?
>
> **Q10 — Functional role taxonomy draft.** Based on reading the plan descriptions and IP's specialist files, propose an initial taxonomy of functional roles for invoice-pulse code. Examples: validation_gate, route_handler, import_parser, data_model, template, test_case, engine_module, utility, configuration, copilot_prompt, migration. How many roles? What's the hierarchy (if any)?
>
> **Q11 — Best practices seed list.** For the top 5 functional roles by chunk count, propose 2-3 best practice patterns each. Example: validation_gate → {strategy pattern for per-rule classes, error accumulation not short-circuit, deterministic output format}. These become the initial seed for the `best_practices` table.
>
> Deposit findings to `anvil/knowledge/research/execution-plan-archive-analysis-2026-04-01.md` using `with open()`. **Final:** Move diagnostic to Done: `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/in-progress-diagnostic-research-pipeline-2026-04-01.md", "/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions/Done/diagnostic-research-pipeline-2026-04-01.md")`. Commit: `"docs: execution plan archive analysis + research pipeline diagnostic to Done"`.
