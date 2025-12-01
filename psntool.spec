# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the project root directory (spec file location)
project_root = Path(SPECPATH)

a = Analysis(
    ['gui.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include any data files if needed
        # ('path/to/data', 'data'),
    ],
    hiddenimports=[
        # PySide6/Qt modules that might not be auto-detected
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtNetwork',
        'PySide6.QtDBus',  # Linux-specific
        # Additional Qt modules
        'PySide6.QtPrintSupport',
        'PySide6.QtOpenGL',
        # Windows-specific Qt modules
        'PySide6.QtWinExtras',  # Windows-specific functionality
        # Other potential hidden imports
        'shiboken6',
        'shiboken6.Shiboken',
        # Platform-specific imports
        'PySide6.QtWaylandClient',  # For Wayland support
        # Windows platform plugins
        'PySide6.QtPlugins.platforms.qwindows',
        # Additional Windows imports
        'win32api',
        'win32con',
        'win32gui',
    ],
    hookspath=['.'],  # Include current directory for custom hooks
    hooksconfig={},  # Let runtime hook handle platform detection
    runtime_hooks=[
        'qt_platform_hook.py',  # Custom runtime hook for Qt platform setup
    ],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'unittest',
        'pdb',
        'pydoc',
        'test',
        # Exclude Qt modules that require X11 libraries in headless environments
        'PySide6.QtQml',
        'PySide6.QtQuick',
        'PySide6.QtWebEngine',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        # Exclude X11-specific Qt platform plugins
        'PySide6.QtGui.xcbqpa',
        'PySide6.QtGui.libQt6XcbQpa',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='psntool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX disabled for compatibility
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console for debugging (change to False later)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon if available: 'icon.ico'
    # Windows-specific: ensure proper GUI app behavior
    version=None,
)