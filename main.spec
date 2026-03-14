# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from vosk import __file__ as vosk_init_file


project_root = Path(SPECPATH)
model_dir = project_root / "model" / "vosk-model-small-ru-0.22"
icon_file = project_root / "assets" / "icon.ico"
vosk_dll = Path(vosk_init_file).resolve().parent / "libvosk.dll"


a = Analysis(
    ["main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(model_dir), "model/vosk-model-small-ru-0.22"),
        (str(vosk_dll), "vosk"),
        (str(icon_file), "assets"),
    ],
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
    name="AI-Assistant",
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
    icon=[str(icon_file)],
)
