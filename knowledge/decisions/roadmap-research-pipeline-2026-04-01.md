# anvil — Research Pipeline Evolution Roadmap
**Date:** 2026-04-01
**Type:** Roadmap — multi-phase
**Diagnostics:** `research-pipeline-diagnostic-2026-04-01.md`, `execution-plan-archive-analysis-2026-04-01.md`

---

## Architecture Decisions (CEO, 2026-04-01)

1. **Functional classification from execution plan lineage.** Dev log Output Receipts are the provenance source (structured, parseable, 85-90% coverage). Plans describe intent; dev logs describe outcome. The chain: dev_log → Files Modified → code_chunks → functional_role.
2. **Best practices: built-in knowledge + web research.** Curated seed list (15 patterns across 5 roles) + web research for gaps. Knowledge base grows across cycles.
3. **Scoring = purpose-aware.** Complexity/coupling/coverage evaluated relative to the chunk's functional role. A validation gate can be complex; a route handler shouldn't be. Role-specific weight profiles replace flat weights.
4. **25 functional roles** in the initial taxonomy (expandable). Grouped: Web Layer, Validation Pipeline, Intelligence Layer, Data Layer, Infrastructure.

---

## Phase 7 — Functional Classification + Provenance

**Goal:** Every code chunk knows what it does (functional_role) and where it came from (execution plan lineage).


**Schema changes:**
- New `functional_roles` table (name, description, parent_role, scoring_weights)
- New `chunk_provenance` table (chunk_id FK, plan_name, dev_log_path, plan_description)
- New `functional_role` column on `code_chunks` (FK to functional_roles.name, nullable)

**Deliverables:**
- Seed `functional_roles` with 25 roles from the diagnostic taxonomy
- Heuristic classifier: maps chunks to roles via decorator patterns (@bp.route → route_handler), naming conventions (gate_N → validation_gate, test_ → test_case), file path patterns (engines/ → engine_module, web/ → route_handler), base class patterns (db.Model → data_model)
- Dev log parser: reads `invoice-pulse/knowledge/development/*.md`, extracts "Files Created or Modified (Code)" sections, maps {dev_log → file_paths}
- Plan-to-dev-log linkage: dev log filenames contain plan slugs + dates, matching to execution plan names
- Provenance ingestion: for each dev log, find matching chunks in code_chunks by file_path, populate chunk_provenance
- Classify all existing chunks: heuristic first, provenance enrichment second (provenance description overrides heuristic for ambiguous cases)

**Dependencies:** Phase 6 complete (pipeline operational).

## Phase 8 — Best Practices Knowledge Base + Purpose-Aware Scoring

**Goal:** Anvil knows the professional standard for each functional role and scores code against it.

**Schema changes:**
- New `best_practices` table (functional_role FK, pattern_name, description, detection_hint, source, severity)

**Deliverables:**
- Seed `best_practices` with 15 patterns from the diagnostic (3 per top 5 role)
- Role-specific scoring weights in config: `ROLE_SCORING_WEIGHTS = {role: {vol, cov, comp, coup, stale}}`
- Scorer modification: `score_project()` looks up chunk.functional_role, uses role-specific weights (fallback to default for unclassified)
- Purpose-relative thresholds: a route_handler with CC > 5 is flagged; a validation_gate with CC > 5 is acceptable
- Web research capability in Lab: when a role has no best practice entries, Claude Code researches established patterns and populates the table
- Best practices accumulate across cycles — new patterns discovered via research or cross-project comparison get added

**Dependencies:** Phase 7 complete (functional classification populated).

## Phase 9 — Research Recommendations in Lab

**Goal:** Lab produces actionable improvement strategies backed by best practices, not just structural findings.

**Deliverables:**
- New finding type: `best_practice_deviation` — chunk violates a known pattern for its functional role
- Lab cross-references: for each complexity/coupling/coverage finding, look up the chunk's functional_role in best_practices, produce a specific recommendation
- Recommendation format: "[chunk] is a [role]. Best practice: [pattern]. Current: [observation]. Recommendation: [specific action]."
- New Planner constraint type: `pattern_recommendation` — includes the best practice and the specific deviation
- Cycle report gains a "Research Recommendations" section with per-role improvement strategies
- Cross-project pattern comparison (when multiple projects scanned): "invoice-pulse's route handlers average CC 12; freight-kb's average CC 5. invoice-pulse should refactor to match."

**Dependencies:** Phase 8 complete (best practices populated, purpose-aware scoring active).

---

## Dependency Map

```
Phase 7 (Classification + Provenance)
  → Phase 8 (Best Practices + Purpose-Aware Scoring)
    → Phase 9 (Research Recommendations)
```

Strictly sequential. Each phase's output is the prior phase's input.
