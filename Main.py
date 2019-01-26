import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel
from PySide2.QtCore import QFile, QObject, Signal, Slot, QDir
from ui_mainwindow import Ui_MainWindow
import Helper
import csv

global ExtenalClassMasterisation

class MainWindow(QMainWindow):
    Manager = None
    DataParse = {}

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.Manager = Helper.ManagerDevice(self)
        self.Manager.start()

        self.ui.SelectScript.clicked.connect(self.LoadScripts)
        self.ui.SelectData.clicked.connect(self.LoadData)
        self.ui.ButtonAllGo.clicked.connect(self.ButtonAllGo)

    def ButtonAllGo(self):
        self.Manager.goDevice()

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
            print(self.DataParse)

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
