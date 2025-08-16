#!/usr/bin/env python3
"""
Robust emoji font installation for Linux servers and desktops.
This approach works consistently across different Linux distributions.
"""

import os
import pathlib
import shutil
import subprocess
import sys
from typing import Optional


class EmojiFont:
    """Handles emoji font installation on Linux systems."""

    FONT_SYSTEM_DIR = pathlib.Path("/usr/share/fonts/truetype/segoe-ui-emoji")
    FONTCONFIG_DIR = pathlib.Path("/etc/fonts/conf.d")
    FONTCONFIG_FILE = FONTCONFIG_DIR / "01-emoji-segoe.conf"

    def __init__(self):
        """Initialize the emoji font installer."""
        self.script_dir = pathlib.Path(__file__).parent
        self.font_file = self.script_dir.parent / "_fonts" / "seguiemj-windows.ttf"

    def check_root_privileges(self) -> bool:
        """Check if running with root privileges."""
        return os.geteuid() == 0

    def run_command(self, command: list[str], check: bool = True) -> Optional[subprocess.CompletedProcess]:
        """Run a system command with error handling."""
        try:
            result = subprocess.run(command, check=check, capture_output=True, text=True)
            return result
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {' '.join(command)}")
            print(f"Error: {e.stderr}")
            if check:
                raise
            return None
        except FileNotFoundError:
            print(f"Command not found: {command[0]}")
            if check:
                raise
            return None

    def create_system_font_directory(self) -> None:
        """Create system fonts directory if it doesn't exist."""
        print("Creating system fonts directory...")
        self.FONT_SYSTEM_DIR.mkdir(parents=True, exist_ok=True)

    def copy_font_file(self) -> None:
        """Copy font file to system directory."""
        if not self.font_file.exists():
            raise FileNotFoundError(f"Font file not found: {self.font_file}")

        print("Copying font to system directory...")
        target_font = self.FONT_SYSTEM_DIR / "seguiemj-windows.ttf"
        shutil.copy2(self.font_file, target_font)

        # Set proper permissions
        target_font.chmod(0o644)

    def remove_conflicting_fonts(self) -> None:
        """Remove conflicting emoji fonts (optional)."""
        print("Removing conflicting emoji fonts...")
        conflicting_fonts = ["fonts-noto-color-emoji", "fonts-noto-emoji"]

        for font in conflicting_fonts:
            result = self.run_command(["apt", "remove", "-y", font], check=False)
            if result and result.returncode == 0:
                print(f"Removed {font}")
            else:
                print(f"Could not remove {font} (may not be installed)")

    def create_fontconfig_directory(self) -> None:
        """Create system-wide fontconfig directory."""
        print("Creating fontconfig directory...")
        self.FONTCONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def create_fontconfig_file(self) -> None:
        """Create system-wide emoji font configuration."""
        print("Creating fontconfig file...")

        fontconfig_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <!-- Prefer Segoe UI Emoji for all emoji rendering -->
  <alias>
    <family>emoji</family>
    <prefer>
      <family>Segoe UI Emoji</family>
    </prefer>
  </alias>
  
  <!-- Map common emoji font names to Segoe UI Emoji -->
  <match target="pattern">
    <test name="family">
      <string>Apple Color Emoji</string>
    </test>
    <edit name="family" mode="assign" binding="same">
      <string>Segoe UI Emoji</string>
    </edit>
  </match>
  
  <match target="pattern">
    <test name="family">
      <string>Noto Color Emoji</string>
    </test>
    <edit name="family" mode="assign" binding="same">
      <string>Segoe UI Emoji</string>
    </edit>
  </match>
  
  <match target="pattern">
    <test name="family">
      <string>Twemoji</string>
    </test>
    <edit name="family" mode="assign" binding="same">
      <string>Segoe UI Emoji</string>
    </edit>
  </match>
  
  <!-- Ensure Segoe UI Emoji is available for all font families -->
  <alias>
    <family>serif</family>
    <prefer>
      <family>Segoe UI Emoji</family>
    </prefer>
  </alias>
  
  <alias>
    <family>sans-serif</family>
    <prefer>
      <family>Segoe UI Emoji</family>
    </prefer>
  </alias>
  
  <alias>
    <family>monospace</family>
    <prefer>
      <family>Segoe UI Emoji</family>
    </prefer>
  </alias>
</fontconfig>"""

        self.FONTCONFIG_FILE.write_text(fontconfig_content)

    def refresh_font_cache(self) -> None:
        """Refresh system font cache."""
        print("Refreshing font cache...")
        self.run_command(["fc-cache", "-f", "-v"])

    def verify_installation(self) -> bool:
        """Verify font installation."""
        print("\nVerifying font installation...")
        result = self.run_command(["fc-list"], check=False)

        if result and result.returncode == 0:
            output = result.stdout.lower()
            if "segoe" in output or "emoji" in output:
                print("✓ Font installation verified")
                return True

        print("⚠ Warning: Font may not be properly installed")
        return False

    def install(self, remove_conflicting: bool = True) -> bool:
        """Install emoji font system-wide."""
        try:
            if not self.check_root_privileges():
                print("Error: This script requires root privileges.")
                print("Please run with sudo or as root user.")
                return False

            print("Installing Segoe UI Emoji font system-wide...")

            self.create_system_font_directory()
            self.copy_font_file()

            if remove_conflicting:
                self.remove_conflicting_fonts()

            self.create_fontconfig_directory()
            self.create_fontconfig_file()
            self.refresh_font_cache()

            success = self.verify_installation()

            if success:
                print("\n✅ Font installation complete!")
                print("\nThe font is now installed system-wide and should work for:")
                print("- Web browsers (Chrome, Firefox, etc.)")
                print("- PDF generation libraries")
                print("- System applications")
                print("- All users on this system")
                print("\nFor web applications, you may need to:")
                print("1. Restart your web server/application")
                print("2. Clear browser cache")
                print("3. Use CSS: font-family: 'Segoe UI Emoji', emoji;")

            return success

        except Exception as e:
            print(f"Error during installation: {e}")
            return False


def main() -> int:
    """Main entry point for the script."""
    installer = EmojiFont()
    success = installer.install()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
