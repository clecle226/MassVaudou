import subprocess
import time
from threading import Thread
import re

class DeviceHelper():
    Processus = None
    Log = ""
    IMEI1 = None
    IMEI2 = None
    SerialNumber = None


    def __init__(self):
        #self.Log += ""
        # Search Run popen in parallels
        #self.Processus = subprocess.Popen(".\\platform-tools\\adb.exe shell", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        print("")
        #print(self.Processus.poll())
        #self.Processus.stdin.write(str.encode("am start -p com.android.chrome\n"))
        #self.Processus = subprocess.Popen(".\\platform-tools\\adb.exe shell", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    def ShellIn(self, Message):
        result = subprocess.run(".\\platform-tools\\adb.exe shell "+Message)
        self.Log += str(result.stdout)
        return str(result.stdout)
    def ClickOnNode(self, NameNode):
        print(self.ShellIn("uiautomator dump /dev/tty"))
#def ShellOut(self):

class Device(Thread):
    SerialNo = ""

    def __init__(self, serialNo):
        Thread.__init__(self)
        self.SerialNo = serialNo
    def run(self):
        TestDevice.run()


class ManagerDevice(Thread):
    ListDevice = dict()
    ThreadUpdateList  = None
    Continue = True

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while self.Continue:
            tmpList = []
            time.sleep(5)
            result = subprocess.run(".\\platform-tools\\adb.exe devices", capture_output=True)

            for l in ((result.stdout).decode("utf-8")).splitlines():
                if re.match(r"(.*)\tdevice", l):
                    result = re.match(r"(.*)\tdevice", l)[1]
                    tmpList.append(result)
            #Ajout de la ListDevice
            AddList = list(set(tmpList)-set(self.ListDevice.keys()))
            for item in AddList:
                ListDevice[item] = Device(item)
            #Delete de la ListDevice
            RemoveList = list(set(self.ListDevice.keys())-set(tmpList))
            

    def stop(self):
        self.Continue = False
