import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QAbstractItemView
from PySide2.QtCore import QFile, QObject, Signal, Slot, QDir, QObject, SIGNAL
from ui_mainwindow import Ui_MainWindow
import Helper
import csv
import requests
import zipfile
import platform
import io

global ExtenalClassMasterisation

class MainWindow(QMainWindow):
    Manager = None
    DataParse = {}

    def __init__(self):
        DossierActuel = QDir(QDir.currentPath())
        if not DossierActuel.cd("platform-tools"):
            url = None
            if platform.system() == "Windows":
                url = 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip'
            elif platform.system() == "Darwin":#MacOS
                url = 'https://dl.google.com/android/repository/platform-tools-latest-darwin.zip' 
            elif platform.system() == "Linux":
                url = 'https://dl.google.com/android/repository/platform-tools-latest-linux.zip' 
            reply = requests.get(url)
            zip_ref = zipfile.ZipFile(io.BytesIO(reply.content))
            zip_ref.extractall(DossierActuel.absolutePath())
            zip_ref.close()
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.Manager = Helper.ManagerDevice(self)
        self.Manager.start()

        self.ui.SelectScript.clicked.connect(self.LoadScripts)
        self.ui.SelectData.clicked.connect(self.LoadData)
        self.ui.ButtonAllGo.clicked.connect(self.ButtonAllGo)

        self.ui.tableWidget.setColumnCount(3)
        self.ui.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget.setHorizontalHeaderLabels(["ID", "Donnée Vérifié", "Etat du script"])
        self.ui.tableWidget.itemActivated.connect(self.ClickDevice)
        #QObject.connect(self.ui.tableWidget, SIGNAL ('itemClicked(item)'), self.ClickDevice)

    def ButtonAllGo(self):
        self.Manager.goDevice()

    def ClickDevice(self, item):
        ClickDevice = (self.ui.tableWidget.item(item.row(),0).text())
        self.ChangerLogTerminal(self.Manager.GetLog(ClickDevice))

    def LoadData(self):
        result = (QFileDialog.getOpenFileName(self))[0]
        if result == None:
            return None
        self.ui.PathData.setText(result)
        with open(result, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter='\t')
            #, quotechar=''
            VarName = []
            for row in spamreader:
                if len(VarName) == 0:
                    VarName = row
                else:
                    tmp = {}
                    i = 0
                    for var in row:
                        tmp[VarName[i]] = var
                        i += 1
                    if VarName.__contains__("DeviceID"):
                        DeviceIDIndex = VarName.index("DeviceID")
                        self.DataParse[row[DeviceIDIndex]] = tmp
                    elif VarName.__contains__("IMEI"):
                        DeviceIDIndex = VarName.index("IMEI")
                        self.DataParse[row[DeviceIDIndex]] = tmp
                    else:
                        print("Error")
        self.Manager.SendData(self.DataParse)
        self.Manager.UpdateViewListDevice()
    def UpdateViewListDevice(self):
        self.Manager.UpdateViewListDevice()
    def LoadScripts(self):
        Result = QFileDialog.getExistingDirectory(self)
        DirScript = QDir(Result)
        if DirScript.cd("Script"):
            if not self.ui.PathData.text().strip() != "":####UnloadScripts
                ListScript = DirScript.entryInfoList(["*.py"])
                for mod in ListScript:
                    # removes module from the system
                    mod_name = mod.baseName()
                    if mod_name in sys.modules:
                        #ListFunction = dir(mod_name)
                        del sys.modules[mod_name]
                        Helper.DeviceHelper.FunctionCallDict = {}
            self.ui.PathScript.setText(Result)
            self.ui.LogTerminal.setText(DirScript.absolutePath())
            sys.path.append(DirScript.absolutePath())
            DirScript.entryInfoList(["*.py"])
            for Script in ListScript:
                __import__(Script.baseName())
                ListFunction = Helper.DeviceHelper.FunctionCallDict.values()
                for item in ListFunction:    
                    self.ui.ListScript.addItem(item)
                #for function in ListFunction:
                #    Helper.DeviceHelper.function = types.MethodType(function,Helper.DeviceHelper)
                    #setattr(Helper.DeviceHelper, ScriptModule.__dict__[function], function)
                    #Helper.DeviceHelper.__dict__[function] = function
            ListVar = []
            f = open(QDir(Result).absoluteFilePath("Var.txt"),'r')
            for ligne in f.readlines():
                ListVar.append(ligne)
            f.close()
            Helper.add_variable_Masterisation(ListVar)
            self.Manager.ReloadTerminaux()
        else:
            #Error
            print("Error")
    def ChangerLogTerminal(self, Content = ""):
        self.ui.LogTerminal.setText(Content)
    def __del__(self):
        self.Manager.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.aboutToQuit.connect(app.deleteLater)
    app.exec_()
    #sys.exit()
