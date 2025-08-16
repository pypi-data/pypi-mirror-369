# Robust emoji font installation for Linux servers and desktops
# This approach works consistently across different Linux distributions

echo "Installing Segoe UI Emoji font system-wide..."

# Create system fonts directory if it doesn't exist
sudo mkdir -p /usr/share/fonts/truetype/segoe-ui-emoji

# Copy font to system directory (works for all users)
sudo cp ../fonts/seguiemj-windows.ttf /usr/share/fonts/truetype/segoe-ui-emoji/

# Set proper permissions
sudo chmod 644 /usr/share/fonts/truetype/segoe-ui-emoji/seguiemj-windows.ttf

# Remove conflicting emoji fonts (optional, comment out if you want to keep them)
sudo apt remove -y fonts-noto-color-emoji fonts-noto-emoji

# Create system-wide fontconfig directory
sudo mkdir -p /etc/fonts/conf.d

# Create system-wide emoji font configuration
sudo tee /etc/fonts/conf.d/01-emoji-segoe.conf > /dev/null << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
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
</fontconfig>
EOF

# Refresh system font cache
sudo fc-cache -f -v

# Verify font installation
echo ""
echo "Verifying font installation..."
fc-list | grep -i "segoe\|emoji" || echo "Warning: Font may not be properly installed"

echo ""
echo "✅ Font installation complete!"
echo ""
echo "The font is now installed system-wide and should work for:"
echo "- Web browsers (Chrome, Firefox, etc.)"
echo "- PDF generation libraries"
echo "- System applications"
echo "- All users on this system"
echo ""
echo "For web applications, you may need to:"
echo "1. Restart your web server/application"
echo "2. Clear browser cache"
echo "3. Use CSS: font-family: 'Segoe UI Emoji', emoji;"