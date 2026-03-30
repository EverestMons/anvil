# Anvil — Project Status

**Status:** Schema Complete
**Last Updated:** 2026-03-29

---

## Current Phase

Phase 1 Schema complete. Ready for Phase 1 Pipeline (SCAN → EXTRACT → SCORE → LAB).

## Completed Milestones

- **Phase 0 Scaffold** (2026-03-29) — git init, COMPANY.md updated, CLAUDE.md, 3 agent specialist files (SA, Developer, QA), domain glossary, feedback log, requirements.txt. QA verified: all PASS.
- **Phase 1 Schema** (2026-03-29) — config.py, db.py with all 10 tables, test_db.py with full CRUD + constraint tests (34 passing), QA verified against SA blueprint. All 7 verification areas PASS.

## Roadmap

Deposited at `knowledge/decisions/roadmap-anvil-build-2026-03-29.md`.

## CEO Decisions Locked

- Claude Code function execution model (Claude Code runs code directly, not external APIs)
- Run tests directly first (no CI/CD yet)
- Separate DBs from Forge (Anvil maintains its own SQLite databases)

## Next

Phase 1 Pipeline — SCAN stage implementation (file walking, content hashing, change detection).
