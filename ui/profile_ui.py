"""Profile UI display components."""

import sys
import os
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtCore import Qt

# Ensure proper imports
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from models import UserProfile


class ProfileUI:
    """Handles profile-related UI display logic."""

    def __init__(self, content_area, content_title):
        self.content_area = content_area
        self.content_title = content_title

    def display_profile_info(self, profile: UserProfile, profile_layout, resign_id_edit, trophy_info_label):
        """Update navigation panel with profile information."""
        # Update profile info
        profile_text = f"Online ID: {profile.online_id}\n"
        if profile.region:
            profile_text += f"Region: {profile.region}\n"

        # Find and update the profile info label in the layout
        for i in range(profile_layout.count()):
            widget = profile_layout.itemAt(i).widget()
            if isinstance(widget, QLabel) and "Loading..." in widget.text():
                widget.setText(profile_text)
                break

        # Update resign ID
        if hasattr(profile, 'resign_id') and profile.resign_id:
            resign_id_edit.setText(profile.resign_id)
        else:
            resign_id_edit.setText("N/A")

        # Update trophy breakdown
        if profile.trophies:
            trophy_text = f"""🏆 Trophies
Level: {profile.trophies.level}
Total: {profile.trophies.total_count}

💎 Platinum: {profile.trophies.platinum}
🟡 Gold: {profile.trophies.gold}
⚪ Silver: {profile.trophies.silver}
🟤 Bronze: {profile.trophies.bronze}"""
            trophy_info_label.setText(trophy_text)
        else:
            trophy_info_label.setText("No trophy data available")

    def add_base64_button(self, profile: UserProfile, profile_layout, copy_callback):
        """Add base64 copy button if profile has base64 data."""
        if hasattr(profile, 'profile_base64') and profile.profile_base64:
            base64_button = QPushButton("📋 Copy Profile Base64")
            base64_button.setProperty("class", "base64-button")
            base64_button.setToolTip("Copy base64 encoded profile data to clipboard")
            base64_button.clicked.connect(lambda: copy_callback(profile.profile_base64))
            profile_layout.addWidget(base64_button)
            return base64_button
        return None

    def show_welcome_content(self, profile: UserProfile):
        """Show welcome content in main area."""
        if not profile:
            return

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        # Welcome message
        welcome = QLabel(f"Welcome back, {profile.online_id}!")
        welcome.setFont(self.content_title.font())
        welcome.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome)

        # Instructions
        instructions = QLabel("Use the buttons on the left to explore your PSN data:")
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Placeholder for future changelog/info
        changelog_placeholder = QLabel("All data is fetched fresh from PSN (no caching).")
        changelog_placeholder.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
        changelog_placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(changelog_placeholder)

        layout.addStretch()
        self.content_area.setWidget(content_widget)
