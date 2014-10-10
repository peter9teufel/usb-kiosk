import wx
import KioskNotebook as kNotebook
from packages.lang.Localizer import *
import sys, os

from wx.lib.wordwrap import wordwrap

BASE_PATH = None

################################################################################
# MAIN FRAME OF APPLICATION ####################################################
################################################################################
class AppFrame(wx.Frame):
    def __init__(self,parent,id,title,base_path):
        wx.Frame.__init__(self,parent,id,title,size=(600,600))
        self.parent = parent
        self.base_path = base_path
        global BASE_PATH
        BASE_PATH = base_path
        self.Bind(wx.EVT_CLOSE, self.Close)
        self.SetupMenuBar()
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.notebook = kNotebook.KioskNotebook(self,-1,None)
        self.mainSizer.Add(self.notebook, 1, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
        self.SetSizerAndFit(self.mainSizer)
        self.Center()
        self.Maximize()
        self.Show()

    def Close(self, event=None):
        self.notebook.Close()
        self.Destroy()
        sys.exit(0)

    def SetupMenuBar(self):
        # menus
        fileMenu = wx.Menu()

        # Help Menu
        about = fileMenu.Append(wx.ID_ANY, "&"+tr("about"))
        self.Bind(wx.EVT_MENU, self.ShowAbout, about)

        # File Menu
        menuExit = fileMenu.Append(wx.ID_EXIT, "&"+tr("exit"),tr("exit"))
        self.Bind(wx.EVT_MENU, self.Close, menuExit)

        # Menubar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&"+tr("file")) # Adding the "filemenu" to the MenuBar

        self.SetMenuBar(menuBar)

    def ShowAbout(self, event):
        # message read from defined version info file in the future
        msg = "Kiosk Editor v1.0\n(c) 2014 by www.multimedia-installationen.at\nContact: software@multimedia-installationen.at\nAll rights reserved."
        dlg = wx.MessageDialog(self, msg, "About", style=wx.OK)
        dlg.ShowModal()



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
