@echo off
setlocal enabledelayedexpansion

REM Run from the repo root (this .bat is in tools\)
cd /d "%~dp0.."

REM Safety: must be a git repo
if not exist ".git" (
  echo ERROR: Not a git repo. Run this inside your repo root.
  pause
  exit /b 1
)

REM Output folder
set "OUTDIR=zips"
if not exist "%OUTDIR%" mkdir "%OUTDIR%"

REM Get short hash for HEAD
for /f %%i in ('git rev-parse --short HEAD') do set "HASH=%%i"

set "ZIPPATH=%OUTDIR%\latest_commit.zip"

echo Creating %ZIPPATH% for HEAD (!HASH!) ...
git archive --format=zip --output="%ZIPPATH%" HEAD
if errorlevel 1 (
  echo ERROR: git archive failed.
  pause
  exit /b 1
)

echo Done: %ZIPPATH%
echo Commit: !HASH!
pause
