import subprocess
import time
from threading import Thread
import re
import types
import os

class DeviceHelper():
    Processus = None
    Log = ""
    IMEI1 = None
    IMEI2 = None
    SerialNumber = ""


    def __init__(self, serialNo):
        #self.Log += ""
        # Search Run popen in parallels
        #self.Processus = subprocess.Popen(".\\platform-tools\\adb.exe shell", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        self.SerialNumber = serialNo
        #print(self.Processus.poll())
        #self.Processus.stdin.write(str.encode("am start -p com.android.chrome\n"))
        #self.Processus = subprocess.Popen(".\\platform-tools\\adb.exe shell", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    def ShellIn(self, Message):
        result = subprocess.run(".\\platform-tools\\adb.exe shell "+Message, env={**os.environ, 'ANDROID_SERIAL': self.SerialNumber}, capture_output=True)
        self.Log += str(result.stdout)
        return str(result.stdout)
    def ClickOnNode(self, NameNode):
        (self.ShellIn("uiautomator dump /dev/tty"))
#def ShellOut(self):


def add_function_Masterisation(func):
    setattr(DeviceHelper, func.__name__, func)

class Device(Thread):
    SerialNo = ""
    HelperNode = None

    def __init__(self, serialNo):
        Thread.__init__(self)
        self.SerialNo = serialNo
        self.HelperNode = DeviceHelper(serialNo)

    def run(self):
        #DeviceHelper.run = types.MethodType( TestDevice.run, DeviceHelper )

        self.HelperNode.run()
        #prnit("")


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
                self.ListDevice[item] = Device(item)
            #Delete de la ListDevice
            RemoveList = list(set(self.ListDevice.keys())-set(tmpList))
            
    def goDevice(self, Serial = None):
        
        if Serial != None:
            self.ListDevice[Serial].run()
        else:
            for item in self.ListDevice:
                self.ListDevice[item].run()
    def stop(self):
        self.Continue = False
