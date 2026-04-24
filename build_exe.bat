@echo off
echo ========================================================
echo Building YouTube Downloader Executable...
echo ========================================================

:: Check if ffmpeg folder exists
if not exist "ffmpeg\ffmpeg.exe" (
    echo [ERROR] FFmpeg not found! 
    echo Please create an 'ffmpeg' folder and place 'ffmpeg.exe' and 'ffprobe.exe' inside it.
    pause
    exit /b
)

:: Check if PyInstaller is installed
python -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing PyInstaller...
    pip install pyinstaller
)

:: Run PyInstaller
:: --noconsole prevents the command prompt from appearing
:: --onedir creates a folder containing the exe and dependencies (better for installers and fast launch)
:: --add-data bundles the local ffmpeg folder into the application
pyinstaller --name "YouTubeDownloader" --windowed --noconfirm --add-data "ffmpeg;ffmpeg" youtube_downloader.py

echo.
echo ========================================================
echo Build Complete!
echo The application is now located in: dist\YouTubeDownloader
echo ========================================================
pause
