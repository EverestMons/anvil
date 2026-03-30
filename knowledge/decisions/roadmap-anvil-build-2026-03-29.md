# Anvil — Build Roadmap
**Date:** 2026-03-29 | **Type:** Roadmap | **Owner:** CEO

---

## Foundation — Study Diagnostic Lineage

Anvil's data model is derived from two study project diagnostics run on 2026-03-22, commissioned specifically to understand how study's chunking architecture could transfer to code analysis:

**Source 1:** `study/knowledge/research/chunk-metadata-diagnostic-2026-03-22.md`
- Mapped study's full structural_metadata pipeline across 5 parsers (EPUB, DOCX, PDF, PPTX, plain text)
- Revealed two metadata paths: DOM-walk (high fidelity) and regex fallback (lossy) — Anvil avoids this by using Python AST (deterministic, not heuristic)
- Identified 8 gaps in study's metadata model (missing blockquote_count, binary list_count, inflated metadata on section splits)
- **Anvil design decision:** `structural_metadata` table uses deterministic signals (cyclomatic complexity, nesting depth, parameter count) not regex heuristics

**Source 2:** `study/knowledge/research/chunk-relationships-diagnostic-2026-03-22.md`
- Mapped study's complete chunk relationship model: no direct chunk-to-chunk FKs, indirect paths via facet bindings and concept links
- Found `section_path` indexed but completely unused — stored hierarchy with zero queries
- Found MinHash similarity results discarded after extraction — signatures persisted but comparison results ephemeral
- Found no chunk-level prerequisite ordering (only skill-level)
- **Anvil design decisions:**
  - `chunk_dependencies` table with explicit directed edges (import/call/inherit) — study had no direct chunk-to-chunk relationships
  - `chunk_similarities` table persists MinHash comparison results — study discarded them
  - `chunk_symbol_bindings` with typed relationships (defines/imports/calls/tests/documents) — study's `chunk_facet_bindings` proved typed bindings work but lacked code-specific types
  - Content-hash dedup via `chunk_fingerprints` — study's SHA-256 model transfers directly

**Transferable patterns (from PROJECT_BRIEF, validated by diagnostics):**

| Study Concept | Anvil Equivalent | Diagnostic Evidence |
|---|---|---|
| `chunks` table | `code_chunks` | Study's schema (20 columns) proved chunk-as-atomic-unit works at scale |
| `chunk_facet_bindings` (typed) | `chunk_symbol_bindings` | Study's binding_type (teaches/prerequisite_for/references) proved typed relationships are queryable |
| `chunk_prerequisites` | `chunk_dependencies` | Study had NO chunk-to-chunk prerequisites — only skill-level. Anvil adds this from day one |
| `chunk_similarities` (missing) | `chunk_similarities` | Study computed MinHash but discarded results. Anvil persists them |
| `chunk_fingerprints` | `chunk_fingerprints` | Study's SHA-256 + MinHash signature model transfers directly |
| `structural_metadata` JSON blob | `structural_metadata` table | Study's blob approach works but regex path is lossy. Anvil uses deterministic AST signals |
| `teaching_effectiveness` | `health_score` | Concept transfers: composite score from multiple signals, updated per cycle |
| Content-hash dedup | Content-hash dedup | Study's `content_hash` column at upload-time proved effective for change detection |
| Classification-aware chunking | Language-aware chunking | Study splits at heading boundaries. Anvil splits at function/class/method boundaries |
| Three-pass merge/split/hash | Three-pass merge/split/hash | Study's chunker handles small/oversized files consistently — same pattern needed for code |

**Not transferred (learning-specific):** FSRS scheduling, mastery tracking, Bloom's taxonomy, session exchanges, pedagogical quality ranking.

---

## Phase 0 — Scaffold

**Goal:** Make Anvil a functioning project in the Eluvian system. No code, just infrastructure.

**Deliverables:**
- `git init` in `/Users/marklehn/Desktop/GitHub/anvil/`
- COMPANY.md update: add Anvil row to Active Projects table, update Forge description to clarify the umbrella concept
- `PROJECT_STATUS.md` — initial status file
- `CLAUDE.md` — agent behavior rules (Python `with open()` for file writes, no heredocs, test requirements, commit message conventions)
- Agent specialist files in `anvil/agents/`:
  - `ANVIL_SYSTEMS_ANALYST.md` — schema design, pipeline architecture, cross-project structural patterns
  - `ANVIL_DEVELOPER.md` — Python implementation, AST parsing, SQLite operations, git CLI integration
  - `ANVIL_QA_ANALYST.md` — pipeline validation, schema verification, test coverage

- `knowledge/research/domain-glossary.md` — stub with Anvil-specific terms (code chunk, symbol binding, health score, cycle, etc.)
- `knowledge/research/agent-prompt-feedback.md` — empty feedback log with Patterns Identified section
- `requirements.txt` — initial dependencies (datasketch for MinHash, no other external deps for Phase 1)

**Dependencies:** None. This is the entry point.

**Execution model:** Single executable plan, DEV-only (documentation creation). QA verifies completeness checklist against SPECIALIST_TEMPLATE.

---

## Phase 1 — Schema + Database

**Goal:** Implement the full SQLite schema from the PROJECT_BRIEF data model. Prove it's correct before writing pipeline code.

**Deliverables:**
- `src/config.py` — project paths, scan targets (invoice-pulse only), cycle settings
- `src/db.py` — SQLite connection management, table creation, migration utilities
- Schema implementation covering all tables:
  - Core: `projects`, `code_chunks`, `chunk_fingerprints`, `chunk_symbol_bindings`, `chunk_dependencies`, `chunk_similarities`
  - Signal: `git_changes`, `test_results`, `health_scores`, `cycle_reports`
- Indexes on foreign keys and common query patterns
- Test suite: schema creation, CRUD operations on each table, constraint verification

**Dependencies:** Phase 0 (agents must exist for plan routing).

**Key constraint:** Schema must match PROJECT_BRIEF data model exactly. Any deviations flagged to CEO before implementation.

**Execution model:** SA blueprint → DEV implementation → QA schema verification (including PRAGMA checks against live DB).

---

## Phase 2 — Scanner

**Goal:** Walk project directories, detect changed files, ingest git history. The scanner is the entry point to every Anvil cycle.

**Deliverables:**
- `src/scanner.py` — file walker with content hashing (SHA-256 for change detection)
  - Walk invoice-pulse project directory
  - Skip `.git/`, `__pycache__/`, `node_modules/`, `.venv/`, other excluded patterns
  - Hash each file, compare against `chunk_fingerprints` to identify new/changed files
  - Register new files in `code_chunks` at file-level granularity (function-level chunking is Phase 3)
- Git history ingestion:

  - Parse `git log` output for last few weeks of commits
  - Populate `git_changes` table: commit hash, date, files changed, message
  - Track per-file change frequency for volatility scoring in Phase 4
- Test suite: scanner against a mock project directory, git log parsing, change detection accuracy

**Dependencies:** Phase 1 (schema must exist).

**Key design decision (from study diagnostic):** Study's content_hash was upload-time only. Anvil's content hash is cycle-time — re-computed every scan to detect changes since last cycle. This is the "only process what's new" optimization from the PROJECT_BRIEF.

**Execution model:** SA blueprint (file walking strategy, git log parsing format, exclusion patterns) → DEV → QA.

---

## Phase 3 — Extractor

**Goal:** Parse Python source files into function/class/method-level chunks. Extract symbols and relationships. This is the core intelligence layer.

**Deliverables:**
- `src/extractor.py` — orchestrates extraction for changed files
- `src/parsers/python_parser.py` — Python AST-based extraction:
  - Function definitions → code_chunks (type: function)
  - Class definitions → code_chunks (type: class)
  - Method definitions → code_chunks (type: method)
  - Module-level code → code_chunks (type: module)
  - Config blocks, test cases → code_chunks (appropriate types)
- Symbol extraction:
  - Import statements → chunk_symbol_bindings (type: imports)
  - Function/method calls → chunk_symbol_bindings (type: calls)
  - Class definitions → chunk_symbol_bindings (type: defines)
  - Test functions covering modules → chunk_symbol_bindings (type: tests)
  - Docstrings → chunk_symbol_bindings (type: documents)
- Dependency graph construction:
  - Import chains → chunk_dependencies (within_file / cross_file)
  - Call graphs → chunk_dependencies
  - Inheritance → chunk_dependencies
- MinHash signature computation for each chunk → chunk_fingerprints
- Similarity pair detection above threshold → chunk_similarities (persistent, unlike study)
- structural_metadata per chunk: cyclomatic complexity, nesting depth, parameter count, import count, docstring presence

- Test suite: AST parsing accuracy, symbol extraction completeness, dependency graph correctness, MinHash similarity detection

**Dependencies:** Phase 2 (scanner must identify which files to extract).

**Key design decision (from study diagnostic):** Study's chunker had a metadata inflation bug — oversized sections split into parts each inherited the full section's metadata counts. Anvil avoids this by computing structural_metadata per-chunk at extraction time (AST-derived, not inherited).

**Special consideration:** Invoice-pulse uses SQLAlchemy patterns for ORM → table mappings. The Python parser should recognize `db.Column()`, `db.relationship()`, and model class definitions as structurally significant. This is the "SQLAlchemy pattern recognition" item from the PROJECT_BRIEF.

**Execution model:** SA blueprint (AST parsing strategy, chunk granularity rules, symbol taxonomy) → DEV → QA (verify against known invoice-pulse structure — e.g., confirm all gate functions in validator.py are extracted as individual chunks).

---

## Phase 4 — Scorer

**Goal:** Compute health scores from the signal tables. Every code chunk gets a composite score reflecting its structural risk.

**Deliverables:**
- `src/scorer.py` — health score computation:
  - **Volatility:** change frequency from `git_changes`, recency weighting, co-change partner identification
  - **Coverage:** test bindings from `chunk_symbol_bindings` (type: tests), coverage percentage
  - **Complexity:** cyclomatic complexity from `structural_metadata`
  - **Coupling:** inbound + outbound edge count from `chunk_dependencies`
  - **Staleness:** last modified date vs dependency last modified dates
- Composite `health_score` per chunk → `health_scores` table
- Scoring weights configurable in `config.py`
- Test suite: scoring formula verification, edge cases (zero-dependency chunks, chunks with no test coverage)

**Dependencies:** Phase 3 (extractor must populate chunks, bindings, dependencies, and git_changes must exist from Phase 2).

**Execution model:** SA blueprint (scoring formula, weight rationale, edge case handling) → DEV → QA.

---

## Phase 5 — Lab

**Goal:** Analyze scored findings and produce actionable outputs. This is where Anvil's structural intelligence becomes useful to the Planner and agents.

**Deliverables:**
- `src/lab.py` — findings analysis and output generation:
  - **Coverage gaps:** functions with high volatility + zero test coverage → flag for Planner
  - **Coupling hotspots:** chunks with high inbound dependency count → flag as high-risk for refactoring plans
  - **Clone detection:** MinHash similarity pairs above threshold → flag for consolidation
  - **Staleness alerts:** chunks whose dependencies have been modified more recently than the chunk itself
  - **Cycle report:** per-cycle summary deposited to `cycle_reports` table and `anvil/knowledge/research/`
- Output formats:
  - Planner-consumable findings (markdown at `anvil/knowledge/research/cycle-N-findings-YYYY-MM-DD.md`)
  - Specialist file update data (concrete numbers for test counts, table counts, function inventories)
  - CEO alerts for critical findings (security vulnerabilities, severely uncovered high-volatility code)
- Test suite: findings generation from known test data, output format verification

**Dependencies:** Phase 4 (scores must exist).

**Execution model:** SA blueprint (findings taxonomy, alert thresholds, output format) → DEV → QA.

---

## Phase 6 — First Cycle

**Goal:** Run the complete SCAN → EXTRACT → SCORE → LAB pipeline against invoice-pulse. Validate output quality. This is the proof-of-concept.

**Deliverables:**
- Full cycle run against invoice-pulse codebase
- Cycle report deposited to `anvil/knowledge/research/`
- Validation: compare Anvil's structural findings against known facts from invoice-pulse specialist files (e.g., does Anvil find the correct number of gate functions? Does it detect the cached/non-cached parallel implementations? Does it flag untested validators?)
- CEO review of findings quality
- Fixes for any pipeline issues discovered during first run

**Dependencies:** Phase 5 (all pipeline stages must be functional).

**Execution model:** DEV runs the cycle → QA validates output against known project state → CEO reviews findings quality.

---

## Dependency Map

```
Phase 0 (Scaffold)
  → Phase 1 (Schema)
    → Phase 2 (Scanner)
      → Phase 3 (Extractor)
        → Phase 4 (Scorer)
          → Phase 5 (Lab)
            → Phase 6 (First Cycle)
```

Strictly sequential. Each phase builds on the prior phase's output. No parallel lanes until Phase 1 is complete (at which point scanner and git history ingestion could theoretically run in parallel, but the simplicity of sequential execution outweighs the marginal time savings).


---

## Future Phases (Post-First Cycle)

These are scoped in the PROJECT_BRIEF but not part of the initial build:

- **Language expansion:** JavaScript/TypeScript parser (study), Swift parser (BrewBuddy, SimpleScreen)
- **Multi-project scanning:** Expand beyond invoice-pulse to all Python projects (forge, freight-kb), then JS/Swift projects
- **Forge integration:** Anvil findings feed into Forge's pattern database. Forge already knows about governance quality; Anvil adds code quality signals. The two systems cross-reference: "this governance rule was applied to a module that Anvil flags as high-risk"
- **Security analysis:** dependency vulnerabilities, exposed secrets, unsafe patterns
- **Performance analysis:** N+1 queries, synchronous bottlenecks, uncached lookups
- **Specialist file auto-update:** Anvil deposits current structural data (test counts, table counts, function inventories) that specialist sync prompts can reference directly instead of re-reading source code

---

## CEO Decisions (2026-03-29)

1. **Execution model: Claude Code functions (no CLI).** Same pattern as Forge — Python functions called by Claude Code. Claude Code runs the full cycle in one session: `scan_project()` → `extract_chunks()` → `score_chunks()` → then Claude Code interprets findings and writes the Lab report. The LLM is the Lab intelligence layer. No standalone CLI needed.

2. **Test result ingestion: run tests directly first.** Simpler path for Phase 1 — Anvil runs `pytest` against invoice-pulse and parses output. Agent-deposited result file ingestion is a later addition.

3. **Separate databases.** Anvil has `anvil.db` (code chunks), Forge has `forge.db` (prompt/governance chunks). Cross-reference happens at the Lab report level — Anvil findings reference Forge rules by name in markdown reports, not by querying Forge's DB. No coupling between the two systems.
