# Chapter 5: Implementation (Part 4)
## Swipe Detection & Position Smoothing

---

## 5.7 Swipe Engine Module (swipe_engine.py)

The Swipe Engine is responsible for detecting dynamic hand movements - specifically left and right swipe gestures. Unlike static gestures that analyze a single frame, swipe detection requires analyzing the **trajectory** of hand movement over time.

### 5.7.1 Module Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SWIPE ENGINE                              │
├─────────────────────────────────────────────────────────────┤
│  Input: Hand centroid position (x, y) + timestamp           │
│                                                             │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │  Trajectory │ -> │   Linear     │ -> │   Swipe      │   │
│  │   Tracking  │    │  Regression  │    │  Validation  │   │
│  └─────────────┘    └──────────────┘    └──────────────┘   │
│                                                             │
│  Output: 'SWIPE_LEFT', 'SWIPE_RIGHT', or 'UNKNOWN'         │
└─────────────────────────────────────────────────────────────┘
```

### 5.7.2 SwipeDetector Class

```python
class SwipeDetector:
    """
    Robust Swipe Detector using Least Squares Regression.

    Uses numpy.polyfit to analyze the geometric properties
    of the hand trajectory.
    """
    def __init__(self, history_length=15, min_dist_left=0.10,
                 min_dist_right=0.10, min_velocity=0.3):
        self.history = deque(maxlen=history_length)
        self.min_dist_left = min_dist_left
        self.min_dist_right = min_dist_right
        self.min_velocity = min_velocity
        self.cooldown = 0.3
        self.last_swipe_time = 0

        # Constraints
        self.MAX_SLOPE = 1.0      # Max slope (45 degrees)
        self.MAX_MSE = 0.02       # Max Mean Squared Error
        self.MAX_Y_VARIANCE = 0.1 # Max vertical variance
```

#### Constructor Parameters Explained

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `history_length` | 15 | Number of positions to remember |
| `min_dist_left` | 0.10 | Minimum distance for left swipe (10% of frame) |
| `min_dist_right` | 0.10 | Minimum distance for right swipe |
| `min_velocity` | 0.3 | Minimum speed threshold |

---

### 5.7.3 Trajectory Tracking with Deque

```
┌─────────────────────────────────────────────────────────────┐
│ TRAJECTORY HISTORY (deque with maxlen=15)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Frame 1    Frame 2    Frame 3    ...    Frame 15          │
│  (x,y,t) -> (x,y,t) -> (x,y,t) -> ... -> (x,y,t)          │
│                                                             │
│  When new point arrives and deque is full:                  │
│  - Oldest point automatically removed                       │
│  - New point added at the end                               │
│                                                             │
│  Example of a RIGHT SWIPE trajectory:                       │
│                                                             │
│     (0.2, 0.5) -> (0.3, 0.5) -> (0.5, 0.5) -> (0.7, 0.5)   │
│        |              |              |              |       │
│        +-- X increases from left to right -----------+      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Simple Explanation:**
> Imagine leaving footprints as you walk. The deque (pronounced "deck") is like
> keeping track of your last 15 footprints. When you take a new step, your oldest
> footprint disappears. By looking at the pattern of footprints, we can tell
> which direction you're walking!

### 5.7.4 The process() Method - Complete Walkthrough

```python
def process(self, centroid, timestamp):
    """
    Input: centroid (x, y) normalized 0.0-1.0, timestamp (seconds)
    Output: 'SWIPE_LEFT', 'SWIPE_RIGHT', or 'UNKNOWN'
    """
```

#### Stage 0: Cooldown Check

```python
# Prevent rapid-fire detections
if timestamp - self.last_swipe_time < self.cooldown:
    pass  # Keep tracking but don't trigger yet
```

This prevents detecting multiple swipes from a single gesture.

#### Stage 1: Build History

```python
# Add current position to trajectory
self.history.append((centroid[0], centroid[1], timestamp))

# Need at least 5 points for reliable analysis
if len(self.history) < 5:
    return 'UNKNOWN'
```

#### Stage 2: Extract Data

```python
# Convert to numpy array for math operations
data = np.array(self.history)
xs = data[:, 0]  # All X coordinates
ys = data[:, 1]  # All Y coordinates
ts = data[:, 2]  # All timestamps

# Calculate movement vectors
start_x, start_y = xs[0], ys[0]
end_x, end_y = xs[-1], ys[-1]

dx = end_x - start_x  # Total horizontal movement
dy = end_y - start_y  # Total vertical movement
dist_x = abs(dx)      # Absolute horizontal distance
```

```
┌─────────────────────────────────────────────────────────────┐
│ DATA EXTRACTION EXAMPLE                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  History: [(0.2, 0.5, 1.0), (0.4, 0.52, 1.1), (0.7, 0.5, 1.2)]
│                                                             │
│  xs = [0.2, 0.4, 0.7]   <- X positions                      │
│  ys = [0.5, 0.52, 0.5]  <- Y positions                      │
│  ts = [1.0, 1.1, 1.2]   <- Timestamps                       │
│                                                             │
│  start_x = 0.2, end_x = 0.7                                 │
│  dx = 0.7 - 0.2 = 0.5 (positive = moving RIGHT)            │
│  dist_x = 0.5 (50% of frame width)                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Stage 3: Fast Rejection Checks

These are computationally "cheap" checks done first:

**A. Velocity Check:**
```python
duration = ts[-1] - ts[0]  # Time elapsed
if duration < 0.05:
    return 'UNKNOWN'  # Too fast to analyze

velocity_x = dist_x / duration

if velocity_x < self.min_velocity:
    return 'UNKNOWN'  # Movement too slow
```

**B. Distance Check:**
```python
# Different thresholds for left vs right
target_dist = self.min_dist_right if dx > 0 else self.min_dist_left
if dist_x < target_dist:
    return 'UNKNOWN'  # Didn't move far enough
```

**C. Vertical Variance Check:**
```python
if np.std(ys) > self.MAX_Y_VARIANCE:
    return 'UNKNOWN'  # Too much up/down movement
```

```
┌─────────────────────────────────────────────────────────────┐
│ VALID SWIPE vs INVALID MOVEMENT                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  VALID (Low Y Variance):          INVALID (High Y Variance):│
│                                                             │
│  Y                                Y                         │
│  │    • • • • •                   │    •                    │
│  │  ─────────────→ X              │      •   •              │
│                                   │        •   •   •        │
│  Straight horizontal line         │  ───────────────→ X     │
│  std(ys) ≈ 0.01                   │  Wavy movement          │
│                                   │  std(ys) ≈ 0.15         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 5.7.5 Linear Regression Analysis

This is the "smart" part of swipe detection - using mathematics to verify the trajectory is a straight line.

#### Understanding numpy.polyfit

```python
# Fit a line: y = mx + c
slope, intercept = np.polyfit(xs, ys, 1)
```

**Simple Explanation:**
> Imagine all the trajectory points as dots on a piece of paper. `polyfit`
> draws the "best fit" straight line through all those dots. The `slope`
> tells us the angle of that line (steep or flat), and `intercept` tells
> us where it crosses the Y axis.

```
┌─────────────────────────────────────────────────────────────┐
│ LINEAR REGRESSION VISUALIZATION                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Y                                                          │
│  │           • actual points                                │
│  │      •  ────────────  fitted line                        │
│  │   •     •     •                                          │
│  │                                                          │
│  └──────────────────────────→ X                             │
│                                                             │
│  The "best fit" line minimizes the total distance           │
│  between the line and all the actual points.                │
│                                                             │
│  Formula: y = slope * x + intercept                         │
│                                                             │
│  Example:                                                   │
│  - slope = 0.1 means slightly upward                        │
│  - slope = 0 means perfectly horizontal                     │
│  - slope = -0.1 means slightly downward                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Slope Validation

```python
# D. Slope Check - Reject diagonal movements
if abs(slope) > self.MAX_SLOPE:  # MAX_SLOPE = 1.0 (45 degrees)
    print(f"DEBUG: Swipe Rejected. Slope too steep: {abs(slope):.2f}")
    return 'UNKNOWN'
```

```
┌─────────────────────────────────────────────────────────────┐
│ SLOPE INTERPRETATION                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Slope = 0      Slope = 0.5      Slope = 1.0     Slope > 1  │
│                                                             │
│     ────        ───╱             ╱               │          │
│                   ╱             ╱                │          │
│  Horizontal    Slight        45° angle      Too diagonal   │
│  (Perfect)     diagonal      (Max allowed)  (REJECTED)     │
│                                                             │
│  ACCEPTED      ACCEPTED      ACCEPTED        REJECTED       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Mean Squared Error (MSE) Calculation

```python
# E. Linearity Check - How well do points fit the line?
predicted_ys = slope * xs + intercept
mse = np.mean((ys - predicted_ys)**2)

if mse > self.MAX_MSE:  # MAX_MSE = 0.02
    print(f"DEBUG: Swipe Rejected. Too wavy (MSE): {mse:.4f}")
    return 'UNKNOWN'
```

**Simple Explanation:**
> MSE measures how "wobbly" the trajectory is. If you drew a straight line
> through all the points, MSE tells you how far the actual points are from
> that line, on average. Lower MSE = straighter path = more likely a swipe.

```
┌─────────────────────────────────────────────────────────────┐
│ MSE (MEAN SQUARED ERROR) EXPLAINED                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: For each point, calculate the error                │
│                                                             │
│       actual_y - predicted_y = error                        │
│                                                             │
│  Step 2: Square each error (makes all values positive)      │
│                                                             │
│       error² = squared_error                                │
│                                                             │
│  Step 3: Calculate mean (average) of all squared errors     │
│                                                             │
│       MSE = (error1² + error2² + ... + errorN²) / N         │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  LOW MSE (Straight):           HIGH MSE (Wavy):             │
│                                                             │
│  •──•──•──•──•                    •                         │
│                                 •   •                       │
│  predicted = actual             •     •   •                 │
│  errors ≈ 0                           •                     │
│  MSE ≈ 0.001                    errors large                │
│                                 MSE ≈ 0.05                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.7.6 Triggering the Swipe

If all checks pass:

```python
# Clear history to start fresh for next gesture
self.history.clear()
self.last_swipe_time = timestamp

# Determine direction based on dx sign
if dx > 0:
    return 'SWIPE_RIGHT'  # Moved left-to-right
else:
    return 'SWIPE_LEFT'   # Moved right-to-left
```

### 5.7.7 Complete Detection Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ SWIPE DETECTION PIPELINE                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Receive new position (x, y, timestamp)                  │
│              │                                              │
│              ▼                                              │
│  2. Check cooldown (0.3s since last swipe?)                 │
│              │ NO → Continue tracking                       │
│              │ YES                                          │
│              ▼                                              │
│  3. Add to history deque                                    │
│              │                                              │
│              ▼                                              │
│  4. Check minimum points (< 5?) ─── YES ──→ Return UNKNOWN  │
│              │ NO                                           │
│              ▼                                              │
│  5. FAST REJECTION CHECKS:                                  │
│     ├─ Velocity < threshold? ─── YES ──→ Return UNKNOWN     │
│     ├─ Distance < minimum?   ─── YES ──→ Return UNKNOWN     │
│     └─ Y variance > max?     ─── YES ──→ Return UNKNOWN     │
│              │ ALL PASSED                                   │
│              ▼                                              │
│  6. GEOMETRIC ANALYSIS:                                     │
│     ├─ Fit line with polyfit                                │
│     ├─ Slope > 1.0 (45°)?    ─── YES ──→ Return UNKNOWN     │
│     └─ MSE > 0.02?           ─── YES ──→ Return UNKNOWN     │
│              │ ALL PASSED                                   │
│              ▼                                              │
│  7. SWIPE CONFIRMED!                                        │
│     ├─ Clear history                                        │
│     ├─ Update last_swipe_time                               │
│     └─ Return SWIPE_LEFT or SWIPE_RIGHT                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5.8 Position Smoother Module (position_smoother.py)

The Position Smoother module reduces jitter in hand tracking, making gestures feel more stable and natural. It uses a **Kalman Filter-like approach** for prediction and smoothing.

### 5.8.1 Why Smoothing is Necessary

```
┌─────────────────────────────────────────────────────────────┐
│ THE JITTER PROBLEM                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Raw MediaPipe Output:        After Smoothing:              │
│                                                             │
│       •                                                     │
│     •   •                         • • • • • •               │
│   •       •   •                                             │
│             •                    Smooth, stable path        │
│                                                             │
│  Even when hand is still,       Smoother removes the        │
│  coordinates "jump around"      noise and creates a         │
│  due to camera noise and        fluid trajectory            │
│  detection uncertainty                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Simple Explanation:**
> Imagine trying to trace a line while riding in a bumpy car. Your hand
> might be aiming for a straight line, but the bumps make it wobbly.
> The smoother is like having a stabilizer that removes the bumps!

### 5.8.2 PositionSmoother2D Class

This is the core smoothing class that tracks a single 2D point.

```python
class PositionSmoother2D:
    """
    A 2D position smoother for tracking hand position (x, y).
    Uses velocity-aware prediction for smooth tracking.
    """

    def __init__(self, smoothing_factor=0.01, responsiveness=0.1):
        # State vector: [x, y, vx, vy] (position and velocity)
        self.state = np.zeros(4)
```

#### The State Vector

The smoother tracks 4 values:

```
┌─────────────────────────────────────────────────────────────┐
│ STATE VECTOR: [x, y, vx, vy]                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  state[0] = x   → Current X position                        │
│  state[1] = y   → Current Y position                        │
│  state[2] = vx  → Velocity in X direction (speed + direction)
│  state[3] = vy  → Velocity in Y direction                   │
│                                                             │
│  By tracking velocity, we can PREDICT where the hand        │
│  will be in the next frame!                                 │
│                                                             │
│  Example:                                                   │
│  state = [0.5, 0.3, 0.02, 0.0]                             │
│                                                             │
│  Means: Hand is at (0.5, 0.3) and moving right              │
│         (vx = 0.02 per frame, vy = 0)                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.8.3 The State Transition Matrix (F)

```python
self.dt = 1.0 / 30.0  # Assume ~30 FPS

self.F = np.array([
    [1, 0, self.dt, 0],      # new_x = x + vx * dt
    [0, 1, 0, self.dt],      # new_y = y + vy * dt
    [0, 0, 1, 0],            # new_vx = vx (velocity persists)
    [0, 0, 0, 1]             # new_vy = vy
])
```

**Simple Explanation:**
> The F matrix is like a "physics rule" that says: "If something is moving
> in a direction, it will probably keep moving that direction." This is
> called **inertia**. The matrix calculates where we expect the hand to be
> based on its current position and speed.

```
┌─────────────────────────────────────────────────────────────┐
│ STATE TRANSITION VISUALIZATION                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Current State:                 Predicted Next State:       │
│  x = 0.5                        x' = 0.5 + 0.02*(1/30)      │
│  y = 0.3                        x' ≈ 0.5007                 │
│  vx = 0.02                                                  │
│  vy = 0.0                       (Hand moved slightly right) │
│                                                             │
│      Current          Predicted                             │
│         ●─────────────────●                                 │
│         │     dt          │                                 │
│         │                 │                                 │
│     position          position                              │
│     + velocity        after dt                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.8.4 The Measurement Matrix (H)

```python
self.H = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0]
])
```

This matrix extracts only the position (x, y) from the full state, because our camera measurement only gives us position - not velocity.

### 5.8.5 Noise Matrices (Q and R)

```python
# Process noise (Q) - How much we expect state to change
self.Q = np.eye(4) * smoothing_factor  # 0.01

# Measurement noise (R) - How much we trust measurements
self.R = np.eye(2) * responsiveness    # 0.1
```

**Simple Explanation:**
> Think of Q and R as "trust levels":
> - **Q (Process Noise)**: How much do we trust our prediction model?
>   Lower = trust model more = smoother output
> - **R (Measurement Noise)**: How much do we trust the camera?
>   Higher = trust camera less = more smoothing

```
┌─────────────────────────────────────────────────────────────┐
│ SMOOTHING vs RESPONSIVENESS TRADE-OFF                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Low Q, High R:              High Q, Low R:                 │
│  "Trust the model"           "Trust the camera"             │
│                                                             │
│  - Very smooth output        - Follows raw data closely     │
│  - Slow to react             - Quick to react               │
│  - Filters out noise         - May include noise            │
│                                                             │
│  Good for: Stable pointer    Good for: Fast gestures        │
│                                                             │
│  The default values (Q=0.01, R=0.1) balance both.           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.8.6 The Predict Step

```python
def predict(self):
    """Predict the next position based on current velocity."""
    if not self.initialized:
        return None

    # State prediction: new_state = F * state
    self.state = self.F @ self.state

    # Covariance prediction: new_P = F * P * F^T + Q
    self.P = self.F @ self.P @ self.F.T + self.Q

    return self.state[0], self.state[1]
```

**Simple Explanation:**
> Prediction is like saying "If the hand was moving right, I bet it's still
> moving right." We use the velocity to guess where the hand will be, even
> before we get the next camera frame.

### 5.8.7 The Update Step

```python
def update(self, measurement):
    """Update the position with a new measurement."""
    z = np.array(measurement)

    if not self.initialized:
        # First measurement - initialize state
        self.state[0] = z[0]  # x
        self.state[1] = z[1]  # y
        self.state[2] = 0     # vx = 0
        self.state[3] = 0     # vy = 0
        self.initialized = True
        return z[0], z[1]

    # Predict first
    self.predict()

    # Measurement residual (innovation)
    y = z - self.H @ self.state  # difference between actual and predicted

    # Residual covariance
    S = self.H @ self.P @ self.H.T + self.R

    # Kalman gain
    K = self.P @ self.H.T @ np.linalg.inv(S)

    # State update: blend prediction with measurement
    self.state = self.state + K @ y

    # Covariance update
    self.P = (self.I - K @ self.H) @ self.P

    return self.state[0], self.state[1]
```

```
┌─────────────────────────────────────────────────────────────┐
│ KALMAN UPDATE VISUALIZATION                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. PREDICT where hand should be (based on velocity)        │
│                                                             │
│       Predicted ●────────────?                              │
│                                                             │
│  2. MEASURE where camera says hand is                       │
│                                                             │
│       Predicted ●              ○ Measurement                │
│                  ↖─────gap─────↗                            │
│                                                             │
│  3. BLEND prediction and measurement                        │
│     (Kalman Gain determines the blend ratio)                │
│                                                             │
│       Predicted ●───K──●───────○ Measurement                │
│                        ↑                                    │
│                   Final Result                              │
│                   (Smoothed Position)                       │
│                                                             │
│  If K is small: Trust prediction more (smoother)            │
│  If K is large: Trust measurement more (responsive)         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.8.8 LandmarkSmoother Class

This class manages 21 individual smoothers - one for each MediaPipe hand landmark.

```python
class LandmarkSmoother:
    """
    Smoothing manager for multiple hand landmarks.
    Provides stable tracking for all 21 hand landmarks.
    """

    def __init__(self, num_landmarks=21, smoothing_factor=0.005,
                 responsiveness=0.05):
        self.smoothers = [
            PositionSmoother2D(smoothing_factor, responsiveness)
            for _ in range(num_landmarks)
        ]
        self.num_landmarks = num_landmarks
```

```
┌─────────────────────────────────────────────────────────────┐
│ LANDMARK SMOOTHER ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LandmarkSmoother                                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  smoother[0]  ← Wrist                                │   │
│  │  smoother[1]  ← Thumb CMC                            │   │
│  │  smoother[2]  ← Thumb MCP                            │   │
│  │  smoother[3]  ← Thumb IP                             │   │
│  │  smoother[4]  ← Thumb Tip                            │   │
│  │  smoother[5]  ← Index MCP                            │   │
│  │  smoother[6]  ← Index PIP                            │   │
│  │  smoother[7]  ← Index DIP                            │   │
│  │  smoother[8]  ← Index Tip                            │   │
│  │  ...                                                 │   │
│  │  smoother[20] ← Pinky Tip                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Each landmark has its own independent smoother!            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Update Method

```python
def update(self, landmarks):
    """
    Update all landmark positions with smoothing.

    Args:
        landmarks: List of landmark objects with .x, .y attributes

    Returns:
        List of smoothed (x, y) tuples
    """
    smoothed = []
    for i, lm in enumerate(landmarks):
        if i < self.num_landmarks:
            sx, sy = self.smoothers[i].update((lm.x, lm.y))
            smoothed.append((sx, sy))
    return smoothed
```

### 5.8.9 PointerSmoother Class

A specialized smoother for mouse pointer control with **adaptive smoothing**.

```python
class PointerSmoother:
    """
    Specialized smoother for mouse pointer control.
    Uses adaptive smoothing based on movement speed.
    """

    def __init__(self, base_smoothing=0.02, base_responsiveness=0.08):
        self.smoother = PositionSmoother2D(base_smoothing, base_responsiveness)
        self.last_position = None
```

#### Adaptive Smoothing Logic

```python
def update(self, x, y):
    """
    When moving fast: Less smoothing for responsiveness
    When stationary/slow: More smoothing for stability
    """
    if self.last_position is not None:
        dx = x - self.last_position[0]
        dy = y - self.last_position[1]
        speed = np.sqrt(dx**2 + dy**2)

        # Adjust responsiveness based on speed
        if speed > 0.05:      # Fast movement
            self.smoother.R = np.eye(2) * (self.base_responsiveness * 0.3)
        elif speed > 0.02:    # Medium movement
            self.smoother.R = np.eye(2) * self.base_responsiveness
        else:                 # Slow/stationary
            self.smoother.R = np.eye(2) * (self.base_responsiveness * 2.0)

    self.last_position = (x, y)
    return self.smoother.update((x, y))
```

```
┌─────────────────────────────────────────────────────────────┐
│ ADAPTIVE SMOOTHING BEHAVIOR                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FAST MOVEMENT (speed > 0.05):                              │
│  ┌───────────────────────────────────────────────┐         │
│  │  R = 0.024 (low - trust measurements more)    │         │
│  │  Result: Quick, responsive tracking           │         │
│  │  Good for: Fast swipes, quick movements       │         │
│  └───────────────────────────────────────────────┘         │
│                                                             │
│  MEDIUM MOVEMENT (0.02 < speed < 0.05):                     │
│  ┌───────────────────────────────────────────────┐         │
│  │  R = 0.08 (default)                           │         │
│  │  Result: Balanced tracking                    │         │
│  │  Good for: Normal gestures                    │         │
│  └───────────────────────────────────────────────┘         │
│                                                             │
│  SLOW/STATIONARY (speed < 0.02):                            │
│  ┌───────────────────────────────────────────────┐         │
│  │  R = 0.16 (high - trust measurements less)    │         │
│  │  Result: Very smooth, stable tracking         │         │
│  │  Good for: Holding pointer still              │         │
│  └───────────────────────────────────────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Simple Explanation:**
> When you're moving your hand fast, you want the cursor to follow quickly.
> But when you're trying to hold still (like clicking a small button), you
> want extra smoothing to prevent jitter. Adaptive smoothing automatically
> adjusts based on how fast you're moving!

---

## 5.9 Summary: Swipe & Smoothing Integration

```
┌─────────────────────────────────────────────────────────────┐
│ HOW SWIPE AND SMOOTHING WORK TOGETHER                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Camera captures raw frame                               │
│              │                                              │
│              ▼                                              │
│  2. MediaPipe detects hand landmarks (21 points)            │
│              │                                              │
│              ▼                                              │
│  3. LandmarkSmoother smooths all 21 points                  │
│     (Reduces jitter in finger positions)                    │
│              │                                              │
│              ▼                                              │
│  4. Calculate hand centroid from smoothed landmarks         │
│              │                                              │
│              ▼                                              │
│  5. SwipeDetector.process(centroid, timestamp)              │
│     (Analyzes trajectory over 15 frames)                    │
│              │                                              │
│              ▼                                              │
│  6. If swipe detected → Execute keyboard shortcut           │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Key Insight: Smoothing happens BEFORE swipe detection!     │
│  This gives the swipe detector cleaner data to analyze.     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5.10 Key Algorithms Summary Table

| Algorithm | Purpose | Key Parameters |
|-----------|---------|----------------|
| **Linear Regression** | Verify swipe trajectory is a straight line | MAX_SLOPE=1.0, MAX_MSE=0.02 |
| **Deque Tracking** | Store last N positions for analysis | history_length=15 |
| **Kalman-like Filter** | Smooth noisy position data | Q=0.01, R=0.1 |
| **Adaptive Smoothing** | Adjust smoothing based on speed | speed thresholds: 0.02, 0.05 |
| **Velocity Estimation** | Predict next position from movement | dt=1/30 (30 FPS) |

---

*End of Chapter 5, Part 4*

**Next: Part 5 - User Interface (ui_manager.py)**
