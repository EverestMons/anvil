"""
Anvil best practice detection engine.

Checks whether code chunks comply with best practices using three modes:
content regex matching, structural metadata thresholds, and combined checks.
"""
from __future__ import annotations

import json
import re


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
        {"pattern": re.compile(r"\b(invoice|contract|carrier|validation)\b", re.IGNORECASE),
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


def check_best_practice(chunk: dict, practice: dict) -> dict:
    """
    Check if a chunk complies with a best practice.

    Returns {"compliant": bool, "observation": str}.
    Observation is empty string if compliant, descriptive if not.
    """
    pattern_name = practice.get("pattern_name", "")
    content = chunk.get("content", "")
    metadata_json = chunk.get("structural_metadata")

    # Mode 1: Content regex checks
    content_checks = CONTENT_CHECKS.get(pattern_name, [])
    for check in content_checks:
        match = check["pattern"].search(content)
        if match:
            return {
                "compliant": False,
                "observation": check["message"],
            }

    # Mode 2: Structural metadata threshold checks
    structural_checks = STRUCTURAL_CHECKS.get(pattern_name, [])
    if structural_checks and metadata_json:
        try:
            meta = json.loads(metadata_json)
        except (json.JSONDecodeError, TypeError):
            meta = {}

        for check in structural_checks:
            value = meta.get(check["field"])
            if value is not None:
                direction = check.get("direction", "max")
                threshold = check["threshold"]
                violated = (
                    (direction == "max" and value > threshold) or
                    (direction == "min" and value < threshold)
                )
                if violated:
                    msg = check["message"].format(value=value)
                    return {"compliant": False, "observation": msg}

    # No violations found (or no automated check available)
    return {"compliant": True, "observation": ""}
