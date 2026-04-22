@echo off
REM ====================================
REM Multimedia Player - Installation Script (Windows)
REM ====================================

echo.
echo ====================================
echo Multimedia Player - Setup
echo ====================================
echo.

REM Step 1: Install Python dependencies
echo Installing Python packages...
echo.

pip install -r requirements.txt

if %errorlevel% neq 0 (
echo.
echo ERROR installing Python packages!
echo Make sure Python and pip are installed correctly.
echo.
pause
exit /b
)

echo.
echo Python packages installed successfully!
echo.

REM Step 2: Check if VLC is installed
echo Checking VLC installation...
echo.

if exist "C:\Program Files\VideoLAN\VLC\vlc.exe" (
echo VLC found in Program Files.
) else if exist "C:\Program Files (x86)\VideoLAN\VLC\vlc.exe" (
echo VLC found in Program Files (x86).
) else (
echo WARNING: VLC Media Player not found!
echo.
echo Please install VLC manually from:
echo https://www.videolan.org/vlc/
echo.
echo The player will NOT work without VLC.
echo.
)

echo.
echo ====================================
echo Setup completed!
echo ====================================
echo.
echo To run the player:
echo    python multimedia_player.py
echo.
echo Controls:
echo    F   - Fullscreen
echo    ESC - Exit fullscreen
echo.

pause
