import wx
import KioskNotebook as kNotebook
from packages.lang.Localizer import *
import sys, os, webbrowser, platform
from packages.rmutil import Logger as log

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
        sc_new = wx.NewId()
        sc_open = wx.NewId()
        sc_save = wx.NewId()
        sc_close_kiosk = wx.NewId()
        sc_create_usb = wx.NewId()
        sc_load_usb = wx.NewId()
        sc_edit_order = wx.NewId()
        sc_new_page = wx.NewId()
        sc_del_current = wx.NewId()
        sc_switch_tab = wx.NewId()
        self.Bind(wx.EVT_MENU, self.notebook.NewConfiguration, id=sc_new)
        self.Bind(wx.EVT_MENU, self.notebook.OpenConfiguration, id=sc_open)
        self.Bind(wx.EVT_MENU, self.notebook.SaveConfiguration, id=sc_save)
        self.Bind(wx.EVT_MENU, self.notebook.CloseConfiguration, id=sc_close_kiosk)
        self.Bind(wx.EVT_MENU, self.notebook.mainPage.WaitForUSBForLoading, id=sc_load_usb)
        self.Bind(wx.EVT_MENU, self.notebook.mainPage.WaitForUSBForCreation, id=sc_create_usb)
        self.Bind(wx.EVT_MENU, self.notebook.EditPageOrder, id=sc_edit_order)
        self.Bind(wx.EVT_MENU, self.notebook.AddNewPage, id=sc_new_page)
        self.Bind(wx.EVT_MENU, self.notebook.DeleteCurrentPage, id=sc_del_current)
        self.Bind(wx.EVT_MENU, self.notebook.SwitchTab, id=sc_switch_tab)

        self.accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('o'), sc_open),
                                              (wx.ACCEL_CTRL, ord('s'), sc_save),
                                              (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('w'), sc_close_kiosk),
                                              (wx.ACCEL_CTRL, ord('r'), sc_create_usb),
                                              (wx.ACCEL_CTRL, ord('l'), sc_load_usb),
                                              (wx.ACCEL_CTRL, ord('e'), sc_edit_order),
                                              (wx.ACCEL_CTRL, ord('t'), sc_new_page),
                                              (wx.ACCEL_CTRL, ord('w'), sc_del_current),
                                              (wx.ACCEL_RAW_CTRL, ord('\t'), sc_switch_tab)
                                             ])
        self.SetAcceleratorTable(self.accel_tbl)

        self.SetupMenuBar()
        if platform.system() == 'Windows':
            # set icon
            ic_main = wx.Icon(resource_path("img/ic_main.ico"), wx.BITMAP_TYPE_ICO)
            self.SetIcon(ic_main)

        self.Center()
        self.Maximize()
        self.notebook.Hide()
        self.Show()

    def Close(self, event=None):
        cancel = False
        if not self.notebook.closed:
            dlg = wx.MessageDialog(self, "Do you want to save your current Kiosk Configuration?", "Save before Exit?", style=wx.YES_NO|wx.CANCEL)
            result = dlg.ShowModal()
            cancel = (result == wx.ID_CANCEL)
            if result  == wx.ID_YES:
                self.notebook.SaveConfiguration()
        if not cancel:
            self.notebook.Close()
            self.Destroy()
            sys.exit(0)

    def SetupMenuBar(self):
        # menus
        fileMenu = wx.Menu()
        usbMenu = wx.Menu()
        editMenu = wx.Menu()
        helpMenu = wx.Menu()

        # new, save and open configurations
        newConfig = fileMenu.Append(wx.ID_ANY, "&"+tr("new_kiosk") + "\tCTRL+N")
        fileMenu.AppendSeparator()
        openConfig = fileMenu.Append(wx.ID_OPEN, "&"+tr("open_kiosk") + "\tCTRL+O")
        saveConfig = fileMenu.Append(wx.ID_SAVE, "&"+tr("save_kiosk") + "\tCTRL+S")
        fileMenu.AppendSeparator()
        importPages = fileMenu.Append(wx.ID_ANY, "&"+tr("import_pages"))
        fileMenu.AppendSeparator()
        closeConfig = fileMenu.Append(wx.ID_ANY, "&"+tr("close_kiosk") + "\tCTRL+SHIFT+W")
        fileMenu.AppendSeparator()

        # exit entry in file menu
        menuExit = fileMenu.Append(wx.ID_EXIT, "&"+tr("exit"),tr("exit"))

        # load and create USB
        loadUsb = usbMenu.Append(wx.ID_ANY, "&"+tr("load_from_usb") + "\tCTRL+L")
        createUsb = usbMenu.Append(wx.ID_ANY, "&"+tr("create_usb") + "\tCTRL+R")

        # edit menu entrie(s)
        pageOrder = editMenu.Append(wx.ID_ANY, "&"+tr("edit_page_order") + "\tCTRL+E")

        # help menu entries
        help = helpMenu.Append(wx.ID_ANY, "&"+tr("online_help"))
        helpMenu.AppendSeparator()
        about = helpMenu.Append(wx.ID_ANY, "&"+tr("about"))

        self.Bind(wx.EVT_MENU, self.notebook.NewConfiguration, newConfig)
        self.Bind(wx.EVT_MENU, self.notebook.SaveConfiguration, saveConfig)
        self.Bind(wx.EVT_MENU, self.notebook.OpenConfiguration, openConfig)
        self.Bind(wx.EVT_MENU, self.notebook.ImportPages, importPages)
        self.Bind(wx.EVT_MENU, self.notebook.CloseConfiguration, closeConfig)
        self.Bind(wx.EVT_MENU, self.ShowAbout, about)
        self.Bind(wx.EVT_MENU, self.Close, menuExit)
        self.Bind(wx.EVT_MENU, self.notebook.mainPage.WaitForUSBForLoading, loadUsb)
        self.Bind(wx.EVT_MENU, self.notebook.mainPage.WaitForUSBForCreation, createUsb)
        self.Bind(wx.EVT_MENU, self.notebook.EditPageOrder, pageOrder)
        self.Bind(wx.EVT_MENU, self.OpenOnlineHelp, help)

        # Menubar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&"+tr("file"))
        menuBar.Append(editMenu, "&"+tr("edit"))
        menuBar.Append(usbMenu, "&USB")
        menuBar.Append(helpMenu, "&"+tr("help"))

        self.SetMenuBar(menuBar)

    def ShowAbout(self, event):
        # message read from defined version info file in the future
        msg = "Kiosk Editor v1.0\n(c) 2014 by www.multimedia-installationen.at\nContact: software@multimedia-installationen.at\nAll rights reserved."
        dlg = wx.MessageDialog(self, msg, tr("about"), style=wx.OK|wx.ICON_INFORMATION)
        dlg.ShowModal()

    def OpenOnlineHelp(self, event):
        webbrowser.open("http://bit.do/usb-kiosk-readme")


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
