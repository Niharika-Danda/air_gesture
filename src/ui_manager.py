# src/ui_manager.py

import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import ctypes
import time 

# Set modern look
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ToastOverlay:
    """
    A transparent, frameless overlay window for visual feedback.
    """
    def __init__(self, root):
        self.top = ctk.CTkToplevel(root)
        self.top.overrideredirect(True)
        self.top.attributes("-topmost", True)
        self.top.attributes("-alpha", 0.85)
        
        # Position centered top
        screen_w = self.top.winfo_screenwidth()
        width = 300
        height = 60
        x = (screen_w - width) // 2
        y = 100
        self.top.geometry(f"{width}x{height}+{x}+{y}")
        
        self.top.withdraw() # Start hidden
        
        self.label = ctk.CTkLabel(
            self.top, 
            text="", 
            font=("Roboto", 24, "bold"), 
            fg_color="#333333", 
            text_color="white", 
            corner_radius=15
        )
        self.label.pack(expand=True, fill="both", padx=2, pady=2)
        
        self.hide_job = None
        self.emoji_map = {
            'SWIPE_LEFT': '◀️ Previous',
            'SWIPE_RIGHT': '▶️ Next',
            'THUMBS_UP': '👍 Like',
            'THUMBS_DOWN': '👎 Dislike',
            'OPEN_PALM': '✋ Stop',
            'OK_SIGN': '👌 OK',
            'V_SIGN': '✌️ Custom',
            'INDEX_POINTING_UP': '☝️ Pointer',
            'SPIDERMAN': '🕸️ Spidey'
        }

    def show(self, gesture):
        text = self.emoji_map.get(gesture, gesture)
        self.label.configure(text=text)
        
        self.top.deiconify()
        self.top.attributes("-topmost", True)
        
        if self.hide_job:
            self.top.after_cancel(self.hide_job)
        self.hide_job = self.top.after(1500, self.hide)

    def hide(self):
        self.top.withdraw()

from src.event_bus import EventBus

class AppUIManager:
    """
    Manages the CustomTkinter-based graphical user interface.
    """
    def __init__(self, root, window_title, available_cameras):
        self.bus = EventBus()
        self.root = root
        self.root.title(window_title)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Subscriptions
        self.bus.subscribe("camera:status", self.update_status)
        self.bus.subscribe("camera:started", self.on_camera_started)
        self.bus.subscribe("camera:stopped", self.on_camera_stopped)
        
        self.is_camera_running = False
        
        # Initialize Toast
        self.toast = ToastOverlay(self.root)
        
        # Animation State
        self.pulse_job = None
        self.pulse_alpha = 1.0
        self.pulse_direction = -1
        
        self.root.geometry("1100x750") # Wider for sidebar

        # --- Main Container (Sidebar + Content) ---
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # 1. Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1) # Spacer push to bottom

        # App Logo / Title
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Air Gesture\nController", font=("Roboto", 20, "bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Controls in Sidebar
        self.start_button = ctk.CTkButton(self.sidebar_frame, text="Start Camera", command=self.on_start_click, fg_color="#28a745", hover_color="#218838", state="disabled")
        self.start_button.grid(row=1, column=0, padx=20, pady=10)

        self.stop_button = ctk.CTkButton(self.sidebar_frame, text="Stop Camera", command=self.on_stop_click, fg_color="#dc3545", hover_color="#c82333", state="disabled")
        self.stop_button.grid(row=2, column=0, padx=20, pady=10)
        
        # Camera Selection
        ctk.CTkLabel(self.sidebar_frame, text="Select Camera:", anchor="w").grid(row=3, column=0, padx=20, pady=(20, 0), sticky="w")
        self.camera_combo = ctk.CTkComboBox(
            self.sidebar_frame, 
            values=available_cameras if available_cameras else ["No Camera"],
            command=self.on_camera_change
        )
        self.camera_combo.grid(row=4, column=0, padx=20, pady=10)
        
        # Settings at Bottom
        self.settings_button = ctk.CTkButton(self.sidebar_frame, text="Settings ⚙️", command=self.open_settings, fg_color="transparent", border_width=1)
        self.settings_button.grid(row=6, column=0, padx=20, pady=20)

        # 2. Content Frame
        self.content_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(1, weight=1) # Canvas expands
        self.content_frame.grid_columnconfigure(0, weight=1)

        # 2.1 Stats Dashboard (Top Bar)
        self.stats_frame = ctk.CTkFrame(self.content_frame, height=80, corner_radius=10)
        self.stats_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        self.stats_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        # Helper to create stats
        def create_stat_card(parent, col, title, initial_value, icon_char):
             card = ctk.CTkFrame(parent, fg_color="transparent")
             card.grid(row=0, column=col, padx=10, pady=10)
             
             icon = ctk.CTkLabel(card, text=icon_char, font=("Roboto", 24))
             icon.pack(side="left", padx=(0, 10))
             
             data = ctk.CTkFrame(card, fg_color="transparent")
             data.pack(side="left")
             
             lbl_title = ctk.CTkLabel(data, text=title, font=("Roboto", 12), text_color="gray")
             lbl_title.pack(anchor="w")
             
             lbl_val = ctk.CTkLabel(data, text=initial_value, font=("Roboto", 16, "bold"))
             lbl_val.pack(anchor="w")
             return lbl_val

        self.fps_label = create_stat_card(self.stats_frame, 0, "FPS", "0", "⚡")
        self.profile_label = create_stat_card(self.stats_frame, 1, "Profile", "Default", "🏠")
        self.gesture_label = create_stat_card(self.stats_frame, 2, "Last Gesture", "-", "👋")
        
        # Status Label (merged into dashboard or separate)
        self.status_label = ctk.CTkLabel(self.stats_frame, text="Idle", font=("Roboto", 14), text_color="gray")
        self.status_label.grid(row=0, column=3, padx=20)
        
        # Smart Context Hints Label (Bottom Row of Content Frame or below dashboard)
        self.hints_label = ctk.CTkLabel(self.content_frame, text="", font=("Roboto", 12, "italic"), text_color="#aaaaaa")
        self.hints_label.grid(row=2, column=0, pady=5)
        
        # 2.2 Video Canvas
        self.canvas_frame = ctk.CTkFrame(self.content_frame) # Background frame for canvas
        self.canvas_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#1a1a1a", highlightthickness=0, borderwidth=0)
        self.canvas.pack(fill="both", expand=True)

        # Opacity Slider (Moving to corner or sidebar? Let's keep in sidebar for cleanliness)
        ctk.CTkLabel(self.sidebar_frame, text="Overlay Opacity:", anchor="w").grid(row=7, column=0, padx=20, pady=(10,0), sticky="w")
        self.opacity_slider = ctk.CTkSlider(self.sidebar_frame, from_=0.2, to=1.0, command=self.change_opacity)
        self.opacity_slider.set(1.0)
        self.opacity_slider.grid(row=8, column=0, padx=20, pady=(0, 20))

        # Other internal states
        self.photo = None
        self.is_overlay = False
        self.settings_window = None
        self.preview_window = None
        self.preview_canvas = None
        self.preview_photo = None
        self._drag_start_x = 0
        self._drag_start_y = 0
        self.close_button = None
        
        # Control Bar State
        self.control_bar = None
        self.control_bar_visible = False
        
        self.gesture_overlay_text = None
        self.gesture_overlay_start_time = 0
        self.gesture_display_duration = 1.0 # Seconds
        
        self.current_fps = 0
        self.tracking_quality = 0.0
        self.is_hand_detected = False
        self.feedback_label = None
        self.config_callback = None

    def _get_cam_index(self, choice, all_cams):
        try:
            return all_cams.index(choice)
        except ValueError:
            return 0

    def open_settings(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            from src import config # Lazy import
            
            self.settings_window = ctk.CTkToplevel(self.root)
            self.settings_window.title("Settings")
            self.settings_window.geometry("500x700") # Increased height for signs box
            self.settings_window.attributes("-topmost", True)
            
            # Tab View
            tabview = ctk.CTkTabview(self.settings_window)
            tabview.pack(fill="both", expand=True, padx=20, pady=20)
            
            tab_gen = tabview.add("General")
            tab_gest = tabview.add("Gestures (Default)")
            
            # --- General Tab ---
            # --- General Tab ---
            ctk.CTkLabel(tab_gen, text="Detection Confidence (Sensitivity)", font=("Roboto", 14, "bold")).pack(pady=(20, 5))
            
            conf_label = ctk.CTkLabel(tab_gen, text="", font=("Roboto", 11), text_color="gray")
            
            def update_conf_text(value):
                val = float(value)
                if val >= 0.8:
                    msg = f"{val:.1f}: Strict. Needs clear hand visibility. zero false positives."
                elif val >= 0.6:
                    msg = f"{val:.1f}: Balanced. Recommended for most users."
                else: 
                    msg = f"{val:.1f}: High Sensitivity. Works in bad light, might misfire."
                conf_label.configure(text=msg)

            confidence_var = ctk.DoubleVar(value=config.MIN_DETECTION_CONFIDENCE)
            slider = ctk.CTkSlider(
                tab_gen, 
                from_=0.1, 
                to=1.0, 
                variable=confidence_var, 
                number_of_steps=9,
                command=update_conf_text
            )
            slider.pack(pady=5)
            conf_label.pack()
            update_conf_text(config.MIN_DETECTION_CONFIDENCE) # Init
            
            ctk.CTkLabel(tab_gen, text="Gesture Cooldown (Seconds)", font=("Roboto", 14, "bold")).pack(pady=(20, 5))
            
            cd_label = ctk.CTkLabel(tab_gen, text="", font=("Roboto", 11), text_color="gray")
            
            def update_cd_text(value):
                val = float(value)
                if val >= 1.0:
                    msg = f"{val:.1f}s: Slow. Prevents accidental double-clicks."
                elif val >= 0.5:
                    msg = f"{val:.1f}s: Normal. Good for slides/presentations."
                else:
                    msg = f"{val:.1f}s: Rapid. Good for gaming or fast scrolling."
                cd_label.configure(text=msg)

            cooldown_var = ctk.DoubleVar(value=config.GESTURE_COOLDOWN)
            cd_slider = ctk.CTkSlider(
                tab_gen, 
                from_=0.1, 
                to=2.0, 
                variable=cooldown_var, 
                number_of_steps=19,
                command=update_cd_text
            )
            cd_slider.pack(pady=5)
            cd_label.pack()
            update_cd_text(config.GESTURE_COOLDOWN) # Init
            
            # Mouse Toggle
            mouse_var = ctk.BooleanVar(value=config.ENABLE_MOUSE)
            mouse_cb = ctk.CTkCheckBox(tab_gen, text="Enable Mouse Pointer (Index Finger)", variable=mouse_var)
            mouse_cb.pack(pady=20)
            
            # --- Sign Allowlist ---
            ctk.CTkLabel(tab_gen, text="Active Static Signs", font=("Roboto", 14, "bold")).pack(pady=(10,5))
            
            # Scrollable frame for signs if list grows, or just a frame
            sign_frame = ctk.CTkScrollableFrame(tab_gen, height=150)
            sign_frame.pack(fill="x", padx=10, pady=5)
            
            self.sign_vars = {}
            for sign_name in config.AVAILABLE_SIGNS:
                # Check if currently enabled
                is_on = sign_name in config.ENABLED_SIGNS
                var = ctk.BooleanVar(value=is_on)
                self.sign_vars[sign_name] = var
                cb = ctk.CTkCheckBox(sign_frame, text=sign_name, variable=var)
                cb.pack(anchor="w", pady=2)

            # --- Gestures Tab ---
            # Scrollable frame for many gestures
            scroll_frame = ctk.CTkScrollableFrame(tab_gest, label_text="Edit Shortcuts")
            scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            profile_data = config.PROFILES.get('DEFAULT', {})
            entry_vars = {}
            
            for gesture, keys in profile_data.items():
                row = ctk.CTkFrame(scroll_frame)
                row.pack(fill="x", pady=5)
                ctk.CTkLabel(row, text=gesture, width=150, anchor="w").pack(side="left", padx=5)
                
                # Join keys with '+' for display
                key_str = "+".join(keys)
                var = ctk.StringVar(value=key_str)
                entry_vars[gesture] = var
                ctk.CTkEntry(row, textvariable=var, width=150).pack(side="right", padx=5)

            # --- Save Logic ---
            def save_settings():
                # General
                config.MIN_DETECTION_CONFIDENCE = float(f"{confidence_var.get():.1f}")
                config.GESTURE_COOLDOWN = float(f"{cooldown_var.get():.1f}")
                config.ENABLE_MOUSE = mouse_var.get()
                
                # Save Enabled Signs
                new_enabled_signs = []
                for s_name, s_var in self.sign_vars.items():
                    if s_var.get():
                        new_enabled_signs.append(s_name)
                config.ENABLED_SIGNS = new_enabled_signs
                
                # Gestures (DEFAULT Profile)
                # We need to explicitly clear keys that are removed
                # First, get current keys to know what might need removing
                current_keys = list(config.PROFILES['DEFAULT'].keys())
                
                new_mapping = {}
                for gesture, var in entry_vars.items():
                    val = var.get().strip()
                    if val:
                        new_mapping[gesture] = val.split("+")
                    else:
                        # User cleared the entry -> Remove the mapping
                        if gesture in config.PROFILES['DEFAULT']:
                            del config.PROFILES['DEFAULT'][gesture]
                
                # Update with new/modified values
                config.PROFILES['DEFAULT'].update(new_mapping)
                
                config.save_config()
                if self.config_callback:
                    self.config_callback()
                self.settings_window.destroy()
                
            ctk.CTkButton(self.settings_window, text="Save & Close", command=save_settings, fg_color="#28a745", hover_color="#218838").pack(pady=10)
            
        else:
            self.settings_window.focus()

    def _on_drag_start(self, event):
        """Record the starting position for drag."""
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _on_drag_motion(self, event):
        """Move the window as the user drags."""
        if self.is_overlay:
            x = self.root.winfo_x() + (event.x - self._drag_start_x)
            y = self.root.winfo_y() + (event.y - self._drag_start_y)
            self.root.geometry(f"+{x}+{y}")

    def _close_preview(self):
        """Close the preview and stop the camera."""
        if hasattr(self, 'bus'):
            self.bus.publish("cmd:stop_camera")
        self.exit_overlay_mode()

    def enter_overlay_mode(self):
        if self.is_overlay: return
        self.is_overlay = True
        
        # Save current foreground window to restore focus
        prev_hwnd = ctypes.windll.user32.GetForegroundWindow()
        
        # Hide main window instead of reconfiguring it
        self.root.withdraw()
        
        # Create dedicated preview window - larger size
        screen_width = self.root.winfo_screenwidth()
        
        self.preview_window = tk.Toplevel(self.root)
        self.preview_window.title("Camera Preview")
        self.preview_window.attributes("-topmost", True)
        self.preview_window.geometry(f"480x320+{screen_width - 500}+20")
        self.preview_window.configure(bg="black")
        # Apply current opacity
        self.preview_window.attributes("-alpha", self.opacity_slider.get())
        self.preview_window.minsize(320, 180)  # Minimum size
        
        # Create canvas that fills the window
        self.preview_canvas = tk.Canvas(
            self.preview_window, 
            bg="black", 
            highlightthickness=0,
            borderwidth=0
        )
        self.preview_canvas.pack(fill="both", expand=True)
        
        # Handle window close via window manager (native X button)
        self.preview_window.protocol("WM_DELETE_WINDOW", self._close_preview)
        
        # Restore focus to previous window
        if prev_hwnd:
            self.root.after(200, lambda: ctypes.windll.user32.SetForegroundWindow(prev_hwnd))

        # Initialize Control Bar
        self._create_control_bar()
        self.preview_window.bind("<Enter>", self._show_control_bar)
        self.preview_window.bind("<Leave>", self._hide_control_bar_delayed)

    def _show_control_bar(self, event=None):
        if self.control_bar and self.preview_window:
            x = self.preview_window.winfo_x() + (self.preview_window.winfo_width() // 2) - 100
            y = self.preview_window.winfo_y() + self.preview_window.winfo_height() + 10
            self.control_bar.geometry(f"200x50+{x}+{y}")
            self.control_bar.deiconify()
            self.control_bar.lift()
            self.control_bar_visible = True

    def _hide_control_bar_delayed(self, event=None):
        # Small delay to allow moving to the bar itself
        self.root.after(500, self._hide_control_bar)

    def _hide_control_bar(self):
        # Should check if mouse is over the bar before hiding
        # Skipping complex check for MVP
        # self.control_bar.withdraw()
        pass

    def _on_drag_motion_preview(self, event):
        """Move the preview window as user drags."""
        if self.preview_window:
            x = self.preview_window.winfo_x() + (event.x - self._drag_start_x)
            y = self.preview_window.winfo_y() + (event.y - self._drag_start_y)
            self.preview_window.geometry(f"+{x}+{y}")

    def change_opacity(self, value):
        """Callback for opacity slider."""
        if self.is_overlay and hasattr(self, 'preview_window') and self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.attributes("-alpha", float(value))

    def exit_overlay_mode(self):
        if not self.is_overlay: return
        self.is_overlay = False
        
        # Destroy preview window
        if self.preview_window:
            self.preview_window.destroy()
            self.preview_window = None
            self.preview_canvas = None
            self.preview_photo = None
        
        # Remove close button reference
        self.close_button = None
        
        # Show main window again
        self.root.deiconify()
        
        if self.control_bar:
            self.control_bar.destroy()
            self.control_bar = None

    def _create_control_bar(self):
        """Creates the floating control bar."""
        if self.control_bar: return
        
        self.control_bar = ctk.CTkToplevel(self.root)
        self.control_bar.overrideredirect(True)
        self.control_bar.attributes("-topmost", True)
        self.control_bar.geometry("200x50")
        
        bar_frame = ctk.CTkFrame(self.control_bar, fg_color="#222222", corner_radius=10)
        bar_frame.pack(fill="both", expand=True)
        
        # Buttons
        ctk.CTkButton(bar_frame, text="⏹", width=40, height=30, fg_color="#dc3545", command=lambda: self.bus.publish("cmd:stop_camera")).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(bar_frame, text="🖼", width=40, height=30, command=self.exit_overlay_mode).pack(side="left", padx=5)
        # Settings trigger?
        ctk.CTkButton(bar_frame, text="⚙", width=40, height=30, command=self.open_settings).pack(side="left", padx=5)
        
        self.control_bar.withdraw()

    def _check_control_bar_hover(self, event):
        """Checks if mouse is near top edge of overlay to show control bar."""
        if not self.is_overlay or not self.preview_window: return
        
        # Simple proximity check logic would go here if we tracked mouse globally
        # But we only get events on the window. 
        # Easier: Just show it always if overlay is active? Or attach to bottom of preview window.
        
        # Let's attach it to bottom of preview for now
        pass

    def update_performance(self, fps, hand_detected, quality):
        """Update performance statistics for the dashboard."""
        self.current_fps = int(fps)
        self.is_hand_detected = hand_detected
        self.tracking_quality = quality
        
        # Update Dashboard FPS Card
        if hasattr(self, 'fps_label'):
            self.fps_label.configure(text=f"{self.current_fps}")

    def trigger_gesture_feedback(self, gesture_name):
        """Trigger visual feedback for a recognized gesture."""
        self.gesture_overlay_text = gesture_name
        self.gesture_overlay_start_time = time.time()

    def _draw_overlay_cv2(self, frame):
        """Draws performance dashboard and gesture feedback directly on the OpenCV frame."""
        h, w = frame.shape[:2]
        
        # 1. FPS Counter (Top-Left) - Bold white text with transparent background
        fps_text = f"FPS: {self.current_fps}"
        
        # Draw text with outline for visibility on any background
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        
        # Black outline for contrast
        cv2.putText(frame, fps_text, (20, 35), font, font_scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
        # White bold text
        cv2.putText(frame, fps_text, (20, 35), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
        
        # Hand Status Indicator (small dot next to FPS)
        status_color = (100, 255, 100) if self.is_hand_detected else (100, 100, 100)
        cv2.circle(frame, (110, 30), 6, status_color, -1)
        if self.is_hand_detected:
            cv2.circle(frame, (110, 30), 9, status_color, 1)
        
        # 2. visual Gesture Toast (Bottom-Center)
        if self.gesture_overlay_text:
            elapsed = time.time() - self.gesture_overlay_start_time
            if elapsed < self.gesture_display_duration:
                text = self.gesture_overlay_text
                
                # Dynamic opacity for fade out (last 200ms)
                alpha = 0.85
                if self.gesture_display_duration - elapsed < 0.2:
                    alpha = 0.85 * ((self.gesture_display_duration - elapsed) / 0.2)
                
                # Toast properties
                font = cv2.FONT_HERSHEY_DUPLEX
                font_scale = 0.8
                thickness = 1
                (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
                
                pad_x = 30
                pad_y = 15
                box_w = text_w + (pad_x * 2)
                box_h = text_h + (pad_y * 2)
                
                center_x = w // 2
                center_y = h - 80
                
                x1 = center_x - box_w // 2
                y1 = center_y - box_h // 2
                x2 = x1 + box_w
                y2 = y1 + box_h
                
                # Draw Translucent Background (Simulated Rounded Corners via multiple rects or just rect)
                # OpenCV drawing is basic, so a simple sleek rectangle looks best with alpha
                toast_overlay = frame.copy()
                
                # Main box
                bg_color = (30, 30, 30)
                # Accent bar on left
                accent_color = (0, 200, 100) # Greeny teal
                
                cv2.rectangle(toast_overlay, (x1, y1), (x2, y2), bg_color, -1)
                # Accent line
                cv2.rectangle(toast_overlay, (x1, y1), (x1 + 4, y2), accent_color, -1)
                
                # Text
                cv2.putText(toast_overlay, text, (center_x - text_w // 2 + 5, center_y + text_h // 2 - 2), 
                           font, font_scale, (255, 255, 255), thickness)
                           
                cv2.addWeighted(toast_overlay, alpha, frame, 1 - alpha, 0, frame)
                
            else:
                self.gesture_overlay_text = None

    def show_feedback(self, text, is_positive=True):
        """Displays a temporary overlay on the video feed."""
        color = "#28a745" if is_positive else "#ffc107"
        
        # Use new trigger method for in-frame feedback
        if ":" in text:
            # e.g. "DEFAULT: SWIPE_LEFT"
            gesture = text.split(":")[-1].strip()
            self.trigger_gesture_feedback(gesture)
        
        # Also keep existing label feedback for non-gesture messages if needed
        # Remove existing if any
        if self.feedback_label:
            self.feedback_label.destroy()
            
        self.feedback_label = ctk.CTkLabel(
            self.main_frame, 
            text=text, 
            fg_color="transparent", 
            text_color=color,
            font=("Roboto", 24, "bold")
        )
        self.feedback_label.place(relx=0.5, rely=0.1, anchor="center")
        
        # Auto hide
        self.root.after(1500, lambda: self.feedback_label.destroy() if self.feedback_label else None)

    def update_frame(self, frame):
        try:
            # Draw UI Overlay (FPS, Status, Gesture Badge) directly on the frame
            self._draw_overlay_cv2(frame)
            
            if self.is_overlay and self.preview_canvas and self.preview_window:
                # Check if preview window still exists
                try:
                    if not self.preview_window.winfo_exists():
                        return
                except:
                    return
                    
                # Overlay mode: render to dedicated preview window
                # Get current canvas size (dynamically resizable)
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()
                
                if canvas_width < 10 or canvas_height < 10:
                    return
                
                # Resize to fill canvas
                resized = cv2.resize(frame, (canvas_width, canvas_height))
                
                image = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
                self.preview_photo = ImageTk.PhotoImage(image=image)
                self.preview_canvas.delete("all")
                self.preview_canvas.create_image(canvas_width//2, canvas_height//2, image=self.preview_photo, anchor=tk.CENTER)
            elif not self.is_overlay:
                # Normal mode: render to main canvas
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                if canvas_width < 1: return
                
                # Maintain aspect ratio
                frame_height, frame_width = frame.shape[:2]
                scale = min(canvas_width/frame_width, canvas_height/frame_height)
                new_w, new_h = int(frame_width*scale), int(frame_height*scale)
                resized = cv2.resize(frame, (new_w, new_h))
                
                # Center
                x, y = canvas_width//2, canvas_height//2
                
                image = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
                self.photo = ImageTk.PhotoImage(image=image)
                self.canvas.delete("all")
                self.canvas.create_image(x, y, image=self.photo, anchor=tk.CENTER)
            
        except Exception as e:
            pass

    def clear_canvas(self):
        """Clears the canvas to black when camera is stopped."""
        self.canvas.delete("all")
        self.photo = None
        # Also clear preview if in overlay mode
        if self.preview_canvas:
            self.preview_canvas.delete("all")
            self.preview_photo = None

    def update_status(self, text):
        # text format examples: "Status: Starting...", "Profile: POWERPOINT", "DEFAULT: SWIPE_LEFT"
        
        if "Profile:" in text:
            # Update Profile Card
            profile_name = text.split(":")[-1].strip()
            self.profile_label.configure(text=profile_name)
            
            # Update Theme Colors based on profile
            from src import config
            theme = config.PROFILE_THEMES.get(profile_name, config.PROFILE_THEMES['UNKNOWN'])
            if theme:
                 # Update Sidebar Button or Border?
                 # For now just update icon if we support it
                 # self.profile_icon.configure(text=theme['icon']) # If we saved reference
                 
                 # Update Hints
                 if 'hints' in theme:
                     self.hints_label.configure(text=f"Hints: {theme['hints']}")
                 else:
                     self.hints_label.configure(text="")
                     
        elif "Status:" in text:
             # Update Status Label
             self.status_label.configure(text=text.replace("Status: ", ""))
             
             if "Running" in text:
                if self.pulse_job is None:
                    self._pulse_status()
             else:
                if self.pulse_job:
                    self.root.after_cancel(self.pulse_job)
                    self.pulse_job = None
                    self.status_label.configure(text_color="gray")

        elif ":" in text:
            # Gesture Event: "PROFILE: GESTURE"
            parts = text.split(":")
            gesture = parts[-1].strip()
            self.gesture_label.configure(text=gesture)
            
            # Trigger Visuals
            self.trigger_gesture_feedback(gesture)
            self.toast.show(gesture)

    def _pulse_status(self):
        # Pulse the status text distinct color
        if self.pulse_direction == -1:
            self.pulse_alpha -= 0.1
            if self.pulse_alpha <= 0.5: self.pulse_direction = 1
        else:
            self.pulse_alpha += 0.1
            if self.pulse_alpha >= 1.0: self.pulse_direction = -1
            
        # Color oscillation: Gray to Green?
        # Actually just toggle text color
        color = "#28a745" if self.pulse_alpha > 0.8 else "#555555"
        self.status_label.configure(text_color=color)
        
        self.pulse_job = self.root.after(150, self._pulse_status)



    def on_start_click(self):
        if self.is_camera_running:
            if not self.is_overlay:
                self.enter_overlay_mode()
        else:
            self.bus.publish("cmd:start_camera")

    def on_stop_click(self):
        self.bus.publish("cmd:stop_camera")

    def on_camera_change(self, choice):
        # Get index from current values
        values = self.camera_combo._values
        idx = self._get_cam_index(choice, values)
        self.bus.publish("cmd:change_camera", idx)
        
    def _on_close(self):
        self.bus.publish("app:quit")
        
    def on_camera_started(self, _=None):
        self.is_camera_running = True
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="normal")
        
    def on_camera_stopped(self, _=None):
        self.is_camera_running = False
        self.clear_canvas()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="Status: Stopped")

