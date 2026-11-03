"""
Automated One-Click Build Script for PhonePe Expense Studio Standalone Executable (.exe)
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def build_executable():
    print("=" * 60)
    print("🚀 BUILDING PHONEPE EXPENSE STUDIO STANDALONE EXECUTABLE (.EXE)")
    print("=" * 60)

    # 1. Generate multi-resolution Windows Icon (.ico)
    print("\n[Step 1/3] Generating PhonePe application icon...")
    icon_script = REPO_ROOT / "scripts" / "create_icon.py"
    subprocess.run([sys.executable, str(icon_script)], check=True)

    # 2. Build React production bundle
    print("\n[Step 2/3] Compiling React 19 + Vite frontend bundle...")
    frontend_dir = REPO_ROOT / "frontend"
    subprocess.run(["npm", "run", "build"], cwd=str(frontend_dir), shell=True, check=True)

    # 3. Package with PyInstaller
    print("\n[Step 3/3] Packaging standalone single-file .exe with PyInstaller...")
    spec_file = REPO_ROOT / "phonepe_studio.spec"
    subprocess.run([
        sys.executable, "-m", "PyInstaller", str(spec_file), "--clean", "-y"
    ], check=True)

    dist_exe = REPO_ROOT / "dist" / "PhonePe_Expense_Studio.exe"
    if dist_exe.exists():
        size_mb = dist_exe.stat().st_size / (1024 * 1024)
        print("\n" + "=" * 60)
        print(f"✅ BUILD SUCCEEDED!")
        print(f"📦 Executable: {dist_exe.resolve()}")
        print(f"📊 File Size : {size_mb:.2f} MB")
        print("🎉 Ready to share with anyone as a single, standalone .exe file!")
        print("=" * 60)
    else:
        print("\n❌ Error: Executable was not found in dist/")

if __name__ == "__main__":
    build_executable()

