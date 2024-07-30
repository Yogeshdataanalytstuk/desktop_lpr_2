# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all PyQt5 submodules
hiddenimports = collect_submodules('PyQt5')

# Collect data files from ultralytics
datas = collect_data_files('ultralytics', includes=['cfg/default.yaml'])

a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=datas + [
        ('saved_model/yolov8n.pt', 'saved_model'),
        ('saved_model/best.pt', 'saved_model'),
        ('saved_model/best.pth', 'saved_model'),
        ('resources/logo.gif', 'resources'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LPR',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='LPR.app',
    icon=None,
    bundle_identifier=None,
)
