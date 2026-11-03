"""
PhonePe Expense Studio - Main Entrypoint
"""

import sys
from pathlib import Path

# Fix Windows console UTF-8 encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main():
    if "--cli" in sys.argv or "-c" in sys.argv:
        from backend.main_cli import run_cli
        run_cli()
    else:
        from backend.main_desktop import start_app
        print("Launching PhonePe Expense Studio Desktop App...")
        start_app()


if __name__ == "__main__":
    main()
