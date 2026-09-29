@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
set "GUPPY_ACTION=%~1"
if "%GUPPY_ACTION%"=="" set "GUPPY_ACTION=install"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 setup.py %GUPPY_ACTION% --platform windows
  exit /b
)
where python >nul 2>nul
if not errorlevel 1 (
  python setup.py %GUPPY_ACTION% --platform windows
  exit /b
)
echo Install Python 3.10 or newer first. See START-HERE.md.
exit /b 2
