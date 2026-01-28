@echo off
echo PLEASE PLUG IN YOUR VR TO SET THIS UP!!!
echo.
cd platform-tools
adb devices
adb shell ip route
echo.
adb tcpip 5037
echo.
echo COPY THAT IP AND PUT IT INSIDE OF SETTINGS.JSON WITH QUOTATIONS AROUND IT (or with nothing if you type it in the menu)!!! MAKE SURE IT ISN'T THE ONE WITH THE SLASH!
echo USE THE TOP RIGHT ONE!!!!
echo IF YOU DON'T SEE AN IP, ON YOUR HEADSET GO TO YOUR WIFI SETTINGS, AND VIEW YOUR WIFI DETAILS, AND THE 'IP' FIELD IS YOUR IP!
echo.
echo NOTE: You need to do this once for every WiFi network you connect to.
echo DM me on Discord if you are having any issues @texan789
echo.
echo.
echo.
pause
