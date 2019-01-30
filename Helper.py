import subprocess
import time
from threading import Thread
import re
import types
import os
from functools import wraps
from PySide2.QtCore import QDir
from PySide2.QtWidgets import QTableWidgetItem
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt
import platform

class DeviceHelper():
    Processus = None
    Log = ""
    IMEI1 = None
    IMEI2 = None
    SerialNumber = ""

    FunctionCallDict = {}
    ListVariable = []
    Variable = dict()


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
        self.IMEI1 = (tradParcell.replace(".","")).strip()
        return self.IMEI1
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
    StateProc = 0 # O= Non commencé, 1 = en cours, 2 = Fini
    ValeurScriptExecution = 0

    ItemId = None
    ItemData = None
    ItemProcess = None

    def __init__(self, serialNo):
        Thread.__init__(self)
        self.SerialNo = serialNo
        self.HelperNode = DeviceHelper(serialNo)
        self.VerifyData()

        self.ItemId = QTableWidgetItem(str(id))
        self.ItemId.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )
        self.ItemData = QTableWidgetItem()
        self.ItemData.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )
        self.ItemProcess = QTableWidgetItem()
        self.ItemProcess.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )
        if not self.StateData:
            self.ItemData.setIcon(QIcon(".\\Asset\\red.svg"))
        else:
            self.ItemData.setIcon(QIcon(".\\Asset\\green.svg"))
        if self.StateProc == 2:
            self.ItemProcess.setIcon(QIcon(".\\Asset\\green.svg"))
        elif self.StateProc == 1:
            self.ItemProcess.setIcon(QIcon(".\\Asset\\orange.svg"))
        else:
            self.ItemProcess.setIcon(QIcon(".\\Asset\\red.svg"))
    def run(self):
        functioCallable = getattr(self.HelperNode, self.HelperNode.FunctionCallDict[1])
        functioCallable()

    def GetState(self):
        return self.SerialNo, self.StateData, self.StateProc

    def GetIMEI(self):
        return self.HelperNode.GetIMEI()

    def VerifyData(self):
        self.StateData = True
        for item in self.HelperNode.ListVariable:
            if item not in self.HelperNode.Variable.keys():
                self.StateData = False
    def SetData(self, Data):
        self.HelperNode.Variable = Data
        self.VerifyData()


class ManagerDevice(Thread):
    ListDevice = dict()
    ThreadUpdateList  = None
    Continue = True
    CallUi = None
    DataParse = None

    def __init__(self, Ui):
        Thread.__init__(self)
        self.CallUi = Ui

    def UpdateViewListDevice(self):
        self.CallUi.ui.tableWidget.setRowCount(0)
        self.CallUi.ui.tableWidget.setRowCount(len(self.ListDevice.keys()))
        i = 0
        for device in self.ListDevice.keys():
            id, data, process = (self.ListDevice[device]).GetState()

            self.CallUi.ui.tableWidget.setItem(i, 1, itemTwo)
            self.CallUi.ui.tableWidget.setItem(i, 2, itemThree)


#            self.CallUi.ui.tableWidget.setItem(i, 1, QTableWidgetItem(QLabel(id)))
#            self.CallUi.ui.tableWidget.setItem(i, 2, QTableWidgetItem(QLabel(id)))
            i += 1


    def run(self):
        while self.Continue:
            tmpList = []
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
            self.UpdateViewListDevice()
            time.sleep(2)
    def AddDevice(self, Serial):
        self.ListDevice[Serial] = Device(Serial)
        #self.CallUi.ui.ListScript.addItem(Serial)
        self.UpdateViewListDevice()
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

    def SendData(self, ListVariable):
        self.DataParse = ListVariable
        for deviceID in self.DataParse.keys():
            print(deviceID)
            if self.ListDevice.keys().__contains__(deviceID):
                self.ListDevice[deviceID].SetData(self.DataParse[deviceID])
            else:
                for deviceIMEI in self.ListDevice.keys():
                    if self.ListDevice[deviceIMEI].GetIMEI() == deviceID:
                        self.ListDevice[deviceIMEI].SetData(self.DataParse[deviceID])

