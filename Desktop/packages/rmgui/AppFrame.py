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
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.notebook = kNotebook.KioskNotebook(self,-1,None,base_path)
        self.mainSizer.Add(self.notebook, 1, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
        self.SetSizerAndFit(self.mainSizer)


        # Create an accelerator table for keyboard shortcuts
        sc_open = wx.NewId()
        sc_save = wx.NewId()
        sc_create_usb = wx.NewId()
        sc_load_usb = wx.NewId()
        sc_edit_order = wx.NewId()
        self.Bind(wx.EVT_MENU, self.notebook.OpenConfiguration, id=sc_open)
        self.Bind(wx.EVT_MENU, self.notebook.SaveConfiguration, id=sc_save)
        self.Bind(wx.EVT_MENU, self.notebook.mainPage.WaitForUSBForLoading, id=sc_load_usb)
        self.Bind(wx.EVT_MENU, self.notebook.mainPage.WaitForUSBForCreation, id=sc_create_usb)
        self.Bind(wx.EVT_MENU, self.notebook.EditPageOrder, id=sc_edit_order)

        self.accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('o'), sc_open),
                                              (wx.ACCEL_CTRL, ord('s'), sc_save),
                                              (wx.ACCEL_CTRL, ord('r'), sc_create_usb),
                                              (wx.ACCEL_CTRL, ord('l'), sc_load_usb),
                                              (wx.ACCEL_CTRL, ord('e'), sc_edit_order)
                                             ])
        self.SetAcceleratorTable(self.accel_tbl)

        self.SetupMenuBar()
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
        editMenu = wx.Menu()

        # save and open configurations
        openConfig = fileMenu.Append(wx.ID_OPEN, "&"+tr("open_kiosk") + "\tCTRL+O")
        saveConfig = fileMenu.Append(wx.ID_SAVE, "&"+tr("save_kiosk") + "\tCTRL+S")
        loadUsb = fileMenu.Append(wx.ID_ANY, "&"+tr("load_from_usb") + "\tCTRL+L")
        createUsb = fileMenu.Append(wx.ID_ANY, "&"+tr("create_usb") + "\tCTRL+R")

        # edit menu entrie(s)
        pageOrder = editMenu.Append(wx.ID_ANY, "&"+tr("edit_page_order") + "\tCTRL+E")

        self.Bind(wx.EVT_MENU, self.notebook.SaveConfiguration, saveConfig)
        self.Bind(wx.EVT_MENU, self.notebook.OpenConfiguration, openConfig)
        self.Bind(wx.EVT_MENU, self.notebook.mainPage.WaitForUSBForLoading, loadUsb)
        self.Bind(wx.EVT_MENU, self.notebook.mainPage.WaitForUSBForCreation, createUsb)

        self.Bind(wx.EVT_MENU, self.notebook.EditPageOrder, pageOrder)

        # Help Menu
        about = fileMenu.Append(wx.ID_ANY, "&"+tr("about"))
        self.Bind(wx.EVT_MENU, self.ShowAbout, about)

        # File Menu
        menuExit = fileMenu.Append(wx.ID_EXIT, "&"+tr("exit"),tr("exit"))
        self.Bind(wx.EVT_MENU, self.Close, menuExit)

        # Menubar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&"+tr("file"))
        menuBar.Append(editMenu, "&"+tr("edit"))

        self.SetMenuBar(menuBar)

    def ShowAbout(self, event):
        # message read from defined version info file in the future
        msg = "Kiosk Editor v1.0\n(c) 2014 by www.multimedia-installationen.at\nContact: software@multimedia-installationen.at\nAll rights reserved."
        dlg = wx.MessageDialog(self, msg, tr("about"), style=wx.OK)
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
