import packages.rmutil as rmutil
from packages.rmgui import *
import TextEditDialog as txtDlg
import ScrollableImageView as siv
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
class KioskEditorPanel(wx.Panel):
    def __init__(self,parent,id,title,index,host_sys):
        #wx.Panel.__init__(self,parent,id,title)
        wx.Panel.__init__(self,parent,-1)
        global HOST_SYS, BASE_PATH
        HOST_SYS = host_sys
        BASE_PATH = parent.parent.base_path
        self.title = title
        self.parent = parent
        self.index = index
        self.texts = {}
        self.images = []
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
        # page name entry
        nameLabel = wx.StaticText(self,-1,label="Page Headline:")
        self.nameCtrl = wx.TextCtrl(self,-1,value=self.title,size=(350,22))
        # text definition
        addText = wx.Button(self,-1,label="Add Text")
        addText.SetName('add_txt')
        self.textList = wx.ListCtrl(self,-1,size=(200,350),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.textList.SetName('txt_list')
        self.textList.Show(True)
        self.textList.InsertColumn(0,"Added texts", width = 180)

        # image definition
        addImg = wx.Button(self,-1,label="Add Image")
        self.imgPreview = siv.ScrollableImageView(self,-1,size=(300,350),images=[],cols=1)

        # preview Button
        preview = wx.Button(self,-1,label="Preview")

        # bind elements TODO!
        addText.Bind(wx.EVT_BUTTON, self.ShowTextEdit)
        self.textList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.ShowTextEdit)
        addImg.Bind(wx.EVT_BUTTON, self.ShowImageSelection)

        # create sizers, add content and add to main sizer
        contentSizer = wx.BoxSizer()
        txtSizer = wx.BoxSizer(wx.VERTICAL)
        txtSizer.Add(addText,flag=wx.TOP|wx.LEFT,border=5)
        txtSizer.Add(self.textList,flag=wx.TOP|wx.LEFT,border=5)
        imgSizer = wx.BoxSizer(wx.VERTICAL)
        imgSizer.Add(addImg,flag=wx.TOP|wx.LEFT,border=5)
        imgSizer.Add(self.imgPreview,flag=wx.TOP|wx.LEFT,border=5)

        contentSizer.Add(txtSizer)
        contentSizer.Add(imgSizer,flag=wx.LEFT,border=30)

        self.mainSizer.Add(nameLabel, flag=wx.LEFT|wx.TOP, border=5)
        self.mainSizer.Add(self.nameCtrl,flag=wx.LEFT|wx.RIGHT|wx.BOTTOM,border=5)
        self.mainSizer.Add(contentSizer,flag=wx.TOP,border=20)
        self.mainSizer.Add(preview,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALL,border=5)

        self.SetSizerAndFit(self.mainSizer)

        #self.LayoutAndFit()
        self.Show(True)


    def LayoutAndFit(self):
        self.mainSizer.Layout()
        self.Fit()
        self.parent.Fit()
        self.parent.parent.Fit()
        self.parent.parent.Center()

    def ShowTextEdit(self, event):
        if event.GetEventObject().GetName() == 'add_txt':
            dlg = txtDlg.TextEditDialog(self,-1,"Enter Text")
            if dlg.ShowModal() == wx.ID_OK:
                cnt = len(self.texts)+1
                label = "Text " + str(cnt)
                self.texts[label] = dlg.text
                self.textList.InsertStringItem(self.textList.GetItemCount(), label)
            if HOST_SYS == HOST_WIN:
                dlg.Destroy()
        elif event.GetEventObject().GetName() == 'txt_list':
            label = event.GetText()
            txt = self.texts[label]
            dlg = txtDlg.TextEditDialog(self,-1,label,txt)
            if dlg.ShowModal() == wx.ID_OK:
                self.texts[label] = dlg.text
            if HOST_SYS == HOST_WIN:
                dlg.Destroy()

    def ShowImageSelection(self, event=None):
        dlg = imagebrowser.ImageDialog(None)

        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetFile()
            self.images.append(file)
            self.imgPreview.AddImage(file)
            print "IMAGES:"
            print self.images
        if HOST_SYS == HOST_WIN:
            dlg.Destroy()


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
