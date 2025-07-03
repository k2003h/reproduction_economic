# 私有方法
import re
import cv2
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


def distinguish_title(text):
    """

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


def extract_paragraphs(img_array, blank_height=30, threshold=5, bg_threshold=253,ignore_line=True):
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
    text_count=0
    # 跳过起始空白行
    while start_idx < len(horizontal_proj) and horizontal_proj[start_idx] <= threshold * img_array.shape[1]:
        start_idx += 1

    for i in range(len(horizontal_proj)):
        if horizontal_proj[i] <= threshold * img_array.shape[1]:
            blank_count += 1
            text_count=0
        else:
            if ignore_line:
                text_count+=1
                blank_count+=1
                if text_count>2:
                    blank_count-=text_count
                    # 检测到连续空行达到指定高度
                    if blank_count >= blank_height:
                        if start_idx < i - blank_count:
                            paragraph = img_array[start_idx:i - blank_count, :]
                            paragraphs.append(paragraph)
                        start_idx = i
                    blank_count = 0
            else:
                if blank_count >= blank_height:
                    if start_idx < i - blank_count:
                        paragraph = img_array[start_idx:i - blank_count, :]
                        paragraphs.append(paragraph)
                    start_idx = i
                blank_count = 0

    # 添加最后一段
    if start_idx < len(horizontal_proj):
        last_region = img_array[start_idx:, :]
        last_proj = np.sum(cv2.cvtColor(last_region, cv2.COLOR_BGR2GRAY) > 252, axis=1)
        if np.any(last_proj > threshold * last_region.shape[1] * 0.1):  # 至少10%区域有文本
            paragraphs.append(last_region)

    return paragraphs


def extract_paragraphs_for_dialogue(img_array, blank_height=30, threshold=5, bg_threshold=253,ignore_line=True):
    """
    参数:
        img_array: OpenCV读取的BGR图像数组
        blank_height: 预期的空行高度(默认30像素)
        threshold: 允许的像素值波动阈值(默认5)

    返回:
        paragraphs: 分割后的段落图像列表
    """
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
    text_count=0
    # 跳过起始空白行
    while start_idx < len(horizontal_proj) and horizontal_proj[start_idx] <= threshold * img_array.shape[1]:
        start_idx += 1

    for i in range(len(horizontal_proj)):
        if horizontal_proj[i] <= threshold * img_array.shape[1]:
            blank_count += 1
            text_count=0
        else:
            if ignore_line:
                text_count+=1
                blank_count+=1
                if text_count>2:
                    blank_count-=text_count
                    # 检测到连续空行达到指定高度
                    if blank_count >= blank_height:
                        if start_idx < i - blank_count:
                            paragraph = img_array[start_idx:i - blank_count, :]
                            paragraphs.append(paragraph)
                        start_idx = i
                    blank_count = 0
            else:
                if blank_count >= blank_height:
                    if start_idx < i - blank_count:
                        paragraph = img_array[start_idx:i - blank_count, :]
                        paragraphs.append(paragraph)
                    start_idx = i
                blank_count = 0

    # 添加最后一段
    if start_idx < len(horizontal_proj):
        last_region = img_array[start_idx:, :]
        last_proj = np.sum(cv2.cvtColor(last_region, cv2.COLOR_BGR2GRAY) > 252, axis=1)
        if np.any(last_proj > threshold * last_region.shape[1] * 0.1):  # 至少10%区域有文本
            paragraphs.append(last_region)

    return paragraphs


def format_date(date_str):
    # 获取当前年份
    current_year = datetime.now().year

    try:
        # 解析原始字符串(假设格式为"月.日")
        month, day = map(int, date_str.split('.'))

        # 创建完整日期对象
        full_date = datetime(current_year, month, day)

        # 格式化为"YYYY.MM.DD"
        return full_date.strftime("%Y.%m.%d")
    except Exception as e:
        print(f"格式转换错误: {e}")
        return None
