import packages.rmutil as util
from packages.rmgui import *
import PlayerInfoDialog as playerDlg
from packages.lang.Localizer import *
import os, sys, platform, ast, time, threading, shutil, copy

if platform.system() == "Linux":
    from wx.lib.pubsub import setupkwargs
    from wx.lib.pubsub import pub as Publisher
else:
    from wx.lib.pubsub import pub as Publisher

import wx
from wx.lib import imagebrowser
from wx.lib.wordwrap import wordwrap

HOST_WIN = 1
HOST_MAC = 2
HOST_LINUX = 3
HOST_SYS = None
BASE_PATH = None

################################################################################
# RASP MEDIA ALL PLAYERS PANEL #################################################
################################################################################
class KioskMainPanel(wx.Panel):
    def __init__(self,parent,id,title,index,host_sys):
        #wx.Panel.__init__(self,parent,id,title)
        wx.Panel.__init__(self,parent,-1)
        global HOST_SYS, BASE_PATH
        HOST_SYS = host_sys
        BASE_PATH = parent.parent.base_path
        self.parent = parent
        self.index = index
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.bg = None
        self.logo = None
        self.imgPath = self.DefaultPath()
        self.usbPath = None
        self.Initialize()


    def DefaultPath(self):
        path = os.path.expanduser("~")
        result = path
        # try common image directory paths
        if os.path.isdir(path + '/Bilder'):
            result = path + '/Bilder'
        elif os.path.isdir(path + '/Eigene Bilder'):
            result = path + '/Eigene Bilder'
        elif os.path.isdir(path + '/Pictures'):
            result = path + '/Pictures'
        elif os.path.isdir(path + '/Images'):
            result = path + '/Images'
        return result

    def LoadData(self):
        pass

    def PageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.parent.GetSelection()
        self.notebook_event = event
        newPage = self.parent.GetPage(new)
        if self.index == newPage.index:
            self.pageDataLoading = True
            self.LoadData()

    def Initialize(self):

        # Background selection
        bg = wx.Button(self,-1,label="Background")
        bgImg = wx.EmptyImage(200,200)
        # create bitmap with preview png
        self.bgCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(bgImg))
        self._SetImagePreview('img/clear.png')

        # Logo selection
        logo = wx.Button(self,-1,label="Logo")
        logoImg = wx.EmptyImage(200,200)
        self.logoCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(logoImg))
        self._SetImagePreview('img/clear.png',logo=True)

        # background music
        musicChk = wx.CheckBox(self,-1,label="Background Music")
        addSong = wx.Button(self,-1,label="Add Song(s)")
        self.songList = wx.ListCtrl(self,-1,size=(300,300),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.songList.Show(True)
        self.songList.InsertColumn(0,tr("filename"), width = 280)

        # crtls to add page, create usb etc
        addPage = wx.Button(self,-1,label="Add Page")
        loadFromUsb = wx.Button(self,-1,label="Load from USB")
        createUsb = wx.Button(self,-1,label="Create USB")
        exitBtn = wx.Button(self,-1,label="Exit")

        # Bind elements TODO!
        bg.Bind(wx.EVT_BUTTON, self.ShowBackgroundSelection)
        logo.Bind(wx.EVT_BUTTON, self.ShowLogoSelection)
        addPage.Bind(wx.EVT_BUTTON, self.parent.AddNewPage)
        createUsb.Bind(wx.EVT_BUTTON, self.WaitForUSBForCreation)
        loadFromUsb.Bind(wx.EVT_BUTTON, self.WaitForUSBForLoading)
        exitBtn.Bind(wx.EVT_BUTTON, self.parent.parent.Close)

        # Create and add sizers to main sizer
        # Sizer for BACKGROUND and LOGO selection
        imgSizer = wx.BoxSizer(wx.VERTICAL)
        imgSizer.Add(bg,flag=wx.TOP|wx.LEFT,border=5)
        imgSizer.Add(self.bgCtrl,flag=wx.TOP|wx.LEFT,border=5)
        imgSizer.Add(logo,flag=wx.TOP|wx.LEFT,border=5)
        imgSizer.Add(self.logoCtrl,flag=wx.TOP|wx.LEFT,border=5)
        # Sizer for AUDIO selection
        audioSizer = wx.BoxSizer(wx.VERTICAL)
        audioSizer.Add(musicChk,flag=wx.TOP|wx.LEFT,border=5)
        audioSizer.Add(addSong,flag=wx.TOP|wx.LEFT,border=5)
        audioSizer.Add(self.songList,flag=wx.TOP|wx.LEFT,border=5)

        # button sizer
        btnSizer = wx.BoxSizer()
        btnSizer.Add(exitBtn)
        btnSizer.Add(loadFromUsb)
        btnSizer.Add(createUsb)
        btnSizer.Add(addPage)

        # add to main sizer
        contentSizer = wx.BoxSizer()
        contentSizer.Add(imgSizer)
        contentSizer.Add(audioSizer,flag=wx.LEFT,border=30)
        self.mainSizer.Add(contentSizer)
        self.mainSizer.Add(btnSizer, flag=wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(self.mainSizer)

        #self.LayoutAndFit()
        self.Show(True)


    def ShowBackgroundSelection(self, event=None):
        dlg = imagebrowser.ImageDialog(None,self.imgPath)

        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetFile()
            self.bg = file
            print "Background selected: ", file
            self._SetImagePreview(file)
        if HOST_SYS == HOST_WIN:
            dlg.Destroy()

    def ShowLogoSelection(self, event=None):
        dlg = imagebrowser.ImageDialog(None,self.imgPath)

        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetFile()
            self.logo = file
            print "Logo selected: ", file
            self._SetImagePreview(file,logo=True)
        if HOST_SYS == HOST_WIN:
            dlg.Destroy()

    def LayoutAndFit(self):
        self.mainSizer.Layout()
        self.Fit()
        self.parent.Fit()
        self.parent.parent.Fit()
        self.parent.parent.Center()

    def _SetImagePreview(self, imagePath, logo=False):
        ## print "PREVIEW IMAGE PATH: " + imagePath
        path = resource_path(imagePath)
        #print "RESOURCE PATH: " + path
        img = wx.Image(path)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()

        maxSize = 200

        if W > H:
            NewW = maxSize
            NewH = maxSize * H / W
        else:
            NewH = maxSize
            NewW = maxSize * W / H
        img = img.Scale(NewW,NewH)

        if logo:
            self.logoCtrl.SetBitmap(wx.BitmapFromImage(img))
        else:
            self.bgCtrl.SetBitmap(wx.BitmapFromImage(img))

    def WaitForUSBForCreation(self, event):
        if self.usbPath == None or not os.path.isdir(self.usbPath):
            self.usbPath = None
            self.__WaitForUSB()
        else:
            self.CreateUSB(self.usbPath)

    def WaitForUSBForLoading(self, event):
        if self.usbPath == None or not os.path.isdir(self.usbPath):
            self.usbPath = None
            self.__WaitForUSB(loading=True)
        else:
            self.LoadFromUSB(self.usbPath)

    def __WaitForUSB(self, loading=False):
        print "Waiting for USB Drive..."
        if loading:
            Publisher.subscribe(self.LoadFromUSB, 'usb_connected')
        else:
            Publisher.subscribe(self.CreateUSB, 'usb_connected')
        self.prgDialog = wx.ProgressDialog(tr("searching"), tr("plug_usb"))
        self.prgDialog.Pulse()
        if HOST_SYS == HOST_WIN:
            util.Win32DeviceDetector.waitForUSBDrive()
        elif HOST_SYS == HOST_MAC or HOST_SYS == HOST_LINUX:
            util.UnixDriveDetector.waitForUSBDrive()

    def LoadFromUSB(self, path):
        self.usbPath = path
        self.prgDialog.UpdatePulse("Loading USB data...")
        # create kiosk directory in temp path
        from os.path import expanduser
        home = expanduser("~")
        appPath = home + '/.usb_kiosk/'
        tmpRoot = appPath + 'tmp/'
        tmpPath = tmpRoot + 'usb_data/'
        if os.path.isdir(tmpRoot):
            shutil.rmtree(tmpRoot)
        os.mkdir(tmpRoot)
        os.mkdir(tmpPath)

        usbPath = path + '/kiosk'
        if os.path.isdir(usbPath):
            # copy background and icon
            srcFile = usbPath + '/bg.jpg'
            destFile = tmpPath + 'bg.jpg'
            if os.path.isfile(srcFile):
                shutil.copyfile(srcFile, destFile)
                self.bg = destFile
            srcFile = usbPath + '/logo.png'
            destFile = tmpPath + 'logo.png'
            if os.path.isfile(srcFile):
                shutil.copyfile(srcFile, destFile)
                self.logo = destFile

            # copy data for single pages to page directories in temp dir
            usbPages = []
            for p in os.listdir(usbPath):
                if p.startswith('page'):
                    usbPages.append(p)
            for usbDir in usbPages:
                pageDir = usbPath + '/' + usbDir + '/'
                tmpPage = tmpPath + usbDir + '/'
                os.mkdir(tmpPage)
                # page headline
                shutil.copyfile(pageDir + 'headline.txt', tmpPage + 'headline.txt')
                # page texts and images
                for file in os.listdir(pageDir):
                    if file.startswith("Text") or file.startswith("image"):
                        shutil.copyfile(pageDir + file, tmpPage + file)

            # parse loaded data, create pages and update UI
            for dir in os.listdir(tmpPath):
                if dir.startswith("page"):
                    # page directory
                    pageDir = tmpPath + dir + '/'
                    images = []
                    txts = []
                    title = ""
                    for file in os.listdir(pageDir):
                        if file.startswith("Text"):
                            # page text
                            with open(pageDir + file) as f:
                                txts.append(f.read().decode("utf-8"))
                        elif file.startswith("image"):
                            # page image
                            images.append(pageDir + file)
                        elif file == "headline.txt":
                            # page headline
                            with open(pageDir + file) as f:
                                title = f.read().decode("utf-8")
                    self.parent.AddKioskPage(title, txts, images)
            # set background and logo preview if applicable
            if not self.bg == None:
                self._SetImagePreview(self.bg)
            if not self.logo == None:
                self._SetImagePreview(self.logo, logo=True)

            print "USB Loading done!"
        self.prgDialog.Update(100)
        if HOST_SYS == HOST_WIN:
            self.prgDialog.Destroy()

        wx.CallAfter(Publisher.unsubscribe, self.LoadFromUSB, 'usb_connected')


    def CreateUSB(self, path):
        self.usbPath = path
        self.prgDialog.UpdatePulse("Creating USB data...")
        # create kiosk directory on usb drive
        usbPath = path + '/kiosk'
        if os.path.isdir(usbPath):
            shutil.rmtree(usbPath)
        os.mkdir(usbPath)

        # copy background and icon if set
        if not self.bg == None:
            # TODO resize BG Image to 1920x1080 FIT MODE
            dstFile = usbPath + '/bg.jpg'
            shutil.copyfile(self.bg, dstFile)
        if not self.logo == None:
            # TODO convert to PNG!
            dstFile = usbPath + '/logo.png'
            shutil.copyfile(self.logo, dstFile)

        # copy data for single pages to page directories in kiosk directory on USB
        for i in range(1,self.parent.GetPageCount()):
            page = self.parent.GetPage(i)
            pageDir = usbPath + '/page' + str(i) + '/'
            os.mkdir(pageDir)
            # page headline
            fileName = pageDir + "headline.txt"
            f = open(fileName, 'w')
            f.write(page.title.encode("utf-8"))
            f.close()
            # page texts
            texts = page.texts
            for j in range(len(texts)):
                fileName = pageDir + "Text" + str(j+1) + ".txt"
                f = open(fileName, 'w')
                f.write(texts[j].encode("utf-8"))
                f.close()
            # page images
            imgs = page.images
            for j in range(len(imgs)):
                ending = ".jpg"
                if imgs[j].endswith(".png") or imgs[j].endswith(".PNG"):
                    ending = ".png"
                dstFile = pageDir + '/image' + str(j) + ending
                shutil.copyfile(imgs[j], dstFile)
        print "USB Preparation done!"
        self.prgDialog.Update(100)
        if HOST_SYS == HOST_WIN:
            self.prgDialog.Destroy()

        wx.CallAfter(Publisher.unsubscribe, self.CreateUSB, 'usb_connected')

# HELPER METHOD to get correct resource path for image file
def resource_path(relative_path):
    global BASE_PATH
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = BASE_PATH
    #print "JOINING " + base_path + " WITH " + relative_path
    resPath = os.path.normcase(os.path.join(base_path, relative_path))
    #resPath = base_path + relative_path
    #print resPath
    return resPath
