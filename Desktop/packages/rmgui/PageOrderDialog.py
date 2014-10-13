import wx
import os, sys, platform
from wx.lib.wordwrap import wordwrap
from packages.lang.Localizer import *

BASE_PATH = ""

################################################################################
# DIALOG FOR PAGE ORDER EDITING ################################################
################################################################################
class PageOrderDialog(wx.Dialog):
    def __init__(self,parent,id,pages,base_path):
        wx.Dialog.__init__(self,parent,id,tr("edit_page_order"))
        global BASE_PATH
        BASE_PATH = base_path
        self.parent = parent
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.pages = pages
        self.__InitUI()
        self.ValidateSelection()
        self.SetSizerAndFit(self.mainSizer)
        self.Center()

    def __InitUI(self):
        self.list = wx.ListCtrl(self,-1,size=(300,200),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.list.Show(True)
        self.list.InsertColumn(0,"Page Name", width = 290)

        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.ValidateSelection)
        self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.ValidateSelection)

        self.UpdateList()

        upImg = wx.Image(resource_path("img/ic_up.png"), wx.BITMAP_TYPE_PNG).Rescale(20,20,wx.IMAGE_QUALITY_HIGH)
        downImg = wx.Image(resource_path("img/ic_down.png"), wx.BITMAP_TYPE_PNG).Rescale(20,20,wx.IMAGE_QUALITY_HIGH)
        upBmp = upImg.ConvertToBitmap()
        downBmp = downImg.ConvertToBitmap()

        self.moveUp = wx.BitmapButton(self,-1,upBmp,pos=(0,0))
        self.moveDown = wx.BitmapButton(self,-1,downBmp,pos=(0,0))
        #moveUp = wx.Button(self,-1,"Move Up")
        #moveDown = wx.Button(self,-1,"Move Down")
        self.moveUp.Bind(wx.EVT_BUTTON, self.MoveSelectedItemUp)
        self.moveDown.Bind(wx.EVT_BUTTON, self.MoveSelectedItemDown)

        ok = wx.Button(self,wx.ID_OK,label="OK")
        cancel = wx.Button(self,wx.ID_CANCEL,label=tr("cancel"))

        ok.Bind(wx.EVT_BUTTON, self.okClicked)
        cancel.Bind(wx.EVT_BUTTON, self.cancelClicked)

        moveSizer = wx.BoxSizer(wx.VERTICAL)
        moveSizer.Add(self.moveUp,flag=wx.ALIGN_CENTER_VERTICAL)
        moveSizer.Add(self.moveDown,flag=wx.ALIGN_CENTER_VERTICAL)

        contentSizer = wx.BoxSizer()
        contentSizer.Add(self.list)
        contentSizer.Add(moveSizer,flag=wx.ALIGN_CENTER_VERTICAL)

        btnSizer = wx.BoxSizer()
        btnSizer.Add(cancel)
        btnSizer.Add(ok)
        self.mainSizer.Add(contentSizer,flag=wx.ALL,border=10)
        self.mainSizer.Add(btnSizer,flag=wx.ALIGN_RIGHT|wx.ALL,border=10)

    def ValidateSelection(self, event=None):
        if not self.list.GetFirstSelected() == -1:
            self.moveUp.Enable()
            self.moveDown.Enable()
        else:
            self.moveUp.Disable()
            self.moveDown.Disable()

    def MoveSelectedItemDown(self, event=None):
        oldIndex = self.list.GetFirstSelected()
        if not oldIndex == -1:
            if oldIndex == self.list.GetItemCount() - 1:
                newIndex = 0
            else:
                newIndex = oldIndex + 1
            self.pages.insert(newIndex + 1, self.pages.pop(oldIndex + 1))
            self.UpdateList(select=newIndex)

    def MoveSelectedItemUp(self, event=None):
        oldIndex = self.list.GetFirstSelected()
        if not oldIndex == -1:
            if oldIndex == 0:
                newIndex = self.list.GetItemCount() - 1
            else:
                newIndex = oldIndex - 1
            self.pages.insert(newIndex + 1, self.pages.pop(oldIndex + 1))
            self.UpdateList(select=newIndex)

    def UpdateList(self, select=-1):
        while self.list.GetItemCount() > 0:
            self.list.DeleteItem(0)
        for i in range(1,len(self.pages)):
            self.list.InsertStringItem(self.list.GetItemCount(), self.pages[i].title)
        if not select == -1:
            self.list.Select(select)

    def okClicked(self, event):
        self.EndModal(wx.ID_OK)
        self.Destroy()

    def cancelClicked(self, event):
        self.EndModal(wx.ID_CANCEL)
        self.Destroy()

# HELPER METHOD to get correct resource path for image file
def resource_path(relative_path):
    global BASE_PATH
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        #print "BASE PATH FOUND: "+ base_path
    except Exception:
        #print "BASE PATH NOT FOUND!"
        base_path = BASE_PATH
    #print "JOINING " + base_path + " WITH " + relative_path
    resPath = os.path.normcase(os.path.join(base_path, relative_path))
    #resPath = base_path + relative_path
    #print resPath
    return resPath
