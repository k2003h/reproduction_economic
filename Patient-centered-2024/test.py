import configparser
import time
import re
from datetime import timedelta

import cv2
from tools.MySQLDatabase import MySQLDatabase
from tools.OCR import OCR
from private_tools import *
from tools.AndroidEmulator import AndroidEmulator
from tools.functions import get_position, compare_image


def get_screenshot():
    project_path = "D:\\Study\\Private\\Python\Code\\reproduction_economic\\Patient-centered-2024\\"
    screenshot_path = project_path + "tempt\\screenshot.png"
    images_path = project_path + "images\\"
    emulator = AndroidEmulator("Patient-centered-2024\\tempt")
    # emulator.debug()
    emulator.connect()
    emulator.screenshot()


def crop_image():
    paddleocr = OCR()
    img = cv2.imread("tempt/screenshot.png")
    cropped_img = img[185:330, :]
    cv2.imshow("img_cropped", cropped_img)
    # cv2.waitKey(10000)
    print(paddleocr.predict(cropped_img))


def distinguish_title(text):
    job_pattern = r'(主任医师|副主任医师|主治医师|医师|助理医师)'
    academic_pattern = r'(教授|副教授|讲师|助教)'

    job_title = re.search(job_pattern, text)
    academic_title = re.search(academic_pattern, text)

    return (
        job_title.group(0) if job_title else None,
        academic_title.group(0) if academic_title else None
    )


def ocr_total():
    paddleocr = OCR()
    img = cv2.imread("tempt/screenshot.png")
    # cropped_img = img[185:330, :]
    # cv2.imshow("img_cropped", cropped_img)
    # cv2.waitKey(10000)


def compare_time():
    project_path = "D:\\Study\\Private\\Python\Code\\reproduction_economic\\Patient-centered-2024\\tempt\\"
    screenshot_path = project_path + "screenshot.png"
    paddleocr = OCR()
    start_time = time.time()
    img = cv2.imread("tempt/screenshot.png")
    print(paddleocr.predict(img))
    full_img_time = time.time() - start_time
    po1 = get_position(project_path + "describe.png", screenshot_path)
    po2 = get_position(project_path + "height.png", screenshot_path)
    po3 = get_position(project_path + "illness.png", screenshot_path)
    po4 = get_position(project_path + "time.png", screenshot_path)
    po5 = get_position(project_path + "already.png", screenshot_path)
    po6 = get_position(project_path + "medicine.png", screenshot_path)
    po7 = get_position(project_path + "guomin.png", screenshot_path)
    print(paddleocr.predict(img[po1[0][1]:po2[0][1], :]))
    print(paddleocr.predict(img[po2[0][1]:po3[0][1], :]))
    print(paddleocr.predict(img[po3[0][1]:po4[0][1], :]))
    print(paddleocr.predict(img[po4[0][1]:po5[0][1], :]))
    print(paddleocr.predict(img[po5[0][1]:po6[0][1], :]))
    print(paddleocr.predict(img[po6[0][1]:po7[0][1], :]))
    print(full_img_time, "分开:", time.time() - start_time - full_img_time)

def test_dialogue():
    config = {
        "load": 10,
    }
    date_list=["今天","昨天"]
    interaction_log=[]
    is_first=True
    paddleocr = OCR()
    img=cv2.imread("./tempt/interaction_full.png")
    for p in extract_paragraphs_for_dialogue(img, 20, 1, 190, scaling=1):
        # -> 暂停避免CPU过热
        if config["load"] != 10:
            time.sleep(10 - config["load"])

        ocr_result = paddleocr.predict(p)
        text = ''.join(ocr_result["text"])
        position = ocr_result["position"]
        interaction_scaling=1
        if not text:
            continue
        # ----> 首先判断是否为日期，["今天/昨天"为汉字，其他日期为"mm.dd"格式]
        if (text in date_list or re.match(r'\d+.\d+', text)) and abs(
                (position[0][0] + position[0][2]) / 2 - 360 * interaction_scaling) < 10 * interaction_scaling:
            if is_first:
                is_first = False
            else:
                interaction_log.append(item)
                if not item["content"]:
                    item["content"] = "ERROR"
                print("\t\t\t", item)
            if text == "今天":
                text = datetime.now().strftime("%Y.%m.%d")
            elif text == "昨天":
                text = (datetime.now() - timedelta(days=1)).strftime("%Y.%m.%d")
            else:
                text = format_date(text)
            item = {"date": text, "charactor": "", "content": ""}
        else:
            # --->判断是否为系统信息(居中且没有角色信息)
            if abs((position[0][0] + position[0][
                2]) / 2 - 355 * interaction_scaling) < 10 * interaction_scaling and not item["charactor"]:
                item["charactor"] = "system"
                item["content"] = text
            # --->判断是否为医生信息(靠左)
            elif abs(position[0][0] - 106 * interaction_scaling) < 5 * interaction_scaling:
                text = text.replace("以上文字由机器转写，仅供参考", "")
                item["charactor"] = text
            elif abs(position[0][0] - 572 * interaction_scaling) < 5 * interaction_scaling:
                item["charactor"] = text
            else:
                if re.fullmatch(r'\){0,2}\d+[\'″]', text):
                    continue
                text = text.replace("以上文字由机器转写，仅供参考", "")
                item["content"] = item["content"] + text
if __name__ == "__main__":
    # emulator=AndroidEmulator()
    # img = cv2.imread("./tempt/interaction_full.png")
    # pd = OCR()
    # start_time = time.time()
    # for p in extract_paragraphs_for_dialogue(img, 20, 1, 190, scaling=0.6):
    #     # cv2.imshow("hh",p)
    #     # cv2.waitKey(10000)
    #     r = pd.predict(p)
    #     text = ''.join(r["text"])
    #     print(text)
    # print(f"{int(time.time()-start_time)}")
    # str = "您好😋，感谢您的信任。我是"
    # db = MySQLDatabase("reproduction_economic")
    # # db.execute_query("INSERT INTO operating VALUES (%s,%s)", (-2,str))
    # r=db.fetch_data("SELECT * FROM operating")
    # for i in r:
    #     print(i)
    emulator=AndroidEmulator("Patient-centered-2024\\tempt")
    # emulator.kill()
    emulator.screenshot()
    # print(cv2.imread("tempt/screenshot.png"))
    # img1=cv2.imread("D:/Study/Code/Python/reproduction_economic/Patient-centered-2024/images/get_location.png")
    # img2=cv2.imread("D:/Study/Code/Python/reproduction_economic/Patient-centered-2024/tempt/screenshot.png")
    # print(compare_image(img1,img2))
