import packages.rmutil as util
from packages.rmgui import *
import PlayerInfoDialog as playerDlg
from packages.lang.Localizer import *
import os, sys, platform, ast, time, threading, shutil, copy, zipfile
from os.path import expanduser

if platform.system() == "Linux":
    from wx.lib.pubsub import setupkwargs
    from wx.lib.pubsub import pub as Publisher
else:
    from wx.lib.pubsub import pub as Publisher

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
class KioskMainPanel(wx.Panel):
    def __init__(self,parent,id,title,index,host_sys,base_path):
        #wx.Panel.__init__(self,parent,id,title)
        wx.Panel.__init__(self,parent,-1)
        global HOST_SYS, BASE_PATH
        HOST_SYS = host_sys
        BASE_PATH = base_path
        self.parent = parent
        self.index = index
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.bg = None
        self.logo = None
        self.songs = []
        self.imgPath = self.DefaultPath()
        self.usbPath = None
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

    def ResetPage(self):
        # reset song list
        self.songs = []
        while self.songList.GetItemCount() > 0:
            self.songList.DeleteItem(0)

        # reset BG and Logo
        self.bg = None
        self.logo = None
        self._SetImagePreview('img/preview.png')
        self._SetImagePreview('img/preview.png', logo=True)

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
        imgBox = wx.StaticBox(self,-1,"Background and Logo")
        imgSizer = wx.StaticBoxSizer(imgBox)

        self.audioBox = wx.StaticBox(self,-1,"Background Music")
        audioSizer = wx.StaticBoxSizer(self.audioBox,wx.VERTICAL)

        # Background selection
        bg = wx.Button(imgBox,-1,label="Background")
        bgImg = wx.EmptyImage(200,200)
        # create bitmap with preview png
        self.bgCtrl = wx.StaticBitmap(imgBox, wx.ID_ANY, wx.BitmapFromImage(bgImg))
        self._SetImagePreview('img/preview.png')

        # Logo selection
        logo = wx.Button(imgBox,-1,label="Logo")
        logoImg = wx.EmptyImage(200,200)
        self.logoCtrl = wx.StaticBitmap(imgBox, wx.ID_ANY, wx.BitmapFromImage(logoImg))
        self._SetImagePreview('img/preview.png',logo=True)

        # background music
        self.musicChk = wx.CheckBox(self.audioBox,-1,label="Enable Background Music")
        self.addSong = wx.Button(self.audioBox,-1,label="Add Song(s)")
        self.songList = wx.ListCtrl(self.audioBox,-1,size=(500,300),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.songList.Show(True)
        self.songList.InsertColumn(0,tr("filename"), width = 200)
        self.songList.InsertColumn(1,"Path", width = 280)

        # Bind elements TODO!
        bg.Bind(wx.EVT_BUTTON, self.ShowBackgroundSelection)
        logo.Bind(wx.EVT_BUTTON, self.ShowLogoSelection)
        self.songList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.SongItemRightClicked)
        self.musicChk.Bind(wx.EVT_CHECKBOX, self.MusicCheckboxToggled)
        self.addSong.Bind(wx.EVT_BUTTON, self.ShowSongSelection)
        self.MusicCheckboxToggled()

        # Create and add sizers to main sizer
        # Sizer for BACKGROUND and LOGO selection

        bgSizer = wx.BoxSizer(wx.VERTICAL)
        logoSizer = wx.BoxSizer(wx.VERTICAL)
        bgSizer.Add(bg,flag=wx.LEFT|wx.ALIGN_CENTER_HORIZONTAL,border=10)
        bgSizer.Add(self.bgCtrl,flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,border=10)
        logoSizer.Add(logo,flag=wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL,border=10)
        logoSizer.Add(self.logoCtrl,flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,border=10)
        imgSizer.Add(bgSizer)
        imgSizer.Add(logoSizer)
        # Sizer for AUDIO selection
        audioSizer.Add(self.musicChk,flag=wx.ALL,border=5)
        audioSizer.Add(self.addSong,flag=wx.ALL,border=5)
        audioSizer.Add(self.songList,flag=wx.ALL,border=5)

        imgSizer.Layout()
        audioSizer.Layout()

        # add to main sizer
        contentSizer = wx.BoxSizer(wx.VERTICAL)
        contentSizer.Add(imgSizer,flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,border=2)
        contentSizer.Add(audioSizer,flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,border=2)
        self.mainSizer.Add(contentSizer,flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,border=5)
        self.SetSizer(self.mainSizer)
        #self.LayoutAndFit()

    def ShowBackgroundSelection(self, event=None):
        dlg = imagebrowser.ImageDialog(None,self.imgPath)

        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetFile()
            self.bg = file
            self._SetImagePreview(file)
            head, tail = os.path.split(file)
            self.imgPath = head
        if HOST_SYS == HOST_WIN:
            dlg.Destroy()

    def ShowLogoSelection(self, event=None):
        dlg = imagebrowser.ImageDialog(None,self.imgPath)

        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetFile()
            self.logo = file
            self._SetImagePreview(file,logo=True)
            head, tail = os.path.split(file)
            self.imgPath = head
        if HOST_SYS == HOST_WIN:
            dlg.Destroy()

    def MusicCheckboxToggled(self, event=None, checked=False):
        if event != None:
            # triggered by chk changing event
            checked = self.musicChk.IsChecked()
        else:
            # manual trigger -> set checked state
            self.musicChk.SetValue(checked)
        if checked:
            self.addSong.Enable()
            #self.songList.Enable()
        else:
            self.addSong.Disable()
            #self.songList.Disable()

    def SongItemRightClicked(self, event):
        global HOST_SYS
        file = event.GetText()
        menu = wx.Menu()
        item = menu.Append(wx.NewId(), "Delete")
        self.Bind(wx.EVT_MENU, self.DeleteSelectedSongItem, item)

        boxRect = self.audioBox.GetRect()
        rect = self.songList.GetRect()
        origin = (boxRect[0]+rect[0],boxRect[1]+rect[1])
        point = event.GetPoint()
        if HOST_SYS == HOST_WIN:
            self.PopupMenu(menu, (origin[0]+point[0]+10,origin[1]+point[1]+15))
        else:
            self.PopupMenu(menu, (origin[0]+point[0]+10,origin[1]+point[1]+45))
        menu.Destroy()

    def DeleteSelectedSongItem(self, event=None):
        index = self.songList.GetFirstSelected()
        while self.songList.GetItemCount() > 0:
            self.songList.DeleteItem(0)
        del self.songs[index]

        for file in self.songs:
            filename = os.path.basename(file)
            idx = self.songList.InsertStringItem(self.songList.GetItemCount(), filename)
            self.songList.SetStringItem(idx,1,file[:-len(filename)])

    def ShowSongSelection(self, event):
        songDialog = wx.FileDialog(self, "Select MP3 files", "", "", "MP3 files (*.mp3)|*.mp3", wx.FD_OPEN | wx.FD_MULTIPLE)
        if songDialog.ShowModal() != wx.ID_CANCEL:
            files = songDialog.GetFilenames()
            dir = songDialog.GetDirectory()
            for file in files:
                self.songs.append(dir + '/' + file)
                idx = self.songList.InsertStringItem(self.songList.GetItemCount(), file)
                self.songList.SetStringItem(idx,1,dir)


    def LayoutAndFit(self):
        self.mainSizer.Layout()
        self.Fit()
        self.parent.Fit()
        self.parent.parent.Fit()
        self.parent.parent.Center()

    def _SetImagePreview(self, imagePath, logo=False):
        ## print "PREVIEW IMAGE PATH: " + imagePath
        path = resource_path(imagePath)
        #print "RESOURCE PATH: " + path
        img = wx.Image(path)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()

        maxSize = 200

        if W > H:
            NewW = maxSize
            NewH = maxSize * H / W
        else:
            NewH = maxSize
            NewW = maxSize * W / H
        img = img.Scale(NewW,NewH)

        if logo:
            self.logoCtrl.SetBitmap(wx.BitmapFromImage(img))
        else:
            self.bgCtrl.SetBitmap(wx.BitmapFromImage(img))

    def WaitForUSBForCreation(self, event):
        if self.usbPath == None or not os.path.isdir(self.usbPath):
            self.usbPath = None
            self.__WaitForUSB()
        else:
            self.CreateUSB(self.usbPath)

    def WaitForUSBForLoading(self, event):
        if self.usbPath == None or not os.path.isdir(self.usbPath):
            self.usbPath = None
            self.__WaitForUSB(loading=True)
        else:
            self.LoadFromUSB(self.usbPath)

    def __WaitForUSB(self, loading=False):
        print "Waiting for USB Drive..."
        if loading:
            Publisher.subscribe(self.LoadFromUSB, 'usb_connected')
        else:
            Publisher.subscribe(self.CreateUSB, 'usb_connected')
        Publisher.subscribe(self.NoUSBFound, 'usb_search_timeout')
        self.prgDialog = wx.ProgressDialog(tr("searching"), tr("plug_usb"))
        self.prgDialog.Pulse()
        if HOST_SYS == HOST_WIN:
            util.Win32DeviceDetector.waitForUSBDrive()
        elif HOST_SYS == HOST_MAC or HOST_SYS == HOST_LINUX:
            util.UnixDriveDetector.waitForUSBDrive()

    def NoUSBFound(self):
        self.prgDialog.Update(100)
        if HOST_SYS == HOST_WIN:
            self.prgDialog.Destroy()
        dlg = wx.MessageDialog(self, "Sorry, I was not able to detect your USB Drive, please unplug and try again.", "No USB Drive detected", style=wx.OK)
        dlg.ShowModal()

    def LoadFromUSB(self, path):
        if HOST_SYS == HOST_WIN and not path.endswith(":"):
            # add colon to path under windows as path is only drive letter
            path += ":"
        if self.usbPath == None:
            self.prgDialog.UpdatePulse("Loading USB data...")
        else:
            self.prgDialog = wx.ProgressDialog(tr("loading"),"Loading USB Data, please wait...")
            self.prgDialog.Pulse()
        self.usbPath = path

        # create kiosk directory in temp path
        home = expanduser("~")
        appPath = home + '/.usb_kiosk/'
        tmpRoot = appPath + 'tmp/'
        tmpPath = tmpRoot + 'kiosk_config/'
        if os.path.isdir(tmpRoot):
            shutil.rmtree(tmpRoot)
        os.mkdir(tmpRoot)
        os.mkdir(tmpPath)

        usbPath = path + '/kiosk'
        if os.path.isdir(usbPath):
            # copy background and icon
            srcFile = usbPath + '/bg.jpg'
            destFile = tmpPath + 'bg.jpg'
            if os.path.isfile(srcFile):
                shutil.copyfile(srcFile, destFile)
                self.bg = destFile
            srcFile = usbPath + '/logo.png'
            destFile = tmpPath + 'logo.png'
            if os.path.isfile(srcFile):
                shutil.copyfile(srcFile, destFile)
                self.logo = destFile

            # copy mp3 files if present
            if os.path.isdir(usbPath + '/mp3/'):
                self.MusicCheckboxToggled(checked=True)
                mp3Usb = usbPath + '/mp3/'
                destPath = tmpPath + 'mp3/'
                os.mkdir(destPath)
                with open(mp3Usb + 'filenames.bak', 'r') as f:
                    data = f.read()
                filenames = data.split("\n")
                fileNr = 0
                for file in os.listdir(mp3Usb):
                    if file.endswith('.mp3'):
                        srcFile = mp3Usb + file
                        destFile = destPath + filenames[fileNr]
                        shutil.copyfile(srcFile,destFile)
                        self.songs.append(destFile)
                        idx = self.songList.InsertStringItem(self.songList.GetItemCount(), filenames[fileNr])
                        self.songList.SetStringItem(idx, 1, destPath)
                        fileNr += 1

            # copy data for single pages to page directories in temp dir
            usbPages = []
            for p in os.listdir(usbPath):
                if p.startswith('page'):
                    usbPages.append(p)
            for usbDir in usbPages:
                pageDir = usbPath + '/' + usbDir + '/'
                tmpPage = tmpPath + usbDir + '/'
                os.mkdir(tmpPage)
                # page headline
                shutil.copyfile(pageDir + 'headline.txt', tmpPage + 'headline.txt')
                # page texts and images
                for file in os.listdir(pageDir):
                    if file.startswith("Text") or file.startswith("image"):
                        shutil.copyfile(pageDir + file, tmpPage + file)

            # parse loaded data, create pages and update UI
            for dir in os.listdir(tmpPath):
                if dir.startswith("page"):
                    # page directory
                    pageDir = tmpPath + dir + '/'
                    images = []
                    txts = []
                    title = ""
                    for file in os.listdir(pageDir):
                        if file.startswith("Text"):
                            # page text
                            with open(pageDir + file) as f:
                                txts.append(f.read().decode("utf-8"))
                        elif file.startswith("image"):
                            # page image
                            images.append(pageDir + file)
                        elif file == "headline.txt":
                            # page headline
                            with open(pageDir + file) as f:
                                title = f.read().decode("utf-8")
                    self.parent.AddKioskPage(title, txts, images)
            # set background and logo preview if applicable
            if not self.bg == None:
                self._SetImagePreview(self.bg)
            if not self.logo == None:
                self._SetImagePreview(self.logo, logo=True)

            print "USB Loading done!"
        self.prgDialog.Update(100)
        if HOST_SYS == HOST_WIN:
            self.prgDialog.Destroy()

        wx.CallAfter(Publisher.unsubscribe, self.LoadFromUSB, 'usb_connected')
        wx.CallAfter(Publisher.unsubscribe, self.LoadFromUSB, 'usb_search_timeout')


    def CreateUSB(self, path):
        if HOST_SYS == HOST_WIN and not path.endswith(":"):
            # add colon to path under windows as path is only drive letter
            path += ":"
        if self.usbPath == None:
            self.prgDialog.UpdatePulse("Creating USB data...")
        else:
            self.prgDialog = wx.ProgressDialog(tr("loading"),"Creating USB Data, please wait...")
            self.prgDialog.Pulse()
        self.usbPath = path


        # create kiosk directory on usb drive
        usbPath = path + '/kiosk'
        if os.path.isdir(usbPath):
            shutil.rmtree(usbPath)
        os.mkdir(usbPath)

        # copy background and icon if set
        if not self.bg == None:
            # TODO resize BG Image to 1920x1080 FIT MODE
            dstFile = usbPath + '/bg.jpg'
            shutil.copyfile(self.bg, dstFile)
        if not self.logo == None:
            # TODO convert to PNG!
            dstFile = usbPath + '/logo.png'
            shutil.copyfile(self.logo, dstFile)

        # copy MP3 files if background music enabled
        if self.musicChk.IsChecked():
            mp3Path = usbPath + '/mp3/'
            os.mkdir(mp3Path)
            fileNames = open(mp3Path + 'filenames.bak', 'w')
            cnt = 0
            for mp3 in self.songs:
                nr = ""
                if cnt < 100:
                    if cnt < 10:
                        nr = "00"
                    else:
                        nr = 0
                    nr += str(cnt)
                fileNames.write(os.path.basename(mp3).encode("utf-8") + "\n")
                shutil.copyfile(mp3, mp3Path + 'BG_Music_Title_' + nr + '.mp3')
                cnt += 1
            fileNames.close()

        # copy data for single pages to page directories in kiosk directory on USB
        for i in range(1,self.parent.GetPageCount() - 1):
            page = self.parent.GetPage(i)
            pageDir = usbPath + '/page' + str(i) + '/'
            os.mkdir(pageDir)
            # page headline
            fileName = pageDir + "headline.txt"
            f = open(fileName, 'w')
            f.write(page.title.encode("utf-8"))
            f.close()
            # page texts
            texts = page.texts
            for j in range(len(texts)):
                fileName = pageDir + "Text" + str(j+1) + ".txt"
                f = open(fileName, 'w')
                f.write(texts[j].encode("utf-8"))
                f.close()
            # page images
            imgs = page.images
            for j in range(len(imgs)):
                ending = ".jpg"
                if imgs[j].endswith(".png") or imgs[j].endswith(".PNG"):
                    ending = ".png"
                dstFile = pageDir + '/image' + str(j) + ending
                shutil.copyfile(imgs[j], dstFile)
        print "USB Preparation done!"
        self.prgDialog.Update(100)
        if HOST_SYS == HOST_WIN:
            self.prgDialog.Destroy()
        dlg = wx.MessageDialog(self, tr("done"), tr("done"), style = wx.OK)
        dlg.ShowModal()
        wx.CallAfter(Publisher.unsubscribe, self.CreateUSB, 'usb_connected')
        wx.CallAfter(Publisher.unsubscribe, self.CreateUSB, 'usb_search_timeout')

    def SaveConfiguration(self, path=None):
        home = expanduser("~")
        appPath = home + '/.usb_kiosk/'
        tmpRoot = appPath + 'tmp/'

        # create kiosk directory
        tmpPath = tmpRoot + 'kiosk_config_save'
        if os.path.isdir(tmpPath):
            shutil.rmtree(tmpPath)
        os.mkdir(tmpPath)

        # copy background and icon if set
        if not self.bg == None:
            dstFile = tmpPath + '/bg.jpg'
            shutil.copyfile(self.bg, dstFile)
        if not self.logo == None:
            # TODO convert to PNG!
            dstFile = tmpPath + '/logo.png'
            shutil.copyfile(self.logo, dstFile)

        # copy MP3 files if background music enabled
        if self.musicChk.IsChecked():
            mp3Path = tmpPath + '/mp3/'
            os.mkdir(mp3Path)
            fileNames = open(mp3Path + 'filenames.bak', 'w')
            cnt = 0
            for mp3 in self.songs:
                nr = ""
                if cnt < 100:
                    if cnt < 10:
                        nr = "00"
                    else:
                        nr = 0
                    nr += str(cnt)
                fileNames.write(os.path.basename(mp3).encode("utf-8") + "\n")
                shutil.copyfile(mp3, mp3Path + 'BG_Music_Title_' + nr + '.mp3')
                cnt += 1
            fileNames.close()

        # copy data for single pages to page directories in kiosk directory on USB
        for i in range(1,self.parent.GetPageCount() - 1):
            page = self.parent.GetPage(i)
            pageDir = tmpPath + '/page' + str(i) + '/'
            os.mkdir(pageDir)
            # page headline
            fileName = pageDir + "headline.txt"
            f = open(fileName, 'w')
            f.write(page.title.encode("utf-8"))
            f.close()
            # page texts
            texts = page.texts
            for j in range(len(texts)):
                fileName = pageDir + "Text" + str(j+1) + ".txt"
                f = open(fileName, 'w')
                f.write(texts[j].encode("utf-8"))
                f.close()
            # page images
            imgs = page.images
            for j in range(len(imgs)):
                ending = ".jpg"
                if imgs[j].endswith(".png") or imgs[j].endswith(".PNG"):
                    ending = ".png"
                dstFile = pageDir + '/image' + str(j) + ending
                shutil.copyfile(imgs[j], dstFile)
        #zipFile = zipfile.ZipFile(path, 'w')
        #self.zipdir(tmpPath, zipFile)
        self.make_zipfile(path, tmpPath)
        dlg = wx.MessageDialog(self, tr("done"), tr("done"), style = wx.OK)
        dlg.ShowModal()

    def OpenConfiguration(self, path):
        home = expanduser("~")
        appPath = home + '/.usb_kiosk/'
        tmpRoot = appPath + 'tmp/'
        self.unzip(path, tmpRoot)
        os.rename(tmpRoot + 'kiosk_config_save', tmpRoot + 'kiosk_config')
        self.LoadPagesFromTempData(tmpRoot + 'kiosk_config/')

    def LoadPagesFromTempData(self, tmpPath):
        # parse loaded data, create pages and update UI
        for dir in os.listdir(tmpPath):
            if dir.startswith("page"):
                # page directory
                pageDir = tmpPath + dir + '/'
                images = []
                txts = []
                title = ""
                for file in os.listdir(pageDir):
                    if file.startswith("Text"):
                        # page text
                        with open(pageDir + file) as f:
                            txts.append(f.read().decode("utf-8"))
                    elif file.startswith("image"):
                        # page image
                        images.append(pageDir + file)
                    elif file == "headline.txt":
                        # page headline
                        with open(pageDir + file) as f:
                            title = f.read().decode("utf-8")
                self.parent.AddKioskPage(title, txts, images)
            elif dir.startswith("mp3"):
                self.MusicCheckboxToggled(checked=True)
                mp3Dir = tmpPath + 'mp3/'
                mp3Tmp = tmpPath + 'mp3_tmp/'
                os.rename(mp3Dir, mp3Tmp)
                os.mkdir(mp3Dir)
                with open(mp3Tmp + 'filenames.bak', 'r') as f:
                    data = f.read()
                filenames = data.split("\n")
                fileNr = 0
                for file in os.listdir(mp3Tmp):
                    if file.endswith('.mp3'):
                        srcFile = mp3Tmp + file
                        destFile = mp3Dir + filenames[fileNr]
                        shutil.copyfile(srcFile,destFile)
                        self.songs.append(destFile)
                        idx = self.songList.InsertStringItem(self.songList.GetItemCount(), filenames[fileNr])
                        self.songList.SetStringItem(idx, 1, mp3Dir)
                        fileNr += 1
                shutil.rmtree(mp3Tmp)
            elif dir == "bg.jpg":
                # set background and logo preview if applicable
                self.bg = tmpPath + dir
                self._SetImagePreview(self.bg)
            elif dir == "logo.png":
                self.logo = tmpPath + dir
                self._SetImagePreview(self.logo, logo=True)

    def unzip(self, zipPath, destPath):
        fh = open(zipPath, 'rb')
        z = zipfile.ZipFile(fh)

        for name in z.namelist():
            z.extract(name, destPath)
        fh.close()

    def make_zipfile(self, output_filename, source_dir):
        relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
        with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
            for root, dirs, files in os.walk(source_dir):
                # add directory (needed for empty dirs)
                zip.write(root, os.path.relpath(root, relroot))
                for file in files:
                    filename = os.path.join(root, file)
                    if os.path.isfile(filename): # regular files only
                        arcname = os.path.join(os.path.relpath(root, relroot), file)
                        zip.write(filename, arcname)

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
