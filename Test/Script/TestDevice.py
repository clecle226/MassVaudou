from Helper import DeviceHelper, add_function_Masterisation
import time
import types

@add_function_Masterisation(1)
def run(self):
    self.ShellIn("am start -p com.android.chrome")
    self.ShellIn("ls -la")
    self.ClickOnNode("test")

#DeviceHelper.run = types.MethodType( run, DeviceHelper )