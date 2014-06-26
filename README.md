USB Kiosk for Raspberry Pi
=========
Introduction
=====
USB Kiosk for Raspberry Pi is a small html based standalone kiosk application for the Raspberry Pi. By providing an easy to use setup with an USB data stick it can be easily updated with content by anyone without the need of network knowledge or SSH access.
Once installed USB Kiosk requires no network connection and is a complete standalone solution for Full HD info screens.
Installation
=====
To prepare a fresh raspberry pi Raspian setup you can run prepare_raspian.sh which will prompt you for a new user password, set the gpu memory split and expand the filesystem. When done the script launches raspi-config in case you want to modify more, otherwise simply choose finish in raspi-config and let the raspberry reboot. The things done by the prepare_raspian.sh script can also be done manually using raspi-config.
You do not need to copy all sources to your raspberry pi by hand. Simple download the 'install_usb_kiosk.sh' script, copy it to the home directory of your 'pi' user and execute it. The script will install all required packages, load the up-to-date usb kiosk sources from the repo and setup the autostart of the kiosk application. The installation script has been tested on a clean Raspian Installation (version from 2014-06-20).
When the install script has finished the Raspberry Pi will shutdown, you can now prepare your data on a USB stick or simply start the player again to see a short How To.
Usage
=====
The USB Kiosk can be filled with content with a USB flash drive.
USB preparation
===
Format your USB Flash Drive using FAT and create a directory called 'kiosk' in the root of the flash drive. For each page of the kiosk create a subfolder. The name of the page subfolder will be used as headline of the page. Put the image for the page (currently one, multiple image support in progress) and a file called "info.txt" in the page folder. The info.txt has to contain the text for the page in one single line (more flexible text support in future version).
Setting up the Kiosk
===
Attach the USB Flash Drive to the Raspberry Pi USB port and power on the Raspberry Pi. The Kiosk startup script will recognize your USB Flash Drive, backup the currently present files from the kiosk player in a folder called 'kiosk_backup' on your USB drive and copy the new files to the kiosk player. That's all, the player will proceed and start the kiosk with the new data.
Getting data from a set up Kiosk
===
If you ever need the data currently used on one of your USB Kiosk Players simply attach an USB Flash Drive that DOES NOT contain a 'kiosk' folder to the Raspberry Pi and reboot it. The startup script will backup the files from the player in a 'kiosk' folder on your USB Flash Drive, ready to use to setup another player. This feature is especially helpful if you need to load the data from a player to modify it or if you like to clone the data from one player to another.
Future improvements
=====
This version of USB Kiosk is still under development, some first features are working quite well but there is still more to come, so stay tuned ;-)
