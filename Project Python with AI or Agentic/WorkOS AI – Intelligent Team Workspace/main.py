#!/usr/bin/env python3
"""
WorkOS AI - Master Application Entry Point
Single command to run everything: py main.py
"""

import sys
import os
import time
import subprocess
import webbrowser

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

# Add backend to path
sys.path.insert(0, BACKEND_DIR)


def print_banner():
    print("\n" + "=" * 60)
    print("      ⚡ WorkOS AI – Intelligent Team Workspace ⚡")
    print("      AI Operating System for Teams • Master Launcher")
    print("=" * 60)


def launch_web_app():
    """Starts backend API, frontend dev server, and opens the browser."""
    print("\n[1/3] Starting FastAPI Backend on http://localhost:8000 ...")
    if os.name == "nt":
        subprocess.Popen(
            f'start "WorkOS AI - Backend" cmd /c "cd /d "{BACKEND_DIR}" && py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"',
            shell=True,
        )
    else:
        subprocess.Popen(
            ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            cwd=BACKEND_DIR,
        )

    print("[2/3] Starting React Frontend on http://localhost:5173 ...")
    if os.name == "nt":
        subprocess.Popen(
            f'start "WorkOS AI - Frontend" cmd /c "cd /d "{FRONTEND_DIR}" && npm run dev"',
            shell=True,
        )
    else:
        subprocess.Popen(["npm", "run", "dev"], cwd=FRONTEND_DIR)

    print("[3/3] Opening browser in 3 seconds...")
    time.sleep(3)
    webbrowser.open("http://localhost:5173")

    print("\n" + "=" * 60)
    print("  ✔ WorkOS AI is now LIVE!")
    print("  • Web App UI:     http://localhost:5173")
    print("  • API Docs:       http://localhost:8000/docs")
    print("  • Health Check:   http://localhost:8000/health")
    print("=" * 60 + "\n")


def launch_desktop_gui():
    """Launches the native standalone desktop GUI window."""
    print("\n[INFO] Launching Native Desktop GUI Application...")
    from app.desktop_app import main as gui_main
    gui_main()


def launch_cli():
    """Launches the interactive terminal CLI."""
    from app.cli import main as cli_main
    cli_main()


def build_standalone_exe():
    """Compiles the app into a single standalone WorkOS-AI.exe."""
    print("\n[INFO] Checking PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("[INFO] Compiling WorkOS-AI.exe (standalone single file)...")
    desktop_app_path = os.path.join(BACKEND_DIR, "app", "desktop_app.py")
    subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--clean",
        "--name", "WorkOS-AI",
        "--distpath", ROOT_DIR,
        desktop_app_path
    ])
    print("\n✔ Standalone 'WorkOS-AI.exe' generated at project root!\n")


def interactive_menu():
    print_banner()
    print("  [1] 🌐 Launch Web App (Backend + Frontend + Browser)  (Default)")
    print("  [2] 🖥️  Launch Native Desktop GUI App")
    print("  [3] 💻 Launch Terminal CLI Command Center")
    print("  [4] 📦 Build Standalone Single-File Executable (.exe)")
    print("  [5] ❌ Exit")
    print("=" * 60)

    try:
        choice = input("\nSelect an option [1-5] (Press Enter for [1]): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
        return

    if choice in ["", "1", "web"]:
        launch_web_app()
    elif choice in ["2", "desktop", "gui"]:
        launch_desktop_gui()
    elif choice in ["3", "cli"]:
        launch_cli()
    elif choice in ["4", "build", "exe"]:
        build_standalone_exe()
    elif choice in ["5", "q", "exit"]:
        print("Goodbye!")
    else:
        print("Invalid selection. Defaulting to Web App...")
        launch_web_app()


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower().strip("-")
        if arg in ["web", "w", "run"]:
            launch_web_app()
        elif arg in ["desktop", "gui", "d"]:
            launch_desktop_gui()
        elif arg in ["cli", "c"]:
            launch_cli()
        elif arg in ["build", "exe", "b"]:
            build_standalone_exe()
        else:
            print(f"Usage: py main.py [web|desktop|cli|build]")
    else:
        interactive_menu()


if __name__ == "__main__":
    main()

