import math
import os
import sys
import time
import random
import subprocess
import numpy as np
import cv2


class AndroidEmulator:
    def __init__(self, save_path, emulator_id="127.0.0.1:62001"):
        self._basic_dir = os.path.dirname(os.path.abspath(__file__))
        self._project_path = self._basic_dir.replace("tools", "")
        self._save_path = save_path
        self._id = emulator_id
        self.adb_path = self._basic_dir.replace("\\tools", "") + "\\src\\adb-tools\\adb.exe"
        self._connect()

    def connect(self):
        subprocess.run(self.adb_path + " disconnect", shell=False)
        r = subprocess.run(self.adb_path + f" connect {self._id}", shell=False, stdout=subprocess.PIPE, text=True,
                           encoding="utf-8")
        if "cannot" in r.stdout:
            return False
        else:
            return "adb连接成功"

    def _connect(self):
        subprocess.run(self.adb_path + " disconnect", shell=False)
        r = subprocess.run(self.adb_path + f" connect {self._id}", shell=False, stdout=subprocess.PIPE, text=True,
                           encoding="utf-8")
        if "connected to" in r.stdout:
            return True
        else:
            raise ConnectionError("无法连接到模拟器")

    def screenshot(self, path=None):
        """
        截图函数,会在指定path下生成screenshot.png
        :param path: 请输入项目后的相对地址，例如path="tools//..."
        :return: 无
        """
        if not path:
            path = self._save_path
        subprocess.run(self.adb_path + f' -s {self._id} shell screencap -p /sdcard/screenshot.png', shell=False,
                       stdout=subprocess.PIPE, text=True, encoding="utf-8")
        screenshot_path = self._project_path + path
        subprocess.run(self.adb_path + f' -s {self._id} pull /sdcard/screenshot.png ' + screenshot_path, shell=False,
                       stdout=subprocess.PIPE, text=True)

    def click(self, x, y, offset=0):
        """
        模拟点击(输入全为int)
        :param x: 横坐标
        :param y: 纵坐标
        :param offset: 偏移
        :return:
        """
        x += random.randint(-offset, offset)
        y += random.randint(-offset, offset)
        click_cmd = self.adb_path + f' -s {self._id} shell input tap ' + str(x) + ' ' + str(y)
        subprocess.run(click_cmd, shell=True, stdout=subprocess.PIPE, text=True)

    def swipe(self, x1, y1, x2, y2, duration=None):
        """

        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :param duration: 单位：毫秒
        :return:
        """
        if duration is None:
            duration = int(math.sqrt(max((x1 - x2) ** 2 + (y1 - y2) ** 2, 0.1)) * 6)
        swipe_cmd = self.adb_path + f' -s {self._id} shell input swipe ' + str(x1) + ' ' + str(y1) + ' ' + str(x2) + ' ' + str(
            y2) + ' ' + str(duration)
        subprocess.run(swipe_cmd, shell=True, stdout=subprocess.PIPE, text=True)

    def key_event(self, code):
        """

        :param code: 3->Home键;4->Back键
        :return:
        """
        back_cmd = self.adb_path + f' -s {self._id} shell input keyevent ' + str(code)
        subprocess.run(back_cmd, shell=True, stdout=subprocess.PIPE, text=True)

    def disconnect(self):
        subprocess.run(self.adb_path + f" -s {self._id} disconnect", shell=False)

    def kill(self):
        subprocess.run(self.adb_path + " kill-server", shell=False)

    def restart(self):
        proc = subprocess.Popen(
            [self.adb_path, "-s", f"{self._id}", "reboot"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # 5秒后强制终止（模拟Ctrl+C）
        time.sleep(5)
        proc.terminate()
        time.sleep(5)
        print("\033[33m<Notice:此处会进行emulator kill操作，出现error属于正常现象>\033[0m")
        self.kill()
        time_out = time.time() + 60
        while True:
            if self.connect():
                print(f"\033[33m<Notice:重启并重新连接成功\033[0m")
                break
            if time.time() > time_out:
                print(f"\033[33m<Error:连接超时>\033[0m")
                sys.exit()
            time.sleep(5)
