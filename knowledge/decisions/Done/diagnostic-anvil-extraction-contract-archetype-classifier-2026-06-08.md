# Anvil — Design Diagnostic: Extraction Contract + Archetype-Pluggable Classifier
**Date:** 2026-06-08 | **Tier:** Medium | **Dispatch Mode:** bellows | **Test Scope:** none | **Execution:** Step 1 (SA) | **Priority:** 2

**auto_close:** false
**pause_for_verdict:** after_step_1

## Context

Anvil is being treated as a shop-standard forge tool: applied to every Eluvian software project as a matter of practice, not case-by-case. The shop spans archetypes (Flask service, autonomous daemon, Tauri/React app, SwiftUI app, CLI/pipeline) and languages (Python today; Swift, TS/JS later). The governing model is "one tool, swappable heads on a common handle": the **handle** (findings vocabulary, scoring framework, cycle lifecycle, DB schema, Bellows integration) is invariant; the **heads** (language extraction, archetype role taxonomy) vary and must be small, well-defined adapters — not parallel tools that drift.

Two things are currently hardcoded to a single project/language and block that model: (1) the core engine is implicitly coupled to whatever `python_parser.py` emits — there is no explicit chunk contract; (2) the classifier is a global regex chain of invoice-pulse rules, so every other project classifies as `utility`.

This diagnostic designs the seam, it does NOT implement it. Output is a design blueprint. The keystone is formalizing the extraction contract; the archetype-pluggable classifier hangs off it. study's chunk schema is examined as a same-shape (heterogeneous source → normalized record → consumer) in-shop precedent — for its boundary *shape*, not its chunking heuristics (which don't transfer: study splits prose semantically, Anvil splits code by grammar).

Read-only design analysis. No source changes. Single SA step; terminal pause for CEO review of the blueprint before any implementation plan is authored.

## How to Run This Plan

Bellows dispatches automatically on deposit. One SA step runs, then the plan pauses for the CEO verdict (`pause_for_verdict: after_step_1`, `auto_close: false`).

---
---

## STEP 1 — ANVIL SYSTEMS ANALYST

---

> **Identity:** You are the Anvil Systems Analyst. **Reads (in order):** `agents/ANVIL_SYSTEMS_ANALYST.md`, `src/parsers/python_parser.py`, `src/db.py` (the `code_chunks` schema and any dependency/edge tables), `src/classifier.py`, `src/scorer.py`, `src/lab.py` (the finding functions that consume chunks), `src/config.py` (`SCORING_WEIGHTS`, `ROLE_SCORING_WEIGHTS`, `ROLE_THRESHOLDS`), and `src/cycle.py` (how extract/score/classify are wired).
>
> **Working directory note:** the worktree IS the anvil root; use relative paths for anvil source. study is a separate repo — read it read-only at the absolute path `/Users/marklehn/Developer/GitHub/study/`.
>
> **This is a READ-ONLY design diagnostic. Modify NO source.** The deliverable is a design blueprint document. If any premise below turns out to be wrong (e.g. complexity is already computed language-agnostically, or the core is already decoupled from the parser), say so explicitly and adjust the design rather than forcing the stated framing.
>
> **Task:** Produce a design blueprint for making Anvil a multi-archetype, multi-language-*ready* forge tool, via (1) an explicit extraction contract that decouples the core from the Python parser, and (2) an archetype-keyed classifier registry. Cover these sections:
>
> **A. Current de facto extraction contract.** From `python_parser.py` + the `code_chunks` schema + how `cycle.py`/extract populate chunks, document the exact chunk record produced today: every field, its type and semantics, and whether it is populated by the parser or computed downstream (in particular: where does the complexity metric come from — parser or scorer? where do dependency/coupling edges come from?). Then map every place the downstream core (classifier, scorer, each `lab.py` finding function) reads a chunk field, and label each field language-agnostic vs Python-specific (AST node types, decorators, import edges, etc.).
>
> **B. Proposed extraction contract (the keystone).** Define an explicit `ChunkRecord` interface: the minimal normalized fields the core requires (e.g. name, file_path, content, chunk_type, line span, normalized complexity, dependency edges), marking required vs optional and the semantics each consumer depends on. Specify the producer interface a language extractor ("head") must implement to emit `ChunkRecord`s, and enumerate exactly what the core must STOP assuming about Python so a non-Python head can plug in. List the concrete decoupling edits required — do NOT make them, list them with file/function references.
>
> **C. Archetype-pluggable classifier.** Document the current classifier (global regex chain: decorator → name → file-path → `utility`) and the role→scoring coupling (`ROLE_SCORING_WEIGHTS.get(role, SCORING_WEIGHTS)` at scorer.py; `ROLE_THRESHOLDS`). Design an archetype-keyed registry: a project declares `(language, archetype)`; the classifier loads that archetype's role taxonomy and the archetype/role scoring profiles. Evaluate where rules should live and RECOMMEND one with rationale: (a) central in anvil keyed by archetype, (b) per-project file in each project's own `knowledge/` (e.g. `anvil-roles.*`), (c) hybrid — archetype templates in anvil + per-project overrides — considering ~7–10 shop projects across a small number of archetypes (flask_service, daemon, tauri_react_app, swiftui_app, cli_pipeline). Specify the project→`(language, archetype)` declaration mechanism (extend `SCAN_TARGETS` to carry metadata? a per-project manifest?). Give the migration: how the existing invoice-pulse rules become the first archetype head, and bellows the second (daemon) — and state whether the IP rules collapse to one archetype or split across several.
>
> **D. Study cross-repo reference (shape only).** Locate study's chunk schema and the chunker(producer)→consumer(tutor/retrieval) boundary under `/Users/marklehn/Developer/GitHub/study/` (likely a chunks table in its DB schema plus a chunking module; consumer is the tutoring/retrieval path). Assess explicitly, with evidence (cite the schema + the boundary code): is it a CLEAN normalized contract (one schema, multiple input types, consumer source-agnostic) or TANGLED (chunker coupled into the consumer)? If clean, extract the transferable shape lessons for Anvil's `ChunkRecord` and producer/consumer seam. If tangled, name the specific anti-pattern Anvil must avoid. Do NOT port study's chunking heuristics — only assess the boundary shape.
>
> **E. Synthesis & sequenced build plan.** State the handle/heads architecture (invariant core+contract vs variant archetype-heads + language-extractors). Give a dependency-ordered build sequence (contract definition → core decoupling → IP-rules→first archetype head → bellows as second tenant → additional language extractors LATER and SEPARATE). Estimate effort and call out risks per step. Explicitly flag multi-language extraction (Swift, TS/JS) as a large separate head, out of scope for the first build. End with a crisp recommendation on the rule-location fork (from C) for the CEO to ratify.
>
> **Stage the deposit (required so it survives teardown):**
> ```bash
> git add knowledge/architecture/anvil-extraction-contract-archetype-design-2026-06-08.md
> git status --short knowledge/architecture/anvil-extraction-contract-archetype-design-2026-06-08.md
> ```
> Confirm it shows staged (`A ` prefix). If not, retry the `git add`.
>
> Standard prompt-feedback protocol — append issues to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `knowledge/architecture/anvil-extraction-contract-archetype-design-2026-06-08.md`
