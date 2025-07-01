import time
import cv2
from PIL import Image
from paddleocr import PaddleOCR
from tools.MySQLDatabase import MySQLDatabase
from tools.functions import *
from tools.AndroidEmulator import AndroidEmulator


def create_tables():
    db = MySQLDatabase("localhost", "root", "1234", "reproduction_economic")
    db.execute_query("CREATE TABLE IF NOT EXISTS doctor ("
                     "id int,"
                     ")")
    db.show_basic_inf()


def ocr_with_paddleocr(image_path, lang='ch'):
    ocr = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False)

    # 对示例图像执行 OCR 推理
    result = ocr.predict(
        input=image_path)

    # 可视化结果并保存 json 结果
    for res in result:
        res.print()
        res.save_to_img("output")
        res.save_to_json("output")

def get_line():
    path = "/Patient-centered-2024/images"
    emulator=AndroidEmulator()
    emulator.connect()
    for i in range(10):
        emulator.screenshot("Patient-centered-2024\\images")
        r = get_positions(path + "\\line.png", path + "\\screenshot.png")
        ys = []
        for ((x, y), similarity) in r:
            ys.append(y)
        ys = sorted(ys)
        emulator.swipe(270, 250 + ys[0] - 415, 270, 250, 1500)
        time.sleep(3)


if __name__ == "__main__":
    emulator = AndroidEmulator()
    emulator.connect()
    emulator.screenshot("Patient-centered-2024\\images")
    # ocr_with_paddleocr()
    # path = "D:\\Study\\Private\\Python\Code\\reproduction_economic\\Patient-centered-2024\\images"
    # r = get_position(path + "\\wait_time.png", path + "\\screenshot.png")
    # print(type(r))
    # ys = []
    # for ((x, y), similarity) in r:
    #     ys.append(y)
    # ys = sorted(ys)
    # print(ys[1] - ys[0])
    # for i in range(10):
    #     emulator.screenshot("Patient-centered-2024\\images")
    #     r = get_position(path + "\\wait_time.png", path + "\\screenshot.png")
    #     print(type(r))
    #     ys = []
    #     for ((x, y), similarity) in r:
    #         ys.append(y)
    #     ys = sorted(ys)
    #     emulator.swipe(270, 250 + ys[1] - ys[0], 270, 250, 1500)
    #     print(ys[1] - ys[0])
    #     time.sleep(1)
    r=ocr_with_paddleocr("Patient-centered-2024/images\\screenshot.png")
    print(r)
    # get_line()
