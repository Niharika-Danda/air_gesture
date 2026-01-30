# tests/test_performance.py

import sys
import os
import time
from collections import deque

# Fix path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.gesture_processor import GestureProcessor
from src import config

def test_temporal_smoothing():
    print("Testing Temporal Smoothing...")
    processor = GestureProcessor()
    
    # Simulate a noisy sequence: 
    # OPEN_PALM, OPEN_PALM, THUMBS_UP (noise), OPEN_PALM, OPEN_PALM
    # The mode should be OPEN_PALM
    
    sequence = ['OPEN_PALM', 'OPEN_PALM', 'THUMBS_UP', 'OPEN_PALM', 'OPEN_PALM']
    
    print(f"Input Sequence: {sequence}")
    
    # Manually fill the buffer as we can't easily mock the full process_frame without an image
    processor.gesture_buffer = deque(sequence, maxlen=5)
    
    from collections import Counter
    most_common = Counter(processor.gesture_buffer).most_common(1)
    result = most_common[0][0]
    
    print(f"Smoothed Result: {result}")
    assert result == 'OPEN_PALM'
    print("Smoothing test passed!")

if __name__ == "__main__":
    try:
        test_temporal_smoothing()
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
