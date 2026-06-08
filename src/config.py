"""
Anvil configuration — paths, scan targets, and tuning parameters.
"""
import os

ANVIL_ROOT = "/Users/marklehn/Developer/GitHub/anvil"

ANVIL_RUNTIME_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ANVIL_DB_PATH = os.path.join(ANVIL_ROOT, "anvil.db")

SCAN_TARGETS = {
    "invoice-pulse": "/Users/marklehn/Developer/GitHub/invoice-pulse",
    "bellows": "/Users/marklehn/Developer/GitHub/bellows",
}

EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    ".vexp",
    "target",
    ".tox",
}

EXCLUDED_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".so",
    ".dylib",
    ".db",
    ".db-shm",
    ".db-wal",
    ".pdf",
    ".docx",
    ".bak",
    ".log",
    ".ico",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
}

MINHASH_NUM_PERM = 128
MINHASH_THRESHOLD = 0.7
GIT_HISTORY_WEEKS = 4

# Scoring weights (higher score = higher risk)
SCORING_WEIGHTS = {
    "volatility": 0.25,
    "coverage": 0.25,
    "complexity": 0.20,
    "coupling": 0.15,
    "staleness": 0.15,
}

# Lab thresholds
HIGH_RISK_THRESHOLD = 0.7
COVERAGE_GAP_THRESHOLD = 0.8
COUPLING_HOTSPOT_THRESHOLD = 0.8
STALENESS_THRESHOLD = 0.8
COMPLEXITY_THRESHOLD = 0.8
COCHANGE_MIN_COUNT = 5

# Role-specific scoring weight overrides (roles not listed use SCORING_WEIGHTS)
ROLE_SCORING_WEIGHTS = {
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

# Role-specific threshold overrides (roles not listed use global thresholds)
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

# Dev log paths for provenance ingestion
DEV_LOG_PATHS = {
    "invoice-pulse": "/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/development/",
    "bellows": "/Users/marklehn/Developer/GitHub/bellows/knowledge/development/",
}
