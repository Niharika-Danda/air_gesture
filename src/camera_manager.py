import threading
import queue
import time
import cv2
import numpy as np
from collections import deque
from src import config
from src.event_bus import EventBus
import logging

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
            # Use DirectShow on Windows for faster/reliable camera access
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                logging.error(f"Failed to open camera {self.camera_index}")
                return
                
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.VIDEO_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.VIDEO_HEIGHT)
            logging.info(f"VisionThread started with camera {self.camera_index}")
            
            # Lazy Loading
            from src.gesture_engine import GestureProcessor
            
            # Lower Thread Priority (Windows) implementation
            try:
                import ctypes
                handle = ctypes.windll.kernel32.GetCurrentThread()
                ctypes.windll.kernel32.SetThreadPriority(handle, -1) # BELOW_NORMAL
            except Exception:
                pass

            self.gesture_processor = GestureProcessor(
                min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
                min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
            )
            
            # Performance Monitoring Variables
            processing_times = deque(maxlen=30)
            frame_skip_counter = 0
            
            while not self.stop_event.is_set():
                ret, frame = self.cap.read()
                if not ret:
                    time.sleep(0.01)
                    continue
                
                # --- Frame Skip Logic ---
                fps = self.cap.get(cv2.CAP_PROP_FPS)
                if fps > 31: 
                    frame_skip_counter += 1
                    if frame_skip_counter % 2 != 0:
                        continue
                
                # --- Adaptive Resolution ---
                avg_process_time = sum(processing_times)/len(processing_times) if processing_times else 0.0
                processing_frame = frame
                
                if avg_process_time > 0.035:
                     scale_factor = 0.75
                     width = int(frame.shape[1] * scale_factor)
                     height = int(frame.shape[0] * scale_factor)
                     processing_frame = cv2.resize(frame, (width, height))
                
                # --- Auto Low Light ---
                self.frame_counter += 1
                if self.frame_counter % 30 == 0:
                     try:
                        small = cv2.resize(frame, (320, 180))
                        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
                        avg = np.mean(gray)
                        if not config.LOW_LIGHT_MODE and avg < 80: config.LOW_LIGHT_MODE = True
                        elif config.LOW_LIGHT_MODE and avg > 100: config.LOW_LIGHT_MODE = False
                     except: pass
                
                t_start = time.time()
                try:
                    gesture, processed_frame, pointer_info, landmarks = self.gesture_processor.process_frame(processing_frame)
                    
                    if processing_times and avg_process_time > 0.035:
                        processed_frame = cv2.resize(processed_frame, (config.VIDEO_WIDTH, config.VIDEO_HEIGHT))
                        
                except ValueError:
                    gesture, processed_frame, pointer_info = self.gesture_processor.process_frame(processing_frame)
                    landmarks = None
                
                t_end = time.time()
                processing_times.append(t_end - t_start)
                
                if self.result_queue.full():
                    try: self.result_queue.get_nowait()
                    except queue.Empty: pass
                
                self.result_queue.put((gesture, processed_frame, pointer_info, landmarks, time.time()))
                
                time.sleep(0.001)
                
        except Exception as e:
            logging.error(f"VisionThread Error: {e}")
        finally:
            if self.cap: self.cap.release()
            if self.gesture_processor: self.gesture_processor.close()

    def stop(self):
        self.stop_event.set()

class CameraManager:
    """
    Manages camera device detection and the VisionThread.
    """
    def __init__(self):
        self.bus = EventBus()
        self.vision_thread = None
        self.result_queue = queue.Queue(maxsize=2)
        
        self.camera_indices = []
        self.camera_names = []
        
        # Subscriptions
        self.bus.subscribe("cmd:start_camera", self.start_camera)
        self.bus.subscribe("cmd:stop_camera", self.stop_camera)
        self.bus.subscribe("cmd:change_camera", self.change_camera)
        self.bus.subscribe("app:quit", self.stop_camera)

    def detect_cameras(self):
        """Fast camera detection."""
        indices = []
        names = []
        for i in range(3):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                indices.append(i)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                friendly_name = config.CAMERA_NAMES.get(i, f"Camera {i}")
                names.append(f"{friendly_name} ({width}x{height})")
            cap.release()
        
        # Reorder preferred
        preferred_idx = config.CAMERA_INDEX
        if preferred_idx in indices:
            pos = indices.index(preferred_idx)
            indices.insert(0, indices.pop(pos))
            names.insert(0, names.pop(pos))
            
        self.camera_indices = indices
        self.camera_names = names
        return indices, names

    def initialize_camera_selection(self):
        self.detect_cameras()
        if not self.camera_indices:
            config.CAMERA_INDEX = -1
        elif config.CAMERA_INDEX not in self.camera_indices:
            config.CAMERA_INDEX = self.camera_indices[0]
        return self.camera_names

    def start_camera(self, _=None):
        if self.vision_thread and self.vision_thread.is_alive():
            return # Already running or restart needed?
        
        self.result_queue = queue.Queue(maxsize=2)
        self.vision_thread = VisionThread(config.CAMERA_INDEX, self.result_queue)
        self.vision_thread.start()
        self.bus.publish("camera:status", "Status: Starting Engine...")
        
        # Give it a moment then confirm running
        threading.Timer(0.1, lambda: self.bus.publish("camera:status", "Status: Running")).start()
        threading.Timer(0.1, lambda: self.bus.publish("camera:started")).start()

    def stop_camera(self, _=None):
        if self.vision_thread:
            self.vision_thread.stop()
            self.vision_thread.join(timeout=2.0)
            self.vision_thread = None
            
            # Clear residual frames
            with self.result_queue.mutex:
                self.result_queue.queue.clear()
            
            self.bus.publish("camera:status", "Status: Stopped")
            self.bus.publish("camera:stopped")

    def change_camera(self, index):
        if index < 0 or index >= len(self.camera_indices): return
        new_idx = self.camera_indices[index]
        
        if new_idx == config.CAMERA_INDEX and self.vision_thread: return
        
        config.CAMERA_INDEX = new_idx
        was_running = self.vision_thread is not None
        
        if was_running:
            self.stop_camera()
            # Wait and restart
            threading.Timer(0.5, self.start_camera).start()

    def get_latest_frame(self):
        """Non-blocking retrieval of latest frame data."""
        if not self.vision_thread:
            return None
            
        latest = None
        while True:
            try:
                latest = self.result_queue.get_nowait()
            except queue.Empty:
                break
        return latest
