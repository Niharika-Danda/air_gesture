# CHAPTER 5: IMPLEMENTATION

# Part 2: Main Application Module

---

## 5.5 Main Module (main.py)

The main module is the heart of our application. It coordinates all other modules, manages the application lifecycle, and handles the core logic of gesture detection and shortcut execution.

**Simple Explanation:** *Think of main.py as the manager of a restaurant. The manager doesn't cook food or serve tables directly, but coordinates the kitchen (gesture engine), waiters (UI), and makes sure everything runs smoothly together.*

---

### 5.5.1 Module Imports and Setup

```python
# src/main.py

# ============================================
# Suppress Library Warnings
# Must be set BEFORE importing these libraries
# ============================================
import os
import warnings

# Suppress background library logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Suppress additional library logging
os.environ['ABSL_MIN_LOG_LEVEL'] = '3'

# Suppress delegate info messages
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Suppress deprecation warnings
warnings.filterwarnings('ignore', category=UserWarning, module='google.protobuf')
warnings.filterwarnings('ignore', category=DeprecationWarning)
```

**Why suppress warnings?**

MediaPipe and TensorFlow produce many informational messages that clutter the console:
```
INFO: Created TensorFlow Lite XNNPACK delegate
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
```

These aren't errors - just information we don't need to see. Setting these environment variables hides them.

**Simple Explanation:** *It's like telling a chatty coworker to only speak up when something important happens, not for every little thing.*

```python
# Standard library imports
import cv2          # OpenCV for camera
import pyautogui    # For keyboard simulation
import tkinter as tk
import time
import sys
import os
import ctypes       # For Windows API calls
from ctypes import wintypes
import numpy as np

# Threading imports
import queue
import threading

# Fix path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Our modules
from src.gesture_engine import GestureProcessor
from src.ui_manager import AppUIManager
from src.audio_feedback import AudioFeedback
from src import config
```

**Import organization:**

| Category | Imports | Purpose |
|----------|---------|---------|
| Standard Library | `os`, `sys`, `time` | Basic Python functionality |
| Image/Video | `cv2`, `numpy` | Camera capture, frame processing |
| Automation | `pyautogui` | Keyboard shortcut execution |
| GUI | `tkinter` | Window management |
| Windows API | `ctypes` | Get active window title |
| Threading | `queue`, `threading` | Background processing |
| Our Modules | `GestureProcessor`, etc. | Custom functionality |

---

### 5.5.2 VisionThread Class

The VisionThread handles all camera and gesture processing in the background, keeping the UI responsive.

```python
class VisionThread(threading.Thread):
    """
    Background thread for camera capture and gesture processing.
    Runs independently of the UI to prevent freezing.
    """

    def __init__(self, camera_index, result_queue):
        super().__init__()  # Initialize parent Thread class
        self.camera_index = camera_index
        self.result_queue = result_queue
        self.stop_event = threading.Event()  # Flag to signal stop
        self.gesture_processor = None
        self.cap = None  # Camera capture object
        self.frame_counter = 0
```

**Constructor explained:**

| Parameter | Purpose |
|-----------|---------|
| `camera_index` | Which camera to use (0, 1, 2, etc.) |
| `result_queue` | Queue to send results to main thread |
| `stop_event` | Thread-safe flag to signal shutdown |
| `gesture_processor` | Will hold the GestureProcessor instance |
| `cap` | Will hold the OpenCV VideoCapture |
| `frame_counter` | Counts frames for periodic tasks |

**Simple Explanation:** *VisionThread is like a dedicated assistant who only handles the camera and gesture detection. They work in a separate room (thread) so the main program doesn't have to wait for them.*

#### The run() Method

```python
def run(self):
    """
    Main thread loop - runs continuously until stopped.
    """
    try:
        # Step 1: Open camera
        self.cap = cv2.VideoCapture(self.camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.VIDEO_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.VIDEO_HEIGHT)

        # Step 2: Create gesture processor
        self.gesture_processor = GestureProcessor(
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
        )

        # Step 3: Main processing loop
        while not self.stop_event.is_set():
            # Capture frame
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue
```

**Step-by-step breakdown:**

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Open Camera                                            │
│                                                                 │
│  cv2.VideoCapture(0)  ───►  Opens camera #0                    │
│  cap.set(WIDTH, 1280) ───►  Sets capture width                 │
│  cap.set(HEIGHT, 720) ───►  Sets capture height                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Create Gesture Processor                               │
│                                                                 │
│  GestureProcessor(...)  ───►  Initializes MediaPipe            │
│                               Sets detection thresholds         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Processing Loop                                        │
│                                                                 │
│  while not stopped:                                             │
│      read frame from camera                                     │
│      process frame for gestures                                 │
│      put results in queue                                       │
│      repeat...                                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Dynamic Low-Light Detection

```python
            # --- Dynamic Environmental Adaptation ---
            self.frame_counter += 1
            if self.frame_counter % 30 == 0:  # Every ~1 second at 30 FPS
                try:
                    # Fast brightness check on smaller image
                    small_frame = cv2.resize(frame, (320, 180))
                    gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                    avg_brightness = np.mean(gray)

                    # Hysteresis Logic to prevent flickering
                    # Turn ON when brightness < 80
                    # Turn OFF when brightness > 100
                    if not config.LOW_LIGHT_MODE and avg_brightness < 80:
                        config.LOW_LIGHT_MODE = True
                    elif config.LOW_LIGHT_MODE and avg_brightness > 100:
                        config.LOW_LIGHT_MODE = False

                except Exception as e:
                    pass  # Silently ignore errors
```

**What is hysteresis?**

```
Brightness Level:
    120 ──────────────────────────────────────────
                                    OFF threshold
    100 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
                    ▲
     80 ─ ─ ─ ─ ─ ─ │─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
                    │               ON threshold
     60 ────────────┼─────────────────────────────
                    │
        Low-light   │   Normal
        mode ON     │   mode

Without hysteresis: Mode would flicker ON/OFF/ON/OFF rapidly
                    when brightness hovers around 80-90

With hysteresis: Must go BELOW 80 to turn ON
                 Must go ABOVE 100 to turn OFF
                 Gap prevents flickering!
```

**Simple Explanation:** *Imagine a thermostat. Instead of turning heat on at exactly 68°F and off at 68°F (which would make it turn on and off constantly), it turns on at 65°F and off at 70°F. The gap prevents rapid switching. We do the same for low-light mode!*

#### Processing and Queue Management

```python
            # Process the frame
            try:
                gesture, processed_frame, pointer_info, landmarks = \
                    self.gesture_processor.process_frame(frame)
            except ValueError:
                # Fallback for compatibility
                gesture, processed_frame, pointer_info = \
                    self.gesture_processor.process_frame(frame)
                landmarks = None

            # Put result in queue (drop old if full)
            if self.result_queue.full():
                try:
                    self.result_queue.get_nowait()  # Remove old frame
                except queue.Empty:
                    pass

            self.result_queue.put((
                gesture,
                processed_frame,
                pointer_info,
                landmarks,
                time.time()
            ))

            # Small sleep to yield CPU
            time.sleep(0.001)
```

**Queue management strategy:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUEUE STRATEGY                               │
│                                                                 │
│  Queue Size: 2 (very small)                                     │
│                                                                 │
│  Why small?                                                     │
│  - We want the LATEST frame, not old ones                      │
│  - Large queue = processing old data = lag                     │
│                                                                 │
│  When queue is full:                                            │
│  ┌─────┬─────┐                                                 │
│  │ Old │ New │  ◄── Queue has 2 items                         │
│  └─────┴─────┘                                                 │
│      │                                                          │
│      ▼  Remove old                                              │
│  ┌─────┐                                                       │
│  │ New │  ◄── Now has space                                    │
│  └─────┘                                                       │
│      │                                                          │
│      ▼  Add newest                                              │
│  ┌─────┬─────────┐                                             │
│  │ New │ Newest  │  ◄── Always fresh data!                     │
│  └─────┴─────────┘                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Simple Explanation:** *Imagine a small mailbox that only holds 2 letters. When a new letter arrives and the mailbox is full, we throw away the oldest letter to make room. This way, we always have the most recent mail!*

#### Cleanup

```python
    except Exception as e:
        print(f"VisionThread Error: {e}")
    finally:
        # Always clean up resources
        if self.cap:
            self.cap.release()
        if self.gesture_processor:
            self.gesture_processor.close()

def stop(self):
    """Signal the thread to stop."""
    self.stop_event.set()
```

**Why `finally` is important:**

```python
try:
    # Code that might fail
except:
    # Handle error
finally:
    # ALWAYS runs, even if error occurred
    # Perfect for cleanup!
```

**Simple Explanation:** *`finally` is like a responsible adult who always cleans up the kitchen, whether dinner was successful or burned. The camera must be released no matter what happens!*

---

### 5.5.3 GestureControllerApp Class

This is the main application class that coordinates everything.

#### Constructor (__init__)

```python
class GestureControllerApp:
    def __init__(self, root):
        self.root = root
        self.is_running = False
        self.last_gesture = None
        self.last_gesture_time = 0
        self.frame_count = 0

        # Adaptive FPS state
        self.last_hand_detected_time = time.time()

        # Profile state
        self.current_profile_name = 'DEFAULT'

        # Threading
        self.result_queue = queue.Queue(maxsize=2)
        self.vision_thread = None
```

**Instance variables explained:**

| Variable | Purpose |
|----------|---------|
| `root` | The main window (CTk instance) |
| `is_running` | True when camera is active |
| `last_gesture` | Previous detected gesture (for debouncing) |
| `last_gesture_time` | When last gesture was triggered |
| `frame_count` | Counter for periodic tasks |
| `last_hand_detected_time` | For idle mode detection |
| `current_profile_name` | Active profile (DEFAULT, POWERPOINT, etc.) |
| `result_queue` | Communication with VisionThread |
| `vision_thread` | The background processing thread |

#### Camera Discovery

```python
def detect_cameras(self):
    """Find all available cameras."""
    index = 0
    arr = []
    for i in range(5):  # Check first 5 indices
        cap = cv2.VideoCapture(i)
        if cap.read()[0]:  # If we can read a frame
            arr.append(i)
            cap.release()
        index += 1
    return arr
```

**How camera detection works:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAMERA DETECTION                             │
│                                                                 │
│  Try index 0: cv2.VideoCapture(0)                              │
│               ├── Can read frame? YES ──► Add to list          │
│               └── Can read frame? NO  ──► Skip                 │
│                                                                 │
│  Try index 1: cv2.VideoCapture(1)                              │
│               ├── Can read frame? YES ──► Add to list          │
│               └── Can read frame? NO  ──► Skip                 │
│                                                                 │
│  ... continue for indices 2, 3, 4                               │
│                                                                 │
│  Result: [0, 2] means cameras at index 0 and 2 work            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Simple Explanation:** *We knock on 5 doors (camera indices) and see which ones answer (can provide video). The ones that answer go on our list of available cameras.*

#### Starting the Camera

```python
def start(self):
    """Start gesture recognition."""
    if not self.is_running:
        # Safety: Wait for any previous thread
        if self.vision_thread and self.vision_thread.is_alive():
            print("DEBUG: Waiting for previous thread to die...")
            self.vision_thread.join(timeout=2.0)

        self.is_running = True
        self.ui_manager.update_status("Status: Starting Engine...")
        self.ui_manager.start_button.configure(state="disabled")

        # Reset Queue
        self.result_queue = queue.Queue(maxsize=2)

        # Start Vision Thread
        self.vision_thread = VisionThread(
            config.CAMERA_INDEX,
            self.result_queue
        )
        self.vision_thread.start()

        # Schedule UI updates
        self.root.after(100, lambda: self.ui_manager.update_status("Status: Running"))
        self.root.after(100, lambda: self.ui_manager.start_button.configure(state="normal"))
        self.root.after(50, lambda: self.ui_manager.enter_overlay_mode())
        self.root.after(100, self.update)
```

**Startup sequence:**

```
User clicks "Start"
        │
        ▼
┌───────────────────┐
│ Check for old     │
│ thread still      │──► Wait up to 2 seconds
│ running           │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Set is_running    │
│ = True            │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Create new        │
│ result queue      │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Create & start    │
│ VisionThread      │──► Camera opens, processing begins
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Schedule:         │
│ - Status update   │
│ - Enable buttons  │
│ - Enter overlay   │
│ - Start update()  │
└───────────────────┘
```

**What is `root.after()`?**

```python
self.root.after(100, self.update)  # Call self.update after 100ms
```

This schedules a function to run after a delay WITHOUT blocking the UI.

**Simple Explanation:** *`after()` is like setting a timer. "After 100 milliseconds, do this task." The program keeps running while waiting, unlike `time.sleep()` which freezes everything.*

#### Stopping the Camera

```python
def stop(self):
    """Stop gesture recognition."""
    if self.is_running:
        self.is_running = False
        self.ui_manager.update_status("Status: Stopping...")

        if self.vision_thread:
            self.vision_thread.stop()  # Signal stop
            self.vision_thread.join(timeout=2.0)  # Wait up to 2 seconds

            if self.vision_thread.is_alive():
                print("WARNING: VisionThread did not stop cleanly!")

            self.vision_thread = None

        self.ui_manager.update_status("Status: Stopped")
        self.ui_manager.start_button.configure(state="normal")
```

**Thread shutdown process:**

```
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│  Main Thread                    Vision Thread                 │
│       │                              │                        │
│       │ stop()                       │                        │
│       ├─────────────────────────────►│                        │
│       │ (sets stop_event)            │                        │
│       │                              │                        │
│       │ join(timeout=2.0)            │ Sees stop_event        │
│       │ ◄────────────────────────────┤ Releases camera        │
│       │ (waits for thread)           │ Closes MediaPipe       │
│       │                              │ Exits run()            │
│       │                              ▼                        │
│       │◄─────────────────────────────  Thread ends            │
│       │                                                       │
│       ▼                                                       │
│  Thread is None                                               │
│  Continue normally                                            │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

#### The Main Update Loop

```python
def update(self):
    """Main UI update loop - polls queue and processes results."""
    if not self.is_running:
        return  # Stop updating if not running

    try:
        # Poll queue for new frames
        # Drain queue to get LATEST frame
        latest_data = None
        while True:
            try:
                latest_data = self.result_queue.get_nowait()
            except queue.Empty:
                break

        if latest_data:
            # Unpack the data
            gesture, processed_frame, pointer_info, landmarks, timestamp = latest_data

            # FPS Calculation
            self.fps_frame_count += 1
            if time.time() - self.fps_start_time >= 1.0:
                self.current_fps = self.fps_frame_count
                self.fps_frame_count = 0
                self.fps_start_time = time.time()

            # Update UI
            hand_detected = pointer_info is not None
            self.ui_manager.update_performance(self.current_fps, hand_detected, 1.0)
            self.ui_manager.update_frame(processed_frame)

            # Process gesture
            self._handle_logic(gesture, pointer_info, landmarks)

    except Exception as e:
        print(f"Update Loop Error: {e}")

    # Periodic tasks (every 30 frames)
    self.frame_count += 1
    if self.frame_count % 30 == 0:
        self._update_app_state()

    # Schedule next update (10ms = 100Hz polling)
    self.root.after(10, self.update)
```

**Update loop flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                     UPDATE LOOP (every 10ms)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Still running? │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │ No                          │ Yes
              ▼                             ▼
         ┌────────┐                ┌─────────────────┐
         │ Return │                │ Drain queue     │
         └────────┘                │ (get latest)    │
                                   └────────┬────────┘
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │ Got new frame?  │
                                   └────────┬────────┘
                                            │
                             ┌──────────────┴──────────────┐
                             │ No                          │ Yes
                             ▼                             ▼
                    (skip to schedule)            ┌─────────────────┐
                                                  │ Calculate FPS   │
                                                  │ Update UI       │
                                                  │ Handle gesture  │
                                                  └────────┬────────┘
                                                           │
                                            ┌──────────────┘
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │ Every 30 frames:│
                                   │ Check window    │
                                   │ Update profile  │
                                   └────────┬────────┘
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │ Schedule next   │
                                   │ update (10ms)   │
                                   └─────────────────┘
```

**Why drain the queue?**

```python
while True:
    try:
        latest_data = self.result_queue.get_nowait()
    except queue.Empty:
        break
```

This loop keeps getting items until the queue is empty, so we always process the NEWEST frame:

```
Queue: [Frame1, Frame2, Frame3]
                              ↑
                         We want THIS one!

After draining: latest_data = Frame3
```

**Simple Explanation:** *If the queue has 3 frames waiting, we want the newest one (Frame3), not the oldest. So we read all of them but only keep the last one.*

#### Handling Gesture Logic

```python
def _handle_logic(self, gesture, pointer_info, landmarks=None):
    """Process detected gestures and execute shortcuts."""

    # --- MOUSE CONTROL ---
    if pointer_info and config.ENABLE_MOUSE:
        try:
            screen_w, screen_h = pyautogui.size()

            # Map camera coordinates to screen
            margin = 0.2
            x_cam = pointer_info['x']
            y_cam = pointer_info['y']

            # Remap: (margin, 1-margin) -> (0, 1)
            x_norm = (x_cam - margin) / (1 - 2*margin)
            y_norm = (y_cam - margin) / (1 - 2*margin)

            # Clamp to valid range
            x_norm = max(0.0, min(1.0, x_norm))
            y_norm = max(0.0, min(1.0, y_norm))

            # Convert to screen coordinates
            target_x = int(x_norm * screen_w)
            target_y = int(y_norm * screen_h)

            # Move mouse
            pyautogui.moveTo(target_x, target_y)

            # Handle click (pinch gesture)
            if pointer_info['click']:
                if not getattr(self, 'is_clicking', False):
                    pyautogui.mouseDown()
                    self.is_clicking = True
            else:
                if getattr(self, 'is_clicking', False):
                    pyautogui.mouseUp()
                    self.is_clicking = False

        except Exception as e:
            pass
```

**Coordinate mapping explained:**

```
Camera View (0.0 to 1.0)         Screen (pixels)
┌─────────────────────┐         ┌─────────────────────┐
│                     │         │                     │
│  margin   usable    │         │                     │
│   0.2    0.2-0.8    │  ───►   │  Full screen        │
│   ▼      ▼    ▼     │         │  0 to 1920 pixels   │
│ ┌──┬─────────┬──┐   │         │                     │
│ │  │  Hand   │  │   │         │  ┌───────────────┐  │
│ │  │  here   │  │   │         │  │ Cursor here   │  │
│ │  │    ●    │  │   │         │  │      ●        │  │
│ └──┴─────────┴──┘   │         │  └───────────────┘  │
│                     │         │                     │
└─────────────────────┘         └─────────────────────┘

With margins, you don't need to reach the very edges of the camera view
to move the cursor to the screen edges.
```

**Simple Explanation:** *The camera sees coordinates from 0.0 to 1.0. We add margins so you don't have to reach the extreme edges. The usable area (0.2 to 0.8) maps to the full screen.*

#### Gesture Filtering and Execution

```python
    # Filter: Only process gestures in current profile
    current_profile = config.PROFILES.get(
        self.current_profile_name,
        config.PROFILES['DEFAULT']
    )
    if gesture != 'UNKNOWN' and gesture not in current_profile:
        gesture = 'UNKNOWN'  # Ignore unmapped gestures

    if gesture != 'UNKNOWN':
        self.last_hand_detected_time = time.time()

    # Check cooldown and trigger
    current_time = time.time()
    if gesture != 'UNKNOWN' and gesture != self.last_gesture:
        if current_time - self.last_gesture_time > config.GESTURE_COOLDOWN:
            self.execute_shortcut(gesture)
            self.last_gesture = gesture
            self.last_gesture_time = current_time
            self.ui_manager.update_status(f"{self.current_profile_name}: {gesture}")
    elif gesture == 'UNKNOWN':
        self.last_gesture = None  # Reset when no gesture
```

**Gesture execution flow:**

```
Gesture Detected: "THUMBS_UP"
          │
          ▼
┌─────────────────────────────┐
│ Is it in current profile?   │
│ (POWERPOINT has THUMBS_UP)  │
└─────────────┬───────────────┘
              │ Yes
              ▼
┌─────────────────────────────┐
│ Is it different from last?  │
│ (Prevents repeat triggers)  │
└─────────────┬───────────────┘
              │ Yes
              ▼
┌─────────────────────────────┐
│ Has cooldown passed?        │
│ (0.3 seconds since last)    │
└─────────────┬───────────────┘
              │ Yes
              ▼
┌─────────────────────────────┐
│ EXECUTE SHORTCUT!           │
│ Update last_gesture         │
│ Update last_gesture_time    │
│ Show feedback               │
└─────────────────────────────┘
```

#### Profile Switching

```python
def _update_app_state(self):
    """Update active profile based on foreground window."""
    window_title = self.get_active_window_title()

    # Check if window matches any profile
    new_profile = 'DEFAULT'
    for title_part, profile_name in config.WINDOW_PROFILE_MAP.items():
        if title_part.lower() in window_title.lower():
            new_profile = profile_name
            break

    # Switch profile if changed
    if new_profile != self.current_profile_name:
        print(f"DEBUG: Switched to Profile: {new_profile}")
        self.current_profile_name = new_profile
        self.ui_manager.update_status(f"Profile: {new_profile}")
```

**Profile matching logic:**

```python
# Window title: "Presentation1 - PowerPoint"
# WINDOW_PROFILE_MAP = {'PowerPoint': 'POWERPOINT', ...}

for title_part, profile_name in WINDOW_PROFILE_MAP.items():
    # Iteration 1: title_part = 'PowerPoint'
    #              'powerpoint' in 'presentation1 - powerpoint' → True!
    #              new_profile = 'POWERPOINT'
    #              break (stop searching)
```

**Simple Explanation:** *Every second or so, we check what window is active. If the title contains "PowerPoint", we switch to the POWERPOINT profile. If it contains "Chrome", we switch to CHROME. Otherwise, we use DEFAULT.*

#### Getting Active Window Title (Windows API)

```python
def get_active_window_title(self):
    """Returns the title of the current foreground window."""
    try:
        # Get handle to foreground window
        hwnd = ctypes.windll.user32.GetForegroundWindow()

        # Get the length of the window title
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)

        # Create buffer and get title
        buff = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)

        return buff.value
    except Exception:
        return ""
```

**How Windows API calls work:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    WINDOWS API FLOW                             │
│                                                                 │
│  Python                     Windows OS                          │
│     │                           │                               │
│     │ GetForegroundWindow()     │                               │
│     ├──────────────────────────►│                               │
│     │                           │ Returns: hwnd (window handle) │
│     │◄──────────────────────────┤                               │
│     │                           │                               │
│     │ GetWindowTextLengthW()    │                               │
│     ├──────────────────────────►│                               │
│     │                           │ Returns: 25 (length)          │
│     │◄──────────────────────────┤                               │
│     │                           │                               │
│     │ GetWindowTextW()          │                               │
│     ├──────────────────────────►│                               │
│     │                           │ Returns: "Document - Chrome"  │
│     │◄──────────────────────────┤                               │
│     │                           │                               │
└─────────────────────────────────────────────────────────────────┘
```

**Simple Explanation:** *We ask Windows "What window is active?" Windows gives us a number (handle). Then we ask "How long is that window's title?" and "What IS the title?" Windows tells us "Document - Chrome" or whatever window is in front.*

#### Executing Shortcuts

```python
def execute_shortcut(self, gesture):
    """Execute keyboard shortcut for recognized gesture."""
    # Don't trigger OPEN_PALM in overlay (might be waving to exit)
    if self.ui_manager.is_overlay and gesture == 'OPEN_PALM':
        return

    # Get shortcut from current profile
    profile = config.PROFILES.get(
        self.current_profile_name,
        config.PROFILES['DEFAULT']
    )
    shortcut = profile.get(gesture)

    if shortcut:
        try:
            # Play feedback sound
            if "SWIPE" in gesture:
                self.audio.play_swipe_sound()
            else:
                self.audio.play_static_gesture_sound()

            # Execute the shortcut
            pyautogui.hotkey(*shortcut)
            print(f"[{self.current_profile_name}] Executed {gesture}: {shortcut}")

        except Exception as e:
            print(f"Failed to execute shortcut: {e}")
            self.audio.play_error_sound()
```

**How pyautogui.hotkey() works:**

```python
shortcut = ['ctrl', 'tab']
pyautogui.hotkey(*shortcut)

# The * unpacks the list:
# pyautogui.hotkey('ctrl', 'tab')

# Which simulates:
# 1. Press and hold Ctrl
# 2. Press and release Tab
# 3. Release Ctrl
```

**Simple Explanation:** *pyautogui.hotkey() is like having a robot finger that can press keyboard keys for us. When we say hotkey('ctrl', 'tab'), it's like the robot pressing Ctrl+Tab on the keyboard!*

---

### 5.5.4 Application Entry Point

```python
if __name__ == "__main__":
    import customtkinter as ctk

    # Enable High DPI scaling
    ctk.set_widget_scaling(1.0)
    ctk.set_window_scaling(1.0)

    # Create main window
    root = ctk.CTk()

    # Create application
    app = GestureControllerApp(root)

    # Handle window close properly
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop(), root.destroy()))

    # Start the event loop
    root.mainloop()
```

**What each line does:**

| Line | Purpose |
|------|---------|
| `if __name__ == "__main__":` | Only runs if this file is executed directly (not imported) |
| `ctk.set_widget_scaling(1.0)` | Prevents blurry widgets on high-DPI displays |
| `root = ctk.CTk()` | Creates the main window |
| `app = GestureControllerApp(root)` | Creates our application |
| `root.protocol(...)` | Handles the X button - stops camera before closing |
| `root.mainloop()` | Starts the GUI event loop (keeps window running) |

**Simple Explanation:** *This is the "start button" of our program. It creates a window, creates our application inside it, and keeps everything running until the user closes the window.*

---

## 5.6 Chapter Summary (Part 2)

In this part, we examined the main application module:

### VisionThread
- Runs camera capture in a background thread
- Processes frames through GestureProcessor
- Manages low-light detection with hysteresis
- Uses queue to communicate with main thread
- Properly cleans up resources on shutdown

### GestureControllerApp
- Coordinates all components of the application
- Discovers and manages cameras
- Controls start/stop lifecycle
- Runs update loop at 100Hz for responsive UI
- Handles gesture-to-shortcut mapping
- Automatically switches profiles based on active window
- Uses Windows API to detect foreground application

### Key Concepts Learned
- **Threading**: Keeping UI responsive while processing video
- **Queue communication**: Safe data passing between threads
- **Hysteresis**: Preventing rapid mode switching
- **Windows API**: Getting active window information
- **Event scheduling**: Using `after()` for non-blocking delays

**Next:** Part 3 will cover the Gesture Engine module (gesture_engine.py), including MediaPipe integration and static gesture recognition algorithms.

---

*[End of Chapter 5 - Part 2]*

---
