"""
Anvil best practice detection engine.

Checks whether code chunks comply with best practices using three modes:
content regex matching, structural metadata thresholds, and combined checks.
"""
from __future__ import annotations

import json


def check_best_practice(chunk: dict, practice: dict,
                        content_checks: dict, structural_checks: dict) -> dict:
    """
    Check if a chunk complies with a best practice.

    Returns {"compliant": bool, "observation": str}.
    Observation is empty string if compliant, descriptive if not.
    """
    pattern_name = practice.get("pattern_name", "")
    content = chunk.get("content", "")
    metadata_json = chunk.get("structural_metadata")

    # Mode 1: Content regex checks
    checks = content_checks.get(pattern_name, [])
    for check in checks:
        match = check["pattern"].search(content)
        if match:
            return {
                "compliant": False,
                "observation": check["message"],
            }

    # Mode 2: Structural metadata threshold checks
    struct_checks = structural_checks.get(pattern_name, [])
    if struct_checks and metadata_json:
        try:
            meta = json.loads(metadata_json)
        except (json.JSONDecodeError, TypeError):
            meta = {}

        for check in struct_checks:
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
