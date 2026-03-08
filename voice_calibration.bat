@echo off
REM Quick Voice Personalization Script for Windows
REM This makes it easy to train the system on your voice

echo.
echo ============================================================
echo         VOICE EMOTION PERSONALIZATION TOOL
echo ============================================================
echo.
echo Choose an option:
echo.
echo 1. Quick Calibration (1 min - 1 sample per emotion)
echo 2. Full Calibration (10 min - 5-10 samples per emotion)
echo 3. Test Voice Accuracy (see what works/doesn't)
echo 4. Check System Status (view training data)
echo 5. Retrain with Existing Samples
echo 6. View Help Guide (read full documentation)
echo 7. Run Main Emotion Detection System
echo.
set /p choice="Your choice (1-7): "

if "%choice%"=="1" (
    echo.
    echo Starting quick calibration...
    echo.
    python voice_personalization.py quick
    pause
) else if "%choice%"=="2" (
    echo.
    echo Starting full calibration...
    echo.
    python voice_personalization.py full
    pause
) else if "%choice%"=="3" (
    echo.
    echo Testing voice detection accuracy...
    echo.
    python voice_calibration_manager.py test
    pause
) else if "%choice%"=="4" (
    echo.
    echo Checking system status...
    echo.
    python voice_calibration_manager.py status
    pause
) else if "%choice%"=="5" (
    echo.
    echo Retraining with existing samples...
    echo.
    python voice_personalization.py train
    pause
) else if "%choice%"=="6" (
    echo.
    echo Opening guide...
    start notepad VOICE_PERSONALIZATION_GUIDE.md
) else if "%choice%"=="7" (
    echo.
    echo Starting emotion detection system...
    echo.
    python final_emotion_detection.py
    pause
) else (
    echo Invalid choice!
    pause
)
