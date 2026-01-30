# src/gesture_recorder.py
import json
import os
import math
import numpy as np

GESTURES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'custom_gestures.json')

class GestureRecorder:
    def __init__(self):
        self.gestures = {}
        self.load_gestures()
        
    def load_gestures(self):
        if os.path.exists(GESTURES_FILE):
            try:
                with open(GESTURES_FILE, 'r') as f:
                    self.gestures = json.load(f)
                print(f"Loaded {len(self.gestures)} custom gestures.")
            except Exception as e:
                print(f"Error loading gestures: {e}")
                self.gestures = {}

    def save_gesture(self, name, landmarks):
        """
        Save a normalized version of the landmarks.
        landmarks: List of objects with x, y attributes (MediaPipe format)
        """
        normalized = self._normalize_landmarks(landmarks)
        self.gestures[name] = normalized
        
        try:
            with open(GESTURES_FILE, 'w') as f:
                json.dump(self.gestures, f, indent=4)
            print(f"Saved gesture '{name}'.")
            return True
        except Exception as e:
            print(f"Error saving gesture: {e}")
            return False

    def find_match(self, landmarks, threshold=0.05):
        """
        Compare current landmarks against saved gestures.
        Returns the name of the best matching gesture if error < threshold.
        """
        if not self.gestures:
            return None
            
        current_norm = self._normalize_landmarks(landmarks)
        
        best_match = None
        min_error = float('inf')
        
        for name, saved_norm in self.gestures.items():
            error = self._calculate_error(current_norm, saved_norm)
            if error < min_error:
                min_error = error
                best_match = name
                
        if min_error < threshold:
            return best_match
        return None

    def _normalize_landmarks(self, landmarks):
        """
        Normalize landmarks to be scale and position invariant.
        1. Center wrist (0) at (0,0)
        2. Scale by size (distance from wrist to middle finger MCP (9))
        """
        points = np.array([[lm.x, lm.y] for lm in landmarks])
        
        # Center at wrist (point 0)
        wrist = points[0]
        centered = points - wrist
        
        # Scale by size (Distance from Wrist(0) to Middle MCP(9))
        # This is a stable reference for hand size
        scale_ref = np.linalg.norm(centered[9])
        if scale_ref < 1e-6: scale_ref = 1.0
        
        normalized = centered / scale_ref
        
        # Flatten to list for JSON serialization
        return normalized.tolist()

    def _calculate_error(self, norm1, norm2):
        """Mean Squared Error between two normalized sets."""
        a = np.array(norm1)
        b = np.array(norm2)
        return np.mean(np.square(a - b))
