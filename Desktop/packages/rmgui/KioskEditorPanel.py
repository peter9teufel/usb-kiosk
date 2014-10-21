# -*- coding: utf-8 -*-
import packages.rmutil as rmutil
from packages.rmgui import *
import TextEditDialog as txtDlg
import ScrollableImageView as siv
from packages.lang.Localizer import *
import os, sys, platform, ast, time, threading, shutil, copy

import webbrowser
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
    def __init__(self,parent,id,title,index,host_sys,texts=[],images=[],base_path=""):
        #wx.Panel.__init__(self,parent,id,title)
        wx.Panel.__init__(self,parent,-1)
        global HOST_SYS, BASE_PATH
        HOST_SYS = host_sys
        BASE_PATH = base_path
        self.title = title
        self.parent = parent
        self.index = index
        self.texts = texts
        self.images = images
        self.imgPath = self.DefaultPath()
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
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

    def ImageDeleted(self, index):
        del self.images[index]

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

        self.mainBox = wx.StaticBox(self,-1,tr("txt_img_box"))
        mainBoxSizer = wx.StaticBoxSizer(self.mainBox, wx.VERTICAL)

        # page name entry
        nameLabel = wx.StaticText(self,-1,label=tr("page_headline"))
        self.nameCtrl = wx.TextCtrl(self,-1,value=self.title,size=(350,22))
        # text definition
        addText = wx.Button(self.mainBox,-1,label=tr("add_text"))
        addText.SetName('add_txt')
        self.textList = wx.ListCtrl(self.mainBox,-1,size=(200,350),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.textList.SetName('txt_list')
        self.textList.Show(True)
        self.textList.InsertColumn(0,tr("added_texts"), width = 180)
        cnt = 1
        for txt in self.texts:
            label = "Text " + str(cnt)
            self.textList.InsertStringItem(self.textList.GetItemCount(), label)
            cnt += 1;

        # image definition
        addImg = wx.Button(self.mainBox,-1,label=tr("add_image"))
        self.imgPreview = siv.ScrollableImageView(self.mainBox,-1,size=(300,350),images=[],dataSource=self,cols=1)
        for img in self.images:
            self.imgPreview.AddImage(img)

        # preview Button
        preview = wx.Button(self,-1,label=tr("preview"))

        # bind elements
        self.nameCtrl.Bind(wx.EVT_TEXT, self.UpdatePageName)
        addText.Bind(wx.EVT_BUTTON, self.ShowTextEdit)
        self.textList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.ShowTextEdit)
        self.textList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.TextItemRightClicked)
        addImg.Bind(wx.EVT_BUTTON, self.ShowImageSelection)
        preview.Bind(wx.EVT_BUTTON, self.PreviewClicked)

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

        headlineSizer = wx.BoxSizer()
        headlineSizer.Add(nameLabel, flag=wx.LEFT|wx.TOP, border=5)
        headlineSizer.Add(self.nameCtrl,flag=wx.LEFT|wx.RIGHT,border=5)



        #mainBoxSizer.Add(headlineSizer,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.TOP, border = 10)
        mainBoxSizer.Add(contentSizer,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT|wx.BOTTOM, border=10)
        #mainBoxSizer.Add(preview,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,border=5)

        self.mainSizer.Add(headlineSizer,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.TOP, border = 10)
        #self.mainSizer.Add(contentSizer,flag=wx.TOP|wx.ALIGN_CENTER_HORIZONTAL,border=20)
        self.mainSizer.Add(mainBoxSizer,flag=wx.TOP|wx.ALIGN_CENTER_HORIZONTAL,border=20)
        self.mainSizer.Add(preview,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,border=5)

        self.SetSizerAndFit(self.mainSizer)
        #self.LayoutAndFit()
        self.Show(True)


    def LayoutAndFit(self):
        self.mainSizer.Layout()
        self.Fit()
        self.parent.Fit()
        self.parent.parent.Fit()
        self.parent.parent.Center()

    def UpdatePageName(self, event=None):
        oldName = self.title
        newName = self.nameCtrl.GetValue()
        self.parent.UpdatePageName(self.index, oldName, newName)
        self.title = newName
        self.parent.modified = True

    def TextItemRightClicked(self, event):
        global HOST_SYS
        file = event.GetText()
        menu = wx.Menu()
        item = menu.Append(wx.NewId(), tr("delete"))
        self.Bind(wx.EVT_MENU, self.DeleteSelectedTextItem, item)

        boxRect = self.mainBox.GetRect()
        rect = self.textList.GetRect()

        origin = (boxRect[0]+rect[0],boxRect[1]+rect[1])
        point = event.GetPoint()
        if HOST_SYS == HOST_WIN:
            self.PopupMenu(menu, (origin[0]+point[0]+10,origin[1]+point[1]+15))
        else:
            self.PopupMenu(menu, (origin[0]+point[0]+10,origin[1]+point[1]+45))
        menu.Destroy()

    def DeleteSelectedTextItem(self, event=None):
        index = self.textList.GetFirstSelected()
        while self.textList.GetItemCount() > 0:
            self.textList.DeleteItem(0)
        del self.texts[index]
        cnt = 1
        for txt in self.texts:
            label = "Text " + str(cnt)
            self.textList.InsertStringItem(self.textList.GetItemCount(), label)
            cnt += 1;
        self.parent.modified = True

    def ShowTextEdit(self, event):
        if event.GetEventObject().GetName() == 'add_txt':
            dlg = txtDlg.TextEditDialog(self,-1,tr("enter_text"))
            if dlg.ShowModal() == wx.ID_OK:
                cnt = len(self.texts)+1
                label = "Text " + str(cnt)
                self.texts.append(dlg.text)
                self.textList.InsertStringItem(self.textList.GetItemCount(), label)
                self.parent.modified = True
            if HOST_SYS == HOST_WIN:
                dlg.Destroy()
        elif event.GetEventObject().GetName() == 'txt_list':
            label = event.GetText()
            index = self.textList.GetFirstSelected()
            txt = self.texts[index]
            dlg = txtDlg.TextEditDialog(self,-1,label,txt)
            if dlg.ShowModal() == wx.ID_OK:
                if self.texts[index] != dlg.text:
                    self.texts[index] = dlg.text
                    self.parent.modified = True
            if HOST_SYS == HOST_WIN:
                dlg.Destroy()

    def ShowImageSelection(self, event=None):
        dlg = imagebrowser.ImageDialog(None,self.imgPath)

        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetFile()
            self.images.append(file)
            self.imgPreview.AddImage(file)
            head, tail = os.path.split(file)
            self.imgPath = head
        if HOST_SYS == HOST_WIN:
            dlg.Destroy()

    def PreviewClicked(self, event):
        name = self.title.encode("utf-8")
        url = "http://bit.do/raspkiosk_preview?NAME=" + name
        if len(self.texts) > 0:
            txts = ""
            for i in range(len(self.texts)):
                txts += self.texts[i].encode("utf-8")
                if i < len(self.texts) - 1:
                    txts += ";"
            url += "&TXTS=" + txts
        if len(self.images) > 0:
            url += "&IMG=1"
        else:
            url += "&IMG=0"
        webbrowser.open(url.decode('utf-8'))

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
