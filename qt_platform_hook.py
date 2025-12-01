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

    is_windows = platform.system() == 'Windows'
    is_ci = bool(os.environ.get('GITHUB_ACTIONS') or os.environ.get('CI'))

    if is_windows:
        # On Windows, ensure Qt can find its platform plugins
        # Don't override QT_QPA_PLATFORM - let Windows Qt work naturally
        # Make sure Qt plugins are in the PATH
        if hasattr(sys, '_MEIPASS'):
            qt_plugins_path = os.path.join(sys._MEIPASS, 'PySide6', 'plugins')
            if os.path.exists(qt_plugins_path):
                current_path = os.environ.get('PATH', '')
                os.environ['PATH'] = qt_plugins_path + os.pathsep + current_path

        # Set Qt to use Windows platform explicitly (sometimes needed)
        os.environ['QT_QPA_PLATFORM'] = 'windows'
    else:
        # Non-Windows platforms
        has_display = bool(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'))

        if not has_display or is_ci:
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        # Otherwise let Qt auto-detect

    # Reduce Qt debug noise
    os.environ['QT_DEBUG_PLUGINS'] = '0'

else:
    # When running from source, let Qt handle platform detection normally
    os.environ['QT_DEBUG_PLUGINS'] = '0'
