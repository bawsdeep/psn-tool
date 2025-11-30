#!/usr/bin/env python3
"""
Local build script for testing PyInstaller builds before GitHub Actions.
Run this to test the build process locally.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def main():
    print("🔨 Building PSN Tool binary...")

    # Check if we're in the right directory
    if not Path("gui.py").exists():
        print("❌ Error: Run this script from the project root directory")
        sys.exit(1)

    # Install PyInstaller if not present
    try:
        import PyInstaller
        print("✅ PyInstaller is available")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    # Install project dependencies
    if Path("requirements.txt").exists():
        print("📦 Installing project dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

    # Determine platform
    system = platform.system().lower()
    if system == "darwin":
        system = "macos"
    print(f"🏗️  Building for {system}...")

    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    result = subprocess.run([sys.executable, "-m", "PyInstaller", "--clean", "psntool.spec"], capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ Build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(1)

    print("✅ Build completed!")
    print("📁 Binary created in: dist/psntool" + (".exe" if system == "windows" else ""))

    # Check if binary exists
    binary_path = Path("dist/psntool.exe" if system == "windows" else "dist/psntool")
    if binary_path.exists():
        size = binary_path.stat().st_size / (1024 * 1024)  # Size in MB
        print(f"📊 Binary size: {size:.2f} MB")
        print("🎉 Build successful!")
    else:
        print("❌ Binary not found!")

if __name__ == "__main__":
    main()
