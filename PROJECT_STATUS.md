# Anvil — Project Status

**Status:** Scorer Complete
**Last Updated:** 2026-03-30

---

## Current Phase

Phase 4 Scorer complete. Ready for Phase 5 (Lab — actionable output generation).

## Completed Milestones

- **Phase 0 Scaffold** (2026-03-29) — git init, COMPANY.md updated, CLAUDE.md, 3 agent specialist files (SA, Developer, QA), domain glossary, feedback log, requirements.txt. QA verified: all PASS.
- **Phase 1 Schema** (2026-03-29) — config.py, db.py with all 10 tables, test_db.py with full CRUD + constraint tests (34 passing), QA verified against SA blueprint. All 7 verification areas PASS.
- **Phase 2 Scanner** (2026-03-30) — file discovery, SHA-256 change detection, git history ingestion, idempotent rescans. Tested against invoice-pulse: 939 files registered, 479 git commits ingested (2168 per-file change records). QA verified: all 8 areas PASS.
- **Phase 3 Extractor** (2026-03-30) — Python AST parser, symbol extraction, dependency resolution, MinHash fingerprinting. Live extraction against invoice-pulse: 188 files processed, 3247 chunks created, 34789 symbols extracted, 12142 dependencies resolved, 3247 fingerprints (3031 with MinHash), 381 similarity pairs. QA verified: all 10 areas PASS.
- **Phase 4 Scorer** (2026-03-30) — 5-dimension health scoring (volatility, coverage, complexity, coupling, staleness), composite scores, test result ingestion. Live scoring against invoice-pulse: 3247 chunks scored, distribution: 29 high-risk, 1413 medium, 1805 low-risk, avg composite 0.26. Top risk: validator gate functions (high volatility + no coverage + high complexity). QA verified: all 9 areas PASS.

## Roadmap

Deposited at `knowledge/decisions/roadmap-anvil-build-2026-03-29.md`.

## CEO Decisions Locked

- Claude Code function execution model (Claude Code runs code directly, not external APIs)
- Run tests directly first (no CI/CD yet)
- Separate DBs from Forge (Anvil maintains its own SQLite databases)

## Next

Phase 5 — Lab (actionable output generation: fix executables, constraints for Planner, specialist file updates, CEO alerts).
