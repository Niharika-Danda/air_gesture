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


class OneEuroFilter:
    """
    One Euro Filter for smooth, low-latency signal filtering.
    Better than simple exponential smoothing - reduces jitter while maintaining responsiveness.
    Reference: https://cristal.univ-lille.fr/~casiez/1euro/
    """
    
    def __init__(self, min_cutoff=1.0, beta=0.007, d_cutoff=1.0):
        """
        Args:
            min_cutoff: Minimum cutoff frequency (lower = smoother when still)
            beta: Speed coefficient (higher = more responsive when moving fast)
            d_cutoff: Derivative cutoff frequency
        """
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        
        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None
        
    def reset(self):
        """Reset the filter state."""
        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None
    
    def _alpha(self, cutoff, dt):
        """Compute smoothing factor alpha."""
        tau = 1.0 / (2.0 * np.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)
    
    def filter(self, x, t=None):
        """
        Filter a value.
        
        Args:
            x: Raw value
            t: Timestamp (optional, uses frame time if not provided)
            
        Returns:
            Filtered value
        """
        import time as time_module
        if t is None:
            t = time_module.time()
            
        if self.x_prev is None:
            self.x_prev = x
            self.t_prev = t
            return x
        
        dt = t - self.t_prev
        if dt <= 0:
            dt = 1.0 / 60.0  # Default to 60 FPS
        
        # Estimate derivative
        dx = (x - self.x_prev) / dt
        
        # Filter derivative
        alpha_d = self._alpha(self.d_cutoff, dt)
        dx_hat = alpha_d * dx + (1.0 - alpha_d) * self.dx_prev
        
        # Adaptive cutoff based on speed
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        
        # Filter position
        alpha = self._alpha(cutoff, dt)
        x_hat = alpha * x + (1.0 - alpha) * self.x_prev
        
        # Store for next iteration
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t
        
        return x_hat


class PointerSmoother:
    """
    Specialized smoother for mouse pointer control.
    Uses One Euro Filter + Kalman for responsive yet stable cursor control.
    """
    
    def __init__(self, base_smoothing=0.005, base_responsiveness=0.02):
        """
        Initialize pointer smoother - optimized for FAST, responsive movement.
        """
        # Kalman filter for velocity-aware prediction
        self.kalman = PositionSmoother2D(base_smoothing, base_responsiveness)
        
        # One Euro Filters for final smoothing (one for X, one for Y)
        # Higher min_cutoff = much faster response  
        # Higher beta = very responsive when moving fast
        self.euro_x = OneEuroFilter(min_cutoff=4.0, beta=1.2, d_cutoff=1.0)
        self.euro_y = OneEuroFilter(min_cutoff=4.0, beta=1.2, d_cutoff=1.0)
        
        self.base_smoothing = base_smoothing
        self.base_responsiveness = base_responsiveness
        self.last_position = None
        self.velocity_history = []  # Track recent velocities for smoothing
        self.max_velocity_history = 2  # Very short history for fastest response
    
    def reset(self):
        """Reset the pointer smoother."""
        self.kalman.reset()
        self.euro_x.reset()
        self.euro_y.reset()
        self.last_position = None
        self.velocity_history = []
    
    def update(self, x, y):
        """
        Update pointer position with enhanced smoothing.
        
        Uses a two-stage approach:
        1. Kalman filter for velocity-aware prediction
        2. One Euro Filter for final jitter reduction
        
        Args:
            x, y: Raw pointer position (0.0 to 1.0)
            
        Returns:
            Smoothed (x, y) position
        """
        import time as time_module
        current_time = time_module.time()
        
        # Calculate movement speed for adaptive behavior
        if self.last_position is not None:
            dx = x - self.last_position[0]
            dy = y - self.last_position[1]
            speed = np.sqrt(dx**2 + dy**2)
            
            # Track velocity history for smoother speed detection
            self.velocity_history.append(speed)
            if len(self.velocity_history) > self.max_velocity_history:
                self.velocity_history.pop(0)
            
            avg_speed = np.mean(self.velocity_history)
            
            # Adaptive Kalman - MINIMAL smoothing for fastest response
            if avg_speed > 0.04:  # Fast movement - almost direct tracking
                self.kalman.R = np.eye(2) * (self.base_responsiveness * 0.05)
            elif avg_speed > 0.02:  # Medium-fast movement
                self.kalman.R = np.eye(2) * (self.base_responsiveness * 0.1)
            elif avg_speed > 0.008:  # Medium movement
                self.kalman.R = np.eye(2) * (self.base_responsiveness * 0.3)
            elif avg_speed > 0.002:  # Slow movement
                self.kalman.R = np.eye(2) * (self.base_responsiveness * 0.6)
            else:  # Nearly stationary - light smoothing
                self.kalman.R = np.eye(2) * self.base_responsiveness
        
        self.last_position = (x, y)
        
        # Stage 1: Kalman filter
        kx, ky = self.kalman.update((x, y))
        
        # Stage 2: One Euro Filter for final smoothing
        fx = self.euro_x.filter(kx, current_time)
        fy = self.euro_y.filter(ky, current_time)
        
        return fx, fy
    
    def get_velocity(self):
        """
        Get the current estimated velocity.
        
        Returns:
            Tuple of (vx, vy) velocity
        """
        return self.kalman.get_velocity()
