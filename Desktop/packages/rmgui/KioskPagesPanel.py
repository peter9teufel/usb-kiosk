import packages.rmutil as util
from packages.rmgui import *
from packages.lang.Localizer import *
import os, sys, platform, ast, time, threading, shutil, copy, zipfile
from os.path import expanduser
from PIL import Image

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
# KIOSK PAGES PANEL ############################################################
################################################################################
class KioskPagesPanel(wx.Panel):
    def __init__(self,parent,id,title,index,host_sys,base_path):
        #wx.Panel.__init__(self,parent,id,title)
        wx.Panel.__init__(self,parent,-1)
        global HOST_SYS, BASE_PATH
        HOST_SYS = host_sys
        BASE_PATH = base_path
        self.parent = parent
        self.index = index
        self.curPage = None
        self.mainSizer = wx.BoxSizer()
        self.imgPath = self.DefaultPath()
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

        self.pagesBox = wx.StaticBox(self,-1,tr("pages"))
        pagesSizer = wx.StaticBoxSizer(self.pagesBox, wx.VERTICAL)

        self.pagesList = wx.ListCtrl(self.pagesBox, -1, size=(220,520), style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.pagesList.InsertColumn(0,tr("pages"), width=210)

        self.pagesList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.PageItemRightClicked)

        addPage = wx.Button(self.pagesBox,-1,label=tr("add_page"))
        addPage.Bind(wx.EVT_BUTTON, self.parent.AddNewPage)

        pagesSizer.Add(self.pagesList)
        pagesSizer.Add(addPage)

        self.setupBox = wx.StaticBox(self,-1,tr("setup"))
        self.setupSizer = wx.StaticBoxSizer(self.setupBox)
        self.setupBox.Hide()

        # BIND ELEMENTS
        self.pagesList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.PageSelected)

        self.mainSizer.Add(pagesSizer)
        self.mainSizer.Add(self.setupSizer)
        self.SetSizer(self.mainSizer)

    def PageSelected(self, event=None):
        sel = self.pagesList.GetFirstSelected()
        page = self.parent.pages[sel]
        self.SetPage(page)

    def AddNewPage(self, page):
        if self.pagesList.GetItemCount() == 0:
            self.setupBox.Show()
        self.pagesList.InsertStringItem(self.pagesList.GetItemCount(), page.title)
        index = self.pagesList.GetFirstSelected()
        while index != -1:
            self.pagesList.Select(index,0)
            index = self.pagesList.GetFirstSelected()
        self.pagesList.Select(page.index)

    def UpdatePageName(self, index, oldName, newName):
        self.pagesList.SetItemText(index, newName)

    def SetPage(self, page):
        if not self.curPage == None:
            self.setupSizer.Detach(self.curPage)
            self.curPage.Hide()
        self.setupSizer.Add(page)
        self.curPage = page
        self.curPage.Show()
        self.mainSizer.Layout()
        self.setupSizer.Layout()
        self.LayoutAndFit()

    def AddKioskPage(self, page):
        if self.pagesList.GetItemCount() == 0:
            self.setupBox.Show()
        self.pagesList.InsertStringItem(self.pagesList.GetItemCount(), page.title)
        page.Hide()

    def ResetPage(self):
        if not self.curPage == None:
            self.setupSizer.Detach(self.curPage)
            self.curPage.Hide()
            self.curPage = None
        self.pagesList.DeleteAllItems()

    def PageItemRightClicked(self, event):
        global HOST_SYS
        file = event.GetText()
        menu = wx.Menu()
        item = menu.Append(wx.NewId(), tr("delete"))
        self.Bind(wx.EVT_MENU, self.DeleteSelectedPageItem, item)

        boxRect = self.pagesBox.GetRect()
        rect = self.pagesList.GetRect()
        origin = (boxRect[0]+rect[0],boxRect[1]+rect[1])
        point = event.GetPoint()
        if HOST_SYS == HOST_WIN:
            self.PopupMenu(menu, (origin[0]+point[0]+10,origin[1]+point[1]+15))
        else:
            self.PopupMenu(menu, (origin[0]+point[0]+10,origin[1]+point[1]+45))
        menu.Destroy()

    def DeleteSelectedPageItem(self, event=None):
        index = self.pagesList.GetFirstSelected()
        if index == self.pagesList.GetItemCount() -1:
            targetIndex = index - 1
        else:
            targetIndex = index
        while self.pagesList.GetItemCount() > 0:
            self.pagesList.DeleteItem(0)
        del self.parent.pages[index]

        for page in self.parent.pages:
            self.pagesList.InsertStringItem(self.pagesList.GetItemCount(), page.title)
        self.parent.modified = True
        if self.pagesList.GetItemCount() > 0:
            self.pagesList.Select(targetIndex)
        else:
            self.setupBox.Hide()

    def LayoutAndFit(self):
        self.mainSizer.Layout()
        self.Fit()
        self.parent.Fit()
        self.parent.parent.Fit()

    
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
