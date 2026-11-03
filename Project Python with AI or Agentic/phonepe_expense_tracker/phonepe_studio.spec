# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Specification for PhonePe Expense Studio
Builds a standalone single-file Windows executable (.exe)
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

REPO_ROOT = Path('.').resolve()

# 1. Collect all static frontend files and sample datasets
datas = [
    (str(REPO_ROOT / 'frontend' / 'dist'), 'frontend/dist'),
    (str(REPO_ROOT / 'data' / 'transactions.txt'), 'data'),
    (str(REPO_ROOT / 'data' / 'sample_expenses_multimonth.csv'), 'data'),
    (str(REPO_ROOT / 'data' / 'sample_expenses_multimonth.xlsx'), 'data'),
    (str(REPO_ROOT / 'data' / 'phonepe.ico'), 'data'),
]

# 2. Collect webview and pythonnet data
datas += collect_data_files('webview')

# 3. Hidden imports for dynamic bridge & platform loaders
hiddenimports = [
    'clr',
    'pythonnet',
    'webview',
    'webview.platforms.winforms',
    'openpyxl',
    'openpyxl.cell._writer',
    'bottle',
    'backend',
    'backend.src.bridge.api',
    'backend.src.services.tracker',
    'backend.src.services.categorizer',
    'backend.src.models.expense',
    'backend.src.config.setting',
    'backend.src.utils.logger',
    'backend.src.utils.file_handler',
    'backend.src.utils.decoratots',
    'backend.main_desktop',
    'backend.main_cli',
]
hiddenimports += collect_submodules('webview')

a = Analysis(
    ['main.py'],
    pathex=[str(REPO_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'IPython', 'jupyter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PhonePe_Expense_Studio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Clean native Windows GUI without terminal popup
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(REPO_ROOT / 'data' / 'phonepe.ico'),
)

