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

# Profile Styling (Icons & Colors & Hints)
PROFILE_THEMES = {
    'DEFAULT': {
        'icon': '🏠', 
        'color': '#1f6aa5',
        'hints': "👋 Swipe L/R to Nav | 🤏 Click to Select"
    },
    'POWERPOINT': {
        'icon': '📊', 
        'color': '#d04423',
        'hints': "👉 Right: Next Slide | 👈 Left: Prev Slide"
    },
    'CHROME': {
        'icon': '🌐', 
        'color': '#4285f4',
        'hints': "👍 Next Tab | 👎 Prev Tab | ✋ Refresh"
    },
    'UNKNOWN': {
        'icon': '❓', 
        'color': '#666666',
        'hints': "No Profile Detected"
    }
}

# Window Matching Rules
# Checked in order. First match determines the profile.
# Keys: 'profile' (required), 'title' (substring), 'process' (exact), 'class' (exact)
APP_MATCHING_RULES = [
    # PowerPoint Presentation Mode (Priority)
    {'profile': 'POWERPOINT', 'process': 'POWERPNT.EXE', 'class': 'screenClass'},
    {'profile': 'POWERPOINT', 'process': 'POWERPNT.EXE', 'class': 'OpusApp'}, # Edit mode
    {'profile': 'POWERPOINT', 'title': 'PowerPoint'}, # Fallback
    {'profile': 'POWERPOINT', 'title': 'Google Slides'},
    
    # Browser
    {'profile': 'CHROME', 'process': 'chrome.exe'},
    {'profile': 'CHROME', 'process': 'msedge.exe'},
    {'profile': 'CHROME', 'title': 'Chrome'}, 
    {'profile': 'CHROME', 'title': 'Edge'}
]

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
CLICK_THRESHOLD = 0.06      # Increased for thumb-middle finger tap
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

def validate_config(data):
    """Validates loaded configuration data."""
    valid = True
    
    # 1. Type Validation
    if not isinstance(data.get("MIN_DETECTION_CONFIDENCE"), (int, float)):
        print("Config Error: MIN_DETECTION_CONFIDENCE must be a number.")
        valid = False
        
    if not isinstance(data.get("GESTURE_COOLDOWN"), (int, float)):
        print("Config Error: GESTURE_COOLDOWN must be a number.")
        valid = False
        
    if not isinstance(data.get("PROFILES"), dict):
        print("Config Error: PROFILES must be a dictionary.")
        valid = False
        
    # 2. Value Range Validation
    conf = data.get("MIN_DETECTION_CONFIDENCE", 0.5)
    if isinstance(conf, (int, float)) and not (0.0 <= conf <= 1.0):
        print("Config Error: MIN_DETECTION_CONFIDENCE must be between 0.0 and 1.0")
        valid = False
        
    return valid

def load_config():
    global MIN_DETECTION_CONFIDENCE, GESTURE_COOLDOWN, PROFILES, ENABLE_MOUSE, ENABLED_SIGNS, AUTO_START_CAMERA
    if not os.path.exists(CONFIG_FILE):
        return

    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            
        if not validate_config(data):
            print("WARNING: Config validation failed. Using defaults for invalid fields or falling back.")
            # We could return here to use defaults, or proceed with partial loading.
            # For now, let's try to load what we can, but errors are logged.
            
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
