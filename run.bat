@echo off
setlocal
echo ===========================================
echo    Air Gesture Shortcut Controller Setup 
echo ===========================================

cd /d "%~dp0"

REM Detection: Check specifically for Python 3.11 first (Best for MediaPipe)
set PYTHON_CMD=
echo Looking for Python 3.11...
py -3.11 --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py -3.11
    echo Found Python 3.11! Perfect.
) ELSE (
    echo Could not find specific Python 3.11 installation.
    echo Checking for any compatible Python...
    
    py --version >nul 2>&1
    IF %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=py
        echo Found default Python via 'py'. Fingers crossed!
    ) ELSE (
        python --version >nul 2>&1
        IF %ERRORLEVEL% EQU 0 (
            set PYTHON_CMD=python
            echo Found 'python'. Fingers crossed!
        )
    )
)

REM If neither is found
IF "%PYTHON_CMD%"=="" (
    echo.
    echo Python is not found!
    echo.
    echo Please install Python 3.11 from https://www.python.org/downloads/release/python-3119/
    echo.
    pause
    exit /b
)

REM Show version
echo Using command: %PYTHON_CMD%
%PYTHON_CMD% --version

IF NOT EXIST "venv" (
    echo First time setup! Creating virtual environment...
    REM Use the detected command to create the venv
    %PYTHON_CMD% -m venv venv
    IF %ERRORLEVEL% NEQ 0 (
        echo.
        echo Failed to create virtual environment.
        pause
        exit /b
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo Failed to activate virtual environment.
    pause
    exit /b
)

REM SELF-HEALING: Check if dependencies are actually installed
echo Checking if tools are ready...
python -c "import cv2; import mediapipe; import pyautogui" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Tools are missing! Installing them now...
    echo (Internet required!)
    pip install -r requirements.txt
    
    IF %ERRORLEVEL% NEQ 0 (
        echo.
        echo Uh oh! Installation failed.
        echo Please check your internet connection.
        echo If you are offline, you need internet for this one-time fix.
        pause
        exit /b
    )
    
    echo Tools installed successfully!
) ELSE (
    echo Tools are ready to go!
)

echo Starting the application...
REM Once activated, we always use 'python' to refer to the venv's python
python src\main.py

echo.
IF %ERRORLEVEL% NEQ 0 (
    echo The application crashed or closed with an error.
) ELSE (
    echo Thanks for playing!
)
echo ===========================================
pause
endlocal
