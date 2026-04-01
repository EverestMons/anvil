# Anvil — Project Status

**Status:** Operational
**Last Updated:** 2026-04-01

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

- **Phase 8 Best Practices + Purpose-Aware Scoring** (2026-04-01) — best_practices table with 15 seed patterns (3 per top 5 roles), role-specific scoring weights for 8 roles, purpose-relative thresholds for 5 roles. Scorer uses role weights, Lab uses role thresholds. Web research hook for Claude Code to discover new practices. Live results: scoring distribution shifted (46 high-risk, 145 complexity hotspots with lower role thresholds). QA verified: all 6 areas PASS.
- **Phase 7 Classification + Provenance** (2026-04-01) — Functional role taxonomy (25 roles across 5 groups), heuristic classifier (decorator > naming > file path > fallback rules), dev log parser with provenance ingestion. Pipeline extended: SCAN -> EXTRACT -> CLASSIFY -> PROVENANCE -> SCORE -> LAB. Live results: 1,605 chunks classified (100% coverage, 24 roles assigned), 8,404 provenance entries from 100 dev logs. QA discovered and fixed backtick-wrapping issue in parser. QA verified: all 7 areas PASS.

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
