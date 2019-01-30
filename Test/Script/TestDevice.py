from Helper import DeviceHelper, add_function_Masterisation
import time
import types


@add_function_Masterisation(1)
def run(self):
    print(self.ShellIn("am start -p com.android.chrome"))
    print(self.ShellIn("ls -la"))
    self.ClickOnNode("test")
    #am start -n com.android.settings/.Settings\$DisplaySettingsActivity
#DeviceHelper.run = types.MethodType( run, DeviceHelper )