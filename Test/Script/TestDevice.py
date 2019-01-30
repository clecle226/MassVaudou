from Helper import DeviceHelper, add_function_Masterisation
import time
import types


@add_function_Masterisation(1)
def run(self):
    self.ShellIn("svc power stayon true") #Desactiver Mise en veille
    self.ShellIn("am start -n com.android.chrome/com.google.android.apps.chrome.Main")
    self.ShellIn("ls -la")
    self.ClickOnNode("test")
    #am start -n com.android.settings/.Settings\$DisplaySettingsActivity
#DeviceHelper.run = types.MethodType( run, DeviceHelper )