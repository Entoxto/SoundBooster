@echo off
echo === Запуск SoundBooster для Windows ===
echo.

cd /d "%~dp0"
python -m pip install -r config\requirements.txt
if errorlevel 1 goto end

python app\sound_booster.py

:end
echo.
pause
