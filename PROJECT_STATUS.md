# Anvil — Project Status

**Status:** Scanner Complete
**Last Updated:** 2026-03-30

---

## Current Phase

Phase 2 Scanner complete. Ready for Phase 3 (Extractor — AST parsing, symbol extraction).

## Completed Milestones

- **Phase 0 Scaffold** (2026-03-29) — git init, COMPANY.md updated, CLAUDE.md, 3 agent specialist files (SA, Developer, QA), domain glossary, feedback log, requirements.txt. QA verified: all PASS.
- **Phase 1 Schema** (2026-03-29) — config.py, db.py with all 10 tables, test_db.py with full CRUD + constraint tests (34 passing), QA verified against SA blueprint. All 7 verification areas PASS.
- **Phase 2 Scanner** (2026-03-30) — file discovery, SHA-256 change detection, git history ingestion, idempotent rescans. Tested against invoice-pulse: 939 files registered, 479 git commits ingested (2168 per-file change records). QA verified: all 8 areas PASS.

## Roadmap

Deposited at `knowledge/decisions/roadmap-anvil-build-2026-03-29.md`.

## CEO Decisions Locked

- Claude Code function execution model (Claude Code runs code directly, not external APIs)
- Run tests directly first (no CI/CD yet)
- Separate DBs from Forge (Anvil maintains its own SQLite databases)

## Next

Phase 3 — Extractor (Python AST parsing, function/class/method chunk extraction, symbol binding creation).
