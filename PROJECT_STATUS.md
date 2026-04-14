# Anvil — Project Status

**Status:** Operational
**Last Updated:** 2026-04-14

---

## Current Phase

Anvil is operational. Full SCAN → EXTRACT → SCORE → LAB pipeline validated against invoice-pulse. Cross-validated against specialist file facts (10/10 PASS). Findings quality assessed — coverage gaps are highest-value (81% signal), Planner integration protocol defined.

## Completed Milestones

- **Phase 0 Scaffold** (2026-03-29) — git init, COMPANY.md updated, CLAUDE.md, 3 agent specialist files (SA, Developer, QA), domain glossary, feedback log, requirements.txt. QA verified: all PASS.
- **Phase 1 Schema** (2026-03-29) — config.py, db.py with all 10 tables, test_db.py with full CRUD + constraint tests (34 passing), QA verified against SA blueprint. All 7 verification areas PASS.
- **Phase 2 Scanner** (2026-03-30) — file discovery, SHA-256 change detection, git history ingestion, idempotent rescans. Tested against invoice-pulse: 939 files registered, 479 git commits ingested (2168 per-file change records). QA verified: all 8 areas PASS.
- **Phase 3 Extractor** (2026-03-30) — Python AST parser, symbol extraction, dependency resolution, MinHash fingerprinting. Live extraction against invoice-pulse: 188 files processed, 3247 chunks created, 34789 symbols extracted, 12142 dependencies resolved, 3247 fingerprints (3031 with MinHash), 381 similarity pairs. QA verified: all 10 areas PASS.
- **Phase 4 Scorer** (2026-03-30) — 5-dimension health scoring (volatility, coverage, complexity, coupling, staleness), composite scores, test result ingestion. Live scoring against invoice-pulse: 3247 chunks scored, distribution: 29 high-risk, 1413 medium, 1805 low-risk, avg composite 0.26. Top risk: validator gate functions (high volatility + no coverage + high complexity). QA verified: all 9 areas PASS.
- **Phase 5 Lab** (2026-03-30) — 6 finding types (coverage gaps, coupling hotspots, clone candidates, staleness alerts, complexity hotspots, co-change patterns), Planner constraint generation, specialist update data, cycle report writing. Live Lab against invoice-pulse: 1212 total findings, 292 Planner constraints generated. QA verified: all 9 areas PASS.
- **Phase 6 First Cycle Validation** (2026-03-30) — cycle runner (pipeline orchestrator + cycle comparison), cross-validated against invoice-pulse specialist facts (10/10 PASS: gate functions exact match, confidence staleness detected, clones verified, coverage gaps confirmed). Findings quality assessed: 25% overall signal-to-noise, coverage gaps 81% signal. Planner integration protocol defined.

- **Phase 9 Research Recommendations** (2026-04-01) — Detection hint engine (content regex + structural metadata checks), best_practice_deviation finding type (809 deviations across 4 roles from live IP data), pattern_recommendation Planner constraint type, Research Recommendations cycle report section grouped by role. Pipeline now produces 7 finding types + research recommendations. QA verified: all 7 areas PASS.
- **Phase 8 Best Practices + Purpose-Aware Scoring** (2026-04-01) — best_practices table with 15 seed patterns (3 per top 5 roles), role-specific scoring weights for 8 roles, purpose-relative thresholds for 5 roles. Scorer uses role weights, Lab uses role thresholds. Web research hook for Claude Code to discover new practices. Live results: scoring distribution shifted (46 high-risk, 145 complexity hotspots with lower role thresholds). QA verified: all 6 areas PASS.
- **Phase 7 Classification + Provenance** (2026-04-01) — Functional role taxonomy (25 roles across 5 groups), heuristic classifier (decorator > naming > file path > fallback rules), dev log parser with provenance ingestion. Pipeline extended: SCAN -> EXTRACT -> CLASSIFY -> PROVENANCE -> SCORE -> LAB. Live results: 1,605 chunks classified (100% coverage, 24 roles assigned), 8,404 provenance entries from 100 dev logs. QA discovered and fixed backtick-wrapping issue in parser. QA verified: all 7 areas PASS.
- **Pytest Symbol Binding Resolver** (2026-04-04) — Function-level "tests" bindings with target_chunk_id populated when test_case chunks call production functions. Fixes 99.5% coverage blind spot. Live validation: 449 new function-level bindings, 74 production chunks gained coverage. QA verified: 10/10 deliverables PASS, no regressions.
- **Phase 2.1 Intent Cross-Reference Layer** (2026-04-14) — find_intent_gaps() + write_intent_audit() live. Eighth Lab finding type cross-references structural signals (coverage gaps, coupling hotspots, complexity hotspots) against project intent (PROJECT_BRIEF.md + domain-glossary.md). Deposits audit-findings-{date}.md to target project knowledge/anvil/. invoice-pulse/knowledge/anvil/ deposit folder established. Live smoke test: 5 findings returned (all 3 signal types), all 9 required keys present. QA verified: all 5 areas PASS.
- **Specialist Sync to Phase 9** (2026-04-14): All three specialist files synced to Phase 9 reality (v2.0).
- **2026-04-14: Cycle 10 complete** (planned as Cycle 9 — DB auto-incremented; prior cycle 9 existed from earlier session). First production run with Phase 2.1 intent gaps. 20 intent gaps found across CRITICAL(7)/HIGH(1)/MEDIUM(6)/LOW(6). audit-findings deposited to invoice-pulse/knowledge/anvil/.
- **2026-04-14: Phase 2.1 refinement shipped** — test file filter added to all 3 find_intent_gaps queries, project intent injection via _extract_project_mission added; 2 pre-existing unrelated test failures (test_find_cochange_patterns, test_find_staleness_alerts) noted and carried forward.
- **2026-04-14: Cycle 10 findings triaged** — Planner curated the 20 raw findings from `invoice-pulse/knowledge/anvil/audit-findings-2026-04-14.md` into `invoice-pulse/knowledge/research/anvil-findings-backlog-2026-04-14.md`. Sorted into 5 actionable (dispute_brief, run_validation, _validate_contract_json, contract_fuel_import_combined, gate_7_linehaul), 3 expected noise (session methods + connection factory), 12 pending triage. First curated backlog produced from the Phase 2.1 refined output — validates that the mission-injection + test-file-filter changes produced findings worth acting on. Future Anvil refinement candidate: suppress session-lifecycle and connection-factory patterns from coupling findings.
- **2026-04-14: Findings noise reduction shipped** — `_is_noise_chunk` helper added; test-file filter applied to `find_coupling_hotspots`, `find_coverage_gaps`, `find_complexity_hotspots` via SQL; session-lifecycle and connection-factory suppression applied to all 4 finding functions via Python helper. Cycle report coupling hotspots now signal-dominant.
- **2026-04-14: QA recovery** — (1) Findings noise reduction shipped and closed: `_is_noise_chunk` helper + SQL test-file filters + 3 new tests; cycle report coupling hotspots now signal-dominant; DEV commit d04fa5e. (2) Cycle 11 stranded plan moved to Done (pre-empted by mission-heading re-run as Cycle 12, already executed, no re-run performed).

## Diagnostics Completed

- **Pytest Symbol Binding Gap** (2026-04-04) — Investigated full pipeline path from test file extraction through coverage scoring. Found 99.5% of production chunks scored as zero test coverage due to module-level-only "tests" bindings and never-populated target_chunk_id. Fix validated: enhance `_store_file_symbols()` to create function-targeted "tests" bindings when test_case calls resolve to production chunks. Findings at `knowledge/research/pytest-bindings-diagnostic-2026-04-04.md`.

## Roadmap

Deposited at `knowledge/decisions/roadmap-anvil-build-2026-03-29.md`.

## CEO Decisions Locked

- Claude Code function execution model (Claude Code runs code directly, not external APIs)
- Run tests directly first (no CI/CD yet)
- Separate DBs from Forge (Anvil maintains its own SQLite databases)

## Next

- Run `from src.cycle import run_cycle` for on-demand cycles
- Planner should consume `coverage_required` and `verify_dependents` constraints (high severity only)
- Tune thresholds per findings quality assessment before Cycle 2
- Extend to additional projects (forge, freight-kb)
- Phase 2 language support (JavaScript/TypeScript) when needed
