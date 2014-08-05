#!/bin/sh

cd /home/pi/usb-kiosk
# check if network connected
result=$(ping -q -w 1 -c 1 `ip r | grep default | cut -d ' ' -f 3` > /dev/null && echo ok || echo error);

if [ "$result" = "ok" ]; then
        echo "Network connection available, trying to update sources...";
        {
                sudo git pull;
        } || {
                echo "Updating sources failed, will try again on next reboot.";
        }
fi
