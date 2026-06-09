"""
Flask service archetype — invoice-pulse rules migrated 1:1.

Registers the flask_service archetype on import. All classification rules,
scoring weights, functional roles, best practices, and detection checks
that were previously hardcoded across classifier.py, config.py, db.py,
and detector.py are consolidated here.
"""
from __future__ import annotations

import re

from src.classifier_registry import ArchetypeDefinition, register_archetype

# --- Classification Rules (priority order preserved exactly) ---

DECORATOR_RULES = [
    (re.compile(r"@\w+_bp\.route\("), "route_handler"),
    (re.compile(r"@\w+_bp\.get\("), "route_handler"),
    (re.compile(r"@\w+_bp\.post\("), "route_handler"),
    (re.compile(r"@app\.route\("), "route_handler"),
]

NAME_RULES = [
    (re.compile(r"^gate_\d+_"), "validation_gate"),
    (re.compile(r"^validate_invoice$"), "validation_orchestrator"),
    (re.compile(r"^validate_batch$"), "batch_validator"),
    (re.compile(r"^route_actions$"), "action_router"),
    (re.compile(r"^generate_\w+_email$"), "content_generator"),
    (re.compile(r"^generate_\w+_ticket$"), "content_generator"),
    (re.compile(r"^detect_\w+_drift$"), "anomaly_detector"),
    (re.compile(r"^discover_\w+"), "pattern_learner"),
    (re.compile(r"^learn_\w+_rules$"), "pattern_learner"),
    (re.compile(r"^check_contradictions$"), "circuit_breaker"),
    (re.compile(r"^run_pro_exit_interviews$"), "exit_interviewer"),
    (re.compile(r"^check_and_log_changes$"), "lifecycle_tracker"),
    (re.compile(r"^run_ingestion$"), "ingestion_orchestrator"),
    (re.compile(r"^run_pipeline$"), "pipeline_orchestrator"),
    (re.compile(r"^run_backup$"), "data_guardian"),
    (re.compile(r"^pre_ingestion_check$"), "data_guardian"),
    (re.compile(r"^post_ingestion_verify$"), "data_guardian"),
    (re.compile(r"^import_pst$"), "email_processor"),
    (re.compile(r"^validate_billto$"), "address_normalizer"),
    (re.compile(r"^_normalize_billto"), "address_normalizer"),
    (re.compile(r"^_create_tables$"), "data_model"),
    (re.compile(r"^_migrate_\w+"), "data_model"),
    (re.compile(r"^_safe_add_column"), "data_model"),
    (re.compile(r"^init_db$"), "data_model"),
    (re.compile(r"^log_event$"), "audit_logger"),
]

FILE_PATH_RULES = [
    (re.compile(r"^engines/confidence\.py$"), "confidence_engine"),
    (re.compile(r"^engines/validator\.py$"), "validation_gate"),
    (re.compile(r"^engines/action_router\.py$"), "action_router"),
    (re.compile(r"^engines/email_generator\.py$"), "content_generator"),
    (re.compile(r"^engines/drift_detector\.py$"), "anomaly_detector"),
    (re.compile(r"^engines/pattern_learner\.py$"), "pattern_learner"),
    (re.compile(r"^engines/circuit_breaker\.py$"), "circuit_breaker"),
    (re.compile(r"^engines/exit_interview\.py$"), "exit_interviewer"),
    (re.compile(r"^engines/lifecycle\.py$"), "lifecycle_tracker"),
    (re.compile(r"^engines/carrier_identity\.py$"), "entity_matcher"),
    (re.compile(r"^engines/billto_validator\.py$"), "address_normalizer"),
    (re.compile(r"^engines/pst_importer\.py$"), "email_processor"),
    (re.compile(r"^engines/email_parser\.py$"), "email_processor"),
    (re.compile(r"^engines/email_matcher\.py$"), "email_processor"),
    (re.compile(r"^engines/backtest\.py$"), "action_router"),
    (re.compile(r"^ingestion/ingest\.py$"), "ingestion_orchestrator"),
    (re.compile(r"^ingestion/xml_parser\.py$"), "data_parser"),
    (re.compile(r"^ingestion/csv_reader\.py$"), "data_parser"),
    (re.compile(r"^web/reporting\.py$"), "report_generator"),
    (re.compile(r"^web/gap_dashboard\.py$"), "report_generator"),
    (re.compile(r"^web/intelligence\.py$"), "report_generator"),
    (re.compile(r"^web/documents\.py$"), "document_manager"),
    (re.compile(r"^web/"), "route_handler"),
    (re.compile(r"^database\.py$"), "data_model"),
    (re.compile(r"^contract_tables\.py$"), "data_model"),
    (re.compile(r"^config\.py$"), "configuration"),
    (re.compile(r"^run_pipeline\.py$"), "pipeline_orchestrator"),
    (re.compile(r"^validate_batch\.py$"), "batch_validator"),
    (re.compile(r"^backup\.py$"), "data_guardian"),
    (re.compile(r"^integrity\.py$"), "data_guardian"),
]

# --- Functional Roles (25 roles, 5 groups) ---

ROLES = [
    # Web Layer
    ("route_handler", "Flask blueprint route functions handling HTTP requests", "web_layer"),
    ("report_generator", "Analytics dashboards and Excel export routes", "web_layer"),
    ("document_manager", "Contract document hierarchy CRUD routes", "web_layer"),
    # Validation Pipeline
    ("validation_gate", "Sequential invoice validation gates returning GateResult", "validation_pipeline"),
    ("validation_orchestrator", "Runs gates in sequence and aggregates results", "validation_pipeline"),
    ("batch_validator", "Concurrent multi-invoice validation with caching", "validation_pipeline"),
    ("action_router", "Maps validation failures to action queue items", "validation_pipeline"),
    ("content_generator", "Text generation for dispute emails and tickets", "validation_pipeline"),
    # Intelligence Layer
    ("confidence_engine", "State machine for contract element confidence lifecycle", "intelligence_layer"),
    ("anomaly_detector", "Drift detection between paid data and contract terms", "intelligence_layer"),
    ("pattern_learner", "Discovers new contract terms from paid invoice patterns", "intelligence_layer"),
    ("circuit_breaker", "Contradiction spike detection to prevent feedback loops", "intelligence_layer"),
    ("exit_interviewer", "PRO resolution capture and pattern logging", "intelligence_layer"),
    # Data Layer
    ("ingestion_orchestrator", "Full CSV/XML ingestion pipeline orchestration", "data_layer"),
    ("data_parser", "XML/CSV parsing and format conversion", "data_layer"),
    ("data_model", "SQLite schema definitions and migrations", "data_layer"),
    ("lifecycle_tracker", "Invoice status transition detection and logging", "data_layer"),
    ("entity_matcher", "Carrier identity detection via fuzzy matching", "data_layer"),
    ("address_normalizer", "Bill-to normalization and fuzzy matching", "data_layer"),
    # Infrastructure
    ("pipeline_orchestrator", "Daily execution sequence coordinator", "infrastructure"),
    ("data_guardian", "Backup and integrity verification", "infrastructure"),
    ("email_processor", "PST import and email-to-invoice matching", "infrastructure"),
    ("configuration", "Centralized settings and constants", "infrastructure"),
    ("audit_logger", "Append-only event logging", "infrastructure"),
    ("utility", "Generic helpers with no domain logic", "infrastructure"),
]

# --- Scoring Weights ---

SCORING_WEIGHTS = {
    "route_handler": {
        "volatility": 0.20, "coverage": 0.30, "complexity": 0.25,
        "coupling": 0.15, "staleness": 0.10,
    },
    "validation_gate": {
        "volatility": 0.15, "coverage": 0.35, "complexity": 0.10,
        "coupling": 0.15, "staleness": 0.25,
    },
    "confidence_engine": {
        "volatility": 0.20, "coverage": 0.25, "complexity": 0.15,
        "coupling": 0.20, "staleness": 0.20,
    },
    "data_model": {
        "volatility": 0.30, "coverage": 0.20, "complexity": 0.10,
        "coupling": 0.25, "staleness": 0.15,
    },
    "utility": {
        "volatility": 0.20, "coverage": 0.20, "complexity": 0.30,
        "coupling": 0.15, "staleness": 0.15,
    },
    "ingestion_orchestrator": {
        "volatility": 0.20, "coverage": 0.25, "complexity": 0.20,
        "coupling": 0.20, "staleness": 0.15,
    },
    "action_router": {
        "volatility": 0.20, "coverage": 0.30, "complexity": 0.20,
        "coupling": 0.15, "staleness": 0.15,
    },
    "report_generator": {
        "volatility": 0.15, "coverage": 0.20, "complexity": 0.25,
        "coupling": 0.15, "staleness": 0.25,
    },
}

# --- Role Thresholds ---

ROLE_THRESHOLDS = {
    "route_handler": {
        "complexity_threshold": 0.60,
        "coupling_hotspot_threshold": 0.80,
    },
    "validation_gate": {
        "complexity_threshold": 0.95,
        "coupling_hotspot_threshold": 0.80,
    },
    "confidence_engine": {
        "complexity_threshold": 0.85,
        "coupling_hotspot_threshold": 0.70,
    },
    "data_model": {
        "complexity_threshold": 0.90,
        "coupling_hotspot_threshold": 0.90,
    },
    "utility": {
        "complexity_threshold": 0.50,
        "coupling_hotspot_threshold": 0.80,
    },
}

# --- Best Practices ---

BEST_PRACTICES = [
    # route_handler
    ("route_handler", "single_responsibility",
     "Each route function handles one concern without multi-step orchestration inline",
     "Function length > 80 lines or multiple DB write operations in one route",
     "curated", "medium"),
    ("route_handler", "input_validation_at_boundary",
     "All form/query params validated before DB operations with type coercion",
     "Missing type coercion on request.form values; raw request.form[] access",
     "curated", "high"),
    ("route_handler", "consistent_error_handling",
     "Flash messages for user errors, proper HTTP status codes, no bare except clauses",
     "Bare except: blocks; missing flash() on validation failure; 200 status on error",
     "curated", "medium"),
    # confidence_engine
    ("confidence_engine", "immutable_state_transitions",
     "All state transitions go through ALLOWED_TRANSITIONS check; no direct state assignment",
     "State column UPDATE without calling transition validation function",
     "curated", "high"),
    ("confidence_engine", "append_only_audit",
     "Every state change writes to confidence_log; no updates or deletes on log table",
     "UPDATE or DELETE on confidence_log table; missing log entry after state change",
     "curated", "high"),
    ("confidence_engine", "threshold_gated_automation",
     "Automated actions require minimum invoice count threshold before triggering",
     "Automation logic without checking min_invoices or sample_size threshold",
     "curated", "high"),
    # validation_gate
    ("validation_gate", "structured_return_type",
     "Every gate returns a GateResult dataclass with pass/fail, reason, and enrichment data",
     "Functions returning bool, tuple, or dict instead of GateResult",
     "curated", "high"),
    ("validation_gate", "error_accumulation",
     "Gates collect all failures within scope rather than short-circuiting on first error",
     "Early return on first failure within a single gate function",
     "curated", "medium"),
    ("validation_gate", "deterministic_output",
     "Same inputs produce same GateResult; no external API calls or datetime in comparisons",
     "External HTTP calls; datetime.now() used in value comparison; random module usage",
     "curated", "medium"),
    # utility
    ("utility", "pure_functions",
     "No side effects, no DB access, no file I/O; pure data transformation only",
     "Functions with conn parameter; file open() calls; global state mutation",
     "curated", "medium"),
    ("utility", "explicit_null_handling",
     "Return typed defaults rather than None; document nullable return values with type hints",
     "Bare return None without Optional type hint; undocumented None returns",
     "curated", "low"),
    ("utility", "no_domain_logic",
     "Helpers should be domain-agnostic; domain-specific logic belongs in its role module",
     "References to invoice, contract, carrier, or validation in utility functions",
     "curated", "medium"),
    # data_model
    ("data_model", "idempotent_schema",
     "All CREATE TABLE use IF NOT EXISTS; ALTER TABLE wrapped in try/except",
     "Missing IF NOT EXISTS; bare ALTER TABLE without error handling",
     "curated", "high"),
    ("data_model", "foreign_key_enforcement",
     "All cross-table references use REFERENCES with explicit ON DELETE policy",
     "Integer columns referencing other tables without FK constraint",
     "curated", "medium"),
    ("data_model", "migration_isolation",
     "Each migration in its own function with clear naming (_migrate_X_schema)",
     "Multiple unrelated ALTER TABLE in one function; unnamed migration logic",
     "curated", "medium"),
]

# --- Content-based checks (regex on chunk content) ---

CONTENT_CHECKS = {
    "consistent_error_handling": [
        {"pattern": re.compile(r"except\s*:"),
         "message": "Bare except clause found"},
    ],
    "input_validation_at_boundary": [
        {"pattern": re.compile(r"request\.form\["),
         "message": "Raw request.form[] access without .get()"},
    ],
    "pure_functions": [
        {"pattern": re.compile(r"\bconn\b"),
         "message": "Database connection parameter found in utility function"},
        {"pattern": re.compile(r"\bopen\s*\("),
         "message": "File I/O found in utility function"},
    ],
    "no_domain_logic": [
        {"pattern": re.compile(r"(?:^|[\s_.])(invoice|contract|carrier|validation)(?:[\s_.]|$)",
                               re.IGNORECASE | re.MULTILINE),
         "message": "Domain-specific term found in utility function"},
    ],
    "deterministic_output": [
        {"pattern": re.compile(r"datetime\.now\(\)"),
         "message": "datetime.now() used in gate function"},
        {"pattern": re.compile(r"\brequests\."),
         "message": "External HTTP call found in gate function"},
    ],
    "idempotent_schema": [
        {"pattern": re.compile(r"CREATE\s+TABLE\s+(?!IF\s+NOT\s+EXISTS)", re.IGNORECASE),
         "message": "CREATE TABLE without IF NOT EXISTS"},
    ],
    "append_only_audit": [
        {"pattern": re.compile(r"\bUPDATE\b.*\bconfidence_log\b|\bDELETE\b.*\bconfidence_log\b",
                               re.IGNORECASE),
         "message": "UPDATE or DELETE on confidence_log table"},
    ],
    "structured_return_type": [
        {"pattern": re.compile(r"\breturn\s+(True|False)\b"),
         "message": "Returns raw boolean instead of GateResult"},
    ],
}

# --- Structural metadata checks ---

STRUCTURAL_CHECKS = {
    "single_responsibility": [
        {"field": "line_count", "threshold": 80, "direction": "max",
         "message": "Function has {value} lines (threshold: 80)"},
    ],
}

# --- Register ---

flask_service = ArchetypeDefinition(
    name="flask_service",
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

register_archetype(flask_service)
