# -*- mode: python ; coding: utf-8 -*-
import os
import mediapipe

# Get Mediapipe modules path
mediapipe_path = os.path.dirname(mediapipe.__file__)

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/config.json', 'src'),
        ('requirements.txt', '.'),
        (os.path.join(mediapipe_path, 'modules'), 'mediapipe/modules'), # Include Mediapipe models
    ],
    hiddenimports=[
        'mediapipe',
        'cv2',
        'customtkinter',
        'pyautogui',
        'packaging',
        'numpy',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
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
    name='AirGestureController',
    debug=False, # Disable debug
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Hide terminal for production
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
