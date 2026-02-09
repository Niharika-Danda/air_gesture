# src/main.py

# ============================================
# Suppress Library Warnings
# Must be set BEFORE importing these libraries
# ============================================
import os
import warnings

# Suppress background library logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['ABSL_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Suppress deprecation warnings
warnings.filterwarnings('ignore', category=UserWarning, module='google.protobuf')
warnings.filterwarnings('ignore', category=DeprecationWarning)

# ============================================

import cv2
import pyautogui
import tkinter as tk
import ctypes
import time
import sys
import numpy as np
from collections import deque

# Fix path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Imports
from src.ui_manager import AppUIManager
from src.audio_feedback import AudioFeedback
from src import config
from src.audio_feedback import AudioFeedback
from src import config
from src.event_bus import EventBus
from src.camera_manager import CameraManager
from src.window_manager import WindowManager

class GestureControllerApp:
    def __init__(self, root):
        self.root = root
        self.bus = EventBus()
        self.camera_manager = CameraManager()
        self.window_manager = WindowManager()
        
        # State
        self.last_gesture = None
        self.last_gesture_time = 0
        self.frame_count = 0
        self.last_hand_detected_time = time.time()
        self.current_profile_name = 'DEFAULT'
        self.fps_frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        self.is_clicking = False
        
        # Capture HWND
        self.app_hwnd = None
        self.root.after(100, self._capture_app_hwnd)
        
        # Initialize UI
        # Get cameras for UI
        camera_names = self.camera_manager.initialize_camera_selection()
        
        self.ui_manager = AppUIManager(
            self.root,
            config.WINDOW_TITLE,
            camera_names
        )
        self.ui_manager.config_callback = self.reload_configuration
        
        # Audio
        self.audio = AudioFeedback(enabled=config.AUDIO_FEEDBACK_ENABLED)
        
        # Start update loop
        self.update()
        
        # Subscriptions
        self.bus.subscribe("app:quit", self.on_quit)
        self.bus.subscribe("cmd:reload_config", self.reload_configuration)

        # Auto-Start logic
        if getattr(config, 'AUTO_START_CAMERA', True):
            print("DEBUG: Auto-starting camera...")
            self.root.after(500, lambda: self.bus.publish("cmd:start_camera"))

    def reload_configuration(self, _=None):
        """Reloads config and restarts camera if needed."""
        print("DEBUG: Reloading configuration...")
        config.load_config()
        self.bus.publish("camera:status", "Settings Reloaded")
        
        # Update Audio state
        self.audio.enabled = config.AUDIO_FEEDBACK_ENABLED

    def _capture_app_hwnd(self):
        try:
            self.app_hwnd = ctypes.windll.user32.GetActiveWindow()
            if not self.app_hwnd:
                self.app_hwnd = ctypes.windll.user32.FindWindowW(None, config.WINDOW_TITLE)
        except Exception: 
            pass

    def on_quit(self, _=None):
        self.bus.publish("cmd:stop_camera")
        self.root.destroy()
        sys.exit(0)

    def update(self):
        # Poll CameraManager for frames
        try:
            latest_data = self.camera_manager.get_latest_frame()
            
            if latest_data:
                # Unpack
                if len(latest_data) == 5:
                    gesture, processed_frame, pointer_info, landmarks, timestamp = latest_data
                else:
                    gesture, processed_frame, pointer_info, timestamp = latest_data
                    landmarks = None
                
                # FPS Calculation
                self.fps_frame_count += 1
                if time.time() - self.fps_start_time >= 1.0:
                    self.current_fps = self.fps_frame_count
                    self.fps_frame_count = 0
                    self.fps_start_time = time.time()
                
                # Update UI
                hand_detected = pointer_info is not None
                quality = 1.0 if hand_detected else 0.0
                self.ui_manager.update_performance(self.current_fps, hand_detected, quality)
                self.ui_manager.update_frame(processed_frame)
                
                # Logic
                self._handle_logic(gesture, pointer_info, landmarks)
                
        except Exception as e:
            print(f"Update Loop Error: {e}")

        # Check Window State
        self.frame_count += 1
        if self.frame_count % 30 == 0:
            self._update_app_state()
            
        self.root.after(10, self.update)

    def _handle_logic(self, gesture, pointer_info, landmarks=None):
        # --- MOUSE CONTROL ---
        if pointer_info and config.ENABLE_MOUSE:
            try:
                # Only move pointer if 'move' flag is True
                # This prevents pointer movement during click-only actions (like pinch)
                should_move = pointer_info.get('move', True)  # Default True for backward compatibility
                
                if should_move:
                    screen_w, screen_h = pyautogui.size()
                    margin = 0.2
                    x_cam = pointer_info['x']
                    y_cam = pointer_info['y']
                    x_norm = (x_cam - margin) / (1 - 2*margin)
                    y_norm = (y_cam - margin) / (1 - 2*margin)
                    x_norm = max(0.0, min(1.0, x_norm))
                    y_norm = max(0.0, min(1.0, y_norm))
                    
                    target_x = int(x_norm * screen_w)
                    target_y = int(y_norm * screen_h)
                    
                    pyautogui.moveTo(target_x, target_y)
                
                # Handle click (works regardless of move flag)
                if pointer_info['click']:
                    if not self.is_clicking:
                        pyautogui.click()  # Single left click
                        self.is_clicking = True
                else:
                    self.is_clicking = False
            except Exception:
                pass
        
        # Filter gesture by profile
        current_profile = config.PROFILES.get(self.current_profile_name, config.PROFILES['DEFAULT'])
        if gesture != 'UNKNOWN' and gesture not in current_profile:
            gesture = 'UNKNOWN'
        
        if gesture != 'UNKNOWN':
             self.last_hand_detected_time = time.time()
        
        # Execute shortcut
        current_time = time.time()
        if gesture != 'UNKNOWN' and gesture != self.last_gesture:
            if current_time - self.last_gesture_time > config.GESTURE_COOLDOWN:
                self.execute_shortcut(gesture)
                self.last_gesture = gesture
                self.last_gesture_time = current_time
                self.ui_manager.update_status(f"{self.current_profile_name}: {gesture}")
        elif gesture == 'UNKNOWN':
             self.last_gesture = None

    def _update_app_state(self):
        """Updates active profile using robust window matching."""
        info = self.window_manager.get_active_window_info()
        title = info.get('title', '')
        process = info.get('process', '')
        win_class = info.get('class', '')
        
        new_profile = 'DEFAULT'
        
        # Check against rules in order
        for rule in config.APP_MATCHING_RULES:
            match = True
            
            # 1. Process Name Match (Exact)
            if 'process' in rule and rule['process'].lower() != process.lower():
                match = False
                
            # 2. Window Class Match (Exact)
            if match and 'class' in rule and rule['class'] != win_class:
                match = False
                
            # 3. Title Match (Substring)
            if match and 'title' in rule and rule['title'].lower() not in title.lower():
                match = False
                
            if match:
                new_profile = rule['profile']
                break
        
        if new_profile != self.current_profile_name:
            print(f"DEBUG: Switched Profile to {new_profile} (App: {process}, Class: {win_class})")
            self.current_profile_name = new_profile
            self.ui_manager.update_status(f"Profile: {new_profile}")

    # Legacy method removed: get_active_window_title

    def execute_shortcut(self, gesture):
        if self.ui_manager.is_overlay and gesture == 'OPEN_PALM':
            return

        profile = config.PROFILES.get(self.current_profile_name, config.PROFILES['DEFAULT'])
        shortcut = profile.get(gesture)
        
        if shortcut:
            try:
                if "SWIPE" in gesture:
                    self.audio.play_swipe_sound()
                else:
                    self.audio.play_static_gesture_sound()
                    
                pyautogui.hotkey(*shortcut)
                print(f"[{self.current_profile_name}] Executed {gesture}: {shortcut}")
            except Exception as e:
                print(f"Failed to execute shortcut: {e}")
                self.audio.play_error_sound()

if __name__ == "__main__":
    import customtkinter as ctk
    
    ctk.set_widget_scaling(1.0)
    ctk.set_window_scaling(1.0)
    
    root = ctk.CTk()
    app = GestureControllerApp(root)
    root.mainloop()
