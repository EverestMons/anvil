"""
Anvil configuration — paths, scan targets, and tuning parameters.
"""
import os

ANVIL_ROOT = "/Users/marklehn/Developer/GitHub/anvil"

ANVIL_RUNTIME_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ANVIL_DB_PATH = os.path.join(ANVIL_ROOT, "anvil.db")

SCAN_TARGETS = {
    "invoice-pulse": {
        "path": "/Users/marklehn/Developer/GitHub/invoice-pulse",
        "language": "python",
        "archetype": "flask_service",
    },
    "bellows": {
        "path": "/Users/marklehn/Developer/GitHub/bellows",
        "language": "python",
        "archetype": "flask_service",
    },
}

EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    ".vexp",
    "target",
    ".tox",
    ".bellows-worktrees",
    ".bellows-cache",
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

# Dev log paths for provenance ingestion
DEV_LOG_PATHS = {
    "invoice-pulse": "/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/development/",
    "bellows": "/Users/marklehn/Developer/GitHub/bellows/knowledge/development/",
}
