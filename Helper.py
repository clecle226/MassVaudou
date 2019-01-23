import subprocess
from subprocess import PIPE

class DeviceHelper():
    Processus = None
    Log = None
    IMEI1 = None
    IMEI2 = None
    SerialNumber = None
    InProc = None
    OutProc = None


    def __init__(self):
        self.Processus = subprocess.Popen("./platform-tools/adb shell", stdin=PIPE, stdout=PIPE)
    def ShellIn(self, Message):
        #out, err = self.Processus.communicate(Message, 15)
        self.Processus.stdin.write(str.encode(Message)
        print(str.decode(self.Processus.stdout.read())
    #def ShellOut(self):
