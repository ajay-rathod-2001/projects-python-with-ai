"""AI Career Intelligence — Unified Single Application Runner.

This script launches the complete backend, initializes database tables,
serves the interactive desktop web application with the Robotics Robo logo,
and automatically opens the interface in your default browser.
"""

import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import webbrowser

# Ensure standard output and error are safe for all Windows console encodings
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Locate project paths supporting frozen single-file executable
if getattr(sys, "frozen", False):
    ROOT_DIR = Path(sys.executable).resolve().parent
    if hasattr(sys, "_MEIPASS"):
        bundle_dir = Path(sys._MEIPASS)
        sys.path.insert(0, str(bundle_dir / "backend"))
        sys.path.insert(0, str(bundle_dir))
else:
    ROOT_DIR = Path(__file__).resolve().parent
    BACKEND_DIR = ROOT_DIR / "backend"
    ROOT_VENV_PYTHON = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
    BACKEND_VENV_PYTHON = BACKEND_DIR / ".venv" / "Scripts" / "python.exe"

    # Detect active virtual environment in backend\.venv or root .venv
    VENV_PYTHON = None
    if BACKEND_VENV_PYTHON.exists():
        VENV_PYTHON = BACKEND_VENV_PYTHON
    elif ROOT_VENV_PYTHON.exists():
        VENV_PYTHON = ROOT_VENV_PYTHON

    # If not running inside .venv, re-execute using the virtual environment
    if VENV_PYTHON and sys.executable.lower() != str(VENV_PYTHON).lower():
        print(f"[*] Switching to virtual environment: {VENV_PYTHON}")
        try:
            sys.exit(subprocess.call([str(VENV_PYTHON), __file__] + sys.argv[1:]))
        except KeyboardInterrupt:
            sys.exit(0)

    # Add backend directory to module search path
    sys.path.insert(0, str(BACKEND_DIR))

try:
    import uvicorn
    from app.core.config import settings
    from app.database.connection import init_db
except ImportError as e:
    print(f"[!] Missing dependencies: {e}")
    print("[*] Please run 'uv pip install -r backend/requirements.txt' or use start.bat")
    sys.exit(1)


def open_browser():
    """Wait for server startup and open the browser."""
    time.sleep(1.8)
    url = f"http://{settings.HOST}:{settings.PORT}/"
    print(f"[*] Opening AI Career Intelligence at: {url}")
    webbrowser.open(url)


def print_banner():
    """Display startup banner."""
    print("=" * 65)
    print("      HIREAI -- INTELLIGENT RECRUITMENT & ASSESSMENT PLATFORM")
    print("=" * 65)
    print(f" [*] Application:   {settings.APP_NAME}")
    print(f" [*] Local Server:  http://{settings.HOST}:{settings.PORT}/")
    print(f" [*] API Docs:      http://{settings.HOST}:{settings.PORT}/docs")
    print(f" [*] Health Check:  http://{settings.HOST}:{settings.PORT}/api/v1/health")
    print(f" [*] Storage Path:  {settings.STORAGE_DIR}")
    print("=" * 65)
    print(" [OK] Initializing database...")
    init_db()
    print(" [OK] Database ready. Starting server (Press Ctrl+C to stop)...")
    print("=" * 65)


def main():
    """Main application entry point."""
    print_banner()

    # Launch browser automatically in background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Start FastAPI server
    from app.main import app as fastapi_app
    uvicorn.run(
        fastapi_app,
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
