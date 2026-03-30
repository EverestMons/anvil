"""
Anvil configuration — paths, scan targets, and tuning parameters.
"""
import os

ANVIL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ANVIL_DB_PATH = os.path.join(ANVIL_ROOT, "anvil.db")

SCAN_TARGETS = {
    "invoice-pulse": "/Users/marklehn/Desktop/GitHub/invoice-pulse",
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
