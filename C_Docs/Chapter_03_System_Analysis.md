# CHAPTER 3: SYSTEM ANALYSIS AND REQUIREMENTS

---

## 3.1 Introduction

Before building any software system, we must carefully analyze what the system needs to do and what resources it requires. This chapter documents the systematic analysis of requirements for the Air Gesture Shortcut Controller.

**Simple Explanation:** *Before building a house, you need a plan. What rooms do you need? How many windows? Where does the door go? System analysis is the same thing - figuring out exactly what our software needs to do before we start coding!*

---

## 3.2 System Overview

### 3.2.1 What the System Does

The Air Gesture Shortcut Controller is a desktop application that:

1. **Captures** live video from a webcam
2. **Detects** hands in the video stream
3. **Recognizes** specific hand gestures (both static poses and dynamic movements)
4. **Executes** keyboard shortcuts based on recognized gestures
5. **Provides** visual and audio feedback to the user

### 3.2.2 System Context Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL ENVIRONMENT                          │
│                                                                         │
│    ┌──────────┐                                      ┌──────────────┐  │
│    │  WEBCAM  │                                      │  OTHER APPS  │  │
│    │ (Camera) │                                      │ (PowerPoint, │  │
│    └────┬─────┘                                      │   Chrome)    │  │
│         │ Video                                      └──────▲───────┘  │
│         │ Stream                                            │          │
│         ▼                                                   │ Keyboard │
│    ┌────────────────────────────────────────────────┐      │ Commands │
│    │                                                │      │          │
│    │       AIR GESTURE SHORTCUT CONTROLLER          │──────┘          │
│    │                                                │                  │
│    │    ┌─────────┐  ┌─────────┐  ┌─────────┐      │                  │
│    │    │ Gesture │  │ Gesture │  │Shortcut │      │                  │
│    │    │Detection│─▶│Recognition─▶│Execution│      │                  │
│    │    └─────────┘  └─────────┘  └─────────┘      │                  │
│    │                                                │                  │
│    └───────────────────┬────────────────────────────┘                  │
│                        │                                               │
│                        ▼                                               │
│                   ┌─────────┐                                          │
│                   │  USER   │                                          │
│                   │(Sees UI,│                                          │
│                   │ Makes   │                                          │
│                   │Gestures)│                                          │
│                   └─────────┘                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Simple Explanation:** *This diagram shows who and what talks to our system. The camera sends pictures in, the user sees feedback and makes gestures, and our system sends keyboard commands to other programs like PowerPoint.*

---

## 3.3 Functional Requirements

Functional requirements describe **what the system must do** - the specific features and functions it must provide.

### 3.3.1 Requirements Table

| ID | Requirement | Description | Priority |
|----|-------------|-------------|----------|
| **FR01** | Camera Capture | System shall capture live video from a connected webcam | High |
| **FR02** | Camera Selection | System shall allow user to select from multiple connected cameras | Medium |
| **FR03** | Hand Detection | System shall detect the presence of a human hand in the video frame | High |
| **FR04** | Landmark Tracking | System shall track 21 landmark points on the detected hand | High |
| **FR05** | Static Gesture Recognition | System shall recognize at least 7 different static hand poses | High |
| **FR06** | Dynamic Gesture Recognition | System shall recognize swipe gestures (left and right) | High |
| **FR07** | Keyboard Shortcut Execution | System shall execute configurable keyboard shortcuts when gestures are recognized | High |
| **FR08** | Visual Feedback | System shall display the camera feed with hand tracking overlay | Medium |
| **FR09** | Gesture Notification | System shall display on-screen notification when a gesture is recognized | Medium |
| **FR10** | Audio Feedback | System shall play sound effects when gestures are recognized | Low |
| **FR11** | Profile Management | System shall support multiple gesture-to-shortcut mapping profiles | Medium |
| **FR12** | Auto Profile Switching | System shall automatically switch profiles based on active application | Medium |
| **FR13** | Settings Interface | System shall provide a GUI for adjusting detection settings | Medium |
| **FR14** | Gesture Enable/Disable | System shall allow users to enable or disable specific gestures | Medium |
| **FR15** | Configuration Persistence | System shall save and load user settings between sessions | Medium |
| **FR16** | Overlay Mode | System shall support a compact overlay mode for minimal screen usage | Low |
| **FR17** | Low-Light Enhancement | System shall enhance video in low-light conditions for better detection | Low |
| **FR18** | Mouse Control | System shall optionally allow hand-based mouse pointer control | Low |

### 3.3.2 Detailed Functional Requirements

#### FR01: Camera Capture

**Description:** The system must be able to access and capture video from a standard USB webcam or built-in laptop camera.

**Acceptance Criteria:**
- System opens camera within 3 seconds of user pressing "Start"
- Video is captured at minimum 720p resolution (1280x720)
- Video is captured at minimum 15 frames per second
- System handles camera disconnection gracefully

**Simple Explanation:** *When you click "Start," the system turns on your camera and starts watching what it sees, just like opening a video call app.*

---

#### FR02: Camera Selection

**Description:** When multiple cameras are connected, users must be able to choose which camera to use.

**Acceptance Criteria:**
- System detects all connected cameras on startup
- Dropdown menu displays available cameras
- Changing camera selection restarts capture with new camera
- System remembers last selected camera

---

#### FR03: Hand Detection

**Description:** The system must identify when a human hand is present in the camera's field of view.

**Acceptance Criteria:**
- Detects hand within 500ms of it appearing in frame
- Works with hands of different sizes and skin tones
- Distinguishes hand from similar-colored backgrounds
- Indicates hand detection status to user (visual indicator)

**Simple Explanation:** *The system plays "I Spy" with your hand - as soon as it sees a hand in the picture, it says "Found it!" and starts watching it closely.*

---

#### FR04: Landmark Tracking

**Description:** Once a hand is detected, the system must track 21 specific points on the hand.

**Acceptance Criteria:**
- All 21 MediaPipe hand landmarks are tracked
- Landmark positions update each frame
- Positions are smoothed to reduce jitter
- Landmarks are drawn on the display for visual feedback

```
The 21 landmarks:
- 0: Wrist
- 1-4: Thumb joints (CMC, MCP, IP, TIP)
- 5-8: Index finger joints (MCP, PIP, DIP, TIP)
- 9-12: Middle finger joints
- 13-16: Ring finger joints
- 17-20: Pinky finger joints
```

---

#### FR05: Static Gesture Recognition

**Description:** The system must recognize these static hand poses:

| Gesture | Description | Visual |
|---------|-------------|--------|
| THUMBS_UP | Thumb extended upward, other fingers curled | 👍 |
| THUMBS_DOWN | Thumb extended downward, other fingers curled | 👎 |
| OPEN_PALM | All five fingers extended and spread | ✋ |
| OK_SIGN | Thumb and index finger forming circle, others extended | 👌 |
| V_SIGN | Index and middle fingers extended in V shape | ✌️ |
| INDEX_POINTING_UP | Only index finger extended upward | ☝️ |
| SPIDERMAN | Thumb, index, and pinky extended | 🤟 |

**Acceptance Criteria:**
- Each gesture recognized with >85% accuracy under normal conditions
- Recognition occurs within 100ms of gesture being formed
- False positive rate <5% during normal hand movement
- Gestures only recognized when hand is in designated region (ROI)

---

#### FR06: Dynamic Gesture Recognition

**Description:** The system must recognize movement-based gestures:

| Gesture | Description | Movement |
|---------|-------------|----------|
| SWIPE_LEFT | Hand moves from right to left | ←←← |
| SWIPE_RIGHT | Hand moves from left to right | →→→ |

**Acceptance Criteria:**
- Swipe detected when hand moves >10% of screen width
- Swipe speed must exceed minimum velocity threshold
- Movement must be relatively straight (not zigzag)
- Cooldown prevents multiple detections from single swipe

**Simple Explanation:** *If you move your hand across the screen like you're brushing crumbs off a table, the system recognizes that as a "swipe" and can trigger an action like going to the next slide.*

---

#### FR07: Keyboard Shortcut Execution

**Description:** When a gesture is recognized, the system must simulate keyboard key presses.

**Acceptance Criteria:**
- Supports single key presses (e.g., "Right Arrow")
- Supports key combinations (e.g., "Ctrl+Tab")
- Shortcuts execute within 50ms of gesture recognition
- Shortcuts are sent to the active/foreground window

**Default Gesture-Shortcut Mappings:**

| Gesture | Default Shortcut | Action |
|---------|-----------------|--------|
| SWIPE_RIGHT | Right Arrow | Next slide/page |
| SWIPE_LEFT | Left Arrow | Previous slide/page |
| THUMBS_UP | Right Arrow | Next (alternative) |
| THUMBS_DOWN | Left Arrow | Previous (alternative) |
| OPEN_PALM | F5 | Start presentation |
| OK_SIGN | Home | Go to beginning |

---

#### FR08-FR18: Additional Requirements (Summarized)

| Requirement | Key Points |
|-------------|-----------|
| **FR08: Visual Feedback** | Camera preview with landmark overlay, ROI box display |
| **FR09: Gesture Notification** | Toast popup showing recognized gesture name |
| **FR10: Audio Feedback** | Different sounds for swipes vs. static gestures |
| **FR11: Profile Management** | DEFAULT, POWERPOINT, CHROME profiles |
| **FR12: Auto Profile Switch** | Detects "PowerPoint" or "Chrome" in window title |
| **FR13: Settings Interface** | Sliders for sensitivity, checkboxes for gestures |
| **FR14: Gesture Enable/Disable** | Allowlist system for static gestures |
| **FR15: Config Persistence** | JSON file saves/loads settings |
| **FR16: Overlay Mode** | Small floating window, always on top |
| **FR17: Low-Light Enhancement** | CLAHE algorithm when brightness < 80 |
| **FR18: Mouse Control** | Index finger controls cursor, pinch to click |

---

## 3.4 Non-Functional Requirements

Non-functional requirements describe **how the system should perform** - qualities like speed, reliability, and usability.

### 3.4.1 Performance Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| **NFR01** | Frame Processing Rate | ≥15 FPS | Frames processed per second |
| **NFR02** | Gesture Recognition Latency | <200ms | Time from gesture to action |
| **NFR03** | Startup Time | <5 seconds | Time from launch to ready |
| **NFR04** | Memory Usage | <500 MB | RAM consumption during operation |
| **NFR05** | CPU Usage | <50% | Average CPU utilization |

**Simple Explanation:** *These are like speed limits and rules for how well the system should work. It should be fast enough that you don't notice any delay between making a gesture and seeing the result!*

### 3.4.2 Reliability Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| **NFR06** | Uptime | System should run continuously without crashes |
| **NFR07** | Error Recovery | System should recover from camera disconnection |
| **NFR08** | Data Integrity | Configuration files should not corrupt on unexpected exit |

### 3.4.3 Usability Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| **NFR09** | Learnability | New user should perform first gesture within 2 minutes |
| **NFR10** | Feedback Clarity | User should always know if their gesture was recognized |
| **NFR11** | Settings Accessibility | All settings reachable within 3 clicks |
| **NFR12** | Visual Design | Modern, dark-themed interface matching current UI trends |

### 3.4.4 Compatibility Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| **NFR13** | Operating System | Windows 10 and Windows 11 |
| **NFR14** | Python Version | Python 3.11 or higher |
| **NFR15** | Camera Compatibility | Any UVC-compliant webcam |
| **NFR16** | Display Resolution | Minimum 1280x720 screen resolution |

---

## 3.5 Hardware Requirements

### 3.5.1 Minimum Hardware Requirements

| Component | Minimum Requirement | Recommended |
|-----------|-------------------|-------------|
| **Processor** | Dual-core 2.0 GHz | Quad-core 2.5 GHz |
| **RAM** | 4 GB | 8 GB |
| **Storage** | 500 MB free space | 1 GB free space |
| **Camera** | 720p (1280x720) webcam | 1080p (1920x1080) webcam |
| **Display** | 1280x720 resolution | 1920x1080 resolution |

### 3.5.2 Camera Requirements

**Simple Explanation:** *Your camera is like the system's eyes. Better eyes mean better seeing! But even a basic laptop camera will work.*

| Specification | Requirement | Reason |
|---------------|-------------|--------|
| **Resolution** | 720p minimum | Enough detail to see finger positions |
| **Frame Rate** | 30 FPS | Smooth gesture tracking |
| **Focus** | Auto-focus preferred | Keeps hand sharp at various distances |
| **Connection** | USB 2.0 or built-in | Standard connectivity |

### 3.5.3 Environmental Requirements

| Factor | Requirement |
|--------|-------------|
| **Lighting** | Normal indoor lighting (not too dark, not direct sunlight) |
| **Background** | Relatively uncluttered preferred |
| **Distance** | Hand should be 1-3 feet from camera |
| **Angle** | Camera should face the user directly |

---

## 3.6 Software Requirements

### 3.6.1 Operating System

| OS | Version | Support Level |
|----|---------|---------------|
| Windows 10 | Version 1903+ | Full Support |
| Windows 11 | All versions | Full Support |
| macOS | - | Not Supported |
| Linux | - | Not Supported |

**Why Windows Only?**
- Uses Windows-specific APIs for window detection (`ctypes.windll`)
- Uses Windows-specific audio (`winsound`)
- Optimized for Windows display scaling

### 3.6.2 Python Environment

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Runtime environment |
| pip | Latest | Package manager |
| venv | Built-in | Virtual environment |

### 3.6.3 Required Python Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| **opencv-python** | Latest | Camera capture, image processing |
| **mediapipe** | Latest | Hand detection and tracking |
| **pyautogui** | Latest | Keyboard/mouse simulation |
| **customtkinter** | Latest | Modern GUI framework |
| **numpy** | Latest | Numerical computations |
| **packaging** | Latest | Version management |
| **Pillow** | Latest | Image handling for GUI |

**Installation Command:**
```bash
pip install opencv-python mediapipe pyautogui customtkinter numpy packaging pillow
```

---

## 3.7 Use Case Analysis

### 3.7.1 Use Case Diagram

```
                    ┌─────────────────────────────────────────┐
                    │       Air Gesture Controller            │
                    │                                         │
                    │  ┌─────────────────────────────────┐   │
                    │  │        Start Camera             │   │
                    │  └─────────────────────────────────┘   │
                    │                  △                      │
                    │                  │                      │
    ┌──────┐        │  ┌─────────────────────────────────┐   │
    │      │        │  │      Perform Gesture            │   │
    │ USER │───────▶│  └─────────────────────────────────┘   │
    │      │        │                  │                      │
    └──────┘        │                  ▼                      │
                    │  ┌─────────────────────────────────┐   │
                    │  │    Receive Feedback             │   │
                    │  └─────────────────────────────────┘   │
                    │                                         │
                    │  ┌─────────────────────────────────┐   │
                    │  │    Configure Settings           │   │
                    │  └─────────────────────────────────┘   │
                    │                                         │
                    │  ┌─────────────────────────────────┐   │
                    │  │    Change Camera                │   │
                    │  └─────────────────────────────────┘   │
                    │                                         │
                    │  ┌─────────────────────────────────┐   │
                    │  │    Stop Camera                  │   │
                    │  └─────────────────────────────────┘   │
                    │                                         │
                    └─────────────────────────────────────────┘
```

### 3.7.2 Detailed Use Cases

#### Use Case 1: Start Gesture Recognition

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC01 |
| **Name** | Start Gesture Recognition |
| **Actor** | User |
| **Preconditions** | Application is open, camera is connected |
| **Main Flow** | 1. User clicks "Start Camera" button<br>2. System initializes camera<br>3. System displays camera preview<br>4. System begins detecting hands<br>5. System enters overlay mode |
| **Postconditions** | System is actively recognizing gestures |
| **Exceptions** | E1: No camera found → Display error message |

**Simple Explanation:** *This is what happens when you click "Start" - the camera turns on and the system starts watching for your hand gestures.*

---

#### Use Case 2: Perform Static Gesture

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC02 |
| **Name** | Perform Static Gesture |
| **Actor** | User |
| **Preconditions** | Camera is running, hand is visible |
| **Main Flow** | 1. User positions hand in ROI zone<br>2. User forms a static gesture (e.g., thumbs up)<br>3. System detects hand landmarks<br>4. System recognizes gesture pattern<br>5. System confirms gesture (2 frames)<br>6. System executes mapped shortcut<br>7. System displays feedback notification<br>8. System plays confirmation sound |
| **Postconditions** | Shortcut has been executed |
| **Exceptions** | E1: Gesture not in allowlist → No action<br>E2: Hand outside ROI → No recognition |

**Activity Flow:**
```
┌─────────────────┐
│  Hand in Frame  │
└────────┬────────┘
         ▼
┌─────────────────┐     No      ┌─────────────────┐
│  Hand in ROI?   │────────────▶│  Clear Buffer   │
└────────┬────────┘             └─────────────────┘
         │ Yes
         ▼
┌─────────────────┐
│ Detect Landmarks│
└────────┬────────┘
         ▼
┌─────────────────┐
│Analyze Geometry │
└────────┬────────┘
         ▼
┌─────────────────┐     No      ┌─────────────────┐
│ Known Gesture?  │────────────▶│ Return UNKNOWN  │
└────────┬────────┘             └─────────────────┘
         │ Yes
         ▼
┌─────────────────┐     No      ┌─────────────────┐
│ In Allowlist?   │────────────▶│ Return UNKNOWN  │
└────────┬────────┘             └─────────────────┘
         │ Yes
         ▼
┌─────────────────┐     No      ┌─────────────────┐
│ Confirmed (2x)? │────────────▶│   Add to Buffer │
└────────┬────────┘             └─────────────────┘
         │ Yes
         ▼
┌─────────────────┐
│Execute Shortcut │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Show Feedback   │
└─────────────────┘
```

---

#### Use Case 3: Perform Swipe Gesture

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC03 |
| **Name** | Perform Swipe Gesture |
| **Actor** | User |
| **Preconditions** | Camera is running, hand is visible |
| **Main Flow** | 1. User moves hand horizontally across the screen<br>2. System tracks hand centroid position over time<br>3. System analyzes trajectory (distance, speed, linearity)<br>4. System confirms valid swipe pattern<br>5. System executes mapped shortcut<br>6. System clears trajectory history<br>7. System enters cooldown period |
| **Postconditions** | Swipe action has been executed |
| **Exceptions** | E1: Movement too slow → No detection<br>E2: Movement not straight → No detection<br>E3: In cooldown → No detection |

---

#### Use Case 4: Configure Settings

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC04 |
| **Name** | Configure Settings |
| **Actor** | User |
| **Preconditions** | Application is open |
| **Main Flow** | 1. User clicks Settings button (⚙️)<br>2. System displays settings window<br>3. User adjusts detection confidence slider<br>4. User adjusts gesture cooldown slider<br>5. User enables/disables specific gestures<br>6. User modifies shortcut mappings<br>7. User clicks "Save & Close"<br>8. System saves configuration to JSON file<br>9. System reloads gesture processor with new settings |
| **Postconditions** | New settings are active and saved |

---

#### Use Case 5: Automatic Profile Switching

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC05 |
| **Name** | Automatic Profile Switching |
| **Actor** | System (automated) |
| **Preconditions** | Camera is running |
| **Trigger** | Every 30 frames (~1 second) |
| **Main Flow** | 1. System gets title of active window<br>2. System checks title against WINDOW_PROFILE_MAP<br>3. If match found, system switches to corresponding profile<br>4. System updates status display with profile name |
| **Example** | Window title contains "PowerPoint" → Switch to POWERPOINT profile |

**Simple Explanation:** *The system is smart enough to notice when you switch to PowerPoint or Chrome and automatically changes which actions the gestures perform!*

---

## 3.8 Data Flow Analysis

### 3.8.1 Level 0 Data Flow Diagram (Context Diagram)

```
                              ┌─────────────────────┐
           Video Stream       │                     │      Keyboard Commands
    ┌──────────────────────▶  │                     │  ────────────────────────▶
    │                         │    AIR GESTURE      │         to Other Apps
┌───┴───┐                     │    CONTROLLER       │
│WEBCAM │                     │                     │      Visual Feedback
└───────┘                     │                     │  ◀───────────────────────
                              │                     │         to User
           Hand Gestures      │                     │
    ┌──────────────────────▶  │                     │      Audio Feedback
    │                         │                     │  ◀───────────────────────
┌───┴───┐                     │                     │         to User
│ USER  │                     │                     │
└───┬───┘                     └─────────────────────┘
    │                                   ▲
    │         Settings Changes          │
    └───────────────────────────────────┘
```

### 3.8.2 Level 1 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌────────┐     Raw Frames      ┌────────────────┐                        │
│   │ WEBCAM │────────────────────▶│  1.0 CAPTURE   │                        │
│   └────────┘                     │    MODULE      │                        │
│                                  └───────┬────────┘                        │
│                                          │                                  │
│                                   Captured Frames                           │
│                                          │                                  │
│                                          ▼                                  │
│                                  ┌────────────────┐                        │
│                                  │  2.0 GESTURE   │                        │
│                                  │    ENGINE      │                        │
│                                  └───────┬────────┘                        │
│                                          │                                  │
│                           ┌──────────────┼──────────────┐                  │
│                           │              │              │                   │
│                    Landmarks      Gesture Name    Processed Frame          │
│                           │              │              │                   │
│                           ▼              ▼              ▼                   │
│   ┌────────┐      ┌────────────┐ ┌────────────┐ ┌────────────────┐        │
│   │  USER  │◀─────│  4.0 UI    │ │3.0 SHORTCUT│ │ Config Store   │        │
│   └────────┘      │  MANAGER   │ │  EXECUTOR  │ │  (JSON File)   │        │
│       │           └────────────┘ └─────┬──────┘ └────────────────┘        │
│       │                                │                  ▲                 │
│       │ Settings                       │ Key Press        │ Load/Save      │
│       └────────────────────────────────┼──────────────────┘                │
│                                        ▼                                    │
│                                 ┌────────────┐                             │
│                                 │ OTHER APPS │                             │
│                                 │(PowerPoint)│                             │
│                                 └────────────┘                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.8.3 Data Dictionary

| Data Item | Description | Format | Source | Destination |
|-----------|-------------|--------|--------|-------------|
| Raw Frame | Single video image from camera | BGR numpy array (720x1280x3) | Webcam | Capture Module |
| Captured Frame | Flipped and preprocessed frame | BGR numpy array | Capture Module | Gesture Engine |
| Landmarks | 21 hand landmark positions | List of (x, y, z) floats | MediaPipe | Gesture Engine |
| Gesture Name | Identified gesture type | String (e.g., "SWIPE_LEFT") | Gesture Engine | Shortcut Executor |
| Processed Frame | Frame with overlays drawn | BGR numpy array | Gesture Engine | UI Manager |
| Shortcut | Keyboard keys to press | List of strings (e.g., ["ctrl", "tab"]) | Config | Shortcut Executor |
| Key Press | Simulated keyboard event | System event | Shortcut Executor | Windows OS |
| Config Data | User settings | JSON object | JSON File | All Modules |

---

## 3.9 Feasibility Analysis

### 3.9.1 Technical Feasibility

| Aspect | Assessment | Justification |
|--------|------------|---------------|
| **Hardware Availability** | ✅ Feasible | Standard webcams are ubiquitous |
| **Software Libraries** | ✅ Feasible | MediaPipe, OpenCV are mature and free |
| **Processing Power** | ✅ Feasible | Modern computers easily handle real-time CV |
| **Development Skills** | ✅ Feasible | Python has gentle learning curve |
| **Integration** | ✅ Feasible | PyAutoGUI provides simple shortcut simulation |

### 3.9.2 Operational Feasibility

| Aspect | Assessment | Justification |
|--------|------------|---------------|
| **User Acceptance** | ✅ Likely | Gesture control is intuitive |
| **Learning Curve** | ✅ Low | Simple gestures, visual feedback |
| **Maintenance** | ✅ Easy | Modular design, clear code structure |
| **Support** | ✅ Manageable | Comprehensive documentation provided |

### 3.9.3 Economic Feasibility

| Item | Cost | Notes |
|------|------|-------|
| Software Licenses | $0 | All libraries are open-source |
| Hardware | $0 | Uses existing webcam |
| Development Time | Student project | Educational purpose |
| Deployment | $0 | Local installation |
| **Total** | **$0** | Completely free solution |

**Simple Explanation:** *Can we actually build this? Yes! We have all the tools we need, they're all free, and modern computers are fast enough to run it. It's totally doable!*

---

## 3.10 Risk Analysis

### 3.10.1 Identified Risks

| Risk ID | Risk | Probability | Impact | Mitigation |
|---------|------|-------------|--------|------------|
| R01 | Poor lighting causes detection failures | Medium | High | Implement CLAHE enhancement |
| R02 | False positive gesture detection | Medium | Medium | Use confirmation frames, cooldown |
| R03 | Camera compatibility issues | Low | High | Use standard OpenCV capture |
| R04 | Performance lag on slow computers | Medium | Medium | Optimize code, reduce FPS if needed |
| R05 | User finds gestures unnatural | Low | Medium | Choose intuitive, common gestures |
| R06 | Interference from background objects | Low | Medium | Implement ROI restriction |

### 3.10.2 Risk Matrix

```
                    IMPACT
            Low     Medium    High
         ┌────────┬─────────┬────────┐
    High │        │         │        │
         ├────────┼─────────┼────────┤
P   Med  │        │R02, R04 │  R01   │
R        ├────────┼─────────┼────────┤
O   Low  │        │R05, R06 │  R03   │
B        └────────┴─────────┴────────┘
```

---

## 3.11 Chapter Summary

In this chapter, we have:

1. **Provided a system overview** showing how the gesture controller fits into its environment

2. **Documented 18 functional requirements** covering all features from camera capture to mouse control

3. **Specified non-functional requirements** for performance, reliability, usability, and compatibility

4. **Detailed hardware requirements** including processor, memory, camera, and environmental needs

5. **Listed software requirements** including OS, Python version, and all required libraries

6. **Analyzed use cases** with detailed flows for starting the camera, performing gestures, and configuring settings

7. **Created data flow diagrams** showing how information moves through the system

8. **Assessed feasibility** from technical, operational, and economic perspectives

9. **Identified and analyzed risks** with mitigation strategies

**Key Findings:**
- The system is technically feasible using existing free tools
- All requirements can be met with standard hardware
- Risks are manageable with proper design decisions

**Simple Summary:** *We figured out exactly what our system needs to do (the features), how well it needs to work (the performance), and what equipment we need (the requirements). We also made sure the project is actually possible to build with free tools and regular computers. Now we're ready to design how all the pieces fit together!*

---

*[End of Chapter 3]*

---
