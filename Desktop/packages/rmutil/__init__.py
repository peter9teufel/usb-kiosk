import ImageUtil, platform, StreamAddresses

if platform.system() == "Windows":
    import Win32DeviceDetector
elif platform.system() == "Darwin" or platform.system() == "Linux":
    import UnixDriveDetector
