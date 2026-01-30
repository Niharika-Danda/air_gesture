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

# ============================================

import cv2
import pyautogui
import tkinter as tk
import time
import sys
import os
import ctypes
import ctypes
from ctypes import wintypes
import numpy as np

# Fix path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.gesture_engine import GestureProcessor
from src.ui_manager import AppUIManager
from src.audio_feedback import AudioFeedback
from src import config

class GestureControllerApp:
    def __init__(self, root):
        self.root = root
        self.is_running = False
        self.last_gesture = None
        self.last_gesture_time = 0
        self.frame_count = 0
        
        # Audio Feedback
        self.audio = AudioFeedback(enabled=config.AUDIO_FEEDBACK_ENABLED)
        
        # FPS Tracking
        self.fps_start_time = time.time()
        self.fps_frame_count = 0
        self.current_fps = 0
        
        # Adaptive FPS state
        self.last_hand_detected_time = time.time()
        
        # Profile state
        self.current_profile_name = 'DEFAULT'
        
        # Camera discovery
        self.camera_indices = self.detect_cameras()
        self.available_cameras = [f"Camera {i}" for i in self.camera_indices]
        if not self.camera_indices:
             self.available_cameras = ["No Camera Found"]
             config.CAMERA_INDEX = -1
        else:
             config.CAMERA_INDEX = self.camera_indices[0]

        # Initialize components
        self.gesture_processor = GestureProcessor(
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
        )
        self.ui_manager = AppUIManager(
            self.root,
            self.start,
            self.stop,
            config.WINDOW_TITLE,
            self.available_cameras,
            self.change_camera,
            self.reload_configuration
        )
        self.cap = None
        
        self.app_hwnd = None
        self.root.after(100, self._capture_app_hwnd)

    def reload_configuration(self):
        """Re-initializes components with new config values."""
        print("DEBUG: Reloading configuration...")
        if self.gesture_processor:
            self.gesture_processor.close()
            
        self.gesture_processor = GestureProcessor(
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
        )
        self.ui_manager.update_status("Settings Saved & Reloaded")

    def _capture_app_hwnd(self):
        try:
            self.app_hwnd = ctypes.windll.user32.GetActiveWindow()
            if not self.app_hwnd:
                self.app_hwnd = ctypes.windll.user32.FindWindowW(None, config.WINDOW_TITLE)
            print(f"DEBUG: App HWND captured: {self.app_hwnd}")
        except Exception as e:
            print(f"DEBUG: Failed to capture app HWND: {e}")

    def detect_cameras(self):
        index = 0
        arr = []
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.read()[0]:
                arr.append(i)
                cap.release()
            index += 1
        return arr

    def change_camera(self, selection_index):
        if selection_index < 0 or selection_index >= len(self.camera_indices):
            return
        new_camera_index = self.camera_indices[selection_index]
        config.CAMERA_INDEX = new_camera_index
        if self.is_running:
            self.stop()
            self.root.after(100, self.start)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.ui_manager.update_status("Status: Initializing Camera...")
            self.ui_manager.start_button.configure(state="disabled")
            
            import threading
            threading.Thread(target=self._init_camera, daemon=True).start()

import queue
import threading
from src import config

class VisionThread(threading.Thread):
    def __init__(self, camera_index, result_queue):
        super().__init__()
        self.camera_index = camera_index
        self.result_queue = result_queue
        self.stop_event = threading.Event()
        self.gesture_processor = None
        self.cap = None
        self.frame_counter = 0

    def run(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.VIDEO_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.VIDEO_HEIGHT)
            
            self.gesture_processor = GestureProcessor(
                min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
                min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
            )
            
            while not self.stop_event.is_set():
                ret, frame = self.cap.read()
                if not ret:
                    time.sleep(0.01)
                    continue
                
                # Heavy processing happens here, off the UI thread
                
                # --- Dynamic Environmental Adaptation ---
                self.frame_counter += 1
                if self.frame_counter % 30 == 0: # Check every ~1 second (at 30 FPS)
                    try:
                        # Fast brightness check on subsampled frame
                        small_frame = cv2.resize(frame, (320, 180))
                        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                        avg_brightness = np.mean(gray)
                        
                        # Hysteresis Logic to prevent flickering
                        # Thresholds: ON < 80, OFF > 100
                        if not config.LOW_LIGHT_MODE and avg_brightness < 80:
                            config.LOW_LIGHT_MODE = True
                        elif config.LOW_LIGHT_MODE and avg_brightness > 100:
                            config.LOW_LIGHT_MODE = False
                            
                    except Exception as e:
                        pass  # Silently ignore AutoCal errors

                try:
                    gesture, processed_frame, pointer_info, landmarks = self.gesture_processor.process_frame(frame)
                except ValueError:
                    # Fallback for old version or error
                    gesture, processed_frame, pointer_info = self.gesture_processor.process_frame(frame)
                    landmarks = None
                
                # Put result in queue (drop old frames if queue is full to prevent lag)
                if self.result_queue.full():
                    try: self.result_queue.get_nowait()
                    except queue.Empty: pass
                
                self.result_queue.put((gesture, processed_frame, pointer_info, landmarks, time.time()))
                
                # Adaptive sleep (simple yield)
                time.sleep(0.001)
                
        except Exception as e:
            print(f"VisionThread Error: {e}")
        finally:
            if self.cap: self.cap.release()
            if self.gesture_processor: self.gesture_processor.close()

    def stop(self):
        self.stop_event.set()


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
        self.result_queue = queue.Queue(maxsize=2) # Keep buffer small for low latency
        self.vision_thread = None
        
        # Camera discovery
        self.camera_indices = self.detect_cameras()
        self.available_cameras = [f"Camera {i}" for i in self.camera_indices]
        if not self.camera_indices:
             self.available_cameras = ["No Camera Found"]
             config.CAMERA_INDEX = -1
        else:
             config.CAMERA_INDEX = self.camera_indices[0]

        # Initialize components
        # Note: GestureProcessor is now owned by the thread
        
        self.ui_manager = AppUIManager(
            self.root,
            self.start,
            self.stop,
            config.WINDOW_TITLE,
            self.available_cameras,
            self.change_camera,
            self.reload_configuration
        )
        
        self.app_hwnd = None
        self.root.after(100, self._capture_app_hwnd)

    def reload_configuration(self):
        """Restarts the thread to pick up new config."""
        print("DEBUG: Reloading configuration...")
        if self.is_running:
            self.stop()
            self.root.after(500, self.start)
        self.ui_manager.update_status("Settings Saved & Reloaded")

    def _capture_app_hwnd(self):
        try:
            self.app_hwnd = ctypes.windll.user32.GetActiveWindow()
            if not self.app_hwnd:
                self.app_hwnd = ctypes.windll.user32.FindWindowW(None, config.WINDOW_TITLE)
            print(f"DEBUG: App HWND captured: {self.app_hwnd}")
        except Exception as e:
            print(f"DEBUG: Failed to capture app HWND: {e}")

    def detect_cameras(self):
        index = 0
        arr = []
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.read()[0]:
                arr.append(i)
                cap.release()
            index += 1
        return arr

    def change_camera(self, selection_index):
        if selection_index < 0 or selection_index >= len(self.camera_indices):
            return
        new_camera_index = self.camera_indices[selection_index]
        config.CAMERA_INDEX = new_camera_index
        if self.is_running:
            self.stop()
            self.root.after(100, self.start)

    def start(self):
        if not self.is_running:
            # Safety: Check for lingering thread
            if self.vision_thread and self.vision_thread.is_alive():
                print("DEBUG: Waiting for previous thread to die...")
                self.vision_thread.join(timeout=2.0)
            
            self.is_running = True
            self.ui_manager.update_status("Status: Starting Engine...")
            self.ui_manager.start_button.configure(state="disabled")
            
            # Reset Queue to clear slate
            self.result_queue = queue.Queue(maxsize=2)
            
            # Start Vision Thread
            self.vision_thread = VisionThread(config.CAMERA_INDEX, self.result_queue)
            self.vision_thread.start()
            
            self.root.after(100, lambda: self.ui_manager.update_status("Status: Running"))
            self.root.after(100, lambda: self.ui_manager.start_button.configure(state="normal"))
            self.root.after(50, lambda: self.ui_manager.enter_overlay_mode()) # Force overlay immediately
            self.root.after(100, self.update)

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.ui_manager.update_status("Status: Stopping...")
            
            if self.vision_thread:
                self.vision_thread.stop()
                # Wait longer for camera release (it can be slow)
                self.vision_thread.join(timeout=2.0)
                if self.vision_thread.is_alive():
                     print("WARNING: VisionThread did not stop cleanly!")
                self.vision_thread = None
                
            self.ui_manager.update_status("Status: Stopped")
            self.ui_manager.start_button.configure(state="normal")
            
        # Don't destroy root here, this is just stopping the engine
        # self.root.destroy() is called by the window close handler

    def update(self):
        if not self.is_running:
            return

        try:
            # Poll queue for new frames
            # We loop to drain the queue and get the LATEST frame if multiple are waiting
            latest_data = None
            while True:
                try:
                    latest_data = self.result_queue.get_nowait()
                except queue.Empty:
                    break
            
            if latest_data:
                # Handle both old (4) and new (5) tuple sizes for robustness during hot-reload
                if len(latest_data) == 5:
                    gesture, processed_frame, pointer_info, landmarks, timestamp = latest_data
                else:
                    gesture, processed_frame, pointer_info, timestamp = latest_data
                    landmarks = None
                
                # FPS Calculation
                if not hasattr(self, 'fps_frame_count'):
                    self.fps_frame_count = 0
                    self.fps_start_time = time.time()
                    self.current_fps = 0
                    
                self.fps_frame_count += 1
                if time.time() - self.fps_start_time >= 1.0:
                    self.current_fps = self.fps_frame_count
                    self.fps_frame_count = 0
                    self.fps_start_time = time.time()
                
                # Performance & Feedback Update
                hand_detected = pointer_info is not None
                quality = 1.0 if hand_detected else 0.0
                self.ui_manager.update_performance(self.current_fps, hand_detected, quality)
                
                self.ui_manager.update_frame(processed_frame)
                self._handle_logic(gesture, pointer_info, landmarks)
                
        except Exception as e:
            print(f"Update Loop Error: {e}")

        # Periodically check window and fullscreen status
        self.frame_count += 1
        if self.frame_count % 30 == 0:
            self._update_app_state()
            
        # UI Update Rate (Fast enough to catch queue updates)
        # Even if camera is slow, UI stays responsive
        self.root.after(10, self.update)

    def _handle_logic(self, gesture, pointer_info, landmarks=None):
        # --- MOUSE CONTROL ---
        if pointer_info and config.ENABLE_MOUSE:
            try:
                screen_w, screen_h = pyautogui.size()
                
                # Mapping Camera Coordinates (0.0-1.0) to Screen
                margin = 0.2
                x_cam = pointer_info['x']
                y_cam = pointer_info['y']
                
                # Remap: (margin, 1-margin) -> (0, 1)
                x_norm = (x_cam - margin) / (1 - 2*margin)
                y_norm = (y_cam - margin) / (1 - 2*margin)
                
                # Clamp
                x_norm = max(0.0, min(1.0, x_norm))
                y_norm = max(0.0, min(1.0, y_norm))
                
                target_x =  int(x_norm * screen_w)
                target_y = int(y_norm * screen_h)
                
                # Move Mouse
                pyautogui.moveTo(target_x, target_y)
                
                # Handle Click (Pinch)
                if pointer_info['click']:
                    if not getattr(self, 'is_clicking', False):
                        pyautogui.mouseDown()
                        self.is_clicking = True
                        print("DEBUG: Mouse Down")
                else:
                    if getattr(self, 'is_clicking', False):
                        pyautogui.mouseUp()
                        self.is_clicking = False
                        print("DEBUG: Mouse Up")
                        
            except Exception as e:
                pass
        
        # Filter: Only process gestures that have a mapping in the current profile
        current_profile = config.PROFILES.get(self.current_profile_name, config.PROFILES['DEFAULT'])
        if gesture != 'UNKNOWN' and gesture not in current_profile:
            gesture = 'UNKNOWN'
        
        if gesture != 'UNKNOWN':
             self.last_hand_detected_time = time.time()
        
        # Check if a new, valid gesture is detected and cooldown has passed
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
        """Updates active profile and checks for fullscreen overlay."""
        window_title = self.get_active_window_title()
        
        # 1. Profile Switching
        new_profile = 'DEFAULT'
        for title_part, profile_name in config.WINDOW_PROFILE_MAP.items():
            if title_part.lower() in window_title.lower():
                new_profile = profile_name
                break
        
        if new_profile != self.current_profile_name:
            print(f"DEBUG: Switched to Profile: {new_profile} (Window: {window_title})")
            self.current_profile_name = new_profile
            self.ui_manager.update_status(f"Profile: {new_profile}")

        # 2. PERMANENT Overlay Mode (Forced)
        # User requested permanent small size overlay.
        if not self.ui_manager.is_overlay:
            self.ui_manager.enter_overlay_mode()

    def get_active_window_title(self):
        """Returns the title of the current foreground window."""
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            return buff.value
        except Exception:
            return ""

    def check_fullscreen(self):
        try:
            user32 = ctypes.windll.user32
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            hwnd = user32.GetForegroundWindow()
            
            if hwnd == self.app_hwnd:
                return self.ui_manager.is_overlay
            
            class RECT(ctypes.Structure):
                _fields_ = [("left", ctypes.c_long),
                            ("top", ctypes.c_long),
                            ("right", ctypes.c_long),
                            ("bottom", ctypes.c_long)]
            
            rect = RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            win_width = rect.right - rect.left
            win_height = rect.bottom - rect.top
            return win_width >= screen_width and win_height >= screen_height
        except Exception:
            return False

    def execute_shortcut(self, gesture):
        if self.ui_manager.is_overlay and gesture == 'OPEN_PALM':
            return

        # Get shortcut from current profile
        profile = config.PROFILES.get(self.current_profile_name, config.PROFILES['DEFAULT'])
        shortcut = profile.get(gesture)
        
        if shortcut:
            try:
                # Audio Feedback
                if not hasattr(self, 'audio'):
                     self.audio = AudioFeedback(enabled=config.AUDIO_FEEDBACK_ENABLED)
                     
                if "SWIPE" in gesture:
                    self.audio.play_swipe_sound()
                else:
                    self.audio.play_static_gesture_sound()
                    
                pyautogui.hotkey(*shortcut)
                print(f"[{self.current_profile_name}] Executed {gesture}: {shortcut}")
            except Exception as e:
                print(f"Failed to execute shortcut: {e}")
                if hasattr(self, 'audio'):
                    self.audio.play_error_sound()
        else:
            # Optional: Play error sound if gesture recognized but not mapped?
            # self.audio.play_error_sound()
            pass

if __name__ == "__main__":
    import customtkinter as ctk
    
    # Enable High DPI scaling
    ctk.set_widget_scaling(1.0)
    ctk.set_window_scaling(1.0)
    
    root = ctk.CTk()
    app = GestureControllerApp(root)
    # Correctly handle window closing
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop(), root.destroy()))
    root.mainloop()
