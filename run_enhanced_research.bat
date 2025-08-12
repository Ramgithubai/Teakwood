@echo off
title Enhanced JustDial WhatsApp Research

echo.
echo ===============================================================
echo   🎭 ENHANCED JUSTDIAL WHATSAPP RESEARCH
echo   Maximum Anti-Detection + Human-Like Clicking
echo ===============================================================
echo.

echo 🚀 Starting Enhanced Research System...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python first.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Run the enhanced research system
echo 🎯 Launching enhanced research runner...
echo.
python run_enhanced_research.py

echo.
echo 📋 Research session completed.
pause
