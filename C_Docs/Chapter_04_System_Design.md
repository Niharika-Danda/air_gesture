# CHAPTER 4: SYSTEM DESIGN

---

## 4.1 Introduction

This chapter presents the architectural design of the Air Gesture Shortcut Controller. We will examine how the system is structured, how different components interact, and the design decisions that make the system efficient and maintainable.

**Simple Explanation:** *If Chapter 3 was about "what" we're building, Chapter 4 is about "how" we're building it. It's like having a blueprint for a house - showing where each room goes and how they connect!*

---

## 4.2 Design Goals and Principles

### 4.2.1 Design Goals

| Goal | Description |
|------|-------------|
| **Real-time Performance** | Process gestures fast enough for immediate response |
| **Modularity** | Separate concerns into independent, replaceable components |
| **Extensibility** | Easy to add new gestures or features |
| **Usability** | Intuitive interface requiring minimal learning |
| **Reliability** | Stable operation without crashes or freezes |
| **Maintainability** | Code that is easy to understand and modify |

### 4.2.2 Design Principles Applied

#### Separation of Concerns
Each module handles one specific responsibility:
- Camera capture is separate from gesture recognition
- UI is separate from processing logic
- Configuration is separate from runtime behavior

**Simple Explanation:** *Imagine a restaurant kitchen. One chef chops vegetables, another cooks, another plates the food. Each person focuses on their job. Our code works the same way - each part does one thing well!*

#### Producer-Consumer Pattern
The vision thread produces frames, the main thread consumes them:
```
VisionThread (Producer) ──▶ Queue ──▶ Main Thread (Consumer)
```

#### Observer Pattern
UI components observe and react to state changes without tight coupling.

#### Single Responsibility Principle
Each class has one primary purpose:
- `GestureProcessor` → Recognizes gestures
- `SwipeDetector` → Detects swipes specifically
- `UIManager` → Handles display and user interaction

---

## 4.3 System Architecture

### 4.3.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AIR GESTURE SHORTCUT CONTROLLER                      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         PRESENTATION LAYER                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │   │
│  │  │ Main Window │  │  Settings   │  │   Toast     │  │  Overlay  │  │   │
│  │  │   (GUI)     │  │   Dialog    │  │  Overlay    │  │   Mode    │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         APPLICATION LAYER                           │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │   │
│  │  │ GestureController│  │  VisionThread   │  │  ShortcutExecutor  │ │   │
│  │  │      App        │  │   (Background)  │  │    (PyAutoGUI)     │ │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         PROCESSING LAYER                            │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐   │   │
│  │  │   Gesture     │  │    Swipe      │  │     Position          │   │   │
│  │  │   Engine      │  │   Detector    │  │     Smoother          │   │   │
│  │  └───────────────┘  └───────────────┘  └───────────────────────┘   │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐   │   │
│  │  │   Gesture     │  │    Audio      │  │    Auto-Calibrator    │   │   │
│  │  │   Recorder    │  │   Feedback    │  │                       │   │   │
│  │  └───────────────┘  └───────────────┘  └───────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                           DATA LAYER                                │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐   │   │
│  │  │    Config     │  │  config.json  │  │  custom_gestures.json │   │   │
│  │  │   Module      │  │    (File)     │  │       (File)          │   │   │
│  │  └───────────────┘  └───────────────┘  └───────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         EXTERNAL LAYER                              │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐   │   │
│  │  │    Webcam     │  │   MediaPipe   │  │    Windows OS         │   │   │
│  │  │   (OpenCV)    │  │    (Google)   │  │  (Keyboard Events)    │   │   │
│  │  └───────────────┘  └───────────────┘  └───────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3.2 Layer Descriptions

| Layer | Purpose | Components |
|-------|---------|------------|
| **Presentation** | User interface and visual feedback | Main window, Settings dialog, Toast notifications, Overlay mode |
| **Application** | Core application logic and coordination | GestureControllerApp, VisionThread, Shortcut execution |
| **Processing** | Gesture detection algorithms | GestureEngine, SwipeDetector, PositionSmoother, AudioFeedback |
| **Data** | Configuration and persistence | Config module, JSON files |
| **External** | Third-party libraries and hardware | OpenCV, MediaPipe, Windows API |

---

## 4.4 Threading Architecture

### 4.4.1 Why Threading?

**Simple Explanation:** *Imagine you're cooking and watching TV at the same time. If you could only do one thing at a time, you'd have to pause TV, stir the pot, pause, watch TV, pause, check the pot... very annoying! Threading lets our program do multiple things at once - process video AND show it on screen smoothly!*

Processing video is computationally expensive. If we did everything in one thread:
1. Capture frame (takes time)
2. Detect hand (takes time)
3. Recognize gesture (takes time)
4. Update UI (blocked while waiting!)

Result: **Laggy, unresponsive interface**

With threading:
- **Vision Thread**: Captures and processes frames continuously
- **Main Thread**: Updates UI smoothly, handles user input

Result: **Smooth, responsive interface**

### 4.4.2 Thread Communication Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│    MAIN THREAD                              VISION THREAD               │
│    (UI + Logic)                             (Camera + Processing)       │
│                                                                         │
│    ┌─────────────┐                          ┌─────────────────┐        │
│    │ Tkinter     │                          │  cv2.VideoCapture│        │
│    │ Event Loop  │                          │                 │        │
│    └──────┬──────┘                          └────────┬────────┘        │
│           │                                          │                  │
│           │  ┌──────────────────────────────────┐   │                  │
│           │  │        RESULT QUEUE              │   │                  │
│           │  │        (maxsize=2)               │   │                  │
│           │  │                                  │   │                  │
│           │  │  ┌────────────────────────────┐ │   │                  │
│           └──┼──│ (gesture, frame, pointer,  │◀┼───┘                  │
│              │  │  landmarks, timestamp)     │ │                       │
│              │  └────────────────────────────┘ │                       │
│              │                                  │                       │
│              └──────────────────────────────────┘                       │
│                                                                         │
│    update() polls queue ──────────────────▶ run() puts results         │
│    every 10ms                               continuously                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.4.3 Queue Design Decisions

| Decision | Value | Reason |
|----------|-------|--------|
| Queue maxsize | 2 | Prevents memory buildup, ensures freshest frames |
| Poll interval | 10ms | Fast enough for smooth UI, not wasteful |
| Drop policy | Drop oldest | Always process most recent frame |

**Simple Explanation:** *The queue is like a small mailbox between the two threads. The vision thread puts processed frames in the mailbox. The main thread takes them out. If the mailbox is full, we throw away old mail to make room for new mail - because we only care about the latest information!*

### 4.4.4 Thread Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION STARTUP                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Main Thread    │
                    │  Initializes    │
                    │  - Create UI    │
                    │  - Load Config  │
                    └────────┬────────┘
                             │
              User clicks "Start Camera"
                             │
                             ▼
                    ┌─────────────────┐
                    │ Create Vision   │
                    │ Thread          │
                    └────────┬────────┘
                             │
           ┌─────────────────┴─────────────────┐
           │                                   │
           ▼                                   ▼
┌─────────────────────┐           ┌─────────────────────┐
│    MAIN THREAD      │           │   VISION THREAD     │
│                     │           │                     │
│  while running:     │           │  while not stopped: │
│    poll queue       │◀──────────│    capture frame    │
│    update UI        │   Queue   │    process frame    │
│    execute shortcuts│           │    put in queue     │
│    check window     │           │                     │
└─────────────────────┘           └─────────────────────┘
           │                                   │
           │      User clicks "Stop"           │
           │                                   │
           ▼                                   ▼
┌─────────────────────┐           ┌─────────────────────┐
│  Set stop flag      │──────────▶│  Stop event set     │
│                     │           │  Release camera     │
│                     │           │  Close MediaPipe    │
└─────────────────────┘           └─────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Thread joins   │
                    │  (waits for     │
                    │   completion)   │
                    └─────────────────┘
```

---

## 4.5 Module Design

### 4.5.1 Module Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SOURCE FILES                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  src/                                                                   │
│  │                                                                      │
│  ├── main.py ─────────────────┐                                        │
│  │   • Entry point            │                                        │
│  │   • GestureControllerApp   │                                        │
│  │   • VisionThread           │◀─── Main orchestrator                  │
│  │                            │                                        │
│  ├── gesture_engine.py ───────┤                                        │
│  │   • GestureProcessor       │◀─── Core gesture recognition           │
│  │   • MediaPipe integration  │                                        │
│  │   • Static gesture logic   │                                        │
│  │                            │                                        │
│  ├── swipe_engine.py ─────────┤                                        │
│  │   • SwipeDetector          │◀─── Dynamic gesture detection          │
│  │   • Trajectory analysis    │                                        │
│  │   • Linear regression      │                                        │
│  │                            │                                        │
│  ├── position_smoother.py ────┤                                        │
│  │   • PositionSmoother2D     │◀─── Jitter reduction                   │
│  │   • LandmarkSmoother       │                                        │
│  │   • PointerSmoother        │                                        │
│  │                            │                                        │
│  ├── ui_manager.py ───────────┤                                        │
│  │   • AppUIManager           │◀─── User interface                     │
│  │   • ToastOverlay           │                                        │
│  │   • Settings window        │                                        │
│  │                            │                                        │
│  ├── config.py ───────────────┤                                        │
│  │   • Configuration constants│◀─── Settings & profiles                │
│  │   • save_config()          │                                        │
│  │   • load_config()          │                                        │
│  │                            │                                        │
│  ├── audio_feedback.py ───────┤                                        │
│  │   • AudioFeedback          │◀─── Sound effects                      │
│  │                            │                                        │
│  ├── gesture_recorder.py ─────┤                                        │
│  │   • GestureRecorder        │◀─── Custom gesture storage             │
│  │                            │                                        │
│  └── calibration.py ──────────┤                                        │
│      • AutoCalibrator         │◀─── Camera & lighting setup            │
│                               │                                        │
└───────────────────────────────┴─────────────────────────────────────────┘
```

### 4.5.2 Module: main.py

**Purpose:** Application entry point and main controller

**Classes:**

#### Class: VisionThread

```
┌─────────────────────────────────────────────────────────────────┐
│                        VisionThread                             │
├─────────────────────────────────────────────────────────────────┤
│ Attributes:                                                     │
│   - camera_index: int          # Which camera to use            │
│   - result_queue: Queue        # Output queue for results       │
│   - stop_event: Event          # Signal to stop thread          │
│   - gesture_processor: obj     # GestureProcessor instance      │
│   - cap: VideoCapture          # OpenCV camera object           │
│   - frame_counter: int         # Counts processed frames        │
├─────────────────────────────────────────────────────────────────┤
│ Methods:                                                        │
│   + run()                      # Main thread loop               │
│   + stop()                     # Signal thread to stop          │
├─────────────────────────────────────────────────────────────────┤
│ Responsibilities:                                               │
│   • Capture frames from camera                                  │
│   • Apply low-light enhancement when needed                     │
│   • Process frames through GestureProcessor                     │
│   • Put results in queue for main thread                        │
└─────────────────────────────────────────────────────────────────┘
```

**Simple Explanation:** *VisionThread is like a dedicated worker who only does one job: watching the camera and figuring out what gestures are being made. It works in the background so the main program can focus on other things.*

#### Class: GestureControllerApp

```
┌─────────────────────────────────────────────────────────────────┐
│                     GestureControllerApp                        │
├─────────────────────────────────────────────────────────────────┤
│ Attributes:                                                     │
│   - root: CTk                  # Main window                    │
│   - is_running: bool           # Camera running state           │
│   - last_gesture: str          # Previous gesture (debounce)    │
│   - last_gesture_time: float   # Timestamp of last gesture      │
│   - current_profile_name: str  # Active profile (DEFAULT, etc)  │
│   - result_queue: Queue        # Shared queue with VisionThread │
│   - vision_thread: Thread      # Background processing thread   │
│   - ui_manager: AppUIManager   # UI component manager           │
│   - audio: AudioFeedback       # Sound effect player            │
├─────────────────────────────────────────────────────────────────┤
│ Methods:                                                        │
│   + __init__(root)             # Initialize application         │
│   + detect_cameras()           # Find available cameras         │
│   + change_camera(index)       # Switch to different camera     │
│   + start()                    # Begin gesture recognition      │
│   + stop()                     # Stop gesture recognition       │
│   + update()                   # Main UI update loop            │
│   + _handle_logic(gesture...)  # Process detected gestures      │
│   + _update_app_state()        # Check window, switch profiles  │
│   + get_active_window_title()  # Get foreground window name     │
│   + execute_shortcut(gesture)  # Send keyboard command          │
│   + reload_configuration()     # Apply new settings             │
└─────────────────────────────────────────────────────────────────┘
```

### 4.5.3 Module: gesture_engine.py

**Purpose:** Hand detection and static gesture recognition

#### Class: GestureProcessor

```
┌─────────────────────────────────────────────────────────────────┐
│                      GestureProcessor                           │
├─────────────────────────────────────────────────────────────────┤
│ Attributes:                                                     │
│   - hands: MediaPipe Hands     # Hand detection model           │
│   - landmarks: list            # Current frame landmarks        │
│   - filtered_landmarks: list   # Smoothed landmarks             │
│   - swipe_detector: obj        # SwipeDetector instance         │
│   - gesture_buffer: deque      # For temporal voting            │
│   - landmark_smoother: obj     # LandmarkSmoother instance      │
│   - pointer_smoother: obj      # PointerSmoother instance       │
│   - recorder: GestureRecorder  # Custom gesture matching        │
├─────────────────────────────────────────────────────────────────┤
│ Methods:                                                        │
│   + process_frame(frame)       # Main processing pipeline       │
│   + _recognize_gesture()       # Static gesture classification  │
│   + _is_ok_sign()              # OK sign specific check         │
│   + close()                    # Release resources              │
├─────────────────────────────────────────────────────────────────┤
│ Processing Pipeline:                                            │
│   1. Flip frame horizontally (mirror effect)                    │
│   2. Apply low-light enhancement if enabled                     │
│   3. Run MediaPipe hand detection                               │
│   4. Smooth landmark positions                                  │
│   5. Calculate hand centroid                                    │
│   6. Check for swipe gesture                                    │
│   7. If no swipe, check static gesture (if in ROI)              │
│   8. Apply temporal voting for confirmation                     │
│   9. Return gesture, frame, pointer info, landmarks             │
└─────────────────────────────────────────────────────────────────┘
```

**Gesture Recognition Flow:**

```
                    ┌─────────────────┐
                    │  Input Frame    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Flip & Enhance  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ MediaPipe Hands │
                    │   Detection     │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │ Hand Found?                 │
              └──────────────┬──────────────┘
                    No       │      Yes
                    │        │        │
                    ▼        │        ▼
           ┌────────────┐    │    ┌─────────────────┐
           │ Clear      │    │    │ Extract 21      │
           │ Buffers    │    │    │ Landmarks       │
           └────────────┘    │    └────────┬────────┘
                             │             │
                             │             ▼
                             │    ┌─────────────────┐
                             │    │ Smooth Positions│
                             │    └────────┬────────┘
                             │             │
                             │             ▼
                             │    ┌─────────────────┐
                             │    │ Calculate       │
                             │    │ Centroid        │
                             │    └────────┬────────┘
                             │             │
                             │    ┌────────┴────────┐
                             │    │                 │
                             │    ▼                 ▼
                             │ ┌──────────┐   ┌──────────┐
                             │ │  Check   │   │  Check   │
                             │ │  Swipe   │   │  Static  │
                             │ └────┬─────┘   └────┬─────┘
                             │      │              │
                             │      └──────┬───────┘
                             │             │
                             │             ▼
                             │    ┌─────────────────┐
                             │    │ Return Result   │
                             │    └─────────────────┘
                             │
                             ▼
                      ┌────────────┐
                      │  Return    │
                      │  UNKNOWN   │
                      └────────────┘
```

### 4.5.4 Module: swipe_engine.py

**Purpose:** Detect horizontal swipe gestures using trajectory analysis

#### Class: SwipeDetector

```
┌─────────────────────────────────────────────────────────────────┐
│                       SwipeDetector                             │
├─────────────────────────────────────────────────────────────────┤
│ Attributes:                                                     │
│   - history: deque             # Recent positions (x, y, time)  │
│   - min_dist_left: float       # Min distance for left swipe    │
│   - min_dist_right: float      # Min distance for right swipe   │
│   - min_velocity: float        # Min speed required             │
│   - cooldown: float            # Seconds between swipes         │
│   - last_swipe_time: float     # Timestamp of last swipe        │
│   - MAX_SLOPE: float           # Max allowed trajectory slope   │
│   - MAX_MSE: float             # Max mean squared error         │
├─────────────────────────────────────────────────────────────────┤
│ Methods:                                                        │
│   + process(centroid, timestamp) # Analyze trajectory           │
├─────────────────────────────────────────────────────────────────┤
│ Detection Algorithm:                                            │
│   1. Add current position to history                            │
│   2. Check cooldown (prevent rapid re-trigger)                  │
│   3. Calculate distance traveled                                │
│   4. Check velocity (must be fast enough)                       │
│   5. Check vertical variance (must be horizontal)               │
│   6. Fit line using linear regression                           │
│   7. Check slope (not too diagonal)                             │
│   8. Check MSE (path must be straight)                          │
│   9. If all pass → SWIPE detected!                              │
└─────────────────────────────────────────────────────────────────┘
```

**Swipe Detection Visualization:**

```
Valid Swipe (Accepted):
┌─────────────────────────────────────────────────┐
│                                                 │
│    ●───●───●───●───●───●───●───●▶              │
│    Start                      End               │
│                                                 │
│    ✓ Horizontal movement                        │
│    ✓ Straight path                              │
│    ✓ Fast enough                                │
│                                                 │
└─────────────────────────────────────────────────┘

Invalid Swipe (Rejected - Too Wavy):
┌─────────────────────────────────────────────────┐
│                  ●                              │
│    ●───●    ●───   ───●                        │
│          ●──        ───●───●                   │
│                                                 │
│    ✗ Path is not straight (high MSE)           │
│                                                 │
└─────────────────────────────────────────────────┘

Invalid Swipe (Rejected - Too Diagonal):
┌─────────────────────────────────────────────────┐
│                               ●                 │
│                           ●                     │
│                       ●                         │
│                   ●                             │
│               ●                                 │
│           ●                                     │
│       ●                                         │
│   ●                                             │
│                                                 │
│    ✗ Slope too steep                            │
│                                                 │
└─────────────────────────────────────────────────┘

Invalid Swipe (Rejected - Too Slow):
┌─────────────────────────────────────────────────┐
│                                                 │
│    ●·····●·····●·····●                         │
│                                                 │
│    ✗ Movement too slow (low velocity)          │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 4.5.5 Module: position_smoother.py

**Purpose:** Reduce jitter in hand tracking for stable interaction

**Simple Explanation:** *When you hold your hand still, the camera might see it wiggling a tiny bit because of small errors. The smoother is like a stabilizer - it remembers where your hand was and guesses where it should be, making the tracking look smooth instead of shaky!*

#### Class: PositionSmoother2D

```
┌─────────────────────────────────────────────────────────────────┐
│                     PositionSmoother2D                          │
├─────────────────────────────────────────────────────────────────┤
│ Attributes:                                                     │
│   - state: array [x, y, vx, vy] # Position and velocity         │
│   - F: matrix                   # State transition matrix       │
│   - H: matrix                   # Measurement matrix            │
│   - Q: matrix                   # Process noise covariance      │
│   - R: matrix                   # Measurement noise covariance  │
│   - P: matrix                   # Estimation error covariance   │
├─────────────────────────────────────────────────────────────────┤
│ Methods:                                                        │
│   + reset()                     # Reset to initial state        │
│   + predict()                   # Predict next position         │
│   + update(measurement)         # Correct with measurement      │
│   + get_velocity()              # Get current velocity estimate │
└─────────────────────────────────────────────────────────────────┘
```

**Kalman Filter Concept (Simplified):**

```
                         ┌─────────────────┐
                         │    PREDICT      │
                         │                 │
    Previous ───────────▶│ "Where should   │──────▶ Predicted
    State                │  the hand be?"  │        Position
                         │                 │
                         └─────────────────┘
                                 │
                                 ▼
                         ┌─────────────────┐
                         │    UPDATE       │
                         │                 │
    Actual    ──────────▶│ "Combine guess  │──────▶ Smoothed
    Measurement          │  with reality"  │        Position
    (from camera)        │                 │
                         └─────────────────┘
```

**Simple Explanation:**
1. *PREDICT: Based on where the hand was and how fast it was moving, guess where it should be now*
2. *UPDATE: Look at where the camera actually sees the hand*
3. *COMBINE: The true position is somewhere between our guess and what the camera sees*
4. *Result: Smooth movement without sudden jumps!*

### 4.5.6 Module: ui_manager.py

**Purpose:** Manage all visual interface components

#### Class: AppUIManager

```
┌─────────────────────────────────────────────────────────────────┐
│                       AppUIManager                              │
├─────────────────────────────────────────────────────────────────┤
│ Attributes:                                                     │
│   - root: CTk                  # Main window reference          │
│   - canvas: Canvas             # Video display area             │
│   - start_button: CTkButton    # Start camera button            │
│   - stop_button: CTkButton     # Stop camera button             │
│   - settings_button: CTkButton # Open settings button           │
│   - status_label: CTkLabel     # Status text display            │
│   - toast: ToastOverlay        # Gesture notification popup     │
│   - is_overlay: bool           # Overlay mode state             │
│   - preview_window: Toplevel   # Floating preview window        │
├─────────────────────────────────────────────────────────────────┤
│ Methods:                                                        │
│   + update_frame(frame)        # Display camera frame           │
│   + update_status(text)        # Update status label            │
│   + update_performance(...)    # Update FPS, detection status   │
│   + enter_overlay_mode()       # Switch to compact mode         │
│   + exit_overlay_mode()        # Return to full mode            │
│   + open_settings()            # Show settings dialog           │
│   + show_feedback(text)        # Show gesture notification      │
│   + _draw_overlay_cv2(frame)   # Draw FPS and status on frame   │
└─────────────────────────────────────────────────────────────────┘
```

**UI Layout Design:**

```
┌─────────────────────────────────────────────────────────────────┐
│  Air Gesture Shortcut Controller                          _ □ X │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                                                           │ │
│  │                                                           │ │
│  │                    VIDEO CANVAS                           │ │
│  │                                                           │ │
│  │    ┌──────────────┐                                       │ │
│  │    │ FPS: 30  ●   │  ◄── Performance overlay              │ │
│  │    └──────────────┘                                       │ │
│  │                                                           │ │
│  │                     ┌─────────────┐                       │ │
│  │                     │  Sign Zone  │ ◄── ROI Box           │ │
│  │                     │             │                       │ │
│  │                     └─────────────┘                       │ │
│  │                                                           │ │
│  │                  ┌─────────────────┐                      │ │
│  │                  │ SWIPE_RIGHT ▶️   │ ◄── Toast           │ │
│  │                  └─────────────────┘                      │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                                                           │ │
│  │  Status: Running    [Camera 0 ▼]  [Start] [Stop] [⚙️]     │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

OVERLAY MODE (Compact Preview):
┌─────────────────────────────┐
│  Camera Preview         [X] │
├─────────────────────────────┤
│ ┌─────────────────────────┐ │
│ │                         │ │
│ │    Compact Video Feed   │ │
│ │                         │ │
│ │    FPS: 30  ●           │ │
│ │                         │ │
│ └─────────────────────────┘ │
└─────────────────────────────┘
   (Always on top, draggable)
```

### 4.5.7 Module: config.py

**Purpose:** Store and manage all configuration settings

```
┌─────────────────────────────────────────────────────────────────┐
│                     Configuration System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Constants (Hardcoded):                                         │
│    CAMERA_INDEX = 0                                             │
│    VIDEO_WIDTH = 1280                                           │
│    VIDEO_HEIGHT = 720                                           │
│    WINDOW_TITLE = "Air Gesture Shortcut Controller"             │
│                                                                 │
│  Settings (User-adjustable):                                    │
│    MIN_DETECTION_CONFIDENCE = 0.5                               │
│    MIN_TRACKING_CONFIDENCE = 0.4                                │
│    GESTURE_COOLDOWN = 0.3                                       │
│    ENABLE_MOUSE = False                                         │
│    ENABLED_SIGNS = []                                           │
│                                                                 │
│  Profile Mappings:                                              │
│    PROFILES = {                                                 │
│      'DEFAULT': { 'SWIPE_RIGHT': ['right'], ... },              │
│      'POWERPOINT': { ... },                                     │
│      'CHROME': { ... }                                          │
│    }                                                            │
│                                                                 │
│  Window Mapping:                                                │
│    WINDOW_PROFILE_MAP = {                                       │
│      'PowerPoint': 'POWERPOINT',                                │
│      'Chrome': 'CHROME',                                        │
│      ...                                                        │
│    }                                                            │
│                                                                 │
│  Functions:                                                     │
│    save_config() → writes to config.json                        │
│    load_config() → reads from config.json                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.5.8 Module: audio_feedback.py

**Purpose:** Provide audio cues when gestures are recognized

```
┌─────────────────────────────────────────────────────────────────┐
│                      AudioFeedback                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Sound Types:                                                   │
│                                                                 │
│  ┌─────────────────┐                                            │
│  │  Swipe Sound    │  1200 Hz for 100ms                        │
│  │  (High beep)    │  ♪ Quick, sharp                           │
│  └─────────────────┘                                            │
│                                                                 │
│  ┌─────────────────┐                                            │
│  │  Static Gesture │  800 Hz → 1200 Hz                         │
│  │  (Two-tone)     │  ♪ ♪ Confirmation                         │
│  └─────────────────┘                                            │
│                                                                 │
│  ┌─────────────────┐                                            │
│  │  Error Sound    │  300 Hz for 300ms                         │
│  │  (Low tone)     │  ♫ Warning                                │
│  └─────────────────┘                                            │
│                                                                 │
│  Implementation:                                                │
│    - Uses Windows winsound API                                  │
│    - Each sound plays in separate thread (non-blocking)         │
│    - Can be enabled/disabled via settings                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4.6 Class Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CLASS DIAGRAM                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐         ┌─────────────────────┐
│ GestureControllerApp│◆───────▶│    AppUIManager     │
├─────────────────────┤         ├─────────────────────┤
│ - root              │         │ - root              │
│ - is_running        │         │ - canvas            │
│ - vision_thread     │    1    │ - toast             │
│ - result_queue      │─────────│ - is_overlay        │
│ - ui_manager        │         │ - settings_window   │
│ - current_profile   │         ├─────────────────────┤
│ - audio             │         │ + update_frame()    │
├─────────────────────┤         │ + update_status()   │
│ + start()           │         │ + open_settings()   │
│ + stop()            │         │ + enter_overlay()   │
│ + update()          │         └─────────────────────┘
│ + execute_shortcut()│
└─────────┬───────────┘
          │
          │ creates
          ▼
┌─────────────────────┐         ┌─────────────────────┐
│    VisionThread     │◆───────▶│  GestureProcessor   │
├─────────────────────┤         ├─────────────────────┤
│ - camera_index      │         │ - hands (MediaPipe) │
│ - result_queue      │    1    │ - landmarks         │
│ - stop_event        │─────────│ - swipe_detector    │
│ - gesture_processor │         │ - landmark_smoother │
│ - cap (VideoCapture)│         │ - gesture_buffer    │
├─────────────────────┤         ├─────────────────────┤
│ + run()             │         │ + process_frame()   │
│ + stop()            │         │ + _recognize_gesture│
└─────────────────────┘         │ + close()           │
                                └─────────┬───────────┘
                                          │
                     ┌────────────────────┼────────────────────┐
                     │                    │                    │
                     ▼                    ▼                    ▼
          ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
          │  SwipeDetector  │  │ LandmarkSmoother │  │ GestureRecorder │
          ├─────────────────┤  ├─────────────────┤  ├─────────────────┤
          │ - history       │  │ - smoothers[]   │  │ - gestures{}    │
          │ - min_velocity  │  │ - num_landmarks │  ├─────────────────┤
          │ - cooldown      │  ├─────────────────┤  │ + save_gesture()│
          ├─────────────────┤  │ + update()      │  │ + find_match()  │
          │ + process()     │  │ + reset()       │  └─────────────────┘
          └─────────────────┘  └────────┬────────┘
                                        │
                                        │ contains 21
                                        ▼
                               ┌─────────────────┐
                               │PositionSmoother2D│
                               ├─────────────────┤
                               │ - state [x,y,vx,vy]
                               │ - F, H, Q, R, P │
                               ├─────────────────┤
                               │ + predict()     │
                               │ + update()      │
                               └─────────────────┘

┌─────────────────────┐
│   AudioFeedback     │◀─────────── Used by GestureControllerApp
├─────────────────────┤
│ - enabled           │
├─────────────────────┤
│ + play_swipe_sound()│
│ + play_static_sound()│
│ + play_error_sound()│
└─────────────────────┘

Key:
  ──────▶  Uses / References
  ◆──────▶  Composition (owns)
  - attribute
  + method()
```

---

## 4.7 Sequence Diagrams

### 4.7.1 Startup Sequence

```
┌──────┐     ┌─────────────┐    ┌───────────┐    ┌────────────┐
│ User │     │   main.py   │    │ UIManager │    │   Config   │
└──┬───┘     └──────┬──────┘    └─────┬─────┘    └──────┬─────┘
   │                │                  │                 │
   │ Run program    │                  │                 │
   │───────────────▶│                  │                 │
   │                │                  │                 │
   │                │  load_config()   │                 │
   │                │─────────────────────────────────▶│
   │                │                  │                 │
   │                │◀─────────────────────────────────│
   │                │                  │                 │
   │                │ Create UI        │                 │
   │                │─────────────────▶│                 │
   │                │                  │                 │
   │                │ detect_cameras() │                 │
   │                │─────────────────▶│                 │
   │                │                  │                 │
   │                │◀─────────────────│                 │
   │                │                  │                 │
   │◀───────────────│ Window Displayed │                 │
   │                │                  │                 │
```

### 4.7.2 Gesture Recognition Sequence

```
┌──────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  ┌──────────┐
│ User │  │VisionThread │  │GestureProcsr│  │SwipeDetect │  │MainThread│
└──┬───┘  └──────┬──────┘  └──────┬──────┘  └──────┬─────┘  └────┬─────┘
   │             │                │                │              │
   │ Swipe Right │                │                │              │
   │────────────▶│                │                │              │
   │             │                │                │              │
   │             │ capture frame  │                │              │
   │             │───────────────▶│                │              │
   │             │                │                │              │
   │             │                │ process()      │              │
   │             │                │───────────────▶│              │
   │             │                │                │              │
   │             │                │ "SWIPE_RIGHT"  │              │
   │             │                │◀───────────────│              │
   │             │                │                │              │
   │             │ put in queue   │                │              │
   │             │──────────────────────────────────────────────▶│
   │             │                │                │              │
   │             │                │                │              │ poll queue
   │             │                │                │              │──────┐
   │             │                │                │              │      │
   │             │                │                │              │◀─────┘
   │             │                │                │              │
   │             │                │                │              │ execute_shortcut()
   │             │                │                │              │──────┐
   │             │                │                │              │      │ pyautogui.press('right')
   │             │                │                │              │◀─────┘
   │             │                │                │              │
   │             │                │                │              │ update UI
   │◀────────────────────────────────────────────────────────────│
   │ See feedback│                │                │              │
   │             │                │                │              │
```

### 4.7.3 Settings Change Sequence

```
┌──────┐     ┌───────────┐    ┌────────────┐    ┌──────────────────┐
│ User │     │ UIManager │    │   Config   │    │GestureControllerApp│
└──┬───┘     └─────┬─────┘    └──────┬─────┘    └─────────┬────────┘
   │               │                 │                    │
   │ Click ⚙️       │                 │                    │
   │──────────────▶│                 │                    │
   │               │                 │                    │
   │               │ open_settings() │                    │
   │               │─────────────────│                    │
   │               │                 │                    │
   │◀──────────────│ Settings window │                    │
   │               │                 │                    │
   │ Adjust slider │                 │                    │
   │──────────────▶│                 │                    │
   │               │                 │                    │
   │ Click Save    │                 │                    │
   │──────────────▶│                 │                    │
   │               │                 │                    │
   │               │ Update values   │                    │
   │               │────────────────▶│                    │
   │               │                 │                    │
   │               │ save_config()   │                    │
   │               │────────────────▶│                    │
   │               │                 │                    │
   │               │ reload_configuration()               │
   │               │────────────────────────────────────▶│
   │               │                 │                    │
   │               │                 │     Restart VisionThread
   │               │                 │                    │───┐
   │               │                 │                    │   │
   │               │                 │                    │◀──┘
   │               │                 │                    │
   │◀──────────────│ Settings saved  │                    │
   │               │                 │                    │
```

---

## 4.8 Static Gesture Recognition Design

### 4.8.1 Geometry-Based Recognition

**Design Decision:** Use landmark positions and distances rather than machine learning for static gesture recognition.

**Why Geometry-Based?**
- No training data required
- Explainable decisions (can debug why a gesture wasn't recognized)
- Fast computation (simple math)
- Works reliably for predefined gesture set

### 4.8.2 Finger State Detection

```
┌─────────────────────────────────────────────────────────────────┐
│                    FINGER EXTENDED CHECK                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  For Index Finger:                                              │
│                                                                 │
│     TIP (8)                                                     │
│       │                                                         │
│       │  d_tip = distance(TIP → WRIST)                         │
│       │                                                         │
│     PIP (6)                                                     │
│       │                                                         │
│       │  d_pip = distance(PIP → WRIST)                         │
│       │                                                         │
│    WRIST (0)                                                    │
│                                                                 │
│  RULE: If d_tip > d_pip → Finger is EXTENDED                   │
│        If d_tip < d_pip → Finger is CURLED                     │
│                                                                 │
│  This works regardless of hand rotation!                        │
│                                                                 │
└───────────���─────────────────────────────────────────────────────┘
```

**Simple Explanation:** *To check if a finger is extended (pointing out) or curled (bent in), we measure how far the fingertip is from the wrist compared to the middle knuckle. If the tip is farther, the finger is extended. This works no matter which way the hand is rotated!*

### 4.8.3 Gesture Decision Table

| Gesture | Thumb | Index | Middle | Ring | Pinky | Extra Check |
|---------|-------|-------|--------|------|-------|-------------|
| THUMBS_UP | Extended | Curled | Curled | Curled | Curled | Thumb tip above thumb IP |
| THUMBS_DOWN | Extended | Curled | Curled | Curled | Curled | Thumb tip below thumb IP |
| OPEN_PALM | Extended | Extended | Extended | Extended | Extended | - |
| FIST | Curled | Curled | Curled | Curled | Curled | - |
| V_SIGN | Curled | Extended | Extended | Curled | Curled | - |
| INDEX_POINTING | Curled | Extended | Curled | Curled | Curled | - |
| SPIDERMAN | Extended | Extended | Curled | Curled | Extended | - |
| OK_SIGN | - | - | Extended | Extended | Extended | Thumb-Index distance < 0.08 |

### 4.8.4 Region of Interest (ROI) Design

```
┌─────────────────────────────────────────────────────────────────┐
│                        CAMERA FRAME                             │
│                                                                 │
│   x=0                                               x=1.0       │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                                                         │  │
│   │     This area is IGNORED for static gestures            │  │
│   │     (Only swipes work here)                             │  │
│   │                                                         │  │
│ y=0.7├─────────────────────────────────────────────────────────│  │
│   │           │                               │             │  │
│   │           │     SIGN ZONE (ROI)           │             │  │
│   │           │                               │             │  │
│   │           │   Static gestures only        │             │  │
│   │           │   recognized HERE             │             │  │
│   │           │                               │             │  │
│   │           │   (Green box when hand        │             │  │
│   │           │    is inside)                 │             │  │
│   │           │                               │             │  │
│ y=1.0└───────────┴───────────────────────────────┴─────────────┘  │
│               x=0.35                         x=0.65             │
│                                                                 │
│   ROI Config: x_min=0.35, x_max=0.65, y_min=0.7, y_max=1.0    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Why ROI?**
- Prevents accidental gesture detection during normal hand movement
- User must intentionally place hand in zone
- Reduces false positives significantly

---

## 4.9 Data Storage Design

### 4.9.1 Configuration File (config.json)

```json
{
    "MIN_DETECTION_CONFIDENCE": 0.5,
    "GESTURE_COOLDOWN": 0.3,
    "ENABLE_MOUSE": false,
    "ENABLED_SIGNS": ["THUMBS_UP", "OPEN_PALM"],
    "PROFILES": {
        "DEFAULT": {
            "SWIPE_RIGHT": ["right"],
            "SWIPE_LEFT": ["left"],
            "THUMBS_UP": ["right"],
            "OPEN_PALM": ["f5"]
        },
        "POWERPOINT": {
            "SWIPE_RIGHT": ["right"],
            "SWIPE_LEFT": ["left"],
            "V_SIGN": ["b"],
            "OK_SIGN": ["home"]
        },
        "CHROME": {
            "THUMBS_UP": ["ctrl", "tab"],
            "THUMBS_DOWN": ["ctrl", "shift", "tab"],
            "OPEN_PALM": ["f5"]
        }
    }
}
```

### 4.9.2 Custom Gestures File (custom_gestures.json)

```json
{
    "MY_CUSTOM_GESTURE": [
        [0.0, 0.0],           // Landmark 0 (wrist, normalized to origin)
        [0.15, -0.1],         // Landmark 1
        [0.25, -0.15],        // Landmark 2
        // ... 21 landmarks total
    ]
}
```

---

## 4.10 Error Handling Design

### 4.10.1 Error Categories and Responses

| Error Type | Cause | System Response |
|------------|-------|-----------------|
| Camera not found | No webcam connected | Display error message, disable Start button |
| Camera in use | Another app using camera | Show message, suggest closing other apps |
| Frame read failure | Camera disconnected | Increment miss counter, retry |
| MediaPipe failure | Processing error | Return UNKNOWN gesture, continue |
| Config file corrupt | Invalid JSON | Use default values, overwrite file |
| Shortcut execution fail | Invalid key combination | Log error, play error sound |

### 4.10.2 Graceful Degradation

```
┌─────────────────────────────────────────────────────────────────┐
│                    GRACEFUL DEGRADATION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Hand lost momentarily?                                         │
│    → Keep last position for 5 frames                           │
│    → Then reset (prevents sudden jumps)                        │
│                                                                 │
│  Low light detected?                                            │
│    → Automatically enable CLAHE enhancement                    │
│    → Hysteresis: ON at <80 brightness, OFF at >100             │
│                                                                 │
│  High CPU usage?                                                │
│    → Reduce FPS from 30 to 5 during idle (no hand)             │
│    → Resume full speed when hand detected                      │
│                                                                 │
│  Queue full?                                                    │
│    → Drop oldest frame                                         │
│    → Always process freshest data                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4.11 Chapter Summary

In this chapter, we have:

1. **Established design goals** including real-time performance, modularity, and extensibility

2. **Presented the system architecture** with clear layer separation:
   - Presentation Layer (UI)
   - Application Layer (Controllers)
   - Processing Layer (Algorithms)
   - Data Layer (Configuration)
   - External Layer (Libraries)

3. **Designed the threading architecture** with:
   - Vision Thread for camera processing
   - Main Thread for UI
   - Queue-based communication

4. **Detailed each module's design**:
   - main.py: Application controller and thread management
   - gesture_engine.py: MediaPipe integration and gesture recognition
   - swipe_engine.py: Trajectory-based swipe detection
   - position_smoother.py: Kalman-filter based smoothing
   - ui_manager.py: CustomTkinter interface
   - config.py: Settings management
   - audio_feedback.py: Sound effects

5. **Created UML diagrams**:
   - Class diagram showing relationships
   - Sequence diagrams for key workflows

6. **Explained gesture recognition design**:
   - Geometry-based finger state detection
   - Decision table for each gesture
   - ROI restriction for static gestures

7. **Documented data storage formats** for configuration and custom gestures

8. **Planned error handling** with graceful degradation strategies

**Key Design Decisions:**
- Threading separates heavy processing from UI
- Geometry-based recognition (no ML training needed)
- ROI prevents accidental static gesture triggers
- Queue drops old frames for real-time responsiveness
- Kalman filtering provides smooth tracking

**Simple Summary:** *We designed our system like a well-organized factory. Different departments (modules) handle different jobs. Workers communicate through mailboxes (queues). Everything has a specific place and purpose. Now we're ready to actually build it!*

---

*[End of Chapter 4]*

---
