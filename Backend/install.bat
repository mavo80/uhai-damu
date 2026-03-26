@echo off
echo Installing required packages for Uhai Damu Chatbot...
echo.

echo Trying python -m pip...
python -m pip install flask flask-cors google-generativeai python-dotenv gunicorn
if %errorlevel% equ 0 goto success

echo.
echo Trying py -m pip...
py -m pip install flask flask-cors google-generativeai python-dotenv gunicorn
if %errorlevel% equ 0 goto success

echo.
echo Trying python3 -m pip...
python3 -m pip install flask flask-cors google-generativeai python-dotenv gunicorn
if %errorlevel% equ 0 goto success

echo.
echo [ERROR] Could not install packages. Please run manually:
echo.
echo python -m pip install flask
echo python -m pip install flask-cors
echo python -m pip install google-generativeai
echo python -m pip install python-dotenv
echo python -m pip install gunicorn
echo.
pause
exit /b 1

:success
echo.
echo ✅ All packages installed successfully!
pause