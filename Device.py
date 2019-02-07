from PySide2.QtCore import QDir, Qt
from PySide2.QtWidgets import QTableWidgetItem, QVBoxLayout, QLabel, QLayout, QListWidgetItem
from PySide2.QtGui import QIcon, QPalette
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

    #Manager = None
    VBoxLayout = None
    #ResultFunction = {}
    ResultFunctionItem = []

    def __init__(self, serialNo, PathProject):
        Thread.__init__(self)
        self.SerialNo = serialNo

        self.ItemId = QTableWidgetItem(str(self.SerialNo))
        self.ItemId.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )
        self.ItemData = QTableWidgetItem("")
        self.ItemData.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )
        self.ItemProcess = QTableWidgetItem("")
        self.ItemProcess.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )
        self.UpdateItem()

        #self.Manager = ManagerNode
        self.VBoxLayout = QVBoxLayout()
        #self.VBoxLayout.setSizeConstraint(QLayout.SetFixedSize)
        self.VBoxLayout.addWidget(QLabel("Initialisation log de "+self.SerialNo))

        self.HelperNode = DeviceHelper(serialNo, PathProject, self)
        self.VerifyData()
        i = 1
        while i <= len(self.HelperNode.FunctionCallDict):
            self.ResultFunctionItem.append(QListWidgetItem(self.HelperNode.FunctionCallDict[i]))
            i = i+1


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
            while i <= len(self.HelperNode.FunctionCallDict):
                functioCallable = getattr(self.HelperNode, self.HelperNode.FunctionCallDict[i])
                result = functioCallable()
                if result == 1:
                    pal = QPalette()
                    pal.setColor(QPalette.Background, Qt.green)
                    self.ResultFunctionItem[self.HelperNode.FunctionCallDict[i]].setPalette(pal)
                i = i+1
            self.StateProc = 2
            self.UpdateItem()

    def GetState(self):
        return self.SerialNo, self.StateData, self.StateProc
    
    def GetItem(self):
        return self.ItemId, self.ItemData, self.ItemProcess

    def GetIMEI(self):
        return self.HelperNode.GetIMEI()

    def GetLayout(self):
        return self.VBoxLayout

    def GetListItemFunction(self):
        return self.ResultFunctionItem

    def VerifyData(self):
        self.StateData = True
        for item in self.HelperNode.ListVariable:
            if item not in self.HelperNode.Variable.keys():
                self.StateData = False
        self.UpdateItem()

    def SetData(self, Data):
        self.HelperNode.Variable = Data
        self.VerifyData()

    def AddLog(self, Text, Sens="Entrant"):
        tmpLabel = QLabel(Text)
        pal = QPalette()
        if Sens == "Entrant":#Entrant : Device -> Computer
            pal.setColor(QPalette.Background, Qt.green)
        elif Sens == "Sortant":#Sortant : Computer -> Device
            pal.setColor(QPalette.Background, Qt.red)
        tmpLabel.setAutoFillBackground(True)
        tmpLabel.setPalette(pal)
        self.VBoxLayout.addWidget(tmpLabel)

