import subprocess

class DeviceHelper():
    Processus = None
    Log = None
    IMEI1 = None
    IMEI2 = None
    SerialNumber = None


    def __init__(self):
        self.Processus = subprocess.Popen(".\\platform-tools\\adb.exe shell", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    def ShellIn(self, Message):
        self.Processus.stdin.write(str.encode(Message))
        #print(self.Processus.stdout.read())
        print(self.Processus.communicate()[0])
#def ShellOut(self):
