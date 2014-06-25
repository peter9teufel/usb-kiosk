USB Kiosk for Raspberry Pi
=========
Introduction
=====
USB Kiosk for Raspberry Pi is a small html based standalone kiosk application for the Raspberry Pi. By providing an easy to use setup with an USB data stick it can be easily updated with content by anyone without the need of network knowledge or SSH access.
Once installed USB Kiosk requires no network connection and is a complete standalone solution for Full HD info screens.
Installation
=====
You do not need to copy all sources to your raspberry pi by hand. Simple download the 'install_usb_kiosk.sh' script, copy it to the home directory of your 'pi' user and execute it. The script will install all required packages, load the up-to-date usb kiosk sources from the repo and setup the autostart of the kiosk application. The installation script has been tested on a clean Raspian Installation (version from 2014-06-20), filesystem expansion, overclocking, memory split and password modifications are not done by the install script for now. This stuff may be added when the project proceeds and has a lot more to offer. :-)
Usage
=====
The USB Kiosk can be filled with content with a USB flash drive.
USB preparation
===
Format your USB Flash Drive using FAT and create a directory called 'kiosk' in the root of the flash drive. Put your images and a file called 'info.txt' in that folder. The 'info.txt' has to contain all text that should scroll on the info line in one single line.
Setting up the Kiosk
===
Attach the USB Flash Drive to the Raspberry Pi USB port and power on the Raspberry Pi. The Kiosk startup script will recognize your USB Flash Drive, backup the currently present files from the kiosk player in a folder called 'kiosk_backup' on your USB drive and copy the new files to the kiosk player. That's all, the player will proceed and start the kiosk with the new data.
Getting data from a set up Kiosk
===
If you ever need the data currently used on one of your USB Kiosk Players simply attach an USB Flash Drive that DOES NOT contain a 'kiosk' folder to the Raspberry Pi and reboot it. The startup script will backup the files from the player in a 'kiosk' folder on your USB Flash Drive, ready to use to setup another player. This feature is especially helpful if you need to load the data from a player to modify it or if you like to clone the data from one player to another.
Future improvements
=====
This version of USB Kiosk is for test purposes by now. I am currently working on a site based design with specific info texts for a specific matching background. Additionally a second screen layout with static text will be added in the future.
