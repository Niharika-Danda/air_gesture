# Chapter 5: Implementation (Part 5)
## User Interface Module

---

## 5.11 UI Manager Module (ui_manager.py)

The UI Manager creates and controls the graphical user interface using **CustomTkinter**, a modern-looking extension of Python's built-in Tkinter library. This module handles everything the user sees and interacts with.

### 5.11.1 Module Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    UI MANAGER MODULE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   MAIN WINDOW                         │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │                                                │  │  │
│  │  │             VIDEO CANVAS                       │  │  │
│  │  │          (800 x 600 pixels)                    │  │  │
│  │  │                                                │  │  │
│  │  │   [FPS: 30  ●]              [SWIPE_RIGHT]     │  │  │
│  │  │                                                │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │                                                       │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ Status: Ready  [Camera ▼] [Start] [Stop] [⚙️] │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Additional Components:                                     │
│  • ToastOverlay (popup notifications)                       │
│  • Settings Window (configuration panel)                    │
│  • Preview Window (overlay mode)                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.11.2 CustomTkinter Setup

```python
import customtkinter as ctk

# Set modern dark appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
```

**Simple Explanation:**
> CustomTkinter is like a "skin" for regular Tkinter that makes buttons,
> sliders, and windows look modern and professional. The "Dark" mode gives
> us a sleek dark theme that's easy on the eyes.

```
┌─────────────────────────────────────────────────────────────┐
│ REGULAR TKINTER vs CUSTOMTKINTER                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Regular Tkinter:              CustomTkinter:               │
│  ┌────────────┐                ╭────────────╮               │
│  │   Button   │                │   Button   │               │
│  └────────────┘                ╰────────────╯               │
│  (Square, dated look)          (Rounded, modern look)       │
│                                                             │
│  • Flat colors                 • Gradient effects           │
│  • Sharp corners               • Rounded corners            │
│  • No themes                   • Dark/Light themes          │
│  • Basic widgets               • Enhanced widgets           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5.12 ToastOverlay Class

Toast notifications are small popup messages that appear briefly to give feedback when a gesture is detected.

### 5.12.1 Class Definition

```python
class ToastOverlay:
    """
    A transparent, frameless overlay window for visual feedback.
    """
    def __init__(self, root):
        self.top = ctk.CTkToplevel(root)
        self.top.overrideredirect(True)   # No window frame
        self.top.attributes("-topmost", True)  # Always on top
        self.top.attributes("-alpha", 0.85)    # 85% opacity

        # Position centered at top of screen
        screen_w = self.top.winfo_screenwidth()
        width = 300
        height = 60
        x = (screen_w - width) // 2
        y = 100
        self.top.geometry(f"{width}x{height}+{x}+{y}")

        self.top.withdraw()  # Start hidden
```

### 5.12.2 Emoji Mapping

```python
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
```

```
┌─────────────────────────────────────────────────────────────┐
│ TOAST OVERLAY APPEARANCE                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                 ╭──────────────────────────╮                │
│                 │     ▶️ Next              │                │
│                 ╰──────────────────────────╯                │
│                                                             │
│  Properties:                                                │
│  • Frameless (no title bar or borders)                      │
│  • Semi-transparent (85% opacity)                           │
│  • Always on top of other windows                           │
│  • Auto-hides after 1.5 seconds                             │
│  • Centered at top of screen                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.12.3 Show and Hide Methods

```python
def show(self, gesture):
    """Display the toast with gesture information."""
    text = self.emoji_map.get(gesture, gesture)
    self.label.configure(text=text)

    self.top.deiconify()  # Make visible
    self.top.attributes("-topmost", True)

    # Cancel any pending hide operation
    if self.hide_job:
        self.top.after_cancel(self.hide_job)

    # Schedule auto-hide after 1.5 seconds
    self.hide_job = self.top.after(1500, self.hide)

def hide(self):
    """Hide the toast."""
    self.top.withdraw()
```

---

## 5.13 AppUIManager Class

The main UI manager class that creates and controls all visual elements.

### 5.13.1 Constructor

```python
class AppUIManager:
    """
    Manages the CustomTkinter-based graphical user interface.
    """
    def __init__(self, root, start_callback, stop_callback,
                 window_title, available_cameras,
                 change_camera_callback, config_callback):
        self.root = root
        self.root.title(window_title)
        self.root.protocol("WM_DELETE_WINDOW", stop_callback)
        self.config_callback = config_callback

        # Initialize Toast notification system
        self.toast = ToastOverlay(self.root)

        # Set window size
        self.root.geometry("900x750")
```

#### Callback Parameters Explained

| Parameter | Purpose |
|-----------|---------|
| `start_callback` | Function to call when "Start Camera" is clicked |
| `stop_callback` | Function to call when "Stop Camera" or window close |
| `change_camera_callback` | Function to call when camera selection changes |
| `config_callback` | Function to call after settings are saved |

### 5.13.2 Layout Structure

```python
# Main Layout Container
self.main_frame = ctk.CTkFrame(self.root, corner_radius=0)
self.main_frame.grid(row=0, column=0, sticky="nsew")
self.root.columnconfigure(0, weight=1)
self.root.rowconfigure(0, weight=1)

# Video Area
self.canvas_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
self.canvas_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")

# Video Canvas (using standard Tkinter for performance)
self.canvas = tk.Canvas(
    self.canvas_frame,
    bg="#1a1a1a",
    width=800,
    height=600,
    highlightthickness=0
)
self.canvas.pack(fill="both", expand=True)
```

```
┌─────────────────────────────────────────────────────────────┐
│ LAYOUT GRID SYSTEM                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  root (CTk window)                                          │
│  └── main_frame (row=0, col=0)                              │
│      ├── canvas_frame (row=0)                               │
│      │   └── canvas (video display)                         │
│      │                                                      │
│      └── controls_frame (row=1)                             │
│          ├── status_label (col=0)                           │
│          ├── camera_combo (col=2)                           │
│          ├── start_button (col=3)                           │
│          ├── stop_button (col=4)                            │
│          └── settings_button (col=5)                        │
│                                                             │
│  Grid weights ensure proper resizing behavior               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.13.3 Control Buttons

```python
# Controls Area
self.controls_frame = ctk.CTkFrame(self.main_frame, height=100)
self.controls_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

# Status Label
self.status_label = ctk.CTkLabel(
    self.controls_frame,
    text="Status: Ready",
    font=("Roboto Medium", 16)
)
self.status_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

# Camera Selection Dropdown
self.camera_var = ctk.StringVar(value=available_cameras[0])
self.camera_combo = ctk.CTkComboBox(
    self.controls_frame,
    values=available_cameras,
    command=lambda choice: change_camera_callback(
        self._get_cam_index(choice, available_cameras)
    ),
    width=200
)
self.camera_combo.grid(row=0, column=2, padx=10, pady=15)

# Start Button (Green)
self.start_button = ctk.CTkButton(
    self.controls_frame,
    text="Start Camera",
    command=start_callback,
    fg_color="#28a745",      # Green background
    hover_color="#218838"    # Darker green on hover
)
self.start_button.grid(row=0, column=3, padx=10, pady=15)

# Stop Button (Red)
self.stop_button = ctk.CTkButton(
    self.controls_frame,
    text="Stop Camera",
    command=stop_callback,
    fg_color="#dc3545",      # Red background
    hover_color="#c82333"    # Darker red on hover
)
self.stop_button.grid(row=0, column=4, padx=10, pady=15)

# Settings Button (Gear icon)
self.settings_button = ctk.CTkButton(
    self.controls_frame,
    text="⚙️",
    width=40,
    command=self.open_settings
)
self.settings_button.grid(row=0, column=5, padx=(0, 20), pady=15)
```

```
┌─────────────────────────────────────────────────────────────┐
│ CONTROL BAR LAYOUT                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                                                       │ │
│  │  Status: Ready   │   Camera 0 ▼   │ Start │ Stop │ ⚙️│ │
│  │                                                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│     Column 0         Column 2      Col 3  Col 4  Col 5     │
│                                                             │
│  Button Colors:                                             │
│  • Start: Green (#28a745) - Indicates "go" action          │
│  • Stop:  Red (#dc3545) - Indicates "stop" action          │
│  • Settings: Default blue theme                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5.14 Settings Window

The settings window allows users to customize detection parameters and gesture shortcuts.

### 5.14.1 Opening the Settings Window

```python
def open_settings(self):
    # Only create if not already open
    if self.settings_window is None or not self.settings_window.winfo_exists():
        from src import config  # Lazy import

        self.settings_window = ctk.CTkToplevel(self.root)
        self.settings_window.title("Settings")
        self.settings_window.geometry("500x700")
        self.settings_window.attributes("-topmost", True)

        # Tab View for organizing settings
        tabview = ctk.CTkTabview(self.settings_window)
        tabview.pack(fill="both", expand=True, padx=20, pady=20)

        tab_gen = tabview.add("General")
        tab_gest = tabview.add("Gestures (Default)")
```

### 5.14.2 Tab Structure

```
┌─────────────────────────────────────────────────────────────┐
│ SETTINGS WINDOW LAYOUT                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ╭─────────────────────────────────────────────────────╮   │
│  │  Settings                                      [X]  │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  ┌─────────────┬───────────────────┐               │   │
│  │  │   General   │ Gestures (Default)│               │   │
│  │  └─────────────┴───────────────────┘               │   │
│  │                                                     │   │
│  │  Detection Confidence (Sensitivity)                │   │
│  │  ──────────────●──────────────                     │   │
│  │  0.6: Balanced. Recommended for most users.        │   │
│  │                                                     │   │
│  │  Gesture Cooldown (Seconds)                        │   │
│  │  ────────●────────────────                         │   │
│  │  0.5s: Normal. Good for slides/presentations.      │   │
│  │                                                     │   │
│  │  [✓] Enable Mouse Pointer (Index Finger)           │   │
│  │                                                     │   │
│  │  Active Static Signs                               │   │
│  │  ┌─────────────────────────────────────┐          │   │
│  │  │ [ ] THUMBS_UP                       │          │   │
│  │  │ [ ] THUMBS_DOWN                     │          │   │
│  │  │ [ ] OPEN_PALM                       │          │   │
│  │  │ [ ] OK_SIGN                         │          │   │
│  │  │ ...                                 │          │   │
│  │  └─────────────────────────────────────┘          │   │
│  │                                                     │   │
│  │           ╭────────────────────╮                   │   │
│  │           │    Save & Close    │                   │   │
│  │           ╰────────────────────╯                   │   │
│  ╰─────────────────────────────────────────────────────╯   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.14.3 Detection Confidence Slider

```python
# Label
ctk.CTkLabel(
    tab_gen,
    text="Detection Confidence (Sensitivity)",
    font=("Roboto", 14, "bold")
).pack(pady=(20, 5))

# Dynamic description label
conf_label = ctk.CTkLabel(
    tab_gen, text="",
    font=("Roboto", 11),
    text_color="gray"
)

def update_conf_text(value):
    val = float(value)
    if val >= 0.8:
        msg = f"{val:.1f}: Strict. Needs clear hand visibility."
    elif val >= 0.6:
        msg = f"{val:.1f}: Balanced. Recommended for most users."
    else:
        msg = f"{val:.1f}: High Sensitivity. Works in bad light."
    conf_label.configure(text=msg)

# Slider
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
```

**Simple Explanation:**
> The slider lets users choose how "picky" the hand detection should be.
> Higher values mean MediaPipe needs to be very sure it sees a hand before
> reporting it. Lower values make it more sensitive but may cause false
> detections.

### 5.14.4 Sign Allowlist Management

```python
# Active Static Signs section
ctk.CTkLabel(
    tab_gen,
    text="Active Static Signs",
    font=("Roboto", 14, "bold")
).pack(pady=(10, 5))

# Scrollable frame for checkboxes
sign_frame = ctk.CTkScrollableFrame(tab_gen, height=150)
sign_frame.pack(fill="x", padx=10, pady=5)

self.sign_vars = {}
for sign_name in config.AVAILABLE_SIGNS:
    is_on = sign_name in config.ENABLED_SIGNS
    var = ctk.BooleanVar(value=is_on)
    self.sign_vars[sign_name] = var
    cb = ctk.CTkCheckBox(sign_frame, text=sign_name, variable=var)
    cb.pack(anchor="w", pady=2)
```

```
┌─────────────────────────────────────────────────────────────┐
│ SIGN ALLOWLIST CONCEPT                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  AVAILABLE_SIGNS (all possible):                            │
│  ├── THUMBS_UP                                              │
│  ├── THUMBS_DOWN                                            │
│  ├── OPEN_PALM                                              │
│  ├── OK_SIGN                                                │
│  ├── V_SIGN                                                 │
│  ├── INDEX_POINTING_UP                                      │
│  └── SPIDERMAN                                              │
│                                                             │
│  ENABLED_SIGNS (user's selection):                          │
│  ├── [✓] THUMBS_UP        <- Will trigger shortcuts         │
│  ├── [ ] THUMBS_DOWN      <- Ignored (unchecked)            │
│  ├── [✓] OPEN_PALM        <- Will trigger shortcuts         │
│  └── [ ] ...              <- Other signs...                 │
│                                                             │
│  Only checked signs will activate keyboard shortcuts!       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.14.5 Gesture Shortcuts Tab

```python
# Scrollable frame for gesture shortcuts
scroll_frame = ctk.CTkScrollableFrame(
    tab_gest,
    label_text="Edit Shortcuts"
)
scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

profile_data = config.PROFILES.get('DEFAULT', {})
entry_vars = {}

for gesture, keys in profile_data.items():
    row = ctk.CTkFrame(scroll_frame)
    row.pack(fill="x", pady=5)

    # Gesture name label
    ctk.CTkLabel(
        row,
        text=gesture,
        width=150,
        anchor="w"
    ).pack(side="left", padx=5)

    # Shortcut entry field
    key_str = "+".join(keys)  # e.g., ["ctrl", "c"] -> "ctrl+c"
    var = ctk.StringVar(value=key_str)
    entry_vars[gesture] = var
    ctk.CTkEntry(row, textvariable=var, width=150).pack(side="right", padx=5)
```

```
┌─────────────────────────────────────────────────────────────┐
│ GESTURES TAB LAYOUT                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Edit Shortcuts                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │  SWIPE_LEFT         │ left                    │    │   │
│  │  SWIPE_RIGHT        │ right                   │    │   │
│  │  THUMBS_UP          │ ctrl+shift+tab          │    │   │
│  │  THUMBS_DOWN        │ ctrl+tab                │    │   │
│  │  OPEN_PALM          │ space                   │    │   │
│  │  OK_SIGN            │ enter                   │    │   │
│  │  ...                                               │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Format: Keys separated by "+"                              │
│  Examples: "left", "ctrl+c", "alt+tab", "shift+f5"         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.14.6 Save Settings Function

```python
def save_settings():
    # Save General settings
    config.MIN_DETECTION_CONFIDENCE = float(f"{confidence_var.get():.1f}")
    config.GESTURE_COOLDOWN = float(f"{cooldown_var.get():.1f}")
    config.ENABLE_MOUSE = mouse_var.get()

    # Save Enabled Signs
    new_enabled_signs = []
    for s_name, s_var in self.sign_vars.items():
        if s_var.get():
            new_enabled_signs.append(s_name)
    config.ENABLED_SIGNS = new_enabled_signs

    # Save Gesture Shortcuts
    new_mapping = {}
    for gesture, var in entry_vars.items():
        val = var.get().strip()
        if val:
            new_mapping[gesture] = val.split("+")
        else:
            # Empty entry = remove the mapping
            if gesture in config.PROFILES['DEFAULT']:
                del config.PROFILES['DEFAULT'][gesture]

    config.PROFILES['DEFAULT'].update(new_mapping)

    # Persist to disk
    config.save_config()

    # Notify main app of config change
    if self.config_callback:
        self.config_callback()

    self.settings_window.destroy()
```

---

## 5.15 Overlay Mode

Overlay mode shows a small floating preview window while the main application is hidden, allowing gesture control while using other applications.

### 5.15.1 Entering Overlay Mode

```python
def enter_overlay_mode(self):
    if self.is_overlay:
        return
    self.is_overlay = True

    # Save current foreground window to restore focus
    prev_hwnd = ctypes.windll.user32.GetForegroundWindow()

    # Hide main window
    self.root.withdraw()

    # Create floating preview window
    screen_width = self.root.winfo_screenwidth()

    self.preview_window = tk.Toplevel(self.root)
    self.preview_window.title("Camera Preview")
    self.preview_window.attributes("-topmost", True)
    self.preview_window.geometry(f"480x320+{screen_width - 500}+20")
    self.preview_window.configure(bg="black")
    self.preview_window.minsize(320, 180)

    # Create canvas for video
    self.preview_canvas = tk.Canvas(
        self.preview_window,
        bg="black",
        highlightthickness=0
    )
    self.preview_canvas.pack(fill="both", expand=True)

    # Handle window close
    self.preview_window.protocol("WM_DELETE_WINDOW", self._close_preview)

    # Restore focus to previous application
    if prev_hwnd:
        self.root.after(200, lambda: ctypes.windll.user32.SetForegroundWindow(prev_hwnd))
```

```
┌─────────────────────────────────────────────────────────────┐
│ OVERLAY MODE VISUALIZATION                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  NORMAL MODE:                  OVERLAY MODE:                │
│                                                             │
│  ┌──────────────────┐          Other Application Window     │
│  │  Main Window     │          ┌──────────────────────────┐│
│  │  ┌────────────┐  │          │                          ││
│  │  │   Video    │  │          │   PowerPoint Slide       ││
│  │  │   Canvas   │  │          │                          ││
│  │  └────────────┘  │          │                     ┌────┤│
│  │  [Start][Stop]   │          │                     │Prev││
│  └──────────────────┘          │                     │iew ││
│                                │                     └────┤│
│  Full-size app visible         └──────────────────────────┘│
│                                                             │
│                                Small floating preview       │
│                                Main window hidden           │
│                                Focus stays on other app     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.15.2 Exiting Overlay Mode

```python
def exit_overlay_mode(self):
    if not self.is_overlay:
        return
    self.is_overlay = False

    # Destroy preview window
    if self.preview_window:
        self.preview_window.destroy()
        self.preview_window = None
        self.preview_canvas = None
        self.preview_photo = None

    # Show main window again
    self.root.deiconify()
```

---

## 5.16 Frame Display System

The frame display system handles rendering video frames from OpenCV to the Tkinter canvas.

### 5.16.1 The update_frame() Method

```python
def update_frame(self, frame):
    try:
        # Draw UI overlays on the frame
        self._draw_overlay_cv2(frame)

        if self.is_overlay and self.preview_canvas:
            # Overlay mode: render to preview window
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()

            if canvas_width < 10 or canvas_height < 10:
                return

            # Resize to fit canvas
            resized = cv2.resize(frame, (canvas_width, canvas_height))

            # Convert BGR to RGB for Tkinter
            image = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
            self.preview_photo = ImageTk.PhotoImage(image=image)

            # Display on canvas
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(
                canvas_width//2, canvas_height//2,
                image=self.preview_photo,
                anchor=tk.CENTER
            )

        elif not self.is_overlay:
            # Normal mode: render to main canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Maintain aspect ratio
            frame_height, frame_width = frame.shape[:2]
            scale = min(canvas_width/frame_width, canvas_height/frame_height)
            new_w, new_h = int(frame_width*scale), int(frame_height*scale)
            resized = cv2.resize(frame, (new_w, new_h))

            # Convert and display
            image = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
            self.photo = ImageTk.PhotoImage(image=image)
            self.canvas.delete("all")
            self.canvas.create_image(
                canvas_width//2, canvas_height//2,
                image=self.photo,
                anchor=tk.CENTER
            )

    except Exception as e:
        pass  # Silently handle display errors
```

```
┌─────────────────────────────────────────────────────────────┐
│ FRAME DISPLAY PIPELINE                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Receive OpenCV frame (BGR format, numpy array)          │
│              │                                              │
│              ▼                                              │
│  2. Draw overlays (FPS, gesture feedback)                   │
│              │                                              │
│              ▼                                              │
│  3. Resize to fit canvas (maintaining aspect ratio)         │
│              │                                              │
│              ▼                                              │
│  4. Convert BGR → RGB (OpenCV uses BGR, Tkinter uses RGB)   │
│              │                                              │
│              ▼                                              │
│  5. Create PIL Image from numpy array                       │
│              │                                              │
│              ▼                                              │
│  6. Convert to PhotoImage (Tkinter-compatible format)       │
│              │                                              │
│              ▼                                              │
│  7. Display on Canvas at center position                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Important Note about PhotoImage:**
> Tkinter's PhotoImage must be stored as an instance variable (self.photo).
> If stored as a local variable, Python's garbage collector will delete it,
> causing the image to disappear from the canvas!

### 5.16.2 Aspect Ratio Calculation

```python
# Calculate scale to fit frame in canvas while maintaining aspect ratio
scale = min(canvas_width/frame_width, canvas_height/frame_height)
new_w, new_h = int(frame_width * scale), int(frame_height * scale)
```

```
┌─────────────────────────────────────────────────────────────┐
│ ASPECT RATIO PRESERVATION                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Original Frame: 640x480 (4:3 ratio)                        │
│  Canvas Size: 800x600                                       │
│                                                             │
│  Scale X = 800/640 = 1.25                                   │
│  Scale Y = 600/480 = 1.25                                   │
│  Scale = min(1.25, 1.25) = 1.25                             │
│                                                             │
│  New size = 640*1.25 x 480*1.25 = 800x600                   │
│                                                             │
│  ┌─────────────────────────────────────┐                   │
│  │                                     │                   │
│  │      Frame fills canvas exactly     │                   │
│  │      (same aspect ratio)            │                   │
│  │                                     │                   │
│  └─────────────────────────────────────┘                   │
│                                                             │
│  If frame was 640x360 (16:9):                               │
│  Scale X = 800/640 = 1.25                                   │
│  Scale Y = 600/360 = 1.67                                   │
│  Scale = min(1.25, 1.67) = 1.25                             │
│                                                             │
│  New size = 800x450 (letterboxed)                           │
│  ┌─────────────────────────────────────┐                   │
│  │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ <- Black bar      │
│  │      Frame content (800x450)       │                   │
│  │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ <- Black bar      │
│  └─────────────────────────────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5.17 Performance Dashboard Overlay

The `_draw_overlay_cv2()` method draws real-time performance information directly on the video frame.

### 5.17.1 FPS and Status Display

```python
def _draw_overlay_cv2(self, frame):
    """Draws performance dashboard and gesture feedback on the frame."""
    h, w = frame.shape[:2]

    # 1. Performance Dashboard (Top-Left)
    overlay = frame.copy()
    cv2.rectangle(overlay, (15, 15), (145, 50), (40, 40, 40), -1)

    # FPS Counter
    fps_text = f"FPS: {self.current_fps}"
    cv2.putText(overlay, fps_text, (25, 40),
                cv2.FONT_HERSHEY_DUPLEX, 0.5, (220, 220, 220), 1)

    # Hand Status Indicator (Green dot when hand detected)
    status_color = (100, 255, 100) if self.is_hand_detected else (80, 80, 80)
    cv2.circle(overlay, (125, 33), 5, status_color, -1)
    if self.is_hand_detected:  # Glow effect
        cv2.circle(overlay, (125, 33), 8, status_color, 1)

    # Apply semi-transparency
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
```

```
┌─────────────────────────────────────────────────────────────┐
│ PERFORMANCE DASHBOARD APPEARANCE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │                                                    │    │
│  │  ╭───────────────╮                                │    │
│  │  │ FPS: 30    ● │  <- Green dot = hand detected   │    │
│  │  ╰───────────────╯                                │    │
│  │                                                    │    │
│  │              Video Content...                      │    │
│  │                                                    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  The dashboard uses semi-transparency (alpha blending)      │
│  so video content is slightly visible behind it.            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.17.2 Gesture Toast Overlay

```python
# 2. Gesture Toast (Bottom-Center)
if self.gesture_overlay_text:
    elapsed = time.time() - self.gesture_overlay_start_time
    if elapsed < self.gesture_display_duration:
        text = self.gesture_overlay_text

        # Fade out effect in last 200ms
        alpha = 0.85
        if self.gesture_display_duration - elapsed < 0.2:
            alpha = 0.85 * ((self.gesture_display_duration - elapsed) / 0.2)

        # Calculate text dimensions
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 0.8
        (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, 1)

        # Position at bottom center
        center_x = w // 2
        center_y = h - 80

        # Draw background box with accent bar
        toast_overlay = frame.copy()
        x1 = center_x - (text_w + 60) // 2
        y1 = center_y - 20
        x2 = x1 + text_w + 60
        y2 = y1 + 40

        cv2.rectangle(toast_overlay, (x1, y1), (x2, y2), (30, 30, 30), -1)
        cv2.rectangle(toast_overlay, (x1, y1), (x1 + 4, y2), (0, 200, 100), -1)

        # Draw text
        cv2.putText(toast_overlay, text,
                    (center_x - text_w // 2 + 5, center_y + text_h // 2 - 2),
                    font, font_scale, (255, 255, 255), 1)

        cv2.addWeighted(toast_overlay, alpha, frame, 1 - alpha, 0, frame)
    else:
        self.gesture_overlay_text = None
```

```
┌─────────────────────────────────────────────────────────────┐
│ GESTURE TOAST APPEARANCE                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │                                                    │    │
│  │              Video Content...                      │    │
│  │                                                    │    │
│  │                                                    │    │
│  │           ┌──────────────────────┐                │    │
│  │           │▌    SWIPE_RIGHT     │                │    │
│  │           └──────────────────────┘                │    │
│  │                    ↑                              │    │
│  │             Green accent bar                       │    │
│  │                                                    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  Toast appears for 1 second, then fades out over 0.2s       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5.18 Visual Feedback System

### 5.18.1 Triggering Feedback

```python
def trigger_gesture_feedback(self, gesture_name):
    """Trigger visual feedback for a recognized gesture."""
    self.gesture_overlay_text = gesture_name
    self.gesture_overlay_start_time = time.time()

def update_performance(self, fps, hand_detected, quality):
    """Update performance statistics for the dashboard."""
    self.current_fps = int(fps)
    self.is_hand_detected = hand_detected
    self.tracking_quality = quality
```

### 5.18.2 Status Updates

```python
def update_status(self, text):
    """Update the status label and trigger visual feedback."""
    self.status_label.configure(text=text)

    # If it's a gesture recognition event, show feedback
    if ":" in text and "Profile" not in text:
        # e.g., "DEFAULT: THUMBS_UP" -> extract "THUMBS_UP"
        gesture = text.split(":")[-1].strip()
        self.trigger_gesture_feedback(gesture)
```

---

## 5.19 Summary: UI Components

```
┌─────────────────────────────────────────────────────────────┐
│ UI MANAGER COMPONENT HIERARCHY                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  AppUIManager                                               │
│  │                                                          │
│  ├── root (CTk main window)                                 │
│  │   ├── main_frame                                         │
│  │   │   ├── canvas_frame                                   │
│  │   │   │   └── canvas (video display)                     │
│  │   │   │                                                  │
│  │   │   └── controls_frame                                 │
│  │   │       ├── status_label                               │
│  │   │       ├── camera_combo                               │
│  │   │       ├── start_button                               │
│  │   │       ├── stop_button                                │
│  │   │       └── settings_button                            │
│  │   │                                                      │
│  │   └── settings_window (CTkToplevel)                      │
│  │       ├── tabview                                        │
│  │       │   ├── "General" tab                              │
│  │       │   │   ├── confidence slider                      │
│  │       │   │   ├── cooldown slider                        │
│  │       │   │   ├── mouse checkbox                         │
│  │       │   │   └── sign checkboxes                        │
│  │       │   │                                              │
│  │       │   └── "Gestures" tab                             │
│  │       │       └── shortcut entries                       │
│  │       │                                                  │
│  │       └── save_button                                    │
│  │                                                          │
│  ├── toast (ToastOverlay)                                   │
│  │   └── top (CTkToplevel - popup window)                   │
│  │       └── label (emoji + text)                           │
│  │                                                          │
│  └── preview_window (overlay mode)                          │
│      └── preview_canvas                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5.20 Key UI Patterns Used

| Pattern | Implementation | Purpose |
|---------|----------------|---------|
| **Callback Pattern** | Button commands passed as functions | Decouple UI from logic |
| **Observer Pattern** | config_callback on save | Notify app of changes |
| **Double Buffering** | Frame copy before drawing | Smooth rendering |
| **Alpha Blending** | cv2.addWeighted() | Semi-transparent overlays |
| **Lazy Import** | `from src import config` in method | Avoid circular imports |
| **Singleton Window** | Check winfo_exists() | Prevent multiple settings windows |

---

*End of Chapter 5, Part 5*

**Next: Part 6 - Supporting Modules (audio_feedback.py, gesture_recorder.py, calibration.py)**
