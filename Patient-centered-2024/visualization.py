import math
import time
from os import PathLike

import cv2
import numpy as np
from matplotlib import pyplot as plt
from paddleocr import PaddleOCR

from private_tools import scaling_image
from tools.OCR import OCR


def extract_paragraphs(img_array:np.ndarray, blank_height:int=30, threshold:int=5, bg_threshold:int=253, scaling:float=1):
    """
    参数:
        img_array: OpenCV读取的BGR图像数组
        blank_height: 预期的空行高度(默认30像素)
        threshold: 允许的像素值波动阈值(默认5)

    返回:
        paragraphs: 分割后的段落图像列表
    """
    img_with_boxes = img_array.copy()
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
                cv2.rectangle(img_with_boxes, (0, start_idx),
                              (img_array.shape[1] - 1, i - blank_count),
                              (0, 0, 255), 2)
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
                        cv2.rectangle(img_with_boxes, (0, start_idx),
                                      (img_array.shape[1] -1, i - blank_count),
                                      (0, 0, 255), 2)
                    start_idx = i
                blank_count = 0

    if start_idx < len(horizontal_proj):
        last_region = img_array[start_idx:, :]
        last_gray = cv2.cvtColor(last_region, cv2.COLOR_BGR2GRAY)
        last_proj = np.sum(last_gray < bg_threshold, axis=1)  # 更合理的投影计算
        if np.sum(last_proj) > threshold * last_region.shape[1] * 0.1:  # 降低阈值至5%
            paragraphs.append(scaling_image(last_region, scaling))
            cv2.rectangle(img_with_boxes, (0, start_idx),
                          (img_array.shape[1] - 1, i - blank_count),
                          (0, 0, 255), 2)


    # plt.figure(figsize=(18, 6))
    # plt.subplot(131), plt.imshow(cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB))
    # plt.title('Original Image'), plt.axis('off')
    # plt.subplot(132), plt.imshow(binary, cmap='gray')
    # plt.title(f'Binary (Threshold={bg_threshold})'), plt.axis('off')
    # plt.subplot(133), plt.imshow(cv2.cvtColor(img_with_boxes, cv2.COLOR_BGR2RGB))
    # plt.title('Segmentation Result'), plt.axis('off')
    # plt.tight_layout()
    # plt.show()

    return paragraphs

def char_accuracy(a, b):
    """字符级准确率"""
    matches = sum(1 for x, y in zip(a, b) if x == y)
    return matches / max(len(a), len(b))


def plot_ocr_scaling_performance():
    """
    可视化不同缩放比例下的OCR性能
    参数:
    """
    scaling_list=[1.0,0.9,0.8,0.7,0.6,0.5,0.4,0.3]
    time_list=[]
    accuracy_list=[]
    start_time = time.time()
    answer = []
    img = cv2.imread("./images/test/advice_test.png")
    ocr = OCR()
    for p in extract_paragraphs(img, 20, 1, 200, 1):
        result = ocr.predict(p)
        answer.append(result["text"][0])
    print(f"不进行缩放的时间：{time.time() - start_time}s,准确率{1.0}")
    score = []
    for scaling in scaling_list:
        start_time = time.time()
        results = []
        for p in extract_paragraphs(img, 20, 1, 200, scaling):
            result = ocr.predict(p)
            results.append(result["text"][0])
        recognise_time = time.time() - start_time
        time_list.append(recognise_time)
        for i in range(len(results)):
            score.append(char_accuracy(answer[i], results[i]))
        accuracy_list.append(np.mean(score))
        print(f"缩放比例{scaling},识别时间：{recognise_time}s,准确率{np.mean(score)}")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号异常
    # 绘制识别时间曲线
    ax1.plot(scaling_list, time_list, 'bo-', label='识别时间')
    ax1.set_xlabel('缩放比例')
    ax1.set_ylabel('时间(s)')
    ax1.set_title('不同缩放比例下的OCR识别时间')
    ax1.grid(True)
    ax1.legend()

    # 绘制准确率曲线
    ax2.plot(scaling_list, accuracy_list, 'rs--', label='准确率')
    ax2.set_xlabel('缩放比例')
    ax2.set_ylabel('准确率')
    ax2.set_title('不同缩放比例下的OCR识别准确率')
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    plot_ocr_scaling_performance()

