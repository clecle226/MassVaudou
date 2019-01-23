#import subprocess
#from subprocess import PIPE
from PySide2.QtCore import QProcess, QByteArray, QObject

class DeviceHelper():
    Processus = None
    Log = None
    IMEI1 = None
    IMEI2 = None
    SerialNumber = None
    InProc = None
    OutProc = None


    def __init__(self):
        self.Processus = QProcess()
        print(self.Processus.error())
        self.Processus.start("echo test")
        print(self.Processus.readAll())
        print(self.Processus.error())
        self.Processus.write(str.encode("ls -la"))
        print(self.Processus.readAllStandardError())
        if not self.Processus.waitForStarted():
            print("rhaaaaaaaa")
        else:
            print(self.Processus.state())
            print(self.Processus.readAll())
        #self.Processus = subprocess.Popen("./platform-tools/adb shell", stdin=PIPE, stdout=PIPE)
    def ShellIn(self, Message):
        self.Processus.write(str.encode(Message))
        print(self.Processus.readAll())
        #out, err = self.Processus.communicate(Message, 15)
        #self.Processus.stdin.write(str.encode(Message))
        #while True:
        #    line = self.Processus.stdout.readline()
        #    if line != '':
                #the real code does filtering here
        #        print("test:"+line.rstrip())
        #    else:
        #        break
        #print( (self.Processus.stdout.read()).decode("utf-8") )
    #def ShellOut(self):
