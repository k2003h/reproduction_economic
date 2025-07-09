import subprocess
from tools.AndroidEmulator import AndroidEmulator



class HDFEmulator(AndroidEmulator):
    # 为好大夫APP适配的安卓模拟器
    def __init__(self,save_path, emulator_id="127.0.0.1:62001"):
        AndroidEmulator.__init__(self, save_path, emulator_id="127.0.0.1:62001")


    def screenshot(self, path=None):
        if not path:
            path = self._save_path
        subprocess.run(self.adb_path + f' -s {self._id} shell screencap -p /sdcard/screenshot.png', shell=False,
                       stdout=subprocess.PIPE, text=True, encoding="utf-8")
        screenshot_path = self._project_path + path
        subprocess.run(self.adb_path + f' -s {self._id} pull /sdcard/screenshot.png ' + screenshot_path, shell=False,
                       stdout=subprocess.PIPE, text=True)