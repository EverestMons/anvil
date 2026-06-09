"""
Tests for best practices table, purpose-aware scoring, and research hook.
"""
import json
import sqlite3

import pytest

from src.db import (
    init_db, create_project, create_chunk, create_health_score,
    create_best_practice, get_best_practices_by_role,
)
from src.scorer import compute_composite
from src.config import SCORING_WEIGHTS
from src.classifier_registry import get_archetype
from src.cycle import seed_archetype_data
from src.lab import research_best_practices

# Ensure archetypes are registered
import src.archetypes  # noqa: F401

_archetype = get_archetype("flask_service")
ROLE_SCORING_WEIGHTS = _archetype.scoring_weights
ROLE_THRESHOLDS = _archetype.role_thresholds


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    init_db(c)
    c.execute("PRAGMA foreign_keys=ON")
    # Seed roles + best practices from archetype
    seed_archetype_data(c, _archetype)
    yield c
    c.close()


# --- Best practices seeding ---

def test_best_practices_seeded(conn):
    """Verify 15 seed patterns exist across 5 roles."""
    cur = conn.execute("SELECT COUNT(*) FROM best_practices")
    assert cur.fetchone()[0] == 15


def test_best_practices_per_role(conn):
    """Verify 3 patterns per role for 5 roles."""
    cur = conn.execute(
        "SELECT functional_role, COUNT(*) FROM best_practices "
        "GROUP BY functional_role ORDER BY functional_role"
    )
    role_counts = {r[0]: r[1] for r in cur.fetchall()}
    assert role_counts == {
        "confidence_engine": 3,
        "data_model": 3,
        "route_handler": 3,
        "utility": 3,
        "validation_gate": 3,
    }


def test_get_best_practices_by_role(conn):
    practices = get_best_practices_by_role(conn, "route_handler")
    assert len(practices) == 3
    names = {p["pattern_name"] for p in practices}
    assert "single_responsibility" in names
    assert "input_validation_at_boundary" in names
    assert "consistent_error_handling" in names


def test_create_best_practice(conn):
    bp_id = create_best_practice(
        conn, "route_handler", "csrf_protection",
        "All POST routes include CSRF token validation",
        detection_hint="POST route without csrf_token check",
        source="web_research",
        severity="high",
    )
    assert bp_id is not None

    practices = get_best_practices_by_role(conn, "route_handler")
    assert len(practices) == 4  # 3 seeded + 1 new


def test_best_practices_severity_constraint(conn):
    """Severity must be low/medium/high."""
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO best_practices (functional_role, pattern_name, "
            "description, severity) VALUES (?, ?, ?, ?)",
            ("utility", "test_pattern", "test", "critical"),
        )


def test_best_practices_unique_constraint(conn):
    """Same role + pattern_name should be rejected."""
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO best_practices (functional_role, pattern_name, "
            "description) VALUES (?, ?, ?)",
            ("route_handler", "single_responsibility", "duplicate"),
        )


# --- Role-specific scoring ---

def test_role_specific_weights_differ():
    """Route handler and validation gate should produce different composites."""
    vol, cov, comp, coup, stale = 0.5, 1.0, 0.8, 0.5, 0.3

    rh_score = compute_composite(
        vol, cov, comp, coup, stale,
        ROLE_SCORING_WEIGHTS["route_handler"],
    )
    vg_score = compute_composite(
        vol, cov, comp, coup, stale,
        ROLE_SCORING_WEIGHTS["validation_gate"],
    )

    # route_handler weights complexity at 0.25, validation_gate at 0.10
    # With high complexity (0.8), route_handler should score higher
    assert rh_score != vg_score
    assert rh_score > vg_score


def test_default_weights_for_unclassified():
    """NULL role should use default SCORING_WEIGHTS."""
    vol, cov, comp, coup, stale = 0.5, 0.5, 0.5, 0.5, 0.5

    default_score = compute_composite(
        vol, cov, comp, coup, stale, SCORING_WEIGHTS,
    )
    # Role lookup falls back to SCORING_WEIGHTS for None
    fallback_weights = ROLE_SCORING_WEIGHTS.get(None, SCORING_WEIGHTS)
    fallback_score = compute_composite(
        vol, cov, comp, coup, stale, fallback_weights,
    )

    assert default_score == fallback_score


def test_all_role_weights_sum_to_one():
    """All role weight profiles must sum to 1.0."""
    for role, weights in ROLE_SCORING_WEIGHTS.items():
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.001, f"{role} weights sum to {total}"


def test_default_weights_sum_to_one():
    total = sum(SCORING_WEIGHTS.values())
    assert abs(total - 1.0) < 0.001


# --- Role-specific thresholds ---

def test_validation_gate_high_complexity_threshold():
    """Validation gates tolerate higher complexity."""
    vg_thresh = ROLE_THRESHOLDS["validation_gate"]["complexity_threshold"]
    rh_thresh = ROLE_THRESHOLDS["route_handler"]["complexity_threshold"]
    assert vg_thresh > rh_thresh


def test_utility_low_complexity_threshold():
    """Utilities should flag at lower complexity."""
    util_thresh = ROLE_THRESHOLDS["utility"]["complexity_threshold"]
    assert util_thresh == 0.50


def test_confidence_engine_low_coupling_threshold():
    """Confidence engine coupling is flagged earlier."""
    ce_thresh = ROLE_THRESHOLDS["confidence_engine"]["coupling_hotspot_threshold"]
    default_thresh = 0.80  # COUPLING_HOTSPOT_THRESHOLD
    assert ce_thresh < default_thresh


# --- Research hook ---

def test_research_best_practices(conn):
    result = research_best_practices(conn, "route_handler")
    assert result["role_name"] == "route_handler"
    assert "Flask blueprint" in result["role_description"]
    assert len(result["existing_practices"]) == 3
    assert "research_prompt" in result
    assert "route_handler" in result["research_prompt"]


def test_research_best_practices_unknown_role(conn):
    result = research_best_practices(conn, "nonexistent_role")
    assert "error" in result


def test_research_prompt_excludes_existing(conn):
    """Research prompt should list existing patterns to avoid duplicates."""
    result = research_best_practices(conn, "validation_gate")
    prompt = result["research_prompt"]
    assert "structured_return_type" in prompt
    assert "error_accumulation" in prompt
    assert "deterministic_output" in prompt
