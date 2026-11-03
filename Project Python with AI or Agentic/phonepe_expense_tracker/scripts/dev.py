"""
Development Runner: Boots Vite Dev Server + PyWebView Desktop Window
"""

import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = REPO_ROOT / "frontend"


def run_dev():
    print("[DEV] Starting Vite development server on port 5173...")
    vite_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=True,
    )

    # Wait for Vite to be ready
    time.sleep(2)

    try:
        print("[DEV] Launching PhonePe Expense Studio in Desktop Window...")
        from backend.main_desktop import start_app
        start_app(dev_url="http://localhost:5173")
    finally:
        print("[DEV] Terminating Vite dev server...")
        vite_proc.terminate()


if __name__ == "__main__":
    run_dev()

