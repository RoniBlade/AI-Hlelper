# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\\\Users\\\\Adam\\\\Documents\\\\Work\\\\LarbCorp\\\\NeuroCorp\\\\AI-Assistant\\\\model\\\\vosk-model-small-ru-0.22', 'model/vosk-model-small-ru-0.22'), ('C:\\\\Users\\\\Adam\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python312\\\\Lib\\\\site-packages\\\\vosk\\\\libvosk.dll', 'vosk'), ('C:\\\\Users\\\\Adam\\\\Documents\\\\Work\\\\LarbCorp\\\\NeuroCorp\\\\AI-Assistant\\\\icon.ico', '.')],
    hiddenimports=[],
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
    name='main',
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
    icon=['C:\\Users\\Adam\\Documents\\Work\\LarbCorp\\NeuroCorp\\AI-Assistant\\icon.ico'],
)
