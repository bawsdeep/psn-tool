#!/usr/bin/env python3
"""PySide6 GUI for PSN Tool."""

import sys
import os
from typing import Optional

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QDialog, QMessageBox,
    QScrollArea, QFrame, QProgressBar, QSplitter, QComboBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QPixmap

from core.client import PSNClient
from models import UserProfile, GameData
import requests
import tempfile

# Import cogs for business logic
from cogs.friends_cog import FriendsCog
from cogs.games_cog import GamesCog
from cogs.search_cog import SearchCog
from cogs.profile_cog import ProfileCog
from cogs.token_cog import TokenCog

# Import UI components
from ui.friends_ui import FriendsUI
from ui.games_ui import GamesUI
from ui.search_ui import SearchUI
from ui.profile_ui import ProfileUI
from ui.settings_ui import SettingsUI
from ui.theme_manager import ThemeManager


class ImageLoader(QThread):
    """Thread for loading images from URLs."""

    finished = Signal(QPixmap)
    error = Signal(str)

    def __init__(self, url: str, size: tuple = None):
        super().__init__()
        self.url = url
        self.size = size  # (width, height) tuple

    def run(self):
        """Download and process image."""
        try:
            if not self.url:
                self.error.emit("No URL provided")
                return

            # Download image
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name

            try:
                # Load pixmap
                pixmap = QPixmap(tmp_path)

                if pixmap.isNull():
                    self.error.emit("Failed to load image")
                    return

                # Resize if needed
                if self.size:
                    pixmap = pixmap.scaled(self.size[0], self.size[1],
                                          Qt.KeepAspectRatio,
                                          Qt.SmoothTransformation)

                self.finished.emit(pixmap)

            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass

        except requests.exceptions.RequestException as e:
            self.error.emit(f"Network error: {str(e)}")
        except Exception as e:
            self.error.emit(f"Image load error: {str(e)}")


class ProfileLoaderThread(QThread):
    """Thread for loading user profile data."""

    finished = Signal(object)  # UserProfile
    error = Signal(str)
    progress = Signal(str)

    def __init__(self, profile_cog):
        super().__init__()
        self.profile_cog = profile_cog

    def run(self):
        """Load profile data."""
        try:
            self.progress.emit("Loading profile from PSN...")
            profile = self.profile_cog.get_my_profile(include_trophies=True, skip_avatars=False)
            if profile:
                self.progress.emit("Processing profile data...")
                self.finished.emit(profile)
            else:
                self.error.emit("Failed to load profile")
        except Exception as e:
            self.error.emit(f"Error loading profile: {str(e)}")


class FriendsLoaderThread(QThread):
    """Thread for loading friends list."""

    finished = Signal(list)  # List[str]
    error = Signal(str)
    progress = Signal(str)

    def __init__(self, friends_cog, limit: int = 50):
        super().__init__()
        self.friends_cog = friends_cog
        self.limit = limit

    def run(self):
        """Load friends list."""
        try:
            friends = self.friends_cog.get_friends_list(limit=self.limit, progress_callback=self.progress.emit)
            self.finished.emit(friends)
        except Exception as e:
            self.error.emit(f"Error loading friends: {str(e)}")


class GamesLoaderThread(QThread):
    """Thread for loading games list."""

    finished = Signal(list)  # List[GameData]
    error = Signal(str)
    progress = Signal(str)

    def __init__(self, games_cog, limit: int = 20):
        super().__init__()
        self.games_cog = games_cog
        self.limit = limit

    def run(self):
        """Load games list."""
        try:
            self.progress.emit("Loading games library from PSN...")
            games = self.games_cog.get_games_list(limit=self.limit)
            self.finished.emit(games)
        except Exception as e:
            self.error.emit(f"Error loading games: {str(e)}")


class UserSearchThread(QThread):
    """Thread for searching users."""

    finished = Signal(object)  # UserProfile or None
    error = Signal(str)
    progress = Signal(str)

    def __init__(self, search_cog, username: str):
        super().__init__()
        self.search_cog = search_cog
        self.username = username

    def run(self):
        """Search for user."""
        try:
            self.progress.emit(f"Searching for user '{self.username}'...")
            profile = self.search_cog.search_user(self.username.strip())
            self.finished.emit(profile)
        except Exception as e:
            self.error.emit(f"Search error: {str(e)}")


class NPSSODialog(QDialog):
    """Dialog for NPSSO token input."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PSN Tool - NPSSO Setup")
        self.setModal(True)
        self.setFixedSize(500, 300)

        layout = QVBoxLayout()

        # Title
        title = QLabel("Welcome to PSN Tool!")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "To use PSN Tool, you need an NPSSO token from PlayStation Network.\n\n"
            "1. Visit: https://ca.account.sony.com/api/v1/ssocookie\n"
            "2. Log in to your PSN account\n"
            "3. Copy the NPSSO token and paste it below:"
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Token input
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Enter your NPSSO token...")
        self.token_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.token_input)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save & Continue")
        self.save_button.clicked.connect(self.accept)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_token(self) -> str:
        """Get the entered token."""
        return self.token_input.text().strip()


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.client = PSNClient()
        self.current_profile: Optional[UserProfile] = None
        self.active_threads = []  # Track active threads for cleanup

        # Initialize cogs for business logic
        self.friends_cog = FriendsCog(self.client)
        self.games_cog = GamesCog(self.client)
        self.search_cog = SearchCog(self.client)
        self.profile_cog = ProfileCog(self.client)
        self.token_cog = TokenCog(self.client)

        self.setWindowTitle("PSN Tool v2.0")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        # Initialize UI
        self.setup_ui()

        # Check if we need NPSSO setup
        if not self.client.is_authenticated():
            self.show_npsso_dialog()
        else:
            self.load_profile()

    def closeEvent(self, event):
        """Handle window close event - cleanup threads."""
        self.cleanup_threads()
        event.accept()

    def cleanup_threads(self):
        """Clean up active threads."""
        for thread in self.active_threads[:]:  # Copy list to avoid modification during iteration
            if thread.isRunning():
                thread.quit()
                thread.wait(1000)  # Wait up to 1 second
                if thread.isRunning():
                    thread.terminate()  # Force termination if needed
            self.active_threads.remove(thread)
        self.active_threads.clear()

    def track_thread(self, thread: QThread):
        """Track a thread for cleanup."""
        self.active_threads.append(thread)
        thread.finished.connect(lambda: self.untrack_thread(thread))

    def untrack_thread(self, thread: QThread):
        """Remove thread from tracking."""
        if thread in self.active_threads:
            self.active_threads.remove(thread)

    def setup_ui(self):
        """Setup the main UI."""
        # Create central widget
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        # Main content area
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Navigation
        self.setup_navigation_panel(splitter)

        # Right panel - Content
        self.setup_content_panel(splitter)

        main_layout.addWidget(splitter)
        splitter.setSizes([300, 900])  # Initial sizes

        central_layout.addLayout(main_layout, stretch=1)

        # Status bar at bottom
        status_bar = self.setup_status_bar()
        central_layout.addWidget(status_bar)

        self.setCentralWidget(central_widget)

        # Initialize UI components
        self.friends_ui = FriendsUI(self.content_area, self.content_title, self.search_friend)
        self.games_ui = GamesUI(self.content_area, self.content_title)
        self.search_ui = SearchUI(
            self.content_area,
            self.content_title,
            self.perform_search,
            self.load_search_picture,
            self.on_search_picture_error
        )
        self.profile_ui = ProfileUI(self.content_area, self.content_title)
        self.settings_ui = SettingsUI(self.content_area, self.content_title, self)

    def setup_navigation_panel(self, splitter):
        """Setup the navigation panel."""
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)

        # Profile section
        profile_frame = QFrame()
        profile_frame.setFrameStyle(QFrame.Box)
        profile_frame.setProperty("class", "profile-frame")
        self.profile_layout = QVBoxLayout(profile_frame)

        profile_title = QLabel("User Profile")
        profile_title.setFont(QFont("Arial", 14, QFont.Bold))
        self.profile_layout.addWidget(profile_title)

        # Profile picture
        self.profile_picture_label = QLabel()
        self.profile_picture_label.setFixedSize(80, 80)
        self.profile_picture_label.setStyleSheet("border: 2px solid #ccc; border-radius: 5px;")
        self.profile_picture_label.setAlignment(Qt.AlignCenter)
        self.profile_picture_label.setText("No Image")
        self.profile_layout.addWidget(self.profile_picture_label, alignment=Qt.AlignCenter)

        # Profile info will be populated later
        self.profile_info_label = QLabel("Loading...")
        self.profile_info_label.setWordWrap(True)
        self.profile_layout.addWidget(self.profile_info_label)

        # Resign ID field
        resign_layout = QHBoxLayout()
        resign_label = QLabel("Resign ID:")
        resign_label.setStyleSheet("font-weight: bold;")
        resign_layout.addWidget(resign_label)

        self.resign_id_edit = QLineEdit()
        self.resign_id_edit.setReadOnly(True)
        self.resign_id_edit.setPlaceholderText("Loading...")
        self.resign_id_edit.setToolTip("Click to select and copy the Resign ID")
        self.resign_id_edit.setProperty("class", "resign-id-field")
        resign_layout.addWidget(self.resign_id_edit)

        self.profile_layout.addLayout(resign_layout)

        # Trophy breakdown
        self.trophy_info_label = QLabel("Loading trophies...")
        self.trophy_info_label.setProperty("class", "trophy-info")
        self.profile_layout.addWidget(self.trophy_info_label)

        nav_layout.addWidget(profile_frame)

        # Navigation buttons
        nav_layout.addStretch()

        buttons_frame = QFrame()
        buttons_layout = QVBoxLayout(buttons_frame)

        nav_title = QLabel("Actions")
        nav_title.setFont(QFont("Arial", 12, QFont.Bold))
        buttons_layout.addWidget(nav_title)

        # Action buttons
        self.friends_button = QPushButton("👥 View Friends")
        self.friends_button.clicked.connect(self.show_friends)
        self.friends_button.setMinimumHeight(40)
        buttons_layout.addWidget(self.friends_button)

        self.games_button = QPushButton("🎮 View Games")
        self.games_button.clicked.connect(self.show_games)
        self.games_button.setMinimumHeight(40)
        buttons_layout.addWidget(self.games_button)

        self.search_button = QPushButton("🔍 Search Users")
        self.search_button.clicked.connect(self.show_search)
        self.search_button.setMinimumHeight(40)
        buttons_layout.addWidget(self.search_button)

        buttons_layout.addStretch()

        # Settings
        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.clicked.connect(self.show_settings)
        buttons_layout.addWidget(self.settings_button)

        nav_layout.addWidget(buttons_frame)

        splitter.addWidget(nav_widget)

    def setup_content_panel(self, splitter):
        """Setup the content panel."""
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Content title
        self.content_title = QLabel("Welcome to PSN Tool")
        self.content_title.setFont(QFont("Arial", 18, QFont.Bold))
        self.content_title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.content_title)

        # Content area
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.content_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Placeholder content
        placeholder = QLabel("Select an action from the left panel to get started.")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #888; font-size: 14px;")
        self.content_area.setWidget(placeholder)

        content_layout.addWidget(self.content_area)

        splitter.addWidget(content_widget)

    def setup_status_bar(self):
        """Setup status bar at bottom of window."""
        # Create status bar widget
        status_widget = QWidget()
        status_widget.setStyleSheet("background-color: #1d2021; border-top: 1px solid #665c54;")
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(10, 5, 10, 5)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        status_layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumWidth(200)
        self.progress_bar.setMaximumWidth(300)
        status_layout.addWidget(self.progress_bar)

        status_layout.addStretch()

        return status_widget

    def show_npsso_dialog(self):
        """Show NPSSO input dialog."""
        dialog = NPSSODialog(self)
        if dialog.exec() == QDialog.Accepted:
            token = dialog.get_token()
            if token:
                if self.client.set_npsso(token):
                    self.load_profile()
                else:
                    QMessageBox.critical(self, "Authentication Failed",
                                       "Invalid NPSSO token. Please check and try again.")
                    self.show_npsso_dialog()
            else:
                QMessageBox.warning(self, "Input Required",
                                  "NPSSO token is required to use PSN Tool.")
                self.close()
        else:
            self.close()

    def load_profile(self):
        """Load user profile."""
        self._show_progress("Loading profile from PSN...")

        # Load profile in background thread
        loader = ProfileLoaderThread(self.profile_cog)
        loader.progress.connect(self._show_progress)
        loader.finished.connect(self.on_profile_loaded)
        loader.error.connect(self.on_profile_error)
        self.track_thread(loader)
        loader.start()

    def on_profile_loaded(self, profile: UserProfile):
        """Handle successful profile load."""
        self.current_profile = profile
        self._hide_progress()

        # Update navigation panel using UI component
        self.profile_ui.display_profile_info(
            profile, self.profile_layout, self.resign_id_edit, self.trophy_info_label
        )

        # Add base64 button if profile has base64 data
        base64_button = self.profile_ui.add_base64_button(
            profile, self.profile_layout, self.copy_profile_base64
        )
        if base64_button:
            self.base64_button = base64_button

        # Load profile picture
        if hasattr(profile, 'avatar_url') and profile.avatar_url:
            self.load_profile_picture(profile.avatar_url)

        # Show welcome message in content area
        self.profile_ui.show_welcome_content(profile)

    def load_profile_picture(self, url: str):
        """Load and display profile picture."""
        loader = ImageLoader(url, (80, 80))
        loader.finished.connect(self.on_profile_picture_loaded)
        loader.error.connect(self.on_profile_picture_error)
        self.track_thread(loader)

        loader.start()

    def load_search_picture(self, url: str, label: QLabel):
        """Load profile picture for search results."""
        loader = ImageLoader(url, (80, 80))
        loader.finished.connect(lambda pixmap: self.on_search_picture_loaded(label, pixmap))
        loader.error.connect(lambda error: self.on_search_picture_error(label, error))
        self.track_thread(loader)
        loader.start()

    def on_profile_picture_loaded(self, pixmap: QPixmap):
        """Handle successful profile picture load."""
        if not pixmap.isNull():
            self.profile_picture_label.setPixmap(pixmap)
        else:
            self.on_profile_picture_error("Invalid image data")

    def on_profile_picture_error(self, error_msg: str):
        """Handle profile picture load error."""
        self.profile_picture_label.setText("No Image")
        print(f"Profile picture error: {error_msg}")

    def on_profile_error(self, error_msg: str):
        """Handle profile load error."""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Profile Load Error", error_msg)

    def _show_error(self, error_msg: str):
        """Helper method to display error messages in content area."""
        self.progress_bar.setVisible(False)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        error_label = QLabel(error_msg)
        error_label.setStyleSheet("color: #d9534f;")
        layout.addWidget(error_label)
        self.content_area.setWidget(content_widget)

    def _show_progress(self, message: str, value: int = 0, maximum: int = 0):
        """Show progress bar with message."""
        self.status_label.setText(message)
        self.progress_bar.setVisible(True)
        self.progress_bar.setFormat("")
        if maximum > 0:
            self.progress_bar.setMaximum(maximum)
            self.progress_bar.setValue(value)
        else:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress

    def _hide_progress(self):
        """Hide progress bar."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")

    def _set_status(self, message: str):
        """Set status bar message."""
        self.status_label.setText(message)

    def show_friends(self):
        """Show friends list."""
        self.friends_ui.show_friends_loading()
        self._show_progress("Loading friends list from PSN...")

        # Load friends in background thread
        loader = FriendsLoaderThread(self.friends_cog, limit=50)
        loader.progress.connect(self._show_progress)
        loader.finished.connect(self.on_friends_loaded)
        loader.error.connect(self.on_friends_error)
        self.track_thread(loader)
        loader.start()

    def on_friends_loaded(self, friends):
        """Handle successful friends load."""
        self._hide_progress()
        self.friends_ui.display_friends_list(friends)

    def on_friends_error(self, error_msg: str):
        """Handle friends load error."""
        self._hide_progress()
        self._show_error(f"Error loading friends: {error_msg}")

    def search_friend(self, friend_name):
        """Search for a friend's profile."""
        self.friends_ui.display_friend_search(friend_name)
        self._show_progress(f"Searching for user '{friend_name}'...")

        # Search in background thread
        searcher = UserSearchThread(self.search_cog, friend_name.strip())
        searcher.progress.connect(self._show_progress)
        searcher.finished.connect(lambda profile: self.on_friend_search_complete(profile, friend_name))
        searcher.error.connect(self.on_friend_search_error)
        self.track_thread(searcher)
        searcher.start()

    def on_friend_search_complete(self, profile, friend_name):
        """Handle friend search completion."""
        self._hide_progress()
        if profile:
            self.search_ui.display_search_results(profile, in_friend_context=True)
            self.content_title.setText(f"Profile: {friend_name}")
        else:
            self.search_ui.show_search_error(f"Could not find user '{friend_name}' or their profile is private.")
            self.content_title.setText("Search Failed")

    def on_friend_search_error(self, error_msg: str):
        """Handle friend search error."""
        self._hide_progress()
        self.search_ui.show_search_error(f"Search error: {error_msg}")
        self.content_title.setText("Search Error")

    def show_games(self):
        """Show games list."""
        self.games_ui.show_games_loading()
        self._show_progress("Loading games library from PSN...")

        # Load games in background thread
        loader = GamesLoaderThread(self.games_cog, limit=20)
        loader.progress.connect(self._show_progress)
        loader.finished.connect(self.on_games_loaded)
        loader.error.connect(self.on_games_error)
        self.track_thread(loader)
        loader.start()

    def on_games_loaded(self, games):
        """Handle successful games load."""
        self._hide_progress()
        self.games_ui.display_games_list(games)

    def on_games_error(self, error_msg: str):
        """Handle games load error."""
        self._hide_progress()
        self._show_error(f"Error loading games: {error_msg}")

    def show_search(self):
        """Show user search interface."""
        self.search_ui.show_search_interface()

    def perform_search(self, username: str):
        """Perform user search."""
        if not username.strip():
            self.search_ui.show_search_error("Please enter a username.")
            return

        self._show_progress(f"Searching for user '{username}'...")

        # Search in background thread
        searcher = UserSearchThread(self.search_cog, username.strip())
        searcher.progress.connect(self._show_progress)
        searcher.finished.connect(self.on_user_search_complete)
        searcher.error.connect(self.on_user_search_error)
        self.track_thread(searcher)
        searcher.start()

    def on_user_search_complete(self, profile):
        """Handle user search completion."""
        self._hide_progress()
        self.search_ui.display_search_results(profile)

    def on_user_search_error(self, error_msg: str):
        """Handle user search error."""
        self._hide_progress()
        self.search_ui.show_search_error(f"Search error: {error_msg}")

    def on_search_picture_loaded(self, label: QLabel, pixmap: QPixmap):
        """Handle search result picture load."""
        if not pixmap.isNull():
            label.setPixmap(pixmap)
        else:
            label.setText("No Image")

    def on_search_picture_error(self, label: QLabel, error_msg: str):
        """Handle search result picture load error."""
        label.setText("No Image")
        print(f"Search picture error: {error_msg}")

    def copy_profile_base64(self, base64_data: str):
        """Copy profile base64 data to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(base64_data)

        # Show confirmation
        QMessageBox.information(
            self, "Copied to Clipboard",
            f"Profile Base64 data copied to clipboard!\n\n"
            f"Length: {len(base64_data)} characters"
        )

    def show_settings(self):
        """Show settings panel."""
        self.settings_ui.show_settings_panel(self.token_cog)

    def change_token(self):
        """Change NPSSO token."""
        reply = QMessageBox.question(
            self, "Change Token",
            "Are you sure you want to change your NPSSO token?\n"
            "You'll need to enter a new one.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.show_npsso_dialog()

    def delete_token(self):
        """Delete stored NPSSO token."""
        reply = QMessageBox.question(
            self, "Delete Token",
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
            if self.token_cog.delete_token():
                # Update UI
                self.current_profile = None
                self.profile_info_label.setText("Not authenticated")
                self.resign_id_edit.setText("")
                self.trophy_info_label.setText("Please authenticate to view trophies")

                # Clear profile picture
                self.profile_picture_label.setText("No Image")

                # Remove base64 button if it exists
                if hasattr(self, 'base64_button'):
                    self.base64_button.setParent(None)
                    delattr(self, 'base64_button')

                QMessageBox.information(
                    self, "Token Deleted",
                    "Your NPSSO token has been deleted.\n"
                    "The application will restart to apply changes."
                )

                # Restart the application
                self.restart_application()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to delete token."
                )

    def restart_application(self):
        """Restart the application."""
        # Close current instance
        self.close()

        # Restart with same arguments
        import sys
        import os
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def apply_theme_from_setting(self):
        """Apply theme based on stored setting."""
        ThemeManager.apply_theme_from_setting(QApplication.instance())


def main():
    """Main application entry point."""
    # Check if we have a display (for headless environments)
    if not os.environ.get('DISPLAY') and sys.platform.startswith('linux'):
        print("❌ No display available. Running in headless mode.")
        print("To run the GUI, make sure you have a display server (X11/Wayland) available.")
        print()
        print("Solutions:")
        print("• On Linux with X11: export DISPLAY=:0")
        print("• On Linux with Wayland: export DISPLAY=:wayland-0")
        print("• Use Xvfb for headless testing: xvfb-run -a python gui.py")
        print("• On Windows/Mac: The GUI should work automatically.")
        print()
        print("Please ensure you have a display server available to run the GUI.")
        return 1

    # Test Qt imports early
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QGuiApplication
    except ImportError as e:
        print(f"❌ Failed to import PySide6: {e}")
        print("Make sure PySide6 is installed: pip install PySide6")
        return 1

    # Additional Qt checks
    try:
        from PySide6.QtGui import QGuiApplication
        if not QGuiApplication.platformName():
            print("❌ Qt platform plugin not available.")
            print("This might be due to missing Qt platform plugins.")
            return 1
    except ImportError:
        print("❌ Failed to import Qt GUI components.")
        return 1

    try:
        app = QApplication(sys.argv)
    except Exception as e:
        print(f"❌ Failed to create QApplication: {e}")
        print("This might be due to display/GUI system issues.")
        return 1

    # Set application properties
    app.setApplicationName("PSN Tool")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("PSN Tool")

    # Apply theme
    ThemeManager.apply_theme(app)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Handle clean shutdown
    exit_code = app.exec()

    # Ensure clean thread cleanup
    if window:
        window.cleanup_threads()
        app.processEvents()
        return exit_code




if __name__ == "__main__":
    sys.exit(main())
