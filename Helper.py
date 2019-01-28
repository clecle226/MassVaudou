import subprocess
import time
from threading import Thread
import re
import types
import os
from functools import wraps
from PySide2.QtCore import QDir
import platform

class DeviceHelper():
    Processus = None
    Log = ""
    IMEI1 = None
    IMEI2 = None
    SerialNumber = ""

    FunctionCallDict = []
    ListVariable = []


    def __init__(self, serialNo):
        #self.Log += ""
        # Search Run popen in parallels
        #self.Processus = subprocess.Popen(".\\platform-tools\\adb.exe shell", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        self.SerialNumber = serialNo
        self.GetIMEI()
        #print(self.Processus.poll())
        #self.Processus.stdin.write(str.encode("am start -p com.android.chrome\n"))
        #self.Processus = subprocess.Popen(".\\platform-tools\\adb.exe shell", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    def ShellIn(self, Message):
        DossierActuel = QDir(QDir.currentPath())
        DossierActuel.cd("platform-tools")
        PathExecutable = ""
        if platform.system() == "Windows":
            PathExecutable = DossierActuel.absoluteFilePath("adb.exe")
        else:
            PathExecutable = DossierActuel.absoluteFilePath("adb")
        result = subprocess.run(PathExecutable+" shell "+Message, env={**os.environ, 'ANDROID_SERIAL': self.SerialNumber}, capture_output=True)
        self.Log += str(result.stdout)
        return str(result.stdout)
    def ClickOnNode(self, NameNode):
       print(self.ShellIn("uiautomator dump /dev/tty"))
    def GetIMEI(self):
        rawResult = self.ShellIn("service call iphonesubinfo 1")
        tradParcell = "".join(re.findall(r"\'(.*?)\'", rawResult))
        self.IMEI1 = tradParcell.replace(".","")
#def ShellOut(self):



def add_function_Masterisation(Ordre):
    def real_decorator(func):
        setattr(DeviceHelper, func.__name__, func)
        DeviceHelper.FunctionCallDict[Ordre] = func.__name__
        def wrapper(*args, **kw):
            return func(*args, **kw)
        return wrapper
    return real_decorator
    
def add_variable_Masterisation(ListVariable):
    DeviceHelper.ListVariable = ListVariable

class Device(Thread):
    SerialNo = ""
    HelperNode = None
    DataPerso = None
    StateData = True
    ValeurScriptExecution = 0

    def __init__(self, serialNo):
        Thread.__init__(self)
        self.SerialNo = serialNo
        self.HelperNode = DeviceHelper(serialNo)
        if len(self.HelperNode.ListVariable) != 0:
            StateData = False

    def run(self):
        functioCallable = getattr(self.HelperNode, self.HelperNode.FunctionCallDict[1])
        functioCallable()

    def GetState(self):
        return {SerialNo, StateData,}


class ManagerDevice(Thread):
    ListDevice = dict()
    ThreadUpdateList  = None
    Continue = True
    CallUi = None

    def __init__(self, Ui):
        Thread.__init__(self)
        self.CallUi = Ui

    def UpdateViewListDevice(self):
        for device in self.ListDevice.keys:

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
                self.AddDevice(item)
            #Delete de la ListDevice
            RemoveList = list(set(self.ListDevice.keys())-set(tmpList))
    def AddDevice(self, Serial):
        self.ListDevice[Serial] = Device(Serial)
        self.CallUi.ui.ListScript.addItem(Serial)
    def goDevice(self, Serial = None):
        
        if Serial != None:
            self.ListDevice[Serial].run()
        else:
            for item in self.ListDevice:
                self.ListDevice[item].run()
    def CleanAll(self):
        fixedKeys = set(self.ListDevice.keys())
        for key in fixedKeys:
            del self.ListDevice[key]
    def ReloadTerminaux(self):
        fixedKeys = set(self.ListDevice.keys())
        self.CleanAll()
        for key in fixedKeys:
            self.AddDevice(key)
    def stop(self):
        self.Continue = False
