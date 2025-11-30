# PSN Tool GUI - PySide6 Interface

A modern, beautiful GUI for the PSN Tool built with PySide6 (Qt6 for Python).

## 🚀 Features

- **Modern Interface**: Clean, responsive design using PySide6
- **NPSSO Management**: Automatic token setup and validation
- **Profile Display**: View your PSN profile with trophy information and profile picture
- **Friends List**: Browse your PlayStation friends
- **Games Library**: View your game collection with play statistics
- **User Search**: Search for other PSN users with profile pictures
- **Settings**: Token management and cache clearing

## 📋 Requirements

- Python 3.8+
- PySide6 (automatically installed)
- Existing PSN Tool dependencies

## 🏁 Quick Start

### Option 1: Download Pre-built Binary (Recommended)
Download the latest release for your platform from [GitHub Releases](https://github.com/bawsdeep/psntool/releases):

- **Windows**: `psntool-windows-v{version}.exe`
- **Linux**: `psntool-linux-v{version}`
- **macOS**: `psntool-macos-v{version}`

Just download and run - no installation required!

### Option 2: Run from Source
```bash
# Clone repository
git clone https://github.com/bawsdeep/psntool.git
cd psntool

# Install dependencies
pip install -r requirements.txt

# Run GUI
python gui.py
```

## 🎨 Interface Overview

### Main Window Layout
```
┌─────────────────┬─────────────────────────────┐
│ User Profile    │ Welcome back, username!     │
│ [Profile Pic]   │                             │
│ Online ID: xxx  │ Use buttons on left to      │
│ Region: xxx     │ explore your PSN data       │
│ Resign ID: xxx  │                             │
│ ──────────────  │ Future: Changelog & info    │
│ 🏆 Trophies     │ will appear here            │
│ Level: xxx      │                             │
│ Total: xxx      │                             │
│ 🥇 Platinum: x  │                             │
│ 🥈 Gold: xx     │                             │
│ 🥉 Silver: xxx  │                             │
│ 🏅 Bronze: xxxx │                             │
│ [📋 Copy Base64]│                             │
├─────────────────┼─────────────────────────────┤
│ 👥 View Friends │ [Friends List]              │
│ 🎮 View Games   │ 1. [Friend1] ← Card button  │
│ 🔍 Search Users │ 2. [Friend2] ← Card button  │
│ ⚙️ Settings     │ 3. [Friend3] ← Card button  │
│                 │ ...                         │
└─────────────────┴─────────────────────────────┘
```

### Navigation Buttons

- **👥 View Friends**: Display your friends list
- **🎮 View Games**: Show your games library with play counts
- **🔍 Search Users**: Search for other PSN users by Online ID
- **⚙️ Settings**: Manage NPSSO token and clear cache

## 🔐 NPSSO Setup

When you first run the GUI:

1. **NPSSO Dialog** appears automatically if no token is stored
2. **Instructions** guide you to get your NPSSO token
3. **Token validation** happens automatically
4. **Profile loads** once authenticated

### Getting NPSSO Token

1. Visit: `https://ca.account.sony.com/api/v1/ssocookie`
2. Log in to your PSN account
3. Copy the NPSSO value from browser developer tools
4. Paste it into the GUI dialog

## 🎮 Using the GUI

### Profile View
- Shows your Online ID, region, and trophy statistics
- **Profile Picture**: Displays your PSN avatar (80x80px)
- **Resign ID**: Clickable field showing your resign ID (copyable)
- **Profile Base64**: Button to copy your full profile data as base64 encoded string
- **Detailed Trophy Breakdown**: Shows level, total, and individual counts for platinum/gold/silver/bronze trophies in the sidebar
- Updates automatically when you change tokens

### Friends List
- Lists all your PlayStation friends
- Shows Online IDs of your friends
- **Card-Style Buttons**: Clean, modern buttons for each friend
- **Clickable Names**: Click any friend's button to search their profile
- Loads up to 50 friends for performance
- Scrollable interface for long friend lists

### Games Library
- Displays your game collection
- Shows play counts and progress where available
- Limited to 20 games in initial view

### User Search
- Enter any PSN Online ID to search
- **Profile Pictures**: Shows avatar images for found users
- **Account & Resign IDs**: Clickable fields for easy copying
- Shows user profile if found
- Displays trophy information for found users

### Settings
- **Change Token**: Update your NPSSO authentication token
- **Delete Token**: Remove stored token and sign out (requires re-authentication)
- **Clear Cache**: Remove stored API data for fresh fetches

## 🛠️ Technical Details

### Architecture
- **PySide6 (Qt6)**: Modern, native GUI framework
- **Modular Design**: Uses existing PSN Tool backend
- **Threading**: Background loading for API calls and images
- **Image Loading**: Downloads and caches profile pictures
- **Cross-Platform**: Native database paths for each OS
- **Responsive**: Adapts to different window sizes

### Data Storage
- **Database**: SQLite with cross-platform paths
  - Linux: `~/.local/share/psntool/psntool.db`
  - macOS: `~/Library/Application Support/PSNTool/psntool.db`
  - Windows: `%APPDATA%\PSNTool\psntool.db`
- **Migration**: Automatic migration from old `~/.psntool/` location
- **Settings**: JSON configuration stored alongside database

### Dependencies
- `PySide6>=6.10.0`: Main GUI framework
- All existing PSN Tool dependencies
- Qt6 runtime libraries (installed with PySide6)

### File Structure
```
gui.py              # Main GUI application
core/client.py      # PSN API client (shared with CLI)
cogs/               # Feature modules (shared with CLI)
models/             # Data models (shared with CLI)
```

## 🐛 Troubleshooting

### GUI Won't Start
```bash
# Check display (Linux)
echo $DISPLAY

# Set display if needed
export DISPLAY=:0

# Check PySide6 installation
python -c "import PySide6; print('PySide6 OK')"
```

### Authentication Issues
- Verify NPSSO token is valid
- Check token hasn't expired (usually 30 days)
- Try getting a fresh token from PSN

### API Errors
- Check internet connection
- PSN API may be temporarily unavailable
- Try clearing cache in settings

### Image Loading Issues
- Profile pictures may not load if URLs are invalid
- Some users may not have profile pictures set
- Check internet connection for image downloads
- Images are cached temporarily during session

## 🚀 Future Enhancements

- **Presence Status**: Show online/offline status of friends
- **Game Details**: More detailed game information and screenshots
- **Comparison Tools**: Compare profiles with friends
- **Export Features**: Export data to various formats
- **Themes**: Light/dark mode switching
- **Notifications**: Alerts for friend activity

## 📱 Platform Support

- **Windows**: ✅ Full support
- **macOS**: ✅ Full support
- **Linux**: ✅ Requires display server (X11/Wayland)
- **Headless**: ⚠️ GUI requires display, use CLI instead

## 🤝 Contributing

The GUI uses the same modular architecture as the CLI tool. New features can be added by:

1. Implementing backend logic in `core/` or `cogs/`
2. Adding GUI components in `gui.py`
3. Testing with both CLI and GUI interfaces

---

**Enjoy exploring your PSN data with the modern GUI interface!** 🎮✨
