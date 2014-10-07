import wx
import sys, platform
from wx.lib.wordwrap import wordwrap
from packages.lang.Localizer import *

################################################################################
# DIALOG FOR GROUP CREATION AND EDITING ########################################
################################################################################
class PlayerInfoDialog(wx.Dialog):
    def __init__(self,parent,id,title,player_info):
        wx.Dialog.__init__(self,parent,id,title)
        self.parent = parent
        self.player_info = player_info
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.__InitUI()

        self.SetSizerAndFit(self.mainSizer)
        self.Center()

    def __InitUI(self):
        pass


    def okClicked(self, event):
        self.EndModal(wx.ID_OK)
        self.Destroy()
