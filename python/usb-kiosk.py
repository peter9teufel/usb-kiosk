#! /usr/bin/env python

import os, sys, subprocess, time, shutil, Image

ROOT_PATH = "/home/pi/usb-kiosk"
HTML_ROOT_PATH = ROOT_PATH + "/html"
USB_PATH = "/media/usb0/"
USB_LOG_PATH = USB_PATH + 'kiosk_log'
USB_KIOSK_PATH = USB_PATH + 'kiosk'
USB_BACKUP_PATH = USB_PATH + 'kiosk_backup'
KIOSK_LOG_PATH = ROOT_PATH + "/log"
KIOSK_PAGES_PATH = HTML_ROOT_PATH + "/pages"

USB_LOGGING = False

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
    if USB_LOGGING:
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
        pagesValid = USBPagesValid()
        if pagesValid['allPagesInvalid']:
            # data available but all page data folders are invalid
            return False
        else:
            return True

def PagesUSB():
    pages = []
    for file in os.listdir(USB_KIOSK_PATH):
        if os.path.isdir(USB_KIOSK_PATH + '/' + file):
            pages.append(file)
    return pages

def USBPagesValid():
    pages = PagesUSB()
    pagesValid = {}
    allValid = True
    allInvalid = True
    for page in pages:
        txtPresent = False
        jpgPresent = False
        # check if at least one image and a txt with info text is present
        for file in os.listdir(USB_KIOSK_PATH + '/' + page):
            if not file.startswith("."):
                WriteLog("USB - kiosk | page: %s File: %s" % (page,file))
                if file.endswith((IMAGE_EXTENSION)):
                    jpgPresent = True
                elif file.endswith((TEXT_EXTENSION)):
                    txtPresent = True
        pagesValid[page] = (txtPresent and jpgPresent)
        if not (txtPresent and jpgPresent):
            allValid = False
        else:
            allInvalid = False
    pagesValid['allPagesValid'] = allValid
    pagesValid['allPagesInvalid'] = allInvalid
    return pagesValid


def UpdateKioskFiles():
    # backup current files from player on USB stick
    if not os.path.isdir(USB_BACKUP_PATH):
        os.mkdir(USB_BACKUP_PATH, 755)
    BackupKioskFilesFromPlayer(USB_BACKUP_PATH)

    # remove old files from player
    DeleteAllFilesInDir(KIOSK_PAGES_PATH)

    WriteLog("Copying files from USB to kiosk player")
    pages = PagesUSB()
    pagesValid = USBPagesValid()

    for page in pages:
        if pagesValid[page]:
            # page is valid --> create page directories and proceed
            os.mkdir(KIOSK_PAGES_PATH + '/' + page)
            os.mkdir(KIOSK_PAGES_PATH + '/' + page + '/img')
            os.mkdir(KIOSK_PAGES_PATH + '/' + page + '/txt')
            for file in os.listdir(USB_KIOSK_PATH + '/' + page):
                srcFile = USB_KIOSK_PATH + '/' + page + '/' + file
                if not file.startswith(".") and file.endswith((IMAGE_EXTENSION)):
                    dstFile = KIOSK_PAGES_PATH + '/' + page + '/img/' + file
                    shutil.copyfile(srcFile, dstFile)
                    OptimizeImage(dstFile)
                elif not file.startswith(".") and file.endswith((TEXT_EXTENSION)):
                    dstFile = KIOSK_PAGES_PATH + '/' + page + '/txt/' + file
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
    if os.path.isdir(destPath):
        shutil.rmtree(destPath)
    WriteLog("Creating path for backup: %s" % destPath)
    os.mkdir(destPath, 755)
    WriteLog("Backing up page folders")
    for folder in os.listdir(KIOSK_PAGES_PATH):
        os.mkdir(destPath + '/' + folder)

        # backup img folder
        curPath = KIOSK_PAGES_PATH + '/' + folder + '/img'
        for file in os.listdir(curPath):
            shutil.copyfile(curPath + '/' + file, destPath + '/' + folder + '/' + file)

        # backup txt folder
        curPath = KIOSK_PAGES_PATH + '/' + folder + '/txt'
        for file in os.listdir(curPath):
            shutil.copyfile(curPath + '/' + file, destPath + '/' + folder + '/' + file)
    WriteLog("Data backup done in " + destPath)

def CheckForLogoUpdate():
    if os.path.isdir(USB_KIOSK_PATH):
        for file in os.listdir(USB_KIOSK_PATH):
            if file.lower().startswith('logo'):
                WriteLog("New Logo found on USB drive, copying to kiosk player")
                shutil.copyfile(USB_KIOSK_PATH + '/' + file, HTML_ROOT_PATH + '/' + file)

def CheckForBackgroundUpdate():
    if os.path.isdir(USB_KIOSK_PATH):
        for file in os.listdir(USB_KIOSK_PATH):
            if file == 'bg.jpg':
                WriteLog("New background found on USB drive, copying to kiosk player")
                shutil.copyfile(USB_KIOSK_PATH + '/' + file, HTML_ROOT_PATH + '/' + file)

def OptimizeImage(imgPath):
    WriteLog("Resizing Image: " + imgPath)
    maxW = 1920
    maxH = 1080
    if imgPath.endswith((IMAGE_EXTENSION)):
        img = Image.open(str(imgPath))
        try:
            img.load()
        except IOError:
            WriteLog("IOError in loading PIL image while optimizing, filling up with grey pixels...")
        w,h = img.size
        if w > maxW or h > maxH:
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
    if not os.path.isdir(KIOSK_PAGES_PATH):
        WriteLog("Creating path for kiosk pages: %s" % KIOSK_PAGES_PATH)
        # os.mkdir(KIOSK_PAGES_PATH, 744)
        os.system("su -l pi -c 'mkdir /home/pi/usb-kiosk/html/pages'")
    if UsbDrivePresent():
        WriteLog("USB device present")
        if KioskFilesPresent():
            WriteLog("Kiosk files found on USB device")
            UpdateKioskFiles()
        else:
            WriteLog("No kiosk files found on USB device")
            WriteLog("Backing up current files from player on USB device")
            BackupKioskFilesFromPlayer(USB_KIOSK_PATH)

        # check and update logo and background
        CheckForLogoUpdate()
        CheckForBackgroundUpdate()
    WriteLog("Startup routine finished, starting kiosk mode...")
    WriteLog("Bye bye...")
    StartKioskMode()


StartupRoutine()
