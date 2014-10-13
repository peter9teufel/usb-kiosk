import wx, platform
from PIL import Image
import wx.lib.scrolledpanel as scrolled
from packages.lang.Localizer import *
import sys

################################################################################
# SCROLLABLE IMAGE VIEW ########################################################
################################################################################
class ScrollableImageView(scrolled.ScrolledPanel):
    def __init__(self,parent,id,size,images,dataSource,cols=2):
        scrolled.ScrolledPanel.__init__(self,parent,id,size=size)
        self.parent = parent
        self.size = size
        self.cols = cols
        self.dataSource = dataSource
        self.mainSizer = wx.GridBagSizer()
        self.images = images
        self.__LoadImages()
        self.SetSizer(self.mainSizer)
        self.LayoutAndScroll()

    def LayoutAndScroll(self):
        self.SetAutoLayout(1)
        self.SetupScrolling(scroll_x=False, scroll_y=True)

    def AddImage(self,imagePath):
        self.images.append(imagePath)
        self.UpdateImages()

    def UpdateImages(self):
        self.mainSizer.Clear(True)
        self.__LoadImages()
        self.LayoutAndScroll()

    def __LoadImages(self):
        row = 0
        col = 0

        sizerH = 0
        maxH = 0

        imgWidth = self.size[0] / self.cols - 4
        images = []

        # load images and determine needed height for sizer
        cnt = 0
        for imgPath in self.images:
            # get resized version of current image and save it temporary
            curImg = self.__ScaleImage(imgPath, imgWidth)
            curImgCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(curImg))
            curImgCtrl.Bind(wx.EVT_LEFT_DOWN, lambda event, index=cnt: self.ImageClicked(event,index))
            self.mainSizer.Add(curImgCtrl,(row,col), flag=wx.ALL, border=2)

            # position for next image
            col = (col + 1) % self.cols
            if col == 0:
                row += 1

    def ImageClicked(self, event, index):
        wx.CallAfter(self.__ImageDeletion, index)


    def __ImageDeletion(self, index):
        dlg = wx.MessageDialog(self, tr("msg_delete_img"), tr("title_delete_img"), style=wx.YES_NO|wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            del self.images[index]
            self.UpdateImages()
            self.dataSource.ImageDeleted(index)


    def __ScaleImage(self, imgPath, width):
        #img = wx.Image(imgPath)
        img = Image.open(imgPath)
        # scale the image, preserving the aspect ratio
        w = img.size[0]
        h = img.size[1]

        newW = width
        newH = width * h / w
        img.thumbnail((newW,newH))

        image = wx.EmptyImage(newW,newH)
        image.SetData(img.convert("RGB").tostring())
        image.SetAlphaData(img.convert("RGBA").tostring()[3::4])

        return image
