# Anvil — Domain Glossary

## Terms

### Code Chunk
Atomic unit of code — a function, class, method, module, config block, or test case. The fundamental entity in Anvil's data model. Each chunk is stored in the `code_chunks` table with its type, source file, line range, and content hash.

### Symbol Binding
Typed relationship between a chunk and a symbol. Binding types: defines, imports, calls, tests, documents. Stored in `chunk_symbol_bindings`. Example: a function chunk "defines" the symbol `validate_invoice`, while a test chunk "tests" that same symbol.

### Chunk Dependency
Directed edge between two chunks — representing import chains, call graphs, or inheritance relationships. Stored in `chunk_dependencies` with source tracking (within_file or cross_file). Used to compute coupling scores and trace impact of changes.

### Health Score
Composite per-chunk score derived from five dimensions: volatility, coverage, complexity, coupling, and staleness. Stored in `health_scores`. Higher scores indicate healthier code. The score feeds into Lab output to prioritize attention and generate fix executables.

### Cycle
One complete SCAN → EXTRACT → SCORE → LAB run against a registered project. Each cycle produces a `cycle_reports` entry summarizing findings, changes detected, and Lab outputs generated. Cycles are on-demand (CEO-triggered).

### Volatility
Change frequency derived from git history. Measured per file and per chunk using `git_changes` data. High volatility combined with low test coverage is a primary risk signal.

### Coverage
Test bindings for a chunk — whether a chunk has associated test chunks that exercise it. Derived from `chunk_symbol_bindings` (type = "tests") cross-referenced with `test_results`. A chunk with zero test bindings has zero coverage.

### Coupling
Inbound plus outbound dependency count for a chunk. Derived from `chunk_dependencies`. High coupling means a chunk is deeply connected to other parts of the codebase — changes to it have wide blast radius.

### Staleness
How recently a chunk was modified relative to when its dependencies were last modified. A chunk that hasn't changed while its dependencies have evolved is potentially stale — it may rely on outdated interfaces or assumptions.

### MinHash Signature
Locality-sensitive hash computed via the datasketch library for near-duplicate detection. Stored in `chunk_fingerprints`. Two chunks with high MinHash similarity (above threshold) are flagged as potential clones or refactoring candidates in `chunk_similarities`.

### Content Hash
SHA-256 hash of file content used for change detection between cycles. Stored in `chunk_fingerprints`. If a file's content hash hasn't changed since the last cycle, SCAN skips it. This is the primary mechanism for incremental processing.
