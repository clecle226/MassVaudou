from PySide2.QtCore import QDir
from PySide2.QtWidgets import QTableWidgetItem
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt
from threading import Thread
from Helper import *


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

    def __init__(self, serialNo, PathProject):
        Thread.__init__(self)
        self.SerialNo = serialNo
        self.HelperNode = DeviceHelper(serialNo, PathProject)
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

