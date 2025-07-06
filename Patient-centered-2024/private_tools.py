# 私有方法
import re
import cv2
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


def distinguish_title(text):
    """
    职称识别
    :param text: 输入title文本
    :return: (工作title,教育title)
    """
    job_pattern = r'(主任医师|副主任医师|主治医师|医师|助理医师)'
    academic_pattern = r'(教授|副教授|讲师|助教)'

    job_title = re.search(job_pattern, text)
    academic_title = re.search(academic_pattern, text)

    return (
        job_title.group(0) if job_title else None,
        academic_title.group(0) if academic_title else None
    )


def extract_paragraphs(img_array, blank_height=30, threshold=5, bg_threshold=253, scaling=1):
    """
    参数:
        img_array: OpenCV读取的BGR图像数组
        blank_height: 预期的空行高度(默认30像素)
        threshold: 允许的像素值波动阈值(默认5)

    返回:
        paragraphs: 分割后的段落图像列表
    """
    # 转换为灰度图并二值化
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, bg_threshold, 255, cv2.THRESH_BINARY_INV)

    # 创建对比图
    # plt.figure(figsize=(12, 6))
    # plt.subplot(121), plt.imshow(cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB))
    # plt.title('Original Image'), plt.axis('off')
    # plt.subplot(122), plt.imshow(binary, cmap='gray')
    # plt.title(f'Binary (Threshold={bg_threshold})'), plt.axis('off')
    # plt.tight_layout()
    # plt.show()

    # 水平投影分析
    horizontal_proj = np.sum(binary, axis=1)
    paragraphs = []
    start_idx = 0
    blank_count = 0
    text_count = 0
    while start_idx < len(horizontal_proj) and horizontal_proj[start_idx] <= threshold * img_array.shape[1]:
        start_idx += 1
    for i in range(len(horizontal_proj)):
        if horizontal_proj[i] <= threshold * img_array.shape[1]:
            blank_count += 1
            text_count = 0
            if i - start_idx > 1000:
                paragraph = img_array[start_idx:i - blank_count, :]
                paragraphs.append(scaling_image(paragraph, scaling))
                start_idx = i
        else:
            text_count += 1
            blank_count += 1
            if text_count > 2:
                blank_count -= text_count
                # 检测到连续空行达到指定高度
                if blank_count >= blank_height:
                    if start_idx < i - blank_count:
                        paragraph = img_array[start_idx:i - blank_count, :]
                        paragraphs.append(scaling_image(paragraph, scaling))
                    start_idx = i
                blank_count = 0

    # 添加最后一段
    if start_idx < len(horizontal_proj):
        last_region = img_array[start_idx:, :]
        last_proj = np.sum(cv2.cvtColor(last_region, cv2.COLOR_BGR2GRAY) > 252, axis=1)
        if np.any(last_proj > threshold * last_region.shape[1] * 0.1):  # 至少10%区域有文本
            paragraphs.append(scaling_image(last_region, scaling))

    return paragraphs


def extract_paragraphs_for_dialogue(img_array, blank_height=30, threshold=5, bg_threshold=253, scaling=1):
    """
    参数:
        img_array: OpenCV读取的BGR图像数组
        blank_height: 预期的空行高度(默认30像素)
        threshold: 允许的像素值波动阈值(默认5)

    返回:
        paragraphs: 分割后的段落图像列表
    """
    # 图片缩放
    # 转换为灰度图并二值化
    gray = cv2.cvtColor(img_array[:, 100:615], cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, bg_threshold, 255, cv2.THRESH_BINARY_INV)

    # 创建对比图
    # plt.figure(figsize=(12, 6))
    # plt.subplot(121), plt.imshow(cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB))
    # plt.title('Original Image'), plt.axis('off')
    # plt.subplot(122), plt.imshow(binary, cmap='gray')
    # plt.title(f'Binary (Threshold={bg_threshold})'), plt.axis('off')
    # plt.tight_layout()
    # plt.show()

    # 水平投影分析
    horizontal_proj = np.sum(binary, axis=1)

    paragraphs = []
    start_idx = 0
    blank_count = 0
    text_count = 0
    # 跳过起始空白行
    while start_idx < len(horizontal_proj) and horizontal_proj[start_idx] <= threshold * img_array.shape[1]:
        start_idx += 1

    for i in range(len(horizontal_proj)):
        if horizontal_proj[i] <= threshold * img_array.shape[1]:
            if i - start_idx > 1000:
                paragraph = img_array[start_idx:i - blank_count, :]
                paragraphs.append(scaling_image(paragraph, scaling))
                start_idx = i
            blank_count += 1
            text_count = 0
        else:
            text_count += 1
            blank_count += 1
            if text_count > 2:
                blank_count -= text_count
                # 检测到连续空行达到指定高度
                if blank_count >= blank_height:
                    if start_idx < i - blank_count:
                        if start_idx > 5:
                            paragraph = img_array[start_idx - 5:i - blank_count + 5, :]
                        else:
                            paragraph = img_array[start_idx:i - blank_count + 1, :]
                        paragraphs.append(scaling_image(paragraph, scaling))
                    start_idx = i
                blank_count = 0

    # 添加最后一段
    if start_idx < len(horizontal_proj):
        last_region = img_array[start_idx:, :]
        last_proj = np.sum(cv2.cvtColor(last_region, cv2.COLOR_BGR2GRAY) > 252, axis=1)
        if np.any(last_proj > threshold * last_region.shape[1] * 0.1):  # 至少10%区域有文本
            paragraphs.append(scaling_image(last_region, scaling))

    return paragraphs


def format_date(date_str: str) -> str:
    """
    日期格式标准化处理，使其对m.y(如7.1)或者yyyy.m.d(如2024.7.1)等格式转化为yyyy.mm.dd
    :param date_str: 原日期
    :return: 标准化处理后的日期
    """
    try:
        parts = list(map(int, date_str.split('.')))

        if len(parts) == 2:  # 处理 m.d 或 mm.dd 格式
            month, day = parts
            current_year = datetime.now().year
            full_date = datetime(current_year, month, day)
        elif len(parts) == 3:  # 处理 yyyy.m.d 格式
            year, month, day = parts
            full_date = datetime(year, month, day)
        else:
            raise ValueError("不支持的日期格式")

        return full_date.strftime("%Y.%m.%d")
    except Exception as e:
        print(f"格式转换错误: {e}")
        return None


def scaling_image(img_array, scaling: float):
    """
    图像缩放
    :param img_array: 原图片数组
    :param scaling: 缩放比例
    :return:
    """
    height, width = img_array.shape[:2]
    new_width = int(width * scaling)
    new_height = int(height * scaling)
    new_size = (new_width, new_height)
    resized_array = cv2.resize(img_array, new_size, interpolation=cv2.INTER_LINEAR)
    return resized_array
