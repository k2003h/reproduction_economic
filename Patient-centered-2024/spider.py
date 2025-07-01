import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup
from tools.functions import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from tools.MySQLDatabase import MySQLDatabase
from tools.AndroidEmulator import AndroidEmulator
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options


def create_tables():
    db = MySQLDatabase("reproduction_economic")
    sql = "CREATE TABLE IF NOT EXISTS doctor (" \
          "id int PRIMARY KEY AUTO_INCREMENT," \
          "url varchar(100)," \
          "UNIQUE(url))"
    sql_add_doctor = "ALTER TABLE doctor ADD (" \
                     "name varchar(10)," \
                     "professional_title VARCHAR(20)," \
                     "educational_title VARCHAR(20)," \
                     "social_appointment TEXT," \
                     "gift INT," \
                     "self_introduction TEXT," \
                     "is_team TINYINT(1)," \
                     "honors TINYINT(1)," \
                     "is_message TINYINT(1)," \
                     "scientific TINYINT(1)," \
                     "further_education TINYINT(1)," \
                     "education TINYINT(1)," \
                     "haodaifu int," \
                     "recommendation float," \
                     "num_patient int," \
                     "visits int," \
                     "papers int," \
                     "followup_patient int," \
                     "evaluation float," \
                     "open_time DATE)"
    sql_create_consultation_for_web = "CREATE TABLE IF NOT EXIST consultation_for_web (" \
                                      "num_interact int," \
                                      "num_reply," \
                                      ""
    db.execute_query(sql)
    db.show_basic_inf()
    db.close_connection()


# --------------------用于Web爬虫--------------------
def get_doctor_home_page_urls():
    db = MySQLDatabase("reproduction_economic")
    base_dir = os.path.dirname(os.path.abspath(__file__)).replace("\\Patient-centered-2024", "")
    browser_file_path = base_dir + "\\src\\browser_profile"
    driver_path = base_dir + "\\src\\driver\\msedgedriver.exe"
    options = Options()
    options.add_argument(f"--user-data-dir={browser_file_path}")
    options.add_argument('--edge-skip-compat-layer-relaunch')
    service = Service(executable_path=driver_path)
    browser = webdriver.Edge(service=service, options=options)
    browser.get("https://www.haodf.com/doctor/list-all-neifenmike.html?p=1")
    while True:
        # 等待元素加载
        WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//span[@class='doc-name']/a"))
        )

        # 获取所有目标链接
        links = browser.find_elements(By.XPATH, "//span[@class='doc-name']/a")
        for link in links:
            url = link.get_attribute("href")
            if url:  # 确保URL有效
                db.execute_query("INSERT INTO doctor (url) VALUES (%s)", (url,))
                print(f"已保存URL: {url}")

        time.sleep(5)
        # 点击下一页
        # noinspection PyBroadException
        try:
            next_page = browser.find_element(By.XPATH, "//div[@class='page_turn']/a[contains(string(),'下一页')]")
            next_page.click()
            WebDriverWait(browser, 10).until(
                EC.staleness_of(next_page)  # 等待页面跳转完成
            )
        except Exception:
            print("没有找到下一页或爬取完成:")
            break


def get_doctor_information():
    db = MySQLDatabase("reproduction_economic")
    data = db.fetch_data("SELECT id,url FROM doctor WHERE num_patient=0")
    browser = start_browser()
    browser.get("https://www.haodf.com")
    time.sleep(5)
    counter = 1
    for (id, url) in data:
        # ----------初始化变量----------
        print(f"----------------这是第{counter}个----------------")
        browser.get(url)
        WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "js-intro-tab"))
        )
        browser.find_element(By.CLASS_NAME, "js-intro-tab").click()
        WebDriverWait(browser, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "js-home-tab"))
        )
        # 开始获取数据
        try:
            name = get_text_by_class_name(browser, "js-doctor-name")
            professional_title = get_text_by_class_name(browser, "doctor-title")
            educational_title = get_text_by_class_name(browser, "doctor-educate-title")
            print("name\t:", name, "\t\tprofessional title\t:", professional_title, "\teducational title\t:",
                  educational_title)
            visits = get_num_by_class_name(browser, "js-total-new-pv")[0]
            followup_patient = get_num_by_class_name(browser, "js-totaldiagnosis-report")[0]
            evaluation = get_num_by_class_name(browser, "js-doctorVoteCnt")[0]
            gift = get_num_by_class_name(browser, "js-presentCnt")[0]
            papers = get_num_by_class_name(browser, "js-articleCount")[0]
            open_time = get_text_by_class_name(browser, "js-openSpaceTime")
            if len(name) == 3:
                print("visits\t:", visits, "\t\tfollowup_patient\t:", followup_patient, "\t\tevaluation\t\t:",
                      evaluation,
                      "\t\tgift\t:", gift, "\topen time\t:", open_time, "\tpapers\t:", papers)
            else:
                print("visits\t:", visits, "\tfollowup_patient\t:", followup_patient, "\t\tevaluation\t\t:", evaluation,
                      "\t\tgift\t:", gift, "\topen time\t:", open_time, "\tpapers\t:", papers)
            self_introduction = 1 if browser.find_elements(By.XPATH, "//h3[contains(string(),'个人简介')]") else 0
            social_appointment = 1 if browser.find_elements(By.XPATH, "//h3[contains(string(),'社会任职')]") else 0
            is_message = 1 if browser.find_elements(By.XPATH, "//h3[contains(string(),'寄语')]") else 0
            honors = 1 if browser.find_elements(By.XPATH, "//h3[contains(string(),'获奖荣誉')]") else 0
            scientific = 1 if browser.find_elements(By.XPATH, "//h3[contains(string(),'科研成果')]") else 0
            further_education = 1 if browser.find_elements(By.XPATH, "//h3[contains(string(),'进修经历')]") else 0
            education = 1 if browser.find_elements(By.XPATH, "//h3[contains(string(),'教育经历')]") else 0
            is_team = 1 if browser.find_elements(By.XPATH, "//div[contains(string(),'团队接诊')]") else 0
            haodaifu = get_num_by_class_name(browser, "honor-wrap")[0]
            recommendation = get_num_by_class_name(browser, "value")[0]
            num_patient = get_num_by_class_name(browser, "js-consult-count")[0]
            print("好大夫\t:", haodaifu, "\t\t推荐指数\t\t：", recommendation, "\t\t\t\t总病人\t\t：", num_patient)
            print(self_introduction, social_appointment, is_message, honors, scientific, further_education, education,
                  is_team)
            db.execute_query("""
                UPDATE doctor SET
                    professional_title = %s,
                    educational_title = %s,
                    social_appointment = %s,
                    gift = %s,
                    self_introduction = %s,
                    is_team = %s,
                    honors = %s,
                    is_message = %s,
                    scientific = %s,
                    further_education = %s,
                    education = %s,
                    haodaifu = %s,
                    recommendation = %s,
                    num_patient = %s,
                    visits = %s,
                    papers = %s,
                    followup_patient = %s,
                    evaluation = %s,
                    open_time = %s,
                    name = %s
                WHERE id = %s
            """, (
                professional_title, educational_title, social_appointment, gift, self_introduction,
                is_team, honors, is_message, scientific, further_education, education, haodaifu,
                recommendation, num_patient, visits, papers, followup_patient, evaluation, open_time,
                name, id
            ))

        except Exception as e:
            print(e)
            print(url)
        counter += 1
        if counter % 10 == 0:
            time.sleep(10 * 60)
        time.sleep(random.randint(0, 10) + 5)


def get_text_by_class_name(browser, class_name):
    elements = browser.find_elements(By.CLASS_NAME, class_name)
    return elements[0].text if elements else None


def get_num_by_class_name(browser, class_name):
    text = get_text_by_class_name(browser, class_name)
    if not text:
        return [0]
    text = text.replace(",", "")
    nums = re.findall(r'\d+\.\d+|\d+', text)
    return nums


# --------------------用于Android爬虫--------------------
def go_to_page():
    # 准备开始
    print("即将在5s后开始爬虫,请打开模拟器", end="")
    start_time = time.time()
    end_time = start_time + 5
    while time.time() < end_time:
        print(".", end="")
        time.sleep(1)

    # 初始化Emulator控制器与相关变量
    project_path = "D:\\Study\\Private\\Python\Code\\reproduction_economic\\Patient-centered-2024\\"
    screenshot_path = project_path + "tempt\\screenshot.png"
    images_path = project_path + "images\\"
    emulator = AndroidEmulator("Patient-centered-2024\\tempt")

    # 打开APP并进入相关界面
    emulator.screenshot("Patient-centered-2024\\tempt")
    position, _ = get_position(images_path + "app_icon.png", screenshot_path)
    emulator.click(position[0], position[1], random.randint(0, 5))  # 打开APP
    print("\n-->点击APP",end="")
    while True:  # APP启动时需要加载
        emulator.screenshot("Patient-centered-2024\\tempt")
        if compare_image(images_path + "experts_list_button.png", screenshot_path):
            break
        time.sleep(0.5)
    position, _ = get_position(images_path + "experts_list_button.png", screenshot_path)
    emulator.click(position[0], position[1], random.randint(0, 10))
    print("-->点击'按科室找'",end="")
    while True:
        emulator.screenshot()
        if compare_image(images_path + "find_by_illness_button.png", screenshot_path):
            break
        time.sleep(0.5)
    position, val = get_position(images_path + "endocrinology_department.png", screenshot_path)
    if val > 0.7:
        emulator.click(position[0], position[1], random.randint(0, 5))
        print("-->点击'内分泌科'", end="")
    while True:
        emulator.screenshot()
        if compare_image(images_path + "\\line.png", screenshot_path):
            break
        time.sleep(0.5)

    # 开始爬虫
    doctor_name=""
    for i in range(100):
        emulator.screenshot()
        split_lines = get_positions(images_path + "\\line.png", screenshot_path)
        split_lines_ordinate = []
        for ((_, ordinate), _) in split_lines:
            split_lines_ordinate.append(ordinate)
        split_lines_ordinate_asc = sorted(split_lines_ordinate)
        sliding_distance = split_lines_ordinate_asc[0]
        if sliding_distance < 400:
            print("准备下拉菜单进行刷新")
            emulator.swipe(270, 600, 270, 300, 1500)
            print("刷新中")
            time.sleep(0.5)
            while True:
                emulator.screenshot()
                if not compare_image(images_path + "refreshing.png", screenshot_path):
                    break
                time.sleep(0.5)
            print("开始向上抬升")
            emulator.swipe(270, 300, 270, 500, 1500)
            time.sleep(1)
            i -= 1
            continue
        emulator.swipe(270, 300 + split_lines_ordinate_asc[0] - 280, 270, 300, 1500)
        time.sleep(3)


def debug():
    project_path = "D:\\Study\\Private\\Python\Code\\reproduction_economic\\Patient-centered-2024\\"
    screenshot_path = project_path + "tempt\\screenshot.png"
    images_path = project_path + "images\\"
    emulator = AndroidEmulator("Patient-centered-2024\\tempt")
    last_screenshot = cv2.imread(screenshot_path)
    for i in range(100):
        emulator.screenshot()
        split_lines = get_positions(images_path + "\\line.png", screenshot_path)
        split_lines_ordinate = []
        for ((_, ordinate), _) in split_lines:
            split_lines_ordinate.append(ordinate)
        split_lines_ordinate_asc = sorted(split_lines_ordinate)
        sliding_distance = split_lines_ordinate_asc[0]
        print(sliding_distance)
        if compare_image(last_screenshot, screenshot_path,threshold=0.9) or sliding_distance<400:
            print("准备下拉菜单进行刷新")
            emulator.swipe(270, 600, 270, 300, 1500)
            print("刷新中")
            time.sleep(0.5)
            while True:
                emulator.screenshot()
                if not compare_image(images_path + "refreshing.png", screenshot_path):
                    break
                time.sleep(0.5)
            print("开始向上抬升")
            emulator.swipe(270, 300, 270, 500, 1500)
            time.sleep(1)
            i-=1
            continue
        else:
            last_screenshot = cv2.imread(screenshot_path)
        emulator.swipe(270, 300 + split_lines_ordinate_asc[0] - 280, 270, 300, 1500)
        time.sleep(3)


if __name__ == "__main__":
    go_to_page()



