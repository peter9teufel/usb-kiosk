# -*- coding: utf-8 -*-
import packages.rmutil as rmutil
from packages.rmgui import *
import TextEditDialog as txtDlg
import ScrollableImageView as siv
from packages.lang.Localizer import *
import os, sys, platform, ast, time, threading, shutil, copy, json

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
    def __init__(self,parent,id,title,index,host_sys,texts=[],images=[],base_path="",customBG=None,styleJSON=None):
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
        self.customBG = customBG
        self.imgPath = self.DefaultPath()
        self.style = 0
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.Initialize(styleJSON)


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

    def ImageAdded(self, imgPath):
        #self.images.append(imgPath)
        self.delAll.Enable()

    def ImageDeleted(self, index):
        #del self.images[index]
        if len(self.images) == 0:
            self.delAll.Disable()

    def PageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.parent.GetSelection()
        self.notebook_event = event
        newPage = self.parent.GetPage(new)
        if self.index == newPage.index:
            self.pageDataLoading = True
            self.LoadData()

    def Initialize(self,styleJSON):
        self.mainBox = wx.StaticBox(self,-1,tr("txt_img_box"))
        mainBoxSizer = wx.StaticBoxSizer(self.mainBox, wx.VERTICAL)

        # page name entry
        nameLabel = wx.StaticText(self,-1,label=tr("page_headline"))
        self.nameCtrl = wx.TextCtrl(self,-1,value=self.title,size=(350,22))
        # text definition
        self.addText = wx.Button(self.mainBox,-1,label=tr("add_text"))
        self.addText.SetName('add_txt')
        self.textList = wx.ListCtrl(self.mainBox,-1,size=(150,385),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.textList.SetName('txt_list')
        self.textList.Show(True)
        self.textList.InsertColumn(0,tr("added_texts"), width = 140)
        cnt = 1
        for txt in self.texts:
            label = "Text " + str(cnt)
            self.textList.InsertStringItem(self.textList.GetItemCount(), label)
            cnt += 1;

        # image definition
        self.addImg = wx.Button(self.mainBox,-1,label=tr("add_image"))
        self.delAll = wx.Button(self.mainBox, -1, label=tr("delete_all"))
        self.delAll.Disable()
        self.imgPreview = siv.ScrollableImageView(self.mainBox,-1,size=(260,385),images=self.images,dataSource=self)
        for img in self.images:
            self.imgPreview.AddImage(img,addToList=False)

        # ticker setup
        tickerBox = wx.StaticBox(self,-1,tr("ticker_setup"))
        tickerBoxSizer = wx.StaticBoxSizer(tickerBox, wx.VERTICAL)
        tickerLabel = wx.StaticText(tickerBox,-1,label=tr("custom_ticker_text")+":")
        self.tickerTxtCtrl = wx.TextCtrl(tickerBox,-1,size=(250,22))
        self.tickerEnabledChk = wx.CheckBox(tickerBox,-1,label=tr("ticker_enabled"))
        self.tickerMovingChk = wx.CheckBox(tickerBox,-1,label=tr("ticker_moving"))
        self.tickerEnabledChk.SetValue(True)
        self.tickerMovingChk.SetValue(True)
        tickerTxtSizer = wx.BoxSizer()

        tickerTxtSizer.Add(tickerLabel)
        tickerTxtSizer.Add(self.tickerTxtCtrl)

        tickerBoxSizer.Add(tickerTxtSizer)
        tickerBoxSizer.Add(self.tickerEnabledChk)
        tickerBoxSizer.Add(self.tickerMovingChk)

        # style setup
        styleBox = wx.StaticBox(self,-1,tr("site_style"))
        styleBoxSizer = wx.StaticBoxSizer(styleBox)
        emptyImg = wx.EmptyImage(250,200)
        self.prevStyle = wx.Button(styleBox,-1,label="<",size=(25,25))
        self.stylePreview = wx.StaticBitmap(styleBox, wx.ID_ANY, wx.BitmapFromImage(emptyImg))
        self.nextStyle = wx.Button(styleBox,-1,label=">",size=(25,25))
        self.style = 0
        self.SetStylePreview()

        styleBoxSizer.Add(self.prevStyle,flag=wx.ALIGN_CENTER_VERTICAL)
        styleBoxSizer.Add(self.stylePreview,flag=wx.ALIGN_CENTER_VERTICAL)
        styleBoxSizer.Add(self.nextStyle,flag=wx.ALIGN_CENTER_VERTICAL)

        # custom page background setup
        bgBox = wx.StaticBox(self,-1,tr("custom_bg"))
        self.bgBoxSizer = wx.StaticBoxSizer(bgBox)
        bgBoxLeftSizer = wx.BoxSizer(wx.VERTICAL)

        self.customBgChk = wx.CheckBox(bgBox,-1,label=tr("custom_bg_enabled"))
        self.selectCustomBg = wx.Button(bgBox,-1,label=tr("custom_bg_select"))
        emptyBg = wx.EmptyImage(160,110)
        self.customBgCtrl = wx.StaticBitmap(bgBox,wx.ID_ANY, wx.BitmapFromImage(emptyBg))
        if not self.customBG == None:
            self.__SetBGPreview(self.customBG)

        bgBoxLeftSizer.Add(self.customBgChk)
        bgBoxLeftSizer.Add(self.selectCustomBg)

        self.bgBoxSizer.Add(bgBoxLeftSizer)
        self.bgBoxSizer.Add(self.customBgCtrl,flag=wx.LEFT|wx.RIGHT, border=10)

        # preview Button
        preview = wx.Button(self,-1,label=tr("preview"))

        # bind elements
        self.nameCtrl.Bind(wx.EVT_TEXT, self.UpdatePageName)
        self.addText.Bind(wx.EVT_BUTTON, self.ShowTextEdit)
        self.textList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.ShowTextEdit)
        self.textList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.TextItemRightClicked)
        self.addImg.Bind(wx.EVT_BUTTON, self.ShowImageSelection)
        self.delAll.Bind(wx.EVT_BUTTON, self.imgPreview.ClearImageView)
        preview.Bind(wx.EVT_BUTTON, self.PreviewClicked)

        self.nextStyle.Bind(wx.EVT_BUTTON, self.NextStyle)
        self.prevStyle.Bind(wx.EVT_BUTTON, self.PrevStyle)

        self.customBgChk.Bind(wx.EVT_CHECKBOX, self.CustomBgEnabledToggled)
        self.CustomBgEnabledToggled(None)
        self.selectCustomBg.Bind(wx.EVT_BUTTON, self.ShowBackgroundSelection)

        # create sizers, add content and add to main sizer
        contentSizer = wx.BoxSizer()
        txtSizer = wx.BoxSizer(wx.VERTICAL)
        txtSizer.Add(self.addText,flag=wx.TOP|wx.LEFT,border=5)
        txtSizer.Add(self.textList,flag=wx.TOP|wx.LEFT,border=5)
        imgSizer = wx.BoxSizer(wx.VERTICAL)
        imgBtnSizer = wx.BoxSizer()
        imgBtnSizer.Add(self.addImg)
        imgBtnSizer.Add(self.delAll)
        imgSizer.Add(imgBtnSizer, flag=wx.TOP|wx.LEFT,border=5)
        imgSizer.Add(self.imgPreview,flag=wx.TOP|wx.LEFT,border=5)

        contentSizer.Add(txtSizer)
        contentSizer.Add(imgSizer,flag=wx.LEFT,border=30)

        headlineSizer = wx.BoxSizer()
        headlineSizer.Add(nameLabel, flag=wx.LEFT|wx.TOP, border=5)
        headlineSizer.Add(self.nameCtrl,flag=wx.LEFT|wx.RIGHT,border=5)



        #mainBoxSizer.Add(headlineSizer,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.TOP, border = 10)
        mainBoxSizer.Add(contentSizer,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT|wx.BOTTOM, border=10)
        #mainBoxSizer.Add(preview,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,border=5)

        mainContentSizer = wx.BoxSizer()
        leftContentSizer = wx.BoxSizer(wx.VERTICAL)
        rightContentSizer = wx.BoxSizer(wx.VERTICAL)

        leftContentSizer.Add(mainBoxSizer,flag=wx.TOP|wx.ALIGN_CENTER_HORIZONTAL,border=20)

        rightContentSizer.Add(tickerBoxSizer,flag=wx.TOP,border=20)
        rightContentSizer.Add(styleBoxSizer)
        rightContentSizer.Add(self.bgBoxSizer)

        mainContentSizer.Add(leftContentSizer)
        mainContentSizer.Add(rightContentSizer)

        self.mainSizer.Add(headlineSizer,flag=wx.TOP, border = 10)
        self.mainSizer.Add(mainContentSizer)
        self.mainSizer.Add(preview,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,border=5)

        # load style info from style JSON if available
        if not styleJSON == None:
            if 'ticker_text' in styleJSON:
                self.tickerTxtCtrl.SetValue(str(styleJSON['ticker_text']))
            if 'ticker_enabled' in styleJSON:
                self.tickerEnabledChk.SetValue(int(styleJSON['ticker_enabled']))
            if 'ticker_moving' in styleJSON:
                self.tickerMovingChk.SetValue(int(styleJSON['ticker_moving']))
            if 'custom_bg' in styleJSON:
                self.customBgChk.SetValue(int(styleJSON['custom_bg']))
            if 'style' in styleJSON:
                self.style = int(styleJSON['style'])
                self.SetStylePreview()
                self.SetUIForStyle()

        self.SetSizer(self.mainSizer)
        #self.LayoutAndFit()
        self.Show(True)

    def GetStyleJSONDefinition(self):
        # {"style": 1, "img_mode": "image_fit", "ticker_text": "grafenwoerth.senecura.at", "ticker_moving": "0", "custom_bg": "page1/nature.jpg"}
        style = {}
        style['style'] = self.style
        if len(self.tickerTxtCtrl.GetValue()) > 0:
            style['ticker_text'] = self.tickerTxtCtrl.GetValue()
        if self.tickerEnabledChk.IsChecked():
            style['ticker_enabled'] = "1"
        else:
            style['ticker_enabled'] = "0"
        if self.tickerMovingChk.IsChecked():
            style['ticker_moving'] = "1"
        else:
            style['ticker_moving'] = "0"
        if self.customBgChk.IsChecked() and not self.customBG == None:
            style['custom_bg'] = "1"
        else:
            style['custom_bg'] = "0"
        return json.dumps(style)

    def NextStyle(self, event):
        self.style += 1
        self.SetStylePreview()
        self.SetUIForStyle()

    def PrevStyle(self, event):
        self.style -= 1
        self.SetStylePreview()
        self.SetUIForStyle()

    def SetUIForStyle(self):
        if self.style == 0:
            self.ToggleTextInputs(True)
            self.addImg.Enable()
        elif self.style == 1:
            self.ToggleTextInputs(True)
            self.addImg.Enable()
        elif self.style == 2:
            # double image style
            self.ToggleTextInputs(False)
            self.addImg.Enable()
        elif self.style == 3:
            # text only style
            self.addImg.Disable()
            self.ToggleTextInputs(True)
        elif self.style == 4:
            # single image style
            self.addImg.Enable()
            self.ToggleTextInputs(False)
        elif self.style == 5:
            # single image fullscreen style
            self.addImg.Enable()
            self.ToggleTextInputs(False)
            pass

    def ToggleTextInputs(self, enabled):
        if enabled:
            self.addText.Enable()
            self.textList.Enable()
        else:
            self.addText.Disable()
            self.textList.Disable()

    def SetStylePreview(self):
        if self.style == 5:
            self.nextStyle.Disable()
        elif self.style == 0:
            self.prevStyle.Disable()
        else:
            self.prevStyle.Enable()
            self.nextStyle.Enable()

        path = resource_path("img/style"+str(self.style)+".png")
        img = wx.Image(path)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()

        maxSize = 340

        if W > H:
            NewW = maxSize
            NewH = maxSize * H / W
        else:
            NewH = maxSize
            NewW = maxSize * W / H
        img = img.Scale(NewW,NewH,quality=wx.IMAGE_QUALITY_HIGH)

        self.stylePreview.SetBitmap(wx.BitmapFromImage(img))

    def CustomBgEnabledToggled(self, event):
        if self.customBgChk.IsChecked():
            self.selectCustomBg.Enable()
            self.customBgCtrl.Enable()
        else:
            self.selectCustomBg.Disable()
            self.customBgCtrl.Disable()

    def __SetBGPreview(self, imagePath):
        img = wx.Image(imagePath)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()

        NewW = 190
        NewH = 190 * H / W
        
        img = img.Scale(NewW,NewH,quality=wx.IMAGE_QUALITY_HIGH)

        self.customBgCtrl.SetBitmap(wx.BitmapFromImage(img))
        self.mainSizer.Layout()

    def ShowBackgroundSelection(self, event=None):
        dlg = imagebrowser.ImageDialog(None,self.imgPath)

        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetFile()
            self.__SetBGPreview(file)
            self.customBG = file
            # save image path of previed image
            head, tail = os.path.split(file)
            self.imgPath = head
        if HOST_SYS == HOST_WIN:
            dlg.Destroy()

    def LayoutAndFit(self):
        self.mainSizer.Layout()
        self.Fit()
        self.parent.Fit()
        self.parent.parent.Fit()
        self.parent.parent.parent.Fit()
        #self.parent.parent.parent.Center()

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
            #self.images.append(file)
            self.imgPreview.AddImage(file)
            #self.delAll.Enable()
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

        webbrowser.open(url)

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
