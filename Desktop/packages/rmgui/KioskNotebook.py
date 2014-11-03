import packages.rmutil as rmutil
from packages.lang.Localizer import *
import KioskMainPanel as mainPanel
import KioskEditorPanel as editPanel
import KioskPagesPanel as pagesPanel
import PageOrderDialog as poDlg
from packages.rmutil import Logger as logger
import os, sys, platform, ast, time, threading, shutil

import wx
from wx.lib.wordwrap import wordwrap

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
        wx.Notebook.__init__(self, parent, id, style=wx.BK_DEFAULT)
        self.base_path = base_path
        self.parent = parent
        self.pages = []
        self.activePageNr = 0
        self.closed = True
        self.modified = False
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
        self.LoadPagesConfigPage()

    def Close(self):
        from os.path import expanduser
        home = expanduser("~")
        appPath = home + '/.usb_kiosk/'
        tmpPath = appPath + 'tmp/'
        logPath = appPath + 'log/'
        if os.path.isdir(tmpPath):
            shutil.rmtree(tmpPath)
        if os.path.isdir(logPath):
            shutil.rmtree(logPath)
        self.Destroy()

    def UpdatePageName(self, index, oldName, newName):
        # use index -1 because page count wrong by 1 due to "+" tab
        if len(newName) > 11:
            newName = newName[:12] + "..."
        self.SetPageText(index - 1, newName)

    def LoadPageData(self, pageNumber):
        # print "Loading config and remote list for page ", pageNumber
        self.GetPage(pageNumber).LoadData()

    def LoadMainPage(self):
        self.mainPage = mainPanel.KioskMainPanel(self,-1,"Kiosk",0,HOST_SYS,self.base_path)
        self.AddPage(self.mainPage, "Kiosk")

    def LoadPagesConfigPage(self):
        self.configPage = pagesPanel.KioskPagesPanel(self,-1,tr("pages"),self.GetPageCount(),HOST_SYS,self.base_path)
        self.AddPage(self.configPage, tr("pages"))

    def AddNewPage(self, event=None):
        if not self.closed:
            newIndex = len(self.pages)
            newPage = editPanel.KioskEditorPanel(self.configPage,-1,tr("new_page"),newIndex,HOST_SYS,[],[],self.base_path)
            self.pages.append(newPage)
            if HOST_SYS == HOST_WIN:
                self.Hide()
            self.configPage.AddNewPage(newPage)
            self.Show()
            self.modified = True

    def AddKioskPage(self, title, texts, images, customBG, styleJSON):
        page = editPanel.KioskEditorPanel(self.configPage,-1,title,len(self.pages),HOST_SYS,texts,images,self.base_path,customBG,styleJSON)
        self.pages.append(page)
        self.configPage.AddKioskPage(page)
        self.modified = True

    def DeletePage(self, event, index):
        '''
        del self.pages[index]
        self.modified = True
        '''

    def DeleteCurrentPage(self, event):
        '''
        if self.activePageNr > 0 and self.activePageNr < self.GetPageCount() - 1:
            self.DeletePage(event, self.activePageNr)
        '''

    def GetEditorPages(self):
        return self.pages

    def NewConfiguration(self, event=None):
        if not self.closed and self.modified:
            dlg = wx.MessageDialog(self, "Do you want to save your current Kiosk Configuration?", "Save before Closing?", style=wx.YES_NO)
            if dlg.ShowModal() == wx.ID_YES:
                self.notebook.SaveConfiguration()
        self.ClearNotebook()
        self.closed = False
        self.modified = False
        self.Show()

    def SaveConfiguration(self, event=None):
        if not self.closed:
            dlg = wx.FileDialog(self, tr("save_selection"), "", "", "KIOSK files(*.kiosk)|*.kiosk", wx.FD_SAVE)

            if dlg.ShowModal() == wx.ID_OK:
                save_path = dlg.GetPath()
                self.mainPage.SaveConfiguration(save_path)
                self.modified = False

    def OpenConfiguration(self, event=None):
        if not self.closed and self.modified:
            dlg = wx.MessageDialog(self, "Do you want to save your current Kiosk Configuration?", "Save before Closing?", style=wx.YES_NO)
            if dlg.ShowModal() == wx.ID_YES:
                self.notebook.SaveConfiguration()
                self.modified = False
        dlg = wx.FileDialog(self, tr("load_selection"), "", "", "KIOSK files(*.kiosk)|*.kiosk", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            open_path = dlg.GetPath()
            if os.path.isfile(open_path) and open_path.endswith(".kiosk"):
                # clear notebook and temp data
                self.ClearNotebook()
                self.Hide()
                self.mainPage.OpenConfiguration(open_path)
                self.closed = False
                self.modified = False
                self.Show()

    def CloseConfiguration(self, event):
        cancel = False
        if self.modified:
            dlg = wx.MessageDialog(self, "Do you want to save your current Kiosk Configuration?", "Save before Closing?", style=wx.YES_NO|wx.CANCEL)
            result = dlg.ShowModal()
            cancel = (result == wx.ID_CANCEL)
            if result == wx.ID_YES:
                self.SaveConfiguration()
        if not cancel:
            self.ClearNotebook()
            self.closed = True
            self.modified = False
            self.Hide()

    def ImportPages(self, event):
        dlg = wx.FileDialog(self, tr("load_selection"), "", "", "KIOSK files(*.kiosk)|*.kiosk", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            open_path = dlg.GetPath()
            if os.path.isfile(open_path) and open_path.endswith(".kiosk"):
                open_path = dlg.GetPath()
                self.mainPage.ImportPages(open_path)

    def EditPageOrder(self, event=None):
        dlg = poDlg.PageOrderDialog(self,-1,self.pages,self.base_path)
        if dlg.ShowModal() == wx.ID_OK:
            self.configPage.pagesList.Select(0)
            self.pages = dlg.pages
            while self.configPage.pagesList.GetItemCount() > 0:
                self.configPage.pagesList.DeleteItem(0)
            
            for page in self.pages:
                self.configPage.pagesList.InsertStringItem(self.configPage.pagesList.GetItemCount(), page.title)
            
            self.modified = True

    def NumberOfFiles(self):
        total = 0
        # image and text files from pages
        for page in self.pages:
            total += len(page.images) + len(page.texts)
        # song files from main panel
        total += len(self.mainPage.songs)
        return total

    def ClearNotebook(self):
        self.SetSelection(0)
        self.mainPage.ResetPage()
        self.configPage.ResetPage()
        self.pages = []
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
        prevSel = self.activePageNr
        self.activePageNr = event.GetSelection()
        if HOST_SYS == HOST_LINUX and event.GetOldSelection() == -1:
            pass
        else:
            sel = event.GetSelection()
            self.LoadPageData(sel)
            