@echo off
setlocal

cd /d "%~dp0"

echo ==================================================
echo           SIGNALDESK LAUNCHER
echo ==================================================
echo.
echo Starting SignalDesk...
echo.
echo IMPORTANT:
echo - Do NOT close this window while using the app
echo - Closing this window will STOP SignalDesk
echo - Logs are saved under the /logs folder
echo.
echo Opening in your browser shortly...
echo ==================================================
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir "logs"

REM Generate timestamp
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set TS=%%i

set LOGFILE=logs\signaldesk_%TS%.log

echo Logging to: %LOGFILE%
echo.

REM Optional: activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat" >> "%LOGFILE%" 2>&1
) else if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat" >> "%LOGFILE%" 2>&1
)

REM Run Streamlit and log output
echo [%TIME%] Running scoring engine...
python -m engine.run_scoring >> "%LOGFILE%" 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Scoring engine failed. Check logs for details.
    echo Log file: %LOGFILE%
    echo.
    pause
    exit /b 1
)

echo [%TIME%] Scoring complete.
echo.
python -m streamlit run app/Home.py >> "%LOGFILE%" 2>&1

echo.
echo ==================================================
echo SignalDesk has stopped.
echo You may now close this window.
echo ==================================================
echo.

pause
endlocal