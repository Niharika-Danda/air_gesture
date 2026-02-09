# REFERENCES AND APPENDICES

---

# REFERENCES

## Academic Papers and Research

[1] Zhang, F., Bazarevsky, V., Vakunov, A., Tkachenka, A., Sung, G., Chang, C. L., & Grundmann, M. (2020). **MediaPipe Hands: On-device Real-time Hand Tracking.** arXiv preprint arXiv:2006.10214. Google Research.

[2] Mitra, S., & Acharya, T. (2007). **Gesture Recognition: A Survey.** IEEE Transactions on Systems, Man, and Cybernetics, Part C (Applications and Reviews), 37(3), 311-324.

[3] Rautaray, S. S., & Agrawal, A. (2015). **Vision based hand gesture recognition for human computer interaction: A survey.** Artificial Intelligence Review, 43(1), 1-54.

[4] Pisharady, P. K., & Saerbeck, M. (2015). **Recent methods and databases in vision-based hand gesture recognition: A review.** Computer Vision and Image Understanding, 141, 152-165.

[5] Kalman, R. E. (1960). **A New Approach to Linear Filtering and Prediction Problems.** Journal of Basic Engineering, 82(1), 35-45.

[6] Welch, G., & Bishop, G. (1995). **An Introduction to the Kalman Filter.** University of North Carolina at Chapel Hill, Department of Computer Science.

[7] Pizer, S. M., Amburn, E. P., Austin, J. D., et al. (1987). **Adaptive histogram equalization and its variations.** Computer Vision, Graphics, and Image Processing, 39(3), 355-368.

## Technical Documentation

[8] Google MediaPipe. (2023). **MediaPipe Hands Documentation.**
https://developers.google.com/mediapipe/solutions/vision/hand_landmarker

[9] OpenCV. (2023). **OpenCV-Python Tutorials.**
https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html

[10] OpenCV. (2023). **Video Capture Documentation.**
https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html

[11] OpenCV. (2023). **CLAHE (Contrast Limited Adaptive Histogram Equalization).**
https://docs.opencv.org/4.x/d5/daf/tutorial_py_histogram_equalization.html

[12] PyAutoGUI. (2023). **PyAutoGUI Documentation.**
https://pyautogui.readthedocs.io/en/latest/

[13] CustomTkinter. (2023). **CustomTkinter Documentation.**
https://customtkinter.tomschimansky.com/documentation/

[14] NumPy. (2023). **NumPy Documentation - numpy.polyfit.**
https://numpy.org/doc/stable/reference/generated/numpy.polyfit.html

[15] Python. (2023). **Python Threading Documentation.**
https://docs.python.org/3/library/threading.html

[16] Python. (2023). **Python Queue Documentation.**
https://docs.python.org/3/library/queue.html

## Books

[17] Szeliski, R. (2022). **Computer Vision: Algorithms and Applications** (2nd ed.). Springer.

[18] Bradski, G., & Kaehler, A. (2008). **Learning OpenCV: Computer Vision with the OpenCV Library.** O'Reilly Media.

[19] Géron, A. (2022). **Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow** (3rd ed.). O'Reilly Media.

## Online Resources

[20] Real Python. (2023). **An Intro to Threading in Python.**
https://realpython.com/intro-to-python-threading/

[21] Towards Data Science. (2022). **Understanding Kalman Filters.**
https://towardsdatascience.com/kalman-filter-explained

[22] GeeksforGeeks. (2023). **Linear Regression using Python.**
https://www.geeksforgeeks.org/linear-regression-python-implementation/

[23] Stack Overflow. (Various). **Community discussions on OpenCV, MediaPipe, and gesture recognition.**
https://stackoverflow.com/

## Standards and Guidelines

[24] Nielsen, J. (1994). **Usability Engineering.** Morgan Kaufmann.

[25] ISO 9241-11:2018. **Ergonomics of human-system interaction — Part 11: Usability: Definitions and concepts.**

[26] Brooke, J. (1996). **SUS: A 'Quick and Dirty' Usability Scale.** Usability Evaluation in Industry, 189-194.

---

# APPENDICES

---

## Appendix A: Installation Guide

### A.1 System Requirements

#### Minimum Requirements:
| Component | Requirement |
|-----------|-------------|
| Operating System | Windows 10 or Windows 11 |
| Processor | Dual-core 2.0 GHz |
| RAM | 4 GB |
| Storage | 500 MB free space |
| Camera | 720p USB webcam or built-in |
| Python | 3.11 or higher |

#### Recommended Requirements:
| Component | Requirement |
|-----------|-------------|
| Operating System | Windows 11 |
| Processor | Quad-core 2.5 GHz |
| RAM | 8 GB |
| Storage | 1 GB free space |
| Camera | 1080p webcam |
| Python | 3.11.x |

### A.2 Installation Steps

#### Step 1: Install Python

1. Download Python 3.11 from https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT:** Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Verify installation by opening Command Prompt and typing:
   ```
   python --version
   ```
   Should display: `Python 3.11.x`

#### Step 2: Download the Project

**Option A: Download ZIP**
1. Download the project ZIP file
2. Extract to a folder (e.g., `C:\GestureController`)

**Option B: Clone with Git**
```bash
git clone <repository-url>
cd air_gesture_controller
```

#### Step 3: Run the Application

**Easy Method (Recommended):**
1. Double-click `run.bat`
2. The script will:
   - Create a virtual environment
   - Install all dependencies
   - Launch the application

**Manual Method:**
```bash
# Open Command Prompt in project folder

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

### A.3 Troubleshooting Installation

| Problem | Solution |
|---------|----------|
| "Python not found" | Reinstall Python with "Add to PATH" checked |
| "pip not found" | Run: `python -m ensurepip --upgrade` |
| Camera not detected | Check camera connection, try different USB port |
| MediaPipe install fails | Ensure Python 3.11 (not 3.12+), try: `pip install mediapipe --upgrade` |
| Permission errors | Run Command Prompt as Administrator |

---

## Appendix B: User Manual

### B.1 Getting Started

#### Starting the Application
1. Double-click `run.bat` or run `python src/main.py`
2. The main window will appear
3. Click "Start Camera" to begin

#### Main Window Overview
```
┌─────────────────────────────────────────────────────────────┐
│  Air Gesture Shortcut Controller                      _ □ X │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                                                       │  │
│  │              CAMERA PREVIEW                           │  │
│  │                                                       │  │
│  │    FPS: 30  ●  ◄── Green dot = hand detected          │  │
│  │                                                       │  │
│  │                  ┌─────────────┐                      │  │
│  │                  │  Sign Zone  │ ◄── Place hand here  │  │
│  │                  └─────────────┘     for static signs │  │
│  │                                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Status: Running  [Camera ▼] [Start] [Stop] [⚙️]      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### B.2 Performing Gestures

#### Swipe Gestures (Always Active)

| Gesture | How to Perform | Default Action |
|---------|----------------|----------------|
| **Swipe Right** | Move hand quickly from left to right | Next slide / Right arrow |
| **Swipe Left** | Move hand quickly from right to left | Previous slide / Left arrow |

**Tips for Swipes:**
- Keep movement horizontal (not diagonal)
- Move at moderate speed (not too slow)
- Movement should be about 1 foot across

#### Static Gestures (Must Enable in Settings)

| Gesture | Hand Position | Default Action |
|---------|---------------|----------------|
| **Thumbs Up** 👍 | Thumb up, other fingers closed | Next / Right |
| **Thumbs Down** 👎 | Thumb down, other fingers closed | Previous / Left |
| **Open Palm** ✋ | All fingers extended | Start presentation (F5) |
| **OK Sign** 👌 | Thumb and index touching, others extended | Home / Confirm |
| **V-Sign** ✌️ | Index and middle fingers up | Custom action |
| **Pointing** ☝️ | Only index finger up | Custom action |
| **Spiderman** 🤟 | Thumb, index, pinky extended | Custom action |

**Tips for Static Gestures:**
- Place hand in the green "Sign Zone" box
- Hold gesture for about 1 second
- Keep hand relatively still

### B.3 Settings

Click the ⚙️ button to open settings.

#### General Tab
- **Detection Confidence:** How sure the system needs to be that it sees a hand
  - Higher (0.8+): More strict, fewer false detections
  - Lower (0.3-0.5): More sensitive, works in poor lighting

- **Gesture Cooldown:** Time between gesture detections
  - Higher (1.0+): Slower, prevents accidental double-triggers
  - Lower (0.3-0.5): Faster response, good for rapid gestures

- **Enable Mouse Pointer:** Control mouse cursor with index finger

- **Active Static Signs:** Check which gestures you want to use

#### Gestures Tab
- Edit keyboard shortcuts for each gesture
- Format: Single keys or combinations with `+`
- Examples: `right`, `left`, `ctrl+tab`, `alt+f4`

### B.4 Profiles

The system automatically changes gesture mappings based on the active application:

| Application | Profile | Optimized For |
|-------------|---------|---------------|
| PowerPoint, Google Slides | POWERPOINT | Presentation control |
| Chrome, Edge | CHROME | Browser navigation |
| Other applications | DEFAULT | General use |

### B.5 Overlay Mode

When you start the camera, the application automatically enters overlay mode:
- Small floating window in top-right corner
- Always stays on top of other windows
- Can be dragged to any position
- Click X to stop camera and close

---

## Appendix C: Keyboard Shortcut Reference

### C.1 Default Profile Shortcuts

| Gesture | Shortcut | Action |
|---------|----------|--------|
| SWIPE_RIGHT | `right` | Right arrow key |
| SWIPE_LEFT | `left` | Left arrow key |

### C.2 PowerPoint Profile Shortcuts

| Gesture | Shortcut | Action |
|---------|----------|--------|
| SWIPE_RIGHT | `right` | Next slide |
| SWIPE_LEFT | `left` | Previous slide |
| THUMBS_UP | `right` | Next slide |
| THUMBS_DOWN | `left` | Previous slide |
| V_SIGN | `b` | Black screen |
| OK_SIGN | `home` | First slide |
| SPIDERMAN | `end` | Last slide |

### C.3 Chrome Profile Shortcuts

| Gesture | Shortcut | Action |
|---------|----------|--------|
| SWIPE_RIGHT | `alt+right` | Forward in history |
| SWIPE_LEFT | `alt+left` | Back in history |
| THUMBS_UP | `ctrl+tab` | Next tab |
| THUMBS_DOWN | `ctrl+shift+tab` | Previous tab |
| OPEN_PALM | `f5` | Refresh page |
| OK_SIGN | `ctrl+t` | New tab |

### C.4 Custom Shortcut Format

When editing shortcuts in settings:

| Format | Example | Keys Pressed |
|--------|---------|--------------|
| Single key | `right` | Right Arrow |
| Two keys | `ctrl+c` | Ctrl + C |
| Three keys | `ctrl+shift+n` | Ctrl + Shift + N |
| Function key | `f5` | F5 |
| Special keys | `home`, `end`, `pageup`, `pagedown` | Respective keys |

---

## Appendix D: Project File Structure

```
air_gesture_controller/
│
├── run.bat                    # Windows launcher script
├── run.sh                     # Linux/Mac launcher script
├── requirements.txt           # Python dependencies
├── config.json               # User configuration (auto-generated)
├── custom_gestures.json      # Custom gesture data (optional)
├── README.md                 # Project readme
├── CLAUDE.md                 # Development documentation
│
├── src/                      # Source code directory
│   ├── __init__.py          # Package initializer
│   ├── main.py              # Application entry point
│   │                        #   - GestureControllerApp class
│   │                        #   - VisionThread class
│   │
│   ├── gesture_engine.py    # Gesture recognition
│   │                        #   - GestureProcessor class
│   │                        #   - MediaPipe integration
│   │                        #   - Static gesture detection
│   │
│   ├── swipe_engine.py      # Swipe detection
│   │                        #   - SwipeDetector class
│   │                        #   - Trajectory analysis
│   │
│   ├── position_smoother.py # Position smoothing
│   │                        #   - PositionSmoother2D class
│   │                        #   - LandmarkSmoother class
│   │                        #   - PointerSmoother class
│   │
│   ├── ui_manager.py        # User interface
│   │                        #   - AppUIManager class
│   │                        #   - ToastOverlay class
│   │
│   ├── config.py            # Configuration management
│   │                        #   - Settings constants
│   │                        #   - Profile definitions
│   │                        #   - save_config(), load_config()
│   │
│   ├── audio_feedback.py    # Audio feedback
│   │                        #   - AudioFeedback class
│   │
│   ├── gesture_recorder.py  # Custom gesture recording
│   │                        #   - GestureRecorder class
│   │
│   └── calibration.py       # Auto-calibration
│                            #   - AutoCalibrator class
│
├── C_Docs/                   # Thesis documentation
│   ├── Chapter_01_Introduction.md
│   ├── Chapter_02_Literature_Review.md
│   ├── Chapter_03_System_Analysis.md
│   ├── Chapter_04_System_Design.md
│   ├── Chapter_05_Implementation.md
│   ├── Chapter_06_Testing_Results.md
│   ├── Chapter_07_Conclusion.md
│   └── Chapter_08_References_Appendices.md
│
└── venv/                     # Virtual environment (auto-created)
```

---

## Appendix E: Configuration File Reference

### E.1 config.json Structure

```json
{
    "MIN_DETECTION_CONFIDENCE": 0.5,
    "GESTURE_COOLDOWN": 0.3,
    "ENABLE_MOUSE": false,
    "ENABLED_SIGNS": [
        "THUMBS_UP",
        "OPEN_PALM"
    ],
    "PROFILES": {
        "DEFAULT": {
            "SWIPE_RIGHT": ["right"],
            "SWIPE_LEFT": ["left"]
        },
        "POWERPOINT": {
            "SWIPE_RIGHT": ["right"],
            "SWIPE_LEFT": ["left"],
            "THUMBS_UP": ["right"],
            "THUMBS_DOWN": ["left"],
            "V_SIGN": ["b"],
            "OK_SIGN": ["home"],
            "SPIDERMAN": ["end"]
        },
        "CHROME": {
            "THUMBS_UP": ["ctrl", "tab"],
            "THUMBS_DOWN": ["ctrl", "shift", "tab"],
            "SWIPE_RIGHT": ["alt", "right"],
            "SWIPE_LEFT": ["alt", "left"],
            "OPEN_PALM": ["f5"],
            "OK_SIGN": ["ctrl", "t"]
        }
    }
}
```

### E.2 Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `MIN_DETECTION_CONFIDENCE` | float | 0.5 | MediaPipe detection threshold (0.0-1.0) |
| `GESTURE_COOLDOWN` | float | 0.3 | Seconds between gesture triggers |
| `ENABLE_MOUSE` | bool | false | Enable mouse pointer control |
| `ENABLED_SIGNS` | array | [] | List of active static gestures |
| `PROFILES` | object | {...} | Gesture-to-shortcut mappings per profile |

### E.3 Constants in config.py (Not User-Editable)

| Constant | Value | Description |
|----------|-------|-------------|
| `CAMERA_INDEX` | 0 | Default camera index |
| `VIDEO_WIDTH` | 1280 | Capture width in pixels |
| `VIDEO_HEIGHT` | 720 | Capture height in pixels |
| `WINDOW_TITLE` | "Air Gesture..." | Application window title |
| `MIN_TRACKING_CONFIDENCE` | 0.4 | MediaPipe tracking threshold |
| `LOW_LIGHT_MODE` | True | Enable CLAHE enhancement |
| `AUDIO_FEEDBACK_ENABLED` | True | Enable sound effects |
| `SIGN_ROI_ENABLED` | True | Enable ROI for static gestures |
| `SIGN_ROI_COORDS` | {...} | ROI boundaries |
| `GESTURE_CONFIRMATION_FRAMES` | 2 | Frames needed to confirm gesture |
| `SMOOTHING_BUFFER_SIZE` | 5 | Temporal voting buffer size |
| `FPS_ACTIVE` | 30 | Target FPS when hand detected |
| `FPS_IDLE` | 200 | Delay (ms) when no hand |
| `IDLE_TIMEOUT` | 5.0 | Seconds before idle mode |

---

## Appendix F: Glossary of Terms

| Term | Definition |
|------|------------|
| **BGR** | Blue-Green-Red color format used by OpenCV |
| **CLAHE** | Contrast Limited Adaptive Histogram Equalization - image enhancement technique |
| **Cooldown** | Minimum time between consecutive gesture detections |
| **FPS** | Frames Per Second - rate of video processing |
| **GUI** | Graphical User Interface |
| **Kalman Filter** | Algorithm for smoothing noisy measurements |
| **Landmark** | A specific point on the hand tracked by MediaPipe |
| **Latency** | Time delay from gesture to action |
| **Linear Regression** | Statistical method to fit a line to data points |
| **MediaPipe** | Google's ML framework for vision tasks |
| **MSE** | Mean Squared Error - measure of prediction accuracy |
| **OpenCV** | Open Source Computer Vision library |
| **Profile** | A set of gesture-to-shortcut mappings |
| **PyAutoGUI** | Python library for keyboard/mouse automation |
| **Queue** | Data structure for thread communication |
| **RGB** | Red-Green-Blue color format |
| **ROI** | Region of Interest - area where gestures are detected |
| **Static Gesture** | Hand pose without movement |
| **Dynamic Gesture** | Hand movement over time (e.g., swipe) |
| **Thread** | Independent execution path in a program |
| **Threshold** | Minimum value to trigger a condition |
| **Toast** | Temporary notification popup |
| **Trajectory** | Path of hand movement over time |

---

## Appendix G: MediaPipe Hand Landmarks Reference

```
                         HAND LANDMARK MAP

              Finger Tips: 4, 8, 12, 16, 20

                         8    12    16    20
                         │     │     │     │
                         │     │     │     │
                    4    7    11    15    19   DIP Joints
                    │    │     │     │     │
                    │    6    10    14    18   PIP Joints
                    │    │     │     │     │
                    3    5     9    13    17   MCP Joints
                    │    │     │     │     │
                    │    └─────┴─────┴─────┘
                    2          │
                    │          │
                    1          │
                    │          │
                    └──────────0                WRIST


        LANDMARK INDEX REFERENCE:

        ┌────────┬────────────────────────────────────┐
        │ Index  │ Description                        │
        ├────────┼────────────────────────────────────┤
        │   0    │ WRIST                              │
        ├────────┼────────────────────────────────────┤
        │   1    │ THUMB_CMC (base)                   │
        │   2    │ THUMB_MCP                          │
        │   3    │ THUMB_IP                           │
        │   4    │ THUMB_TIP                          │
        ├────────┼────────────────────────────────────┤
        │   5    │ INDEX_FINGER_MCP (knuckle)         │
        │   6    │ INDEX_FINGER_PIP                   │
        │   7    │ INDEX_FINGER_DIP                   │
        │   8    │ INDEX_FINGER_TIP                   │
        ├────────┼────────────────────────────────────┤
        │   9    │ MIDDLE_FINGER_MCP                  │
        │  10    │ MIDDLE_FINGER_PIP                  │
        │  11    │ MIDDLE_FINGER_DIP                  │
        │  12    │ MIDDLE_FINGER_TIP                  │
        ├────────┼────────────────────────────────────┤
        │  13    │ RING_FINGER_MCP                    │
        │  14    │ RING_FINGER_PIP                    │
        │  15    │ RING_FINGER_DIP                    │
        │  16    │ RING_FINGER_TIP                    │
        ├────────┼────────────────────────────────────┤
        │  17    │ PINKY_MCP                          │
        │  18    │ PINKY_PIP                          │
        │  19    │ PINKY_DIP                          │
        │  20    │ PINKY_TIP                          │
        └────────┴────────────────────────────────────┘

        Joint Types:
        - CMC: Carpometacarpal (thumb base)
        - MCP: Metacarpophalangeal (knuckle)
        - PIP: Proximal Interphalangeal (middle joint)
        - DIP: Distal Interphalangeal (joint near tip)
        - TIP: Fingertip
```

---

## Appendix H: Troubleshooting Guide

### H.1 Camera Issues

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| "No Camera Found" | Camera not connected | Check USB connection |
| | Camera in use by another app | Close other apps using camera |
| | Driver issue | Update camera drivers |
| Black screen | Camera privacy cover closed | Remove cover |
| | Low light | Improve lighting |
| | Wrong camera selected | Select correct camera in dropdown |
| Laggy video | CPU overloaded | Close other applications |
| | Low-end hardware | Reduce video resolution in config |

### H.2 Gesture Recognition Issues

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| Gestures not detected | Hand not in ROI | Move hand to green box |
| | Gesture not enabled | Enable in Settings |
| | Confidence too high | Lower detection confidence |
| | Poor lighting | Improve lighting or enable low-light mode |
| False detections | Confidence too low | Increase detection confidence |
| | Background interference | Use plain background |
| | Too fast movement | Perform gestures more slowly |
| Swipes not working | Movement too slow | Swipe faster |
| | Movement too curved | Keep movement straight |
| | Distance too short | Make larger swipe motion |

### H.3 Application Issues

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| App crashes on start | Missing dependencies | Run `pip install -r requirements.txt` |
| | Python version wrong | Use Python 3.11 |
| Settings not saving | Permission issue | Run as Administrator |
| | Disk full | Free up disk space |
| Shortcuts not working | Wrong profile active | Check profile in status |
| | Target app not focused | Click on target app first |
| | Shortcut format wrong | Check shortcut syntax |

### H.4 Performance Issues

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| Low FPS | CPU overloaded | Close other applications |
| | High resolution | Reduce VIDEO_WIDTH/HEIGHT |
| | Many smoothers | Reduce SMOOTHING_BUFFER_SIZE |
| High latency | Queue backup | Restart application |
| | Background processes | Close unnecessary programs |
| Memory growing | Memory leak | Restart after long sessions |

---

## Appendix I: Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Initial | First release with core features |
| | | - 7 static gestures |
| | | - 2 dynamic gestures (swipe) |
| | | - 3 profiles (DEFAULT, POWERPOINT, CHROME) |
| | | - Settings UI |
| | | - Overlay mode |
| | | - Low-light enhancement |
| | | - Position smoothing |
| | | - Audio feedback |

---

## Appendix J: License Information

### Project License

This project is developed for educational purposes as part of a thesis/capstone project.

### Third-Party Licenses

| Library | License | URL |
|---------|---------|-----|
| MediaPipe | Apache 2.0 | https://github.com/google/mediapipe/blob/master/LICENSE |
| OpenCV | Apache 2.0 | https://opencv.org/license/ |
| NumPy | BSD 3-Clause | https://numpy.org/doc/stable/license.html |
| PyAutoGUI | BSD 3-Clause | https://github.com/asweigart/pyautogui/blob/master/LICENSE.txt |
| CustomTkinter | MIT | https://github.com/TomSchimansky/CustomTkinter/blob/master/LICENSE |
| Pillow | HPND | https://github.com/python-pillow/Pillow/blob/main/LICENSE |

---

*[End of References and Appendices]*

---
