import time
import re
import cv2
from tools.MySQLDatabase import MySQLDatabase
from tools.OCR import OCR
from private_tools import *
from tools.AndroidEmulator import AndroidEmulator
from tools.functions import get_position


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


if __name__ == "__main__":
    img = cv2.imread("./tempt/interaction_full.png")
    pd = OCR()
    start_time = time.time()
    for p in extract_paragraphs_for_dialogue(img, 20, 1, 190, scaling=0.6):
        # cv2.imshow("hh",p)
        # cv2.waitKey(10000)
        r = pd.predict(p)
        text = ''.join(r["text"])
        print(text)
    # print(f"{int(time.time()-start_time)}")
    # str = "您好😋，感谢您的信任。我是"
    # db = MySQLDatabase("reproduction_economic")
    # # db.execute_query("INSERT INTO operating VALUES (%s,%s)", (-2,str))
    # r=db.fetch_data("SELECT * FROM operating")
    # for i in r:
    #     print(i)
    # emulator=AndroidEmulator("Patient-centered-2024\\tempt")
    # emulator.click(0,0,0)
