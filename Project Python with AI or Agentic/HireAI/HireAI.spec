# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import sys

block_cipher = None
project_root = Path.cwd()

added_files = [
    (str(project_root / 'backend' / 'app' / 'static'), 'app/static'),
    (str(project_root / 'backend' / 'app' / 'static'), 'backend/app/static'),
    (str(project_root / 'backend' / 'app'), 'app'),
]

hidden_imports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespans',
    'uvicorn.lifespans.auto',
    'fastapi',
    'starlette',
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'pydantic',
    'pydantic_settings',
    'fitz',
    'docx',
    'striprtf',
    'chardet',
    'reportlab',
    'app',
    'app.main',
    'app.api',
    'app.api.v1',
    'app.api.v1.resume_routes',
    'app.api.v1.job_routes',
    'app.api.v1.matching_routes',
    'app.api.v1.recommendation_routes',
    'app.api.v1.report_routes',
    'app.api.v1.assessment_routes',
    'app.api.v1.interview_routes',
    'app.api.v1.auth_routes',
    'app.models',
    'app.models.resume',
    'app.models.job',
    'app.models.match',
    'app.models.recommendation',
    'app.models.history',
    'app.models.settings',
    'app.models.assessment',
    'app.models.interview',
    'app.models.auth',
    'app.workers',
    'app.workers.code_runner',
    'app.interview',
    'app.interview.copilot',
    'app.assessment',
    'app.assessment.service',
]

a = Analysis(
    ['run.py'],
    pathex=[str(project_root), str(project_root / 'backend')],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'transformers', 'spacy', 'onnxruntime', 'scipy', 'sympy', 'narwhals', 'matplotlib'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HireAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / 'backend' / 'app' / 'static' / 'robotics_resume_robo.jpg') if (project_root / 'backend' / 'app' / 'static' / 'robotics_resume_robo.jpg').exists() else None,
)

