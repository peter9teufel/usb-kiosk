import os

def write(msg):
    from os.path import expanduser
    home = expanduser("~")
    appPath = home + '/.usb_kiosk/'
    logPath = appPath + 'log/'
    if not os.path.isdir(logPath):
        os.mkdir(logPath)

    logfile = logPath + 'kiosk.log'

    if os.path.isfile(logfile):
        __appendToLog(logfile, msg)
    else:
        __createAndWrite(logfile, msg)


def __createAndWrite(logfile, msg):
    with open(logfile, 'w') as f:
        f.write(msg + '\n')

def __appendToLog(logfile, msg):
    with open(logfile, 'a') as f:
        f.write(msg + '\n')
