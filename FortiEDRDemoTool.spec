# -*- mode: python ; coding: utf-8 -*-

import fortiedr
import os
from pathlib import Path
import sys

# Ensure the fortiedr api file exists
api_json_path = os.path.join(
    os.path.dirname(fortiedr.__file__), "api_parameters.json"
)

if not os.path.exists(api_json_path):
    raise FileNotFoundError(f"Missing: {api_json_path}")

# -------------------- Add tcping binary from project_root/tools --------------------
# Determine project root robustly: use current working directory (build script cds there)
project_root = Path.cwd()
tcping_src = str(project_root / "tools" / "tcping.exe")

# binaries accepts tuples (src, dest_folder_inside_runtime)
# This will place tcping.exe into the extracted runtime folder under "tools"
binaries = [
    (tcping_src, "tools"),
]
# -------------------------------------------------------------------------------

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=binaries,
    datas=[
        ('assets', 'assets'),
        ('.env', '.'),
        (api_json_path, 'fortiedr'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FortiEDRDemoTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI only
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/fortinet.ico'  # Icon
)
