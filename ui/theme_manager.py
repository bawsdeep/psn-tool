"""Theme management utilities."""

import sys
import os
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

# Ensure proper imports
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


# Gruvbox Color Palette Constants
class GruvboxColors:
    """Gruvbox color palette for consistent theming."""

    # Dark backgrounds (darkest to lightest)
    BG0_H = "#1d2021"  # Darkest background
    BG0 = "#282828"    # Dark background
    BG1 = "#3c3836"    # Medium background
    BG2 = "#504945"    # Light background
    BG3 = "#665c54"    # Lighter background
    BG4 = "#7c6f64"    # Lightest background

    # Foregrounds (lightest to darkest)
    FG0 = "#fbf1c7"    # Lightest foreground
    FG1 = "#ebdbb2"    # Light foreground
    FG2 = "#d5c4a1"    # Medium foreground
    FG3 = "#bdae93"    # Dark foreground
    FG4 = "#a89984"    # Darker foreground

    # Accent colors
    RED = "#cc241d"
    GREEN = "#98971a"
    YELLOW = "#d79921"
    BLUE = "#458588"
    PURPLE = "#b16286"
    AQUA = "#689d6a"
    ORANGE = "#d65d0e"

    # Gray
    GRAY = "#928374"


class ThemeManager:
    """Handles theme application and management."""

    @staticmethod
    def apply_theme(app):
        """Apply theme based on user preference or best available defaults."""
        from utils.database import get_setting

        # Check for stored theme preference
        theme = get_setting("theme") or "default"

        if theme == "gruvbox":
            # Apply Gruvbox theme - try Fusion base first
            try:
                app.setStyle("Fusion")
                ThemeManager._apply_gruvbox_theme(app)
            except Exception as e:
                ThemeManager._apply_custom_palette(app)

        elif theme == "dark":
            # Apply custom dark theme
            ThemeManager._apply_custom_palette(app)

        else:  # default - Fusion + Gruvbox
            # Try styles in order of preference
            preferred_styles = ["Fusion", "Breeze", "Cleanlooks", "Plastique", "Windows", "Macintosh"]

            applied_style = None
            for style_name in preferred_styles:
                try:
                    app.setStyle(style_name)
                    applied_style = style_name
                    break
                except Exception as e:
                    continue

            # Try to apply Gruvbox theme on top of the working base style
            if applied_style:
                try:
                    ThemeManager._apply_gruvbox_theme(app)
                    return
                except Exception as e:
                    # Continue to custom fallback
                    pass

            # If no style worked or Gruvbox failed, apply a custom palette as ultimate fallback
            if not applied_style:
                ThemeManager._apply_custom_palette(app)

    @staticmethod
    def apply_theme_from_setting(app):
        """Apply theme based on stored setting."""
        from utils.database import get_setting
        theme = get_setting("theme") or "default"

        if theme == "gruvbox":
            # Apply Gruvbox theme
            ThemeManager._apply_gruvbox_theme(app)
        elif theme == "dark":
            # Apply custom dark theme
            ThemeManager._apply_custom_palette(app)
        else:  # default
            # Try to apply Fusion + Gruvbox overlay
            try:
                app.setStyle("Fusion")
                ThemeManager._apply_gruvbox_theme(app)
            except Exception as e:
                print(f"⚠️  Could not apply default theme: {e}")
                ThemeManager._apply_custom_palette(app)

    @staticmethod
    def _apply_gruvbox_theme(app):
        """Apply the popular Gruvbox color scheme."""
        from PySide6.QtGui import QPalette, QColor
        from PySide6.QtCore import Qt

        palette = QPalette()

        # Use Gruvbox color constants
        bg0_h = QColor(GruvboxColors.BG0_H)
        bg0 = QColor(GruvboxColors.BG0)
        bg1 = QColor(GruvboxColors.BG1)
        bg2 = QColor(GruvboxColors.BG2)

        fg0 = QColor(GruvboxColors.FG0)
        fg1 = QColor(GruvboxColors.FG1)
        fg2 = QColor(GruvboxColors.FG2)

        blue = QColor(GruvboxColors.BLUE)
        purple = QColor(GruvboxColors.PURPLE)
        gray = QColor(GruvboxColors.GRAY)

        # Set palette colors using Gruvbox scheme with improved contrast
        palette.setColor(QPalette.Window, bg0_h)      # Main window background
        palette.setColor(QPalette.WindowText, fg1)    # Main window text
        palette.setColor(QPalette.Base, bg0)          # Input field backgrounds
        palette.setColor(QPalette.AlternateBase, bg1) # Alternate backgrounds
        palette.setColor(QPalette.Text, fg1)          # Input field text
        palette.setColor(QPalette.BrightText, fg0)    # Bright text for highlights
        palette.setColor(QPalette.Highlight, blue)    # Selection background
        palette.setColor(QPalette.HighlightedText, bg0_h) # Selected text
        palette.setColor(QPalette.Button, bg1)        # Button backgrounds
        palette.setColor(QPalette.ButtonText, fg1)    # Button text
        palette.setColor(QPalette.Link, blue)         # Links
        palette.setColor(QPalette.LinkVisited, purple) # Visited links

        # ToolTip colors
        palette.setColor(QPalette.ToolTipBase, bg2)
        palette.setColor(QPalette.ToolTipText, fg2)

        # Set disabled colors (muted versions)
        palette.setColor(QPalette.Disabled, QPalette.WindowText, gray)
        palette.setColor(QPalette.Disabled, QPalette.Text, gray)
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, gray)

        app.setPalette(palette)

        # Apply stylesheet using constants
        app.setStyleSheet(ThemeManager._build_gruvbox_stylesheet())

    @staticmethod
    def _build_gruvbox_stylesheet():
        """Build the Gruvbox stylesheet using constants."""
        return f"""
        /* Gruvbox stylesheet */
        QMainWindow {{
            background-color: {GruvboxColors.BG0};
        }}

        QPushButton {{
            background-color: {GruvboxColors.BG2};
            color: {GruvboxColors.FG1};
            border: 1px solid {GruvboxColors.BG4};
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}

        QPushButton[class="friend-button"] {{
            background-color: {GruvboxColors.BG2};
            color: {GruvboxColors.FG1};
            border: 1px solid {GruvboxColors.BG4};
            border-radius: 6px;
            text-align: left;
            padding: 8px 12px;
            font-size: 14px;
            font-weight: 500;
            min-width: 150px;
        }}

        QPushButton[class="base64-button"] {{
            background-color: {GruvboxColors.BG2};
            color: {GruvboxColors.FG1};
            border: 1px solid {GruvboxColors.BG4};
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
        }}

        QLabel[class="trophy-info"] {{
            background-color: {GruvboxColors.BG0_H};
            border: 1px solid {GruvboxColors.BG3};
            border-radius: 4px;
            padding: 8px;
            color: {GruvboxColors.FG1};
            margin-top: 5px;
        }}

        QLineEdit {{
            background-color: {GruvboxColors.BG0_H};
            color: {GruvboxColors.FG1};
            border: 1px solid {GruvboxColors.BG3};
            border-radius: 4px;
            padding: 4px;
            selection-background-color: {GruvboxColors.BLUE};
        }}

        QLineEdit[class="resign-id-field"] {{
            background-color: {GruvboxColors.BG0_H};
            color: {GruvboxColors.FG1};
            border: 1px solid {GruvboxColors.BG3};
            border-radius: 3px;
            padding: 2px;
            font-family: monospace;
            font-size: 11px;
            selection-background-color: {GruvboxColors.BLUE};
        }}

        QLineEdit[class="search-input"] {{
            background-color: {GruvboxColors.BG1};
            color: {GruvboxColors.FG1};
            border: 2px solid {GruvboxColors.BG3};
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 14px;
            font-weight: 500;
            selection-background-color: {GruvboxColors.AQUA};
            min-height: 20px;
        }}

        QLineEdit[class="search-input"]:focus {{
            border: 2px solid {GruvboxColors.AQUA};
            background-color: {GruvboxColors.BG0};
        }}

        QLineEdit[class="search-input"]:hover {{
            border: 2px solid {GruvboxColors.BG4};
        }}

        QLabel[class="games-info"] {{
            background-color: {GruvboxColors.BG0_H};
            border: 1px solid {GruvboxColors.BG3};
            border-radius: 5px;
            padding: 10px;
            color: {GruvboxColors.FG1};
            font-family: monospace;
        }}

        QFrame[class="search-section"] {{
            background-color: {GruvboxColors.BG1};
            border: 1px solid {GruvboxColors.BG4};
            border-radius: 8px;
        }}

        QPushButton[class="search-button"] {{
            background-color: {GruvboxColors.BG2};
            color: {GruvboxColors.FG1};
            border: 1px solid {GruvboxColors.BG4};
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}

        QPushButton[class="search-button"]:hover {{
            background-color: {GruvboxColors.BG3};
        }}

        QPushButton[class="search-button"]:pressed {{
            background-color: {GruvboxColors.BG1};
        }}

        QProgressBar {{
            background-color: {GruvboxColors.BG0_H};
            border: 1px solid {GruvboxColors.BG3};
            border-radius: 6px;
            text-align: center;
            color: {GruvboxColors.FG1};
            font-weight: bold;
            height: 22px;
        }}

        QProgressBar::chunk {{
            background-color: {GruvboxColors.BG2};
            border-radius: 5px;
            margin: 1px;
        }}
        """

    @staticmethod
    def _apply_custom_palette(app):
        """Apply a custom color palette when no system themes are available."""
        from PySide6.QtGui import QPalette, QColor
        from PySide6.QtCore import Qt

        palette = QPalette()

        # Base colors - modern dark theme
        window_color = QColor(53, 53, 53)
        window_text_color = QColor(255, 255, 255)
        base_color = QColor(25, 25, 25)
        alternate_base_color = QColor(53, 53, 53)
        text_color = QColor(255, 255, 255)
        bright_text_color = QColor(255, 255, 255)
        highlight_color = QColor(42, 130, 218)
        highlighted_text_color = QColor(255, 255, 255)
        button_color = QColor(53, 53, 53)
        button_text_color = QColor(255, 255, 255)
        link_color = QColor(42, 130, 218)
        link_visited_color = QColor(255, 0, 255)

        # Set palette colors
        palette.setColor(QPalette.Window, window_color)
        palette.setColor(QPalette.WindowText, window_text_color)
        palette.setColor(QPalette.Base, base_color)
        palette.setColor(QPalette.AlternateBase, alternate_base_color)
        palette.setColor(QPalette.Text, text_color)
        palette.setColor(QPalette.BrightText, bright_text_color)
        palette.setColor(QPalette.Highlight, highlight_color)
        palette.setColor(QPalette.HighlightedText, highlighted_text_color)
        palette.setColor(QPalette.Button, button_color)
        palette.setColor(QPalette.ButtonText, button_text_color)
        palette.setColor(QPalette.Link, link_color)
        palette.setColor(QPalette.LinkVisited, link_visited_color)

        # Set disabled colors (slightly dimmed)
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(128, 128, 128))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(128, 128, 128))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(128, 128, 128))

        app.setPalette(palette)

        # Also set some application-wide stylesheet for better consistency
        app.setStyleSheet("""
            /* Modern dark theme stylesheet */
            QMainWindow {
                background-color: #353535;
                color: #ffffff;
            }

            QWidget {
                background-color: #353535;
                color: #ffffff;
            }

            QPushButton {
                background-color: #2a82da;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #3a92ea;
            }

            QPushButton:pressed {
                background-color: #1a72ca;
            }

            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }

            QLineEdit, QTextEdit {
                background-color: #191919;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }

            QLineEdit:focus, QTextEdit:focus {
                border-color: #2a82da;
            }

            QLineEdit[class="search-input"] {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
                font-weight: 500;
                min-height: 20px;
            }

            QLineEdit[class="search-input"]:focus {
                border: 2px solid #689d6a;
                background-color: #191919;
            }

            QLineEdit[class="search-input"]:hover {
                border: 2px solid #666666;
            }

            QFrame[class="search-section"] {
                background-color: #2a2a2a;
                border: 1px solid #666666;
                border-radius: 8px;
            }

            QPushButton[class="search-button"] {
                background-color: #555555;
                color: #ffffff;
                border: 1px solid #666666;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }

            QPushButton[class="search-button"]:hover {
                background-color: #666666;
            }

            QPushButton[class="search-button"]:pressed {
                background-color: #444444;
            }

            QLabel {
                color: #ffffff;
            }

            QFrame {
                border: 1px solid #555555;
                border-radius: 4px;
            }

            QScrollArea {
                border: none;
            }

            QProgressBar {
                background-color: #191919;
                border: 1px solid #555555;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                height: 22px;
            }

            QProgressBar::chunk {
                background-color: #555555;
                border-radius: 5px;
                margin: 1px;
            }
        """)
