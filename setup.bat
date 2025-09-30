@echo off
echo =======================================
echo    Fosen VPN - Windows Setup Script
echo =======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found!
python --version

echo.
echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Warning: Some packages may have failed to install
    echo You can try installing them manually:
    echo   pip install cryptography colorama
    echo.
)

echo.
echo =======================================
echo Setup complete!
echo.
echo To run the VPN:
echo   GUI Mode:    python fosen_vpn.py
echo   Server Mode: python fosen_vpn.py server
echo   Client Mode: python fosen_vpn.py client
echo   Help:        python fosen_vpn.py help
echo =======================================
pause