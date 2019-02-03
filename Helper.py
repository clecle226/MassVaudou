import subprocess
import re
import types
import os
from functools import wraps
import platform
import xml.etree.ElementTree  as ET
from PySide2.QtCore import QDir
import time

class DeviceHelper():
    Processus = None
    Log = ""
    IMEI1 = None
    IMEI2 = None
    SerialNumber = ""

    FunctionCallDict = {}
    ListVariable = []
    Variable = dict()

    PathProject = ""


    def __init__(self, serialNo, pathProject):
        self.SerialNumber = serialNo
        self.PathProject = pathProject
        self.GetIMEI()

    def CallADB(self, Message):
        DossierActuel = QDir(QDir.currentPath())
        DossierActuel.cd("platform-tools")
        PathExecutable = ""
        if platform.system() == "Windows":
            PathExecutable = DossierActuel.absoluteFilePath("adb.exe")
        else:
            PathExecutable = DossierActuel.absoluteFilePath("adb")
        result = subprocess.run(PathExecutable+" "+Message, env={**os.environ, 'ANDROID_SERIAL': self.SerialNumber}, capture_output=True)
        return result

    def ShellIn(self, Message, PrintLog = True):
        result = self.CallADB("shell "+Message)
        self.Log += "<--"+str(Message)
        if PrintLog:
            self.Log += "-->"+str(result.stdout)+str("\r\n")
        return str(result.stdout, 'utf-8')

    def InstallApk(self, Name = "", ListoptionADB = ""):#Locate APK in ressources dir
        DossierProject = QDir(self.PathProject)
        DossierProject.cd('Ressource')
        PathAPK = DossierProject.absoluteFilePath(Name)
        print(self.CallADB("install "+ListoptionADB+" "+PathAPK))


    def CreateWebsiteShortcutChrome(self, Adresse = "google.com", Name = "Test%sWhitespace", Initialisation = True):
        self.ShellIn("am start -n com.android.chrome/com.google.android.apps.chrome.Main -d "+Adresse)
        #self.ShellIn("ls -la")
        if Initialisation:
            #if self.HasNode(IdNode = "com.android.chrome:id/send_report_checkbox",  Timeout = 0):
            self.ClickOnNode(IdNode = "com.android.chrome:id/send_report_checkbox")
            #if self.HasNode(IdNode = "com.android.chrome:id/terms_accept",  Timeout = 0):
            self.ClickOnNode(IdNode = "com.android.chrome:id/terms_accept")
            #if self.HasNode(IdNode = "com.android.chrome:id/negative_button",  Timeout = 0):
            self.ClickOnNode(IdNode = "com.android.chrome:id/negative_button")
        # if self.HasNode(IdNode = "com.android.chrome:id/toolbar_buttons",  Timeout = 0):
            #self.ClickOnNode(IdNode = "com.android.chrome:id/toolbar_buttons")
        self.ClickOnIndexMenu(IdIndex = "1", IdMenu="com.android.chrome:id/toolbar_buttons", TypeItem = "com.android.chrome:id/menu_button")
        self.ClickOnIndexMenu(IdIndex = "9", IdMenu = "com.android.chrome:id/app_menu_list", TypeItem = "com.android.chrome:id/menu_item_text")
        self.ClearTextEdit(IdTextEdit = "com.android.chrome:id/text")
        self.ShellIn("input text '"+(Name).replace(" ", "%s")+"'")
        self.ClickOnNode(IdNode = "android:id/button1")
        self.ClickOnNode(IdNode = "com.android.chrome:id/tab_switcher_button")
        self.ClickOnIndexMenu(IdIndex = "1", IdMenu="com.android.chrome:id/toolbar_buttons", TypeItem = "com.android.chrome:id/menu_button")
        self.ClickOnIndexMenu(IdIndex = "2", IdMenu = "com.android.chrome:id/app_menu_list", TypeItem = "com.android.chrome:id/menu_item_text")
        self.ShellIn("am force-stop com.android.chrome")

    def ClickOnNode(self, IdNode = ""):
        tree = ET.fromstring(self.GetScreen())
        ListNode = (tree.findall(".//node[@resource-id='"+IdNode+"']"))
        result = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNode[0].attrib['bounds'])
        if len(result) >= 1:
            if result[0].__len__() == 4:
                MidX = (int(result[0][0])+int(result[0][2]))/2
                MidY = (int(result[0][1])+int(result[0][3]))/2
                self.ShellIn("input tap "+str(int(MidX))+" "+str(int(MidY)))
    def ClickOnNodeByXPath(self, XPath = ""):
        tree = ET.fromstring(self.GetScreen())
        ListNode = (tree.findall(XPath))
        result = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNode[0].attrib['bounds'])
        if len(result) >= 1:
            if result[0].__len__() == 4:
                MidX = (int(result[0][0])+int(result[0][2]))/2
                MidY = (int(result[0][1])+int(result[0][3]))/2
                self.ShellIn("input tap "+str(int(MidX))+" "+str(int(MidY)))
    def ClickOnIndexMenu(self, IdIndex = "", IdMenu = "", TypeItem = ""):
        tree = ET.fromstring(self.GetScreen())
        ListNode = (tree.findall(".//node[@resource-id='"+IdIndex+"']/node[@index='"+IdMenu+"']/node[@resource-id='"+TypeItem+"']"))
        result = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNode[0].attrib['bounds'])
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

    def GetScreen(self):
        ActualScreen = (re.findall("<.*>", str(self.CallADB("exec-out uiautomator dump /dev/tty").stdout, 'utf-8')))[0]#FiltreXmlDump
        return ActualScreen

    def Test(self):
        ActualScreen = self.GetScreen()
        tree = ET.fromstring(ActualScreen)

        #.//*[@resource-id='com.sec.android.app.launcher:id/launcher']//*[@resource-id='com.sec.android.app.launcher:id/iconview_titleView' and @text='Applications Microsoft']/..

        #<node .*? resource-id=\""+re.escape(IdMenu)+"\" .*?>.*?<node index=\""+re.escape(IdIndex)+"\".*?><node .*? resource-id=\""+re.escape(TypeItem)+"\" .*? bounds=\"\[(\d*),(\d*)\]\[(\d*),(\d*)\]\" /></node>.*?</node>
        ListNode = (tree.findall(".//node[@resource-id='com.android.chrome:id/app_menu_list']/node[@index='9']/node[@resource-id='com.android.chrome:id/menu_item_text']"))
        
        result = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNode[0].attrib['bounds'])
        if len(result) >= 1:
            if result[0].__len__() == 4:
                MidX = (int(result[0][0])+int(result[0][2]))/2
                MidY = (int(result[0][1])+int(result[0][3]))/2
                self.ShellIn("input tap "+str(int(MidX))+" "+str(int(MidY)))


    def ClearTextEdit(self, IdTextEdit = ""):
        ActualScreen = self.GetScreen()
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
