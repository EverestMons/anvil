"""
Anvil heuristic functional role classifier.

Classifies code chunks into functional roles using a priority-ordered
rule chain: decorator patterns > naming conventions > file path patterns > fallback.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Optional

from src import db
from src.classifier_registry import ArchetypeDefinition, get_archetype
from src.config import SCAN_TARGETS

# Ensure archetypes are registered
import src.archetypes  # noqa: F401


def classify_chunk(chunk_dict: dict, archetype: ArchetypeDefinition) -> Optional[str]:
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
    for pattern, role in archetype.decorator_rules:
        if pattern.search(content_head):
            return role

    # Priority 3: Naming conventions
    for pattern, role in archetype.name_rules:
        if pattern.search(name):
            return role

    # Priority 4: File path patterns
    for pattern, role in archetype.file_path_rules:
        if pattern.search(file_path):
            return role

    # Priority 5: Fallback
    return "utility"


def classify_project(conn, project_name: str) -> dict:
    """
    Classify all chunks in a project. Updates code_chunks.functional_role.

    Loads archetype from SCAN_TARGETS internally.
    Skips module and test_case chunk_types.
    Returns {"classified": N, "unclassified": N, "role_distribution": {...}}.
    """
    project = db.get_project(conn, project_name)
    if project is None:
        raise ValueError(f"Project not found: {project_name}")

    project_id = project["id"]

    # Load archetype from SCAN_TARGETS
    target = SCAN_TARGETS.get(project_name, {})
    archetype_name = target.get("archetype") if isinstance(target, dict) else None
    if not archetype_name:
        raise ValueError(f"No archetype configured for project: {project_name}")
    archetype = get_archetype(archetype_name)

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
        role = classify_chunk(chunk, archetype)
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
