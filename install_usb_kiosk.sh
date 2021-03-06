#!/bin/sh

echo "Removing not used wolfram engine..."
# remove not used wolfram-engine
sudo apt-get -y remove wolfram-engine;

echo "Updating sources and system..."
# update apt sources and upgrade installed packages
sudo apt-get -y update;
sudo apt-get -y upgrade;

echo "Installing required packages..."
# install apache webserver with php5
sudo apt-get -y install apache2 php5 libapache2-mod-php5;

# install python imaging library
sudo apt-get -y install python-imaging

# install chromium browser with x11 utils and unclutter
sudo apt-get -y install chromium x11-xserver-utils unclutter;

# install usbmount
sudo apt-get -y install usbmount

# install netifaces
sudo apt-get -y install python-netifaces;

# install mplayer for webradio playback
sudo apt-get -y install mplayer;

echo "Cloning usb-kiosk source from github"
# clone usb-kiosk sourcefiles to /home/pi/usb-kiosk
cd /home/pi;
su -l pi -c 'git clone https://github.com/peter9teufel/usb-kiosk.git';

# prepare page directory
su -l pi -c 'mkdir /home/pi/usb-kiosk/html/pages';

# set symbolic link from webserver root to html dir of usb-kiosk
sudo ln -s /home/pi/usb-kiosk/html /var/www/usb-kiosk;

echo "Writing boot config...";
sudo cat /home/pi/usb-kiosk/rpi_usb_kiosk_boot_config.txt > /boot/config.txt;

echo "Setting up automatic update and autostart of usb-kiosk startup script"
# modify rc.local to start kiosk at boot
sudo head -n -2 /etc/rc.local > /home/pi/usb-kiosk/rc.local.tmp;
sudo cat /home/pi/usb-kiosk/rc.local.tmp > /etc/rc.local;
# automatic update at startup disabled for now
# sudo echo 'sudo /home/pi/usb-kiosk/update_player.sh' >> /etc/rc.local;
sudo echo 'cd /home/pi/usb-kiosk/python' >> /etc/rc.local;
sudo echo 'sudo python usb-kiosk.py' >> /etc/rc.local;
sudo echo 'exit 0' >> /etc/rc.local;
# remove temp file
sudo rm /home/pi/usb-kiosk/rc.local.tmp;

echo "Setting up autostart file for LXDE desktop"
# modify autostart file for LXDE desktop
# backup original autostart file
sudo cp /etc/xdg/lxsession/LXDE/autostart /etc/xdg/lxsession/LXDE/autostart.BAK;
# write new autostart file
sudo echo '@xset s off' > /etc/xdg/lxsession/LXDE/autostart;
sudo echo '@xset -dpms' >> /etc/xdg/lxsession/LXDE/autostart;
sudo echo '@xset s noblank' >> /etc/xdg/lxsession/LXDE/autostart;
sudo echo '@chromium --kiosk --incognito --disable-translate http://127.0.0.1/usb-kiosk/infoscreen.html' >> /etc/xdg/lxsession/LXDE/autostart
# write autostart for pi user specific as well, seems to be necessary with newest wheezy release
sudo echo '@xset s off' > /etc/xdg/lxsession/LXDE-pi/autostart;
sudo echo '@xset -dpms' >> /etc/xdg/lxsession/LXDE-pi/autostart;
sudo echo '@xset s noblank' >> /etc/xdg/lxsession/LXDE-pi/autostart;
sudo echo '@chromium --kiosk --incognito --disable-translate http://127.0.0.1/usb-kiosk/infoscreen.html' >> /etc/xdg/lxsession/LXDE-pi/autostart

echo 'Setup complete!';
echo 'Rebooting now...';
sudo reboot;

# install script deletes itself after completion
rm -- "$0"
