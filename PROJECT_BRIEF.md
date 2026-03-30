# Anvil — Project Brief
**Owner:** Mark Lehn (CEO)
**Status:** Scoping
**Created:** 2026-03-27
**Last Updated:** 2026-03-27

---

## What Anvil Is

Anvil is the structural memory of Eluvian. It analyzes codebases across all active projects to build and maintain a persistent, queryable model of how the software actually works — every file, function, class, import, dependency, and test relationship. This model updates every cycle and feeds back into how the Planner writes plans and how agents execute work.

Anvil is a standalone project: Python CLI + SQLite, same stack as Forge (Prompt Forge). It runs on the personal Mac alongside Forge. It has its own agent, its own database, its own knowledge base. The Planner interacts with Anvil's agent through diagnostic and orchestration prompts, same as any other project specialist.

"Forge" is the umbrella concept for systematic improvement through structured analysis. Prompt Forge improves governance and agent prompts by analyzing knowledge artifacts. Anvil (Code Forge) improves engineering quality by analyzing source code, git history, test results, and structural patterns.

---

## What Anvil Is Not

- Not a linter or formatter — it doesn't enforce style rules
- Not a CI/CD system — it doesn't block deploys or run in pipelines
- Not a documentation generator — it produces structural intelligence, not docs
- Not a replacement for agent specialist files — it provides data that specialist files reference
- Not Prompt Forge with different inputs — the taxonomy, scoring, and outputs are purpose-built for code analysis

---

## Problem Statement

Knowledge in Eluvian currently flows through agent reports and CEO context. When the Planner writes a plan for invoice-pulse, it knows high-level facts (68+ tables, 1,200+ tests) from specialist files. But it doesn't know which tables are tightly coupled, which functions are most complex, which test files cover which modules, how gate functions call each other, or where the real architectural seams are. That context gets discovered piecemeal through diagnostic prompts — one question at a time, one session at a time — and then evaporates when the session ends.

Anvil holds that structural understanding persistently. It updates every cycle. The Planner and agents query it instead of rediscovering it.
---

## Analysis Domains

### Core (first cycle targets)
- **Code structure** — file inventory, function/class/method extraction, import graphs, call relationships
- **Testing** — coverage mapping (which tests cover which modules), test health over time, gap identification
- **Volatility** — git history analysis, change frequency per file/function, co-change patterns
- **Code patterns** — duplicated logic, parallel implementation divergence (cached/non-cached), dead code

### Secondary (subsequent cycles)
- **Security** — dependency vulnerabilities, exposed secrets, unsafe patterns
- **Performance** — N+1 queries, synchronous bottlenecks, uncached lookups, per-item DB loops
- **Cross-project patterns** — structural similarities and divergences across projects

### Periodic (quarterly)
- **Dependency health** — version currency, upgrade opportunities, deprecation tracking
- **Methods research** — better approaches to patterns found across the codebase

---

## Architecture Foundation — Borrowed from Study

A diagnostic of Study's chunking architecture (2026-03-27) confirmed that its core data model transfers to code analysis. Anvil borrows these patterns:
### Transferable Patterns
| Study Concept | Anvil Equivalent | What It Does |
|---|---|---|
| `chunks` | `code_chunks` | Functions, classes, modules, configs, test cases |
| `chunk_facet_bindings` | `chunk_symbol_bindings` | Typed relationships: defines/imports/calls/tests/documents |
| `chunk_prerequisites` | `chunk_dependencies` | Directed edges: import chains, call graphs, within_file/cross_file |
| `chunk_similarities` | `chunk_similarities` | Clone detection, refactoring candidates via MinHash |
| `chunk_fingerprints` | `chunk_fingerprints` | Content hashing for change detection across cycles |
| `structural_metadata` | `structural_metadata` | Complexity, signature, import count, coverage, docstring presence |
| `teaching_effectiveness` | `health_score` | Bug correlation, test coverage, volatility, churn rate |
| Content-hash dedup | Content-hash dedup | SHA-256 exact match, MinHash near-duplicate detection |
| Classification-aware chunking | Language-aware chunking | Split Python at class/function, Swift at struct/class/extension, JS at export/component |
| Three-pass merge/split/hash | Three-pass merge/split/hash | Handle small files and oversized files consistently |

### Not Transferred (Learning-Specific)
FSRS scheduling, mastery tracking, Bloom's taxonomy, session exchanges, pedagogical quality ranking.

---

## Pipeline

**SCAN** — Walk project directories, identify changed files via content hashing (SHA-256). Only process what's new since last cycle. Ingest git history for the same period.

**EXTRACT** — Parse source files using language-appropriate tooling (Python AST, Swift parser, JS/TS AST). Build code chunks at function/class/method granularity. Extract relationships: imports, calls, definitions, test coverage mappings. Store in SQLite with typed bindings.

**SCORE** — Evaluate each chunk on: volatility (change frequency), coverage (tested or not), complexity (cyclomatic or equivalent), coupling (inbound/outbound dependency count), staleness (last modified vs dependencies' last modified). Composite health_score derived from these signals.
**LAB** — Analyze scored findings and produce actionable outputs:
- Fix executables for the Planner (e.g., "validator.py gate_3 needs test coverage")
- Constraints for future plans (e.g., "this module has 4 dependents, verify none break")
- Specialist file updates with current structural data
- Alerts for CEO attention (e.g., "security vulnerability in dependency X")

---

## Data Model (Initial)

### Core Tables
- `projects` — registered project metadata
- `code_chunks` — individual code units (function, class, method, module, config block, test case)
- `chunk_fingerprints` — SHA-256 + MinHash signatures per chunk
- `chunk_symbol_bindings` — typed relationships between chunks and symbols (defines/imports/calls/tests/documents)
- `chunk_dependencies` — directed edges between chunks (import/call/inherit), with source tracking (within_file/cross_file)
- `chunk_similarities` — MinHash similarity pairs above threshold

### Signal Tables
- `git_changes` — per-file change history from git log (commit hash, date, files changed, message)
- `test_results` — per-run test outcomes (pass/fail/skip counts, failed test names, date)
- `health_scores` — composite per-chunk scores (volatility, coverage, complexity, coupling, staleness)
- `cycle_reports` — per-cycle summaries and Lab findings

### Scoring Dimensions
| Dimension | Source | Signal |
|---|---|---|
| Volatility | git_changes | Change frequency, recency, co-change partners |
| Coverage | test_results + chunk_symbol_bindings | Which chunks have test bindings, coverage % |
| Complexity | structural_metadata | Cyclomatic complexity, nesting depth, parameter count |
| Coupling | chunk_dependencies | Inbound + outbound edge count |
| Staleness | git_changes + chunk_dependencies | Last modified vs dependency last modified |
---

## Language Support

### Phase 1 — Python (invoice-pulse only)
- Tooling: Python AST module (stdlib, no dependencies)
- Special: SQLAlchemy pattern recognition for ORM → table mappings
- Expand to Forge and freight-kb after first cycle proves the pipeline

### Phase 2 — JavaScript/TypeScript
- Projects: study (Tauri/React)
- Tooling: TypeScript AST via ts-morph or similar
- Special: React component relationship tracking

### Phase 3 — Swift
- Projects: BrewBuddy, SimpleScreen
- Tooling: Swift syntax parsing (SwiftSyntax or regex-based extraction)
- Special: SwiftUI view hierarchy tracking

---

## Agent Interface

Anvil has its own agent (to be created as a specialist file). The Planner and CEO interact with it through:

- **Diagnostic prompts** — "What's the structural risk profile of invoice-pulse's validation pipeline?"
- **Orchestration prompts** — "Run a full cycle against invoice-pulse and deposit findings"
- **Query prompts** — "Which functions in engines/validator.py have no test coverage and high volatility?"

Anvil's agent reads the SQLite database, runs analysis, and deposits findings to Anvil's knowledge base. The Planner references those findings when writing plans for other projects.
---

## Feedback Loop into Eluvian Operations

```
Anvil cycle runs
    → Structural findings deposited
        → Planner reads findings before writing plans
            → Plans include Anvil-sourced constraints
                → Agents execute with structural context
                    → Code changes picked up in next Anvil cycle
                        → Model updates
```

---

## CEO Decisions (2026-03-27)

1. **Cycle frequency** — On-demand, same as Forge. CEO says "run an Anvil session" to trigger.
2. **Initial scope** — Invoice-pulse only for Phase 1. Other Python projects introduced after first cycle proves the pipeline.
3. **Git history depth** — Seed with last few weeks of commit history. Full history import deferred.
4. **Test result ingestion** — Both: Anvil can run test suites directly AND ingest results from agent-deposited files. Dual-mode from the start.

---

## Project Structure

```
/anvil
├── PROJECT_BRIEF.md
├── PROJECT_STATUS.md
├── CLAUDE.md
├── /agents
│   └── [specialist files TBD]
├── /knowledge
│   ├── /architecture
│   ├── /decisions
│   │   └── /Done
│   ├── /development
│   ├── /design
│   ├── /qa
│   └── /research
├── /src
│   ├── config.py
│   ├── scanner.py
│   ├── extractor.py
│   ├── scorer.py
│   ├── lab.py
│   └── /parsers
│       ├── python_parser.py
│       ├── javascript_parser.py  (Phase 2)
│       └── swift_parser.py       (Phase 3)
├── /tests
├── anvil.db
└── requirements.txt
```
---

## Dependencies

- Python 3.x (stdlib AST module for Phase 1)
- SQLite
- Git CLI (for git log parsing)
- MinHash library (datasketch or similar)
- No Anthropic SDK — Claude Code is the intelligence layer, same as Forge
