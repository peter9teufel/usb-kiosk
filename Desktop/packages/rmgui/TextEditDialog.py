import wx
import sys
from packages.lang.Localizer import *

################################################################################
# DIALOG FOR TEXT EDITING ######################################################
################################################################################
class TextEditDialog(wx.Dialog):
    def __init__(self,parent,id,title,text=""):
        wx.Dialog.__init__(self,parent,id,title)
        self.parent = parent
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.text = text

        self.__InitUI()
        self.SetSizerAndFit(self.mainSizer)
        self.Center()

    def __InitUI(self):
        self.textCtrl = wx.TextCtrl(self,-1,size=(400,300),style=wx.TE_MULTILINE,value=self.text)
        ok = wx.Button(self,wx.ID_OK,label="OK")
        cancel = wx.Button(self,wx.ID_CANCEL,label=tr("cancel"))

        ok.Bind(wx.EVT_BUTTON, self.okClicked)
        cancel.Bind(wx.EVT_BUTTON, self.cancelClicked)

        btnSizer = wx.BoxSizer()
        btnSizer.Add(cancel)
        btnSizer.Add(ok)
        self.mainSizer.Add(self.textCtrl,flag=wx.ALL,border=10)
        self.mainSizer.Add(btnSizer,flag=wx.ALIGN_RIGHT|wx.ALL,border=10)



    def okClicked(self, event):
        self.text = self.textCtrl.GetValue()
        self.EndModal(wx.ID_OK)
        self.Destroy()

    def cancelClicked(self, event):
        self.EndModal(wx.ID_CANCEL)
        self.Destroy()
