import numpy as np
from collections import deque
import time

class SwipeDetector:
    """
    Robust Swipe Detector using Least Squares Regression.
    
    Uses numpy.polyfit to analyze the geometric properties of the hand trajectory.
    Enforces strict linearity and velocity constraints to prevent false positives.
    """
    def __init__(self, history_length=15, min_dist_left=0.10, min_dist_right=0.10, min_velocity=0.3):
        self.history = deque(maxlen=history_length)
        self.min_dist_left = min_dist_left
        self.min_dist_right = min_dist_right
        self.min_velocity = min_velocity
        self.cooldown = 0.3
        self.last_swipe_time = 0
        
        # Constraints (Relaxed for casual usage)
        self.MAX_SLOPE = 1.0         # Max slope (45 degrees) - Allow diagonal swipes
        self.MAX_MSE = 0.02          # Max Mean Squared Error - Allow wavy lines
        self.MAX_Y_VARIANCE = 0.1    # Max vertical variance - Allow vertical drift
        
        self.debug = True # Enable debug prints to console

    def process(self, centroid, timestamp):
        """
        Input: centroid (x, y) normalized 0.0-1.0, timestamp (seconds)
        Output: 'SWIPE_LEFT', 'SWIPE_RIGHT', or 'UNKNOWN'
        """
        # 1. Cooldown Check
        if timestamp - self.last_swipe_time < self.cooldown:
             # Keep tracking but don't trigger
             pass

        # 2. Add to history
        self.history.append((centroid[0], centroid[1], timestamp))
        
        # Need enough points for regression
        if len(self.history) < 5:
            return 'UNKNOWN'

        if timestamp - self.last_swipe_time < self.cooldown:
             return 'UNKNOWN'

        # 3. Analyze Trajectory
        # Copy to numpy arrays
        data = np.array(self.history)
        xs = data[:, 0]
        ys = data[:, 1]
        ts = data[:, 2]
        
        # Calculate Vectors
        start_x, start_y = xs[0], ys[0]
        end_x, end_y = xs[-1], ys[-1]
        
        dx = end_x - start_x
        dy = end_y - start_y
        dist_x = abs(dx)
        
        duration = ts[-1] - ts[0]
        if duration < 0.05: return 'UNKNOWN'
        
        velocity_x = dist_x / duration
        
        # --- STAGE 1: Fast Rejection (Cheap Checks) ---
        
        # A. Velocity Check
        if velocity_x < self.min_velocity:
            return 'UNKNOWN'
            
        # B. Distance Check (Direction Dependant)
        target_dist = self.min_dist_right if dx > 0 else self.min_dist_left
        if dist_x < target_dist:
            return 'UNKNOWN'
            
        # C. Vertical Variance Check (Must be tight)
        if np.std(ys) > self.MAX_Y_VARIANCE:
            return 'UNKNOWN'

        # --- STAGE 2: Geometric Analysis (Least Squares) ---
        
        # Fit Line: y = mx + c
        try:
            slope, intercept = np.polyfit(xs, ys, 1)
        except Exception:
            return 'UNKNOWN' 
            
        # D. Slope Check 
        if abs(slope) > self.MAX_SLOPE:
            if self.debug: print(f"DEBUG: Swipe Rejected. Slope too steep: {abs(slope):.2f} > {self.MAX_SLOPE}")
            return 'UNKNOWN'
            
        # E. Linearity Check
        predicted_ys = slope * xs + intercept
        mse = np.mean((ys - predicted_ys)**2)
        
        if mse > self.MAX_MSE:
             if self.debug: print(f"DEBUG: Swipe Rejected. Too wavy (MSE): {mse:.4f} > {self.MAX_MSE}")
             return 'UNKNOWN'

        if self.debug: print(f"DEBUG: SWIPE DETECTED! Dir:{'R' if dx>0 else 'L'} Dist:{dist_x:.2f} Slope:{slope:.2f}")

        # --- TRIGGER ---
        
        self.history.clear()
        self.last_swipe_time = timestamp
        
        if dx > 0:
            return 'SWIPE_RIGHT'
        else:
            return 'SWIPE_LEFT'
