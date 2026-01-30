# src/config.py

# Profile-based Gesture to Keyboard Shortcut Mappings
# The keys are profile names. 'DEFAULT' is the fallback.
# Mappings include both static signs and dynamic gestures.
PROFILES = {
    'DEFAULT': {
        # 'THUMBS_UP': ['right'],          # Disabled
        # 'THUMBS_DOWN': ['left'],         # Disabled
        # 'OPEN_PALM': ['f5'],             # Disabled
        # 'OK_SIGN': ['home']              # Disabled
        
        # Swipe Mode (Horizontal)
        'SWIPE_RIGHT': ['right'],   # Next Slide
        'SWIPE_LEFT': ['left'],     # Previous Slide
    },
    'POWERPOINT': {
         'THUMBS_UP': ['right'],        # Disabled
         'THUMBS_DOWN': ['left'],       # Disabled
        #ca'OPEN_PALM': ['f5'],           # Disabled
         'V_SIGN': ['b'],               # Disabled
        #'INDEX_POINTING_UP': ['w'],    # Disabled
         'OK_SIGN': ['home'],           # Disabled
         'SPIDERMAN': ['end'],           # Disabled
        
        # Swipe Mode (Horizontal)
        'SWIPE_RIGHT': ['right'],   # Next Slide
        'SWIPE_LEFT': ['left'],     # Previous Slide
    },
    'CHROME': {
        'THUMBS_UP': ['ctrl', 'tab'],    # Next Tab
        'THUMBS_DOWN': ['ctrl', 'shift', 'tab'], # Prev Tab
        'SWIPE_RIGHT': ['alt', 'right'], # Forward
        'SWIPE_LEFT': ['alt', 'left'],   # Back
        'OPEN_PALM': ['f5'],             # Refresh
        'OK_SIGN': ['ctrl', 't']         # New Tab
    }
}

# Window Title to Profile Name Mapping (substring match)
WINDOW_PROFILE_MAP = {
    'PowerPoint': 'POWERPOINT',
    'Google Slides': 'POWERPOINT',
    'Chrome': 'CHROME',
    'Edge': 'CHROME'
}

# Camera and UI Configuration
CAMERA_INDEX = 2  # Default to Webcam
WINDOW_TITLE = "Air Gesture Shortcut Controller"
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
AUTO_CALIBRATE_ON_STARTUP = True
AUTO_START_CAMERA = True # Automatically start camera on launch

# Camera Names (customize these based on your system)
# Map camera index to a friendly name
CAMERA_NAMES = {
    0: "Camo (Virtual)",
    1: "External Camera",
    2: "Webcam"
}

# Hand Detection Settings
MIN_DETECTION_CONFIDENCE = 0.5 # Detection sensitivity (lower = more sensitive)
MIN_TRACKING_CONFIDENCE = 0.4  # Tracking stability (lower = maintains lock better)
GESTURE_COOLDOWN = 0.3
LOW_LIGHT_MODE = True # Brightness/Contrast enhancement
AUDIO_FEEDBACK_ENABLED = True # Enable sound effects

# ROI (Region of Interest) for Static Signs
# Only recognize signs if hand is in this box (Normalized 0.0-1.0)
SIGN_ROI_ENABLED = True
SIGN_ROI_COORDS = {
    'x_min': 0.35, # Center-ish (Width 30%)
    'y_min': 0.7,  # Bottom 30%
    'x_max': 0.65, 
    'y_max': 1.0   
}

# Dynamic Gesture (Swipe) Settings
# Dynamic Gesture (Swipe) Settings - VELOCITY MODE
SWIPE_VELOCITY_THRESHOLD = 0.02  # Minimum frame-to-frame distance to count as "moving"
SWIPE_MIN_DISTANCE_LEFT = 0.02   # Accumulated distance for Left Swipe (Micro-movement)
SWIPE_MIN_DISTANCE_RIGHT = 0.02  # Accumulated distance for Right Swipe (Micro-movement)
GESTURE_CONFIRMATION_FRAMES = 2 # Number of consecutive/voting frames to confirm static gesture

# Mouse Control Settings
MOUSE_SENSITIVITY = 1.8      # Increased to 1.8 for lighter feel (less hand movement)
MOUSE_SMOOTHING = 0.35       # Increased to 0.35 (More responsive/snappy, less "heavy")
CLICK_THRESHOLD = 0.035      # Tightened to prevent accidental clicks
ENABLE_MOUSE = False         # Master toggle for mouse control

# Performance & Robustness Settings
MAX_MISSED_FRAMES = 5      # Retain history for this many frames if tracking is lost (Debounce)
SMOOTHING_BUFFER_SIZE = 5  # Number of frames for gesture voting
FPS_ACTIVE = 30            # Target delay in ms when active (approx 33 FPS)
FPS_IDLE = 200             # Target delay in ms when idle (approx 5 FPS)
IDLE_TIMEOUT = 5.0         # Seconds of no hand detection before checking idle

# Available Static Signs (for UI selection)
AVAILABLE_SIGNS = [
    'THUMBS_UP', 'THUMBS_DOWN', 'OPEN_PALM', 'OK_SIGN', 
    'VICTORY', 'POINT_UP', 'SPIDERMAN'
]

# Enabled Static Signs (User Allowlist)
ENABLED_SIGNS = [] # Default empty, user must enable

import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

def save_config():
    data = {
        "MIN_DETECTION_CONFIDENCE": MIN_DETECTION_CONFIDENCE,
        "GESTURE_COOLDOWN": GESTURE_COOLDOWN,
        "ENABLE_MOUSE": ENABLE_MOUSE,
        "ENABLED_SIGNS": ENABLED_SIGNS,
        "AUTO_START_CAMERA": AUTO_START_CAMERA,
        "PROFILES": PROFILES
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        print("Configuration saved.")
    except Exception as e:
        print(f"Error saving config: {e}")

def load_config():
    global MIN_DETECTION_CONFIDENCE, GESTURE_COOLDOWN, PROFILES, ENABLE_MOUSE, ENABLED_SIGNS, AUTO_START_CAMERA
    if not os.path.exists(CONFIG_FILE):
        return

    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            
        MIN_DETECTION_CONFIDENCE = data.get("MIN_DETECTION_CONFIDENCE", MIN_DETECTION_CONFIDENCE)
        GESTURE_COOLDOWN = data.get("GESTURE_COOLDOWN", GESTURE_COOLDOWN)
        ENABLE_MOUSE = data.get("ENABLE_MOUSE", ENABLE_MOUSE)
        ENABLED_SIGNS = data.get("ENABLED_SIGNS", ENABLED_SIGNS)
        AUTO_START_CAMERA = data.get("AUTO_START_CAMERA", True)
        
        # Update profiles but keep structure
        saved_profiles = data.get("PROFILES", {})
        for profile, mappings in saved_profiles.items():
            if profile in PROFILES:
                PROFILES[profile].update(mappings)
            else:
                PROFILES[profile] = mappings
                
        print("Configuration loaded.")
    except Exception as e:
        print(f"Error loading config: {e}")

# Load on import
load_config()
