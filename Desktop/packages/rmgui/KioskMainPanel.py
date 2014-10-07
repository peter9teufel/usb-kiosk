import packages.rmutil as rmutil
from packages.rmgui import *
import PlayerInfoDialog as playerDlg
from packages.lang.Localizer import *
import os, sys, platform, ast, time, threading, shutil, copy

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
        self.Initialize()



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
        dlg = imagebrowser.ImageDialog(None)

        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetFile()
            print "Background selected: ", file
            self._SetImagePreview(file)
        if HOST_SYS == HOST_WIN:
            dlg.Destroy()

    def ShowLogoSelection(self, event=None):
        dlg = imagebrowser.ImageDialog(None)

        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetFile()
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
