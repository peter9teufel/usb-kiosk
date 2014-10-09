#! /usr/bin/env python

import os, sys, subprocess, time, shutil, Image, threading
import urllib2

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
STREAM_ENDING = ('.nsv', '.m3u', '.pls')

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
        pagesValid[page] = (jpgPresent)
        if not (jpgPresent):
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

    # remove old stream info if present
    streamfile = HTML_ROOT_PATH + '/stream.txt'
    if os.path.isfile(streamfile):
        os.remove(streamfile)

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
                    # shutil.copyfile(srcFile, dstFile)
                    # OptimizeImage(dstFile)
                    # fileName, basePath, destPath
                    OptimizeAndCopyImage(file, USB_KIOSK_PATH + '/' + page, KIOSK_PAGES_PATH + '/' + page + '/img')
                elif not file.startswith(".") and file.endswith((TEXT_EXTENSION)):
                    dstFile = KIOSK_PAGES_PATH + '/' + page + '/txt/' + file
                    shutil.copyfile(srcFile, dstFile)
    if os.path.isfile(USB_KIOSK_PATH + '/stream.txt'):
        print "Copying stream address file..."
        dstFile = HTML_ROOT_PATH + '/stream.txt'
	srcFile = USB_KIOSK_PATH + '/stream.txt'
	shutil.copyfile(srcFile, dstFile)
    WriteLog("File update done")

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
        if os.path.isdir(curPath):
            for file in os.listdir(curPath):
                shutil.copyfile(curPath + '/' + file, destPath + '/' + folder + '/' + file)

        # backup txt folder
        curPath = KIOSK_PAGES_PATH + '/' + folder + '/txt'
        if os.path.isdir(curPath):
            for file in os.listdir(curPath):
                shutil.copyfile(curPath + '/' + file, destPath + '/' + folder + '/' + file)
    WriteLog("Backing up streamfile, logo and background")
    streamfile = HTML_ROOT_PATH + '/stream.txt'
    if os.path.isfile(streamfile):
        shutil.copyfile(streamfile, destPath + '/stream.txt')
    shutil.copyfile(HTML_ROOT_PATH + '/bg.jpg', destPath + '/bg.jpg')
    shutil.copyfile(HTML_ROOT_PATH + '/logo.png', destPath + '/logo.png')
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

def OptimizeAndCopyImage(fileName, basePath, destPath, maxW=1920, maxH=1080, minW=400, minH=400):
    filePath = basePath + '/' + fileName
    destFilePath = destPath + '/' + fileName
    if filePath.endswith((IMAGE_EXTENSION)):
        #print "Opening image " + filePath
        img = Image.open(str(filePath))
        try:
            img.load()
        except IOError:
            print "IOError in loading PIL image while optimizing, filling up with grey pixels..."
        # check exif data if image was originally rotated
        #img = _checkOrientation(img)
        w,h = img.size

        if w > maxW or h > maxH:
            if w/h > 1.770:
                width = maxW
                height = maxW * h / w
            else:
                height = maxH
                width = maxH * w / h
            img.thumbnail((width, height))
        elif w < minW or h < minH:
            if w/h > 1.770:
                width = minW
                height = minW * h / w
            else:
                height = minH
                width = minH * w / h
            img.thumbnail((width, height))
        else:
            width = w
            height = h
        WriteLog("Saving optimized image: %d x %d at path %s" % (width,height,destFilePath))
        if(fileName.endswith('.png') or fileName.endswith('.PNG')):
            img.save(destFilePath, 'PNG')
        else:
            img.save(destFilePath, 'JPEG', quality=90)

def GetStreamAddr():
    streamAddr = ""
    fname = HTML_ROOT_PATH + '/stream.txt'
    if os.path.isfile(fname):
        content = []
        with open(fname) as f:
            content = f.readlines()
        for line in content:
            # remove line break
	    line = line[:-1]
	    print "Checking stream.txt line: ", line
	    if len(line) > 5 and not line.startswith('#') and line.endswith((STREAM_ENDING)):
                streamAddr = line
    return streamAddr

def StartKioskMode():
    os.system("su -l pi -c 'startx'")

def StartWebradioStream():
    streamAddr = GetStreamAddr()
    print "Stream address from stream.txt: ",streamAddr
    if len(streamAddr) > 0:
        cmd = ""
        if 'apasf.apa.at:8000' in streamAddr:
            # ORF stream address, needs to be handled with omxplayer
            cmd = "omxplayer " + streamAddr
        elif streamAddr.endswith('pls') or streamAddr.endswith('m3u'):
            # normal m3u or pls stream address, can be player using mplayer
            cmd = "mplayer -playlist " + streamAddr

        print "Starting live stream with command: ", cmd
        os.system(cmd)

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


    # start webradio stream in separate thread
    t = threading.Thread(target=StartWebradioStream)
    t.start()
    StartKioskMode()


StartupRoutine()
