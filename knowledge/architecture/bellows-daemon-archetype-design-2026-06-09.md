# Bellows Daemon Archetype Design
**Date:** 2026-06-09 | **Agent:** Anvil Systems Analyst | **Source:** BP3 Diagnostic

## Context

This design proposes the `daemon` archetype for bellows — the second archetype head after `flask_service` (invoice-pulse). Currently bellows is registered in SCAN_TARGETS with `archetype: "flask_service"`, causing all 155 classifiable chunks to fall through to the `utility` fallback (no Flask routes, no validation gates, no `engines/` directory). This diagnostic refines the preliminary C.7 taxonomy from the 2026-06-08 blueprint against the actual bellows chunk population in the live DB.

### Population Baseline (Cycle 2)

- **Total bellows chunks:** 3,695
- **Chunk type breakdown:** module=3,088 | test_case=452 | function=127 | method=20 | class=8
- **Classifiable chunks** (function + method + class): **155**
- **Current functional_role distribution:** utility=155 (100%) — confirms the 2026-06-08 BACKLOG mono-role finding

---

## Section 1 — Role Taxonomy

Starting from C.7's preliminary 9 roles, refined against the actual bellows file/name population. Changes from C.7:

- **Confirmed:** plan_dispatcher, worktree_manager, agent_lifecycle, config_loader, cache_manager, utility
- **Renamed:** cli_command → cli_script (bellows has no interactive CLI commands; its scripts are batch maintenance tools)
- **Dropped:** git_operator (bellows does not have standalone git operation modules; git operations are embedded in worktree_manager), template_engine (no template rendering module exists in bellows)
- **Added:** gate_checker (21 chunks in gates.py — QA validation gates are a major bellows subsystem), verdict_handler (13 chunks across verdict.py + bellows.py — verdict lifecycle is a distinct domain), plan_validator (10 chunks in validators.py + decisions.py — pre-dispatch validation), notifier (19 chunks in notifier.py + server.py — push notifications + response server), plan_parser (7 chunks — plan metadata extraction helpers), data_model (2 chunks — DB schema/recording)

### Final Taxonomy: 13 Roles, 4 Groups

| Role | Group | Description | Example bellows chunks (file:name) |
|---|---|---|---|
| plan_dispatcher | orchestration | Core daemon loop: file watching, plan detection, dispatch coordination, parallel grouping, queue drain | bellows.py:Bellows, bellows.py:handle_new_plan, bellows.py:run_plan, bellows.py:on_created |
| worktree_manager | orchestration | Git worktree creation, teardown, diff capture, merge conflict handling | bellows.py:_create_worktree, bellows.py:_teardown_worktree, bellows.py:WorktreeCreationError |
| agent_lifecycle | orchestration | Agent spawning via Claude Code CLI, step execution, prompt construction, output parsing | runner.py:run_step, planner.py:build_system_prompt, planner.py:consult, parser.py:parse |
| gate_checker | governance | QA validation gates checking agent step output before verdict decision | gates.py:check, gates.py:_gate_deposit_exists, gates.py:_gate_scope_check, gates.py:_gate_rule_22_verification |
| verdict_handler | governance | Verdict posting, consumption, ledger logging, malformed-verdict detection | verdict.py:check_verdict, verdict.py:post_verdict_request, bellows.py:_consume_verdicts |
| plan_validator | governance | Pre-dispatch plan validation, decision block extraction, header field type checks | validators.py:validate_at_claim, validators.py:check_stop_prose, decisions.py:extract_decision_blocks |
| config_loader | configuration | Configuration file loading, bellows root resolution, secret merging | bellows.py:load_config, bellows_root.py:resolve_bellows_root |
| notifier | infrastructure | Push notifications (Pushover), event coalescing, deferred flush, response server | notifier.py:notify_verdict_request, notifier.py:push, server.py:ResponseServer |
| cache_manager | infrastructure | Shadow file cache for plan dedup and change detection | bellows.py:_shadow_path, bellows.py:_read_shadow, bellows.py:_write_shadow, bellows.py:_delete_shadow |
| plan_parser | infrastructure | Plan header/metadata parsing, step number extraction, slug computation | bellows.py:extract_step_number, bellows.py:extract_total_steps, bellows.py:header_says_pause, bellows.py:slug_for |
| data_model | infrastructure | SQLite schema migrations and run recording | bellows.py:migrate_db, bellows.py:record_run |
| cli_script | interface | Standalone maintenance and migration scripts | scripts/check_backlog_freshness.py:main, scripts/migrate_config.py:migrate |
| utility | infrastructure | Generic helpers with no domain logic (fallback) | test helper functions (24 chunks in tests/) |

---

## Section 2 — Classifier Rules (Priority-Ordered)

Classification priority: decorator_rules → name_rules → file_path_rules → utility fallback.

### 2.1 Decorator Rules

Empty — bellows is a CLI daemon with no decorator-based routing (no Flask, no Click decorators on scanned functions).

```python
DECORATOR_RULES = []
```

### 2.2 Name Rules (34 rules)

```python
NAME_RULES = [
    # gate_checker — QA validation gate functions
    (re.compile(r"^_gate_"), "gate_checker"),

    # notifier — push notification functions
    (re.compile(r"^notify_\w+"), "notifier"),
    (re.compile(r"^(?:push|init_notifications)$"), "notifier"),

    # worktree_manager — git worktree lifecycle
    (re.compile(r"^_?(?:create|teardown)_worktree$"), "worktree_manager"),
    (re.compile(r"^Worktree(?:Creation|Teardown)Error$"), "worktree_manager"),
    (re.compile(r"^_?capture_git_diff$"), "worktree_manager"),
    (re.compile(r"^_?parse_diff_stat$"), "worktree_manager"),

    # verdict_handler — verdict lifecycle
    (re.compile(r"^(?:check_verdict|post_verdict_request|log_to_ledger)$"), "verdict_handler"),
    (re.compile(r"^_consume_verdicts$"), "verdict_handler"),
    (re.compile(r"^_cleanup_verdicts"), "verdict_handler"),
    (re.compile(r"^_scan_misplaced_verdicts$"), "verdict_handler"),
    (re.compile(r"^extract_primary_deposit$"), "verdict_handler"),

    # agent_lifecycle — agent spawning and execution
    (re.compile(r"^build_(?:system_prompt|context_envelope|consult_file)$"), "agent_lifecycle"),
    (re.compile(r"^run_step$"), "agent_lifecycle"),
    (re.compile(r"^consult$"), "agent_lifecycle"),

    # config_loader — configuration loading
    (re.compile(r"^load_config$"), "config_loader"),
    (re.compile(r"^resolve_bellows_root$"), "config_loader"),

    # data_model — schema and recording
    (re.compile(r"^migrate_db$"), "data_model"),
    (re.compile(r"^record_run$"), "data_model"),

    # plan_dispatcher — plan detection and dispatch
    (re.compile(r"^handle_(?:new_plan|parallel_group)$"), "plan_dispatcher"),
    (re.compile(r"^run_plan$"), "plan_dispatcher"),
    (re.compile(r"^is_runnable_plan$"), "plan_dispatcher"),
    (re.compile(r"^on_(?:created|modified|moved)$"), "plan_dispatcher"),
    (re.compile(r"^(?:Bellows|PlanHandler)$"), "plan_dispatcher"),

    # plan_parser — plan metadata parsing
    (re.compile(r"^extract_(?:step_number|total_steps|parallel_group)$"), "plan_parser"),
    (re.compile(r"^header_says_pause$"), "plan_parser"),
    (re.compile(r"^is_final_step$"), "plan_parser"),
    (re.compile(r"^slug_for$"), "plan_parser"),
    (re.compile(r"^_apply_defensive_header_defaults$"), "plan_parser"),

    # plan_validator — plan validation
    (re.compile(r"^validate_at_claim$"), "plan_validator"),
    (re.compile(r"^check_(?:dispatch_mismatch|missing_dispatch_mode|header_field_types|pause_for_verdict_value|stop_prose)"), "plan_validator"),
    (re.compile(r"^extract_decision_blocks$"), "plan_validator"),

    # cache_manager — shadow file cache
    (re.compile(r"^_?(?:shadow_path|read_shadow|write_shadow|delete_shadow)$"), "cache_manager"),
]
```

### 2.3 File Path Rules (12 rules)

```python
FILE_PATH_RULES = [
    (re.compile(r"^gates\.py$"), "gate_checker"),
    (re.compile(r"^verdict\.py$"), "verdict_handler"),
    (re.compile(r"^notifier\.py$"), "notifier"),
    (re.compile(r"^server\.py$"), "notifier"),
    (re.compile(r"^runner\.py$"), "agent_lifecycle"),
    (re.compile(r"^planner\.py$"), "agent_lifecycle"),
    (re.compile(r"^parser\.py$"), "agent_lifecycle"),
    (re.compile(r"^validators\.py$"), "plan_validator"),
    (re.compile(r"^decisions\.py$"), "plan_validator"),
    (re.compile(r"^bellows_root\.py$"), "config_loader"),
    (re.compile(r"^scripts/"), "cli_script"),
    (re.compile(r"^bellows\.py$"), "plan_dispatcher"),
]
```

### 2.4 Projected Role Distribution

Simulation against the 155 classifiable bellows chunks:

| Role | Count | % | Matched By | Source Files |
|---|---|---|---|---|
| plan_dispatcher | 25 | 16.1% | 10 name + 15 file_path | bellows.py |
| gate_checker | 21 | 13.5% | 10 name + 11 file_path | gates.py |
| notifier | 19 | 12.3% | 8 name + 11 file_path | notifier.py (14), server.py (5) |
| verdict_handler | 13 | 8.4% | 7 name + 6 file_path | verdict.py (10), bellows.py (3) |
| cli_script | 12 | 7.7% | 12 file_path | scripts/*.py |
| agent_lifecycle | 10 | 6.5% | 4 name + 6 file_path | planner.py (6), runner.py (2), parser.py (2) |
| plan_validator | 10 | 6.5% | 7 name + 3 file_path | validators.py (7), decisions.py (3) |
| plan_parser | 7 | 4.5% | 7 name | bellows.py |
| worktree_manager | 6 | 3.9% | 6 name | bellows.py |
| cache_manager | 4 | 2.6% | 4 name | bellows.py |
| config_loader | 2 | 1.3% | 2 name | bellows.py (1), bellows_root.py (1) |
| data_model | 2 | 1.3% | 2 name | bellows.py |
| utility | 24 | 15.5% | 24 fallback | tests/*.py (test helpers) |
| **Total** | **155** | **100%** | | |

**Residual utility:** 24/155 = 15.5% — all are test helper functions/classes (fixtures, factory functions). This is a dramatic improvement from 100% utility.

**Non-utility classification rate:** 131/155 = 84.5%.

---

## Section 3 — Scoring Profiles (Defaults, Untuned)

These are sensible starting defaults adapted to daemon roles. **Explicitly flagged as untuned** — revisit only if bellows becomes a recurring cycle target requiring scoring precision.

### 3.1 Scoring Weights

Each weight set sums to 1.0. Rationale per role:

```python
SCORING_WEIGHTS = {
    "plan_dispatcher": {
        # Core orchestrator: complexity and coupling matter most (many dependencies, branching logic)
        "volatility": 0.20, "coverage": 0.25, "complexity": 0.25,
        "coupling": 0.20, "staleness": 0.10,
    },
    "gate_checker": {
        # Gates must be well-tested; individual gates are simple but staleness is risky
        "volatility": 0.15, "coverage": 0.35, "complexity": 0.10,
        "coupling": 0.15, "staleness": 0.25,
    },
    "verdict_handler": {
        # Verdict correctness is critical; coverage and coupling both important
        "volatility": 0.20, "coverage": 0.30, "complexity": 0.15,
        "coupling": 0.20, "staleness": 0.15,
    },
    "agent_lifecycle": {
        # Agent management: balanced profile, coupling matters (subprocess + API calls)
        "volatility": 0.20, "coverage": 0.25, "complexity": 0.20,
        "coupling": 0.20, "staleness": 0.15,
    },
    "worktree_manager": {
        # Git operations: volatility matters (OS/git version sensitivity), coupling moderate
        "volatility": 0.25, "coverage": 0.25, "complexity": 0.15,
        "coupling": 0.20, "staleness": 0.15,
    },
    "notifier": {
        # Notifications: staleness is primary risk (external API drift), low complexity
        "volatility": 0.15, "coverage": 0.20, "complexity": 0.20,
        "coupling": 0.15, "staleness": 0.30,
    },
    "plan_validator": {
        # Validators: coverage critical (must catch invalid plans), similar to gates
        "volatility": 0.15, "coverage": 0.35, "complexity": 0.10,
        "coupling": 0.15, "staleness": 0.25,
    },
    "utility": {
        # Generic helpers: complexity is primary concern, balanced otherwise
        "volatility": 0.20, "coverage": 0.20, "complexity": 0.30,
        "coupling": 0.15, "staleness": 0.15,
    },
}
```

### 3.2 Role Thresholds

```python
ROLE_THRESHOLDS = {
    "plan_dispatcher": {
        "complexity_threshold": 0.75,
        "coupling_hotspot_threshold": 0.85,
    },
    "gate_checker": {
        "complexity_threshold": 0.90,
        "coupling_hotspot_threshold": 0.80,
    },
    "verdict_handler": {
        "complexity_threshold": 0.80,
        "coupling_hotspot_threshold": 0.80,
    },
    "agent_lifecycle": {
        "complexity_threshold": 0.80,
        "coupling_hotspot_threshold": 0.75,
    },
    "worktree_manager": {
        "complexity_threshold": 0.70,
        "coupling_hotspot_threshold": 0.80,
    },
    "utility": {
        "complexity_threshold": 0.50,
        "coupling_hotspot_threshold": 0.80,
    },
}
```

Roles without explicit thresholds (notifier, plan_validator, config_loader, cache_manager, plan_parser, data_model, cli_script) inherit the global defaults from `config.py` (complexity=0.8, coupling=0.8).

---

## Section 4 — Best Practices + Content/Structural Checks

Minimal daemon-appropriate set. Sparse by design — practices are added only where bellows source exhibits a clear pattern worth enforcing.

### 4.1 Best Practices (8 rules, 5 roles)

```python
BEST_PRACTICES = [
    # gate_checker
    ("gate_checker", "structured_gate_return",
     "Each gate returns a consistent tuple of (pass/fail, reason, details)",
     "Gate function returning inconsistent types or missing reason string",
     "curated", "high"),
    ("gate_checker", "independent_gate_logic",
     "Each gate checks one concern independently without depending on other gates' results",
     "Gate function calling another gate or reading shared mutable state between gates",
     "curated", "medium"),

    # plan_dispatcher
    ("plan_dispatcher", "idempotent_dispatch",
     "Plan dispatch is idempotent — re-dispatching the same plan produces no side effects",
     "Missing seen-cache check; duplicate dispatch on filesystem event burst",
     "curated", "high"),
    ("plan_dispatcher", "claim_before_execute",
     "Plans are claimed (renamed to in-progress) before any execution begins",
     "Execution starting without file rename; race window between detection and claim",
     "curated", "high"),

    # worktree_manager
    ("worktree_manager", "cleanup_on_failure",
     "Worktree directories are cleaned up even when creation or teardown partially fails",
     "Orphaned worktree directory after WorktreeCreationError; missing force-remove fallback",
     "curated", "high"),

    # verdict_handler
    ("verdict_handler", "append_only_ledger",
     "Verdict ledger entries are append-only JSON lines; no updates or deletes",
     "UPDATE or DELETE on ledger file; overwriting existing verdict entries",
     "curated", "high"),

    # data_model
    ("data_model", "idempotent_schema",
     "All CREATE TABLE use IF NOT EXISTS; migrations wrapped in try/except",
     "Missing IF NOT EXISTS; bare ALTER TABLE without error handling",
     "curated", "high"),

    # utility
    ("utility", "pure_functions",
     "No side effects, no DB access, no file I/O; pure data transformation only",
     "Functions with file open() calls or subprocess calls in utility helpers",
     "curated", "medium"),
]
```

### 4.2 Content Checks

```python
CONTENT_CHECKS = {
    "idempotent_schema": [
        {"pattern": re.compile(r"CREATE\s+TABLE\s+(?!IF\s+NOT\s+EXISTS)", re.IGNORECASE),
         "message": "CREATE TABLE without IF NOT EXISTS"},
    ],
    "append_only_ledger": [
        {"pattern": re.compile(r"\bUPDATE\b.*\bledger\b|\bDELETE\b.*\bledger\b", re.IGNORECASE),
         "message": "UPDATE or DELETE on ledger data"},
    ],
    "pure_functions": [
        {"pattern": re.compile(r"\bopen\s*\("),
         "message": "File I/O found in utility function"},
        {"pattern": re.compile(r"\bsubprocess\b"),
         "message": "Subprocess call found in utility function"},
    ],
}
```

### 4.3 Structural Checks

```python
STRUCTURAL_CHECKS = {
    "structured_gate_return": [
        {"field": "line_count", "threshold": 60, "direction": "max",
         "message": "Gate function has {value} lines (threshold: 60)"},
    ],
}
```

---

## Section 5 — ArchetypeDefinition Assembly + Executable Hand-Off

### 5.1 ArchetypeDefinition Fields

The daemon archetype mirrors the `flask_service.py` shape exactly:

```python
daemon = ArchetypeDefinition(
    name="daemon",
    roles=ROLES,                      # 13 (role, description, group) tuples
    decorator_rules=DECORATOR_RULES,  # [] — empty for daemons
    name_rules=NAME_RULES,            # 34 (regex, role) pairs
    file_path_rules=FILE_PATH_RULES,  # 12 (regex, role) pairs
    scoring_weights=SCORING_WEIGHTS,  # 8 role-specific weight dicts
    role_thresholds=ROLE_THRESHOLDS,  # 6 role-specific threshold dicts
    best_practices=BEST_PRACTICES,    # 8 (role, id, desc, anti, source, severity) tuples
    content_checks=CONTENT_CHECKS,    # 3 practice IDs → pattern lists
    structural_checks=STRUCTURAL_CHECKS,  # 1 practice ID → threshold list
)

register_archetype(daemon)
```

### 5.2 SCAN_TARGETS Update

The bellows entry in `src/config.py` currently reads:

```python
"bellows": {
    "path": "/Users/marklehn/Developer/GitHub/bellows",
    "language": "python",
    "archetype": "flask_service",  # ← WRONG
},
```

Change to:

```python
"bellows": {
    "path": "/Users/marklehn/Developer/GitHub/bellows",
    "language": "python",
    "archetype": "daemon",  # ← CORRECT
},
```

### 5.3 Archetype Import Registration

Add to `src/archetypes/__init__.py` (or create if absent):

```python
import src.archetypes.daemon  # noqa: F401 — triggers register_archetype on import
```

This mirrors the existing pattern for `flask_service`.

### 5.4 Additive Regression Expectation

The downstream implementing executable (DEV + QA) must verify:

1. **Invoice-pulse byte-identical:** Run classify-only on invoice-pulse; compare the classify-only hash (functional_role assignments) against baseline. The flask_service archetype is untouched — zero changes expected. **Use classify-only hash, NOT composite hash** (per 2026-06-09 LESSON: composite hashes include time-dependent fields like `last_scanned` that produce false-negative regression signals).

2. **Bellows meaningful classification:** Run classify on bellows with `archetype: "daemon"`. Verify:
   - At least 80% of classifiable chunks receive a non-utility role
   - Projected: 131/155 = 84.5% non-utility
   - No chunk receives a role not in the daemon ROLES list
   - The utility residual is exclusively test helper chunks

### 5.5 Gap Assessment

| Gap | Current State | Proposed State | Change Required |
|---|---|---|---|
| daemon archetype missing | No `daemon` archetype registered in ARCHETYPES | `src/archetypes/daemon.py` with 13 roles, 34 name rules, 12 file_path rules, 8 best practices | NEW file |
| bellows mono-role | 155/155 classifiable chunks = utility | 131/155 meaningful roles, 24 utility (test helpers only) | Archetype registration |
| SCAN_TARGETS archetype wrong | `"archetype": "flask_service"` | `"archetype": "daemon"` | Edit `src/config.py` line 21 |
| Role-specific scoring absent | Global defaults applied uniformly | 8 role-specific scoring weight profiles | In daemon.py |
| Daemon best practices absent | No bellows-specific practice rules | 8 rules across 5 roles with content/structural checks | In daemon.py |

---

## Section 6 — Verification Blocks

### Rule 39 Verification

| # | Claim | Query | Expected Output |
|---|---|---|---|
| V1 | Bellows project exists with id=2 | `SELECT id FROM projects WHERE name = 'bellows'` | 2 |
| V2 | Total bellows chunk count = 3695 | `SELECT COUNT(*) FROM code_chunks WHERE project_id = 2` | 3695 |
| V3 | Classifiable chunks = 155 | `SELECT COUNT(*) FROM code_chunks WHERE project_id = 2 AND chunk_type IN ('function','method','class')` | 155 |
| V4 | All classifiable chunks are utility | `SELECT functional_role, COUNT(*) FROM code_chunks WHERE project_id = 2 AND chunk_type IN ('function','method','class') GROUP BY functional_role` | utility\|155 |
| V5 | No existing daemon archetype | `python3 -c "from src.classifier_registry import ARCHETYPES; print('daemon' in ARCHETYPES)"` | False |
| V6 | Current bellows SCAN_TARGET uses flask_service | Inspect `src/config.py` line 21 | `"archetype": "flask_service"` |

---

## Output Receipt
**Agent:** Anvil Systems Analyst
**Step:** 1 (SA diagnostic)
**Status:** Complete

### What Was Done
Designed the bellows `daemon` archetype: 13-role taxonomy across 4 groups, 34 name rules + 12 file_path rules (no decorator rules), 8 scoring weight profiles, 6 role threshold sets, 8 best practice rules with content/structural checks. Projected 84.5% non-utility classification rate (131/155 chunks). Verified current all-utility baseline against live DB.

### Files Deposited
- `anvil/knowledge/architecture/bellows-daemon-archetype-design-2026-06-09.md` — full daemon archetype design

### Files Created or Modified (Code)
- None (design diagnostic only — no source changes)

### Decisions Made
- Dropped C.7's `git_operator` and `template_engine` roles (no corresponding bellows modules)
- Added 6 roles not in C.7: gate_checker, verdict_handler, plan_validator, notifier, plan_parser, data_model
- Renamed C.7's `cli_command` to `cli_script` (batch scripts, not interactive CLI)
- Used `bellows.py` file_path fallback → plan_dispatcher (daemon core catch-all, mirrors flask_service's `web/` → route_handler pattern)
- Test helper chunks (24) intentionally left as utility fallback — not worth a dedicated role

### Flags for CEO
- None

### Flags for Next Step
- Implementing executable should create `src/archetypes/daemon.py`, update `src/config.py` SCAN_TARGETS, and verify regression (classify-only hash for invoice-pulse, role distribution for bellows)
- Use classify-only hash for regression, NOT composite hash (2026-06-09 LESSON)
