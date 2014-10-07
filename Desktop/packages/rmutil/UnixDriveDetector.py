import threading, sys, os, time, platform, getpass
import wx
if platform.system() == "Linux":
    from wx.lib.pubsub import setupkwargs
    from wx.lib.pubsub import pub as Publisher
else:
    from wx.lib.pubsub import pub as Publisher

if platform.system() == "Linux":
    if 'fedora' in platform.dist():
        user = getpass.getuser()
        VOLUMES_PATH = "/run/media/" + user
    else:
        VOLUMES_PATH = "/media"
else:
    VOLUMES_PATH = "/Volumes"
bg_thread = None
runFlag = True
volumes = None

def waitForUSBDrive():
    # load current list of volumes
    global volumes
    volumes = os.listdir(VOLUMES_PATH)
    global bg_thread
    if bg_thread == None:
        bg_thread = BackgroundUSBDetection()
        bg_thread.daemon = True
        bg_thread.start()
        bg_thread.join()

# RESULT CALL --> wx.CallAfter(Publisher.sendMessage, 'usb_connected', path=drive_path)


### THREAD FOR ASYNC USB DETECTION ###
class BackgroundUSBDetection(threading.Thread):
    def __init__(self):
        self.run_event = threading.Event()
        threading.Thread.__init__(self, name="Mac_Drive_Detector")

    def run(self):
        print "Thread started..."
        global runFlag, volumes
        while runFlag:
            # check volumes
            curVols = os.listdir(VOLUMES_PATH)
            newVol = self.NewVolumes(volumes, curVols)
            # update list of volumes in case a volume was disconnected (e.g. retry plugging USB)
            volumes = curVols
            if len(newVol) > 0:
                wx.CallAfter(Publisher.sendMessage, 'usb_connected', path=VOLUMES_PATH + '/' + newVol[0])
                runFlag = False
            time.sleep(2)


    def NewVolumes(self, oldVolumes, curVolumes):
        newVol = []
        for volume in curVolumes:
            if not volume in oldVolumes:
                newVol.append(volume)
        return newVol


if __name__=='__main__':
    # load current list of volumes
    volumes = os.listdir(VOLUMES_PATH)
    waitForUSBDrive()
