"""Tests for the daemon archetype definition."""
import re
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.classifier_registry import get_archetype, ARCHETYPES


class TestDaemonArchetypeRegistration:
    """Verify daemon archetype is registered and structurally correct."""

    def test_get_archetype_daemon_returns_definition(self):
        """get_archetype('daemon') returns the daemon ArchetypeDefinition."""
        defn = get_archetype("daemon")
        assert defn.name == "daemon"
        assert len(defn.roles) == 13
        assert len(defn.name_rules) == 33
        assert len(defn.file_path_rules) == 12
        assert len(defn.decorator_rules) == 0
        assert len(defn.scoring_weights) == 8
        assert len(defn.role_thresholds) == 6
        assert len(defn.best_practices) == 8
        assert len(defn.content_checks) == 3
        assert len(defn.structural_checks) == 1

    def test_registry_holds_both_archetypes(self):
        """Both flask_service and daemon are registered in ARCHETYPES."""
        assert "flask_service" in ARCHETYPES
        assert "daemon" in ARCHETYPES
        assert len(ARCHETYPES) >= 2

    def test_daemon_roles_are_valid_tuples(self):
        """Each role is a (name, description, group) tuple."""
        defn = get_archetype("daemon")
        for role in defn.roles:
            assert len(role) == 3, f"Role tuple has wrong length: {role}"
            name, desc, group = role
            assert isinstance(name, str) and name
            assert isinstance(desc, str) and desc
            assert isinstance(group, str) and group

    def test_all_role_names(self):
        """All 13 expected role names are present."""
        defn = get_archetype("daemon")
        role_names = {r[0] for r in defn.roles}
        expected = {
            "plan_dispatcher", "worktree_manager", "agent_lifecycle",
            "gate_checker", "verdict_handler", "plan_validator",
            "config_loader", "notifier", "cache_manager", "plan_parser",
            "data_model", "cli_script", "utility",
        }
        assert role_names == expected


class TestDaemonClassification:
    """Verify a sample daemon-pattern chunk classifies to its expected role."""

    def test_gate_function_name_classifies_to_gate_checker(self):
        """A name starting with _gate_ should match gate_checker via name rules."""
        defn = get_archetype("daemon")
        test_name = "_gate_deposit_exists"
        matched_role = None
        for pattern, role in defn.name_rules:
            if pattern.search(test_name):
                matched_role = role
                break
        assert matched_role == "gate_checker"

    def test_bellows_py_file_path_classifies_to_plan_dispatcher(self):
        """bellows.py file path should match plan_dispatcher via file_path rules."""
        defn = get_archetype("daemon")
        test_path = "bellows.py"
        matched_role = None
        for pattern, role in defn.file_path_rules:
            if pattern.search(test_path):
                matched_role = role
                break
        assert matched_role == "plan_dispatcher"

    def test_notify_function_classifies_to_notifier(self):
        """A name like notify_verdict_request should match notifier."""
        defn = get_archetype("daemon")
        test_name = "notify_verdict_request"
        matched_role = None
        for pattern, role in defn.name_rules:
            if pattern.search(test_name):
                matched_role = role
                break
        assert matched_role == "notifier"

    def test_scripts_file_path_classifies_to_cli_script(self):
        """scripts/ prefix should match cli_script via file_path rules."""
        defn = get_archetype("daemon")
        test_path = "scripts/check_backlog_freshness.py"
        matched_role = None
        for pattern, role in defn.file_path_rules:
            if pattern.search(test_path):
                matched_role = role
                break
        assert matched_role == "cli_script"
