"""
Daemon archetype — bellows rules per BP3 design.

Registers the daemon archetype on import. Classification rules,
scoring weights, functional roles, best practices, and detection checks
for the bellows file-watching daemon.
"""
from __future__ import annotations

import re

from src.classifier_registry import ArchetypeDefinition, register_archetype

# --- Classification Rules (priority order: decorator > name > file_path > utility) ---

DECORATOR_RULES = []

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

# --- Functional Roles (13 roles, 4 groups) ---

ROLES = [
    # Orchestration
    ("plan_dispatcher", "Core daemon loop: file watching, plan detection, dispatch coordination, parallel grouping, queue drain", "orchestration"),
    ("worktree_manager", "Git worktree creation, teardown, diff capture, merge conflict handling", "orchestration"),
    ("agent_lifecycle", "Agent spawning via Claude Code CLI, step execution, prompt construction, output parsing", "orchestration"),
    # Governance
    ("gate_checker", "QA validation gates checking agent step output before verdict decision", "governance"),
    ("verdict_handler", "Verdict posting, consumption, ledger logging, malformed-verdict detection", "governance"),
    ("plan_validator", "Pre-dispatch plan validation, decision block extraction, header field type checks", "governance"),
    # Configuration
    ("config_loader", "Configuration file loading, bellows root resolution, secret merging", "configuration"),
    # Infrastructure
    ("notifier", "Push notifications (Pushover), event coalescing, deferred flush, response server", "infrastructure"),
    ("cache_manager", "Shadow file cache for plan dedup and change detection", "infrastructure"),
    ("plan_parser", "Plan header/metadata parsing, step number extraction, slug computation", "infrastructure"),
    ("data_model", "SQLite schema migrations and run recording", "infrastructure"),
    ("cli_script", "Standalone maintenance and migration scripts", "interface"),
    ("utility", "Generic helpers with no domain logic (fallback)", "infrastructure"),
]

# --- Scoring Weights ---

SCORING_WEIGHTS = {
    "plan_dispatcher": {
        "volatility": 0.20, "coverage": 0.25, "complexity": 0.25,
        "coupling": 0.20, "staleness": 0.10,
    },
    "gate_checker": {
        "volatility": 0.15, "coverage": 0.35, "complexity": 0.10,
        "coupling": 0.15, "staleness": 0.25,
    },
    "verdict_handler": {
        "volatility": 0.20, "coverage": 0.30, "complexity": 0.15,
        "coupling": 0.20, "staleness": 0.15,
    },
    "agent_lifecycle": {
        "volatility": 0.20, "coverage": 0.25, "complexity": 0.20,
        "coupling": 0.20, "staleness": 0.15,
    },
    "worktree_manager": {
        "volatility": 0.25, "coverage": 0.25, "complexity": 0.15,
        "coupling": 0.20, "staleness": 0.15,
    },
    "notifier": {
        "volatility": 0.15, "coverage": 0.20, "complexity": 0.20,
        "coupling": 0.15, "staleness": 0.30,
    },
    "plan_validator": {
        "volatility": 0.15, "coverage": 0.35, "complexity": 0.10,
        "coupling": 0.15, "staleness": 0.25,
    },
    "utility": {
        "volatility": 0.20, "coverage": 0.20, "complexity": 0.30,
        "coupling": 0.15, "staleness": 0.15,
    },
}

# --- Role Thresholds ---

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

# --- Best Practices ---

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

# --- Content-based checks (regex on chunk content) ---

CONTENT_CHECKS = {
    "idempotent_schema": [
        {"pattern": re.compile(r"CREATE\s+TABLE\s+(?!IF\s+NOT\s+EXISTS)", re.IGNORECASE),
         "message": "CREATE TABLE without IF NOT EXISTS"},
    ],
    "append_only_ledger": [
        {"pattern": re.compile(r"UPDATE.*ledger|DELETE.*ledger", re.IGNORECASE),
         "message": "UPDATE or DELETE on ledger data"},
    ],
    "pure_functions": [
        {"pattern": re.compile(r"open\s*\("),
         "message": "File I/O found in utility function"},
        {"pattern": re.compile(r"subprocess"),
         "message": "Subprocess call found in utility function"},
    ],
}

# --- Structural metadata checks ---

STRUCTURAL_CHECKS = {
    "structured_gate_return": [
        {"field": "line_count", "threshold": 60, "direction": "max",
         "message": "Gate function has {value} lines (threshold: 60)"},
    ],
}

# --- Register ---

daemon = ArchetypeDefinition(
    name="daemon",
    roles=ROLES,
    decorator_rules=DECORATOR_RULES,
    name_rules=NAME_RULES,
    file_path_rules=FILE_PATH_RULES,
    scoring_weights=SCORING_WEIGHTS,
    role_thresholds=ROLE_THRESHOLDS,
    best_practices=BEST_PRACTICES,
    content_checks=CONTENT_CHECKS,
    structural_checks=STRUCTURAL_CHECKS,
)

register_archetype(daemon)
