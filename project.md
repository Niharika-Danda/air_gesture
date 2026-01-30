# Air Gesture Shortcut Controller - Project Documentation

## Project Overview
The **Air Gesture Shortcut Controller** is a Python-based application that allows users to control their computer using hand gestures captured via a webcam. It is specifically optimized for presentations, providing an automatic "Overlay Mode" when full-screen applications (like PowerPoint or Google Slides) are detected.

**GitHub Repository:** [https://github.com/Niharika-Danda/air_gesture](https://github.com/Niharika-Danda/air_gesture)

## Architecture
The project follows a modular design, separating gesture logic, user interface, and system configuration.

### Core Components (`src/`)
- **[main.py](file:///c:/Users/NH/Desktop/NH/Gemini/v1/air_gesture_controller/src/main.py)**: The entry point and orchestrator. It manages the main application loop, camera discovery, and the transition between normal and overlay modes.
- **[gesture_processor.py](file:///c:/Users/NH/Desktop/NH/Gemini/v1/air_gesture_controller/src/gesture_processor.py)**: Encapsulates hand detection and gesture recognition using MediaPipe. It identifies landarks and maps them to high-level gestures (e.g., `THUMBS_UP`, `OPEN_PALM`).
- **[ui_manager.py](file:///c:/Users/NH/Desktop/NH/Gemini/v1/air_gesture_controller/src/ui_manager.py)**: Handles the Tkinter-based GUI. It manages the video feed display, control buttons, and the logic for the floating overlay window.
- **[config.py](file:///c:/Users/NH/Desktop/NH/Gemini/v1/air_gesture_controller/src/config.py)**: Centralized configuration for gesture-to-shortcut mappings, camera settings, and confidence thresholds.

## Key Features

### 1. Gesture Recognition
Uses Google's MediaPipe framework to track 21 hand landmarks in real-time. Current supported gestures and their default mappings:

| Gesture | Shortcut | Action |
| :--- | :--- | :--- |
| `THUMBS_UP` | `Right Arrow` | Next Slide |
| `THUMBS_DOWN` | `Left Arrow` | Previous Slide |
| `OPEN_PALM` | `F5` | Start Presentation |
| `V_SIGN` | `B` | Black Screen |
| `INDEX_POINTING_UP` | `W` | White Screen |
| `OK_SIGN` | `Home` | First Slide |
| `SPIDERMAN` | `End` | Last Slide |

### 2. Permanent Overlay Mode
The application now defaults to a "Permanent Overlay" mode to ensure visibility while using other applications.
- **Always On**: The window is permanently set to a small 320x180 floating window.
- **Top-Right Positioning**: Automatically positions itself at the top-right corner.
- **Always on Top**: Remains visible above all other windows.
- **Seamless Interaction**: Allows users to see the camera feed and gesture feedback while controlling the mouse or shortcuts in other apps.

### 3. Camera Management
Supports multiple webcams with real-time switching via a dropdown menu in the UI.

## Environment & Dependencies
- **Python Version**: Recommended 3.11 (optimized for MediaPipe).
- **Key Libraries**:
    - `opencv-python`: For video capture and frame processing.
    - `mediapipe`: For hand tracking and landmark detection.
    - `pyautogui`: For simulating keyboard shortcut execution.
    - `Pillow`: For image handling within the Tkinter UI.

## File Structure
```text
air_gesture_controller/
├── src/
│   ├── main.py                # Main Application Logic
│   ├── gesture_processor.py   # Hand Tracking & Gesture Logic
│   ├── ui_manager.py          # Tkinter GUI & Overlay Logic
│   └── config.py              # Configuration & Shortcut Mappings
├── run.bat                    # Windows Launcher (One-click setup)
├── run.sh                     # Linux/Mac Launcher
├── requirements.txt           # Project Dependencies
└── README.md                  # User-friendly Guide
```
