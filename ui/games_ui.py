"""Games UI display components."""

import sys
import os
from typing import List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt

# Ensure proper imports
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from models import GameData


class GamesUI:
    """Handles games-related UI display logic."""

    def __init__(self, content_area, content_title):
        self.content_area = content_area
        self.content_title = content_title

    def display_games_list(self, games: List[GameData]):
        """Display games list."""
        self.content_title.setText("Games Library")

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        count_label = QLabel(f"Your Games ({len(games)})")
        count_label.setFont(self.content_title.font())
        layout.addWidget(count_label)

        games_text = ""
        for game in games[:20]:  # Limit display
            games_text += f"• {game.name}\n"
            if game.play_count > 0:
                games_text += f"  Plays: {game.play_count}\n"
            if game.progress and game.progress > 0:
                games_text += f"  Progress: {game.progress}%\n"
            games_text += "\n"

        games_label = QLabel(games_text.strip())
        games_label.setProperty("class", "games-info")
        games_label.setWordWrap(True)
        layout.addWidget(games_label)

        if len(games) > 20:
            more_label = QLabel(f"... and {len(games) - 20} more games")
            more_label.setStyleSheet("color: #666; font-style: italic;")
            layout.addWidget(more_label)

        layout.addStretch()
        self.content_area.setWidget(content_widget)

    def display_user_games_list(self, online_id: str, games: List[GameData], back_callback=None):
        """Display another user's games list."""
        self.content_title.setText(f"{online_id}'s Games")

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        # Back button
        if back_callback:
            back_layout = QHBoxLayout()
            back_button = QPushButton("← Back to Profile")
            back_button.setProperty("class", "back-button")
            back_button.clicked.connect(lambda: back_callback(online_id))
            back_layout.addWidget(back_button)
            back_layout.addStretch()
            layout.addLayout(back_layout)

        if not games:
            no_games_label = QLabel(
                f"This user's games library is empty or not publicly visible.\n"
                f"PSN privacy settings often hide games lists."
            )
            no_games_label.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
            no_games_label.setAlignment(Qt.AlignCenter)
            no_games_label.setWordWrap(True)
            layout.addWidget(no_games_label)
        else:
            count_label = QLabel(f"{online_id}'s Games ({len(games)})")
            count_label.setFont(self.content_title.font())
            layout.addWidget(count_label)

            games_text = ""
            for game in games[:20]:  # Limit display
                games_text += f"• {game.name}\n"
                if game.play_count > 0:
                    games_text += f"  Plays: {game.play_count}\n"
                if game.progress and game.progress > 0:
                    games_text += f"  Progress: {game.progress}%\n"
                games_text += "\n"

            games_label = QLabel(games_text.strip())
            games_label.setProperty("class", "games-info")
            games_label.setWordWrap(True)
            layout.addWidget(games_label)

            if len(games) > 20:
                more_label = QLabel(f"... and {len(games) - 20} more games")
                more_label.setStyleSheet("color: #666; font-style: italic;")
                layout.addWidget(more_label)

        layout.addStretch()
        self.content_area.setWidget(content_widget)

    def show_games_loading(self):
        """Show games loading state."""
        self.content_title.setText("Games Library")

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        loading_label = QLabel("Loading games library...")
        layout.addWidget(loading_label)

        self.content_area.setWidget(content_widget)

    def show_user_games_loading(self, online_id: str):
        """Show loading state for another user's games list."""
        self.content_title.setText(f"{online_id}'s Games")

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        loading_label = QLabel(f"Loading games library for {online_id} (if public)...")
        layout.addWidget(loading_label)

        self.content_area.setWidget(content_widget)
