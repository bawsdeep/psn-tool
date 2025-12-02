"""Search UI display components."""

import sys
import os
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton, QFrame
from PySide6.QtCore import Qt, QTimer

# Ensure proper imports
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from models import UserProfile


class SearchUI:
    """Handles search-related UI display logic."""

    def __init__(self, content_area, content_title, search_callback=None, image_load_callback=None, image_error_callback=None, view_friends_callback=None, view_games_callback=None):
        self.content_area = content_area
        self.content_title = content_title
        self.search_callback = search_callback
        self.image_load_callback = image_load_callback
        self.image_error_callback = image_error_callback
        # Optional callback to view a user's friends list (if public)
        self.view_friends_callback = view_friends_callback
        # Optional callback to view a user's games list (if public)
        self.view_games_callback = view_games_callback
        self.search_results_container = None
        self.search_input = None
        self.search_results_label = None
        self.search_section = None  # Reference to search section for hiding/showing
        self._widget_valid = True  # Track if widgets are still valid

    def show_search_interface(self):
        """Show user search interface."""
        # Disconnect old search input signals if it exists
        if self.search_input:
            try:
                self.search_input.returnPressed.disconnect()
            except (TypeError, RuntimeError):
                # Signal already disconnected or widget deleted, ignore
                pass
        
        self._widget_valid = True  # Mark widgets as valid
        self.content_title.setText("Search Users")
        
        # Show search section if it exists and was hidden
        if self.search_section:
            try:
                _ = self.search_section.objectName()  # Verify it's still valid
                self.search_section.setVisible(True)
                # Clear any existing results
                self.clear_search_results_container()
                if self.search_results_label:
                    try:
                        self.search_results_label.setText("")
                    except RuntimeError:
                        pass
                # Ensure signal connection is still active
                if self.search_input:
                    try:
                        _ = self.search_input.objectName()  # Verify it's still valid
                        # Reconnect signal in case it was disconnected
                        try:
                            self.search_input.returnPressed.disconnect()
                        except (TypeError, RuntimeError):
                            # Signal not connected, that's fine
                            pass
                        self.search_input.returnPressed.connect(self._on_search_triggered)
                        # Set focus to search input after a short delay
                        QTimer.singleShot(50, lambda: self._focus_search_input())
                    except RuntimeError:
                        # Widget was deleted, will recreate below
                        pass
                return  # Don't recreate if section is still valid
            except RuntimeError:
                # Widget was deleted, will be recreated below
                self.search_section = None

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Search section with better visual design
        search_section = QFrame()
        search_section.setFrameStyle(QFrame.Box)
        search_section.setProperty("class", "search-section")
        search_layout = QVBoxLayout(search_section)
        search_layout.setSpacing(12)
        search_layout.setContentsMargins(20, 20, 20, 20)

        search_label = QLabel("Enter a PSN Online ID to search:")
        search_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        search_layout.addWidget(search_label)

        # Search input and button in horizontal layout
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)

        # Store search input as instance variable
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("e.g., VaultTec_Trading")
        self.search_input.setProperty("class", "search-input")
        # Connect Enter key to search - use method reference instead of lambda
        self.search_input.returnPressed.connect(self._on_search_triggered)
        input_layout.addWidget(self.search_input, stretch=1)
        # Set focus to search input for immediate typing
        self.search_input.setFocus()

        search_button = QPushButton("🔍 Search")
        search_button.setProperty("class", "search-button")
        search_button.clicked.connect(self._on_search_triggered)
        search_button.setMinimumWidth(120)
        input_layout.addWidget(search_button)

        search_layout.addLayout(input_layout)
        layout.addWidget(search_section)

        # Search results container
        self.search_results_container = QWidget()
        results_layout = QVBoxLayout(self.search_results_container)
        self.search_results_label = QLabel("")
        results_layout.addWidget(self.search_results_label)

        layout.addWidget(self.search_results_container)
        layout.addStretch()
        self.content_area.setWidget(content_widget)
        
        # Store reference to search section for hiding/showing
        self.search_section = search_section

    def _show_search_again(self):
        """Show search interface again after results are displayed."""
        self.show_search_interface()
        # Set focus to search input after a short delay to ensure widget is visible
        # Use QTimer to schedule focus after the widget is shown
        if self.search_input:
            try:
                _ = self.search_input.objectName()  # Verify it's still valid
                # Use single-shot timer to set focus after widget is shown
                QTimer.singleShot(50, lambda: self._focus_search_input())
            except RuntimeError:
                # Widget was deleted, ignore
                pass
    
    def _focus_search_input(self):
        """Set focus to search input and select all text."""
        if self.search_input:
            try:
                _ = self.search_input.objectName()  # Verify it's still valid
                # Ensure widget is visible and enabled
                if self.search_input.isVisible() and self.search_input.isEnabled():
                    self.search_input.setFocus()
                    self.search_input.selectAll()
            except RuntimeError:
                # Widget was deleted, ignore
                pass
    
    def _on_search_triggered(self):
        """Handle search trigger from button or Enter key."""
        if self.search_input:
            try:
                # Check if widget is still valid before accessing it
                _ = self.search_input.objectName()
                username = self.search_input.text()
                self.perform_search(username)
            except RuntimeError:
                # Widget was deleted, recreate interface
                self.show_search_interface()
                # Try again if widget was recreated
                if self.search_input:
                    try:
                        username = self.search_input.text()
                        self.perform_search(username)
                    except RuntimeError:
                        # Still invalid, just return
                        pass

    def perform_search(self, username: str):
        """Perform user search."""
        # Ensure search interface is shown and widgets exist
        if not self.search_results_label or not self.search_input:
            self.show_search_interface()
        else:
            # Verify widgets are still valid
            try:
                _ = self.search_input.objectName()
                _ = self.search_results_label.objectName()
            except RuntimeError:
                # Widgets were deleted, recreate interface
                self.show_search_interface()
        
        if not username.strip():
            try:
                if self.search_results_label:
                    _ = self.search_results_label.objectName()  # Verify it's still valid
                    self.search_results_label.setText("Please enter a username.")
            except RuntimeError:
                # Widget was deleted, recreate interface
                self.show_search_interface()
                if self.search_results_label:
                    try:
                        self.search_results_label.setText("Please enter a username.")
                    except RuntimeError:
                        pass
            return

        try:
            if self.search_results_label:
                _ = self.search_results_label.objectName()  # Verify it's still valid
                self.search_results_label.setText("Searching...")
        except RuntimeError:
            # Widget was deleted, recreate interface
            self.show_search_interface()
            if self.search_results_label:
                try:
                    self.search_results_label.setText("Searching...")
                except RuntimeError:
                    pass

        if self.search_callback:
            self.search_callback(username.strip())

    def display_search_results(self, profile: Optional[UserProfile], in_friend_context: bool = False):
        """Display search results with profile picture."""
        if not profile:
            try:
                if self.search_results_container:
                    self.clear_search_results_container()
                    if self.search_results_label:
                        try:
                            self.search_results_label.setText("User not found or profile is private.")
                        except RuntimeError:
                            # Widget was deleted, recreate interface
                            self.show_search_interface()
                            if self.search_results_label:
                                self.search_results_label.setText("User not found or profile is private.")
            except RuntimeError:
                # Widgets were deleted, recreate interface
                self.show_search_interface()
                if self.search_results_label:
                    self.search_results_label.setText("User not found or profile is private.")
            return

        # Check if we're in search UI context or friend search context
        if not in_friend_context:
            try:
                # Check if search_results_container still exists
                if hasattr(self, 'search_results_container') and self.search_results_container:
                    # Verify the widget is still valid
                    try:
                        _ = self.search_results_container.objectName()
                    except RuntimeError:
                        # Widget was deleted, recreate interface
                        self.show_search_interface()
                    
                    # We're in search UI context - clear existing content and add to container
                    self.clear_search_results_container()
                    self._add_profile_to_container(profile)
                else:
                    # Container doesn't exist, recreate interface
                    self.show_search_interface()
                    self.clear_search_results_container()
                    self._add_profile_to_container(profile)
            except RuntimeError:
                # Widgets were deleted, recreate interface
                self.show_search_interface()
                self.clear_search_results_container()
                self._add_profile_to_container(profile)
        else:
            # We're in friend search context - display directly in content area
            self._display_profile_directly(profile)

    def _add_profile_to_container(self, profile: UserProfile):
        """Add profile to search results container."""
        # Ensure container exists (it may have been deleted when switching views)
        try:
            if not self.search_results_container:
                self.show_search_interface()
            else:
                # Verify the widget is still valid
                try:
                    _ = self.search_results_container.objectName()
                except RuntimeError:
                    # Widget was deleted, recreate interface
                    self.show_search_interface()
            
            if not self.search_results_container or not self.search_results_container.layout():
                self.show_search_interface()

            # Hide the search section after displaying results
            if self.search_section:
                try:
                    _ = self.search_section.objectName()  # Verify it's still valid
                    self.search_section.setVisible(False)
                except RuntimeError:
                    # Widget was deleted, ignore
                    pass

            result_widget = self._create_profile_widget(profile)
            
            # Add a "Search Again" button at the top of results
            from PySide6.QtWidgets import QHBoxLayout, QPushButton
            button_layout = QHBoxLayout()
            search_again_button = QPushButton("🔍 Search Again")
            search_again_button.setProperty("class", "search-button")
            search_again_button.clicked.connect(self._show_search_again)
            button_layout.addWidget(search_again_button)
            button_layout.addStretch()
            
            layout = self.search_results_container.layout()
            if layout:
                # Insert button at the beginning
                layout.insertLayout(0, button_layout)
                layout.addWidget(result_widget)
        except RuntimeError:
            # Widgets were deleted, recreate interface and try again
            self.show_search_interface()
            if self.search_results_container and self.search_results_container.layout():
                result_widget = self._create_profile_widget(profile)
                self.search_results_container.layout().addWidget(result_widget)

    def _display_profile_directly(self, profile: UserProfile):
        """Display profile directly in content area."""
        try:
            # Mark old widgets as invalid before replacing
            self._widget_valid = False
            
            # Disconnect signals from search input before it gets deleted
            if self.search_input:
                try:
                    self.search_input.returnPressed.disconnect()
                except (TypeError, RuntimeError):
                    # Signal already disconnected or widget deleted, ignore
                    pass
            
            # Clear references to widgets that will be deleted
            # This prevents accessing deleted widgets later
            self.search_input = None
            self.search_results_container = None
            self.search_results_label = None
            
            # Get old widget before replacing it
            old_widget = self.content_area.widget()
            
            content_widget = QWidget()
            layout = QVBoxLayout(content_widget)

            result_widget = self._create_profile_widget(profile)
            layout.addWidget(result_widget)
            layout.addStretch()

            # Set content - this will delete the old widget
            self.content_area.setWidget(content_widget)
            
            # Mark new widgets as valid
            self._widget_valid = True
            
            # Delete old widget explicitly to ensure cleanup
            if old_widget:
                old_widget.deleteLater()
        except RuntimeError:
            # Widget was deleted, ignore and continue
            self._widget_valid = True  # Reset flag
            # Clear references
            self.search_input = None
            self.search_results_container = None
            self.search_results_label = None
            pass

    def _create_profile_widget(self, profile: UserProfile):
        """Create a profile display widget."""
        from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QLineEdit

        result_widget = QWidget()
        result_layout = QHBoxLayout(result_widget)

        # Profile picture container for better alignment
        picture_container = QWidget()
        picture_container.setFixedSize(80, 80)
        picture_layout = QVBoxLayout(picture_container)
        picture_layout.setContentsMargins(0, 0, 0, 0)
        picture_layout.setSpacing(0)

        picture_label = QLabel()
        picture_label.setFixedSize(80, 80)
        picture_label.setStyleSheet("border: 2px solid #ccc; border-radius: 5px;")
        picture_label.setAlignment(Qt.AlignCenter)
        picture_label.setText("No Image")

        # Load profile picture if available
        if hasattr(profile, 'avatar_url') and profile.avatar_url and self.image_load_callback and self.image_error_callback:
            self.image_load_callback(profile.avatar_url, picture_label)

        picture_layout.addWidget(picture_label)
        result_layout.addWidget(picture_container, alignment=Qt.AlignTop)

        # Profile info
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)

        # Online ID
        online_label = QLabel(f"Online ID: {profile.online_id}")
        online_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(online_label)

        # Account ID
        account_layout = QHBoxLayout()
        account_layout.addWidget(QLabel("Account ID:"))
        account_id_edit = QLineEdit(str(profile.account_id))
        account_id_edit.setReadOnly(True)
        account_id_edit.setToolTip("Click to select and copy the Account ID")
        account_id_edit.setProperty("class", "resign-id-field")
        account_layout.addWidget(account_id_edit)
        info_layout.addLayout(account_layout)

        # Resign ID
        resign_layout = QHBoxLayout()
        resign_layout.addWidget(QLabel("Resign ID:"))
        resign_id_edit = QLineEdit(getattr(profile, 'resign_id', 'N/A'))
        resign_id_edit.setReadOnly(True)
        resign_id_edit.setToolTip("Click to select and copy the Resign ID")
        resign_id_edit.setProperty("class", "resign-id-field")
        resign_layout.addWidget(resign_id_edit)
        info_layout.addLayout(resign_layout)

        # Region
        region_label = QLabel(f"Region: {profile.region or 'Unknown'}")
        info_layout.addWidget(region_label)

        # Trophies
        if profile.trophies:
            trophies_label = QLabel(f"""Trophies: Level {profile.trophies.level}
Total: {profile.trophies.total_count}
💎 Platinum: {profile.trophies.platinum}, 🟡 Gold: {profile.trophies.gold}
⚪ Silver: {profile.trophies.silver}, 🟤 Bronze: {profile.trophies.bronze}""")
            trophies_label.setWordWrap(True)
            info_layout.addWidget(trophies_label)

        # Action buttons
        buttons_layout = QHBoxLayout()
        
        # View Friends button (if callback provided)
        if self.view_friends_callback:
            friends_button = QPushButton("👥 View Friends (if public)")
            friends_button.setToolTip("View this user's friends list if their privacy settings allow it.")
            friends_button.setProperty("class", "action-button")
            friends_button.clicked.connect(lambda: self.view_friends_callback(profile.online_id))
            buttons_layout.addWidget(friends_button)

        # View Games button (if callback provided)
        if self.view_games_callback:
            games_button = QPushButton("🎮 View Games (if public)")
            games_button.setToolTip("View this user's games library if their privacy settings allow it.")
            games_button.setProperty("class", "action-button")
            games_button.clicked.connect(lambda: self.view_games_callback(profile.online_id))
            buttons_layout.addWidget(games_button)

        if buttons_layout.count() > 0:
            info_layout.addLayout(buttons_layout)

        info_layout.addStretch()
        result_layout.addWidget(info_widget, stretch=1)

        return result_widget

    def clear_search_results_container(self):
        """Clear search results container."""
        # Guard against deleted widgets (common in Qt when switching views)
        try:
            if hasattr(self, 'search_results_container') and self.search_results_container:
                layout = self.search_results_container.layout()
                if layout:
                    while layout.count():
                        child = layout.takeAt(0)
                        if child.widget():
                            child.widget().deleteLater()
        except RuntimeError:
            # Underlying C++ object already deleted; ignore and let caller recreate UI
            self.search_results_container = None

    def show_search_error(self, error_msg: str):
        """Show search error message."""
        if self.search_results_label:
            try:
                self.search_results_label.setText(error_msg)
            except RuntimeError:
                # Widget was deleted, recreate interface
                self.show_search_interface()
                if self.search_results_label:
                    self.search_results_label.setText(error_msg)
        self.clear_search_results_container()
