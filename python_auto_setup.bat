@echo off
setlocal

set PYTHON_VERSION=3.12.4
set PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe

:: Define the path to the installer
set "installer=%TEMP%\python-installer.exe"

:: Download the installer
powershell -Command "Invoke-WebRequest -Uri '%url%' -OutFile '%installer%'"

:: Install Python (quiet install, add to PATH, disable path length limit)
start /wait "" "%installer%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

:: Delete the installer
del "%installer%"

endlocal
