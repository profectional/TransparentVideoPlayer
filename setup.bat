@echo off
setlocal

echo Get Python from (https://www.python.org/downloads/)
set /p install_python=Else do you want to install Python 3.12.4 automatically (y/n)?

if /i "%install_python%"=="y" (
    :: Target Python version to install
    set "target_version=3.12.4"

    :: Download Python installer
    powershell.exe -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/%target_version%/python-%target_version%-amd64.exe -OutFile python_installer.exe"

    :: Install Python
    start /wait python_installer.exe /quiet PrependPath=1

    :: Remove Python installer
    del python_installer.exe
)

:: Wait for 5 seconds
timeout /t 5 /nobreak >nul

:: Get the directory of the current script
for %%I in ("%~dp0") do set "script_dir=%%~fI"

:: Construct the absolute path to module_setup.py
set "module_setup_path=%script_dir%module\module_setup.py"

:: Run module_setup.py
echo Installing modules...
python "%module_setup_path%"

:: Run main.py
python "%script_dir%main.py"

endlocal