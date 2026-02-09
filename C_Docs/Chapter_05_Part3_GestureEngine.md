# CHAPTER 5: IMPLEMENTATION

# Part 3: Gesture Engine Module

---

## 5.6 Gesture Engine Module (gesture_engine.py)

The Gesture Engine is the core intelligence of our application. It takes raw video frames and outputs recognized gestures. This module integrates MediaPipe for hand detection and implements custom logic for gesture classification.

**Simple Explanation:** *The Gesture Engine is like a translator. It takes pictures from the camera (which are just colored dots to a computer) and translates them into meaningful gestures like "thumbs up" or "swipe right" that our program can understand and act on.*

---

### 5.6.1 Module Imports

```python
# src/gesture_engine.py

# Suppress library warnings for cleaner output
import os
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['ABSL_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore', category=UserWarning, module='google.protobuf')

import cv2
import mediapipe as mp
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_drawing
import math
from collections import deque, Counter
import time

# Our custom modules
from src.position_smoother import LandmarkSmoother, PointerSmoother
from src.gesture_recorder import GestureRecorder
```

**Import purposes:**

| Import | Purpose |
|--------|---------|
| `cv2` | Image processing (color conversion, CLAHE) |
| `mediapipe` | Hand detection and landmark extraction |
| `math` | Distance calculations (hypot, sqrt) |
| `deque` | Fixed-size buffer for gesture history |
| `Counter` | Vote counting for gesture confirmation |
| `LandmarkSmoother` | Reduces jitter in landmark positions |
| `GestureRecorder` | Matches custom user-defined gestures |

---

### 5.6.2 GestureProcessor Class - Constructor

```python
class GestureProcessor:
    """
    Handles the detection of hand landmarks and recognition of gestures.
    Supports both static signs and dynamic swipe gestures.
    Uses position smoothing for stable tracking.
    """

    def __init__(self, min_detection_confidence=0.7, min_tracking_confidence=0.5):
        """
        Initializes the hand tracking system.

        Args:
            min_detection_confidence: How sure MediaPipe must be to detect a hand
            min_tracking_confidence: How sure MediaPipe must be to keep tracking
        """
        # MediaPipe Hands setup
        self.mp_hands = mp_hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,      # Video mode (not single images)
            max_num_hands=1,              # Track only one hand
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp_drawing

        # Current frame's landmarks
        self.landmarks = None
        self.filtered_landmarks = None  # Smoothed positions
```

**MediaPipe Hands Configuration:**

```
┌─────────────────────────────────────────────────────────────────┐
│                 MEDIAPIPE HANDS SETTINGS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  static_image_mode = False                                      │
│  ├── False: Optimized for video (uses tracking between frames) │
│  └── True: Treats each frame independently (slower)            │
│                                                                 │
│  max_num_hands = 1                                              │
│  ├── We only track one hand                                     │
│  └── Reduces processing time and complexity                     │
│                                                                 │
│  min_detection_confidence = 0.5                                 │
│  ├── 50% confidence threshold for initial detection             │
│  └── Lower = more sensitive, Higher = stricter                  │
│                                                                 │
│  min_tracking_confidence = 0.4                                  │
│  ├── 40% confidence to maintain tracking                        │
│  └── Lower = keeps tracking longer, Higher = loses track easier │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Continuing the constructor:**

```python
        # Custom Gesture Recorder
        self.recorder = GestureRecorder()

        # Swipe Detector
        from src import config
        from src.swipe_engine import SwipeDetector
        self.swipe_detector = SwipeDetector(
            history_length=config.SWIPE_HISTORY_LENGTH if hasattr(config, 'SWIPE_HISTORY_LENGTH') else 10,
            min_dist_left=config.SWIPE_MIN_DISTANCE_LEFT,
            min_dist_right=config.SWIPE_MIN_DISTANCE_RIGHT,
            min_velocity=0.4
        )

        # Gesture voting buffer
        self.gesture_buffer = deque(maxlen=config.SMOOTHING_BUFFER_SIZE)

        # Debounce for lost tracking
        self.missed_frames = 0

        # Position smoothers
        self.landmark_smoother = LandmarkSmoother(
            num_landmarks=21,
            smoothing_factor=0.005,
            responsiveness=0.05
        )
        self.pointer_smoother = PointerSmoother(
            base_smoothing=0.02,
            base_responsiveness=0.08
        )

        # Legacy pointer state
        self.prev_pointer_x = 0
        self.prev_pointer_y = 0
```

**Component relationships:**

```
┌─────────────────────────────────────────────────────────────────┐
│                   GestureProcessor Components                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐                                            │
│  │  MediaPipe      │──► Detects hand, extracts 21 landmarks    │
│  │  Hands          │                                            │
│  └─────────────────┘                                            │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                            │
│  │  Landmark       │──► Smooths all 21 landmark positions       │
│  │  Smoother       │    (reduces jitter)                        │
│  └─────────────────┘                                            │
│           │                                                     │
│           ├──────────────────────┐                              │
│           ▼                      ▼                              │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  Swipe          │    │  Static Gesture │                    │
│  │  Detector       │    │  Recognition    │                    │
│  └─────────────────┘    └─────────────────┘                    │
│           │                      │                              │
│           └──────────┬───────────┘                              │
│                      ▼                                          │
│             ┌─────────────────┐                                 │
│             │ Gesture Buffer  │──► Voting for confirmation      │
│             │ (deque)         │                                 │
│             └─────────────────┘                                 │
│                      │                                          │
│                      ▼                                          │
│              Final Gesture Output                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 5.6.3 The Main Processing Pipeline - process_frame()

```python
def process_frame(self, frame):
    """
    Processes a single video frame to detect and recognize gestures.

    Args:
        frame: BGR image from OpenCV (numpy array)

    Returns:
        tuple: (gesture_name, processed_frame, pointer_info, landmarks)
    """
    # Step 1: Flip frame horizontally (mirror effect)
    frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
```

**Why flip the frame?**

```
Without flip:                    With flip (mirror):
┌─────────────────┐              ┌─────────────────┐
│                 │              │                 │
│  Move right ──► │              │ ◄── Move right  │
│                 │              │                 │
│  Your right     │              │  Your right     │
│  hand appears   │              │  hand appears   │
│  on LEFT side   │              │  on RIGHT side  │
│                 │              │                 │
└─────────────────┘              └─────────────────┘
      Confusing!                    Natural mirror!
```

**Simple Explanation:** *Without flipping, moving your right hand makes it appear on the left side of the screen - very confusing! Flipping creates a mirror effect, so the video feels natural like looking in a mirror.*

#### Low-Light Enhancement (CLAHE)

```python
    # Step 2: Low-light enhancement
    from src import config
    if config.LOW_LIGHT_MODE:
        # Convert to LAB color space
        lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)

        # Split into L, A, B channels
        l, a, b = cv2.split(lab)

        # Apply CLAHE to L (lightness) channel only
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        cl = clahe.apply(l)

        # Merge back and convert to RGB
        limg = cv2.merge((cl, a, b))
        frame = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
```

**What is CLAHE?**

CLAHE = Contrast Limited Adaptive Histogram Equalization

```
┌─────────────────────────────────────────────────────────────────┐
│                      HOW CLAHE WORKS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Original Dark Image:          After CLAHE:                     │
│  ┌─────────────────┐          ┌─────────────────┐              │
│  │░░░░░░░░░░░░░░░░░│          │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│              │
│  │░░░░░░░░░░░░░░░░░│          │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│              │
│  │░░░░░░░✋░░░░░░░░│   ───►   │▓▓▓▓▓▓✋▓▓▓▓▓▓▓▓│              │
│  │░░░░░░░░░░░░░░░░░│          │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│              │
│  │░░░░░░░░░░░░░░░░░│          │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│              │
│  └─────────────────┘          └─────────────────┘              │
│   Hand barely visible          Hand clearly visible            │
│                                                                 │
│  Process:                                                       │
│  1. Convert to LAB (separates lightness from color)            │
│  2. Enhance only the L (lightness) channel                     │
│  3. Keep colors (A, B) unchanged                                │
│  4. Merge back together                                         │
│                                                                 │
│  clipLimit=2.0: Prevents over-amplification of noise           │
│  tileGridSize=(8,8): Divides image into 8x8 regions            │
│                      (adaptive = different enhancement          │
│                       for different areas)                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Simple Explanation:** *CLAHE is like adjusting the brightness on your TV, but smarter. Instead of making everything brighter equally, it adjusts different areas separately. Dark areas get brighter, but already-bright areas don't get washed out. We only adjust brightness (L channel), not colors (A, B channels).*

#### MediaPipe Hand Detection

```python
    # Step 3: Run MediaPipe hand detection
    frame.setflags(write=False)  # MediaPipe requires immutable array
    results = self.hands.process(frame)
    frame.setflags(write=True)   # Make writable again

    # Convert back to BGR for OpenCV operations
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    final_gesture = 'UNKNOWN'
    pointer_info = None
```

**What MediaPipe returns:**

```python
results.multi_hand_landmarks
# If hand detected: [<HandLandmark object>]
# If no hand: None

# Each HandLandmark contains 21 landmarks:
# results.multi_hand_landmarks[0].landmark[0]  → Wrist
# results.multi_hand_landmarks[0].landmark[4]  → Thumb tip
# results.multi_hand_landmarks[0].landmark[8]  → Index tip
# ... and so on
```

#### Processing Detected Hands

```python
    if results.multi_hand_landmarks:
        self.missed_frames = 0  # Reset miss counter

        for hand_landmarks in results.multi_hand_landmarks:
            # Store raw landmarks
            self.landmarks = hand_landmarks.landmark

            # Apply smoothing to all landmarks
            self.filtered_landmarks = self.landmark_smoother.update(self.landmarks)

            # Draw landmarks on frame
            self.mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS
            )
```

**Landmark smoothing visualization:**

```
Raw landmarks (jittery):         Smoothed landmarks (stable):
     ●                                  ●
    ╱                                  ╱
   ●  ← jumps around                  ●  ← stable position
    ╲                                  ╲
     ●                                  ●

Frame 1: (0.50, 0.30)            Frame 1: (0.50, 0.30)
Frame 2: (0.53, 0.28)  ← noise   Frame 2: (0.51, 0.29)  ← smooth
Frame 3: (0.48, 0.31)  ← noise   Frame 3: (0.50, 0.30)  ← smooth
Frame 4: (0.51, 0.29)            Frame 4: (0.50, 0.30)
```

#### Pointer Logic (For Mouse Control)

```python
            # --- POINTER LOGIC ---
            # Get raw index finger tip position
            raw_index_x = self.landmarks[8].x
            raw_index_y = self.landmarks[8].y

            # Apply smoothing for stable pointer
            curr_x, curr_y = self.pointer_smoother.update(raw_index_x, raw_index_y)

            # Get thumb position for click detection
            thumb_x, thumb_y = self.filtered_landmarks[4] if self.filtered_landmarks else (self.landmarks[4].x, self.landmarks[4].y)
            index_x, index_y = self.filtered_landmarks[8] if self.filtered_landmarks else (self.landmarks[8].x, self.landmarks[8].y)

            # Check for pinch (click) gesture
            from src import config
            pad_dist = math.hypot(index_x - thumb_x, index_y - thumb_y)
            is_clicking = pad_dist < config.CLICK_THRESHOLD

            pointer_info = {
                'x': curr_x,
                'y': curr_y,
                'click': is_clicking
            }
```

**Pinch detection for clicking:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    PINCH DETECTION                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Not clicking (distance > threshold):                          │
│                                                                 │
│      Index tip (8)                                              │
│           ●                                                     │
│           │                                                     │
│           │  distance = 0.15                                    │
│           │  threshold = 0.035                                  │
│           │  0.15 > 0.035 → NOT clicking                       │
│           │                                                     │
│           ●                                                     │
│      Thumb tip (4)                                              │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Clicking (distance < threshold):                               │
│                                                                 │
│      Index tip (8)                                              │
│          ●●  ← Pinched together!                               │
│      Thumb tip (4)                                              │
│                                                                 │
│           distance = 0.02                                       │
│           threshold = 0.035                                     │
│           0.02 < 0.035 → CLICKING!                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Simple Explanation:** *To detect a "click", we measure the distance between your thumb tip and index finger tip. When you pinch them together (like pinching a grain of rice), the distance becomes very small - that's a click!*

#### Centroid Calculation and Swipe Detection

```python
            # --- GESTURE LOGIC ---
            # Calculate hand centroid (center of palm area)
            wrist = self.landmarks[0]
            index_mcp = self.landmarks[5]   # Index knuckle
            pinky_mcp = self.landmarks[17]  # Pinky knuckle

            cx = (wrist.x + index_mcp.x + pinky_mcp.x) / 3.0
            cy = (wrist.y + index_mcp.y + pinky_mcp.y) / 3.0
            current_centroid = (cx, cy)

            # Run swipe detection
            swipe_gesture = self.swipe_detector.process(current_centroid, time.time())
```

**Why use centroid for swipes?**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CENTROID CALCULATION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Hand Landmarks:                Centroid:                       │
│                                                                 │
│      8  12  16  20                                              │
│      │   │   │   │                                              │
│      7  11  15  19                                              │
│      │   │   │   │                                              │
│  4   6  10  14  18                                              │
│  │   │   │   │   │                                              │
│  3   5───9──13──17  ◄── Pinky MCP (17)                         │
│  │   │                                                          │
│  2   │                      ●  ◄── Centroid                     │
│  │   │                     ╱│╲    (average of 0, 5, 17)        │
│  1   │                    ╱ │ ╲                                 │
│  │   │                   ╱  │  ╲                                │
│  └───0  ◄── Wrist      0────5────17                            │
│      │                                                          │
│      Index MCP (5) ──►                                          │
│                                                                 │
│  Why these 3 points?                                            │
│  - Wrist (0): Base of hand                                      │
│  - Index MCP (5): One side of palm                              │
│  - Pinky MCP (17): Other side of palm                           │
│  - Together they form a triangle representing the palm          │
│  - Average = center of palm (stable point for tracking)         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Simple Explanation:** *To track swipe movements, we don't use a fingertip (too jittery) or the wrist (moves less than the hand). Instead, we use the CENTER of your palm - the average of three key points. This gives a stable position that moves with your whole hand.*

#### ROI Check for Static Gestures

```python
            # Check if hand is in ROI for static gestures
            from src import config
            in_roi = False
            if config.SIGN_ROI_ENABLED:
                roi = config.SIGN_ROI_COORDS
                in_roi = (roi['x_min'] <= cx <= roi['x_max']) and \
                         (roi['y_min'] <= cy <= roi['y_max'])
            else:
                in_roi = True  # ROI disabled, always allow

            # Draw ROI box on frame
            h, w, _ = frame.shape
            if config.SIGN_ROI_ENABLED:
                roi = config.SIGN_ROI_COORDS
                # Green if inside, Yellow if outside
                box_color = (0, 255, 0) if in_roi else (0, 255, 255)
                cv2.rectangle(frame,
                              (int(roi['x_min']*w), int(roi['y_min']*h)),
                              (int(roi['x_max']*w), int(roi['y_max']*h)),
                              box_color, 4)
                cv2.putText(frame, "Sign Zone",
                            (int(roi['x_min']*w)+5, int(roi['y_min']*h)+20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 1)
```

**ROI visualization on screen:**

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                     CAMERA FEED                           │ │
│  │                                                           │ │
│  │   FPS: 30  ●                                              │ │
│  │                                                           │ │
│  │                                                           │ │
│  │                         ✋ (Hand outside ROI)             │ │
│  │                              - Swipes work                │ │
│  │                              - Static gestures IGNORED    │ │
│  │                                                           │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │              SIGN ZONE (Yellow box)                 │ │ │
│  │  │                                                     │ │ │
│  │  │                       ✋ (Hand inside ROI)          │ │ │
│  │  │                           - Swipes work             │ │ │
│  │  │                           - Static gestures ACTIVE  │ │ │
│  │  │                           (Box turns GREEN)         │ │ │
│  │  │                                                     │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Gesture Classification Logic

```python
            if swipe_gesture != 'UNKNOWN':
                # Swipe detected - prioritize over static gestures
                final_gesture = swipe_gesture
                self.gesture_buffer.clear()  # Reset static tracking

            elif in_roi:
                # Check for static gestures (only if in ROI)
                raw_gesture = self._recognize_gesture()
                self.gesture_buffer.append(raw_gesture)

                if self.gesture_buffer:
                    from src import config
                    # Vote: find most common gesture in buffer
                    most_common = Counter(self.gesture_buffer).most_common(1)
                    gesture_name, count = most_common[0]

                    # Must appear in enough frames to confirm
                    if count >= config.GESTURE_CONFIRMATION_FRAMES:
                        # Check allowlist
                        if gesture_name in config.ENABLED_SIGNS:
                            final_gesture = gesture_name
                        else:
                            final_gesture = 'UNKNOWN'
                    else:
                        final_gesture = 'UNKNOWN'
            else:
                # Outside ROI - clear static gesture history
                self.gesture_buffer.clear()
```

**Gesture voting (temporal smoothing):**

```
┌─────────────────────────────────────────────────────────────────┐
│                    GESTURE VOTING SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Buffer size: 5 frames                                          │
│  Confirmation threshold: 2 frames                               │
│                                                                 │
│  Example 1 - Confirmed gesture:                                 │
│  ┌─────┬─────┬─────┬─────┬─────┐                               │
│  │ THB │ THB │ UNK │ THB │ THB │  Buffer contents               │
│  └─────┴─────┴─────┴─────┴─────┘                               │
│                                                                 │
│  Vote count: THUMBS_UP=4, UNKNOWN=1                            │
│  Most common: THUMBS_UP (4 times)                              │
│  4 >= 2 (threshold) → CONFIRMED: THUMBS_UP                     │
│                                                                 │
│  ───────────────────────────────────────────────────────────── │
│                                                                 │
│  Example 2 - Not confirmed (too few):                          │
│  ┌─────┬─────┬─────┬─────┬─────┐                               │
│  │ UNK │ UNK │ THB │ UNK │ V_S │  Buffer contents               │
│  └─────┴─────┴─────┴─────┴─────┘                               │
│                                                                 │
│  Vote count: UNKNOWN=3, THUMBS_UP=1, V_SIGN=1                  │
│  Most common: UNKNOWN (3 times)                                │
│  But we don't confirm UNKNOWN, so: No gesture                  │
│                                                                 │
│  ───────────────────────────────────────────────────────────── │
│                                                                 │
│  Example 3 - Flickering prevented:                             │
│  Without voting: THB→UNK→THB→UNK→THB (rapid switching!)        │
│  With voting: THB→THB→THB→THB→THB (stable output)              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Simple Explanation:** *Sometimes the gesture detection flickers between "thumbs up" and "unknown" very quickly. The voting system looks at the last 5 frames and picks the most common result. This prevents the gesture from rapidly switching on and off.*

#### Handling Lost Tracking

```python
    else:
        # No hand detected
        from src import config
        self.missed_frames += 1

        if self.missed_frames > config.MAX_MISSED_FRAMES:
            # Hand has been gone too long - reset everything
            self.gesture_buffer.clear()
            self.landmarks = None
            self.filtered_landmarks = None
            self.landmark_smoother.reset()
            self.pointer_smoother.reset()

    return final_gesture, frame, pointer_info, self.landmarks
```

**Debounce logic for lost tracking:**

```
Hand visible → Hand gone (frame 1) → Gone (frame 2) → ... → Gone (frame 5) → RESET

┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│  ✋  │  ✋  │  ❌  │  ❌  │  ❌  │  ❌  │  ❌  │  ❌  │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
   0     0     1     2     3     4     5     RESET!
                                        │
                                        └── missed_frames > MAX_MISSED_FRAMES (5)
                                            Clear buffers, reset smoothers

Why wait 5 frames?
- Hand might briefly go out of view
- Camera might miss a frame
- Blinking or temporary occlusion
- Don't want to reset too quickly!
```

---

### 5.6.4 Static Gesture Recognition - _recognize_gesture()

This is where the magic of recognizing hand shapes happens!

```python
def _recognize_gesture(self):
    """
    Recognizes static hand poses based on landmark positions.
    Uses rotation-invariant geometry for robustness.
    """
    if not self.landmarks:
        return 'UNKNOWN'

    wrist = self.landmarks[0]
```

#### Finger State Detection

```python
    # Robust Finger State Detection
    # Check if finger is extended by comparing distances to wrist
    def is_finger_extended(tip_idx, pip_idx):
        tip = self.landmarks[tip_idx]
        pip = self.landmarks[pip_idx]

        # Distance from tip to wrist
        d_tip_wrist = math.hypot(tip.x - wrist.x, tip.y - wrist.y)

        # Distance from PIP (middle joint) to wrist
        d_pip_wrist = math.hypot(pip.x - wrist.x, pip.y - wrist.y)

        # If tip is further from wrist than PIP, finger is extended
        return d_tip_wrist > d_pip_wrist
```

**The rotation-invariant trick:**

```
┌─────────────────────────────────────────────────────────────────┐
│                ROTATION-INVARIANT FINGER CHECK                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Traditional method (Y-coordinate):                             │
│  ─────────────────────────────────                              │
│  "Is tip.y < pip.y?" (Is tip above middle joint?)              │
│                                                                 │
│    Hand upright:        Hand sideways:       Hand upside down: │
│         8                    ─8                     │          │
│         │                   /                       │          │
│         6               ──6                         6          │
│         │             /                             │          │
│    tip.y < pip.y ✓   tip.y ≈ pip.y ✗          tip.y > pip.y ✗ │
│    WORKS!             FAILS!                    FAILS!         │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Our method (Distance to wrist):                                │
│  ──────────────────────────────                                 │
│  "Is tip further from wrist than pip?"                         │
│                                                                 │
│    Hand upright:        Hand sideways:       Hand upside down: │
│         8                    ─8                     │          │
│        ╱│                   ╱                      ╱│          │
│       ╱ 6               ──6                      ╱ 6          │
│      ╱  │             ╱                         ╱  │          │
│     ╱   │           ╱                          ╱   │          │
│    0    │          0                          0    8          │
│                                                                 │
│  d_tip > d_pip ✓    d_tip > d_pip ✓      d_tip > d_pip ✓      │
│  WORKS!              WORKS!                WORKS!              │
│                                                                 │
│  Key insight: Extended fingers are ALWAYS further from wrist   │
│               than bent fingers, regardless of hand rotation!   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Simple Explanation:** *The old way checks if fingertip is "above" the knuckle - but what's "above" if the hand is sideways? Our way measures DISTANCE from wrist. An extended finger is always farther from the wrist than a bent finger, no matter how the hand is rotated!*

#### Thumb State Detection

```python
    # Robust Thumb State
    thumb_tip = self.landmarks[4]
    thumb_ip = self.landmarks[3]    # Joint before tip
    pinky_mcp = self.landmarks[17]

    # Thumb extended if tip is further from pinky than IP joint
    d_tip_pinky = math.hypot(thumb_tip.x - pinky_mcp.x, thumb_tip.y - pinky_mcp.y)
    d_ip_pinky = math.hypot(thumb_ip.x - pinky_mcp.x, thumb_ip.y - pinky_mcp.y)

    thumb_extended = d_tip_pinky > d_ip_pinky

    # Check all other fingers
    index_extended = is_finger_extended(8, 6)
    middle_extended = is_finger_extended(12, 10)
    ring_extended = is_finger_extended(16, 14)
    pinky_extended = is_finger_extended(20, 18)
```

**Thumb detection uses different reference:**

```
Why use pinky_mcp for thumb instead of wrist?
──────────────────────────────────────────────

          8  12  16  20
          │   │   │   │
      4   │   │   │   │
      │   │   │   │   │
      3───5───9──13──17 ◄── Pinky MCP
      │   │
      2   │
      │   │
      1   │
      │   │
      └───0 ◄── Wrist

Problem with wrist reference:
- Thumb is on the SIDE of the hand
- When thumb moves out, distance to wrist doesn't change much

Solution - use pinky MCP:
- When thumb extends OUT, it moves AWAY from pinky
- d_tip_pinky increases significantly
- Much more reliable detection!
```

#### Gesture Decision Tree

```python
    # 1. OPEN_PALM: All fingers extended
    if thumb_extended and index_extended and middle_extended and ring_extended and pinky_extended:
        return 'OPEN_PALM'

    # 2. FIST: All fingers curled
    elif not thumb_extended and not index_extended and not middle_extended and not ring_extended and not pinky_extended:
        return 'FIST'

    # 3. INDEX_POINTING_UP: Only index extended
    elif not thumb_extended and index_extended and not middle_extended and not ring_extended and not pinky_extended:
        return 'INDEX_POINTING_UP'

    # 4. V_SIGN: Index and middle extended
    elif not thumb_extended and index_extended and middle_extended and not ring_extended and not pinky_extended:
        return 'V_SIGN'

    # 5. SPIDERMAN: Thumb, index, and pinky extended
    elif thumb_extended and index_extended and not middle_extended and not ring_extended and pinky_extended:
        return 'SPIDERMAN'

    # 6. OK_SIGN: Special check (thumb-index touching)
    elif self._is_ok_sign():
        return 'OK_SIGN'

    # 7. THUMBS_UP / THUMBS_DOWN: Only thumb extended
    elif thumb_extended and not index_extended and not middle_extended and not ring_extended and not pinky_extended:
        # Check thumb orientation
        if self.landmarks[4].y < self.landmarks[3].y:  # Tip above IP
            return 'THUMBS_UP'
        else:
            return 'THUMBS_DOWN'

    # 8. Check custom gestures
    custom_match = self.recorder.find_match(self.landmarks)
    if custom_match:
        return custom_match

    return 'UNKNOWN'
```

**Complete gesture decision table:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        GESTURE DECISION TABLE                               │
├───────────────┬───────┬───────┬────────┬──────┬───────┬─────────────────────┤
│ Gesture       │ Thumb │ Index │ Middle │ Ring │ Pinky │ Extra Condition     │
├───────────────┼───────┼───────┼────────┼──────┼───────┼─────────────────────┤
│ OPEN_PALM     │  ✓    │  ✓    │   ✓    │  ✓   │  ✓    │ -                   │
│ FIST          │  ✗    │  ✗    │   ✗    │  ✗   │  ✗    │ -                   │
│ INDEX_POINT   │  ✗    │  ✓    │   ✗    │  ✗   │  ✗    │ -                   │
│ V_SIGN        │  ✗    │  ✓    │   ✓    │  ✗   │  ✗    │ -                   │
│ SPIDERMAN     │  ✓    │  ✓    │   ✗    │  ✗   │  ✓    │ -                   │
│ OK_SIGN       │  -    │  -    │   ✓    │  ✓   │  ✓    │ thumb-index touch   │
│ THUMBS_UP     │  ✓    │  ✗    │   ✗    │  ✗   │  ✗    │ tip.y < ip.y        │
│ THUMBS_DOWN   │  ✓    │  ✗    │   ✗    │  ✗   │  ✗    │ tip.y > ip.y        │
└───────────────┴───────┴───────┴────────┴──────┴───────┴─────────────────────┘

✓ = Extended    ✗ = Curled    - = Don't care
```

#### OK Sign Detection

```python
def _is_ok_sign(self):
    """Special detection for OK sign (thumb-index circle)."""
    index_tip = self.landmarks[8]
    thumb_tip = self.landmarks[4]

    # Distance between thumb and index tips
    distance = math.sqrt(
        (index_tip.x - thumb_tip.x)**2 +
        (index_tip.y - thumb_tip.y)**2
    )

    # Check other fingers are extended
    def is_finger_extended(tip_idx, pip_idx):
        return self.landmarks[tip_idx].y < self.landmarks[pip_idx].y

    middle_extended = is_finger_extended(12, 10)
    ring_extended = is_finger_extended(16, 14)
    pinky_extended = is_finger_extended(20, 18)

    # OK sign: thumb-index close + other fingers extended
    return distance < 0.08 and middle_extended and ring_extended and pinky_extended
```

**OK sign detection visualized:**

```
┌─────────────────────────────────────────────────────────────────┐
│                      OK SIGN DETECTION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Correct OK Sign:                                               │
│                                                                 │
│              12   16   20     ← Extended fingers (up)           │
│              │    │    │                                        │
│              11   15   19                                       │
│              │    │    │                                        │
│    4●───●8   10   14   18                                       │
│     ╲   ╱    │    │    │                                        │
│      ╲ ╱     9────13───17                                       │
│       ○      │                                                  │
│    Circle!   │                                                  │
│              0                                                  │
│                                                                 │
│  Checks:                                                        │
│  1. distance(4, 8) < 0.08  ← Thumb and index touching          │
│  2. middle_extended = True  ← Finger pointing up                │
│  3. ring_extended = True    ← Finger pointing up                │
│  4. pinky_extended = True   ← Finger pointing up                │
│                                                                 │
│  All conditions TRUE → OK_SIGN detected!                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 5.6.5 Resource Cleanup

```python
def close(self):
    """Releases MediaPipe hand tracking resources."""
    self.hands.close()
```

**Simple Explanation:** *When we're done, we need to tell MediaPipe to release its memory and resources. It's like turning off the lights when you leave a room - good practice to clean up!*

---

## 5.7 Chapter Summary (Part 3)

In this part, we examined the Gesture Engine module in detail:

### MediaPipe Integration
- Configured hand detection with appropriate confidence thresholds
- Extracted 21 hand landmarks per frame
- Drew landmarks on frame for visual feedback

### Frame Processing Pipeline
1. Flip frame horizontally (mirror effect)
2. Apply CLAHE low-light enhancement
3. Run MediaPipe hand detection
4. Smooth landmark positions
5. Calculate hand centroid
6. Check for swipes (dynamic gestures)
7. Check for static gestures (if in ROI)
8. Apply temporal voting for confirmation
9. Return final gesture

### Gesture Recognition Algorithms
- **Rotation-invariant finger detection**: Uses distance to wrist instead of Y-coordinates
- **Thumb detection**: Uses distance to pinky MCP for reliable detection
- **Gesture decision tree**: Clear logic for each of 8 gestures
- **OK sign special case**: Detects thumb-index circle formation

### Key Concepts Learned
- **CLAHE**: Adaptive contrast enhancement for low-light
- **Rotation invariance**: Making detection work regardless of hand orientation
- **Temporal voting**: Smoothing gesture output over multiple frames
- **ROI filtering**: Preventing accidental gesture triggers
- **Debouncing**: Handling temporary hand disappearance gracefully

**Next:** Part 4 will cover the Swipe Detection and Position Smoothing modules.

---

*[End of Chapter 5 - Part 3]*

---
