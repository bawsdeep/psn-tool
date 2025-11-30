"""Settings and token management UI components."""

import sys
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton, QMessageBox, QComboBox

# Ensure proper imports
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


class SettingsUI:
    """Handles settings and token management UI display logic."""

    def __init__(self, content_area, content_title, main_window):
        self.content_area = content_area
        self.content_title = content_title
        self.main_window = main_window

    def show_settings_panel(self, token_cog):
        """Show settings panel."""
        self.content_title.setText("Settings")

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        settings_label = QLabel("Settings & Configuration")
        settings_label.setFont(self.content_title.font())
        layout.addWidget(settings_label)

        # Token management
        layout.addWidget(self._create_token_management_section(token_cog))

        # Cache management
        layout.addWidget(self._create_cache_management_section(token_cog))

        # Theme selection
        layout.addWidget(self._create_theme_section())

        layout.addStretch()
        self.content_area.setWidget(content_widget)

    def _create_token_management_section(self, token_cog):
        """Create token management section."""
        token_group = QFrame()
        token_group.setFrameStyle(QFrame.Box)
        token_layout = QVBoxLayout(token_group)

        token_title = QLabel("NPSSO Token Management")
        token_title.setFont(self.content_title.font())
        token_layout.addWidget(token_title)

        # Token management buttons
        button_layout = QHBoxLayout()

        change_token_button = QPushButton("Change Token")
        change_token_button.clicked.connect(self._handle_change_token)
        change_token_button.setToolTip("Update your NPSSO token")
        button_layout.addWidget(change_token_button)

        delete_token_button = QPushButton("Delete Token")
        delete_token_button.clicked.connect(lambda: self._handle_delete_token(token_cog))
        delete_token_button.setToolTip("Remove stored NPSSO token and sign out")
        delete_token_button.setStyleSheet("QPushButton { color: #d9534f; }")  # Red text for delete action
        button_layout.addWidget(delete_token_button)

        token_layout.addLayout(button_layout)
        return token_group

    def _create_cache_management_section(self, token_cog):
        """Create cache management section."""
        cache_group = QFrame()
        cache_group.setFrameStyle(QFrame.Box)
        cache_layout = QVBoxLayout(cache_group)

        cache_title = QLabel("Cache Management")
        cache_title.setFont(self.content_title.font())
        cache_layout.addWidget(cache_title)

        clear_cache_button = QPushButton("Clear Cached Data")
        clear_cache_button.clicked.connect(lambda: self._handle_clear_cache(token_cog))
        cache_layout.addWidget(clear_cache_button)

        return cache_group

    def _create_theme_section(self):
        """Create theme selection section."""
        theme_group = QFrame()
        theme_group.setFrameStyle(QFrame.Box)
        theme_layout = QVBoxLayout(theme_group)

        theme_title = QLabel("Theme Selection")
        theme_title.setFont(self.content_title.font())
        theme_layout.addWidget(theme_title)

        theme_layout.addWidget(QLabel("Choose your preferred theme:"))

        # Theme selection dropdown
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Default (Fusion + Gruvbox)", "default")
        self.theme_combo.addItem("Classic Dark", "dark")
        self.theme_combo.addItem("Gruvbox (Recommended)", "gruvbox")

        # Load current theme setting
        from utils.database import get_setting
        current_theme = get_setting("theme") or "default"
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        self.theme_combo.currentTextChanged.connect(self._handle_theme_changed)
        theme_layout.addWidget(self.theme_combo)

        return theme_group

    def _handle_change_token(self):
        """Handle change token button click."""
        reply = QMessageBox.question(
            self.main_window, "Change Token",
            "Are you sure you want to change your NPSSO token?\n"
            "You'll need to enter a new one.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.main_window.show_npsso_dialog()

    def _handle_delete_token(self, token_cog):
        """Handle delete token button click."""
        reply = QMessageBox.question(
            self.main_window, "Delete Token",
            "Are you sure you want to delete your stored NPSSO token?\n\n"
            "This will:\n"
            "• Remove your authentication\n"
            "• Clear all cached data\n"
            "• Require re-authentication for all features\n\n"
            "You can re-authenticate at any time.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # Default to No for safety
        )

        if reply == QMessageBox.Yes:
            if token_cog.delete_token():
                QMessageBox.information(
                    self.main_window, "Token Deleted",
                    "Your NPSSO token has been deleted.\n"
                    "The application will restart to apply changes."
                )
                self.main_window.restart_application()
            else:
                QMessageBox.critical(
                    self.main_window, "Error",
                    "Failed to delete token."
                )

    def _handle_clear_cache(self, token_cog):
        """Handle clear cache button click."""
        token_cog.clear_cache()
        QMessageBox.information(self.main_window, "Cache Cleared",
                              "All cached data has been cleared.")

    def _handle_theme_changed(self, theme_name):
        """Handle theme selection change."""
        theme_value = self.theme_combo.currentData()
        from utils.database import set_setting
        set_setting("theme", theme_value)

        # Apply the theme immediately
        self.main_window.apply_theme_from_setting()

        QMessageBox.information(self.main_window, "Theme Changed",
                              f"Theme changed to: {theme_name}\n\n"
                              "The theme will be applied immediately.")
