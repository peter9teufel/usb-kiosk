import packages.rmutil as rmutil
from packages.lang.Localizer import *
import KioskMainPanel as mainPanel
import KioskEditorPanel as editPanel
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

        wx.EVT_RIGHT_DOWN(self , self.OnNotebookRightClick)

        self.mainPage = None
        self.LoadMainPage()
        self.LoadPlusTab()

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
                page = self.GetPage(index)
                menu = wx.Menu()
                item = menu.Append(wx.NewId(), tr("delete"))
                #self.Bind(wx.EVT_MENU, self.DeleteSelectedTextItem, item)
                self.Bind(wx.EVT_MENU, lambda event, index=index: self.DeletePage(event,index), item)
                rect = self.GetRect()
                point = event.GetPosition()
                self.PopupMenu(menu, (rect[0]+point[0]+10,rect[1]+point[1]+10))
                menu.Destroy()

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
        self.pages.append(self.mainPage)
        self.AddPage(self.mainPage, "Kiosk")

    def LoadPlusTab(self):
        self.plusTab = wx.Panel(self,-1)
        self.AddPage(self.plusTab, "+")

    def AddNewPage(self, event=None):
        newIndex = self.GetPageCount()
        newPage = editPanel.KioskEditorPanel(self,-1,tr("new_page"),newIndex,HOST_SYS,[],[],self.base_path)
        self.pages.append(newPage)
        if HOST_SYS == HOST_WIN:
            self.Hide()
        self.InsertPage(self.GetPageCount()-1,newPage, tr("new_page"),select=True)
        self.Show()
        self.modified = True

    def AddKioskPage(self, title, texts, images):
        page = editPanel.KioskEditorPanel(self,-1,title,self.GetPageCount(),HOST_SYS,texts,images,self.base_path)
        self.pages.append(page)
        tabTitle = title
        if len(tabTitle) > 11:
            tabTitle = tabTitle[:12] + "..."
        self.InsertPage(self.GetPageCount()-1,page, tabTitle)
        self.modified = True

    def DeletePage(self, event, index):
        targetIndex = 0
        if self.activePageNr == index:
            if self.activePageNr < self.GetPageCount() - 2:
                targetIndex = index
            else:
                targetIndex = index - 1
            self.SetSelection(targetIndex)
        #elif self.activePageNr > index:
            #targetIndex = self.activePageNr - 1
        #self.SetSelection(0)
        self.RemovePage(index)
        del self.pages[index]
        if targetIndex != self.activePageNr:
            self.SetSelection(targetIndex)
        self.modified = True

    def DeleteCurrentPage(self, event):
        if self.activePageNr > 0 and self.activePageNr < self.GetPageCount() - 1:
            self.DeletePage(event, self.activePageNr)

    def GetEditorPages(self):
        return self.pages[1:]

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

    def OpenConfiguration(self, event=None):
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
        if self.modified:
            dlg = wx.MessageDialog(self, "Do you want to save your current Kiosk Configuration?", "Save before Closing?", style=wx.YES_NO)
            if dlg.ShowModal() == wx.ID_YES:
                self.notebook.SaveConfiguration()
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
            self.SetSelection(0)
            changed = False
            for i in range(len(self.pages)):
                if dlg.pages[i].index != self.pages[i].index:
                    changed = True
            if changed:
                self.pages = dlg.pages
                while self.GetPageCount() > 2:
                    self.RemovePage(1)
                for i in range(1,len(self.pages)):
                    page = self.pages[i]
                    page.index = i+1
                    tabTitle = page.title
                    if len(tabTitle) > 11:
                        tabTitle = tabTitle[:12] + "..."
                    self.InsertPage(self.GetPageCount()-1, page, tabTitle)
                self.modified = True

    def NumberOfFiles(self):
        total = 0
        # image and text files from pages
        for i in range(1,len(self.pages)):
            page = self.pages[i]
            total += len(page.images) + len(page.texts)
        # song files from main panel
        total += len(self.pages[0].songs)
        return total

    def ClearNotebook(self):
        self.SetSelection(0)
        # delete all notebook pages
        while self.GetPageCount() > 2:
            self.RemovePage(1)
            del self.pages[1]
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

    def SwitchTab(self, event):
        targetIndex = 0
        if self.activePageNr < self.GetPageCount() -2:
            targetIndex = self.activePageNr + 1
        self.SetSelection(targetIndex)

    def OnPageChanged(self, event):
        global HOST_SYS
        prevSel = self.activePageNr
        self.activePageNr = event.GetSelection()
        if HOST_SYS == HOST_LINUX and event.GetOldSelection() == -1:
            pass
        else:
            sel = event.GetSelection()
            if sel < self.GetPageCount() - 1:
                self.LoadPageData(sel)
            else:
                self.AddNewPage()
