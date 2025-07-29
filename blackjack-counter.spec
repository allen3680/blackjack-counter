# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Blackjack Counter
"""

import sys
from pathlib import Path

block_cipher = None

# Get the root directory
ROOT_DIR = Path.cwd()

a = Analysis(
    ['scripts/run_app.py'],
    pathex=[str(ROOT_DIR)],
    binaries=[],
    datas=[
        # Include all YAML configuration files
        ('src/config/strategy.yaml', 'src/config'),
        ('src/config/wong_halves.yaml', 'src/config'),
        ('src/config/shortcuts.yaml', 'src/config'),
        ('src/config/deviations.yaml', 'src/config'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'yaml',
        'src',
        'src.gui',
        'src.gui.app_modern_qt',
        'src.core',
        'src.core.basic_strategy',
        'src.core.card_counter',
        'src.core.game_state',
        'src.core.hand',
        'src.config',
        'src.utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'tkinter',
        'notebook',
        'IPython',
        'jupyter',
    ],
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
    name='BlackjackCounter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file here if you have one
    version=None,  # You can add version info here
)