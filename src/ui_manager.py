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

class AppUIManager:
    """
    Manages the CustomTkinter-based graphical user interface.
    """
    def __init__(self, root, start_callback, stop_callback, window_title, available_cameras, change_camera_callback, config_callback):
        self.root = root
        self.root.title(window_title)
        self.root.protocol("WM_DELETE_WINDOW", stop_callback)
        self.config_callback = config_callback
        
        # Initialize Toast
        self.toast = ToastOverlay(self.root)
        
        # Determine geometry
        self.root.geometry("900x750")

        # Main Layout
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Video Area (Canvas needs to be standard tk for performance/compatibility)
        self.canvas_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.canvas_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        
        # Canvas
        self.canvas = tk.Canvas(self.canvas_frame, bg="#1a1a1a", width=800, height=600, highlightthickness=0, borderwidth=0)
        self.canvas.pack(fill="both", expand=True)

        # Visual Feedback Label (Overlay on top of canvas)
        self.feedback_label = None # Created dynamically

        # Controls Area
        self.controls_frame = ctk.CTkFrame(self.main_frame, height=100)
        self.controls_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        self.controls_frame.columnconfigure(1, weight=1) # Spacer

        # Status
        self.status_label = ctk.CTkLabel(self.controls_frame, text="Status: Idle - Press Start", font=("Roboto Medium", 16))
        self.status_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Camera Selection
        self.camera_var = ctk.StringVar(value=available_cameras[0] if available_cameras else "No Camera")
        self.camera_combo = ctk.CTkComboBox(
            self.controls_frame, 
            values=available_cameras if available_cameras else ["No Camera"],
            command=lambda choice: change_camera_callback(self._get_cam_index(choice, available_cameras)),
            width=200
        )
        self.camera_combo.grid(row=0, column=2, padx=10, pady=15)
        
        # Buttons (disabled initially until camera starts)
        self.start_button = ctk.CTkButton(self.controls_frame, text="Start", command=start_callback, fg_color="#28a745", hover_color="#218838", state="disabled")
        self.start_button.grid(row=0, column=3, padx=10, pady=15)

        self.stop_button = ctk.CTkButton(self.controls_frame, text="Stop", command=stop_callback, fg_color="#dc3545", hover_color="#c82333", state="disabled")
        self.stop_button.grid(row=0, column=4, padx=10, pady=15)

        # Settings Button
        self.settings_button = ctk.CTkButton(self.controls_frame, text="⚙️", width=40, command=self.open_settings)
        self.settings_button.grid(row=0, column=5, padx=(0, 20), pady=15)

        self.photo = None
        self.is_overlay = False
        self.pre_overlay_geometry = "900x750"
        self.settings_window = None
        
        # Preview overlay window (separate Toplevel for clean full-size preview)
        self.preview_window = None
        self.preview_canvas = None
        self.preview_photo = None
        
        # Drag state for overlay window
        self._drag_start_x = 0
        self._drag_start_y = 0
        
        # Close button for overlay
        self.close_button = None
        self.stop_callback = stop_callback  # Store for close button
        
        # Visual Feedback State
        self.gesture_overlay_text = None
        self.gesture_overlay_start_time = 0
        self.gesture_display_duration = 1.0 # Seconds
        
        # Performance Stats
        self.current_fps = 0
        self.tracking_quality = 0.0 # 0.0 to 1.0
        self.is_hand_detected = False

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
        if self.stop_callback:
            self.stop_callback()
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

    def _on_drag_motion_preview(self, event):
        """Move the preview window as user drags."""
        if self.preview_window:
            x = self.preview_window.winfo_x() + (event.x - self._drag_start_x)
            y = self.preview_window.winfo_y() + (event.y - self._drag_start_y)
            self.preview_window.geometry(f"+{x}+{y}")

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

    def update_performance(self, fps, hand_detected, quality):
        """Update performance statistics for the dashboard."""
        self.current_fps = int(fps)
        self.is_hand_detected = hand_detected
        self.tracking_quality = quality

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
        self.status_label.configure(text=text)
        # Also trigger feedback if it's a recognition event (heuristic)
        if ":" in text and "Profile" not in text: 
            # e.g., "DEFAULT: THUMBS_UP" -> Show "THUMBS_UP"
            gesture = text.split(":")[-1].strip()
            self.trigger_gesture_feedback(gesture) # Trigger Badge Overlay
            self.show_feedback(gesture) # Show standard label overlay too? explicit call is better.

