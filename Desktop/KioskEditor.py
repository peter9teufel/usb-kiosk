from packages.rmgui import AppFrame as rm_app
from packages.rmutil import Logger as logger
import os, platform, shutil
try:
    import wx
except ImportError:
    raise ImportError,"Wx Python is required."


# set working directory to scripts path
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
base_path = dname
app = wx.App()

# create app data path if not already present and tmp path
from os.path import expanduser
home = expanduser("~")
appPath = home + '/.usb_kiosk/'
tmpPath = appPath + 'tmp/'
if not os.path.isdir(appPath):
    os.mkdir(appPath)

if os.path.isdir(tmpPath):
    shutil.rmtree(tmpPath)
os.mkdir(tmpPath)

frame = rm_app.AppFrame(None, -1, 'Kiosk Editor', base_path)
app.MainLoop()
