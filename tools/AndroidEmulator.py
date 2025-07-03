import math
import os
import random
import subprocess
import numpy as np
import cv2


class AndroidEmulator:
    def __init__(self, save_path):
        self._basic_dir = os.path.dirname(os.path.abspath(__file__))
        self._project_path = self._basic_dir.replace("tools", "")
        self._save_path = save_path
        self.adb_path = self._basic_dir.replace("\\tools", "") + "\\src\\adb-tools\\adb.exe"
        self.connect()

    def connect(self):
        subprocess.run(self.adb_path + " disconnect", shell=True)
        r = subprocess.run(self.adb_path + " connect 127.0.0.1:62001", shell=False, stdout=subprocess.PIPE, text=True,
                           encoding="utf-8")
        if "cannot" in r.stdout:
            raise ConnectionError("无法连接到模拟器")
        else:
            print("adb连接成功")

    def screenshot(self, path=None):
        """
        截图函数,会在指定path下生成screenshot.png
        :param path: 请输入项目后的相对地址，例如path="tools//..."
        :return: 无
        """
        if not path:
            path = self._save_path
        subprocess.run(self.adb_path + ' shell screencap -p /sdcard/screenshot.png', shell=False,
                       stdout=subprocess.PIPE, text=True, encoding="utf-8")
        screenshot_path = self._project_path + path
        subprocess.run(self.adb_path + ' pull /sdcard/screenshot.png ' + screenshot_path, shell=False,
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
        click_cmd = self.adb_path + ' shell input tap ' + str(x) + ' ' + str(y)
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
        swipe_cmd = self.adb_path + ' shell input swipe ' + str(x1) + ' ' + str(y1) + ' ' + str(x2) + ' ' + str(
            y2) + ' ' + str(duration)
        subprocess.run(swipe_cmd, shell=True, stdout=subprocess.PIPE, text=True)

    def key_event(self, code):
        """

        :param code: 3->Home键;4->Back键
        :return:
        """
        back_cmd = self.adb_path + ' shell input keyevent ' + str(code)
        subprocess.run(back_cmd, shell=True, stdout=subprocess.PIPE, text=True)

    def disconnect(self):
        subprocess.run(self.adb_path + " disconnect", shell=False)

    def debug(self):
        subprocess.run(self.adb_path+" kill-server",shell=False)