"""
Custom PyInstaller hook for PySide6 to properly handle Qt platform plugins.
This hook ensures Qt platform detection works correctly at runtime.
"""

import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Don't force platform during build - let runtime hook handle it
# This allows the executable to work on both headless and desktop systems

# Collect all PySide6 modules
hiddenimports = collect_submodules('PySide6')

# Collect all data files (including platform plugins)
# The runtime hook will handle platform selection
datas = collect_data_files('PySide6')

# No binaries needed for this hook
binaries = []
