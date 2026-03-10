@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo TubeGrab Pro baslatiliyor...
echo.

REM Python yollarini dene
where python >nul 2>&1 && (
    python tubegrab_pro.py
    goto :end
)

where py >nul 2>&1 && (
    py tubegrab_pro.py
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" tubegrab_pro.py
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" tubegrab_pro.py
    goto :end
)

if exist "C:\Python311\python.exe" (
    C:\Python311\python.exe tubegrab_pro.py
    goto :end
)

echo [HATA] Python bulunamadi!
echo.
echo Cozum: Python'u yukleyin ve PATH'e ekleyin:
echo   1. https://www.python.org/downloads/ adresinden indirin
echo   2. Kurulumda "Add Python to PATH" kutusunu isaretleyin
echo   3. pip install customtkinter yt-dlp komutunu calistirin
echo.
pause
:end
