import packages.rmutil as rmutil
from packages.lang.Localizer import *
import KioskMainPanel as mainPanel
import KioskEditorPanel as editPanel
import PageOrderDialog as poDlg
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
    def __init__(self, parent, id, log, base_path):
        wx.Notebook.__init__(self, parent, id, style=
                            wx.BK_DEFAULT
                            )
        self.base_path = base_path
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

        wx.EVT_RIGHT_DOWN(self , self.OnNotebookRightClick)

        self.mainPage = None
        self.LoadMainPage()
        self.LoadPlusTab()
        self.Show()

    def Close(self):
        from os.path import expanduser
        home = expanduser("~")
        appPath = home + '/.usb_kiosk/'
        tmpPath = appPath + 'tmp/'
        if os.path.isdir(tmpPath):
            shutil.rmtree(tmpPath)
        self.Destroy()

    def OnNotebookRightClick(self, event):
        index, type = self.HitTest(event.GetPosition())
        if index > -1:
            if index > 0 and index < self.GetPageCount() - 1:
                print "Clicked on Page with Index: ", index
                page = self.GetPage(index)
                menu = wx.Menu()
                item = menu.Append(wx.NewId(), "Delete")
                #self.Bind(wx.EVT_MENU, self.DeleteSelectedTextItem, item)
                self.Bind(wx.EVT_MENU, lambda event, index=index: self.DeletePage(event,index), item)
                rect = self.GetRect()
                point = event.GetPosition()
                self.PopupMenu(menu, (rect[0]+point[0]+10,rect[1]+point[1]+10))
                menu.Destroy()

    def UpdatePageName(self, index, oldName, newName):
        # use index -1 because page count wrong by 1 due to "+" tab
        self.SetPageText(index - 1, newName)

    def LoadPageData(self, pageNumber):
        # print "Loading config and remote list for page ", pageNumber
        self.GetPage(pageNumber).LoadData()

    def LoadMainPage(self):
        self.mainPage = mainPanel.KioskMainPanel(self,-1,"Kiosk Main",0,HOST_SYS,self.base_path)
        self.pages.append(self.mainPage)
        self.AddPage(self.mainPage, "Kiosk Main")

    def LoadPlusTab(self):
        self.plusTab = wx.Panel(self,-1)
        self.AddPage(self.plusTab, "+")

    def AddNewPage(self, event=None):
        newIndex = self.GetPageCount()
        newPage = editPanel.KioskEditorPanel(self,-1,"New Page",newIndex,HOST_SYS,[],[],self.base_path)
        self.pages.append(newPage)
        self.InsertPage(self.GetPageCount()-1,newPage, "New Page",select=True)

    def AddKioskPage(self, title, texts, images):
        page = editPanel.KioskEditorPanel(self,-1,title,self.GetPageCount(),HOST_SYS,texts,images,self.base_path)
        self.pages.append(page)
        self.InsertPage(self.GetPageCount()-1,page, title)

    def DeletePage(self, event, index):
        self.SetSelection(0)
        self.RemovePage(index)
        del self.pages[index]

    def SaveConfiguration(self, event=None):
        dlg = wx.FileDialog(self, "Select where to save your Kiosk Configuration", "", "", "KIOSK files(*.kiosk)|*.*", wx.FD_SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            save_path = dlg.GetPath() + ".kiosk"
            self.mainPage.SaveConfiguration(save_path)
            #print "You want to save your config to ", save_path

    def OpenConfiguration(self, event=None):
        # clear notebook and temp data
        self.ClearNotebook()
        dlg = wx.FileDialog(self, "Select your Kiosk Configuration", "", "", "KIOSK files(*.kiosk)|*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            open_path = dlg.GetPath()
            self.mainPage.OpenConfiguration(open_path)

    def EditPageOrder(self, event=None):
        dlg = poDlg.PageOrderDialog(self,-1,self.pages,self.base_path)
        if dlg.ShowModal() == wx.ID_OK:
            self.SetSelection(0)
            self.pages = dlg.pages
            while self.GetPageCount() > 2:
                self.RemovePage(1)
            for i in range(1,len(self.pages)):
                self.InsertPage(self.GetPageCount()-1,self.pages[i], self.pages[i].title)

    def ClearNotebook(self):
        # delete all notebook pages
        while self.GetPageCount() > 2:
            self.RemovePage(1)
            del self.pages[1]
        self.activePageNr = 0
        self.mainPage.ResetPage()
        # clear temp data from previously opened/saved kiosk
        home = os.path.expanduser("~")
        appPath = home + '/.usb_kiosk/'
        tmpRoot = appPath + 'tmp/'
        kConfDir = tmpRoot + 'kiosk_config'
        kSaveDir = tmpRoot + 'kiosk_config_save'
        if os.path.isdir(kConfDir):
            shutil.rmtree(kConfDir)
        if os.path.isdir(kSaveDir):
            shutil.rmtree(kSaveDir)


    def OnPageChanged(self, event):
        global HOST_SYS
        # print "ON PAGE CHANGED TRIGGER"
        self.activePageNr = event.GetSelection()
        if HOST_SYS == HOST_LINUX and event.GetOldSelection() == -1:
            pass
        else:
            sel = event.GetSelection()
            if sel < self.GetPageCount() - 1:
                self.LoadPageData(sel)
            else:
                self.AddNewPage()
