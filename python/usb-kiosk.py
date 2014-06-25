#! /usr/bin/env python

import os, sys, subprocess, time, shutil, Image

USB_PATH = "/media/usb0/"
USB_LOG_PATH = USB_PATH + 'kiosk_log'
USB_KIOSK_PATH = USB_PATH + 'kiosk'
USB_BACKUP_PATH = USB_PATH + 'kiosk_backup'
KIOSK_LOG_PATH = "/home/pi/usb-kiosk/log"
KIOSK_IMG_PATH = "/home/pi/usb-kiosk/html/img"
KIOSK_TXT_PATH = "/home/pi/usb-kiosk/html/txt"

IMAGE_EXTENSION = ('.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG')
TEXT_EXTENSION = ('.txt', '.TXT')

def WriteLog(logMsg):

    now = time.strftime("%c")
    msg = "%s: %s" % (now, logMsg)
    print "LOG: ", msg
    msg += "\n"
    if not os.path.isdir(KIOSK_LOG_PATH):
        os.mkdir(KIOSK_LOG_PATH, 755)
    log = open(KIOSK_LOG_PATH + '/kiosk.log', 'a')
    log.write(msg)
    try:
        if not os.path.isdir(USB_LOG_PATH):
            os.mkdir(USB_LOG_PATH, 755)
        log_usb = open(USB_LOG_PATH + '/kiosk.log', 'a')
        log_usb.write(msg)
        log_usb.close()
    except:
        log.write("%s: USB Logfile can not be opened, only local log written." % now)
    log.close()

def UsbDrivePresent():
    proc = subprocess.Popen(["ls /dev | grep 'sda'"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    if 'sda' in out:
        return True
    else:
        return False

def KioskFilesPresent():
    # check if usb contains kiosk directory
    if os.path.isdir(USB_KIOSK_PATH):
        WriteLog("USB Kiosk directory present")
        txtPresent = False
        jpgPresent = False
        # check if at least one image and a txt with info text is present
        for file in os.listdir(USB_KIOSK_PATH):
            WriteLog("USB - kiosk: %s" % file)
            if file.endswith((IMAGE_EXTENSION)):
                jpgPresent = True
            elif file.endswith((TEXT_EXTENSION)):
                txtPresent = True
        return (txtPresent and jpgPresent)
    else:
        return False

def UpdateKioskFiles():
    # backup current files from player on USB stick
    if not os.path.isdir(USB_BACKUP_PATH):
        os.mkdir(USB_BACKUP_PATH, 755)
    BackupKioskFilesFromPlayer(USB_BACKUP_PATH)

    # remove old files from player
    DeleteAllFilesInDir(KIOSK_IMG_PATH)
    DeleteAllFilesInDir(KIOSK_TXT_PATH)

    WriteLog("Copying files from USB to kiosk player")
    # copy new files from USB device to kiosk player
    for file in os.listdir(USB_KIOSK_PATH):
        srcFile = USB_KIOSK_PATH + '/' + file
        dstFile = ""
        if not file.startswith(".") and file.endswith((IMAGE_EXTENSION)):
            dstFile = KIOSK_IMG_PATH + '/' + file
            shutil.copyfile(srcFile, dstFile)
            OptimizeImage(dstFile)
        elif not file.startswith(".") and file.endswith((TEXT_EXTENSION)):
            dstFile = KIOSK_TXT_PATH + '/' + file
            shutil.copyfile(srcFile, dstFile)
    WriteLog("File update done")

def DeleteAllFilesInDir(dir_path):
    WriteLog("Deleting files in directory %s" %dir_path)
    for file in os.listdir(dir_path):
        fullPath = dir_path + '/' + file
        if os.path.isdir(fullPath):
            shutil.rmtree(fullPath)
        else:
            os.remove(fullPath)

def BackupKioskFilesFromPlayer(destPath):
    if not os.path.isdir(destPath):
        WriteLog("Creating path for backup: %s" % destPath)
        os.mkdir(destPath, 755)
    WriteLog("Backing up textfiles")
    for file in os.listdir(KIOSK_TXT_PATH):
        filePath = KIOSK_TXT_PATH + '/' + file
        shutil.copy(filePath, destPath)
    WriteLog("Backing up images")
    for file in os.listdir(KIOSK_IMG_PATH):
        filePath = KIOSK_IMG_PATH + '/' + file
        shutil.copy(filePath, destPath)

def OptimizeImage(imgPath):
    WriteLog("Optimizing Image: " + imgPath)
    maxW = 1920
    maxH = 1080
    if imgPath.endswith((IMAGE_EXTENSION)):
        img = Image.open(str(imgPath))
        try:
            img.load()
        except IOError:
            WriteLog("IOError in loading PIL image while optimizing, filling up with grey pixels...")
        w,h = img.size
        if w/h < 1.770:
            width = maxW
            height = maxW * h / w
        else:
            height = maxH
            width = maxH * w / h
        img.thumbnail((width, height))

        WriteLog("Imagesize %d x %d" % (width, height))
        if width == 1920:
            WriteLog("Cropping height")
            # crop upper and lower part
            diff = height - 1080
            img = img.crop((0,diff/2,width,height-diff/2))
        else:
            WriteLog("Cropping width")
            # crop left and right part
            diff = width - 1920
            img = img.crop((diff/2,0,width-diff/2,height))
        img.save(imgPath, 'JPEG', quality=90)


def StartKioskMode():
    os.system("su -l pi -c 'startx'")

# Main Method
def StartupRoutine():
    if not os.path.isdir(KIOSK_TXT_PATH):
        WriteLog("Creating path for kiosk txt file: %s" % KIOSK_TXT_PATH)
        os.mkdir(KIOSK_TXT_PATH, 755)
    if not os.path.isdir(KIOSK_IMG_PATH):
        WriteLog("Creating path for kiosk images: %s" % KIOSK_IMG_PATH)
        os.mkdir(KIOSK_IMG_PATH, 755)
    if UsbDrivePresent():
        WriteLog("USB device present")
        if KioskFilesPresent():
            WriteLog("Kiosk files found on USB device")
            UpdateKioskFiles()
        else:
            WriteLog("No kiosk files found on USB device")
            WriteLog("Backing up current files from player on USB device")
            BackupKioskFilesFromPlayer(USB_KIOSK_PATH)
    WriteLog("Startup routine finished, starting kiosk mode...")
    WriteLog("Bye bye...")
    StartKioskMode()


StartupRoutine()
