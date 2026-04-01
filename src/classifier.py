"""
Anvil heuristic functional role classifier.

Classifies code chunks into functional roles using a priority-ordered
rule chain: decorator patterns > naming conventions > file path patterns > fallback.
"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Optional

from src import db


# --- Classification Rules (priority order) ---

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

# More specific rules first, catch-all patterns last
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


def classify_chunk(chunk_dict: dict) -> Optional[str]:
    """
    Classify a single chunk into a functional role.

    Uses priority-ordered rules: chunk_type > decorators > naming > file path > fallback.
    Returns functional role name string, or None for module/test_case chunks.
    """
    chunk_type = chunk_dict.get("chunk_type", "")
    name = chunk_dict.get("name", "")
    file_path = chunk_dict.get("file_path", "")
    content = chunk_dict.get("content", "")

    # Priority 1: chunk_type overrides
    if chunk_type in ("module", "test_case"):
        return None
    if chunk_type == "config":
        return "configuration"

    # Priority 2: Decorator patterns (first 10 lines of content)
    content_head = "\n".join(content.split("\n")[:10])
    for pattern, role in DECORATOR_RULES:
        if pattern.search(content_head):
            return role

    # Priority 3: Naming conventions
    for pattern, role in NAME_RULES:
        if pattern.search(name):
            return role

    # Priority 4: File path patterns
    for pattern, role in FILE_PATH_RULES:
        if pattern.search(file_path):
            return role

    # Priority 5: Fallback
    return "utility"


def classify_project(conn, project_name: str) -> dict:
    """
    Classify all chunks in a project. Updates code_chunks.functional_role.

    Skips module and test_case chunk_types.
    Returns {"classified": N, "unclassified": N, "role_distribution": {...}}.
    """
    project = db.get_project(conn, project_name)
    if project is None:
        raise ValueError(f"Project not found: {project_name}")

    project_id = project["id"]

    # Get all classifiable chunks (exclude module and test_case)
    conn.row_factory = db._row_to_dict
    cur = conn.execute(
        "SELECT * FROM code_chunks WHERE project_id = ? "
        "AND chunk_type NOT IN ('module', 'test_case')",
        (project_id,),
    )
    chunks = cur.fetchall()
    conn.row_factory = None

    classified = 0
    unclassified = 0
    distribution = defaultdict(int)

    for chunk in chunks:
        role = classify_chunk(chunk)
        if role:
            conn.execute(
                "UPDATE code_chunks SET functional_role = ? WHERE id = ?",
                (role, chunk["id"]),
            )
            classified += 1
            distribution[role] += 1
        else:
            unclassified += 1

    conn.commit()
    return {
        "classified": classified,
        "unclassified": unclassified,
        "role_distribution": dict(distribution),
    }
