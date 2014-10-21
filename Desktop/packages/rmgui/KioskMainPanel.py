import packages.rmutil as util
from packages.rmgui import *
from packages.lang.Localizer import *
import os, sys, platform, ast, time, threading, shutil, copy, zipfile
from os.path import expanduser
from PIL import Image

if platform.system() == "Linux":
    from wx.lib.pubsub import setupkwargs
    from wx.lib.pubsub import pub as Publisher
else:
    from wx.lib.pubsub import pub as Publisher

import wx
from wx.lib import imagebrowser
from wx.lib.wordwrap import wordwrap

from packages.rmutil import Logger as log

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
        self.streams = []
        self.streamAddr = None
        self.imgPath = self.DefaultPath()
        self.usbPath = None
        log.write("Initializing UI for Main Panel...")
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
        self.streamCombo.SetSelection(-1)
        self.streamAddr = None
        self.musicRadioBox.SetSelection(0)
        self.MusicRadioBoxChanged()
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
        imgBox = wx.StaticBox(self,-1,tr("bg_logo_box"),size=(523,310))
        imgSizer = wx.StaticBoxSizer(imgBox)

        self.audioBox = wx.StaticBox(self,-1,tr("bg_music"))
        self.audioSizer = wx.StaticBoxSizer(self.audioBox,wx.VERTICAL)

        # Background selection
        bg = wx.Button(imgBox,-1,label=tr("background"))
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
        self.musicRadioBox = wx.RadioBox(self.audioBox,-1,choices=[tr("no_music"), tr("mp3_files"), tr("webradio_stream")],size=(490,42))
        self.addSong = wx.Button(self.audioBox,-1,label=tr("add_songs"))
        self.songList = wx.ListCtrl(self.audioBox,-1,size=(490,300),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.songList.InsertColumn(0,tr("filename"), width = 200)
        self.songList.InsertColumn(1,tr("path"), width = 280)
        self.streams = util.StreamAddresses.GetStreamNames()
        self.streamCombo = wx.ComboBox(self.audioBox, choices=self.streams)
        self.streamCombo.SetSelection(-1)

        # Bind elements
        bg.Bind(wx.EVT_BUTTON, self.ShowBackgroundSelection)
        logo.Bind(wx.EVT_BUTTON, self.ShowLogoSelection)
        self.songList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.SongItemRightClicked)
        self.musicRadioBox.Bind(wx.EVT_RADIOBUTTON, self.MusicRadioBoxChanged)
        self.musicRadioBox.Bind(wx.EVT_RADIOBOX, self.MusicRadioBoxChanged)
        self.addSong.Bind(wx.EVT_BUTTON, self.ShowSongSelection)
        self.streamCombo.Bind(wx.EVT_COMBOBOX, self.StreamComboSelected)
        self.MusicRadioBoxChanged()

        # Create and add sizers to main sizer
        # Sizer for BACKGROUND and LOGO selection
        bgSizer = wx.BoxSizer(wx.VERTICAL)
        logoSizer = wx.BoxSizer(wx.VERTICAL)
        bgSizer.Add(bg,flag=wx.wx.ALIGN_CENTER_HORIZONTAL)
        bgSizer.Add(self.bgCtrl,flag=wx.TOP|wx.ALIGN_CENTER_HORIZONTAL,border=10)
        logoSizer.Add(logo,flag=wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL,border=10)
        logoSizer.Add(self.logoCtrl,flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL,border=10)
        imgSizer.Add(bgSizer, 1, flag=wx.EXPAND)
        imgSizer.Add(logoSizer, 1, flag=wx.EXPAND)
        # Sizer for AUDIO selection
        self.audioSizer.Add(self.musicRadioBox,flag=wx.RIGHT|wx.BOTTOM,border=10)
        self.audioSizer.Add(self.streamCombo,flag=wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_HORIZONTAL,border=10)
        self.audioSizer.Add(self.addSong,flag=wx.RIGHT,border=10)
        self.audioSizer.Add(self.songList,flag=wx.RIGHT|wx.BOTTOM,border=10)

        imgSizer.Layout()
        self.audioSizer.Layout()

        # add to main sizer
        contentSizer = wx.BoxSizer(wx.VERTICAL)
        contentSizer.Add(imgSizer,flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,border=2)
        contentSizer.Add(self.audioSizer,flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,border=2)
        self.mainSizer.Add(contentSizer,flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,border=5)

        self.SetSizer(self.mainSizer)

    def MusicRadioBoxChanged(self, event=None):
        sel = self.musicRadioBox.GetSelection()
        if sel == 0:
            self.songList.Hide()
            self.addSong.Hide()
            self.streamCombo.Hide()
        elif sel == 1:
            self.songList.Show()
            self.addSong.Show()
            self.streamCombo.Hide()
        elif sel == 2:
            self.songList.Hide()
            self.addSong.Hide()
            self.streamCombo.Show()
        self.audioSizer.Layout()
        self.mainSizer.Layout()
        self.parent.modified = True

    def StreamComboSelected(self, event):
        name = self.streams[self.streamCombo.GetSelection()]
        self.streamAddr = util.StreamAddresses.GetAddrForStream(self.streamCombo.GetSelection())
        self.parent.modified = True

    def ShowBackgroundSelection(self, event=None):
        dlg = imagebrowser.ImageDialog(None,self.imgPath)

        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetFile()
            self.bg = file
            self._SetImagePreview(file)
            head, tail = os.path.split(file)
            self.imgPath = head
            self.parent.modified = True
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
            self.parent.modified = True
        if HOST_SYS == HOST_WIN:
            dlg.Destroy()

    def SongItemRightClicked(self, event):
        global HOST_SYS
        file = event.GetText()
        menu = wx.Menu()
        item = menu.Append(wx.NewId(), tr("delete"))
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
        self.parent.modified = True

    def ShowSongSelection(self, event):
        songDialog = wx.FileDialog(self, tr("select_mp3s"), "", "", "MP3 files (*.mp3)|*.mp3", wx.FD_OPEN | wx.FD_MULTIPLE)
        if songDialog.ShowModal() != wx.ID_CANCEL:
            files = songDialog.GetFilenames()
            dir = songDialog.GetDirectory()
            for file in files:
                self.songs.append(dir + '/' + file)
                idx = self.songList.InsertStringItem(self.songList.GetItemCount(), file)
                self.songList.SetStringItem(idx,1,dir)
            self.parent.modified = True


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
        self.mainSizer.Layout()

    def WaitForUSBForCreation(self, event):
        if not self.parent.closed:
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
            self.prgDialog = wx.ProgressDialog(tr("load_from_usb"), tr("plug_usb"))
        else:
            Publisher.subscribe(self.CreateUSB, 'usb_connected')
            self.prgDialog = wx.ProgressDialog(tr("create_usb"), tr("plug_usb"))
        Publisher.subscribe(self.NoUSBFound, 'usb_search_timeout')
        self.prgDialog.Pulse()
        if HOST_SYS == HOST_WIN:
            util.Win32DeviceDetector.waitForUSBDrive()
        elif HOST_SYS == HOST_MAC or HOST_SYS == HOST_LINUX:
            util.UnixDriveDetector.waitForUSBDrive()

    def NoUSBFound(self):
        self.prgDialog.Update(100)
        if HOST_SYS == HOST_WIN:
            self.prgDialog.Destroy()
        dlg = wx.MessageDialog(self, tr("msg_no_usb"), tr("title_no_usb"), style=wx.OK|wx.ICON_ERROR)
        dlg.ShowModal()

    def LoadFromUSB(self, path):
        if HOST_SYS == HOST_WIN and not path.endswith(":"):
            # add colon to path under windows as path is only drive letter
            path += ":"
        if self.usbPath == None:
            self.prgDialog.UpdatePulse(tr("loading_usb_data"))
        else:
            self.prgDialog = wx.ProgressDialog(tr("load_from_usb"),tr("loading_usb_data"))
            self.prgDialog.Pulse()
        self.usbPath = path

        self.parent.ClearNotebook()
        self.parent.Hide()

        # create kiosk directory in temp path
        home = expanduser("~")
        appPath = home + '/.usb_kiosk/'
        tmpRoot = appPath + 'tmp/'
        tmpPath = tmpRoot + 'kiosk_config/'
        if os.path.isdir(tmpRoot):
            shutil.rmtree(tmpRoot)
        os.mkdir(tmpRoot)
        os.mkdir(tmpPath)
        self.musicRadioBox.SetSelection(0)

        usbPath = path + '/kiosk'
        if os.path.isdir(usbPath):
            # copy background and icon
            srcFile = usbPath + '/bg.jpg'
            destFile = tmpPath + 'bg.jpg'
            if os.path.isfile(srcFile):
                self.prgDialog.UpdatePulse(os.path.basename(destFile))
                shutil.copyfile(srcFile, destFile)
                self.bg = destFile
            srcFile = usbPath + '/logo.png'
            destFile = tmpPath + 'logo.png'
            if os.path.isfile(srcFile):
                self.prgDialog.UpdatePulse(os.path.basename(destFile))
                shutil.copyfile(srcFile, destFile)
                self.logo = destFile

            # copy mp3 files if present
            if os.path.isdir(usbPath + '/mp3/'):
                self.musicRadioBox.SetSelection(1)
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
                        self.prgDialog.UpdatePulse(os.path.basename(destFile))
                        shutil.copyfile(srcFile,destFile)
                        self.songs.append(destFile)
                        idx = self.songList.InsertStringItem(self.songList.GetItemCount(), filenames[fileNr])
                        self.songList.SetStringItem(idx, 1, destPath)
                        fileNr += 1

            # copy stream.txt file if ppresent
            if os.path.isfile(usbPath + '/stream.txt'):
                self.prgDialog.UpdatePulse('stream.txt')
                shutil.copyfile(usbPath + '/stream.txt', tmpPath + 'stream.txt')
                with open(tmpPath + 'stream.txt') as streamFile:
                    self.streamAddr = streamFile.read()
                    self.musicRadioBox.SetSelection(2)
                    self.streamCombo.SetSelection(self.streams.index(util.StreamAddresses.GetNameForAddr(self.streamAddr)))

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
                        self.prgDialog.UpdatePulse(file)
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
            self.MusicRadioBoxChanged()


        self.prgDialog.Update(100)
        if HOST_SYS == HOST_WIN:
            self.prgDialog.Destroy()

        self.mainSizer.Layout()
        self.parent.Show()
        self.parent.modified = True
        wx.CallAfter(Publisher.unsubscribe, self.LoadFromUSB, 'usb_connected')
        wx.CallAfter(Publisher.unsubscribe, self.LoadFromUSB, 'usb_search_timeout')


    def CreateUSB(self, path):
        if HOST_SYS == HOST_WIN and not path.endswith(":"):
            # add colon to path under windows as path is only drive letter
            path += ":"
        if self.usbPath == None:
            self.prgDialog.Update(100)
            if HOST_SYS == HOST_WIN:
                self.prgDialog.Destroy()
        self.usbPath = path

        totalFiles = self.parent.NumberOfFiles()
        numFiles = 0
        # create kiosk directory on usb drive
        usbPath = path + '/kiosk'
        if os.path.isdir(usbPath):
            shutil.rmtree(usbPath)
        os.mkdir(usbPath)

        # calc estimated size required with free space on USB
        estimatedSize = self.EstimatedUSBDataSize()
        estMB = estimatedSize/1024/1024
        fs_info = self.GetDiskUsageStats(path)
        freeUSB = fs_info["free"]
        freeMB = freeUSB/1024/1024

        if estimatedSize < freeUSB:
            self.prgDialog = wx.ProgressDialog(tr("create_usb"), tr("creating_usb_data"), maximum=totalFiles)
            # copy background and icon if set
            if not self.bg == None:
                # background image is resized on player
                dstFile = usbPath + '/bg.jpg'
                shutil.copyfile(self.bg, dstFile)
            if not self.logo == None:
                # resize and save --> PIL converts the image to PNG in case it is a JPG
                logo = Image.open(self.logo)
                w,h = logo.size
                newW = 300
                newH = newW * w/h
                logo.thumbnail((newW, newH))
                dstFile = usbPath + '/logo.png'
                logo.save(dstFile, 'PNG')

            # copy MP3 files if background music enabled
            if self.musicRadioBox.GetSelection() == 1:
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
                            nr = "0"
                        nr += str(cnt)
                    fileNames.write(os.path.basename(mp3).encode("utf-8") + "\n")
                    shutil.copyfile(mp3, mp3Path + 'BG_Music_Title_' + nr + '.mp3')
                    numFiles += 1
                    self.prgDialog.Update(numFiles, os.path.basename(mp3))
                    cnt += 1
                fileNames.close()
            elif self.musicRadioBox.GetSelection() == 2:
                # write stream address to streamfile on usb drive
                with open(usbPath + '/stream.txt', 'w') as streamFile:
                    streamFile.write(self.streamAddr)

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
                    numFiles += 1
                    self.prgDialog.Update(numFiles, os.path.basename(fileName))
                # page images
                imgs = page.images
                for j in range(len(imgs)):
                    ending = ".jpg"
                    if imgs[j].endswith(".png") or imgs[j].endswith(".PNG"):
                        ending = ".png"
                    dstFile = pageDir + '/image' + str(j) + ending
                    shutil.copyfile(imgs[j], dstFile)
                    numFiles += 1
                    self.prgDialog.Update(numFiles, os.path.basename(dstFile))
            if numFiles < totalFiles:
                self.prgDialog.Update(totalFiles)
            if HOST_SYS == HOST_WIN:
                self.prgDialog.Destroy()
            dlg = wx.MessageDialog(self, tr("msg_usb_done"), tr("done"), style = wx.OK|wx.ICON_INFORMATION)
            dlg.ShowModal()
        else:
            free = ""
            est = ""
            if freeMB > 1024 and estMB > 1024:
                free = str(freeMB/1024) + " GB"
                est = str(estMB/1024) + " GB"
            else:
                free = str(freeMB) + " MB"
                est = str(estMB) + " MB"

            dlg = wx.MessageDialog(self, tr("msg_usb_no_space") % (free,est), tr("title_usb_no_space"), style = wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()


        wx.CallAfter(Publisher.unsubscribe, self.CreateUSB, 'usb_connected')
        wx.CallAfter(Publisher.unsubscribe, self.CreateUSB, 'usb_search_timeout')

    def SaveConfiguration(self, path=None):
        prgDlg = wx.ProgressDialog(tr("saving"), tr("msg_saving"))
        prgDlg.Pulse()
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
            # resize and save --> PIL converts the image to PNG in case it is a JPG
            logo = Image.open(self.logo)
            w,h = logo.size
            newW = 300
            newH = newW * w/h
            logo.thumbnail((newW, newH))
            dstFile = tmpPath + '/logo.png'
            logo.save(dstFile, 'PNG')

        # copy MP3 files if background music enabled
        if self.musicRadioBox.GetSelection() == 1:
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
        elif self.musicRadioBox.GetSelection() == 2:
            # write stream.txt file to tmp path with selected stream address
            with open(tmpPath + '/stream.txt', 'w') as streamFile:
                streamFile.write(self.streamAddr)

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
        self.make_zipfile(path, tmpPath)
        prgDlg.Update(100)
        if HOST_SYS == HOST_WIN:
            prgDlg.Destroy()
        #dlg = wx.MessageDialog(self, tr("msg_saving_done"), tr("done"), style = wx.OK|wx.ICON_INFORMATION)
        #dlg.ShowModal()

    def OpenConfiguration(self, path):
        prgDialog = wx.ProgressDialog(tr("title_opening"), tr("msg_opening"))
        prgDialog.Pulse()
        home = expanduser("~")
        appPath = home + '/.usb_kiosk/'
        tmpRoot = appPath + 'tmp/'
        self.unzip(path, tmpRoot)
        os.rename(tmpRoot + 'kiosk_config_save', tmpRoot + 'kiosk_config')
        self.LoadPagesFromTempData(tmpRoot + 'kiosk_config/')
        prgDialog.Update(100)
        if HOST_SYS == HOST_WIN:
            prgDialog.Destroy()

    def ImportPages(self, path):
        self.parent.Hide()
        prgDialog = wx.ProgressDialog(tr("loading"), tr("msg_importing"))
        prgDialog.Pulse()
        home = expanduser("~")
        appPath = home + '/.usb_kiosk/'
        tmpRoot = appPath + 'tmp/'
        tmpPath = tmpRoot + 'tmp_import_' + os.path.basename(path) + '/'
        if os.path.isdir(tmpPath):
            shutil.rmtree(tmpPath)
        os.mkdir(tmpPath)
        self.unzip(path, tmpPath)
        os.rename(tmpPath + 'kiosk_config_save', tmpPath + 'kiosk_config')
        self.LoadPagesFromTempData(tmpPath + 'kiosk_config/', include_main=False)
        prgDialog.Update(100)
        if HOST_SYS == HOST_WIN:
            prgDialog.Destroy()

    def LoadPagesFromTempData(self, tmpPath, include_main=True):
        # self.musicRadioBox.SetSelection(0)
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
            elif dir.startswith("mp3") and include_main:
                self.musicRadioBox.SetSelection(1)
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
            elif dir == "bg.jpg" and include_main:
                # set background and logo preview if applicable
                self.bg = tmpPath + dir
                self._SetImagePreview(self.bg)
            elif dir == "logo.png" and include_main:
                self.logo = tmpPath + dir
                self._SetImagePreview(self.logo, logo=True)
            elif dir == "stream.txt" and include_main:
                with open(tmpPath + dir) as streamFile:
                    self.streamAddr = streamFile.read()
                self.musicRadioBox.SetSelection(2)
                self.streamCombo.SetSelection(self.streams.index(util.StreamAddresses.GetNameForAddr(self.streamAddr)))
        self.MusicRadioBoxChanged()
        self.mainSizer.Layout()
        self.parent.Show()

    def AppendPagesFromTempData(self, tmpPath):
        self.musicRadioBox.SetSelection(0)
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
        self.mainSizer.Layout()

    def EstimatedUSBDataSize(self):
        total = 0
        for song in self.songs:
            total += os.stat(song).st_size
        for page in self.parent.GetEditorPages():
            for img in page.images:
                total += os.stat(img).st_size
            for txt in page.texts:
                total += len(txt)
        return total

    def GetDiskUsageStats(self, path):
        if hasattr(os, 'statvfs'):  # POSIX
            st = os.statvfs(path)
            free = st.f_bavail * st.f_frsize
            total = st.f_blocks * st.f_frsize
            used = (st.f_blocks - st.f_bfree) * st.f_frsize
            return {"total":total, "used": used, "free": free}
        elif os.name == 'nt':       # Windows
            import ctypes
            import sys
            _, total, free = ctypes.c_ulonglong(), ctypes.c_ulonglong(), ctypes.c_ulonglong()
            if sys.version_info >= (3,) or isinstance(path, unicode):
                fun = ctypes.windll.kernel32.GetDiskFreeSpaceExW
            else:
                fun = ctypes.windll.kernel32.GetDiskFreeSpaceExA
            ret = fun(path, ctypes.byref(_), ctypes.byref(total), ctypes.byref(free))
            if ret == 0:
                raise ctypes.WinError()
            used = total.value - free.value
            return {"total":total.value, "used": used, "free": free.value}

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
