rmdir /S /Q build
rmdir /S /Q dist
rmdir /S /Q Release
TIMEOUT 2
md Release

set "cwd=%~dp0"
set "destPath=Release"
set "distPath=dist"

start /wait pyinstaller KioskEditor.spec

set "distFile=%distPath%\Kiosk Editor.exe"
set "destFile=%destPath%\Kiosk Editor.exe"
copy "%distFile%" "%destFile%"

rmdir /S /Q build dist
