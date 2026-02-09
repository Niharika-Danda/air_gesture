# Windows .exe Build Plan - Air Gesture Controller

**Project:** Air Gesture Controller with Swipes
**Objective:** Convert Python project to standalone Windows .exe while maintaining venv
**Date Created:** 2026-02-05
**Status:** Planning Phase

---

## Table of Contents
1. [Overview](#overview)
2. [Phase 1: Tool Selection & Setup](#phase-1-tool-selection--setup)
3. [Phase 2: Pre-Build Configuration](#phase-2-pre-build-configuration)
4. [Phase 3: Build the Executable](#phase-3-build-the-executable)
5. [Phase 4: Testing & Optimization](#phase-4-testing--optimization)
6. [Phase 5: Creating Windows Installer](#phase-5-creating-windows-installer)
7. [Phase 6: Distribution & venv Maintenance](#phase-6-distribution--venv-maintenance)
8. [Phase 7: Advanced Configuration](#phase-7-advanced-configuration)
9. [Phase 8: Post-Build Tasks](#phase-8-post-build-tasks)
10. [Quick Reference Commands](#quick-reference-commands)
11. [Troubleshooting](#troubleshooting)

---

## Overview

Convert your Python gesture controller project into a standalone Windows .exe file while maintaining the virtual environment for development and updates.

### Key Points
- **venv is KEPT** for development, testing, and rebuilding
- **End-users receive only** `AirGestureController.exe`
- **No Python installation required** on end-user machines
- **All dependencies bundled** into single executable

### Project Architecture
```
Air Gesture Controller
├── src/main.py              ← Entry point
├── src/gesture_engine.py    ← Core gesture recognition
├── src/camera_manager.py    ← Camera handling
├── src/ui_manager.py        ← CustomTkinter GUI
├── src/config.json          ← Runtime configuration
├── venv/                    ← Keep for development
├── requirements.txt         ← Dependencies
└── assets/                  ← Icons & resources (optional)
```

---

## Phase 1: Tool Selection & Setup

### Why PyInstaller?

| Tool | Pros | Cons | Best For |
|------|------|------|----------|
| **PyInstaller** | ✓ MediaPipe/OpenCV support ✓ Large community ✓ Easy setup | Larger exe size | Your project |
| cx_Freeze | More flexible | Complex configuration | Large apps |
| py2exe | Lightweight | Limited Python 3.x support | Outdated |
| Nuitka | Fastest execution | Long compile time | Performance-critical |

**Decision:** Use **PyInstaller** - best compatibility with your stack.

### Installation

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Install PyInstaller
pip install pyinstaller

# Verify installation
pyinstaller --version
```

---

## Phase 2: Pre-Build Configuration

### Step 1: Create PyInstaller Spec File

Create `build_spec.spec` in project root:

```python
# -*- mode: python ; coding: utf-8 -*-
# build_spec.spec - PyInstaller configuration for Air Gesture Controller

block_cipher = None

a = Analysis(
    ['src/main.py'],                    # Entry point
    pathex=[],
    binaries=[],
    datas=[
        ('src/config.json', 'src'),     # Include runtime config
        ('requirements.txt', '.'),      # Include requirements
    ],
    hiddenimports=[
        'mediapipe',                    # Hand gesture recognition
        'cv2',                          # OpenCV for camera
        'customtkinter',                # Modern GUI framework
        'pyautogui',                    # Shortcut execution
        'packaging',                    # Version utilities
        'numpy',                        # Numerical computing
        'PIL',                          # Image processing
    ],
    hookspath=[],
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AirGestureController',        # Name of .exe file
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                           # Use UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                      # No console window
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app_icon.ico',         # Optional: application icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AirGestureController'
)
```

### Step 2: Create App Icon (Optional but Recommended)

1. Create `assets/` folder in project root
2. Add `app_icon.ico` file (256x256 or larger)
3. Or convert PNG to ICO using online tools

```bash
# Using Python PIL
from PIL import Image
img = Image.open('icon.png')
img.save('assets/app_icon.ico')
```

### Step 3: Update & Verify requirements.txt

Ensure all dependencies are pinned with versions:

```
opencv-python==4.8.1.78
mediapipe==0.10.3
pyautogui==0.9.53
customtkinter==5.2.0
packaging==23.2
numpy==1.24.3
Pillow==10.0.0
```

**Verify:** Run in venv
```bash
pip list
```

### Step 4: Create Config Directory Structure

```bash
mkdir assets
# Place your icon here if available
```

---

## Phase 3: Build the Executable

### Option A: Using Spec File (Recommended)

```bash
# Activate venv
.\venv\Scripts\activate

# Build with spec file
pyinstaller build_spec.spec

# Output: dist/AirGestureController.exe
```

### Option B: Direct Command (Simpler, Less Control)

```bash
pyinstaller \
    --onefile \
    --windowed \
    --add-data="src/config.json:src" \
    --hidden-import=mediapipe \
    --hidden-import=cv2 \
    --hidden-import=customtkinter \
    --name=AirGestureController \
    --icon=assets/app_icon.ico \
    src/main.py
```

### Build Output Structure

```
Project Root/
├── build/                   # Temp build files (can delete)
├── dist/
│   ├── AirGestureController.exe       # ← Standalone executable
│   ├── _internal/           # Dependencies & libraries
│   └── ...
├── build_spec.spec
└── AirGestureController.spec           # Auto-generated
```

### Expected Build Time
- **First build:** 3-5 minutes (downloads models)
- **Subsequent builds:** 1-2 minutes
- **Exe size:** 400-600 MB (includes MediaPipe + OpenCV)

---

## Phase 4: Testing & Optimization

### Pre-Release Testing Checklist

#### Test 1: Basic Execution
```bash
# Navigate to dist folder
cd dist

# Run standalone exe (no Python needed)
AirGestureController.exe

# Verify: App launches with GUI
```

#### Test 2: Core Functionality
- [ ] Camera starts automatically
- [ ] Hand detection works in real-time
- [ ] Gestures are recognized (thumbs up, swipes, etc.)
- [ ] Profile switching works based on active window
- [ ] Audio feedback plays correctly

#### Test 3: Feature Validation
- [ ] Shortcut execution (keyboard input sent to active app)
- [ ] PowerPoint profile activates with presentation open
- [ ] Chrome profile activates in browser
- [ ] Overlay mode activates in full-screen apps
- [ ] FPS display shows correct performance

#### Test 4: Error Handling
- [ ] App handles no camera gracefully
- [ ] Missing config.json is handled
- [ ] Invalid profiles don't crash app
- [ ] Rapid gesture clicks don't break app

#### Test 5: Performance
```bash
# Monitor resource usage
# Expected: <200MB RAM, <20% CPU at idle
```

### Common Build Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `ImportError: No module named 'mediapipe'` | Missing from hiddenimports | Add `--hidden-import=mediapipe` |
| Camera not detected | DirectShow backend missing | Rebuild with latest OpenCV |
| GUI window black/no render | console=True or missing display | Set `console=False` in spec |
| File too large (>1GB) | Bloated dependencies | Remove unused packages from hiddenimports |
| Exe won't start on other PC | Missing Visual C++ runtime | Include VCREDIST installer |
| Gesture detection fails | MediaPipe models not included | Add models to datas in spec |

### Optimization Strategies

#### Reduce Exe Size
```python
# In build_spec.spec
excludedimports=[
    'matplotlib',      # If not used
    'pandas',          # If not used
    'scipy',           # If not used
]
upx=True             # Enable UPX compression
```

#### Improve Startup Time
```python
# In spec file
a = Analysis(
    ...
    runtime_hooks=['./optimize_loader.py'],  # Custom loader
)
```

#### Better Performance
- Build for specific Windows architecture (32-bit vs 64-bit)
- Test on target Windows versions (7, 10, 11)

---

## Phase 5: Creating Windows Installer

### Why Create an Installer?
- Professional distribution method
- Start menu shortcuts
- Uninstall support
- Registry integration (optional)
- Better user experience

### Option A: Inno Setup (Recommended for Beginners)

**Installation:**
1. Download from: https://jrsoftware.org/isdl.php
2. Install Inno Setup

**Create installer script** (`installer.iss`):

```ini
[Setup]
AppName=Air Gesture Controller
AppVersion=1.0.0
AppPublisher=Your Name/Company
AppPublisherURL=https://github.com/yourusername/air_gesture_controller
AppSupportURL=https://github.com/yourusername/air_gesture_controller
AppUpdatesURL=https://github.com/yourusername/air_gesture_controller
DefaultDirName={pf}\AirGestureController
DefaultGroupName=Air Gesture Controller
AllowNoIcons=yes
OutputDir=.\installer_output
OutputBaseFilename=AirGestureController_Setup
SetupIconFile=assets\app_icon.ico
UninstallDisplayIcon={app}\AirGestureController.exe
VersionInfoVersion=1.0.0.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\AirGestureController.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\config.json"; DestDir: "{app}\src"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Air Gesture Controller"; Filename: "{app}\AirGestureController.exe"
Name: "{group}\{cm:UninstallProgram,Air Gesture Controller}"; Filename: "{uninstallexe}"
Name: "{desktop}\Air Gesture Controller"; Filename: "{app}\AirGestureController.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AirGestureController.exe"; Description: "{cm:LaunchProgram,Air Gesture Controller}"; Flags: nowait postinstall skipifsilent
```

**Build installer:**
1. Open `installer.iss` in Inno Setup
2. Click Compile
3. Output: `installer_output/AirGestureController_Setup.exe`

### Option B: NSIS (Advanced)

For more control, use NSIS (Nullsoft Scriptable Install System).

### Option C: WiX Toolset (Enterprise)

Professional MSI creation for large deployments.

---

## Phase 6: Distribution & venv Maintenance

### Directory Structure After Build

```
C:\Users\NH\Desktop\NH\Gemini\v1\air_gesture_controller with Swipes\
├── venv/                           ← KEEP for development
│   ├── Scripts/
│   ├── Lib/
│   └── pyvenv.cfg
├── src/
│   ├── main.py
│   ├── gesture_engine.py
│   ├── camera_manager.py
│   └── ...
├── dist/
│   └── AirGestureController.exe    ← Give to end-users
├── build/                          ← Can delete after testing
├── installer_output/
│   └── AirGestureController_Setup.exe    ← For distribution
├── assets/
│   └── app_icon.ico
├── build_spec.spec
├── requirements.txt
├── EXE_BUILD_PLAN.md
└── README.md
```

### Workflow: Development → Release

#### Step 1: Development & Testing
```bash
# Work in venv
.\venv\Scripts\activate
python src/main.py

# Make changes, test locally
```

#### Step 2: Update Dependencies (if needed)
```bash
# Add new package
pip install new-package
pip freeze > requirements.txt

# Update hiddenimports in build_spec.spec
```

#### Step 3: Build Release
```bash
# Ensure venv is activated
.\venv\Scripts\activate

# Build exe
pyinstaller build_spec.spec

# Test exe
.\dist\AirGestureController.exe
```

#### Step 4: Create Installer
```bash
# Use Inno Setup to build .exe installer
# Or distribute dist/AirGestureController.exe directly
```

#### Step 5: Distribution
```
Option A: Direct exe
  └─ Send dist/AirGestureController.exe to users

Option B: Installer (Professional)
  └─ Send installer_output/AirGestureController_Setup.exe
```

### venv Maintenance Strategy

**Keep venv for:**
- Running tests: `pytest tests/`
- Development: `python src/main.py`
- Building releases: `pyinstaller build_spec.spec`
- Installing new dependencies: `pip install`

**Why NOT delete venv:**
- Needed for future code changes
- Used for testing before building
- Required for dependency updates
- venv is lightweight (few MB after cleanup)

**Clean up venv (optional):**
```bash
# Remove unused packages
pip autoclean

# Or create fresh venv when bloated
deactivate
rmdir /s venv
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

## Phase 7: Advanced Configuration

### Single-File vs Multi-File Distribution

#### Single-File (--onefile)
**Pros:**
- Easy for users: just one .exe
- Better for installer distribution
- Simpler deployment

**Cons:**
- Slower startup (unpacks to temp)
- Larger file size
- More disk I/O

```bash
pyinstaller --onefile src/main.py
```

#### Multi-File (--onedir)
**Pros:**
- Faster startup
- Easier to debug
- Can update individual DLLs

**Cons:**
- Multiple files to distribute
- Harder for end-users to manage

```bash
pyinstaller --onedir src/main.py
```

**Recommendation:** Use `--onefile` for distribution, `--onedir` for testing.

### Console vs Windowed Mode

#### Windowed (console=False) - Recommended
```python
console=False   # No console window, just your CustomTkinter GUI
```

#### Console (console=True)
```python
console=True    # Shows console window for debugging/logs
```

**For gesture app:** Use `console=False` for clean user experience.

### Code Signing (Optional)

Prevent "Windows Defender SmartScreen" warnings:

```bash
# Requires code signing certificate
signtool sign /f certificate.pfx /p password /t http://timestamp.server.com AirGestureController.exe
```

---

## Phase 8: Post-Build Tasks

### Immediate After-Build

- [ ] Test exe on clean Windows system (no Python)
- [ ] Test on different Windows versions (7, 10, 11)
- [ ] Test on different hardware (laptop camera, etc.)
- [ ] Verify all gestures work consistently
- [ ] Check audio feedback in various environments

### Before Release

- [ ] Create user documentation (Installation guide)
- [ ] Create system requirements document
- [ ] Setup auto-update mechanism (optional)
- [ ] Test installer on clean system
- [ ] Get testing feedback from beta users

### Version Management

Create version tracking:

```python
# src/version.py
__version__ = "1.0.0"

# Update in:
# - build_spec.spec (AppVersion)
# - installer.iss (AppVersion)
# - README.md
```

### Auto-Update System (Optional)

```python
# src/update_checker.py
import requests
import json

def check_for_updates():
    response = requests.get('https://api.github.com/repos/username/air_gesture_controller/releases/latest')
    latest = response.json()['tag_name']
    current = __version__
    return latest > current
```

---

## Quick Reference Commands

### Full Build Workflow
```bash
# 1. Activate venv
.\venv\Scripts\activate

# 2. Build exe
pyinstaller build_spec.spec

# 3. Test exe
.\dist\AirGestureController.exe

# 4. Create installer (if using Inno Setup)
# Open installer.iss in Inno Setup and click Compile

# 5. Result files
# - dist/AirGestureController.exe (for direct distribution)
# - installer_output/AirGestureController_Setup.exe (for professional distribution)
```

### One-Line Build (No Spec File)
```bash
pyinstaller --onefile --windowed --add-data="src/config.json:src" --hidden-import=mediapipe --hidden-import=cv2 --hidden-import=customtkinter --name=AirGestureController --icon=assets/app_icon.ico src/main.py
```

### Update After Code Changes
```bash
# 1. Make changes in src/
# 2. Test in venv: python src/main.py
# 3. Rebuild: pyinstaller build_spec.spec
# 4. Test new exe: dist/AirGestureController.exe
# 5. Update version in build_spec.spec
```

### Clean Build (Remove Old Artifacts)
```bash
# Remove build directories
rmdir /s /q build dist

# Rebuild
pyinstaller build_spec.spec
```

### Size Optimization
```bash
# Minimal dependencies build
pyinstaller --onefile --windowed --noupx src/main.py

# With compression
pyinstaller --onefile --windowed --upx-dir=C:\UPX src/main.py
```

---

## Troubleshooting

### Build Fails: ImportError

**Error:** `ModuleNotFoundError: No module named 'mediapipe'`

**Solutions:**
1. Add to hiddenimports in spec file
2. Ensure venv is activated
3. Reinstall: `pip install mediapipe --force-reinstall`

### Exe Won't Start

**Possible causes:**
1. Missing Visual C++ runtime → Download VCREDIST
2. Outdated MediaPipe → `pip install --upgrade mediapipe`
3. Corrupted build → Run: `rmdir /s /q build dist` then rebuild

### Camera Not Working in Exe

**Fixes:**
1. Use `cv2.CAP_DSHOW` instead of default backend
2. Install Windows Media Feature Pack (for some Windows editions)
3. Update camera drivers
4. Try different camera index in config.json

### Gesture Recognition Failed in Exe

**Troubleshooting:**
1. Verify MediaPipe models are included (check `build_spec.spec` datas)
2. Test with console=True to see error messages
3. Check lighting conditions
4. Verify hand is in camera view

### Installer Won't Run

**Check:**
1. Administrator privileges required? Set in Inno Setup
2. Windows version compatibility (test on target OS)
3. Check antivirus not blocking installer
4. Run with compatibility mode if needed

### Performance Issues in Exe

**Optimization steps:**
1. Monitor CPU/RAM usage
2. Reduce video resolution in config.json
3. Lower gesture detection confidence threshold
4. Disable overlay mode if not needed
5. Update GPU drivers for CV processing

### File Size Too Large (>800MB)

**Reduction strategies:**
1. Remove unused hiddenimports
2. Enable UPX compression: `upx=True`
3. Use `--onedir` for multi-file distribution
4. Remove debug info: `strip=True`

---

## Testing Checklist

### Functionality Testing
- [ ] App launches without errors
- [ ] Camera initializes automatically
- [ ] All 5+ gestures recognized in real-time
- [ ] Shortcuts execute in target applications
- [ ] Profile switching works (PowerPoint, Chrome, etc.)
- [ ] Audio feedback plays
- [ ] Overlay mode activates in presentations
- [ ] Config reloads work
- [ ] Quit function works cleanly

### Performance Testing
- [ ] FPS >30 in normal conditions
- [ ] CPU usage <25% at idle
- [ ] RAM usage <200MB
- [ ] No lag between gesture and action
- [ ] No memory leaks over 30min runtime

### Compatibility Testing
- [ ] Works on Windows 10
- [ ] Works on Windows 11
- [ ] Works on different webcams
- [ ] Works with USB camera hubs
- [ ] Works with high-resolution cameras

### Error Handling
- [ ] Graceful handling with no camera
- [ ] No crash on invalid config
- [ ] No crash on missing files
- [ ] Proper error messages displayed

---

## Next Steps

1. **Implement Phase 1-2:** Setup PyInstaller and create spec file
2. **Build Phase 3:** Create first exe and test
3. **Iterate Phase 4:** Fix issues and optimize
4. **Distribute Phase 5:** Create installer
5. **Maintain:** Use venv for updates

---

## Resources

- **PyInstaller Docs:** https://pyinstaller.org/
- **Inno Setup:** https://jrsoftware.org/isinfo.php
- **MediaPipe:** https://mediapipe.dev/
- **CustomTkinter:** https://github.com/TomSchimansky/CustomTkinter

---

**Status:** Ready for implementation
**Last Updated:** 2026-02-05
