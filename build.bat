@echo off
echo === Сборка SoundBooster для Windows ===
echo.

cd /d "%~dp0"
python scripts\download_equalizer_apo.py
if errorlevel 1 goto end

python scripts\build.py

:end
echo.
pause
