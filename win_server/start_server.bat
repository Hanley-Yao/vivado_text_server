@echo off
setlocal
rem #
rem # COPYRIGHT NOTICE
rem # Copyright 2025 Text Editor Server. All Rights Reserved.
rem # 

rem ##
rem # Text Editor TCP Server with Vivado Hardware Server Integration
rem # This script launches both Vivado Hardware Server and Text Editor TCP Server
rem ##

rem ##
rem # Check if Python is installed
rem ##
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found, please install Python 3 first
    pause
    exit /b 1
)

rem ##
rem # Launch Vivado Hardware Server
rem ##
echo Starting Vivado Hardware Server...
start "Vivado HW Server" "C:\Xilinx\Vivado\2023.1\bin\hw_server.bat"
echo.

rem ##
rem # Launch Text Editor TCP Server
rem ##
echo Starting Text Editor TCP Server...
echo Server will listen on port 3112...
echo Please ensure firewall allows inbound connections on this port
echo.
python text_editor_server.py

pause
endlocal
