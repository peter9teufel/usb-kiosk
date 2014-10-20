#! /bin/sh

# clean up first
echo "Cleaning up old build and release directories..."
rm -rf build dist Release
mkdir Release

# get current directory and destination path
cwd=$(pwd)
destPath="$cwd/Release"
distPath="dist"

##### BUILD RASPMEDIA IMAGE TRANSFER #####
echo ""
echo "Compiling Kiosk Editor..."
pyinstaller KioskEditor.spec

# copy built version to tools directory
echo ""
echo "Making release file for Kiosk Editor..."
distFile="$distPath/Kiosk Editor.app"
destFile="$destPath/Kiosk Editor.app"
cp -r "$distFile" "$destFile"

# modify plist file of app to be foreground
#echo "Updating Info.plist for Kiosk Editor Release..."
#plist="$destFile/Contents/Info"
#defaults write "$plist" LSBackgroundOnly -string NO
#plist="$plist.plist"
#plutil -convert xml1 "$plist"

# remove build directories
echo "Cleaning up..."
rm -rf build dist

echo "Build done, bye bye..."
