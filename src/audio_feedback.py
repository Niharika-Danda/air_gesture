# src/audio_feedback.py
import winsound
import threading
import time

class AudioFeedback:
    def __init__(self, enabled=True):
        self.enabled = enabled
        
    def set_enabled(self, enabled):
        self.enabled = enabled

    def _play_freq(self, freq, duration):
        if not self.enabled: return
        try:
            winsound.Beep(freq, duration)
        except Exception:
            pass

    def play_swipe_sound(self):
        """Short high pitch beep for swipes"""
        threading.Thread(target=self._play_freq, args=(1200, 100), daemon=True).start()

    def play_static_gesture_sound(self):
        """Two-tone confirmation for static gestures"""
        def _sound():
            self._play_freq(800, 100)
            time.sleep(0.05)
            self._play_freq(1200, 100)
        threading.Thread(target=_sound, daemon=True).start()

    def play_error_sound(self):
        """Low pitch tone for errors"""
        threading.Thread(target=self._play_freq, args=(300, 300), daemon=True).start()
