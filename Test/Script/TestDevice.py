from Helper import DeviceHelper, add_function_Masterisation
import time
import types


@add_function_Masterisation(1)
def run(self):
    self.ShellIn("svc power stayon true") #Desactiver Mise en veille
    #self.ShellIn("am start -n com.android.chrome/com.google.android.apps.chrome.Main -d https://stackoverflow.com")
    #self.ShellIn("ls -la")
    #if self.HasNode(IdNode = "com.android.chrome:id/send_report_checkbox",  Timeout = 0):
    #self.ClickOnNode(IdNode = "com.android.chrome:id/send_report_checkbox")
    #if self.HasNode(IdNode = "com.android.chrome:id/terms_accept",  Timeout = 0):
    #self.ClickOnNode(IdNode = "com.android.chrome:id/terms_accept")
    #if self.HasNode(IdNode = "com.android.chrome:id/negative_button",  Timeout = 0):
    #self.ClickOnNode(IdNode = "com.android.chrome:id/negative_button")
   # if self.HasNode(IdNode = "com.android.chrome:id/toolbar_buttons",  Timeout = 0):
    self.ClickOnIndexMenu(IdIndex = "1", IdMenu="com.android.chrome:id/toolbar_buttons", TypeItem = "com.android.chrome:id/menu_button")
    self.ClickOnIndexMenu(IdIndex = "9", IdMenu = "com.android.chrome:id/app_menu_list", TypeItem = "com.android.chrome:id/menu_item_text")
    self.ClearTextEdit(IdTextEdit = "com.android.chrome:id/text")
    

    
    
    #am start -n com.android.settings/.Settings\$DisplaySettingsActivity
#DeviceHelper.run = types.MethodType( run, DeviceHelper )

#<node index="1" text="Envoyez des statistiques d'utilisation et des rapports d'erreur pour améliorer Chrome." resource-id="com.android.chrome:id/send_report_checkbox" class="android.widget.CheckBox" package="com.android.chrome" content-desc="" checkable="true" checked="true" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[36,602][444,700]" />
#<node index="1" text="Accepter et continuer" resource-id="com.android.chrome:id/terms_accept" class="android.widget.Button" package="com.android.chrome" content-desc="" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[93,776][386,830]" />