"""
Custom PyInstaller hook for PySide6 to exclude X11-dependent plugins in headless environments.
"""

import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Force offscreen platform for Qt before any Qt imports
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['QT_DEBUG_PLUGINS'] = '0'

# Collect PySide6 modules but exclude problematic X11 plugins
hiddenimports = collect_submodules('PySide6')

# Remove X11-dependent modules that cause issues in headless environments
excluded_modules = [
    'PySide6.QtPlugins.platforms.xcb',
    'PySide6.QtPlugins.platforms.libqxcb',
    'PySide6.QtPlugins.xcbglintegrations',
    'xcb',
    'xcbqpa',
]

# Filter out excluded modules
hiddenimports = [mod for mod in hiddenimports if not any(excl in mod.lower() for excl in excluded_modules)]

# Collect data files but exclude X11 platform plugins
datas = collect_data_files('PySide6')

# Filter out X11 platform plugins from datas
filtered_datas = []
for src, dst in datas:
    if 'platforms/libqxcb' in src or 'xcbglintegrations' in src:
        continue  # Skip X11 plugins
    filtered_datas.append((src, dst))

datas = filtered_datas

# No binaries needed for this hook
binaries = []
