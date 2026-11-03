"""
Configuration and Environment Settings
"""

import os
import sys
from pathlib import Path
import logging

logger = logging.getLogger("PhonePeTracker")

# Determine bundle directory (for PyInstaller single-file bundle) vs repo root
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BUNDLE_DIR = Path(sys._MEIPASS)
    EXE_DIR = Path(sys.executable).parent
else:
    BUNDLE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    EXE_DIR = BUNDLE_DIR

ROOT_DIR = BUNDLE_DIR


def _load_env_file(env_path: Path) -> None:
    """Read .env file key-value pairs into environment safely."""
    try:
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip())
            logger.info("Environment variables loaded from %s", env_path)
    except Exception as e:
        logger.error("Error loading environment variables from %s: %s", env_path, e)


# Load .env if present (check EXE directory first, then BUNDLE directory)
_env_path = EXE_DIR / ".env" if (EXE_DIR / ".env").exists() else BUNDLE_DIR / ".env"
_load_env_file(_env_path)

# Settings
BUDGET_LIMIT: float = float(os.getenv("BUDGET_LIMIT", "10000.0"))
YEARLY_BUDGET_LIMIT: float = float(os.getenv("YEARLY_BUDGET_LIMIT", "120000.0"))

# Locate default data file (prefer data folder next to .exe if user provided one)
_env_data_rel = os.getenv("DATA_FILE_PATH", "data/transactions.txt")
_external_data = EXE_DIR / _env_data_rel
if _external_data.exists():
    DATA_FILE_PATH: Path = _external_data
else:
    DATA_FILE_PATH: Path = BUNDLE_DIR / _env_data_rel

# Output paths (write next to .exe in user directory)
_output_dir = EXE_DIR / "data"
try:
    _output_dir.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON_PATH: Path = _output_dir / "summary.json"
except Exception:
    _user_cache = Path.home() / ".phonepe_expense_studio"
    _user_cache.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON_PATH: Path = _user_cache / "summary.json"

_log_dir = EXE_DIR / "logs"
try:
    _log_dir.mkdir(parents=True, exist_ok=True)
    LOG_FILE_PATH: Path = _log_dir / "tracker.log"
except Exception:
    _user_cache = Path.home() / ".phonepe_expense_studio"
    _user_cache.mkdir(parents=True, exist_ok=True)
    LOG_FILE_PATH: Path = _user_cache / "tracker.log"

FRONTEND_DIST_PATH: Path = BUNDLE_DIR / "frontend" / "dist"
