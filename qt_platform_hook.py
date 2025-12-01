"""
Runtime hook for PyInstaller to set up Qt platform plugins properly.
This ensures the application works in both GUI and headless environments.
"""

import os
import sys

# Set Qt platform to offscreen if no display is available
if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Ensure XDG_RUNTIME_DIR is set for Qt
if not os.environ.get('XDG_RUNTIME_DIR'):
    os.environ['XDG_RUNTIME_DIR'] = '/tmp/runtime-user'

# Create the runtime directory if it doesn't exist
runtime_dir = os.environ['XDG_RUNTIME_DIR']
if not os.path.exists(runtime_dir):
    try:
        os.makedirs(runtime_dir, exist_ok=True)
    except (OSError, PermissionError):
        # Fallback to temp directory
        import tempfile
        runtime_dir = tempfile.mkdtemp(prefix='qt-runtime-')
        os.environ['XDG_RUNTIME_DIR'] = runtime_dir
