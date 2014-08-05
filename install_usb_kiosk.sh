#!/bin/sh

echo "Removing preparation script..."
sudo rm prepare_raspbian.sh;

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

echo "Cloning usb-kiosk source from github"
# clone usb-kiosk sourcefiles to /home/pi/usb-kiosk
cd /home/pi;
su -l pi -c 'git clone https://github.com/peter9teufel/usb-kiosk.git';

# prepare page directory
su -l pi -c 'mkdir /home/pi/usb-kiosk/html/pages';

# set symbolic link from webserver root to html dir of usb-kiosk
sudo ln -s /home/pi/usb-kiosk/html /var/www/usb-kiosk;

echo "Setting up automatic update and autostart of usb-kiosk startup script"
# modify rc.local to start kiosk at boot
sudo head -n -2 /etc/rc.local > /home/pi/usb-kiosk/rc.local.tmp;
sudo cat /home/pi/usb-kiosk/rc.local.tmp > /etc/rc.local;
sudo echo 'sudo /home/pi/usb-kiosk/update_player_sh' >> /etc/rc.local;
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

echo 'Setup complete!';
echo 'Please prepare a usb stick with kiosk data for first boot.';
echo 'Shutting down...';
sudo shutdown -h now;
