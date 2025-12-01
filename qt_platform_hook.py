"""
Runtime hook for PyInstaller to set up Qt platform plugins properly.
This ensures the application works in both GUI and headless environments.
Only applies when running from a PyInstaller bundle.
"""

import os
import sys

# Only apply special Qt platform handling when running from PyInstaller bundle
if getattr(sys, 'frozen', False):
    import platform

    # Check environment
    has_display = bool(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'))
    is_ci = bool(os.environ.get('GITHUB_ACTIONS') or os.environ.get('CI'))
    is_windows = platform.system() == 'Windows'

    # Platform-specific handling
    if is_windows:
        # On Windows, let Qt use default Windows platform
        # Don't set QT_QPA_PLATFORM to avoid conflicts with Windows Qt
        pass
    elif not has_display or is_ci:
        # Only force offscreen on Linux/macOS when headless
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''
    else:
        # On Linux/macOS desktop, let Qt auto-detect
        pass

    # Set Qt debug level to reduce noise
    os.environ['QT_DEBUG_PLUGINS'] = '0'

    # Ensure proper temp directory for Qt (cross-platform)
    if not os.environ.get('XDG_RUNTIME_DIR') and not is_windows:
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

else:
    # When running from source, let Qt handle platform detection normally
    os.environ['QT_DEBUG_PLUGINS'] = '0'
