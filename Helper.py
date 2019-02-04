import subprocess
import re
import types
import os
from functools import wraps
import platform
import xml.etree.ElementTree  as ET
from PySide2.QtCore import QDir
import time
#import lxml.etree

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
        if Initialisation:
            self.ClickOnNodeByResourceId(IdNode = "com.android.chrome:id/send_report_checkbox")
            self.ClickOnNodeByResourceId(IdNode = "com.android.chrome:id/terms_accept")
            self.ClickOnNodeByResourceId(IdNode = "com.android.chrome:id/negative_button")
        self.ClickOnIndexMenu(IdIndex = "1", IdMenu="com.android.chrome:id/toolbar_buttons", TypeItem = "com.android.chrome:id/menu_button")
        self.ClickOnIndexMenu(IdIndex = "9", IdMenu = "com.android.chrome:id/app_menu_list", TypeItem = "com.android.chrome:id/menu_item_text")
        self.ClearTextEdit(IdTextEdit = "com.android.chrome:id/text")
        self.ShellIn("input text '"+(Name).replace(" ", "%s")+"'")
        self.ClickOnNodeByResourceId(IdNode = "android:id/button1")
        self.ClickOnNodeByResourceId(IdNode = "com.android.chrome:id/tab_switcher_button")
        self.ClickOnIndexMenu(IdIndex = "1", IdMenu="com.android.chrome:id/toolbar_buttons", TypeItem = "com.android.chrome:id/menu_button")
        self.ClickOnIndexMenu(IdIndex = "2", IdMenu = "com.android.chrome:id/app_menu_list", TypeItem = "com.android.chrome:id/menu_item_text")
        self.ShellIn("am force-stop com.android.chrome")

    def ClickOnNodeByResourceId(self, IdNode = ""):
        self.ClickOnNodeByResourceId(".//node[@resource-id='"+IdNode+"']")
    def ClickOnIndexMenu(self, IdIndex = "", IdMenu = "", TypeItem = ""):
        self.ClickOnNodeByXPath(".//node[@resource-id='"+IdIndex+"']/node[@index='"+IdMenu+"']/node[@resource-id='"+TypeItem+"']")

    def ClickOnNodeByXPath(self, XPath = ""):
        tree = ET.fromstring(self.GetScreen())
        ListNode = (tree.findall(XPath))
        result = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNode[0].attrib['bounds'])
        if len(result) >= 1:
            if result[0].__len__() == 4:
                MidX = (int(result[0][0])+int(result[0][2]))/2
                MidY = (int(result[0][1])+int(result[0][3]))/2
                self.ShellIn("input tap "+str(int(MidX))+" "+str(int(MidY)))
    def LongClickOnNodeByXPath(self, XPath = "", TimeClick = 500):
        tree = ET.fromstring(self.GetScreen())
        ListNode = (tree.findall(XPath))
        result = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNode[0].attrib['bounds'])
        if len(result) >= 1:
            if result[0].__len__() == 4:
                MidX = (int(result[0][0])+int(result[0][2]))/2
                MidY = (int(result[0][1])+int(result[0][3]))/2
                self.ShellIn("input swipe "+str(int(MidX))+" "+str(int(MidY))+" "+str(int(MidX))+" "+str(int(MidY))+" "+str(TimeClick))
    def LongClickOnIconeLauncher(self, Name = ""):
        #good XPath but wrong Parser ET
        #.//*[@resource-id='com.sec.android.app.launcher:id/launcher']//*[@resource-id='com.sec.android.app.launcher:id/iconview_titleView' and @text='Téléphone']/..
        self.LongClickOnNodeByXPath(".//*[@resource-id='com.sec.android.app.launcher:id/launcher']//*[@text='"+Name+"']/..")

    def MoveIconeFirstPlace(self, Name=""):
        tree = ET.fromstring(self.GetScreen())
        ListNode = (tree.findall(".//*[@resource-id='com.sec.android.app.launcher:id/launcher']//*[@text='"+Name+"']/.."))
        result = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNode[0].attrib['bounds'])
        if len(result) >= 1:
            if result[0].__len__() == 4:
                MidXSource = (int(result[0][0])+int(result[0][2]))/2
                MidYSource = (int(result[0][1])+int(result[0][3]))/2
                ListNode = (tree.findall(".//*[@resource-id='com.sec.android.app.launcher:id/launcher']//*[@resource-id='com.sec.android.app.launcher:id/apps_content']/*[1]/*[1]/*[@index='0']"))
                resultDest = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNode[0].attrib['bounds'])
                LeftXDest = int(resultDest[0][0])
                MidYDest = (int(resultDest[0][1])+int(resultDest[0][3]))/2
                self.ShellIn("input draganddrop "+str(int(MidXSource))+" "+str(int(MidYSource))+" "+str(int(LeftXDest))+" "+str(int(MidYDest))+" 250")
    def SearchClickIconeLauncher(self, Name=""):
        EcranNumber = 0
        IconeFound = False
        ActualScreen = self.GetScreen()
        while ActualScreen != NextSxreen or not IconeFound:
            ActualScreen = NextScreen
            tree = ET.fromstring(ActualScreen)
            ListNode = (tree.findall(".//*[@resource-id='com.sec.android.app.launcher:id/launcher']//*[@text='"+Name+"']/.."))
            if len(ListNode) > 0:# IconeTrouvé
                self.ClickOnNodeByXPath(self, ".//*[@resource-id='com.sec.android.app.launcher:id/launcher']//*[@text='"+Name+"']/..")
                IconeFound = True
            else:#Icone non trouvé
                ListNodeSlide = (tree.findall(".//*[@resource-id='com.sec.android.app.launcher:id/launcher']"))
                result = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNode[0].attrib['bounds'])
                if len(result) >= 1:
                    if result[0].__len__() == 4:
                        #MidXSource = (int(result[0][0])+int(result[0][2]))/2
                        MidYSource = (int(result[0][1])+int(result[0][3]))/2
                EcranNumber += 1
        while EcranNumber > 0:
            tree = ET.fromstring(ActualScreen)
            ListNode = (tree.findall(".//*[@resource-id='com.sec.android.app.launcher:id/launcher']"))
            result = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNode[0].attrib['bounds'])
            if len(result) >= 1:
                if result[0].__len__() == 4:
                    #MidXSource = (int(result[0][0])+int(result[0][2]))/2
                    MidYSource = (int(result[0][1])+int(result[0][3]))/2
            EcranNumber =- 1
            
    result = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNode[0].attrib['bounds'])
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
        self.MoveIconeFirstPlace("Galerie")
        '''ActualScreen = self.GetScreen()
        tree = ET.fromstring(ActualScreen)
        #root = lxml.etree.parse(ActualScreen)
        #print(root.xpath(".//*[@resource-id='com.sec.android.app.launcher:id/launcher']//*[@resource-id='com.sec.android.app.launcher:id/iconview_titleView' and @text='Téléphone']/.."))
        #.//*[@resource-id='com.sec.android.app.launcher:id/launcher']//*[@resource-id='com.sec.android.app.launcher:id/iconview_titleView' and @text='Applications Microsoft']/..

        #<node .*? resource-id=\""+re.escape(IdMenu)+"\" .*?>.*?<node index=\""+re.escape(IdIndex)+"\".*?><node .*? resource-id=\""+re.escape(TypeItem)+"\" .*? bounds=\"\[(\d*),(\d*)\]\[(\d*),(\d*)\]\" /></node>.*?</node>
        ListNode = (tree.findall(".//*[@resource-id='com.sec.android.app.launcher:id/launcher']//*[@resource-id='com.sec.android.app.launcher:id/iconview_titleView' and @text='Téléphone']/.."))
        
        result = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNode[0].attrib['bounds'])
        if len(result) >= 1:
            if result[0].__len__() == 4:
                MidX = (int(result[0][0])+int(result[0][2]))/2
                MidY = (int(result[0][1])+int(result[0][3]))/2
                self.ShellIn("input swipe "+str(int(MidX))+" "+str(int(MidY))+" "+str(int(MidX))+" "+str(int(MidY))+" 500")'''


    def ClearTextEdit(self, IdTextEdit = ""):
        ActualScreen = self.GetScreen()
        tree = ET.fromstring(ActualScreen)

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
