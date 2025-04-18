# -*- mode: python ; coding: utf-8 -*-

import fortiedr
import os

api_json_path = os.path.join(
    os.path.dirname(fortiedr.__file__), "api_parameters.json"
)

if not os.path.exists(api_json_path):
    raise FileNotFoundError(f"Missing: {api_json_path}")
    
block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('.env', '.'),
        (api_json_path, 'fortiedr'),
        ('backend/Fortinet_CA_SSL.cer', 'backend')
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
    console=False,  # False = pas de console, GUI uniquement
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/fortinet.ico'  # Icon
)
