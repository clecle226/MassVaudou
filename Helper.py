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
import xml.etree.ElementTree  as ET

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
        self.SerialNumber = serialNo
        self.GetIMEI()
        
    def ShellIn(self, Message, PrintLog = True):
        DossierActuel = QDir(QDir.currentPath())
        DossierActuel.cd("platform-tools")
        PathExecutable = ""
        if platform.system() == "Windows":
            PathExecutable = DossierActuel.absoluteFilePath("adb.exe")
        else:
            PathExecutable = DossierActuel.absoluteFilePath("adb")
        result = subprocess.run(PathExecutable+" shell "+Message, env={**os.environ, 'ANDROID_SERIAL': self.SerialNumber}, capture_output=True)
        self.Log += "<--"+str(Message)
        if PrintLog:
            self.Log += "-->"+str(result.stdout)+str("\r\n")
        return str(result.stdout, 'utf-8')
    def ClickOnNode(self, TextNode = "", IdNode = "", IdItemMenu= ""):
        ActualScreen = self.ShellIn("uiautomator dump /dev/tty", False)
        result = re.findall("<node .*? resource-id=\""+re.escape(IdNode)+"\" .*? bounds=\"\[(\d*),(\d*)\]\[(\d*),(\d*)\]\" />", ActualScreen)
        #result = re.findall(r"resource-id=\""+re.escape(IdNode)+"\" .*? bounds=\"\[(\d+),(\d+)\]\[(\d+),(\d+)\]\" \/>", ActualScreen)
        if len(result) >= 1:
            if result[0].__len__() == 4:
                MidX = (int(result[0][0])+int(result[0][2]))/2
                MidY = (int(result[0][1])+int(result[0][3]))/2
                self.ShellIn("input tap "+str(int(MidX))+" "+str(int(MidY)))
    def ClickOnIndexMenu(self, IdIndex = "", IdMenu = "", TypeItem = ""):
        ActualScreen = self.ShellIn("uiautomator dump /dev/tty", False)
        result = re.findall("<node .*? resource-id=\""+re.escape(IdMenu)+"\" .*?>.*?<node index=\""+re.escape(IdIndex)+"\".*?><node .*? resource-id=\""+re.escape(TypeItem)+"\" .*? bounds=\"\[(\d*),(\d*)\]\[(\d*),(\d*)\]\" /></node>.*?</node>", ActualScreen)
        if len(result) >= 1:
            if result[0].__len__() == 4:
                MidX = (int(result[0][0])+int(result[0][2]))/2
                MidY = (int(result[0][1])+int(result[0][3]))/2
                self.ShellIn("input tap "+str(int(MidX))+" "+str(int(MidY)))
    def HasNode(self, IdNode="", Timeout = 15):
        FinalTimestamp = time.time()+Timeout
        Succesfull = False
        while not Succesfull and time.time() <= FinalTimestamp:
            ActualScreen = self.ShellIn("uiautomator dump /dev/tty", False)
            result = re.findall("<node .*? resource-id=\""+re.escape(IdNode)+"\"", ActualScreen)
            if result.__len__() != 0:
                return True
        return False
    def ClearTextEdit(self, IdTextEdit = ""):
        ActualScreen = (re.findall("<.*>", self.ShellIn("uiautomator dump /dev/tty", False)))[0]
        tree = ET.fromstring(ActualScreen)

        #if IdTextEdit != ".*?":
        #    IdTextEdit = re.escape(IdTextEdit)
        #result = re.findall("<node .*? text=\"(.*?)\".*?resource-id=\""+IdTextEdit+"\" class=\"android\.widget\.EditText\" .*? />", ActualScreen)
        #print(result)
       # NbrChar = len(result[0][0])
        NbrChar = len((tree.findall(".//*[@resource-id='"+IdTextEdit+"']")[0]).attrib['text'])
        repeatInput = ""
        i = 0
        while i <= NbrChar:
            repeatInput += " KEYCODE_DEL"
            i += 1
        self.ShellIn("input keyevent KEYCODE_MOVE_END")
        self.ShellIn("input keyevent --longpress"+repeatInput)


    def GetIMEI(self):
        rawResult = self.ShellIn("service call iphonesubinfo 1", False)
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

    ItemId = QTableWidgetItem()
    ItemData = QTableWidgetItem()
    ItemProcess = QTableWidgetItem()

    def __init__(self, serialNo):
        Thread.__init__(self)
        self.SerialNo = serialNo
        self.HelperNode = DeviceHelper(serialNo)
        self.VerifyData()

        self.ItemId = QTableWidgetItem(str(self.SerialNo))
        self.ItemId.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )
        self.ItemData = QTableWidgetItem("")
        self.ItemData.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )
        self.ItemProcess = QTableWidgetItem("")
        self.ItemProcess.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )
        self.UpdateItem()

    def UpdateItem(self):
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
        if self.StateProc == 0:
            self.StateProc = 1
            self.UpdateItem()
            i = 1
            while i <= self.HelperNode.FunctionCallDict.__len__():
                functioCallable = getattr(self.HelperNode, self.HelperNode.FunctionCallDict[i])
                functioCallable()
                i = i+1
            self.StateProc = 2
            self.UpdateItem()

    def GetState(self):
        return self.SerialNo, self.StateData, self.StateProc
    
    def GetItem(self):
        return self.ItemId, self.ItemData, self.ItemProcess

    def GetIMEI(self):
        return self.HelperNode.GetIMEI()

    def VerifyData(self):
        self.StateData = True
        for item in self.HelperNode.ListVariable:
            if item not in self.HelperNode.Variable.keys():
                self.StateData = False
        self.UpdateItem()

    def SetData(self, Data):
        self.HelperNode.Variable = Data
        self.VerifyData()

    def GetLog(self):
        return self.HelperNode.Log


class ManagerDevice(Thread):
    ListDevice = dict()
    ThreadUpdateList  = None
    Continue = True
    CallUi = None
    DataParse = None

    DeviceSelected = None

    def __init__(self, Ui):
        Thread.__init__(self)
        self.CallUi = Ui

    def UpdateViewListDevice(self):
        #self.CallUi.ui.tableWidget.setRowCount(0)
        #self.CallUi.ui.tableWidget.setRowCount(len(self.ListDevice.keys()))
        i = 0
        #ListIdDeviceTable = []
        #LenRow = self.CallUi.ui.tableWidget.rowCount()
        #while i < LenRow:
        #    ListIdDeviceTable.append(self.CallUi.ui.tableWidget.item(i, 0))
        
        #for device in self.ListDevice.keys():
        #    id, data, process = (self.ListDevice[device]).GetState()

        #    self.CallUi.ui.tableWidget.setItem(i, 1, itemTwo)
        #    self.CallUi.ui.tableWidget.setItem(i, 2, itemThree)


#            self.CallUi.ui.tableWidget.setItem(i, 1, QTableWidgetItem(QLabel(id)))
#            self.CallUi.ui.tableWidget.setItem(i, 2, QTableWidgetItem(QLabel(id)))
        #    i += 1


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
            self.GetLog()
            time.sleep(2)


    def AddDevice(self, Serial):
        self.ListDevice[Serial] = Device(Serial)

        Itemid, data, process = (self.ListDevice[Serial]).GetItem()
        self.CallUi.ui.tableWidget.setRowCount(self.CallUi.ui.tableWidget.rowCount()+1)
        self.CallUi.ui.tableWidget.setItem(self.CallUi.ui.tableWidget.rowCount()-1, 0, Itemid)
        self.CallUi.ui.tableWidget.setItem(self.CallUi.ui.tableWidget.rowCount()-1, 1, data)
        self.CallUi.ui.tableWidget.setItem(self.CallUi.ui.tableWidget.rowCount()-1, 2, process)

        #self.UpdateViewListDevice()
    def RemoveDevice(self, Serial):
        ItemId, _, _ = (self.ListDevice[Serial]).GetItem()
        self.CallUi.ui.tableWidget.removeRow(self.CallUi.ui.tableWidget.row(ItemId))
        del self.ListDevice[Serial]

    def goDevice(self, Serial = None):
        if Serial != None:
            self.ListDevice[Serial].run()
        else:
            for item in self.ListDevice:
                self.ListDevice[item].run()
    def CleanAll(self):
        fixedKeys = set(self.ListDevice.keys())
        for key in fixedKeys:
            self.RemoveDevice(key)
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
            if self.ListDevice.keys().__contains__(deviceID):
                self.ListDevice[deviceID].SetData(self.DataParse[deviceID])
            else:
                for deviceIMEI in self.ListDevice.keys():
                    if self.ListDevice[deviceIMEI].GetIMEI() == deviceID:
                        self.ListDevice[deviceIMEI].SetData(self.DataParse[deviceID])
    
    def GetLog(self, Serial = None):
        if Serial != None:
            self.DeviceSelected = Serial
            strlog = self.ListDevice[self.DeviceSelected].GetLog()
            self.CallUi.ui.LogTerminal.setText(strlog)
            return strlog

