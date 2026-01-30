# tests/test_logic.py

import sys
import os
import time

# Fix path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.gesture_engine import GestureProcessor
from src import config

class MockLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def test_swipe_detection():
    print("Testing Swipe Detection...")
    processor = GestureProcessor()
    
    # Simulate a RIGHT swipe (X increasing)
    print("Simulating SWIPE_RIGHT...")
    for i in range(10):
        mock_wrist = MockLandmark(0.1 + (i * 0.05), 0.5)
        # We need to mock the landmark access in processor
        processor.landmarks = [mock_wrist]
        processor.history.append((mock_wrist.x, mock_wrist.y, time.time()))
        
    gesture = processor._detect_swipe()
    print(f"Result: {gesture}")
    assert gesture == 'SWIPE_RIGHT'
    print("SWIPE_RIGHT test passed!\n")

def test_profile_logic():
    print("Testing Profile Switching Logic...")
    # Mocking config.WINDOW_PROFILE_MAP check as done in main.py
    window_titles = [
        "Presentation1 - PowerPoint",
        "Google Chrome - Github",
        "My Document - Word"
    ]
    
    expected_profiles = [
        "POWERPOINT",
        "CHROME",
        "DEFAULT"
    ]
    
    for title, expected in zip(window_titles, expected_profiles):
        detected_profile = 'DEFAULT'
        for title_part, profile_name in config.WINDOW_PROFILE_MAP.items():
            if title_part.lower() in title.lower():
                detected_profile = profile_name
                break
        print(f"Title: '{title}' -> Profile: {detected_profile}")
        assert detected_profile == expected
    
    print("Profile logic tests passed!\n")

if __name__ == "__main__":
    try:
        test_swipe_detection()
        test_profile_logic()
        print("All logic tests passed successfully!")
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"An error occurred during testing: {e}")
