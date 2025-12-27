#!/bin/bash
# Script to create the PHAI.app bundle

echo "Creating PHAI.app bundle..."

# Create app structure
mkdir -p PHAI.app/Contents/MacOS
mkdir -p PHAI.app/Contents/Resources

# Copy Info.plist if it doesn't exist
if [ ! -f "PHAI.app/Contents/Info.plist" ]; then
    cat > PHAI.app/Contents/Info.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>PHAI</string>
    <key>CFBundleIdentifier</key>
    <string>com.phai.mediaorganizer</string>
    <key>CFBundleName</key>
    <string>PHAI</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF
fi

# Create launcher script
cat > PHAI.app/Contents/MacOS/PHAI << 'EOF'
#!/bin/bash

# Get the directory where the app bundle is located
APP_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$APP_DIR"

# Activate virtual environment and run the GUI
source PHAIenv/bin/activate
python gui_app.py
EOF

# Make executable
chmod +x PHAI.app/Contents/MacOS/PHAI

echo "✅ PHAI.app created successfully!"
echo "You can now double-click PHAI.app to launch the application."

