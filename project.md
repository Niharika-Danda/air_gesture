# Air Gesture Shortcut Controller - Project Documentation

## Project Overview
The **Air Gesture Shortcut Controller** is a Python-based application that allows users to control their computer using hand gestures captured via a webcam. It is specifically optimized for presentations, providing an automatic "Overlay Mode" when full-screen applications (like PowerPoint or Google Slides) are detected.

**GitHub Repository:** [https://github.com/Niharika-Danda/air_gesture](https://github.com/Niharika-Danda/air_gesture)

## Architecture
The project follows a modular design, separating gesture logic, user interface, and system configuration.

### Core Components (`src/`)
- **[main.py](file:///c:/Users/NH/Desktop/NH/Gemini/v1/air_gesture_controller/src/main.py)**: The entry point and orchestrator. It manages the main application loop, camera discovery, and the transition between normal and overlay modes.
- **[gesture_engine.py](file:///c:/Users/NH/Desktop/NH/Gemini/v1/air_gesture_controller/src/gesture_engine.py)**: The core processing unit. It uses MediaPipe for hand tracking and orchestrates gesture recognition (both static and dynamic).
- **[swipe_engine.py](file:///c:/Users/NH/Desktop/NH/Gemini/v1/air_gesture_controller/src/swipe_engine.py)**: A specialized engine for detecting dynamic swipe gestures (Left/Right) using trajectory analysis and velocity thresholds.
- **[ui_manager.py](file:///c:/Users/NH/Desktop/NH/Gemini/v1/air_gesture_controller/src/ui_manager.py)**: Handles the Tkinter-based GUI. It manages the video feed display, control buttons, and the logic for the floating overlay window.
- **[config.py](file:///c:/Users/NH/Desktop/NH/Gemini/v1/air_gesture_controller/src/config.py)**: Centralized configuration for profiles, mappings, and sensitivity settings.

## Key Features

### 1. Hybrid Gesture Recognition
Combines multiple detection methods for robust control:
- **Dynamic Swipes**: Velocity-based swipe detection (Left/Right) for natural slide navigation. works independently of static signs.
- **Static Signs**: Recognizes poses like `THUMBS_UP`, `OPEN_PALM`, `OK_SIGN` using geometric analysis.
- **Custom Gestures**: Includes a `GestureRecorder` system to save and recognize custom hand shapes via `custom_gestures.json`.

### 2. Application Profiles
Automatically switches control schemes based on the active window:
- **Default**: Swipes map to Arrow Keys (Next/Prev Slide).
- **PowerPoint/Slides**: Optimized for presentation control.
- **Chrome/Browser**: Swipes map to Tab switching or Back/Forward navigation.

### 3. Permanent Overlay Mode
The application defaults to a "Permanent Overlay" mode:
- **Always On**: Small 320x180 floating window.
- **Smart Positioning**: Stays at the top-right, always on top.
- **Feedback**: Shows the camera feed and recognized gestures in real-time.

## Environment & Dependencies
- **Python Version**: Recommended 3.11+.
- **Key Libraries**:
    - `opencv-python`: Video capture.
    - `mediapipe`: Hand tracking.
    - `pyautogui`: Keyboard simulation.
    - `numpy`: Geometric calculations for swipes/custom gestures.

## File Structure
```text
air_gesture_controller/
├── src/
│   ├── main.py                # Main Application Logic
│   ├── gesture_engine.py      # Core Gesture Processor
│   ├── swipe_engine.py        # Dynamic Swipe Logic
│   ├── gesture_recorder.py    # Custom Gesture Saving/Loading
│   ├── position_smoother.py   # Cursor/Landmark Smoothing
│   ├── ui_manager.py          # Tkinter GUI
│   └── config.py              # Configuration & Mappings
├── run.bat                    # Windows Launcher
├── requirements.txt           # Dependencies
└── README.md                  # User Guide
```
