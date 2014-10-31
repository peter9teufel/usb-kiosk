# -*- coding: utf-8 -*-
import wx, platform
from PIL import Image, ImageFilter
import wx.lib.scrolledpanel as scrolled
from packages.lang.Localizer import *
import sys, platform
from threading import Timer

SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG')

################################################################################
# SCROLLABLE IMAGE VIEW ########################################################
################################################################################
class ImageDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        for file in filenames:
            self.window.AddImage(file)

class ScrollableImageView(scrolled.ScrolledPanel):
    def __init__(self,parent,id,size,images,dataSource):
        scrolled.ScrolledPanel.__init__(self,parent,id,size=size)
        self.parent = parent
        self.size = size
        self.dataSource = dataSource
        # variables for drag re-order
        self.imgClicked = -1
        self.dragDelete = False
        self.swappedIndex = -1
        self.draggedBmp = None
        self.swapped = False
        self.ctrlSize = None
        self.imgWidth = 0
        self.prevX = -1
        self.delPath = 0
        self.imgCtrls = []

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.images = images
        self.__LoadImages()
        self.SetSizer(self.mainSizer)
        dropTarget = ImageDropTarget(self)
        self.SetDropTarget(dropTarget)
        self.LayoutAndScroll()

    def OnLeftDown(self, event, ctrl):
        index = self.imgCtrls.index(ctrl)
        self.imgClicked = index
        self.draggedBmp = self.imgCtrls[index].GetBitmap()
        # blur preview of image that is beeing dragged
        img = self.__ScaleImage(self.images[index], self.imgWidth, blurred=True)
        bmp = wx.BitmapFromImage(img)
        self.imgCtrls[index].SetBitmap(bmp)

    def OnLeftUp(self, event, ctrl):
        if not self.draggedBmp == None:
            if self.swapped:
                self.imgClicked = self.swappedIndex
            self.imgCtrls[self.imgClicked].SetBitmap(self.draggedBmp)
        if self.dragDelete:
            self.__DeleteImage(self.imgClicked)
        self.imgClicked = -1
        self.draggedBmp = None
        self.ctrlSize = None
        self.swappedIndex = -1
        self.swapped = False
        self.dragDelete = False


    def OnMotion(self, event, ctrl):
        index = self.imgCtrls.index(ctrl)
        if self.imgClicked != -1 and self.imgClicked in (index-1, index, index+1):
            ctrl = self.imgCtrls[self.imgClicked]
            if self.ctrlSize == None:
                self.ctrlSize = ctrl.GetSize()
            pos = ctrl.GetScreenPosition()
            size = ctrl.GetSize()
            sizerOffsetClicked = (self.imgClicked * (size[1]+4))
            sizerOffsetCursor = (index * (size[1]+4))
            upper = pos[1]
            lower = upper + size[1]

            rightEdge = pos[0] + self.imgWidth
            evPosY = event.GetPosition()[1] + pos[1]
            evPosX = event.GetPosition()[0] + pos[0]

            if platform.system() == 'Windows':
                upper += sizerOffsetClicked
                lower += sizerOffsetClicked
                evPosY += sizerOffsetCursor

            if evPosY < upper and self.imgClicked > 0:
                if not self.swapped:
                    self.SwapImages(self.imgClicked, self.imgClicked-1)
                    self.swappedIndex = self.imgClicked - 1
                    self.swapped = True
            elif evPosY > lower and self.imgClicked < len(self.images)-1:
                if not self.swapped:
                    self.SwapImages(self.imgClicked, self.imgClicked+1)
                    self.swappedIndex = self.imgClicked + 1
                    self.swapped = True
            elif evPosY < lower and evPosY > upper:
                if self.swapped:
                    self.SwapImages(self.imgClicked, self.swappedIndex)
                    self.swapped = False
                if evPosX > rightEdge:
                    diff = evPosX - rightEdge
                    newWidth = self.imgWidth - diff
                    if newWidth < 0:
                        newWidth = 0
                    ctrl.SetSize((newWidth, self.ctrlSize[1]))

                    if newWidth == 0:
                        self.dragDelete = True
                    else:
                        self.dragDelete = False
                else:
                    ctrl.SetSize(self.ctrlSize)
                    dragDelete = False


    def SwapImages(self, index1, index2):
        # get controls
        ctrl = self.imgCtrls[index1]
        swapCtrl = self.imgCtrls[index2]

        # get bitmaps
        clickedImg = ctrl.GetBitmap()
        swapImg = swapCtrl.GetBitmap()

        # swap bitmaps
        swapCtrl.SetBitmap(clickedImg)
        ctrl.SetBitmap(swapImg)

        # swap images in list
        tmp = self.images.pop(index1)
        self.images.insert(index2, tmp)
        self.LayoutAndFit()


    def LayoutAndScroll(self):
        self.SetAutoLayout(1)
        self.SetupScrolling(scroll_x=False, scroll_y=True)

    def LayoutAndFit(self):
        self.mainSizer.Layout()
        self.FitInside()

    def AddImage(self,imagePath,addToList=True):
        if imagePath.endswith((SUPPORTED_IMAGE_EXTENSIONS)):
            if addToList:
                self.images.append(imagePath)
            self.UpdateImages()
            self.dataSource.ImageAdded(imagePath)

    def UpdateImages(self):
        self.mainSizer.Clear(True)
        self.imgCtrls = []
        self.__LoadImages()
        self.LayoutAndScroll()

    def __LoadImages(self):
        sizerH = 0
        maxH = 0

        imgWidth = self.size[0] - 20
        self.imgWidth = imgWidth
        images = []
        # load images and determine needed height for sizer
        for imgPath in self.images:
            # get resized version of current image and save it temporary
            curImg = self.__ScaleImage(imgPath, imgWidth)
            curImgCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(curImg))
            curImgCtrl.Bind(wx.EVT_LEFT_DOWN, lambda event, ctrl=curImgCtrl: self.OnLeftDown(event,ctrl))
            curImgCtrl.Bind(wx.EVT_LEFT_UP, lambda event, ctrl=curImgCtrl: self.OnLeftUp(event,ctrl))
            curImgCtrl.Bind(wx.EVT_MOTION, lambda event, ctrl=curImgCtrl: self.OnMotion(event,ctrl))
            curImgCtrl.Bind(wx.EVT_LEFT_DCLICK, lambda event, ctrl=curImgCtrl: self.ImageDoubleClicked(event,ctrl))

            self.mainSizer.Add(curImgCtrl, flag=wx.ALL, border=2)
            self.imgCtrls.append(curImgCtrl)

    def ImageDoubleClicked(self, event, ctrl):
        index = self.imgCtrls.index(ctrl)
        wx.CallAfter(self.__ImageDeletion, index)

    def ClearImageView(self, event=None):
        dlg = wx.MessageDialog(self.parent, tr("msg_delete_all"), tr("delete_all"), style=wx.YES_NO|wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            for i in reversed(range(len(self.images))):
                self.__DeleteImage(i)

    def __ImageDeletion(self, index):
        selectedBmp = self.imgCtrls[index].GetBitmap()
        # blur preview of image that is beeing dragged
        img = self.__ScaleImage(self.images[index], self.imgWidth, blurred=True)
        bmp = wx.BitmapFromImage(img)
        self.imgCtrls[index].SetBitmap(bmp)
        dlg = wx.MessageDialog(self, tr("msg_delete_img"), tr("title_delete_img"), style=wx.YES_NO|wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.__DeleteImage(index)
        else:
            self.imgCtrls[index].SetBitmap(selectedBmp)

    def __DeleteImage(self,index):
        del self.images[index]
        ctrl = self.imgCtrls.pop(index)
        wx.CallAfter(self.Unbind, wx.EVT_LEFT_UP, source=ctrl)
        ctrl.Hide()
        self.mainSizer.Detach(ctrl)
        self.LayoutAndFit()
        #self.UpdateImages()
        self.dataSource.ImageDeleted(index)


    def __ScaleImage(self, imgPath, width, blurred=False):
        #img = wx.Image(imgPath)
        img = Image.open(imgPath)
        # scale the image, preserving the aspect ratio
        w = img.size[0]
        h = img.size[1]

        newW = width
        newH = width * h / w
        img = img.resize((newW,newH))

        if blurred:
            img = img.filter(ImageFilter.GaussianBlur(radius=20))
            mask = Image.new((img.mode), (img.size))
            img = Image.blend(img, mask, 0.3)

        image = wx.EmptyImage(newW,newH)
        image.SetData(img.convert("RGB").tostring())
        image.SetAlphaData(img.convert("RGBA").tostring()[3::4])

        return image
