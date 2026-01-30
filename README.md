# 🎈 Air Gesture Shortcut Controller - Fun Edition! 🎈

Hello! This is a magic program that lets you use your hands to control your computer, just like a wizard! 🧙‍♂️✨

It sees your hand through the camera and presses buttons on the keyboard for you. Great for showing off your slide shows without touching anything!

## 🧩 What Is This?

It's a computer program that looks at your hand.
- If you give a **Thumbs Up** 👍, it presses the **Right Arrow** key (Next Slide!).
- If you give a **Thumbs Down** 👎, it presses the **Left Arrow** key (Go Back!).
- It has lots of other magic signs too!

---

## 🛠️ What Do We Need?

Before we play, we need to get our toys ready. We need:
1.  **A Computer** (Windows, Mac, or Linux).
2.  **A Webcam** (The eye that sees you).
3.  **Python** (The language the computer speaks).
4.  **Internet** (To get the special tools).

---


## 🚀 Let's Play! (The Easy Way)

We made a magic button for you!


### If you use Windows:
1.  Double-click the file named **`run.bat`**.
2.  That's it! It will set up everything and start the program.
    *   *Note: You only need internet the VERY FIRST time you run it. After that, you can play offline!* ✈️

### If you use Mac or Linux:
1.  Open your terminal.
2.  Type `./run.sh` and press Enter.



## 🌟 New Magic Powers!

### 1. Modern Dashboard 📊
- **Sidebar Navigation**: Sleek controls on the left for starting/stopping the camera and settings.
- **Live Stats**: Real-time cards showing **FPS**, your current **Profile**, and the **Last Gesture** detected.
- **Smart Hints**: The dashboard now tells you *exactly* what gestures work in your current app!

### 2. High-Tech Visuals ✨
- **Neon Glow**: Your hand landmarks glow with a cool cyberpunk effect.
- **Particle Sparks**: Move your finger fast to emit cyan-colored sparks!
- **Pointer Trails**: A smooth fading trail follows your movements.

### 3. Presentation & Overlay 🎥
- **Auto-Overlay**: When you go full-screen, the app shrinks to a tiny, translucent window in the corner.
- **Floating Controls**: Hover your mouse over the tiny window to see hidden controls.
- **Toast Notifications**: Smooth popups show you what's happening without blocking your view.

---

## 🤓 The "I Want To Do It Myself" Way (Manual Setup)

If the magic button doesn't work, you can do it step-by-step:

### Step 1: Get the Code 📦
Open your computer's "Command Prompt" or "Terminal" and type:
```bash
git clone https://github.com/your-username/air-gesture-controller.git
cd air_gesture_controller
```

### Step 2: Make a Safe Space (Virtual Environment) 🛡️

- **Windows:**
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

- **Mac/Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Step 3: Get the Tools 🔧
```bash
pip install -r requirements.txt
```

### Step 4: Run It! 🎮
```bash
python src/main.py
```


---

## ✋ How to Use Your Hands

Make these shapes (or moves!) with your hand to do magic:

| Gesture | Action |
| :--- | :--- |
| **👋 Swipe Hand Right** | Next Slide (Right Arrow) |
| **👋 Swipe Hand Left** | Previous Slide (Left Arrow) |
| **👍 Thumbs Up** | Next Slide (Right Arrow) |
| **👎 Thumbs Down** | Previous Slide (Left Arrow) |
| **✋ Open Palm** | **Start** the Show (F5) |
| **✌️ Peace Sign** | Make Screen **Black** (B) |
| **☝️ Point Up** | Make Screen **White** (W) |
| **👌 OK Sign**<br>*(Thumb + Index touch)* | Go to **First** Slide (Home) |
| **🤟 Spiderman**<br>*(Thumb + Index + Pinky)* | Go to **Last** Slide (End) |

*Note: Swipes work best when you move your hand quickly across the camera!*

---

## � Magic Profiles (Context Awareness)

This program is smart! It knows what you are doing and changes its magic spells:

1.  **PowerPoint / Slides Mode** 📊
    *   This is the default! Use the gestures above to control your presentation.
    *   Also has **Presentation Mode**: If you go full screen, the camera window shrinks automatically!

2.  **Chrome / Web Mode** �
    *   If you open **Google Chrome**, the gestures change!
    *   **Thumbs Up** 👍 -> Switch to **Next Tab**
    *   **Thumbs Down** 👎 -> Switch to **Previous Tab**
    *   **Swipe Right** -> Go **Forward** on the web page
    *   **Swipe Left** -> Go **Back** on the web page
    *   **OK Sign** 👌 -> Open a **New Tab**

---

## ⚡ Battery Saving Power
If you step away from the camera for more than 5 seconds, the program goes to sleep 💤 to save your battery. As soon as you wave your hand, it wakes up instantly!

---

## 🚑 Uh Oh! Fixing Booboos (Troubleshooting)

### 1. "I typed `python` but nothing happened or it says 'command not found'!"
- **Fix:** You might need to install Python. Go to `python.org` and download it. When you install it, make sure to check the box that says **"Add Python to PATH"**.

### 2. "It says `ModuleNotFoundError: No module named ...`"
- **Fix:** You forgot to install the tools! or you are not in the safe space.
- Make sure you see `(venv)` in your terminal.
- Run `pip install -r requirements.txt` again.

### 3. "The camera window didn't open!" / "It says 'Error: Could not open camera'"
- **Fix:** Is another program using your camera? (Like Zoom or Teams?) Close them!
- Is your camera plugged in? Unplug it and plug it back in.

### 4. "It's pressing buttons too fast!"
- **Fix:** The program has a "cooldown" (a nap time) so it doesn't press buttons too fast. It waits 0.4 seconds.

### 5. "It doesn't see my hand!"
- **Fix:** Make sure there is enough light in the room! 💡 The computer needs to see you clearly.

### 6. "The swipes aren't working!"
- **Fix:** Try moving your hand faster! The program looks for quick movements. Watch the black console window—it will tell you if it sees a swipe (`DEBUG: Swipe Delta...`).

### 7. "I want to change the buttons!"
- **Fix:** Ask a grown-up (or a programmer) to open `src/config.py`. They can change what keys get pressed in the `PROFILES` list.

Have fun being a wizard! 🧙‍♂️✨
