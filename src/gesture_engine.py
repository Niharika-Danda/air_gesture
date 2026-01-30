# src/gesture_processor.py

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

# Position smoothing imports
from src.position_smoother import LandmarkSmoother, PointerSmoother
from src.gesture_recorder import GestureRecorder

class GestureProcessor:
    """
    Handles the detection of hand landmarks and recognition of gestures from a video frame.
    Supports both static signs and dynamic swipe gestures.
    Uses position smoothing for stable tracking.
    """
    def __init__(self, min_detection_confidence=0.7, min_tracking_confidence=0.5):
        """
        Initializes the hand tracking system and history for dynamic gestures.
        """
        self.mp_hands = mp_hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp_drawing
        self.landmarks = None
        self.filtered_landmarks = None  # Smoothed landmark positions
        
        # Custom Gesture Recorder
        self.recorder = GestureRecorder()
        
        from src import config
        # Swipe Detector
        from src.swipe_engine import SwipeDetector
        self.swipe_detector = SwipeDetector(
            history_length=config.SWIPE_HISTORY_LENGTH if hasattr(config, 'SWIPE_HISTORY_LENGTH') else 10,
            min_dist_left=config.SWIPE_MIN_DISTANCE_LEFT, 
            min_dist_right=config.SWIPE_MIN_DISTANCE_RIGHT,
            min_velocity=0.4 # Fast movement
        )
        
        # Buffer for temporal smoothing of static signs
        self.gesture_buffer = deque(maxlen=config.SMOOTHING_BUFFER_SIZE)
        
        # Debounce/Robustness
        self.missed_frames = 0
        
        # Position smoothers for stable tracking
        self.landmark_smoother = LandmarkSmoother(
            num_landmarks=21,
            smoothing_factor=0.005,
            responsiveness=0.05
        )
        self.pointer_smoother = PointerSmoother(
            base_smoothing=0.02,
            base_responsiveness=0.08
        )
        
        # Legacy pointer state (kept for fallback)
        self.prev_pointer_x = 0
        self.prev_pointer_y = 0

    def process_frame(self, frame):
        """
        Processes a single video frame to detect hand landmarks and recognize a gesture.

        Returns:
            A tuple containing:
            - The name of the recognized gesture (str).
            - The frame with hand landmarks drawn on it (numpy array).
        """
        # Flip the frame horizontally for a later selfie-view display
        # and convert the BGR image to RGB.
        frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        
        # --- Low-Light Enhancement ---
        from src import config
        if config.LOW_LIGHT_MODE:
            # We apply CLAHE to the L-channel of LAB color space to boost local contrast
            lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            limg = cv2.merge((cl,a,b))
            frame = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
        
        frame.setflags(write=False)
        results = self.hands.process(frame)
        frame.setflags(write=True)

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        final_gesture = 'UNKNOWN'
        
        # Mouse Pointer Logic
        pointer_info = None
        
        if results.multi_hand_landmarks:
            self.missed_frames = 0
            
            for hand_landmarks in results.multi_hand_landmarks:
                self.landmarks = hand_landmarks.landmark
                
                # Apply position smoothing to all landmarks for stable tracking
                self.filtered_landmarks = self.landmark_smoother.update(self.landmarks)
                
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # --- POINTER LOGIC (Index Tip with Smoothing) ---
                # Get raw positions
                raw_index_x = self.landmarks[8].x
                raw_index_y = self.landmarks[8].y
                
                # Apply smoothing for stable pointer
                curr_x, curr_y = self.pointer_smoother.update(raw_index_x, raw_index_y)
                
                # Get filtered thumb position for click detection
                thumb_x, thumb_y = self.filtered_landmarks[4] if self.filtered_landmarks else (self.landmarks[4].x, self.landmarks[4].y)
                index_x, index_y = self.filtered_landmarks[8] if self.filtered_landmarks else (self.landmarks[8].x, self.landmarks[8].y)
                
                # Check Click (Pinch) using filtered positions
                from src import config
                pad_dist = math.hypot(index_x - thumb_x, index_y - thumb_y)
                is_clicking = pad_dist < config.CLICK_THRESHOLD
                
                pointer_info = {
                    'x': curr_x,
                    'y': curr_y,
                    'click': is_clicking
                }
                
                # --- GESTURE LOGIC ---
                # Calculate Centroid (Average of Wrist, Index MCP, Pinky MCP)
                wrist = self.landmarks[0]
                index_mcp = self.landmarks[5]
                pinky_mcp = self.landmarks[17]
                
                cx = (wrist.x + index_mcp.x + pinky_mcp.x) / 3.0
                cy = (wrist.y + index_mcp.y + pinky_mcp.y) / 3.0
                current_centroid = (cx, cy)
                
                # 1. Run Trajectory-Based Swipe Detection
                swipe_gesture = self.swipe_detector.process(current_centroid, time.time())
                
                # Check ROI for Static Signs
                from src import config
                in_roi = False
                if config.SIGN_ROI_ENABLED:
                    roi = config.SIGN_ROI_COORDS
                    in_roi = (roi['x_min'] <= cx <= roi['x_max']) and (roi['y_min'] <= cy <= roi['y_max'])
                else:
                    in_roi = True

                # Draw ROI Box
                h, w, _ = frame.shape
                if config.SIGN_ROI_ENABLED:
                    roi = config.SIGN_ROI_COORDS
                    # Color: Green if hand is inside, else Yellow
                    box_color = (0, 255, 0) if in_roi else (0, 255, 255) 
                    cv2.rectangle(frame, 
                                  (int(roi['x_min']*w), int(roi['y_min']*h)), 
                                  (int(roi['x_max']*w), int(roi['y_max']*h)), 
                                  box_color, 4)
                    cv2.putText(frame, "Sign Zone", (int(roi['x_min']*w)+5, int(roi['y_min']*h)+20), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 1)

                if swipe_gesture != 'UNKNOWN':
                     final_gesture = swipe_gesture
                     self.gesture_buffer.clear()
                     # Reset static tracking if swipe occurs
                elif in_roi:
                    # 2. Static Signs (Only if in ROI)
                    # 2. Static Signs
                    raw_gesture = self._recognize_gesture()
                    self.gesture_buffer.append(raw_gesture)
                    if self.gesture_buffer:
                         from src import config
                         most_common = Counter(self.gesture_buffer).most_common(1)
                         gesture_name, count = most_common[0]
                         if count >= config.GESTURE_CONFIRMATION_FRAMES:
                             # Check Allowlist
                             if gesture_name in config.ENABLED_SIGNS:
                                 final_gesture = gesture_name
                             else:
                                 final_gesture = 'UNKNOWN'
                         else:
                             final_gesture = 'UNKNOWN'
                else:
                    # Hand detected but outside ROI - Clear static history
                     self.gesture_buffer.clear()
        else:
            from src import config
            self.missed_frames += 1
            if self.missed_frames > config.MAX_MISSED_FRAMES:
                # Reset detector state if hand is lost for too long
                self.gesture_buffer.clear()
                self.landmarks = None
                self.filtered_landmarks = None
                # Reset smoothers so they reinitialize when hand reappears
                self.landmark_smoother.reset()
                self.pointer_smoother.reset()

        return final_gesture, frame, pointer_info, self.landmarks


    def _recognize_gesture(self):
        """
        Recognizes a specific static sign based on the positions of hand landmarks.
        Uses rotation-invariant geometry (distance ratios) for robustness.
        """
        if not self.landmarks:
            return 'UNKNOWN'

        wrist = self.landmarks[0]
        
        # Robust Finger State Detection (Rotation Independent)
        # Checks if Tip is further from Wrist than PIP joint
        def is_finger_extended(tip_idx, pip_idx):
            tip = self.landmarks[tip_idx]
            pip = self.landmarks[pip_idx]
            
            d_tip_wrist = math.hypot(tip.x - wrist.x, tip.y - wrist.y)
            d_pip_wrist = math.hypot(pip.x - wrist.x, pip.y - wrist.y)
            
            return d_tip_wrist > d_pip_wrist

        # Robust Thumb State
        # Check angle between Thumb Tip, MCP, and Index MCP for "out" ness?
        # Simpler: Check distance of Thumb Tip to Pinky MCP vs Thumb IP to Pinky MCP
        thumb_tip = self.landmarks[4]
        thumb_ip = self.landmarks[3]
        pinky_mcp = self.landmarks[17]
        
        d_tip_pinky = math.hypot(thumb_tip.x - pinky_mcp.x, thumb_tip.y - pinky_mcp.y)
        d_ip_pinky = math.hypot(thumb_ip.x - pinky_mcp.x, thumb_ip.y - pinky_mcp.y)
        
        thumb_extended = d_tip_pinky > d_ip_pinky
        
        # Check other fingers (Tip vs PIP check is robust for rotation)
        index_extended = is_finger_extended(8, 6)
        middle_extended = is_finger_extended(12, 10)
        ring_extended = is_finger_extended(16, 14)
        pinky_extended = is_finger_extended(20, 18)

        # 1. Identify Hand SHAPE first (Orientation Independent)
        shape = 'UNKNOWN'
        
        if thumb_extended and index_extended and middle_extended and ring_extended and pinky_extended:
            return 'OPEN_PALM'
            
        elif not thumb_extended and not index_extended and not middle_extended and not ring_extended and not pinky_extended:
            return 'FIST'
            
        elif not thumb_extended and index_extended and not middle_extended and not ring_extended and not pinky_extended:
            return 'INDEX_POINTING_UP' # Shape is "One Finger", direction implies UP but we key off shape
            
        elif not thumb_extended and index_extended and middle_extended and not ring_extended and not pinky_extended:
            return 'V_SIGN'
            
        elif thumb_extended and index_extended and not middle_extended and not ring_extended and pinky_extended:
            return 'SPIDERMAN'
            
        elif self._is_ok_sign():
            return 'OK_SIGN'
            
        # Thumbs Up/Down Shape: Thumb Extended, others curled
        elif thumb_extended and not index_extended and not middle_extended and not ring_extended and not pinky_extended:
             # Now check orientation for Up/Down
             # Compare Thumb Tip Y vs Thumb IP Y
             # Note: This PART is still orientation dependent because "Up" is a direction relative to the screen
             if self.landmarks[4].y < self.landmarks[3].y: # Tip above IP
                 return 'THUMBS_UP'
             else:
                 return 'THUMBS_DOWN'
        
        # Check for Custom Gestures
        custom_match = self.recorder.find_match(self.landmarks)
        if custom_match:
            return custom_match

        return 'UNKNOWN'

    def _is_ok_sign(self):
        index_tip = self.landmarks[8]
        thumb_tip = self.landmarks[4]
        distance = math.sqrt((index_tip.x - thumb_tip.x)**2 + (index_tip.y - thumb_tip.y)**2)
        
        def is_finger_extended(tip_idx, pip_idx):
             return self.landmarks[tip_idx].y < self.landmarks[pip_idx].y

        middle_extended = is_finger_extended(12, 10)
        ring_extended = is_finger_extended(16, 14)
        pinky_extended = is_finger_extended(20, 18)
        
        return distance < 0.08 and middle_extended and ring_extended and pinky_extended

    def close(self):
        """Releases the hand tracking resources."""
        self.hands.close()
