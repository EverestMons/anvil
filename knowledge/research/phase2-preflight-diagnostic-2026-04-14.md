# Anvil Phase 2 Pre-Flight Diagnostic — Findings
**Date:** 2026-04-14 | **Deposited by:** Anvil Developer

---

## Section A — Specialist File Staleness Audit

All three specialist files carry `**Last Updated:** 2026-03-29` — predating Phases 7–9 (classifier, provenance, best practices, research recommendations). None reference Phase 7–9 blueprints. None describe the full pipeline correctly.

### Staleness Table

| File | Stale Facts | Missing Sections | Severity |
|---|---|---|---|
| ANVIL_SYSTEMS_ANALYST.md | Pipeline listed as 4 stages (SCAN → EXTRACT → SCORE → LAB); Knowledge Base Index shows "none yet" | CLASSIFY stage, PROVENANCE stage; best_practices / functional_roles / chunk_provenance tables not in Key Sources | HIGH |
| ANVIL_DEVELOPER.md | Project-Specific Context says "Anvil is in Phase 0 (scaffolding), moving to Phase 1" — Phases 0–9 are complete; Domain Focus lists 4-stage pipeline only | CLASSIFY + PROVENANCE stages; classifier.py, provenance.py, detector.py absent from Domain Focus | CRITICAL |
| ANVIL_QA_ANALYST.md | Domain Focus and Key Sources reference no Phase 7–9 artifacts; cross-validation ground truth (68+ tables, 944+ tests, 11 gates, 27 modules) not verified | best_practices, functional_roles, chunk_provenance absent from schema verification checklist | HIGH |

### Per-File Detail

**ANVIL_SYSTEMS_ANALYST.md**
- (1) Domain Focus: SCAN → EXTRACT → SCORE → LAB only. No mention of classification, provenance, best practices, or research recommendations.
- (2) Key Sources: references Study diagnostics and Forge scanner — no Phase 7–9 blueprints.
- (3) Pipeline description: "four stages: SCAN → EXTRACT → SCORE → LAB" — incorrect; actual pipeline is 6 stages.
- (4) Table counts: none mentioned; Knowledge Base Index is empty ("none yet").

**ANVIL_DEVELOPER.md**
- (1) Domain Focus: lists Python AST, datasketch, git CLI, MinHash — no classifier, provenance, best practices, or detector.
- (2) Key Sources: no Phase 7–9 blueprints referenced.
- (3) Pipeline description: 4-stage SCAN → EXTRACT → SCORE → LAB only.
- (4) Phase status: "Anvil is in Phase 0, moving to Phase 1" — massively stale; Phases 0–9 are complete.
- (4) src/ files not mentioned: classifier.py, provenance.py, detector.py, config.py (ROLE_THRESHOLDS).

**ANVIL_QA_ANALYST.md**
- (1) Domain Focus: covers chunk accuracy, symbol bindings, health scores only — no best practices validation, no role classification verification.
- (2) Key Sources: no Phase 7–9 blueprints.
- (3) Cross-validation ground truth cites invoice-pulse facts (68+ tables, 944+ tests, 11 gates, 27 modules) — may still be accurate but omits Anvil's three new tables (best_practices, functional_roles, chunk_provenance) from schema verification.

---

## Section B — Current Pipeline Shape

### Pipeline Stages (from src/cycle.py)

| Stage | Function | Fault Behavior |
|---|---|---|
| 1. SCAN | `scan_project(conn, project_name)` | Fatal — aborts pipeline on error |
| 2. EXTRACT | `extract_project(conn, project_name, cycle_id)` | Fatal — aborts pipeline on error |
| 2.5 CLASSIFY | `classify_project(conn, project_name)` | Non-fatal — scoring works without it |
| 2.5b PROVENANCE | `ingest_provenance(conn, project_name, dev_log_dir)` | Non-fatal — only runs if DEV_LOG_PATHS configured |
| 3. SCORE | `score_project(conn, project_name, cycle_id)` | Non-fatal — lab runs even if scorer fails |
| 4. LAB | `run_lab(conn, project_name, cycle_id)` | Non-fatal |

**Full pipeline:** `SCAN → EXTRACT → CLASSIFY → PROVENANCE → SCORE → LAB`

### Finding Types (from src/lab.py — run_lab())

| Finding Key | Function | Description |
|---|---|---|
| coverage_gaps | `find_coverage_gaps()` | Untested high-risk chunks (coverage_score + composite_score thresholds) |
| coupling_hotspots | `find_coupling_hotspots()` | Highly coupled chunks — role-specific thresholds via ROLE_THRESHOLDS |
| clone_candidates | `find_clone_candidates()` | Near-duplicate chunk pairs from chunk_similarities |
| staleness_alerts | `find_staleness_alerts()` | Chunks whose dependencies are newer than the chunk itself |
| complexity_hotspots | `find_complexity_hotspots()` | Overly complex functions — role-specific thresholds |
| cochange_patterns | `find_cochange_patterns()` | File pairs that change together in git (Jaccard scored) |
| best_practice_deviations | `find_best_practice_deviations()` | Chunks violating best practices for their functional_role |

### Planner Constraint Types (from generate_planner_constraints())

| Constraint Type | Source Finding |
|---|---|
| coverage_required | coverage_gaps |
| verify_dependents | coupling_hotspots |
| refactor_candidate | clone_candidates AND complexity_hotspots |
| investigation_needed | staleness_alerts |
| pattern_recommendation | best_practice_deviations |

### Cycle Report Sections (from write_cycle_report())

1. Executive Summary (files, chunks, high-risk count, avg score, total findings)
2. Coverage Gaps
3. Coupling Hotspots
4. Clone Candidates
5. Staleness Alerts
6. Complexity Hotspots
7. Co-Change Patterns
8. Research Recommendations (best practice deviations, grouped by functional role)
9. Planner Constraints (grouped by constraint type)
10. Specialist Update Data (chunk counts by type, dep/sim counts, avg score, high-risk count)

---

## Section C — Current Schema Tables

### Live Tables in anvil.db (2026-04-14)

| Table | In SA Specialist File | Notes |
|---|---|---|
| code_chunks | Yes (core) | — |
| chunk_fingerprints | Yes (core) | — |
| chunk_symbol_bindings | Yes (core) | — |
| chunk_dependencies | Yes (core) | — |
| chunk_similarities | Yes (core) | — |
| git_changes | Yes (signal) | — |
| test_results | Yes (signal) | — |
| health_scores | Yes (signal) | — |
| cycle_reports | Yes (signal) | — |
| projects | Implied | — |
| sqlite_sequence | System | — |
| best_practices | **NO** | Phase 8 addition — stores per-role patterns with severity |
| functional_roles | **NO** | Phase 7 addition — defines role taxonomy |
| chunk_provenance | **NO** | Phase 7 addition — stores dev log / provenance events |

**Gap summary:** Three Phase 7–9 tables are absent from all specialist files. The SA schema description covers 9 of 12 data tables (~75%). Any agent reading the SA file to understand the live schema will miss best_practices, functional_roles, and chunk_provenance.

---

## Section D — Live Stats Snapshot (2026-04-14)

| Metric | Count |
|---|---|
| code_chunks | 5,753 |
| chunk_symbol_bindings | 312,733 |
| health_scores | 26,966 |
| best_practices | 25 |

**Observations:**
- 5,753 chunks from invoice-pulse — no chunk count target is specified in any specialist file.
- 312,733 symbol bindings (~54 bindings/chunk avg) reflects import and call-site resolution at scale.
- 26,966 health_score rows indicates multi-cycle accumulation (health_scores are cycle-stamped, not replaced/upserted).
- 25 best_practice rules across functional roles is the current corpus for deviation detection in Lab.

---

## Section E — Phase 2 Readiness Gaps

### Gaps Table

| Gap | Impact on Phase 2.1 | Priority |
|---|---|---|
| No src/ file reads PROJECT_BRIEF.md or domain glossary | Phase 2 strategic audit needs intent cross-referencing; currently no pipeline code ingests project intent signals — Claude Code is the sole reader of those files | HIGH |
| No finding type cross-references project intent | All 7 finding types are purely structural. None ask "does this chunk align with what the project is supposed to do?" — an intent-layer finding type is the core Phase 2 architectural delta | HIGH |
| All three specialist files are stale (pre-Phase 7–9) | Planning sessions that use specialist files get wrong pipeline (4 stages vs 6) and wrong phase status (Phase 0–1 vs Phases 0–9 complete) | HIGH |
| best_practices, functional_roles, chunk_provenance absent from specialist files | SA schema section, Developer Key Sources, and QA cross-validation checklist all miss ~25% of the live schema | HIGH |
| No knowledge/anvil/ deposit folder in invoice-pulse | Anvil deposits cycle findings to its own knowledge/research/; invoice-pulse has no dedicated Anvil subfolder. Phase 2 cross-project planner integration has no agreed deposit location on the target project side | MEDIUM |
| Phase 2.1 strategic audit roadmap exists but specialist files have no Phase 2 context | Agents picking up Phase 2 work read stale Phase 0–1 framing; Knowledge Base Index shows "none yet" in all three files | MEDIUM |

---

## Output Receipt
**Agent:** Anvil Developer
**Step:** 1 (standalone diagnostic)
**Status:** Complete

### What Was Done
Full pre-flight diagnostic across 5 sections: specialist staleness audit (all 3 files HIGH/CRITICAL stale vs Phase 7–9 reality), current pipeline shape documented (6 stages, 7 finding types, 5 constraint types, 10 report sections), live schema inventoried (3 tables missing from specialist files), live DB stats captured (5,753 chunks, 312,733 symbols, 26,966 health_scores, 25 best_practices), and 6 Phase 2 readiness gaps enumerated.

### Files Deposited
- `anvil/knowledge/research/phase2-preflight-diagnostic-2026-04-14.md` — full 5-section pre-flight findings

### Files Created or Modified (Code)
- None

### Decisions Made
- Severity CRITICAL assigned to ANVIL_DEVELOPER.md phase status staleness ("Phase 0 → 1" when Phases 0–9 are complete) — highest-impact stale fact for any agent reading that file

### Flags for CEO
- All three specialist files require updates before Phase 2.1 planning agents read them. The Developer file is most urgent. Recommend a specialist-file refresh executable as Phase 2 prerequisite.
- No `knowledge/anvil/` folder exists in invoice-pulse for Anvil deposit targeting — Phase 2.1 planning should decide the deposit location convention before first cross-project output.

### Flags for Next Step
- Phase 2.1 planning should budget for specialist file refresh as a pre-task, or explicitly note that agents must ignore stale phase status in ANVIL_DEVELOPER.md.
- The intent-layer gap (no finding type reads PROJECT_BRIEF) is the architectural delta that most distinguishes Phase 2 from Phase 1 — the new finding type design is the core Phase 2.1 deliverable.
