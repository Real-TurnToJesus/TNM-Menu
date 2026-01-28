@echo off
cd platform-tools
adb devices
adb tcpip 5037
echo.
echo Server started on port 5037
echo.
pause
