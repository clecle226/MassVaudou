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
    LastScreen = ""

    FunctionCallDict = {}
    ListVariable = []
    Variable = dict()


    PathProject = ""

    DeviceObject = None


    def __init__(self, serialNo, pathProject, Deviceobject):
        self.SerialNumber = serialNo
        self.PathProject = pathProject
        self.DeviceObject = Deviceobject
        self.GetIMEI()

    def CallADB(self, Message):
        self.LastScreen = ""

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
        #self.Log += "<--"+str(Message)
        self.DeviceObject.AddLog(Message,"Sortant")
        if PrintLog:
            self.DeviceObject.AddLog(str(result.stdout, 'utf-8'),"Entrant")
            #self.Log += "-->"+str(result.stdout)+str("\r\n")
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
        return self.ClickOnNodeByXPath(".//node[@resource-id='"+IdNode+"']")
    def ClickOnIndexMenu(self, IdIndex = "", IdMenu = "", TypeItem = ""):
        return self.ClickOnNodeByXPath(".//node[@resource-id='"+IdIndex+"']/node[@index='"+IdMenu+"']/node[@resource-id='"+TypeItem+"']")

    def ClickOnNodeByXPath(self, XPath = ""):
        tree = ET.fromstring(self.GetScreen())
        ListNode = (tree.findall(XPath))
        result = None
        if len(ListNode) > 0:
            result = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNode[0].attrib['bounds'])
            if len(result) >= 1:
                if result[0].__len__() == 4:
                    MidX = (int(result[0][0])+int(result[0][2]))/2
                    MidY = (int(result[0][1])+int(result[0][3]))/2
                    self.ShellIn("input tap "+str(int(MidX))+" "+str(int(MidY)))
                    return True
        return False
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

    def ChangeWallpaperSamsungThemes(self):
        self.ShellIn("am start -n com.samsung.android.themestore/com.samsung.android.themestore.activity.MainActivity")
        #Bouton Ajout raccourcis samsung thèmes (disabled)
        self.ClickOnNodeByResourceId("com.samsung.android.themestore:id/cb_add_shortcut")
        #Bouton démmaré
        self.ClickOnNodeByXPath(".//*[@resource-id='com.samsung.android.themestore:id/fragement_base']/*[@index='0']/*[@index='1']/*[@index='2']")
        #Autoriser
        self.ClickOnNodeByResourceId("com.android.packageinstaller:id/permission_allow_button")
        #Refuser l'ajout à l'écran d'accueil
        self.ClickOnNodeByResourceId("com.sec.android.app.launcher:id/add_item_cancel_button")
        #Click On Galerie
        self.ClickOnNodeByXPath(".//*[@resource-id='com.samsung.android.themestore:id/rcv_main_my_device']/*[@index='0']/*[@index='0']")
        #WARNING RISK OF ERROR Change method speedly
        #Click on anyone pictures
        self.ClickOnNodeByXPath(".//*[@class='com.sec.samsung.gallery.glview.composeView.ThumbObject']")
        #Ecran de vérouillage ET d'accueil
        self.ClickOnNodeByXPath(".//*[@resource-id='android:id/resolver_list']/*[@index='0']/*[@index='2']")
        #Definir comme fond d'écran
        self.ClickOnNodeByResourceId("com.sec.android.wallpapercropper2:id/actionbar_layout")
        self.ShellIn("input keyevent KEYCODE_HOME")

    def DesactivatePackage(self, ListPackage):
        for item in ListPackage:
            self.ShellIn("pm disable-user "+ListPackage)
    def RemovePackage(self, ListPackage):
        for item in ListPackage:
            self.ShellIn("pm uninstall"+ListPackage)
        
    def CreateDossierApp(self, ListeIcone = [], NomDossier="Null", CopyOnDesktop = False, MoveFirstPlace = True):
        def ChangePage(ActualPage, GoPage):
            while ActualPage != GoPage:
                if ActualPage < GoPage:
                    self.SlideByXPath("Gauche",".//*[@resource-id='com.sec.android.app.launcher:id/launcher']")
                    ActualPage += 1
                elif ActualPage > GoPage:
                    self.SlideByXPath("Droite",".//*[@resource-id='com.sec.android.app.launcher:id/launcher']")
                    ActualPage -= 1
            return ActualPage

        #Ouvrir launcher
        self.ShellIn("am start -n com.sec.android.app.launcher/com.sec.android.app.launcher.activities.LauncherActivity")
        if self.HasNode("com.sec.android.app.launcher:id/workspace"):
            #Slide up
            self.SlideByXPath("Haut",".//*[@resource-id='com.sec.android.app.launcher:id/workspace']/node[1]")
        #InitialiseListePage et go first page
        ListPageIcone = {}
        for Item in ListeIcone:
            ListPageIcone[Item] = 0
        ActualScreen = self.GetScreen()
        NextScreen = ""
        while ActualScreen != NextScreen:
            if NextScreen != "":
                ActualScreen = NextScreen
            self.SlideByXPath("Droite",".//*[@resource-id='com.sec.android.app.launcher:id/launcher']")
            NextScreen = self.GetScreen()
        ActualPage = 1
        NextScreen = ""
        while ActualScreen != NextScreen:
            if NextScreen != "":
                ActualScreen = NextScreen
            ListIconePageActual = self.SearchIconeInPage(ActualScreen, ListeIcone)
            for item in ListIconePageActual:
                ListPageIcone[item] = ActualPage
            
            self.SlideByXPath("Gauche",".//*[@resource-id='com.sec.android.app.launcher:id/launcher']")
            NextScreen = self.GetScreen()
            ActualPage += 1
        ActualPage -= 1

        #Longclick 1er icone
        ActualPage = ChangePage(ActualPage, ListPageIcone[ListeIcone[0]])
        self.LongClickOnIconeLauncher(ListeIcone[0])
        self.ClickOnNodeByXPath(".//*[@resource-id='com.sec.android.app.launcher:id/drag_layer']/*[@index='0']")
        #Search le reste des Icone
        i = 1
        while i < len(ListeIcone):
            ActualPage = ChangePage(ActualPage, ListPageIcone[ListeIcone[i]])
            self.ClickOnNodeByXPath(".//*[@resource-id='com.sec.android.app.launcher:id/launcher']//*[@text='"+ListeIcone[i]+"']/..")
            i +=1
        #clickCréerDossier
        self.ClickOnNodeByResourceId("com.sec.android.app.launcher:id/multi_select_create_folder")
        #click pour modifier le nom du dossier
        self.ClickOnNodeByResourceId("com.sec.android.app.launcher:id/folder_name")
        #Ecrire Nom du dossier et fin création(Double retour)
        self.ShellIn("input text '"+(NomDossier).replace(" ", "%s")+"'")
        self.ShellIn("input keyevent KEYCODE_BACK KEYCODE_BACK")
        if CopyOnDesktop:
            self.LongClickOnIconeLauncher(NomDossier)
            self.ClickOnNodeByXPath(".//*[@resource-id='com.sec.android.app.launcher:id/drag_layer']/*[@index='1']")

    def SearchIconeInPage(self, ActualScreen, ListIcone):
        ResultListIcone = []
        tree = ET.fromstring(ActualScreen)
        for item in ListIcone:
            ListNode = (tree.findall(".//*[@resource-id='com.sec.android.app.launcher:id/launcher']//*[@text='"+item+"']/.."))
            if len(ListNode) > 0:
                result = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNode[0].attrib['bounds'])
                if len(result) >= 1:
                    if len(result[0]) == 4:
                        ResultListIcone.append(item)
        return ResultListIcone
    def SlideByXPath(self, Direction = "Gauche", XPath = "", Timeout="250"):
        tree = ET.fromstring(self.GetScreen())
        ListNode = (tree.findall(XPath))
        result = None
        if len(ListNode) > 0:
            result = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNode[0].attrib['bounds'])
            if len(result) >= 1:
                if result[0].__len__() == 4:
                    #-1% for parse error of screen border
                    LeftCorner = int(result[0][0])-int(0.01*int(result[0][0]))
                    RightCorner = int(result[0][2])-int(0.01*int(result[0][2]))
                    DownCorner = int(result[0][3])-int(0.01*int(result[0][3]))
                    UpCorner =int(result[0][1])-int(0.01*int(result[0][1]))

                    MidX = (int(result[0][0])+int(result[0][2]))/2
                    MidY = (int(result[0][1])+int(result[0][3]))/2
                    
                    if Direction == "Gauche":
                        self.ShellIn("input swipe "+str(RightCorner)+" "+str(int(MidY))+" "+str(LeftCorner)+" "+str(int(MidY))+" "+Timeout)
                    elif Direction == "Droite":
                        self.ShellIn("input swipe "+str(LeftCorner)+" "+str(int(MidY))+" "+str(RightCorner)+" "+str(int(MidY))+" "+Timeout)
                    elif Direction == "Haut":
                        self.ShellIn("input swipe "+str(int(MidX))+" "+str(DownCorner)+" "+str(int(MidX))+" "+str(UpCorner)+" "+Timeout)
                    elif Direction == "Bas":
                        self.ShellIn("input swipe "+str(int(MidX))+" "+str(UpCorner)+" "+str(int(MidX))+" "+str(DownCorner)+" "+Timeout)
                    else:
                        return False
                    return True
        return False
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
        NextScreen = ""
        while ActualScreen != NextScreen and not IconeFound:
            if NextScreen != "":
                ActualScreen = NextScreen
            tree = ET.fromstring(ActualScreen)
            if self.ClickOnNodeByXPath( ".//*[@resource-id='com.sec.android.app.launcher:id/launcher']//*[@text='"+Name+"']/.."):# IconeTrouvé
                IconeFound = True
            else:#Icone non trouvé
                ListNodeSlide = (tree.findall(".//*[@resource-id='com.sec.android.app.launcher:id/launcher']"))
                resultSlide = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNodeSlide[0].attrib['bounds'])
                if len(resultSlide) >= 1:
                    if resultSlide[0].__len__() == 4:
                        #MidXSource = (int(result[0][0])+int(result[0][2]))/2
                        MidY = (int(resultSlide[0][1])+int(resultSlide[0][3]))/2
                    self.ShellIn("input swipe "+str(int(resultSlide[0][2])-2)+" "+str(int(MidY))+" "+str(int(resultSlide[0][0]))+" "+str(int(MidY))+" 250")
                EcranNumber += 1
                NextScreen = self.GetScreen()
        if not IconeFound:
            print("Erreur")
        while EcranNumber > 0:
            tree = ET.fromstring(self.GetScreen())
            ListNodeSlide = (tree.findall(".//*[@resource-id='com.sec.android.app.launcher:id/launcher']"))
            resultSlide = re.findall("\[(\d*),(\d*)\]\[(\d*),(\d*)\]", ListNodeSlide[0].attrib['bounds'])
            if len(resultSlide) >= 1:
                if resultSlide[0].__len__() == 4:
                    #MidXSource = (int(result[0][0])+int(result[0][2]))/2
                    MidY = (int(resultSlide[0][1])+int(resultSlide[0][3]))/2
            self.ShellIn("input swipe "+str(int(resultSlide[0][0]))+" "+str(int(MidY))+" "+str(int(resultSlide[0][2]))+" "+str(int(MidY))+" 250")
            EcranNumber -= 1

    def HasNode(self, IdNode="", Timeout = 15):
        FinalTimestamp = time.time()+Timeout
        Succesfull = False
        while not Succesfull and time.time() <= FinalTimestamp:
            tree = ET.fromstring(self.GetScreen())
            ListNode = (tree.findall(".//*[@resource-id='"+IdNode+"']"))
            if len(ListNode) > 0:
                return True
        return False

    def GetScreen(self):
        if self.LastScreen != "":
            return self.LastScreen
        FinalTimestamp = time.time()+15
        ActualScreen = []
        while len(ActualScreen) == 0 and time.time() <= FinalTimestamp:
            ActualScreen = (re.findall("<.*>", str(self.CallADB("exec-out uiautomator dump /dev/tty").stdout, 'utf-8')))#FiltreXmlDump
        return ActualScreen[0]

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
