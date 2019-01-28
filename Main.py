import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel
from PySide2.QtCore import QFile, QObject, Signal, Slot, QDir
from ui_mainwindow import Ui_MainWindow
import Helper
import requests
import zipfile
import platform
import io

global ExtenalClassMasterisation

class MainWindow(QMainWindow):
    Manager = None

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

        self.Manager = Helper.ManagerDevice()
        self.Manager.start()

        self.ui.SelectScript.clicked.connect(self.LoadFormFile)
        self.ui.SelectData.clicked.connect(self.LoadFormFile)
        self.ui.ButtonAllGo.clicked.connect(self.ButtonAllGo)

    def ButtonAllGo(self):
        self.Manager.goDevice()

    def LoadFormFile(self):
        result = QFileDialog.getExistingDirectory(self)
        if(self.sender() == self.ui.SelectScript):
            self.LoadScripts(result)
        elif(self.sender() == self.ui.SelectData):
            self.ui.PathData.setText(result)

    def LoadScripts(self, Result = None):
        DirScript = QDir(Result)
        if DirScript.cd("Script"):
            if not self.ui.PathData.text().strip() != "":####UnloadScripts
                ListScript = DirScript.entryInfoList(["*.py"])
                for mod in ListScript:
                    # removes module from the system
                    mod_name = mod.baseName()
                    if mod_name in sys.modules:
                        ListFunction = dir(mod_name)
                        del sys.modules[mod_name]
                        for function in ListFunction:
                            del Helper.DeviceHelper.__dict__[function]
                    self.ui.ListScript.addItem(mod.fileName())
            self.ui.PathScript.setText(Result)
            self.ui.LogTerminal.setText(DirScript.absolutePath())
            sys.path.append(DirScript.absolutePath())
            DirScript.entryInfoList(["*.py"])
            for Script in ListScript:
                __import__(Script.baseName())
                ListFunction = dir(Script.baseName())
                #for function in ListFunction:
                #    Helper.DeviceHelper.function = types.MethodType(function,Helper.DeviceHelper)
                    #setattr(Helper.DeviceHelper, ScriptModule.__dict__[function], function)
                    #Helper.DeviceHelper.__dict__[function] = function
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
