# How to Open PHAI.app

If macOS blocks the app from opening, here's how to fix it:

## Method 1: Right-click and Open (Recommended)

1. **Right-click** (or Control+click) on `PHAI.app`
2. Select **"Open"** from the menu
3. Click **"Open"** in the security dialog that appears
4. The app will now open normally

## Method 2: Remove Quarantine Attribute

Open Terminal and run:
```bash
cd "/Users/francescacentini/Desktop/Life/Hobbies/06_Computer science/01_Projects/PHAI"
xattr -cr PHAI.app
```

Then try double-clicking the app again.

## Method 3: System Settings

1. Go to **System Settings** → **Privacy & Security**
2. Scroll down to **Security**
3. If you see a message about PHAI being blocked, click **"Open Anyway"**

## Alternative: Use the Script

If the app still doesn't work, you can always use:
```bash
./run_gui.sh
```

Or manually:
```bash
source PHAIenv/bin/activate
python gui_app.py
```

