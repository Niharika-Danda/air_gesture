import ctypes
from ctypes import wintypes
import os

# Define required Windows API structures and constants
class WindowManager:
    """
    Provides robust methods to get information about the active window,
    including Title, Process Name, and Window Class.
    """
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.psapi = ctypes.windll.psapi
        self.kernel32 = ctypes.windll.kernel32
        
        # Constants
        self.PROCESS_QUERY_INFORMATION = 0x0400
        self.PROCESS_VM_READ = 0x0010

    def get_active_window_info(self):
        """
        Returns a dictionary containing:
        - 'title': Window Title
        - 'process': Process Executable Name (e.g., 'chrome.exe')
        - 'class': Window Class Name
        """
        hwnd = self.user32.GetForegroundWindow()
        if not hwnd:
            return {'title': "", 'process': "", 'class': ""}

        return {
            'title': self._get_window_title(hwnd),
            'process': self._get_window_process_name(hwnd),
            'class': self._get_window_class(hwnd)
        }

    def _get_window_title(self, hwnd):
        length = self.user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return ""
        buff = ctypes.create_unicode_buffer(length + 1)
        self.user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value

    def _get_window_class(self, hwnd):
        buff = ctypes.create_unicode_buffer(256)
        self.user32.GetClassNameW(hwnd, buff, 256)
        return buff.value

    def _get_window_process_name(self, hwnd):
        pid = wintypes.DWORD()
        self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        h_process = self.kernel32.OpenProcess(
            self.PROCESS_QUERY_INFORMATION | self.PROCESS_VM_READ,
            False, 
            pid
        )
        
        if not h_process:
            return ""
            
        try:
            # GetModuleBaseNameW is often enough and safer/easier than full path
            buff = ctypes.create_unicode_buffer(1024)
            if self.psapi.GetModuleBaseNameW(h_process, None, buff, 1024):
                return buff.value
            
            # Fallback to GetProcessImageFileNameW if ModuleBaseName fails (sometimes happens for elevated processes)
            if self.psapi.GetProcessImageFileNameW(h_process, buff, 1024):
                full_path = buff.value
                return os.path.basename(full_path)
                
            return ""
        finally:
            self.kernel32.CloseHandle(h_process)
