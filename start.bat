@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

set "FRONTEND_PORT=5173"
set "FRONTEND_URL=http://localhost:%FRONTEND_PORT%"

echo ============================================
echo  RudyTrade AI - paper-only system startup
echo ============================================
echo.

set "MODE=start"
set "REINSTALL=0"
for %%A in (%*) do (
    if /i "%%~A"=="--check" set "MODE=check"
    if /i "%%~A"=="--reinstall" set "REINSTALL=1"
    if /i "%%~A"=="--help" goto :usage
    if /i "%%~A"=="-h" goto :usage
)

set "PY_CMD="
where py >nul 2>nul && set "PY_CMD=py -3"
if not defined PY_CMD (
    where python >nul 2>nul && set "PY_CMD=python"
)
if not defined PY_CMD (
    echo [ERROR] Python 3.10+ was not found on PATH.
    echo         Install it from https://www.python.org/downloads/ and retry.
    exit /b 1
)

set "VENV_PY=.venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo [1/7] Creating virtual environment in .venv ...
    %PY_CMD% -m venv .venv
    if errorlevel 1 goto :fail
    set "REINSTALL=1"
) else (
    echo [1/7] Virtual environment already present.
)

if "%REINSTALL%"=="1" (
    echo [2/7] Installing package with dev extras ...
    "%VENV_PY%" -m pip install --upgrade pip >nul
    "%VENV_PY%" -m pip install -e ".[dev]"
    if errorlevel 1 goto :fail
) else (
    echo [2/7] Package already installed - use --reinstall to refresh.
)

if not exist ".env" (
    echo [3/7] Creating .env from .env.example ...
    copy /y ".env.example" ".env" >nul
    if errorlevel 1 goto :fail
    echo       Review .env before adding any real credentials.
) else (
    echo [3/7] Using existing .env - PAPER_ONLY must stay true.
)

echo [4/7] Initializing paper-only SQLite database ...
"%VENV_PY%" -m rudytrade.cli init-db
if errorlevel 1 goto :fail

if /i "%MODE%"=="check" (
    echo.
    echo Running test suite ...
    "%VENV_PY%" -m pytest
    if errorlevel 1 goto :fail
)

where npm >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js/npm was not found on PATH.
    echo         Install Node.js 18+ from https://nodejs.org/ and retry.
    exit /b 1
)

if "%REINSTALL%"=="1" (
    echo [5/7] Installing frontend dependencies ...
    pushd frontend
    call npm install
    if errorlevel 1 (
        popd
        goto :fail
    )
    popd
) else if not exist "frontend\node_modules" (
    echo [5/7] Installing frontend dependencies ...
    pushd frontend
    call npm install
    if errorlevel 1 (
        popd
        goto :fail
    )
    popd
) else (
    echo [5/7] Frontend dependencies already installed - use --reinstall to refresh.
)

echo [6/7] Starting frontend dev server in a new window ...
start "RudyTrade Frontend" /d "frontend" cmd /k "npm run dev"

echo       Waiting for %FRONTEND_URL% ...
where curl >nul 2>nul
if errorlevel 1 (
    timeout /t 5 /nobreak >nul
) else (
    set "READY=0"
    for /l %%I in (1,1,30) do (
        if "!READY!"=="0" (
            curl -s -o nul --max-time 2 "%FRONTEND_URL%" >nul 2>nul && set "READY=1"
            if "!READY!"=="0" timeout /t 1 /nobreak >nul
        )
    )
    if "!READY!"=="0" (
        echo [WARN] The frontend did not respond yet. Opening the browser anyway;
        echo        check the "RudyTrade Frontend" window for npm output.
    )
)

echo [7/7] Opening %FRONTEND_URL% in Chrome ...
set "CHROME="
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not defined CHROME if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if not defined CHROME if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" set "CHROME=%LocalAppData%\Google\Chrome\Application\chrome.exe"
if not defined CHROME (
    where chrome >nul 2>nul && set "CHROME=chrome"
)
if defined CHROME (
    start "" "!CHROME!" "%FRONTEND_URL%"
) else (
    echo       Chrome was not found - opening in the default browser instead.
    start "" "%FRONTEND_URL%"
)

echo.
echo ============================================
echo  System ready (paper-only, no live orders).
echo  Virtual environment: .venv
echo  Database:            data/rudytrade.sqlite3
echo  Frontend:            %FRONTEND_URL%
echo  Close the "RudyTrade Frontend" window to stop it.
echo ============================================
exit /b 0

:usage
echo Usage: start.bat [--check] [--reinstall]
echo   --check      Run the test suite after startup
echo   --reinstall  Reinstall Python and frontend dependencies
exit /b 0

:fail
echo.
echo [ERROR] Startup failed. See the output above.
exit /b 1
