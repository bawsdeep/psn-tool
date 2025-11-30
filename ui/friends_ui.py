"""Friends UI display components."""

import sys
import os
from typing import List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout
from PySide6.QtCore import Qt
from functools import partial

# Ensure proper imports
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


class FriendsUI:
    """Handles friends-related UI display logic."""

    def __init__(self, content_area, content_title, search_callback=None):
        self.content_area = content_area
        self.content_title = content_title
        self.search_callback = search_callback

    def display_friends_list(self, friends: List[str]):
        """Display friends list with clickable names."""
        self.content_title.setText("Friends List")

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        count_label = QLabel(f"Your Friends ({len(friends)})")
        count_label.setFont(self.content_title.font())
        layout.addWidget(count_label)

        # Instructions
        instructions = QLabel("Click on any friend's name to search their profile:")
        instructions.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(instructions)

        # Create clickable friend buttons
        friends_widget = QWidget()
        friends_layout = QVBoxLayout(friends_widget)

        for i, friend in enumerate(friends, 1):
            # Create a horizontal layout for each friend
            friend_layout = QHBoxLayout()

            # Friend number
            number_label = QLabel(f"{i}.")
            number_label.setFixedWidth(30)
            number_label.setStyleSheet("font-family: monospace; color: #666; font-weight: bold;")
            friend_layout.addWidget(number_label)

            # Clickable friend name button with card-like styling
            friend_button = QLabel(friend)
            friend_button.setProperty("class", "friend-button")
            friend_button.setCursor(Qt.PointingHandCursor)  # Show hand cursor on hover
            if self.search_callback:
                # Make it clickable by wrapping in a widget that handles clicks
                friend_button.mousePressEvent = lambda event, name=friend: self.search_callback(name)
            friend_layout.addWidget(friend_button)

            friend_layout.addStretch()
            friends_layout.addLayout(friend_layout)

        # Add scroll area for long friend lists
        scroll_area = QScrollArea()
        scroll_area.setWidget(friends_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(400)  # Limit height
        layout.addWidget(scroll_area)

        layout.addStretch()
        self.content_area.setWidget(content_widget)

    def display_friend_search(self, friend_name: str):
        """Display friend search interface."""
        self.content_title.setText(f"Searching: {friend_name}")

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        loading_label = QLabel(f"Searching for {friend_name}...")
        layout.addWidget(loading_label)

        self.content_area.setWidget(content_widget)

    def show_friends_loading(self):
        """Show friends loading state."""
        self.content_title.setText("Friends List")

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        loading_label = QLabel("Loading friends list...")
        layout.addWidget(loading_label)

        self.content_area.setWidget(content_widget)
