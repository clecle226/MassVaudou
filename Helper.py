from subprocess import Popen, PIPE

class DeviceHelper():
    Processus = None
    Log = None
    IMEI1 = None
    IMEI2 = None
    SerialNumber = None

    def __init__(self):
        Processus = subprocess.Popen("adb shell")
    def ShellIn(self, Message):
        Processus.communicate(Message, time)

    #def ShellOut(self):
