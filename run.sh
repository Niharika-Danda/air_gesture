#!/bin/bash

echo "==========================================="
echo "🪄 Air Gesture Shortcut Controller Setup 🪄"
echo "==========================================="

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "📦 First time setup! Creating virtual environment..."
    python3 -m venv venv
fi

echo "🛡️ Activating virtual environment..."
source venv/bin/activate

# 🩺 SELF-HEALING: Check if dependencies are actually installed
echo "🩺 Checking if tools are ready..."
python -c "import cv2; import mediapipe; import pyautogui" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️ Tools are missing! Installing them now..."
    echo "(Internet required!)"
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ Uh oh! Installation failed."
        echo "Please check your internet connection."
        exit 1
    fi
    echo "✅ Tools installed successfully!"
else
    echo "✅ Tools are ready to go!"
fi

echo "🚀 Starting the application..."
python src/main.py
