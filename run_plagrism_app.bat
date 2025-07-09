@echo off
title Run Flask with Ngrok after Flask is ready

REM Step 1: Start Flask app in a new command window
echo [%time%] Starting Flask app...
start "Flask App" cmd /k "cd /d %~dp0 && conda activate anaconda && python app.py --no-reload"

REM Step 2: Wait for Flask to be ready by checking localhost:5000
echo [%time%] Waiting for Flask to be ready...
:wait_for_flask
powershell -Command "try { $r = Invoke-WebRequest -Uri http://127.0.0.1:5000 -UseBasicParsing -TimeoutSec 1; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"
if errorlevel 1 (
    timeout /t 1 >nul
    goto wait_for_flask
)

REM Step 3: Launch ngrok in a new window after Flask is ready
echo [%time%] Flask is ready. Launching ngrok...
start "Ngrok Tunnel" cmd /k "ngrok http 127.0.0.1:5000"
