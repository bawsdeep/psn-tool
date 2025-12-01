"""
Runtime hook for PyInstaller to set up Qt platform plugins properly.
This ensures the application works in both GUI and headless environments.
"""

import os
import sys

# Check if we're in a headless environment (no display available)
has_display = bool(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'))
is_ci = bool(os.environ.get('GITHUB_ACTIONS') or os.environ.get('CI'))

# Only force offscreen platform in truly headless environments
if not has_display or is_ci:
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    # In headless environments, disable platform plugins that require X11
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''
else:
    # On desktop systems, let Qt auto-detect the best platform
    # Don't override QT_QPA_PLATFORM if it's already set
    pass

# Ensure XDG_RUNTIME_DIR is set for Qt (needed even on desktop)
if not os.environ.get('XDG_RUNTIME_DIR'):
    # Try common locations first
    for candidate in ['/run/user/1000', '/tmp/runtime-user']:
        if os.path.exists(candidate):
            os.environ['XDG_RUNTIME_DIR'] = candidate
            break
    else:
        # Fallback to creating a temp directory
        import tempfile
        runtime_dir = tempfile.mkdtemp(prefix='qt-runtime-')
        os.environ['XDG_RUNTIME_DIR'] = runtime_dir

# Set Qt debug level to reduce noise
os.environ['QT_DEBUG_PLUGINS'] = '0'
