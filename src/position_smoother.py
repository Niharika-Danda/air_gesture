# src/position_smoother.py
"""
Position smoothing implementation for stable hand tracking.
Reduces jitter and provides smooth gesture recognition.
"""

import numpy as np


class PositionSmoother2D:
    """
    A 2D position smoother for tracking hand position (x, y).
    Uses velocity-aware prediction for smooth tracking.
    """
    
    def __init__(self, smoothing_factor=0.01, responsiveness=0.1):
        """
        Initialize the position smoother.
        
        Args:
            smoothing_factor: How much smoothing to apply (lower = smoother)
            responsiveness: How responsive to new measurements (higher = more smoothing)
        """
        # State vector: [x, y, vx, vy] (position and velocity)
        self.state = np.zeros(4)
        
        # State transition matrix (velocity-based prediction)
        self.dt = 1.0 / 30.0  # Assume ~30 FPS
        self.F = np.array([
            [1, 0, self.dt, 0],
            [0, 1, 0, self.dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        # Measurement matrix (we only measure x, y position)
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])
        
        # Smoothing parameters
        self.Q = np.eye(4) * smoothing_factor
        self.Q[2, 2] = smoothing_factor * 2
        self.Q[3, 3] = smoothing_factor * 2
        
        # Responsiveness parameters
        self.R = np.eye(2) * responsiveness
        
        # Estimation error covariance
        self.P = np.eye(4) * 1.0
        
        # Identity matrix
        self.I = np.eye(4)
        
        # Initialization flag
        self.initialized = False
    
    def reset(self):
        """Reset the smoother state."""
        self.state = np.zeros(4)
        self.P = np.eye(4) * 1.0
        self.initialized = False
    
    def predict(self):
        """
        Predict the next position based on current velocity.
        
        Returns:
            Predicted (x, y) position
        """
        if not self.initialized:
            return None
            
        # State prediction
        self.state = self.F @ self.state
        
        # Covariance prediction
        self.P = self.F @ self.P @ self.F.T + self.Q
        
        return self.state[0], self.state[1]
    
    def update(self, measurement):
        """
        Update the position with a new measurement.
        
        Args:
            measurement: Tuple of (x, y) position
            
        Returns:
            Smoothed (x, y) position
        """
        z = np.array(measurement)
        
        if not self.initialized:
            # First measurement - initialize state
            self.state[0] = z[0]
            self.state[1] = z[1]
            self.state[2] = 0  # Initial velocity x
            self.state[3] = 0  # Initial velocity y
            self.initialized = True
            return z[0], z[1]
        
        # Predict step
        self.predict()
        
        # Measurement residual
        y = z - self.H @ self.state
        
        # Residual covariance
        S = self.H @ self.P @ self.H.T + self.R
        
        # Smoothing gain
        K = self.P @ self.H.T @ np.linalg.inv(S)
        
        # State update
        self.state = self.state + K @ y
        
        # Covariance update
        self.P = (self.I - K @ self.H) @ self.P
        
        return self.state[0], self.state[1]
    
    def get_velocity(self):
        """
        Get the current estimated velocity.
        
        Returns:
            Tuple of (vx, vy) velocity
        """
        if self.initialized:
            return self.state[2], self.state[3]
        return 0, 0


class LandmarkSmoother:
    """
    Smoothing manager for multiple hand landmarks.
    Provides stable tracking for all 21 hand landmarks.
    """
    
    def __init__(self, num_landmarks=21, smoothing_factor=0.005, responsiveness=0.05):
        """
        Initialize smoothers for each landmark.
        
        Args:
            num_landmarks: Number of hand landmarks (21 points)
            smoothing_factor: Smoothing factor for position changes
            responsiveness: How responsive to new positions
        """
        self.smoothers = [
            PositionSmoother2D(smoothing_factor, responsiveness) 
            for _ in range(num_landmarks)
        ]
        self.num_landmarks = num_landmarks
    
    def reset(self):
        """Reset all landmark smoothers."""
        for s in self.smoothers:
            s.reset()
    
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
    
    def get_smoothed_position(self, landmark_idx, raw_x, raw_y):
        """
        Get smoothed position for a single landmark.
        
        Args:
            landmark_idx: Index of the landmark (0-20)
            raw_x, raw_y: Raw measured position
            
        Returns:
            Smoothed (x, y) position
        """
        if 0 <= landmark_idx < self.num_landmarks:
            return self.smoothers[landmark_idx].update((raw_x, raw_y))
        return raw_x, raw_y


class PointerSmoother:
    """
    Specialized smoother for mouse pointer control.
    Uses adaptive smoothing based on movement speed for responsive yet stable control.
    """
    
    def __init__(self, base_smoothing=0.02, base_responsiveness=0.08):
        """
        Initialize pointer smoother with adaptive parameters.
        """
        self.smoother = PositionSmoother2D(base_smoothing, base_responsiveness)
        self.base_smoothing = base_smoothing
        self.base_responsiveness = base_responsiveness
        self.last_position = None
    
    def reset(self):
        """Reset the pointer smoother."""
        self.smoother.reset()
        self.last_position = None
    
    def update(self, x, y):
        """
        Update pointer position with adaptive smoothing.
        
        When moving fast: Less smoothing for responsiveness
        When stationary/slow: More smoothing for stability
        
        Args:
            x, y: Raw pointer position (0.0 to 1.0)
            
        Returns:
            Smoothed (x, y) position
        """
        # Calculate movement speed
        if self.last_position is not None:
            dx = x - self.last_position[0]
            dy = y - self.last_position[1]
            speed = np.sqrt(dx**2 + dy**2)
            
            # Adaptive smoothing: faster movement = trust measurements more
            if speed > 0.05:  # Fast movement
                self.smoother.R = np.eye(2) * (self.base_responsiveness * 0.3)
            elif speed > 0.02:  # Medium movement
                self.smoother.R = np.eye(2) * self.base_responsiveness
            else:  # Slow/stationary
                self.smoother.R = np.eye(2) * (self.base_responsiveness * 2.0)
        
        self.last_position = (x, y)
        return self.smoother.update((x, y))
