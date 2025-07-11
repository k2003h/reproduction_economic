import os
import cv2
import random
import numpy as np
from os import PathLike
from selenium import webdriver
from paddleocr import PaddleOCR
from tools.MySQLDatabase import MySQLDatabase
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options


# ---------------用于爬虫---------------
def get_useragent_list():
    db = MySQLDatabase("graduation_design")
    query_sql = "SELECT useragent FROM user_agent WHERE types=%s and popularity !=%s"
    ua_list = db.fetch_data(query_sql, ("Windows", "Uncommon"))
    return ua_list


def get_random_header():
    header = {
        'User-Agent': random.choice(get_useragent_list()),
        'Accept-Language': 'en-US,en;q=0.9',
        'Authorization': 'Bearer your_token'

    }
    return header


def start_browser():
    base_dir = os.path.dirname(os.path.abspath(__file__)).replace("\\tools", "")
    browser_file_path = base_dir + "\\src\\browser_profile"
    driver_path = base_dir + "\\src\\driver\\msedgedriver.exe"
    options = Options()
    options.add_argument(f"--user-data-dir={browser_file_path}")
    options.add_argument('--edge-skip-compat-layer-relaunch')
    service = Service(executable_path=driver_path)
    return webdriver.Edge(service=service, options=options)


def get_positions(img1: cv2.UMat | PathLike[str] | str, img2: cv2.UMat | PathLike[str] | str, threshold=0.7,
                  nms_threshold=0.3):
    """
    在img2中查找img1的位置
    :param img1: 原始图片(numpy数组或文件路径)
    :param img2: 目标图片(numpy数组或文件路径)
    :param nms_threshold:
    :param threshold:
    :return:
    """
    # 模板匹配
    if isinstance(img1, str):
        img1 = cv2.imread(img1, cv2.IMREAD_COLOR)
    if isinstance(img2, str):
        img2 = cv2.imread(img2, cv2.IMREAD_COLOR)
    h, w = img1.shape[:2]
    result = cv2.matchTemplate(img2, img1, cv2.TM_CCOEFF_NORMED)

    # 获取所有超过阈值的匹配位置
    loc = np.where(result >= threshold)
    matches = list(zip(*loc[::-1]))

    # 非极大值抑制
    boxes = []
    for pt in matches:
        boxes.append([pt[0], pt[1], pt[0] + w, pt[1] + h])

    indices = cv2.dnn.NMSBoxes(
        boxes,
        [result[y, x] for (x, y) in matches],
        threshold,
        nms_threshold
    )

    # 计算中心点坐标
    positions = []
    for i in indices:
        x, y = matches[i]
        center = (x + w // 2, y + h // 2)
        positions.append((center, result[y, x]))

    return positions


def get_position(img1: cv2.UMat | PathLike[str], img2: cv2.UMat | PathLike[str], scale: float = 1.0):
    """
    在img2中查找img1的位置
    :param img1: 原始图片(numpy数组或文件路径)
    :param img2: 目标图片(numpy数组或文件路径)
    :param scale: 缩放比例(>1缩小img2，<1缩小img1)
    :return: img1在img2中的坐标(中心), 相似度
    """
    # 读取图片
    if isinstance(img1, str):
        img1 = cv2.imread(img1, cv2.IMREAD_COLOR)
    if isinstance(img2, str):
        img2 = cv2.imread(img2, cv2.IMREAD_COLOR)

    # 根据缩放比例调整图片大小
    if scale > 1:
        # 缩小img2
        new_width = int(img2.shape[1] / scale)
        new_height = int(img2.shape[0] / scale)
        img2 = cv2.resize(img2, (new_width, new_height))
    elif 0 < scale < 1:
        # 缩小img1
        new_width = int(img1.shape[1] * scale)
        new_height = int(img1.shape[0] * scale)
        img1 = cv2.resize(img1, (new_width, new_height))

    # 模板匹配
    result = cv2.matchTemplate(img2, img1, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 计算匹配位置(中心点坐标)
    h, w = img1.shape[:2]
    x = max_loc[0] + w // 2
    y = max_loc[1] + h // 2

    return (x, y), max_val


def compare_image(img1: str | PathLike[str] | np.ndarray, img2: str | PathLike[str] | np.ndarray, scale: float = 1.0,
                  threshold: float = 0.7) -> bool:
    """
    在img2中查找img1是否存在
    :param img1: 原始图片路径
    :param img2: 目标图片(numpy数组)
    :param scale: 缩放比例(>1缩小img2，<1缩小img1)
    :param threshold:判断临界值
    :return: 是否存在
    """
    # 读取图片
    if isinstance(img1, str):
        img1 = cv2.imread(img1, cv2.IMREAD_COLOR)
    if isinstance(img2, str):
        img2 = cv2.imread(img2, cv2.IMREAD_COLOR)

    # 根据缩放比例调整图片大小
    if scale > 1:
        # 缩小img2
        new_width = int(img2.shape[1] / scale)
        new_height = int(img2.shape[0] / scale)
        img2 = cv2.resize(img2, (new_width, new_height))
    elif 0 < scale < 1:
        # 缩小img1
        new_width = int(img1.shape[1] * scale)
        new_height = int(img1.shape[0] * scale)
        img1 = cv2.resize(img1, (new_width, new_height))

    # 模板匹配
    result = cv2.matchTemplate(img2, img1, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)

    return max_val > threshold


def ocr(image_path):
    paddleocr = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False)

    # 对示例图像执行 OCR 推理
    result = paddleocr.predict(
        input=image_path)

    # 可视化结果并保存 json 结果
    for res in result:
        res.print()
        res.save_to_img("output")
        res.save_to_json("output")
