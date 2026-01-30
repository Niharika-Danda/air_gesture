import cv2
import time
import numpy as np

class AutoCalibrator:
    """
    Handles automatic detection of the best camera and assessment of lighting conditions.
    """
    
    def run_auto_calibration(self):
        """
        Scans available cameras, selects the best one based on resolution and validity,
        and checks if low-light mode should be enabled.
        
        Returns:
            dict: {
                'best_camera_index': int,
                'suggested_low_light_mode': bool,
                'log': list of str (for UI/Console)
            }
        """
        print("DEBUG: Starting Auto Calibration...")
        log = []
        available_cameras = []
        
        # 1. Scan Cameras (Indices 0-3)
        for i in range(4):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    # Get properties
                    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    
                    # Calculate brightness score (Mean Intensity)
                    # Convert to grayscale for simple brightness
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    mean_brightness = np.mean(gray)
                    
                    # Store info
                    cam_info = {
                        'index': i,
                        'res': width * height,
                        'brightness': mean_brightness,
                        'valid': True
                    }
                    available_cameras.append(cam_info)
                    log.append(f"Camera {i}: {int(width)}x{int(height)}, Brightness: {mean_brightness:.1f}")
                else:
                    log.append(f"Camera {i}: Failed to read frame.")
                cap.release()
            else:
                pass # Camera not found
                
        if not available_cameras:
            log.append("No cameras found.")
            return {
                'best_camera_index': 0,
                'suggested_low_light_mode': False,
                'log': log
            }
            
        # 2. Select Best Camera
        # Strategy: Prefer Higher Resolution. If tie, prefer lower index.
        # Check if brightness is usable (> 20). If completely black, skip unless it's the only one.
        
        # Sort by Resolution (Desc), then Index (Asc)
        available_cameras.sort(key=lambda x: (-x['res'], x['index']))
        
        best_cam = available_cameras[0]
        log.append(f"Selected Camera {best_cam['index']} as best candidate.")
        
        # 3. Analyze Lighting on Best Camera
        # Determine Low Light Mode
        # Threshold: if mean brightness < 90 (out of 255), it's dim.
        is_low_light = best_cam['brightness'] < 90
        
        if is_low_light:
            log.append(f"Low Light Detected (Level {best_cam['brightness']:.1f}). Enabling Enhancement.")
        else:
            log.append(f"Lighting is adequate (Level {best_cam['brightness']:.1f}).")
            
        return {
            'best_camera_index': best_cam['index'],
            'suggested_low_light_mode': is_low_light,
            'log': log
        }

if __name__ == "__main__":
    # Test run
    cal = AutoCalibrator()
    result = cal.run_auto_calibration()
    print("Result:", result)
