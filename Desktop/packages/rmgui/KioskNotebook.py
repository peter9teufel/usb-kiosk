import packages.rmutil as rmutil
from packages.lang.Localizer import *
import KioskMainPanel as mainPanel
import KioskEditorPanel as editPanel
import os, sys, platform, ast, time, threading, shutil

import wx
from wx.lib.wordwrap import wordwrap
from operator import itemgetter
from packages.lang.Localizer import *

playerCount = 0
activePageNr = 0

HOST_WIN = 1
HOST_MAC = 2
HOST_LINUX = 3
HOST_SYS = None

################################################################################
# IMAGE TRANSFER NOTEBOOK FOR PLAYER PANELS ####################################
################################################################################
class KioskNotebook(wx.Notebook):
    def __init__(self, parent, id, log):
        wx.Notebook.__init__(self, parent, id, style=
                            wx.BK_DEFAULT
                            )
        self.parent = parent
        self.pages = []
        self.activePageNr = 0
        global HOST_SYS
        # check platform
        if platform.system() == 'Windows':
            HOST_SYS = HOST_WIN
        elif platform.system() == 'Darwin':
            HOST_SYS = HOST_MAC
        elif platform.system() == 'Linux':
            HOST_SYS = HOST_LINUX

        if HOST_SYS == HOST_LINUX or HOST_SYS == HOST_WIN:
            self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        elif HOST_SYS == HOST_MAC:
            self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanged)
        self.mainPage = None
        self.LoadMainPage()
        self.Show()

    def Close(self):
        from os.path import expanduser
        home = expanduser("~")
        appPath = home + '/.usb_kiosk/'
        tmpPath = appPath + 'tmp/'
        if os.path.isdir(tmpPath):
            shutil.rmtree(tmpPath)
        self.Destroy()

    def UpdatePageName(self, oldName, newName):
        for i in range(self.GetPageCount()):
            page = self.GetPage(i)
            label = page.GetLabel()
            found = label == oldName
            if found:
                self.SetPageText(i, newName)

    def LoadPageData(self, pageNumber):
        # print "Loading config and remote list for page ", pageNumber
        self.GetPage(pageNumber).LoadData()

    def LoadMainPage(self):
        self.mainPage = mainPanel.KioskMainPanel(self,-1,"Kiosk Main",0,HOST_SYS)
        self.pages.append(self.mainPage)
        self.AddPage(self.mainPage, "Kiosk Main")

    def AddNewPage(self, event=None):
        newPage = editPanel.KioskEditorPanel(self,-1,"New Page",self.GetPageCount(),HOST_SYS)
        self.pages.append(newPage)
        self.AddPage(newPage, "New Page")

    def AddKioskPage(self, title, texts, images):
        page = editPanel.KioskEditorPanel(self,-1,title,self.GetPageCount(),HOST_SYS,texts,images)
        self.pages.append(page)
        self.AddPage(page, title)

    def OnPageChanged(self, event):
        global HOST_SYS
        # print "ON PAGE CHANGED TRIGGER"
        self.activePageNr = event.GetSelection()
        if HOST_SYS == HOST_LINUX and event.GetOldSelection() == -1:
            pass
        else:
            sel = event.GetSelection()
            self.LoadPageData(sel)
