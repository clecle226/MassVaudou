from Device import *
from PySide2.QtWidgets import QTableWidgetItem

from threading import Thread
import re


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
            self.GetLog()
            time.sleep(2)


    def AddDevice(self, Serial):
        self.ListDevice[Serial] = Device(Serial,self.CallUi.ui.PathScript.text())

        Itemid, data, process = (self.ListDevice[Serial]).GetItem()
        self.CallUi.ui.tableWidget.setRowCount(self.CallUi.ui.tableWidget.rowCount()+1)
        self.CallUi.ui.tableWidget.setItem(self.CallUi.ui.tableWidget.rowCount()-1, 0, Itemid)
        self.CallUi.ui.tableWidget.setItem(self.CallUi.ui.tableWidget.rowCount()-1, 1, data)
        self.CallUi.ui.tableWidget.setItem(self.CallUi.ui.tableWidget.rowCount()-1, 2, process)

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

