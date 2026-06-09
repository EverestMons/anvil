"""
Anvil archetype registry — ArchetypeDefinition dataclass and lookup functions.

Each archetype defines the full set of classification rules, scoring weights,
functional roles, best practices, and detection checks for a project type.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ArchetypeDefinition:
    """Complete archetype specification for a project type."""
    name: str
    roles: list[tuple[str, str, str]]
    decorator_rules: list[tuple[re.Pattern, str]]
    name_rules: list[tuple[re.Pattern, str]]
    file_path_rules: list[tuple[re.Pattern, str]]
    scoring_weights: dict[str, dict[str, float]]
    role_thresholds: dict[str, dict[str, float]]
    best_practices: list[tuple[str, str, str, str, str, str]]
    content_checks: dict[str, list[dict]]
    structural_checks: dict[str, list[dict]]


ARCHETYPES: dict[str, ArchetypeDefinition] = {}


def register_archetype(archetype: ArchetypeDefinition) -> None:
    """Register an archetype definition."""
    ARCHETYPES[archetype.name] = archetype


def get_archetype(name: str) -> ArchetypeDefinition:
    """Look up a registered archetype by name. Raises ValueError if not found."""
    if name not in ARCHETYPES:
        raise ValueError(f"Unknown archetype: {name}")
    return ARCHETYPES[name]
