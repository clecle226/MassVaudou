from Helper import DeviceHelper, add_function_Masterisation
import time
import types


@add_function_Masterisation(1)
def run(self):
    self.ShellIn("svc power stayon true") #Desactiver Mise en veille
    self.Test()
    #self.CreateWebsiteShortcutChrome(Adresse = "https://stackoverflow.com", Name = "Le site des pro", Initialisation = True)
    #self.CreateWebsiteShortcutChrome(Adresse = "https://danstonchat.com", Name = "tjs le meilleur", Initialisation = False)
    #self.InstallApk("FDroid.apk", "-r")
    

    
    
    #am start -n com.android.settings/.Settings\$DisplaySettingsActivity
#DeviceHelper.run = types.MethodType( run, DeviceHelper )

#<node index="1" text="Envoyez des statistiques d'utilisation et des rapports d'erreur pour améliorer Chrome." resource-id="com.android.chrome:id/send_report_checkbox" class="android.widget.CheckBox" package="com.android.chrome" content-desc="" checkable="true" checked="true" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[36,602][444,700]" />
#<node index="1" text="Accepter et continuer" resource-id="com.android.chrome:id/terms_accept" class="android.widget.Button" package="com.android.chrome" content-desc="" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[93,776][386,830]" />